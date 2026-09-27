"""AHN4 girdi kalite kapisi (Bolum 12.12) — kriter 1-C-c'nin on-kosulu (D-036).

Asama : 1 hazirlik
Kural `config/acceptance_criteria.yml` -> `input_gate_ahn4` altindadir; bu
scriptten ONCE ayri commit ile muhurlenmistir (5342d47).

Olcer:
  G4-A/B  medyan nokta yogunlugu (10 m hucre, merkezi B icinde, tum siniflar)
  G4-C    ucus tarihi: gps_time -> UTC (Adjusted Standard GPS Time; AHN5 ile ayni cozum)
  G4-D    sinif dagilimi (kodlar veriden okunur)
  G4-E    sifir donuslu hucre orani + 1-C-a kumesinde 1,0 m iceriden daraltilmis
          ayakizinda AHN4 sinif 6 nokta ADEDI (sonuc degil)
  G4-F    ATTRIBUTION.md'de AHN4 satiri dolu mu (lisans script icinde YAZILMAZ —
          M-005 besinci tekrar dersi; kaynak insan kaydindadir)

Cikti : reports/01_prep_ahn4_input_gate.md (+ .meta.json)
"""

from __future__ import annotations

import collections
import csv
import datetime as dt
import json
import re
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import src.common  # noqa: E402,F401  (M-003: PROJ once)

import laspy  # noqa: E402
import shapely  # noqa: E402
from shapely.geometry import shape  # noqa: E402
from shapely.strtree import STRtree  # noqa: E402

from src.common.config import load_acceptance_criteria, resolve  # noqa: E402
from src.common.logging_setup import setup_logging  # noqa: E402
from src.common.meta import git_commit, utc_now, write_meta  # noqa: E402

CHUNK = 5_000_000
GPS_EPOCH = dt.datetime(1980, 1, 6, tzinfo=dt.timezone.utc)
LEAP_S = 18                  # GPS-UTC farki 2017-01-01'den beri 18 s (tarih icin ihmal edilebilir)
WEEK_S = 604_800
AHN5_FLIGHT_START = dt.date(2023, 2, 8)   # D-020, gps_time'dan olculdu


def _gps_to_utc(t: float) -> dt.datetime:
    """Adjusted Standard GPS Time (GPS saniyesi - 1e9) -> UTC. Birim: s."""
    return GPS_EPOCH + dt.timedelta(seconds=float(t) + 1e9 - LEAP_S)


def main() -> int:
    logger, run_id, _ = setup_logging("verify_ahn4_gate")
    cfg_all = load_acceptance_criteria()
    gate = cfg_all["input_gate_ahn4"]
    if gate["status"] != "SEALED_BEFORE_OBSERVATION":
        raise RuntimeError("input_gate_ahn4 muhursuz — olcum yapilmaz (Bolum 12.2)")
    chk = gate["checks"]
    hard = float(chk["G4-A_density_hard"]["threshold"])
    expect = float(chk["G4-B_density_expectation"]["threshold"])
    cell = float(cfg_all["input_gate_ahn"]["method"]["grid_cell_m"])
    inset = float(cfg_all["stage_1"]["criteria"][[c["id"] for c in cfg_all["stage_1"]["criteria"]]
                                                 .index("1-C")]["components"]["c_temporal_ahn4"]
                  ["points"]["footprint_inset_m"])
    logger.info("Muhurlu kapi | hucre %.0f m | sert >= %.1f | beklenti >= %.1f | ic daraltma %.1f m",
                cell, hard, expect, inset)

    aoi = resolve("root.aoi")
    area_b = shape(json.loads((aoi / "area_B_context.geojson").read_text(encoding="utf-8"))
                   ["features"][0]["geometry"])
    bminx, bminy, bmaxx, bmaxy = area_b.bounds
    nx, ny = int(np.ceil((bmaxx - bminx) / cell)), int(np.ceil((bmaxy - bminy) / cell))
    counts = np.zeros((nx, ny), dtype=np.int64)

    # --- 1-C-a kumesi + 3DBAG oznitelikleri (bouwjaar filtresi tarih olculunce uygulanir) ---
    rep = resolve("reports.dir")
    eval_ids = [r["bag_id"] for r in csv.DictReader((rep / "01_prep_1Ca_eval_set.csv").open(encoding="utf-8"))]
    ref = {r["bag_id"]: r for r in csv.DictReader(
        (rep / "01_prep_3dbag_rmse_reference.csv").open(encoding="utf-8"))}
    feats = {f["properties"]["identificatie"]: f for f in json.loads(
        (resolve("data.raw") / "bag" / "bag_pand.geojson").read_text(encoding="utf-8"))["features"]}
    inner, inner_ids, n_empty = [], [], 0
    for b in eval_ids:
        g = shape(feats[b]["geometry"]).buffer(-inset)
        if g.is_empty:
            n_empty += 1
            continue
        inner.append(g); inner_ids.append(b)
    tree = STRtree(inner)
    c6_in = np.zeros(len(inner), dtype=np.int64)
    logger.info("1-C-a kumesi %d bina | daraltma sonrasi bos (cok dar) %d", len(eval_ids), n_empty)

    classes: collections.Counter = collections.Counter()
    strip_min: dict[int, float] = {}
    strip_max: dict[int, float] = {}
    gmin, gmax = np.inf, -np.inf
    laz = sorted((resolve("data.raw") / "ahn" / "AHN4_T").glob("*.LAZ"))
    for path in laz:
        n_file = 0
        with laspy.open(str(path)) as rd:
            for ch in rd.chunk_iterator(CHUNK):
                x = np.asarray(ch.x); y = np.asarray(ch.y)
                m = (x >= bminx) & (x < bmaxx) & (y >= bminy) & (y < bmaxy)
                if not m.any():
                    continue
                x, y = x[m], y[m]
                cls = np.asarray(ch.classification)[m]
                gps = np.asarray(ch.gps_time)[m]
                psid = np.asarray(ch.point_source_id)[m]
                np.add.at(counts, (((x - bminx) / cell).astype(np.int64),
                                   ((y - bminy) / cell).astype(np.int64)), 1)
                u, c = np.unique(cls, return_counts=True)
                classes.update(dict(zip(u.tolist(), c.tolist())))
                gmin, gmax = min(gmin, float(gps.min())), max(gmax, float(gps.max()))
                for s in np.unique(psid):
                    gs = gps[psid == s]
                    strip_min[int(s)] = min(strip_min.get(int(s), np.inf), float(gs.min()))
                    strip_max[int(s)] = max(strip_max.get(int(s), -np.inf), float(gs.max()))
                s6 = cls == 6
                if s6.any():
                    hit = tree.query(shapely.points(x[s6], y[s6]), predicate="within")
                    if hit.size:
                        np.add.at(c6_in, hit[1], 1)
                n_file += int(m.sum())
        logger.info("%s | B bbox icinde %d nokta", path.name, n_file)

    # --- G4-A/B yogunluk ---
    cx = bminx + (np.arange(nx) + 0.5) * cell
    cy = bminy + (np.arange(ny) + 0.5) * cell
    gx, gy = np.meshgrid(cx, cy, indexing="ij")
    in_b = shapely.contains_xy(area_b, gx, gy)
    dens = counts[in_b] / (cell * cell)
    med = float(np.median(dens)); p10 = float(np.percentile(dens, 10))
    zero_pct = float(100 * np.mean(counts[in_b] == 0))
    a_ok = med >= hard
    b_ok = med >= expect

    # --- G4-C tarih ---
    resolvable = gmin > WEEK_S
    d_first = _gps_to_utc(gmin) if resolvable else None
    d_last = _gps_to_utc(gmax) if resolvable else None
    c_ok = bool(resolvable and d_last.date() < AHN5_FLIGHT_START)
    flight_year = d_first.year if resolvable else None       # muhurlu: EN ERKEN yil
    days = sorted({_gps_to_utc(v).date() for v in strip_min.values()}) if resolvable else []

    # --- G4-D sinif ---
    d_ok = classes.get(6, 0) > 0

    # --- G4-E olculebilirlik (adet; sonuc degil) ---
    n20 = {b: int(c) for b, c in zip(inner_ids, c6_in)}

    def byear(b: str) -> int:
        v = feats[b]["properties"].get("bouwjaar")
        return int(v) if str(v).isdigit() else 0
    set_c = [b for b in inner_ids
             if flight_year and byear(b) < flight_year
             and str(ref.get(b, {}).get("b3_mutatie_ahn4_ahn5")) == "False"]
    n_by_year = sum(1 for b in inner_ids if flight_year and byear(b) >= flight_year)
    n_by_mut = sum(1 for b in inner_ids if str(ref.get(b, {}).get("b3_mutatie_ahn4_ahn5")) != "False")
    measurable = sum(1 for b in set_c if n20[b] >= 20)

    # --- G4-F lisans (insan kaydi) ---
    attr = Path(resolve("documents.attribution")).read_text(encoding="utf-8")
    row = next((ln for ln in attr.splitlines() if re.match(r"\|\s*1b\s*\|.*AHN4", ln)), "")
    f_ok = bool(row) and "TODO" not in row

    checks = [
        ("G4-A yogunluk (sert)", f"medyan {med:.2f} p/m2 (p10 {p10:.2f})", f">= {hard}", a_ok, True),
        ("G4-B yogunluk (beklenti)", f"medyan {med:.2f} p/m2", f">= {expect} (UYARI)", b_ok, False),
        ("G4-C ucus tarihi", (f"{d_first:%Y-%m-%d} .. {d_last:%Y-%m-%d} UTC; ucus gunleri {len(days)}"
                              if resolvable else "COZULEMEDI (hafta zamani)"),
         "cozulebilir VE < 2023-02-08", c_ok, True),
        ("G4-D sinif dagilimi", ", ".join(f"{k}: {v:,}" for k, v in sorted(classes.items())),
         "sinif 6 var", d_ok, True),
        ("G4-E kapsama", f"sifir donuslu hucre %{zero_pct:.2f}; 1-C-c kumesi {len(set_c)} bina, "
                         f">=20 sinif-6 noktasi olan {measurable}", "esik yok (rapor)", True, False),
        ("G4-F lisans", "ATTRIBUTION.md satir 1b " + ("dolu" if f_ok else "YOK/TODO"),
         "birincil kaynaktan okunmus", f_ok, True),
    ]
    overall = all(ok for _, _, _, ok, blocking in checks if blocking)
    for n, v, t, ok, blk in checks:
        logger.info("%s | %s | %s | %s", n, v, t, "PASS" if ok else ("FAIL" if blk else "UYARI"))
    logger.info("KAPI: %s | AHN4 ucus yili (en erken): %s", "PASS" if overall else "FAIL", flight_year)

    tbl = ["| Kontrol | Olculen | Muhurlu kural | Sonuc |", "|---|---|---|---|"]
    for n, v, t, ok, blk in checks:
        tbl.append(f"| {n} | {v} | {t} | **{'PASS' if ok else ('FAIL' if blk else 'UYARI')}** |")
    strips = ["| Ucus gunu (UTC) | serit sayisi |", "|---|---|"]
    per_day = collections.Counter(_gps_to_utc(v).date() for v in strip_min.values()) if resolvable else {}
    for d, k in sorted(per_day.items()):
        strips.append(f"| {d} | {k} |")
    md = [
        "# AHN4 girdi kalite kapisi (Bolum 12.12) — kriter 1-C-c on-kosulu",
        "",
        "> **Veri donemi:** 1-C-c modeli AHN5 2023-02-08/14'ten kurar; bu kapi AHN4'u olcer.",
        "> **Kural:** `config/acceptance_criteria.yml` -> `input_gate_ahn4`, olcumden ONCE "
        "muhurlendi (5342d47). Bu rapor 1-C-c'nin SONUCUNU icermez; yalnizca girdiyi olcer.",
        "",
        f"run_id: `{run_id}` · git_commit: `{git_commit()}` · calistirma (UTC): {utc_now()}",
        "",
        f"## Genel sonuc: **{'PASS' if overall else 'FAIL'}**",
        "",
        *tbl,
        "",
        f"**1-C-c kumesi icin AHN4 ucus yili (muhurlu: en erken yil): {flight_year}.** "
        f"1-C-a kumesi {len(eval_ids)} bina -> daraltma sonrasi bos {n_empty} -> "
        f"bouwjaar >= {flight_year} cikan {n_by_year} -> mutasyon bayragi True/bilinmeyen "
        f"cikan {n_by_mut} -> **1-C-c kumesi {len(set_c)}**, bunlardan >= 20 sinif-6 "
        f"noktasi olan {measurable}.",
        "",
        "## Ucus gunleri (serit baslangicina gore)",
        "",
        *strips,
        "",
        "## Sinirlamalar",
        "",
        "- gps_time Adjusted Standard GPS Time varsayilarak cozuldu (AHN5 ile ayni; "
        "global_encoding bayragi AHN5'te yanlisti). Sonuc tarihleri NGR kaydinin "
        "zamansal kapsamiyla (2019-11-30 / 2022-03-25) karsilastirilmalidir — asagida.",
        "- Yogunluk tum siniflarla olculdu (AHN5 kapisiyla ayni yontem).",
        "- Lisans: bu script lisansi YAZMAZ; ATTRIBUTION.md'deki insan kaydini denetler.",
        "",
    ]
    if resolvable:
        in_ngr = dt.date(2019, 11, 30) <= d_first.date() and d_last.date() <= dt.date(2022, 3, 25)
        md.insert(-7, f"NGR RWS DTM kaydinin zamansal kapsami 2019-11-30 / 2022-03-25; olculen aralik "
                      f"bu kapsamin **{'icinde' if in_ngr else 'DISINDA'}**.\n")
    out = rep / "01_prep_ahn4_input_gate.md"
    out.write_text("\n".join(md), encoding="utf-8")
    write_meta(out, run_id=run_id, inputs=laz,
               parameters={"median_density": med, "p10_density": p10, "zero_cells_pct": zero_pct,
                           "flight_first_utc": d_first.isoformat() if resolvable else None,
                           "flight_last_utc": d_last.isoformat() if resolvable else None,
                           "flight_year_used": flight_year, "classes": dict(classes),
                           "set_1Cc": len(set_c), "measurable_ge20": measurable,
                           "overall": "PASS" if overall else "FAIL"},
               notes="Muhurlu kural input_gate_ahn4 (5342d47).")
    logger.info("TAMAM | %s", out.name)
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
