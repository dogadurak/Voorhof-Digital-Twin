"""A ve B alan sinirlarini resmi CBS buurt'larindan uretir.

Asama : 0.2  (Karar D-009)
Cikti : aoi/area_A_analysis.geojson   — 7 resmi konut buurt'unun birlesimi
        aoi/area_B_context.geojson    — A + 300 m tampon
        + .meta.json + data/DATA_LOG.md kayitlari

A ELLE CIZILMEZ, ARANMAZ. Resmi birimlerden birlestirilir; oznel karar yoktur.
Dislanan buurt kodlari config/acceptance_criteria.yml -> aoi_definition
altinda kilitlidir, koda gomulmez.

CRS NOTU: Dosyalar EPSG:28992 (RD New) koordinatlariyla ve acik bir `crs`
uyesiyle yazilir. RFC 7946 GeoJSON'un WGS84 olmasini ongorur; burada bilerek
sapilmistir cunku AGENTS.md Bolum 12.1 planimetrik CRS olarak EPSG:28992'yi
zorunlu kiliyor ve kaynak veri (PDOK) de bu sekilde sunuluyor. QGIS ve
geopandas bu bicimi dogru okur. Yeniden projeksiyon YAPILMAZ — gereksiz bir
donusum, gereksiz bir hata kaynagidir.

Onkosul: download_cbs_wijk.py calistirilmis olmali.

Calistirma:
    python src/00_acquisition/build_aoi.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from shapely.geometry import mapping, shape
from shapely.ops import unary_union

from src.common.config import load_acceptance_criteria, resolve, expected_crs
from src.common.data_log import append_entry
from src.common.logging_setup import setup_logging
from src.common.meta import write_meta

M2_PER_HA = 10_000.0


def _write_geojson(path: Path, geometry, properties: dict, crs: str) -> None:
    """Tek ozellikli bir GeoJSON yazar, CRS'i acikca belirterek.

    Girdi : path       — cikti dosyasi
            geometry   — shapely geometrisi
            properties — ozellik oznitelikleri
            crs        — "EPSG:28992" bicimli kod
    Cikti : None
    """
    authority, code = crs.split(":")
    payload = {
        "type": "FeatureCollection",
        "crs": {"type": "name", "properties": {"name": f"urn:ogc:def:crs:{authority}::{code}"}},
        "features": [{"type": "Feature", "properties": properties, "geometry": mapping(geometry)}],
    }
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def _describe(name: str, geometry, logger) -> dict:
    """Bir alan geometrisini olcer ve loglar; bozuksa exception firlatir.

    Cikti : dict — {"area_ha", "valid", "geom_type", "parts", "bounds"}
    Birim : alan ha, sinirlar m (EPSG:28992)

    Gecersiz veya coklu parcali bir AOI, Asama 1'e kadar sessizce tasinirsa
    rekonstruksiyon ve tampon hesaplarini bozar. Burada durdurulur.
    """
    parts = len(geometry.geoms) if geometry.geom_type == "MultiPolygon" else 1
    info = {
        "area_ha": round(geometry.area / M2_PER_HA, 2),
        "valid": bool(geometry.is_valid),
        "geom_type": geometry.geom_type,
        "parts": parts,
        "bounds": [round(v, 1) for v in geometry.bounds],
    }
    logger.info(
        "%s | alan=%.2f ha | gecerli=%s | tip=%s | parca=%d | bbox=%s",
        name, info["area_ha"], info["valid"], info["geom_type"], parts, info["bounds"],
    )
    if not geometry.is_valid:
        raise ValueError(f"{name} geometrisi GECERSIZ. AOI bu haliyle kullanilamaz.")
    if parts > 1:
        logger.warning(
            "%s %d parcadan olusuyor. Bu beklenmiyordu — dislanan buurt'lar alani "
            "bolmus olabilir. Devam ediliyor ama raporda belirtilecek.", name, parts,
        )
    return info


def main() -> int:
    logger, run_id, _ = setup_logging("build_aoi")
    target_crs = expected_crs("planimetric")
    aoi_cfg = load_acceptance_criteria()["aoi_definition"]

    excluded = {b["code"]: b["name"] for b in aoi_cfg["area_a"]["excluded_buurten"]}
    buffer_m = float(aoi_cfg["area_b"]["buffer_m"])
    logger.info("Dislanan buurt'lar (config'ten): %s", excluded)
    logger.info("B tamponu (config'ten): %.0f m", buffer_m)

    src_path = resolve("data.raw") / "cbs" / "voorhof_buurten.geojson"
    if not src_path.is_file():
        logger.error("Onkosul eksik: %s yok. Once download_cbs_wijk.py calistirin.", src_path)
        return 1

    collection = json.loads(src_path.read_text(encoding="utf-8"))

    found_crs = collection.get("crs", {}).get("properties", {}).get("name", "")
    if not found_crs.endswith(target_crs.split(":")[1]):
        logger.error("CRS uyusmazligi: %s bekleniyordu, %s bulundu.", target_crs, found_crs)
        return 1
    logger.info("CRS kontrol | kaynak=%s | beklenen=%s | UYUSTU", src_path.name, target_crs)

    included, industry = [], []
    for feature in collection["features"]:
        code = feature["properties"]["buurtcode"]
        (industry if code in excluded else included).append(feature)

    if len(industry) != len(excluded):
        logger.error(
            "Dislanacak %d buurt tanimli ama veride %d bulundu. Kodlar degismis olabilir.",
            len(excluded), len(industry),
        )
        return 1

    codes = sorted(f["properties"]["buurtcode"] for f in included)
    logger.info("Dahil edilen konut buurt'u: %d | %s", len(included), ", ".join(codes))
    for feature in sorted(included, key=lambda f: f["properties"]["buurtcode"]):
        props = feature["properties"]
        logger.info(
            "   %-12s %-30s %3s ha  nufus %5s",
            props["buurtcode"], props["buurtnaam"],
            props.get("oppervlakteLandInHa"), props.get("aantalInwoners"),
        )

    area_a = unary_union([shape(f["geometry"]) for f in included])
    area_b = area_a.buffer(buffer_m)
    industry_geom = unary_union([shape(f["geometry"]) for f in industry])

    info_a = _describe("A (analiz alani)", area_a, logger)
    info_b = _describe("B (baglam/tampon)", area_b, logger)

    # --- Dislama gercekten temiz mi? Varsayilmaz, olculur. ---
    overlap_ha = area_a.intersection(industry_geom).area / M2_PER_HA
    logger.info("A ∩ sanayi = %.4f ha (0 olmali)", overlap_ha)
    if overlap_ha > 0.01:
        logger.error("Dislanan buurt'lar A ile kesisiyor (%.4f ha). Durduruldu.", overlap_ha)
        return 1

    ind_in_b = industry_geom.intersection(area_b).area / M2_PER_HA
    ind_total = industry_geom.area / M2_PER_HA
    logger.info(
        "Sanayi buurt'lari | toplam %.2f ha | B icinde %.2f ha (%%%.0f) - "
        "model ve golge/CFD girdisi olarak KALIYOR, yalnizca A raporlamasindan cikti",
        ind_total, ind_in_b, 100 * ind_in_b / ind_total,
    )

    # CBS kara alani vs geometrik alan — birim tanimi farki (Bolum 12.1)
    cbs_land_ha = sum(f["properties"].get("oppervlakteLandInHa") or 0 for f in included)
    logger.info(
        "Alan tanimi farki | CBS kara alani %d ha | geometrik alan %.2f ha | fark %.2f ha "
        "(CBS su yuzeyini haric tutar)", cbs_land_ha, info_a["area_ha"], info_a["area_ha"] - cbs_land_ha,
    )

    out_dir = resolve("root.aoi")
    out_dir.mkdir(parents=True, exist_ok=True)
    path_a = out_dir / "area_A_analysis.geojson"
    path_b = out_dir / "area_B_context.geojson"

    _write_geojson(path_a, area_a, {
        "name": "A — analiz alani",
        "definition": "Voorhof (WK050324) 7 resmi konut buurt'unun birlesimi",
        "included_buurtcodes": codes,
        "excluded_buurtcodes": sorted(excluded),
        "area_ha_geometric": info_a["area_ha"],
        "area_ha_cbs_land": cbs_land_ha,
        "role": "analysis",
        "decision_ref": "D-009",
        "source": "CBS Wijken en Buurten 2025 (PDOK WFS)",
    }, target_crs)

    _write_geojson(path_b, area_b, {
        "name": "B — baglam / tampon",
        "definition": f"A + {buffer_m:.0f} m tampon",
        "area_ha_geometric": info_b["area_ha"],
        "role": "context",
        "reported": False,
        "note": "SIMULE EDILIR, RAPORLANMAZ (AGENTS.md Bolum 3). Sanayi binalari burada KALIR.",
        "industry_ha_inside": round(ind_in_b, 2),
        "decision_ref": "D-009",
    }, target_crs)

    for path, label, info, note in (
        (path_a, "A — analiz alani", info_a,
         f"{len(included)} resmi konut buurt'unun birlesimi: {', '.join(codes)}. "
         f"Dislanan 2 sanayi buurt'u: {', '.join(sorted(excluded))}. "
         f"A ∩ sanayi = {overlap_ha:.4f} ha. Tek parca, gecerli geometri. "
         f"CBS kara alani {cbs_land_ha} ha, geometrik alan {info_a['area_ha']} ha "
         f"(fark su yuzeyi)."),
        (path_b, "B — baglam/tampon", info_b,
         f"A + {buffer_m:.0f} m tampon, programatik uretildi. "
         f"Sanayi buurt'larinin {ind_in_b:.2f} ha'i ({100*ind_in_b/ind_total:.0f}%) B icinde "
         f"ve modelde KALIYOR (golge/CFD girdisi). B raporlanmaz."),
    ):
        write_meta(
            path, run_id=run_id, inputs=[src_path],
            parameters={
                "included_buurtcodes": codes,
                "excluded_buurtcodes": sorted(excluded),
                "buffer_m": buffer_m,
                "area_ha": info["area_ha"],
                "geom_type": info["geom_type"],
                "parts": info["parts"],
            },
            software={"shapely_op": "unary_union + buffer"},
            notes=f"CRS {target_crs}, kaynaktan okundu ve dogrulandi. Karar D-009.",
        )
        append_entry(
            dataset=f"AOI — {label}",
            path=path, run_id=run_id,
            source_url="turetilmis (CBS Wijken en Buurten 2025'ten)",
            provider="Voorhof Digital Twin / Karar D-009",
            version="D-009",
            query=f"buurtcode in {codes}" if path is path_a else f"A.buffer({buffer_m:.0f})",
            crs=target_crs,
            time_reference="yok (idari sinir, CBS 2025)",
            license_="TODO_0.3: CBS kaynak lisansindan turer",
            attribution="TODO_0.3",
            processing="unary_union" + (f" + buffer({buffer_m:.0f} m)" if path is path_b else ""),
            notes=note,
        )

    logger.info("TAMAM | %s (%.2f ha) | %s (%.2f ha)",
                path_a.name, info_a["area_ha"], path_b.name, info_b["area_ha"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
