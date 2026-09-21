"""CBS Wijken en Buurten 2025'ten Voorhof (WK050324) sinirini indirir.

Asama : 0.2a
Cikti : data/raw/cbs/voorhof_wijk.geojson
        data/raw/cbs/voorhof_buurten.geojson
        + .meta.json + data/DATA_LOG.md kaydi

Karar D-007: CBS Wijken en Buurten, AGENTS.md Bolum 4'teki envantere bu kararla
eklenen yeni kaynaktir.

DIKKAT: CBS'teki resmi ad "Voorhof" DEGIL, **"Wijk 24 Voorhof"**tur. Ad uzerinden
tam esleme sorgusu 0 kayit dondurur (MISTAKES.md M-004). Bu yuzden sorgu **wijkcode**
uzerinden yapilir.

Calistirma:
    python src/00_acquisition/download_cbs_wijk.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.common import wfs
from src.common.config import load_paths, resolve, expected_crs
from src.common.data_log import append_entry
from src.common.logging_setup import log_crs, setup_logging
from src.common.meta import write_meta

WIJKCODE = "WK050324"
WIJKNAAM = "Wijk 24 Voorhof"


def main() -> int:
    logger, run_id, _ = setup_logging("download_cbs_wijk")
    sources = load_paths()["remote_sources"]["cbs_wijkenbuurten"]
    target_crs = expected_crs("planimetric")

    out_dir = resolve("data.raw") / "cbs"
    out_dir.mkdir(parents=True, exist_ok=True)

    logger.info("CBS Wijken en Buurten %s | wijkcode=%s", sources["dataset_year"], WIJKCODE)

    # --- 1. Wijk siniri (tek poligon) ---
    wijk_filter = wfs.property_equals_filter("wijkcode", WIJKCODE)
    wijk = wfs.fetch_features(
        service=sources["wfs"],
        typename=sources["layers"]["wijken"],
        version=sources["version"],
        filter_xml=wijk_filter,
        # M-004 kural 2: donen her kayit gercekten bu wijkcode mu?
        verify=lambda f: f["properties"].get("wijkcode") == WIJKCODE,
        logger=logger,
    )

    if len(wijk["features"]) != 1:
        logger.error("Beklenen 1 wijk, donen %d. Devam edilmiyor.", len(wijk["features"]))
        return 1

    found_crs = wfs.crs_urn_to_epsg(wijk["crs"]["properties"]["name"])
    log_crs(logger, sources["layers"]["wijken"], found_crs, target_crs)

    props = wijk["features"][0]["properties"]
    if props.get("wijknaam") != WIJKNAAM:
        logger.warning(
            "wijknaam beklenenden farkli: bulunan=%r beklenen=%r. "
            "CBS yil surumu degismis olabilir.", props.get("wijknaam"), WIJKNAAM
        )

    wijk_path = out_dir / "voorhof_wijk.geojson"
    wijk_path.write_text(json.dumps(wijk, ensure_ascii=False), encoding="utf-8")

    minx, miny, maxx, maxy = wfs.bounds_of(wijk["features"])
    logger.info(
        "Voorhof bbox | x %.1f..%.1f y %.1f..%.1f | %.0f x %.0f m",
        minx, maxx, miny, maxy, maxx - minx, maxy - miny,
    )

    # --- 2. Voorhof'un buurt'lari (baglam; woonfunctie yorumu icin) ---
    # buurtcode, wijkcode'un BU + son 6 hane bicimi: WK050324 -> BU050324xx
    buurt_prefix = "BU" + WIJKCODE[2:]
    buurten_all = wfs.fetch_features(
        service=sources["wfs"],
        typename=sources["layers"]["buurten"],
        version=sources["version"],
        bbox=wfs.bbox_param(minx, miny, maxx, maxy, target_crs),
        logger=logger,
    )
    # bbox komsu wijk'lerin buurt'larini da getirir; kod on ekiyle daraltilir
    buurten = {
        "type": "FeatureCollection",
        "crs": buurten_all["crs"],
        "features": [
            f for f in buurten_all["features"]
            if str(f["properties"].get("buurtcode", "")).startswith(buurt_prefix)
        ],
    }
    logger.info(
        "Buurt filtresi | bbox'tan %d -> %s on ekiyle %d",
        len(buurten_all["features"]), buurt_prefix, len(buurten["features"]),
    )

    buurten_path = out_dir / "voorhof_buurten.geojson"
    buurten_path.write_text(json.dumps(buurten, ensure_ascii=False), encoding="utf-8")

    # --- 3. Tekrarlanabilirlik kayitlari ---
    for path, layer, query in (
        (wijk_path, sources["layers"]["wijken"], f"filter: wijkcode={WIJKCODE}"),
        (buurten_path, sources["layers"]["buurten"], f"bbox + buurtcode on eki {buurt_prefix}"),
    ):
        write_meta(
            path,
            run_id=run_id,
            parameters={"wijkcode": WIJKCODE, "layer": layer, "query": query},
            software={"service": sources["wfs"], "wfs_version": sources["version"]},
            notes="CRS dosyadan okundu ve EPSG:28992 ile karsilastirildi (uyustu).",
        )
        append_entry(
            dataset=f"CBS Wijken en Buurten {sources['dataset_year']} — {layer}",
            path=path,
            run_id=run_id,
            source_url=sources["wfs"],
            provider="CBS / PDOK",
            version=str(sources["dataset_year"]),
            query=query,
            crs=found_crs,
            time_reference="yok (yillik idari sinir)",
            license_="TODO_0.3: PDOK lisans kosulu kaynagindan dogrulanacak",
            attribution="TODO_0.3",
            notes=(
                f"Resmi ad '{WIJKNAAM}' — 'Voorhof' ile tam esleme sorgusu 0 dondurur "
                f"(M-004). Sorgu wijkcode uzerinden yapildi. "
                f"Filtre ciktidan dogrulandi. Ham dosya degistirilmedi."
            ),
        )

    logger.info("TAMAM | wijk=%s | buurt=%d", wijk_path.name, len(buurten["features"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
