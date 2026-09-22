"""3DBAG LOD2 modellerini B alani + 50 m icin indirir ve AHN kaynagini olcer.

Asama : 0.3  (Kararlar D-006, D-010, D-013)
Cikti : data/raw/3dbag/3dbag_pand.city.jsonl  (CityJSONFeature, satir basina bir bina)
        data/raw/3dbag/3dbag_metadata.json
        + .meta.json + data/DATA_LOG.md kaydi

KRITIK OLCUM (kullanici talimati, Asama 0.3 madde 3):
3DBAG'in hangi AHN surumunu kullandigi `b3_pw_bron` ve `b3_pw_datum`
ozniteliklerinden **her bina icin** okunur ve dagilimi raporlanir.
Bizim girdimiz AHN5'tir (Karar D-013); fark cikarsa kriter 1-B'nin
`consistency_check` etiketi korunur ve fark AGENTS.md Bolum 5'e sinirlama
olarak yazilir.

NOT — numberMatched CityObject sayar, pand DEGIL: her pand icin bir `Building`
ve bir veya daha fazla `BuildingPart` nesnesi doner. Pand sayisi ayrica sayilir.

Calistirma:
    python src/00_acquisition/download_3dbag.py
"""

from __future__ import annotations

import collections
import json
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from shapely.geometry import shape

from src.common.config import resolve, expected_crs
from src.common.data_log import append_entry
from src.common.logging_setup import setup_logging
from src.common.meta import write_meta

API = "https://api.3dbag.nl/collections/pand/items"

# --- SURUM PARMAK IZI (MISTAKES.md M-013, Karar D-023) ---
# API'nin `version.collection` etiketi bir BEYANDIR, dogrulama degil: 2026-09-22'de
# etiket "v2023.10.08" derken icerik 2025.09.03 ile tutarliydi. Surum, oznitelik
# kumesinden BAGIMSIZ olarak cikarilir. Kaynak (birincil, okundu 2026-09-22):
# https://docs.3dbag.nl/en/overview/release_notes/
# Her surum icin: bu surumde VAR olmasi gereken ve OLMAMASI gereken isaret oznitelikler.
_ADDED_2024_12 = {"b3_mutatie_ahn4_ahn5", "b3_puntdichtheid_ahn5", "b3_nodata_fractie_ahn5",
                  "b3_nodata_radius_ahn5", "b3_extrusie", "b3_pw_onvoldoende"}
_RELEASE_MARKERS = {
    "2023.10.08": {"present": {"b3_reconstructie_onvolledig"},
                   "absent": {"b3_bouwlagen", "b3_succes"} | _ADDED_2024_12},
    "2024.02.28": {"present": {"b3_bouwlagen", "b3_reconstructie_onvolledig"},
                   "absent": {"b3_succes"} | _ADDED_2024_12},
    "2024.04.20": {"present": {"b3_bouwlagen", "b3_reconstructie_onvolledig"},
                   "absent": {"b3_succes"} | _ADDED_2024_12},
    "2024.12.16": {"present": {"b3_bouwlagen", "b3_succes"} | _ADDED_2024_12,
                   "absent": {"b3_reconstructie_onvolledig"}},
    "2025.09.03": {"present": {"b3_bouwlagen"} | _ADDED_2024_12,
                   "absent": {"b3_reconstructie_onvolledig", "b3_succes"}},
}


def _version_fingerprint(attribute_names: set[str]) -> list[str]:
    """Oznitelik kumesiyle TUTARLI 3DBAG surumlerini dondurur.

    Girdi : attribute_names — indirilen Building nesnelerindeki tum oznitelik adlari
    Cikti : list[str] — tutarli surumler (bos liste = bilinen hicbir surume uymuyor)
    Birim : yok

    Not: 2024.02.28 ve 2024.04.20 (yama surumu) oznitelik duzeyinde AYIRT
    EDILEMEZ; ikisi birden donerse bu bir belirsizliktir, hata degildir.
    """
    return [v for v, m in _RELEASE_MARKERS.items()
            if m["present"] <= attribute_names and not (m["absent"] & attribute_names)]
SAFETY_MARGIN_M = 50.0      # Karar D-010
PAGE_LIMIT = 1000
TIMEOUT_S = 180


def main() -> int:
    logger, run_id, _ = setup_logging("download_3dbag")
    crs_z = expected_crs("with_height")

    area_b = shape(json.loads(
        (resolve("root.aoi") / "area_B_context.geojson").read_text(encoding="utf-8")
    )["features"][0]["geometry"])
    bminx, bminy, bmaxx, bmaxy = area_b.bounds
    bbox = (bminx - SAFETY_MARGIN_M, bminy - SAFETY_MARGIN_M,
            bmaxx + SAFETY_MARGIN_M, bmaxy + SAFETY_MARGIN_M)
    bbox_str = ",".join(f"{v:.1f}" for v in bbox)
    logger.info("Kapsam | B + %.0f m (D-010) | %s", SAFETY_MARGIN_M, bbox_str)

    # --- Boyut on olcumu (M-004 kural 3) ---
    probe = requests.get(API, params={"bbox": bbox_str, "limit": 1}, timeout=TIMEOUT_S)
    probe.raise_for_status()
    probe_data = probe.json()
    expected_objects = probe_data.get("numberMatched")
    collection_version = None
    logger.info("numberMatched (CityObject) = %s", expected_objects)

    out_dir = resolve("data.raw") / "3dbag"
    out_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = out_dir / "3dbag_pand.city.jsonl"

    features_written = 0
    pand_ids: set[str] = set()
    pw_bron = collections.Counter()
    pw_datum = collections.Counter()
    pw_onvoldoende = collections.Counter()
    attribute_names: set[str] = set()
    # OGC API Features sayfalamasi: `next` baglantisi IZLENIR, offset URETILMEZ.
    # Sebep: bu API `offset=0` icin HTTP 500 donuyor (olculdu 2026-09-21).
    # Kendi offset'ini uretmek servise dair bir VARSAYIMDIR; `next` baglantisini
    # izlemek servisin kendi beyanini kullanir (M-005 ilkesinin sayfalamaya
    # uygulanmis hali).
    next_url: str | None = API
    next_params: dict | None = {"bbox": bbox_str, "limit": PAGE_LIMIT}

    with jsonl_path.open("w", encoding="utf-8") as fh:
        while next_url:
            response = requests.get(next_url, params=next_params, timeout=TIMEOUT_S)
            response.raise_for_status()
            page = response.json()
            next_params = None  # `next` linki tum parametreleri zaten tasir

            if collection_version is None:
                collection_version = (
                    page.get("metadata", {}).get("metadata", {}).get("datasetVersion")
                    or page.get("metadata", {}).get("version")
                )

            batch = page.get("features", [])
            if not batch:
                break

            for feature in batch:
                fh.write(json.dumps(feature, ensure_ascii=False) + "\n")
                features_written += 1
                for obj in feature.get("CityObjects", {}).values():
                    attrs = obj.get("attributes")
                    if not attrs or obj.get("type") != "Building":
                        continue
                    attribute_names.update(attrs.keys())
                    identificatie = attrs.get("identificatie")
                    if identificatie:
                        pand_ids.add(identificatie)
                    pw_bron[str(attrs.get("b3_pw_bron"))] += 1
                    pw_datum[str(attrs.get("b3_pw_datum"))] += 1
                    pw_onvoldoende[str(attrs.get("b3_pw_onvoldoende"))] += 1

            if features_written % (PAGE_LIMIT * 2) < len(batch):
                logger.info("Sayfa | %d ozellik | %d benzersiz pand",
                            features_written, len(pand_ids))

            next_url = next(
                (l["href"] for l in page.get("links", []) if l.get("rel") == "next"), None
            )

    size_bytes = jsonl_path.stat().st_size
    logger.info("Indirme tamam | %d ozellik | %d benzersiz pand | %.1f MB",
                features_written, len(pand_ids), size_bytes / 2**20)

    # --- M-005 otomatiklestirmesi: oznitelik listesi kayda gecer ---
    logger.info("Oznitelikler | 3dbag:pand | %d alan", len(attribute_names))

    # --- M-013: API etiketi ile icerik parmak izi KARSILASTIRILIR ---
    fp = _version_fingerprint(attribute_names)
    label = str(collection_version)
    if len(fp) == 1 and fp[0] in label:
        version_record = f"{fp[0]} (API etiketi ve icerik parmak izi TUTARLI)"
        logger.info("Surum | etiket %s | parmak izi %s | TUTARLI", label, fp)
    else:
        version_record = (f"BELIRSIZ - API etiketi '{label}', icerik parmak izi {fp or 'bilinen surume uymuyor'}"
                          " (M-013: etiket bir beyandir, dogrulama degil)")
        logger.warning("Surum | etiket %s | parmak izi %s | CELISKI veya BELIRSIZLIK", label, fp)

    # --- ITEM 3: AHN kaynagi dagilimi ---
    logger.info("=== 3DBAG'in kullandigi nokta bulutu kaynagi ===")
    for source, count in pw_bron.most_common():
        logger.info("  b3_pw_bron = %-8s %6d bina (%%%.1f)",
                    source, count, 100 * count / max(1, sum(pw_bron.values())))
    for year, count in pw_datum.most_common():
        logger.info("  b3_pw_datum = %-6s %6d bina", year, count)
    for flag, count in pw_onvoldoende.most_common():
        logger.info("  b3_pw_onvoldoende = %-6s %6d bina", flag, count)

    ahn5_share = 100 * pw_bron.get("ahn5", 0) / max(1, sum(pw_bron.values()))
    if ahn5_share >= 99.0:
        logger.info("SONUC: 3DBAG bu alanda AHN5 kullanmis (%%%.1f). Girdimizle AYNI "
                    "surum (Karar D-013). Kriter 1-B icin surum farki SINIRLAMASI YOK.",
                    ahn5_share)
    else:
        logger.warning("SONUC: 3DBAG binalarinin yalnizca %%%.1f'i AHN5 tabanli. "
                       "Kriter 1-B'de surum farki SINIRLAMA olarak raporlanmali "
                       "(Karar D-013).", ahn5_share)

    metadata_path = out_dir / "3dbag_metadata.json"
    metadata_path.write_text(json.dumps({
        "collection_version": collection_version,
        "api_query": {"bbox": bbox_str, "limit": PAGE_LIMIT},
        "numberMatched_cityobjects": expected_objects,
        "features_written": features_written,
        "unique_panden": len(pand_ids),
        "b3_pw_bron": dict(pw_bron),
        "b3_pw_datum": dict(pw_datum),
        "b3_pw_onvoldoende": dict(pw_onvoldoende),
        "attributes": sorted(attribute_names),
    }, indent=2, ensure_ascii=False), encoding="utf-8")

    write_meta(
        jsonl_path, run_id=run_id,
        parameters={
            "bbox_epsg28992": list(bbox),
            "safety_margin_m": SAFETY_MARGIN_M,
            "features": features_written,
            "unique_panden": len(pand_ids),
            "b3_pw_bron": dict(pw_bron),
        },
        software={"api": API, "collection_version": str(collection_version)},
        notes=f"CRS {crs_z}. 3DBAG nokta bulutu kaynagi her bina icin olculdu.",
    )
    append_entry(
        dataset="3DBAG LOD2 (CityJSONFeature)",
        path=jsonl_path, run_id=run_id,
        source_url=API,
        provider="TU Delft 3D geoinformation",
        version=version_record,
        query=f"bbox={bbox_str} (EPSG:28992) = B + {SAFETY_MARGIN_M:.0f} m; sayfalama limit={PAGE_LIMIT}",
        crs=crs_z,
        time_reference=f"b3_pw_datum dagilimi: {dict(pw_datum)}",
        license_="CC BY 4.0 (AGENTS.md Bolum 7) - attribution ZORUNLU",
        attribution="TODO: 3DBAG resmi attribution metni kaynagindan alinacak",
        processing="yok (ham indirme)",
        notes=(
            f"{features_written} CityJSONFeature, {len(pand_ids)} benzersiz pand. "
            f"numberMatched={expected_objects} CityObject sayar (Building + BuildingPart), "
            f"pand DEGIL. "
            f"NOKTA BULUTU KAYNAGI (b3_pw_bron): {dict(pw_bron)}. "
            f"Yil (b3_pw_datum): {dict(pw_datum)}. "
            f"Bizim girdimiz AHN5'tir (D-013); AHN5 payi %{ahn5_share:.1f}. "
            f"OZNITELIKLER ({len(attribute_names)}): {', '.join(sorted(attribute_names))}"
        ),
    )
    logger.info("TAMAM | %s", jsonl_path.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
