"""Asama 0.3 spot kontrolu — BAGIMSIZ ikinci yoldan yeniden sayim.

AGENTS.md Bolum 13.2-2 (spot kontrol) ve 13.2-5 (capraz hesap).

Neyi sinar:
  `reports/ahn_point_density_by_building.csv` sabit seed ile secilen N bina
  icin, ayakizi ici nokta sayilarini ve ayakizi alanini **farkli bir kod
  yoluyla** yeniden hesaplar ve karsilastirir.

Neden bagimsiz:
  Asil hesap (`verify_ahn_quality.py`) sunlari kullanir:
    - `shapely.points(...)` vektorel nokta uretimi
    - `STRtree.query(..., predicate="within")` mekansal indeks
    - `shapely` poligon alani
  Bu script hicbirini kullanmaz:
    - nokta nokta `prepared.contains(Point)` (mekansal indeks YOK)
    - alan icin **shoelace** formulu, ham koordinatlardan
  Ayni hata iki yolda ayni sekilde tekrarlanmazsa fark gorunur. M-007 tam da
  boyle bir hataydi (yuklem yonu); o hata bu kontrolle de yakalanirdi.

Cikti : reports/00_stage_0_3_spot_check.md
        reports/spot_check_0_3.csv

Calistirma:
    python src/qa/spot_check_0_3.py
"""

from __future__ import annotations

import csv
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# M-003 / M-012: PROJ, pyproj'u yukleyen kutuphanelerden ONCE sabitlenir.
import src.common  # noqa: E402,F401

import laspy
import numpy as np
from shapely.geometry import Point, shape
from shapely.prepared import prep

from src.common.config import load_acceptance_criteria, resolve
from src.common.logging_setup import setup_logging
from src.common.meta import write_meta

N_SAMPLE = 10
CHUNK = 5_000_000


def shoelace_area(geom_json: dict) -> float:
    """Poligon alanini HAM koordinatlardan shoelace ile hesaplar (m2).

    Girdi : GeoJSON geometri (Polygon veya MultiPolygon)
    Cikti : alan, m2 (delikler cikarilmis)
    Birim : m2

    shapely kullanmaz — capraz hesap icin bilerek bagimsiz.
    """
    def ring(coords):
        s = 0.0
        for (x1, y1), (x2, y2) in zip(coords, coords[1:]):
            s += x1 * y2 - x2 * y1
        return abs(s) / 2.0

    polys = ([geom_json["coordinates"]] if geom_json["type"] == "Polygon"
             else geom_json["coordinates"])
    total = 0.0
    for poly in polys:
        total += ring(poly[0]) - sum(ring(h) for h in poly[1:])
    return total


def main() -> int:
    logger, run_id, _ = setup_logging("spot_check_0_3")
    seed = int(load_acceptance_criteria()["input_gate_ahn"]["visual_check"]["seed"])
    logger.info("Spot kontrol | N=%d | seed=%d (config'ten)", N_SAMPLE, seed)

    rows = list(csv.DictReader(
        (resolve("reports.dir") / "ahn_point_density_by_building.csv").open(encoding="utf-8")))
    rng = random.Random(seed)
    sample = rng.sample(rows, N_SAMPLE)
    ids = {r["bag_id"] for r in sample}
    logger.info("Secilen bina: %s", ", ".join(sorted(ids)))

    bag = {f["properties"]["identificatie"]: f for f in json.loads(
        (resolve("data.raw") / "bag" / "bag_pand.geojson").read_text(encoding="utf-8"))["features"]
        if f["properties"]["identificatie"] in ids}
    geoms = {k: shape(v["geometry"]) for k, v in bag.items()}
    prepared = {k: prep(g) for k, g in geoms.items()}
    bounds = {k: g.bounds for k, g in geoms.items()}

    total_cnt = {k: 0 for k in ids}
    cls6_cnt = {k: 0 for k in ids}
    for path in sorted((resolve("data.raw") / "ahn" / "AHN5_T").glob("*.LAZ")):
        with laspy.open(str(path)) as reader:
            for ch in reader.chunk_iterator(CHUNK):
                x = np.asarray(ch.x); y = np.asarray(ch.y)
                cls = np.asarray(ch.classification)
                for bid in ids:
                    x0, y0, x1, y1 = bounds[bid]
                    m = (x >= x0) & (x <= x1) & (y >= y0) & (y <= y1)
                    if not m.any():
                        continue
                    pg = prepared[bid]
                    xs, ys, cs = x[m], y[m], cls[m]
                    for px, py, pc in zip(xs, ys, cs):       # nokta nokta, indeks YOK
                        if pg.contains(Point(px, py)):
                            total_cnt[bid] += 1
                            if pc == 6:
                                cls6_cnt[bid] += 1
        logger.info("%s islendi", path.name)

    # DIKKAT (M-014): CSV'deki alan iki ondaliga YUVARLANMISTIR. Tam
    # hassasiyetli shoelace degerini yuvarlanmis degerle karsilastirmak sahte
    # bir fark uretir (olculdu: 2,1e-04, oysa gercek fark 5,2e-07). Bu yuzden
    # IKI AYRI kontrol yapilir:
    #   (a) geometrik: shoelace  <-> shapely (ikisi de tam hassasiyet)
    #   (b) raporlama: CSV degeri <-> round(shapely, 2)
    out_rows, worst, csv_bad = [], 0.0, 0
    for r in sorted(sample, key=lambda r: r["bag_id"]):
        bid = r["bag_id"]
        a_csv = float(r["footprint_area_m2"])
        a_ref = geoms[bid].area                      # shapely, YUVARLANMAMIS
        a_ind = shoelace_area(bag[bid]["geometry"])
        if abs(a_csv - round(a_ref, 2)) > 1e-9:
            csv_bad += 1
        n_ref, n_ind = int(r["point_count"]), total_cnt[bid]
        c_ref, c_ind = int(r["building_class_points"]), cls6_cnt[bid]
        da = abs(a_ind - a_ref)
        worst = max(worst, da / max(a_ref, 1e-9))
        out_rows.append({
            "bag_id": bid,
            "alan_csv_m2": f"{a_csv:.2f}",
            "alan_ref_m2": f"{a_ref:.6f}", "alan_bagimsiz_m2": f"{a_ind:.6f}",
            "alan_fark_m2": f"{a_ind - a_ref:+.9f}",
            "nokta_ref": n_ref, "nokta_bagimsiz": n_ind, "nokta_fark": n_ind - n_ref,
            "sinif6_ref": c_ref, "sinif6_bagimsiz": c_ind, "sinif6_fark": c_ind - c_ref,
        })

    csv_path = resolve("reports.dir") / "spot_check_0_3.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out_rows[0]))
        w.writeheader(); w.writerows(out_rows)

    n_bad = sum(1 for r in out_rows if r["nokta_fark"] != 0 or r["sinif6_fark"] != 0)
    verdict = "PASS" if n_bad == 0 and worst < 1e-6 and csv_bad == 0 else "FAIL"
    logger.info("Nokta sayimi farkli olan bina: %d/%d | en buyuk bagil alan farki: %.2e "
                "| CSV yuvarlamasi hatali: %d", n_bad, N_SAMPLE, worst, csv_bad)
    logger.info("SPOT KONTROL: %s", verdict)

    tbl = "\n".join(
        f"| `{r['bag_id']}` | {r['alan_csv_m2']} | {r['alan_ref_m2']} | {r['alan_bagimsiz_m2']} | {r['alan_fark_m2']} | "
        f"{r['nokta_ref']:,} | {r['nokta_bagimsiz']:,} | {r['nokta_fark']:+d} | "
        f"{r['sinif6_ref']:,} | {r['sinif6_bagimsiz']:,} | {r['sinif6_fark']:+d} |"
        for r in out_rows)

    md = resolve("reports.dir") / "00_stage_0_3_spot_check.md"
    md.write_text(f"""# Asama 0.3 — Spot kontrol (bagimsiz ikinci yol)

**run_id** `{run_id}` · **N = {N_SAMPLE}** · **seed = {seed}** (config'ten:
`input_gate_ahn.visual_check.seed`) · AGENTS.md Bolum 13.2-2 ve 13.2-5

## Yontem — neden bagimsiz

| | Asil hesap (`verify_ahn_quality.py`) | Bu kontrol |
|---|---|---|
| Nokta-poligon | `STRtree.query(..., predicate="within")` | nokta nokta `prepared.contains(Point)`, indeks YOK |
| Nokta uretimi | `shapely.points(...)` vektorel | tek tek `Point(x, y)` |
| Alan | `shapely` poligon alani | **shoelace** formulu, ham koordinatlardan |

Ayni hata iki yolda ayni sekilde tekrarlanmadikca fark gorunur. M-007
(yuklem yonu) tam da bu kontrolle yakalanabilecek bir hataydi.

## Sonuc

| bag_id | alan CSV | alan shapely | alan shoelace | fark | nokta ref | nokta bagimsiz | fark | sinif6 ref | sinif6 bagimsiz | fark |
|---|---|---|---|---|---|---|---|---|---|---|
{tbl}

- Nokta sayimi farkli olan bina: **{n_bad} / {N_SAMPLE}**
- En buyuk bagil alan farki (shoelace vs shapely, ikisi de tam hassasiyet):
  **{worst:.2e}** — koordinatlar ~84.000 oldugu icin shoelace'te beklenen
  kayan nokta birikimi
- CSV yuvarlamasi (`round(shapely, 2)`) hatali olan bina: **{csv_bad} / {N_SAMPLE}**

**SPOT KONTROL: {verdict}**
""", encoding="utf-8")
    write_meta(md, run_id=run_id,
               parameters={"n_sample": N_SAMPLE, "random_seed": seed,
                           "mismatched_buildings": n_bad, "max_rel_area_diff": worst,
                           "csv_rounding_errors": csv_bad,
                           "verdict": verdict},
               notes="Bagimsiz ikinci yol: STRtree yok, vektorel nokta yok, alan shoelace.")
    logger.info("TAMAM | %s", md.name)
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
