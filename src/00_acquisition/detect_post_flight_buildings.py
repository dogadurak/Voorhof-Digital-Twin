"""Ucus sonrasi yapilmis / yeniden yapilmis binalari tespit eder.

Asama : 0.3  (Karar D-022; kurallar D-020, D-019)
Kapsam: A ve B alanlarindaki TUM panden (status filtreli, centroid kurali)

Esikler `config/acceptance_criteria.yml` -> `post_flight_detection` altindan
OKUNUR. O blok bu scriptten ONCE ayri bir commit ile muhurlenmistir
(commit d4cf95b, status: SEALED_NOT_EXECUTED).

Olculen metrikler (hepsi ayakizi POLIGONU icine dusen noktalar uzerinden):
  building_class_ratio            sinif 6 / tum
  ground_class_ratio              sinif 2 / tum
  single_return_density_above_2m  yerel maaiveld + 2 m ustundeki TEK donuslu
                                  nokta / ayakizi alani
  class6_footprint_coverage       icinde sinif 6 olan 2 m hucre / nokta iceren
                                  2 m hucre

Bellek notu: yerel maaiveld her bina icin ayri gerekir ve medyan tek geciste
hesaplanamaz. Cozum: bina x z-bin histogrami biriktirilir (0,25 m bin), medyan
histogramdan cikarilir, tek donuslu sayim ayni histogramdan esik ustu
toplanir. Boylece LAZ'lar TEK KEZ okunur.

Calistirma:
    python src/00_acquisition/detect_post_flight_buildings.py
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# M-003 / M-012: PROJ dizini, pyproj'u yukleyen laspy/shapely/pyproj'dan ONCE
# sabitlenmeli. Aksi halde pyproj PostgreSQL'in PROJ dizinine kilitlenir ve her
# calistirmada "unable to set PROJ database path" uyarisi basar.
import src.common  # noqa: E402,F401

import laspy
import shapely
from shapely.geometry import shape
from shapely.strtree import STRtree

from src.common.config import load_acceptance_criteria, resolve
from src.common.logging_setup import setup_logging
from src.common.meta import write_meta

CHUNK = 5_000_000
ZMIN, ZMAX, ZBIN = -12.0, 64.0, 0.25
NBINS = int((ZMAX - ZMIN) / ZBIN)
CELL = 2.0          # class6_footprint_coverage hucre boyu (config: 2x2 m)


def _assert_predicate_direction(logger) -> None:
    """MISTAKES.md M-007: yuklem yonu her calistirmada fiilen sinanir."""
    from shapely.geometry import box as _box
    hits = STRtree([_box(0, 0, 10, 10)]).query(
        shapely.points(np.array([5.0, 50.0]), np.array([5.0, 50.0])),
        predicate="within")
    if hits.shape[1] != 1 or hits[0][0] != 0:
        raise RuntimeError(
            f"STRtree yuklem yonu beklenenden farkli: 'within' {hits.shape[1]} "
            f"eslesme verdi, 1 bekleniyordu (shapely {shapely.__version__}).")
    logger.info("STRtree yuklem yonu dogrulandi ('within')")


def main() -> int:
    logger, run_id, _ = setup_logging("detect_post_flight_buildings")
    _assert_predicate_direction(logger)

    cfg_all = load_acceptance_criteria()
    cfg = cfg_all["post_flight_detection"]
    status_cfg = cfg_all["stage_0_2"]["status_filter"]
    if cfg["status"] != "SEALED_NOT_EXECUTED":
        logger.warning("post_flight_detection.status = %s (beklenen: "
                       "SEALED_NOT_EXECUTED)", cfg["status"])
    crit = cfg["post_flight_candidate"]["criteria"]
    k1 = float(crit["K1"]["threshold"])
    k2 = float(crit["K2"]["threshold"])
    k3 = float(crit["K3"]["threshold"])
    r1 = int(cfg["rebuild_suspect"]["definition"]["criteria"]["R1"]["threshold"])
    logger.info("Muhurlu esikler | K1 <= %.2f | K2 >= %.2f | K3 < %.1f p/m2 | "
                "R1 bouwjaar >= %d", k1, k2, k3, r1)

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

    tree = STRtree(geoms)
    total = np.zeros(n, dtype=np.int64)
    c6 = np.zeros(n, dtype=np.int64)
    c2 = np.zeros(n, dtype=np.int64)
    hist_g = np.zeros((n, NBINS), dtype=np.int32)      # sinif 2 z-histogrami
    hist_s = np.zeros((n, NBINS), dtype=np.int32)      # TEK donuslu z-histogrami
    cells_any: set[tuple[int, int, int]] = set()
    cells_c6: set[tuple[int, int, int]] = set()

    bminx, bminy, bmaxx, bmaxy = area_b.bounds
    laz = sorted((resolve("data.raw") / "ahn" / "AHN5_T").glob("*.LAZ"))
    logger.info("Islenecek LAZ: %d", len(laz))

    for path in laz:
        seen = 0
        with laspy.open(str(path)) as reader:
            for ch in reader.chunk_iterator(CHUNK):
                x = np.asarray(ch.x); y = np.asarray(ch.y); z = np.asarray(ch.z)
                cls = np.asarray(ch.classification)
                nret = np.asarray(ch.number_of_returns)

                m = (x >= bminx) & (x <= bmaxx) & (y >= bminy) & (y <= bmaxy)
                if not m.any():
                    continue
                x, y, z, cls, nret = x[m], y[m], z[m], cls[m], nret[m]

                hit = tree.query(shapely.points(x, y), predicate="within")
                if not hit.size:
                    continue
                pi, bi = hit[0], hit[1]          # nokta indeksi, bina indeksi
                seen += pi.size

                np.add.at(total, bi, 1)
                zb = np.clip(((z[pi] - ZMIN) / ZBIN).astype(np.int64), 0, NBINS - 1)

                is6 = cls[pi] == 6
                if is6.any():
                    np.add.at(c6, bi[is6], 1)
                is2 = cls[pi] == 2
                if is2.any():
                    np.add.at(c2, bi[is2], 1)
                    np.add.at(hist_g, (bi[is2], zb[is2]), 1)
                is1r = nret[pi] == 1
                if is1r.any():
                    np.add.at(hist_s, (bi[is1r], zb[is1r]), 1)

                ix = (x[pi] / CELL).astype(np.int64)
                iy = (y[pi] / CELL).astype(np.int64)
                cells_any.update(zip(bi.tolist(), ix.tolist(), iy.tolist()))
                if is6.any():
                    cells_c6.update(zip(bi[is6].tolist(), ix[is6].tolist(),
                                        iy[is6].tolist()))
        logger.info("%s | %d nokta ayakizi icinde", path.name, seen)

    logger.info("Metrikler hesaplaniyor...")
    # --- yerel maaiveld: sinif 2 histogramindan medyan ---
    cum = np.cumsum(hist_g, axis=1)
    tot_g = cum[:, -1]
    ground = np.full(n, np.nan)
    ok = tot_g > 0
    idx = np.argmax(cum >= (tot_g[:, None] / 2.0), axis=1)
    ground[ok] = ZMIN + (idx[ok] + 0.5) * ZBIN

    # --- K3: maaiveld + 2 m ustundeki TEK donuslu nokta ---
    bin_of_2m = np.where(ok, np.clip(((ground + 2.0 - ZMIN) / ZBIN), 0,
                                     NBINS - 1).astype(np.int64), NBINS)
    single_above = np.zeros(n, dtype=np.int64)
    cum_s = np.cumsum(hist_s, axis=1)
    tot_s = cum_s[:, -1]
    for i in range(n):
        b = bin_of_2m[i]
        single_above[i] = tot_s[i] - (cum_s[i, b] if b < NBINS else tot_s[i])
    k3_dens = np.divide(single_above, areas, out=np.zeros(n), where=areas > 0)

    ratio6 = np.divide(c6.astype(float), total.astype(float),
                       out=np.full(n, np.nan), where=total > 0)
    ratio2 = np.divide(c2.astype(float), total.astype(float),
                       out=np.full(n, np.nan), where=total > 0)

    cnt_any = np.zeros(n, dtype=np.int64)
    cnt_c6 = np.zeros(n, dtype=np.int64)
    for b, _, _ in cells_any:
        cnt_any[b] += 1
    for b, _, _ in cells_c6:
        cnt_c6[b] += 1
    cov6 = np.divide(cnt_c6.astype(float), cnt_any.astype(float),
                     out=np.full(n, np.nan), where=cnt_any > 0)

    # --- MUHURLU KURALLARI UYGULA ---
    K1 = (ratio6 <= k1) & ~np.isnan(ratio6)
    K2 = (ratio2 >= k2) & ~np.isnan(ratio2)
    K3 = k3_dens < k3
    n_met = K1.astype(int) + K2.astype(int) + K3.astype(int)
    candidate = n_met == 3
    partial = n_met == 2

    bouwjaar = np.array([int(f["properties"].get("bouwjaar") or 0) for f in panden])
    rebuild = (bouwjaar >= r1) & ~candidate
    ambiguous = rebuild & (bouwjaar == r1)

    return _report(logger, run_id, panden, geoms, areas, in_a, total, c6, c2,
                   ratio6, ratio2, k3_dens, cov6, ground, K1, K2, K3,
                   candidate, partial, rebuild, ambiguous, bouwjaar,
                   k1, k2, k3, r1)


def _fmt(sel, areas, panden):
    """Bolum 14.6 / M-010: hem SAYI hem ALAN."""
    return int(sel.sum()), float(areas[sel].sum())


def _report(logger, run_id, panden, geoms, areas, in_a, total, c6, c2,
            ratio6, ratio2, k3_dens, cov6, ground, K1, K2, K3,
            candidate, partial, rebuild, ambiguous, bouwjaar,
            k1, k2, k3, r1) -> int:
    from collections import Counter
    n = len(panden)
    rep = resolve("reports.dir")

    def rows(sel, extra=()):
        out = []
        for i in np.argsort(-areas * sel)[:int(sel.sum())]:
            p = panden[i]["properties"]
            out.append([p["identificatie"], f"{areas[i]:.2f}", "A" if in_a[i] else "B",
                        p.get("gebruiksdoel") or "", p.get("bouwjaar") or "",
                        p.get("status") or "", int(total[i]),
                        "" if np.isnan(ratio6[i]) else f"{ratio6[i]:.4f}",
                        "" if np.isnan(ratio2[i]) else f"{ratio2[i]:.4f}",
                        f"{k3_dens[i]:.3f}",
                        "" if np.isnan(cov6[i]) else f"{cov6[i]:.4f}",
                        *[e(i) for e in extra]])
        return out

    head = ["bag_id", "footprint_area_m2", "alan", "gebruiksdoel", "bouwjaar",
            "status", "point_count", "building_class_ratio", "ground_class_ratio",
            "single_return_density_above_2m", "class6_footprint_coverage"]

    for name, sel, extra, eh in (
        ("post_flight_buildings.csv", candidate, (), []),
        ("post_flight_suspects.csv", partial,
         (lambda i: "K1" if K1[i] else "", lambda i: "K2" if K2[i] else "",
          lambda i: "K3" if K3[i] else ""), ["K1", "K2", "K3"]),
        ("rebuild_suspects.csv", rebuild,
         (lambda i: "EVET" if ambiguous[i] else "hayir",),
         ["bouwjaar_belirsiz"]),
    ):
        with (rep / name).open("w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(head + eh)
            w.writerows(rows(sel, extra))
        logger.info("%s | %d satir", name, int(sel.sum()))

    nc, ac = _fmt(candidate, areas, panden)
    npar, apar = _fmt(partial, areas, panden)
    nrb, arb = _fmt(rebuild, areas, panden)
    tot_area = float(areas.sum())
    logger.info("=== SONUC (B alani, %d pand, %.0f m2) ===", n, tot_area)
    logger.info("  ucus sonrasi aday : %4d bina (%%%.2f) | %9.0f m2 (%%%.2f)",
                nc, 100*nc/n, ac, 100*ac/tot_area)
    logger.info("  supheli (2/3)     : %4d bina (%%%.2f) | %9.0f m2 (%%%.2f)",
                npar, 100*npar/n, apar, 100*apar/tot_area)
    logger.info("  olasi yeniden yapim: %3d bina (%%%.2f) | %9.0f m2 (%%%.2f)",
                nrb, 100*nrb/n, arb, 100*arb/tot_area)
    logger.info("  bunlarin %d'inde bouwjaar BELIRSIZ (== %d)",
                int(ambiguous.sum()), r1)

    def gd(sel):
        cc = Counter((panden[i]["properties"].get("gebruiksdoel") or "(islev yok)")
                     for i in np.where(sel)[0])
        return cc

    def top5(sel):
        out = []
        for r_, i in enumerate(np.argsort(-areas * sel)[:min(5, int(sel.sum()))], 1):
            p = panden[i]["properties"]
            out.append(f"| {r_} | `{p['identificatie']}` | {areas[i]:,.1f} | "
                       f"{'A' if in_a[i] else 'B'} | "
                       f"{p.get('gebruiksdoel') or '(islev yok)'} | "
                       f"{p.get('bouwjaar')} | "
                       f"{'' if np.isnan(ratio6[i]) else f'{ratio6[i]:.3f}'} | "
                       f"{'' if np.isnan(cov6[i]) else f'{cov6[i]:.3f}'} |")
        return "\n".join(out) or "| — | (yok) | | | | | | |"

    def gdrows(sel):
        c = gd(sel)
        tot = max(1, int(sel.sum()))
        return "\n".join(f"| {k} | {v} | %{100*v/tot:.1f} |"
                         for k, v in c.most_common(8)) or "| — | 0 | |"

    out = rep / "00_stage_0_3_post_flight_detection.md"
    out.write_text(f"""# Ucus sonrasi bina tespiti — A ve B alanlari

**Karar D-022** · run_id `{run_id}` · muhur commit'i `d4cf95b`

> **VERI DONEMI (D-020).** Geometri AHN5 **2023-02-08 / 02-14**; BAG
> oznitelikleri **2026-09**. Arada 3,5 yil var.

Esikler config'ten okundu ve bu hesaptan **once** muhurlendi:
**K1 <= {k1}** · **K2 >= {k2}** · **K3 < {k3} p/m2** · **R1 bouwjaar >= {r1}**

Kapsam: **B alanindaki {n:,} pand** (status filtreli, centroid kurali);
bunlarin **{int(in_a.sum()):,}**'i A alaninda. Toplam ayakizi {tot_area:,.0f} m2.

## 1. Sonuc — HEM SAYI HEM ALAN (Bolum 14.6)

| Grup | Bina | Bina payi | Alan m2 | Alan payi |
|---|---|---|---|---|
| **Ucus sonrasi aday** (K1+K2+K3) | **{nc}** | %{100*nc/n:.2f} | {ac:,.0f} | **%{100*ac/tot_area:.2f}** |
| **Supheli** (3 kosuldan tam 2'si) | **{npar}** | %{100*npar/n:.2f} | {apar:,.0f} | %{100*apar/tot_area:.2f} |
| **Olasi yeniden yapim** (R1) | **{nrb}** | %{100*nrb/n:.2f} | {arb:,.0f} | %{100*arb/tot_area:.2f} |

## 2. Ucus sonrasi adaylar

Kullanim islevi:

| gebruiksdoel | Bina | Pay |
|---|---|---|
{gdrows(candidate)}

Etkiye (alana) gore en buyuk 5:

| # | bag_id | m2 | alan | gebruiksdoel | bouwjaar | sinif 6 orani | sinif 6 kapsama |
|---|---|---|---|---|---|---|---|
{top5(candidate)}

Tam liste: `reports/post_flight_buildings.csv`

## 3. Supheli (3 kosuldan tam 2'si) — KARAR VERILMEDI

| gebruiksdoel | Bina | Pay |
|---|---|---|
{gdrows(partial)}

Etkiye gore en buyuk 5:

| # | bag_id | m2 | alan | gebruiksdoel | bouwjaar | sinif 6 orani | sinif 6 kapsama |
|---|---|---|---|---|---|---|---|
{top5(partial)}

Hangi kosullarin saglandigi CSV'de sutun olarak: `post_flight_suspects.csv`

## 4. Olasi yeniden yapim (sloop-nieuwbouw) — KARAR VERILMEDI

`bouwjaar >= {r1}` **VE** ucus sonrasi aday **degil**. Bu binalarda LiDAR
**eski catiyi** gormus olabilir; Asama 1'de eski geometri yeni binaya
giydirilirse **sessiz hata** olur (D-022).

**{int(ambiguous.sum())} binada `bouwjaar == {r1}` ve bu BELIRSIZDIR:** BAG
yalnizca yil verir, ucus Subat 2023'tedir; bina ucustan once de sonra da
yapilmis olabilir.

| gebruiksdoel | Bina | Pay |
|---|---|---|
{gdrows(rebuild)}

Etkiye gore en buyuk 5:

| # | bag_id | m2 | alan | gebruiksdoel | bouwjaar | sinif 6 orani | sinif 6 kapsama |
|---|---|---|---|---|---|---|---|
{top5(rebuild)}

Tam liste: `reports/rebuild_suspects.csv`

**`class6_footprint_coverage` nasil okunur:** ayakizi icindeki 2 m hucrelerden
icinde en az bir sinif 6 noktasi bulunanlarin orani. **Dusuk deger**, eski
catinin yeni ayakizini ortmedigini — yani ayakizinin degistigini — dusundurur.
**SINIRLAMA:** bitisik nizamda komsu binanin cati noktalari ayakizina tasip
orani **yukseltebilir**; Voorhof'ta bitisik nizam yaygindir. Bu metrik tek
basina karar vermez (D-022).

## 5. Ne yapilmadi

- Bu rapor **hicbir bina icin karar vermez**. Ucus sonrasi adaylar D-020
  geregi `estimated_lod1` veya `footprint_only` olur; supheli ve yeniden
  yapim listeleri **yalnizca uyaridir**.
- Yeniden yapim listesi **gorsel olarak dogrulanmamistir** (Bolum 12.13).
  Amacli ornek `0503100000038177` gorsel orneklemdedir.
""", encoding="utf-8")

    write_meta(out, run_id=run_id,
               parameters={"n_panden_B": n, "n_in_A": int(in_a.sum()),
                           "candidates": nc, "candidate_area_m2": ac,
                           "partial": npar, "rebuild": nrb,
                           "ambiguous_bouwjaar": int(ambiguous.sum()),
                           "K1": k1, "K2": k2, "K3": k3, "R1": r1},
               notes="Esikler config'ten okundu; muhur commit'i d4cf95b (D-022).")
    logger.info("TAMAM | %s", out.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
