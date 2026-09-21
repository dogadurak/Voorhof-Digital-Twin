"""BAG pand ve verblijfsobject katmanlarini Voorhof bbox + tampon ile indirir.

Asama : 0.2a
Cikti : data/raw/bag/bag_pand.geojson
        data/raw/bag/bag_verblijfsobject.geojson
        + .meta.json + data/DATA_LOG.md kayitlari

NEDEN IKI KATMAN:
woonfunctie orani VBO duzeyinde hesaplanir (Karar D-008), bu yuzden her iki katman
da gerekir. `bag:pand` da bir `gebruiksdoel` alani TASIR, ama kullanilamaz:
panden'in %40,6'si konut birimi icermeyen yardimci yapilardir (garaj, trafo, depo)
ve gebruiksdoel'leri bostur; pand duzeyinde oran %50,5'te kalir ve >=%90 esigi
hicbir karede saglanamaz.

(Bu dosyanin onceki surumu "gebruiksdoel pand uzerinde DEGIL" diyordu — bu YANLISTI,
bkz. MISTAKES.md M-005.)

NEDEN TAMPON:
Merkezi Voorhof icinde olan bir 600 m kare, sinirdan 300 m disari tasabilir
(kriter 0.2-C zaten %20'ye kadar tasmaya izin veriyor). Tamponsuz indirme kenardaki
adaylarin bina sayimini eksik gosterir ve secimi sistematik olarak merkeze kaydirir.
Tampon degeri config'ten okunur (stage_0_2.download_extent).

Bu tampon 0.2a'ya ozgudur. Asama 0.3 indirmeleri Karar D-006 uyarinca secilen
**B alani** bbox'i ile sinirlanir.

Onkosul: download_cbs_wijk.py calistirilmis olmali.

Calistirma:
    python src/00_acquisition/download_bag.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.common import wfs
from src.common.config import load_acceptance_criteria, load_paths, resolve, expected_crs
from src.common.data_log import append_entry
from src.common.logging_setup import log_crs, setup_logging
from src.common.meta import write_meta

BUFFER_M = 300.0  # stage_0_2.download_extent ile tutarli; asagida config'ten dogrulanir


def main() -> int:
    logger, run_id, _ = setup_logging("download_bag")
    sources = load_paths()["remote_sources"]["bag"]
    target_crs = expected_crs("planimetric")

    stage = load_acceptance_criteria()["stage_0_2"]
    half_side = stage["grid"]["square_side_m"] / 2.0
    if half_side != BUFFER_M:
        logger.error(
            "Tampon tutarsiz: config kare kenari %s m -> yarisi %s m, script %s m kullaniyor.",
            stage["grid"]["square_side_m"], half_side, BUFFER_M,
        )
        return 1
    logger.info("Tampon config ile dogrulandi: %.0f m (kare kenarinin yarisi)", half_side)

    wijk_path = resolve("data.raw") / "cbs" / "voorhof_wijk.geojson"
    if not wijk_path.is_file():
        logger.error("Onkosul eksik: %s yok. Once download_cbs_wijk.py calistirin.", wijk_path)
        return 1

    wijk = json.loads(wijk_path.read_text(encoding="utf-8"))
    minx, miny, maxx, maxy = wfs.bounds_of(wijk["features"])
    bminx, bminy = minx - half_side, miny - half_side
    bmaxx, bmaxy = maxx + half_side, maxy + half_side

    logger.info(
        "Indirme bbox (Voorhof + %.0f m) | x %.1f..%.1f y %.1f..%.1f | %.0f x %.0f m",
        half_side, bminx, bmaxx, bminy, bmaxy, bmaxx - bminx, bmaxy - bminy,
    )

    bbox = wfs.bbox_param(bminx, bminy, bmaxx, bmaxy, target_crs)
    out_dir = resolve("data.raw") / "bag"
    out_dir.mkdir(parents=True, exist_ok=True)

    results: list[tuple[Path, str, int]] = []

    for key, filename in (("pand", "bag_pand.geojson"),
                          ("verblijfsobject", "bag_verblijfsobject.geojson")):
        layer = sources["layers"][key]
        logger.info("--- %s indiriliyor ---", layer)

        collection = wfs.fetch_features(
            service=sources["wfs"],
            typename=layer,
            version=sources["version"],
            bbox=bbox,
            page_size=sources["count_default"],
            logger=logger,
        )

        found_crs = wfs.crs_urn_to_epsg(collection["crs"]["properties"]["name"])
        log_crs(logger, layer, found_crs, target_crs)

        # M-004 kural 2: bbox gercekten uygulandi mi? Ciktidan dogrula.
        fminx, fminy, fmaxx, fmaxy = wfs.bounds_of(collection["features"])
        tolerance = 1000.0  # bbox'a degen geometriler disari tasabilir
        if (fminx < bminx - tolerance or fmaxx > bmaxx + tolerance
                or fminy < bminy - tolerance or fmaxy > bmaxy + tolerance):
            logger.error(
                "bbox UYGULANMAMIS olabilir: donen veri x %.0f..%.0f y %.0f..%.0f, "
                "istenen x %.0f..%.0f y %.0f..%.0f. Veri yazilmadi.",
                fminx, fmaxx, fminy, fmaxy, bminx, bmaxx, bminy, bmaxy,
            )
            return 1
        logger.info("bbox ciktidan dogrulandi | %s", layer)

        # M-005 / Bolum 14.5: sema iddiasi degil, gercek oznitelik listesi kayda gecer
        schema = wfs.describe_attributes(
            collection["features"], layer, logger=logger, value_counts_for=("status",)
        )

        out_path = out_dir / filename
        out_path.write_text(json.dumps(collection, ensure_ascii=False), encoding="utf-8")
        results.append((out_path, layer, len(collection["features"])))

        write_meta(
            out_path,
            run_id=run_id,
            inputs=[wijk_path],
            parameters={
                "bbox_epsg28992": [bminx, bminy, bmaxx, bmaxy],
                "buffer_m": half_side,
                "layer": layer,
                "feature_count": len(collection["features"]),
            },
            software={"service": sources["wfs"], "wfs_version": sources["version"]},
            notes="bbox Voorhof sinirindan turetildi; CRS okundu ve dogrulandi.",
        )
        status_lines = " · ".join(
            f"{k}: {v}" for k, v in schema["value_counts"]["status"].items()
        )
        append_entry(
            dataset=f"BAG — {layer}",
            path=out_path,
            run_id=run_id,
            source_url=sources["wfs"],
            provider="Kadaster / PDOK",
            version="WFS v2_0 (surum etiketi servis tarafinda yok)",
            query=(
                f"bbox={bminx:.1f},{bminy:.1f},{bmaxx:.1f},{bmaxy:.1f} "
                f"(EPSG:28992) = Voorhof bbox + {half_side:.0f} m tampon; "
                f"sayfalama count={sources['count_default']}"
            ),
            crs=found_crs,
            time_reference="yok (BAG durum verisi; indirme anindaki gecerli kayit)",
            license_="TODO_0.3: PDOK/Kadaster lisans kosulu kaynagindan dogrulanacak",
            attribution="TODO_0.3",
            notes=(
                f"Ozellik sayisi: {len(collection['features'])}. "
                f"bbox ciktidan dogrulandi (M-004 kural 2). "
                f"Ham dosya degistirilmedi. "
                f"OZNITELIKLER ({len(schema['attributes'])}): "
                f"{', '.join(schema['attributes'])}. "
                f"STATUS DAGILIMI: {status_lines}. "
                f"Status filtresi config/acceptance_criteria.yml -> "
                f"stage_0_2.status_filter altinda tanimlidir (Karar D-008); "
                f"degerler bu dagilimdan dogrulanmistir (M-005)."
            ),
        )

    for path, layer, count in results:
        logger.info("TAMAM | %-28s %6d ozellik | %s", layer, count, path.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
