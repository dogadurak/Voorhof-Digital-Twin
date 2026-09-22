"""Bina yuksekliklerini AHN5 nokta bulutundan DOGRUDAN olcer.

Asama : 0.3  (Karar D-030 / P-019 kalibrasyonunun girdisi)
Kapsam: B alanindaki TUM panden (status filtreli, centroid kurali)

Yontem `config/acceptance_criteria.yml` ->
`storey_height_calibration.height_measurement` altindan OKUNUR. O blok bu
scriptten ONCE ayri bir commit ile muhurlenmistir (commit f2667c1,
status: SEALED_BEFORE_OBSERVATION).

    h_measured_m = p70(z, sinif 6, ayakizi ICINDE)
                 - medyan(z, sinif 2, ayakizi DISINDAKI halkada)

    halka = footprint.buffer(5,0 m) \\ footprint.buffer(0,5 m)

Neden halka: normal bir binada ayakizi ICINDE zemin noktasi neredeyse yoktur
(cati zemini kapatir); oradan okunan bir "maaiveld" gurultudur. Halka binanin
oturdugu YEREL kotu olcer.

Neden p70: p100/max cati ustu teknik hacimleri (asansor kulesi, tesisat)
yakalar. Muhurlu kat sayim kurali R5 bunlari KAT SAYMAZ; olcum de saymamalidir.

3DBAG `b3_h_dak_*` BILEREK KULLANILMAZ: 3DBAG de AHN'den turetilir ve Asama
1'de kriter 1-B'de ona karsi karsilastirma yapilacaktir. Kalibrasyonu ona
baglamak o karsilastirmayi kismen donguselleştirirdi (Bolum 12.10).

Bellek notu: yuzdelikler tek geciste hesaplanamaz. Cozum: bina x z-bin
histogrami (0,10 m bin) biriktirilir ve yuzdelikler histogramdan okunur.
Boylece 9 LAZ dosyasi TEK KEZ okunur.

Cikti : reports/building_heights_ahn5.csv + .meta.json

Calistirma:
    python src/00_acquisition/measure_building_heights.py
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# M-003 / M-012: PROJ dizini, pyproj'u yukleyen laspy/shapely'den ONCE sabitlenir.
import src.common  # noqa: E402,F401

import laspy  # noqa: E402
import shapely  # noqa: E402
from shapely.geometry import shape  # noqa: E402
from shapely.strtree import STRtree  # noqa: E402

from src.common.config import load_acceptance_criteria, resolve  # noqa: E402
from src.common.logging_setup import setup_logging  # noqa: E402
from src.common.meta import write_meta  # noqa: E402

CHUNK = 5_000_000
ZMIN, ZMAX = -12.0, 64.0


def _assert_predicate_direction(logger) -> None:
    """MISTAKES.md M-007: STRtree yuklem yonu her calistirmada FIILEN sinanir."""
    from shapely.geometry import box as _box
    hits = STRtree([_box(0, 0, 10, 10)]).query(
        shapely.points(np.array([5.0, 50.0]), np.array([5.0, 50.0])),
        predicate="within")
    if hits.shape[1] != 1 or hits[0][0] != 0:
        raise RuntimeError(
            f"STRtree yuklem yonu beklenenden farkli: 'within' {hits.shape[1]} "
            f"eslesme verdi, 1 bekleniyordu (shapely {shapely.__version__}).")
    logger.info("STRtree yuklem yonu dogrulandi ('within')")


def _pct_from_hist(hist: np.ndarray, q: float, zmin: float, zbin: float) -> np.ndarray:
    """Bina x z histogramindan q yuzdeligini okur.

    Girdi : hist (n x nbins, int), q (0-1), zmin (m), zbin (m)
    Cikti : n uzunlugunda dizi, yuzdelik degeri (m); noktasiz bina icin NaN
    Birim : m (NAP)
    """
    cum = np.cumsum(hist, axis=1)
    tot = cum[:, -1]
    out = np.full(hist.shape[0], np.nan)
    ok = tot > 0
    if not ok.any():
        return out
    idx = np.argmax(cum >= (tot[:, None] * q), axis=1)
    out[ok] = zmin + (idx[ok] + 0.5) * zbin      # bin MERKEZI
    return out


def main() -> int:
    logger, run_id, _ = setup_logging("measure_building_heights")
    _assert_predicate_direction(logger)

    cfg_all = load_acceptance_criteria()
    cal = cfg_all["storey_height_calibration"]
    if cal["status"] != "SEALED_BEFORE_OBSERVATION":
        logger.warning("storey_height_calibration.status = %s (beklenen: "
                       "SEALED_BEFORE_OBSERVATION)", cal["status"])
    hm = cal["height_measurement"]
    zbin = float(hm["z_bin_m"])
    r_in = float(hm["ground_z"]["buffer_inner_m"])
    r_out = float(hm["ground_z"]["buffer_outer_m"])
    nbins = int(round((ZMAX - ZMIN) / zbin))
    logger.info("Muhurlu yontem | cati=%s | zemin=halka %.1f-%.1f m | z-bin=%.2f m",
                hm["roof_z"]["statistic"], r_in, r_out, zbin)

    status_cfg = cfg_all["stage_0_2"]["status_filter"]
    aoi = resolve("root.aoi")
    area_a = shape(json.loads((aoi / "area_A_analysis.geojson").read_text(
        encoding="utf-8"))["features"][0]["geometry"])
    area_b = shape(json.loads((aoi / "area_B_context.geojson").read_text(
        encoding="utf-8"))["features"][0]["geometry"])

    panden = [
        f for f in json.loads((resolve("data.raw") / "bag" / "bag_pand.geojson")
                              .read_text(encoding="utf-8"))["features"]
        if f["properties"].get("status") in status_cfg["pand_include"]
        and area_b.contains(shape(f["geometry"]).centroid)
    ]
    geoms = [shape(f["geometry"]) for f in panden]
    n = len(geoms)
    in_a = np.array([area_a.contains(g.centroid) for g in geoms])
    areas = np.array([g.area for g in geoms])
    logger.info("Kapsam | B alaninda %d pand (bunlarin %d'i A'da)", n, int(in_a.sum()))

    logger.info("Halka poligonlari uretiliyor (buffer %.1f m \\ %.1f m)...", r_out, r_in)
    rings = [g.buffer(r_out).difference(g.buffer(r_in)) for g in geoms]

    tree_fp = STRtree(geoms)
    tree_rg = STRtree(rings)

    hist6 = np.zeros((n, nbins), dtype=np.int32)      # sinif 6, ayakizi ICINDE
    histg = np.zeros((n, nbins), dtype=np.int32)      # sinif 2, HALKADA

    bminx, bminy, bmaxx, bmaxy = area_b.bounds
    pad = r_out + 1.0                                  # halka B'nin disina tasabilir
    laz = sorted((resolve("data.raw") / "ahn" / "AHN5_T").glob("*.LAZ"))
    logger.info("Islenecek LAZ: %d", len(laz))

    for path in laz:
        n6 = n2 = 0
        with laspy.open(str(path)) as reader:
            for ch in reader.chunk_iterator(CHUNK):
                x = np.asarray(ch.x); y = np.asarray(ch.y); z = np.asarray(ch.z)
                cls = np.asarray(ch.classification)

                m = ((x >= bminx - pad) & (x <= bmaxx + pad)
                     & (y >= bminy - pad) & (y <= bmaxy + pad))
                if not m.any():
                    continue
                x, y, z, cls = x[m], y[m], z[m], cls[m]
                zb = np.clip(((z - ZMIN) / zbin).astype(np.int64), 0, nbins - 1)

                # --- cati: sinif 6, ayakizi ICINDE ---
                s6 = cls == 6
                if s6.any():
                    hit = tree_fp.query(shapely.points(x[s6], y[s6]), predicate="within")
                    if hit.size:
                        pi, bi = hit[0], hit[1]
                        np.add.at(hist6, (bi, zb[s6][pi]), 1)
                        n6 += pi.size

                # --- zemin: sinif 2, HALKADA ---
                s2 = cls == 2
                if s2.any():
                    hit = tree_rg.query(shapely.points(x[s2], y[s2]), predicate="within")
                    if hit.size:
                        pi, bi = hit[0], hit[1]
                        np.add.at(histg, (bi, zb[s2][pi]), 1)
                        n2 += pi.size
        logger.info("%s | sinif6 ayakizi ici: %d | sinif2 halkada: %d", path.name, n6, n2)

    logger.info("Yuzdelikler histogramdan okunuyor...")
    p30 = _pct_from_hist(hist6, 0.30, ZMIN, zbin)
    p70 = _pct_from_hist(hist6, 0.70, ZMIN, zbin)
    p90 = _pct_from_hist(hist6, 0.90, ZMIN, zbin)
    gmed = _pct_from_hist(histg, 0.50, ZMIN, zbin)
    c6 = hist6.sum(axis=1)
    cg = histg.sum(axis=1)

    h = p70 - gmed
    span = p90 - p30

    out = resolve("reports.dir") / "building_heights_ahn5.csv"
    cols = ["bag_id", "alan", "footprint_area_m2", "bouwjaar", "status", "gebruiksdoel",
            "class6_points", "roof_p30_z_nap_m", "roof_p70_z_nap_m", "roof_p90_z_nap_m",
            "roof_span_m", "ground_ring_points", "ground_z_nap_m", "h_measured_m"]
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        for i, f in enumerate(panden):
            pr = f["properties"]
            w.writerow([
                pr["identificatie"], "A" if in_a[i] else "B", f"{areas[i]:.2f}",
                pr.get("bouwjaar") or "", pr.get("status") or "",
                pr.get("gebruiksdoel") or "",
                int(c6[i]),
                "" if np.isnan(p30[i]) else f"{p30[i]:.3f}",
                "" if np.isnan(p70[i]) else f"{p70[i]:.3f}",
                "" if np.isnan(p90[i]) else f"{p90[i]:.3f}",
                "" if np.isnan(span[i]) else f"{span[i]:.3f}",
                int(cg[i]),
                "" if np.isnan(gmed[i]) else f"{gmed[i]:.3f}",
                "" if np.isnan(h[i]) else f"{h[i]:.3f}",
            ])

    ok = ~np.isnan(h)
    logger.info("Olculen bina: %d / %d (%.1f%%)", int(ok.sum()), n, 100 * ok.mean())
    logger.info("Olculemeyen | sinif6 noktasi yok: %d | halkada zemin yok: %d",
                int((c6 == 0).sum()), int((cg == 0).sum()))
    if ok.any():
        logger.info("h_measured_m | medyan %.2f | p10 %.2f | p90 %.2f | max %.2f",
                    float(np.median(h[ok])), float(np.percentile(h[ok], 10)),
                    float(np.percentile(h[ok], 90)), float(np.nanmax(h)))
    neg = int((h[ok] < 0).sum()) if ok.any() else 0
    if neg:
        logger.warning("NEGATIF yukseklik: %d bina — cati zeminden alcak olamaz, "
                       "bu binalarda olcum guvenilmez (raporlanir)", neg)

    write_meta(out, run_id=run_id,
               parameters={"method": "p70(class6 in footprint) - median(class2 in ring)",
                           "z_bin_m": zbin, "ring_inner_m": r_in, "ring_outer_m": r_out,
                           "buildings": n, "buildings_in_a": int(in_a.sum()),
                           "measured": int(ok.sum()), "negative_height": neg,
                           "laz_files": [p.name for p in laz]},
               notes=("Muhurlu yontem: storey_height_calibration.height_measurement "
                      "(commit f2667c1, olcumden ONCE). 3DBAG yukseklikleri "
                      "KULLANILMADI (Bolum 12.10)."))
    logger.info("TAMAM | %s", out.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
