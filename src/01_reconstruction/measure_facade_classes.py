"""AHN5 verimizde bina CEPHELERINE dusen noktalarin sinifini olcer.

Asama : 1 hazirlik (P-012 ve D-017 girdisi)
Soru  : AHN4 taniminda cepheler sinif 6 (bebouwing) idi. AHN programinin 2024
        calisma raporu (WP1) AHN5'te cephelerin sinif 1 (overig) oldugunu
        soyluyor. Bu tanim BIZIM verimizde gecerli mi?

Yontem `config/acceptance_criteria.yml` -> `facade_class_measurement` altindan
OKUNUR. O blok bu scriptten ONCE ayri commit'lerle muhurlenmistir
(4b6ad61, b353121; status: SEALED_BEFORE_OBSERVATION).

    cephe bolgesi (bina i):
        yatay : footprint_i.buffer(+0,5) \\ footprint_i.buffer(-0,5)
                \\ (diger tum panden ayakizlerinin birlesimi)
        dusey : ground_z_i + 1,5  <=  z  <=  roof_p30_i - 1,0
    kontrol bolgesi (bina i):
        footprint_i.buffer(-1,0) icinde, z >= roof_p30_i

    d = ayakizi sinirina yatay uzaklik (ic negatif, dis pozitif)

Girdi : reports/building_heights_ahn5.csv (ground_z, roof_p30, h_measured —
        muhurlu yukseklik olcumunun ciktisi), data/raw/bag/bag_pand.geojson,
        data/raw/ahn/AHN5_T/*.LAZ
Cikti : reports/facade_class_measurement_ahn5.csv (+ .meta.json)
        reports/01_prep_facade_class_measurement.md (+ .meta.json)

Calistirma:
    python src/01_reconstruction/measure_facade_classes.py
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
from src.common.meta import git_commit, utc_now, write_meta  # noqa: E402

CHUNK = 5_000_000
NCLS = 256
REPORT_CLASSES = [1, 2, 6, 9, 14, 26]          # WP1 §3.1.1 kodlari (+0 yok sayilmaz: "diger")
SIDE_IN, SIDE_OUT = 0, 1


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


def _share(counts: np.ndarray, cls: int) -> float:
    """Sinif `cls`'nin toplam icindeki payi. Girdi: sinif sayim vektoru. Birim: oran (0-1)."""
    tot = counts.sum()
    return float(counts[cls] / tot) if tot else float("nan")


def _fmt(v: float, nd: int = 3) -> str:
    return "—" if np.isnan(v) else f"{v:.{nd}f}"


def main() -> int:
    logger, run_id, _ = setup_logging("measure_facade_classes")
    _assert_predicate_direction(logger)

    cfg = load_acceptance_criteria()["facade_class_measurement"]
    if cfg["status"] != "SEALED_BEFORE_OBSERVATION":
        raise RuntimeError(f"facade_class_measurement.status = {cfg['status']}; "
                           "muhursuz yontemle olcum yapilmaz (Bolum 12.2)")
    v = cfg["interpretation_rule"]["values"]
    half = float(v["band_half_width_m"])
    wall = float(v["wall_band_m"])
    z_lo_off = float(v["zone_bottom_above_ground_m"])
    z_hi_off = float(v["zone_top_below_roof_p30_m"])
    inset = float(v["control_inset_m"])
    logger.info("Muhurlu yontem | bant +/-%.1f m | z: zemin+%.1f .. p30-%.1f | duvar |d|<=%.1f",
                half, z_lo_off, z_hi_off, wall)

    # --- olculmus yukseklikler (muhurlu yukseklik olcumunun ciktisi) ---
    hcsv = resolve("reports.dir") / "building_heights_ahn5.csv"
    rows = list(csv.DictReader(hcsv.open(encoding="utf-8")))
    logger.info("Yukseklik tablosu: %d satir", len(rows))

    # --- TUM panden (komsu cikarimi icin status filtresi YOK — muhafazakar) ---
    feats = json.loads((resolve("data.raw") / "bag" / "bag_pand.geojson")
                       .read_text(encoding="utf-8"))["features"]
    all_ids = [f["properties"]["identificatie"] for f in feats]
    all_geoms = [shape(f["geometry"]) for f in feats]
    geom_by_id = dict(zip(all_ids, all_geoms))
    tree_all = STRtree(all_geoms)
    logger.info("BAG panden (komsu cikarimi icin, tumu): %d", len(all_geoms))

    # --- kapsam ---
    sel = []
    n_low = n_zone = n_nogeom = 0
    for r in rows:
        if not r["h_measured_m"]:
            continue
        h = float(r["h_measured_m"])
        if h < float(v["min_h_measured_m"]):
            n_low += 1
            continue
        zlo = float(r["ground_z_nap_m"]) + z_lo_off
        zhi = float(r["roof_p30_z_nap_m"]) - z_hi_off
        if zhi - zlo < float(v["min_zone_height_m"]):
            n_zone += 1
            continue
        g = geom_by_id.get(r["bag_id"])
        if g is None:
            n_nogeom += 1
            continue
        sel.append((r, g, zlo, zhi))
    n = len(sel)
    logger.info("Kapsam | secilen %d | h<%.1f m: %d | cephe bolgesi <%.1f m: %d | geometri yok: %d",
                n, float(v["min_h_measured_m"]), n_low, float(v["min_zone_height_m"]),
                n_zone, n_nogeom)
    if n_nogeom:
        logger.warning("%d bina icin BAG geometrisi bulunamadi — olcume girmedi", n_nogeom)

    # --- bantlar ---
    logger.info("Bantlar uretiliyor (komsu ayakizleri cikariliyor)...")
    geoms = [s[1] for s in sel]
    bnds = np.array([g.boundary for g in geoms], dtype=object)
    garr = np.array(geoms, dtype=object)
    bands, ctrls = [], []
    n_neigh_cut = 0
    n_repaired = 0
    for r, g, _, _ in sel:
        outer = g.buffer(half)
        band = outer.difference(g.buffer(-half))
        idx = tree_all.query(outer, predicate="intersects")
        others = [all_geoms[j] for j in idx
                  if all_ids[j] != r["bag_id"] and not all_geoms[j].equals(g)]
        if others:
            try:
                band = band.difference(shapely.union_all(others))
            except shapely.errors.GEOSException as exc:
                # Bolum 12.8: tek bozuk geometri calismayi durdurmaz; onarilir ve loglanir
                logger.warning("%s: komsu cikarimi GEOS hatasi (%s) — make_valid ile tekrar",
                               r["bag_id"], exc)
                band = shapely.make_valid(band).difference(
                    shapely.union_all([shapely.make_valid(o) for o in others]))
                n_repaired += 1
            n_neigh_cut += 1
        bands.append(band)
        ctrls.append(g.buffer(-inset))
    logger.info("Komsu ayakizi cikarilan bina: %d / %d | geometri onarilan: %d",
                n_neigh_cut, n, n_repaired)
    band_area = np.array([b.area for b in bands])
    ctrl_ok = np.array([not c.is_empty for c in ctrls])

    zlo = np.array([s[2] for s in sel])
    zhi = np.array([s[3] for s in sel])
    p30 = np.array([float(s[0]["roof_p30_z_nap_m"]) for s in sel])

    tree_band = STRtree(bands)
    ctrl_idx = np.flatnonzero(ctrl_ok)
    tree_ctrl = STRtree([ctrls[i] for i in ctrl_idx])

    fac = np.zeros((n, 2, NCLS), dtype=np.int64)     # bina x (ic,dis) x sinif
    walln = np.zeros((n, NCLS), dtype=np.int64)      # |d| <= wall olanlar
    ctl = np.zeros((n, NCLS), dtype=np.int64)        # kontrol bolgesi

    allb = shapely.union_all(bands + [ctrls[i] for i in ctrl_idx])
    bminx, bminy, bmaxx, bmaxy = allb.bounds
    laz = sorted((resolve("data.raw") / "ahn" / "AHN5_T").glob("*.LAZ"))
    logger.info("Islenecek LAZ: %d", len(laz))

    for path in laz:
        nf = nc = 0
        with laspy.open(str(path)) as reader:
            for ch in reader.chunk_iterator(CHUNK):
                x = np.asarray(ch.x); y = np.asarray(ch.y); z = np.asarray(ch.z)
                cls = np.asarray(ch.classification).astype(np.int64)
                m = (x >= bminx) & (x <= bmaxx) & (y >= bminy) & (y <= bmaxy)
                if not m.any():
                    continue
                x, y, z, cls = x[m], y[m], z[m], cls[m]
                pts = shapely.points(x, y)

                # --- cephe bolgesi ---
                hit = tree_band.query(pts, predicate="within")
                if hit.size:
                    pi, bi = hit[0], hit[1]
                    keep = (z[pi] >= zlo[bi]) & (z[pi] <= zhi[bi])
                    pi, bi = pi[keep], bi[keep]
                    if pi.size:
                        p = pts[pi]
                        d = shapely.distance(p, bnds[bi])
                        inside = shapely.contains(garr[bi], p)
                        side = np.where(inside, SIDE_IN, SIDE_OUT)
                        np.add.at(fac, (bi, side, cls[pi]), 1)
                        w = d <= wall
                        np.add.at(walln, (bi[w], cls[pi][w]), 1)
                        nf += pi.size

                # --- kontrol bolgesi (cati) ---
                hit = tree_ctrl.query(pts, predicate="within")
                if hit.size:
                    pi, ci = hit[0], hit[1]
                    bi = ctrl_idx[ci]
                    keep = z[pi] >= p30[bi]
                    np.add.at(ctl, (bi[keep], cls[pi][keep]), 1)
                    nc += int(keep.sum())
        logger.info("%s | cephe bolgesi: %d nokta | kontrol: %d nokta", path.name, nf, nc)

    # ------------------------------------------------------------------ analiz
    pool_in = fac[:, SIDE_IN].sum(axis=0)
    pool_out = fac[:, SIDE_OUT].sum(axis=0)
    pool_all = pool_in + pool_out
    pool_ctl = ctl.sum(axis=0)
    pool_wall = walln.sum(axis=0)

    s6_in, s6_out = _share(pool_in, 6), _share(pool_out, 6)
    s1_all = _share(pool_all, 1)
    s6_ctl = _share(pool_ctl, 6)
    wc1 = float(pool_wall[1] / pool_all[1]) if pool_all[1] else float("nan")
    wc6 = float(pool_wall[6] / pool_all[6]) if pool_all[6] else float("nan")
    # Duzgun dagilimdaki beklenen duvar payi: bant alani ~ 2*half*cevre (komsu
    # cikarimi yuzunden yaklasik). Yalniz baglam icin raporlanir; karar esigi degil.
    uniform_wall = wall / half

    nb = fac.sum(axis=(1, 2))
    has = nb > 0
    b6 = np.full(n, np.nan)
    b6[has] = fac[has][:, :, 6].sum(axis=1) / nb[has]

    # --- muhurlu okuma kurali ---
    if np.isnan(s6_ctl) or s6_ctl < float(v["control_min_class6_share"]):
        verdict = "UNINTERPRETABLE"
    elif (s6_in < float(v["wp1_max_class6_share"]) and s6_out < float(v["wp1_max_class6_share"])
          and wc1 > float(v["wp1_min_class1_wall_concentration"])):
        verdict = "WP1_AHN5_DEFINITION_HOLDS"
    elif s6_in > float(v["ahn4_min_class6_share"]) and s6_out > float(v["ahn4_min_class6_share"]):
        verdict = "AHN4_DEFINITION_HOLDS"
    else:
        verdict = "MIXED"
    logger.info("Havuz | sinif6 ic %.3f dis %.3f | sinif1 %.3f | duvar yogunlasmasi s1 %.3f s6 %.3f "
                "| kontrol s6 %.3f | KARAR: %s", s6_in, s6_out, s1_all, wc1, wc6, s6_ctl, verdict)

    # ------------------------------------------------------------------ CSV
    rep = resolve("reports.dir")
    out_csv = rep / "facade_class_measurement_ahn5.csv"
    cols = (["bag_id", "alan", "h_measured_m", "band_area_m2", "zone_z_lo_nap_m", "zone_z_hi_nap_m"]
            + [f"facade_in_c{c}" for c in REPORT_CLASSES] + ["facade_in_other"]
            + [f"facade_out_c{c}" for c in REPORT_CLASSES] + ["facade_out_other"]
            + ["wall_c1", "wall_c6", "control_points", "control_c6", "facade_class6_share"])
    with out_csv.open("w", newline="", encoding="utf-8") as fh:
        wr = csv.writer(fh)
        wr.writerow(cols)
        for i, (r, _, _, _) in enumerate(sel):
            fin, fout = fac[i, SIDE_IN], fac[i, SIDE_OUT]
            wr.writerow(
                [r["bag_id"], r["alan"], r["h_measured_m"], f"{band_area[i]:.2f}",
                 f"{zlo[i]:.2f}", f"{zhi[i]:.2f}"]
                + [int(fin[c]) for c in REPORT_CLASSES]
                + [int(fin.sum() - fin[REPORT_CLASSES].sum())]
                + [int(fout[c]) for c in REPORT_CLASSES]
                + [int(fout.sum() - fout[REPORT_CLASSES].sum())]
                + [int(walln[i, 1]), int(walln[i, 6]), int(ctl[i].sum()), int(ctl[i, 6]),
                   "" if np.isnan(b6[i]) else f"{b6[i]:.4f}"])
    logger.info("CSV yazildi: %s (%d satir)", out_csv.name, n)

    # ------------------------------------------------------------------ rapor
    def cls_table(title_counts: list[tuple[str, np.ndarray]]) -> list[str]:
        head = "| Bolge | toplam | " + " | ".join(f"sinif {c}" for c in REPORT_CLASSES) + " | diger |"
        sep = "|" + "---|" * (len(REPORT_CLASSES) + 3)
        lines = [head, sep]
        for name, cnt in title_counts:
            tot = int(cnt.sum())
            other = int(tot - cnt[REPORT_CLASSES].sum())
            cells = [f"{int(cnt[c]):,} ({_fmt(cnt[c] / tot if tot else np.nan, 3)})"
                     for c in REPORT_CLASSES]
            lines.append(f"| {name} | {tot:,} | " + " | ".join(cells)
                         + f" | {other:,} |")
        return lines

    order = np.argsort(-nb)[:5]
    top5 = ["| bag_id | alan | h (m) | cephe noktasi | sinif 6 payi | sinif 1 payi |",
            "|---|---|---|---|---|---|"]
    for i in order:
        tot = int(nb[i])
        c1 = int(fac[i, :, 1].sum())
        top5.append(f"| `{sel[i][0]['bag_id']}` | {sel[i][0]['alan']} | {sel[i][0]['h_measured_m']} "
                    f"| {tot:,} | {_fmt(b6[i])} | {_fmt(c1 / tot if tot else np.nan)} |")

    bh = b6[has]
    n_nopts = int((~has).sum())
    rule = cfg["interpretation_rule"]
    md = [
        "# Cephe noktasi sinif olcumu — AHN5 (Asama 1 hazirlik)",
        "",
        "> **Veri donemi:** geometri AHN5 2023-02-08/14 · oznitelik BAG 2026-09 (D-020).",
        "> **Yontem:** `config/acceptance_criteria.yml` -> `facade_class_measurement`, "
        "olcumden ONCE muhurlendi (commit 4b6ad61, b353121). Bu rapor o yontemi "
        "DEGISTIRMEDEN uygular.",
        "> **Ne dogrulaniyor:** WP1 (2024) calisma raporundaki AHN5 sinif taniminin "
        "bizim veride gecerliligi. Referans bir BELGE tanimidir; bu olcum bagimsiz "
        "bir ground truth DEGILDIR (ayni AHN5 noktalari).",
        "",
        f"run_id: `{run_id}` · git_commit: `{git_commit()}` · calistirma (UTC): {utc_now()}",
        "",
        "## Sonuc (muhurlu okuma kurali)",
        "",
        f"**{verdict}**",
        "",
        "| Olcu | Deger | Muhurlu esik |",
        "|---|---|---|",
        f"| Kontrol (cati) bolgesi sinif 6 payi | {_fmt(s6_ctl)} | >= {v['control_min_class6_share']} (yorum sarti) |",
        f"| Cephe bolgesi sinif 6 payi — ic yari (d<0) | {_fmt(s6_in)} | WP1: < {v['wp1_max_class6_share']} · AHN4: > {v['ahn4_min_class6_share']} |",
        f"| Cephe bolgesi sinif 6 payi — dis yari (d>0) | {_fmt(s6_out)} | WP1: < {v['wp1_max_class6_share']} · AHN4: > {v['ahn4_min_class6_share']} |",
        f"| Sinif 1 noktalarinin duvar cizgisinde (abs(d) <= {wall} m) payi | {_fmt(wc1)} | WP1: > {v['wp1_min_class1_wall_concentration']} |",
        f"| Sinif 6 noktalarinin duvar cizgisinde payi | {_fmt(wc6)} | — (yalniz raporlanir) |",
        f"| Duzgun dagilimda beklenen duvar payi (yaklasik, {wall}/{half}) | {_fmt(uniform_wall, 2)} | — (baglam) |",
        "",
        "## Kapsam",
        "",
        f"- Yukseklik tablosunda {len(rows):,} bina; secilen **{n:,}**.",
        f"- Dislanan: h < {v['min_h_measured_m']} m: {n_low:,} · cephe bolgesi < "
        f"{v['min_zone_height_m']} m: {n_zone:,} · BAG geometrisi bulunamadi: {n_nogeom:,} · "
        f"yuksekligi olculemeyen binalar zaten tabloda bos (kapsam disi).",
        f"- Komsu ayakizi cikarilan bina: {n_neigh_cut:,} / {n:,}.",
        f"- Cephe bolgesinde hic noktasi olmayan bina: {n_nopts:,}.",
        "",
        "## Havuzlanmis sinif dagilimi (nokta agirlikli)",
        "",
        *cls_table([("cephe — ic yari", pool_in), ("cephe — dis yari", pool_out),
                    ("cephe — toplam", pool_all), (f"duvar cizgisi abs(d)<={wall}", pool_wall),
                    ("KONTROL: cati", pool_ctl)]),
        "",
        "## Bina basina sinif 6 payi (sayiya gore)",
        "",
        f"Noktasi olan {bh.size:,} bina: medyan {_fmt(np.median(bh) if bh.size else np.nan)} · "
        f"p10 {_fmt(np.percentile(bh, 10) if bh.size else np.nan)} · "
        f"p90 {_fmt(np.percentile(bh, 90) if bh.size else np.nan)}.",
        "",
        "Cephe bolgesinde en cok noktasi olan 5 bina (etkiye gore, Bolum 14.6):",
        "",
        *top5,
        "",
        "## Okuma kurali (muhurlu metin, degistirilmedi)",
        "",
        f"- WP1_AHN5_DEFINITION_HOLDS: {rule['WP1_AHN5_DEFINITION_HOLDS'].strip()}",
        f"- AHN4_DEFINITION_HOLDS: {rule['AHN4_DEFINITION_HOLDS'].strip()}",
        f"- MIXED: {rule['MIXED'].strip()}",
        f"- Kontrol sarti: {rule['control_required'].strip()}",
        "",
        "## Sinirlamalar",
        "",
        "- Sinif 1 AHN5'te bitki ortusunu da icerir. Duvara yakin agac/cali noktalari "
        "cephe bolgesine dusebilir; duvar yogunlasmasi olcusu bunu kismen ayirir, "
        "tamamen ayiramaz.",
        "- BAG ayakizi bovenaanzicht (ust gorunus) sinirdir; sacak tasmasi olan binalarda "
        "duvar ayakizinin ICINDE kalir. Ic/dis yari bu yuzden ayri raporlanir.",
        "- Balkon, galeri (galerijflat) ve sacak noktalari cephe bolgesine duser; "
        "bunlarin 'cati' mi 'cephe' mi sayildigi WP1'de tanimli degildir.",
        "- Iki secili binanin bantlari (ayakizlari disinda) cakisabilir; o noktalar iki "
        "binaya da sayilir.",
        "- Esikler (0,20 / 0,50 / 0,60 / 0,80) ajanin on-kaydidir, bir belgeden "
        "alinmamistir.",
        "- Bu olcum AHN5'in BESTEK'ini degil, calisma raporundaki tanimi sinar; bestek "
        "okunmadi.",
        "",
    ]
    out_md = rep / "01_prep_facade_class_measurement.md"
    out_md.write_text("\n".join(md), encoding="utf-8")

    params = {k: v[k] for k in v} | {"buildings_selected": n, "verdict": verdict,
                                    "laz_files": [p.name for p in laz]}
    for target in (out_csv, out_md):
        write_meta(target, run_id=run_id, inputs=[hcsv], parameters=params,
                   software={"laspy": laspy.__version__, "shapely": shapely.__version__,
                             "numpy": np.__version__},
                   notes="Muhurlu yontem: facade_class_measurement (commit 4b6ad61, b353121).")
    logger.info("TAMAM | %s | %s", out_csv.name, out_md.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
