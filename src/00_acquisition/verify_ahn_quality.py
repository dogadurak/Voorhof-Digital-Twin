"""AHN LAZ girdi kalite kapisi — AGENTS.md Bolum 12.12, Karar D-015.

Asama : 0.3
Cikti : reports/00_stage_0_3_ahn_gate.md
        reports/ahn_point_density_by_building.csv

Esikler `config/acceptance_criteria.yml` -> `input_gate_ahn` altindan OKUNUR,
koda gomulmez (Bolum 13.2-1). O blok bu scriptten ONCE ayri bir commit ile
muhurlenmistir.

Bellek notu: 420 milyon nokta bir kerede bellege alinmaz. Her LAZ dosyasi
laspy'nin chunk okuyucusuyla parca parca islenir; sayimlar numpy histogrami
uzerinde biriktirilir.

Calistirma:
    python src/00_acquisition/verify_ahn_quality.py
"""

from __future__ import annotations

import collections
import csv
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import laspy
import shapely
from shapely.geometry import shape
from shapely.prepared import prep
from shapely.strtree import STRtree

from src.common.config import load_acceptance_criteria, resolve
from src.common.logging_setup import setup_logging
from src.common.meta import write_meta

CHUNK = 5_000_000


def _assert_predicate_direction(logger) -> None:
    """STRtree predicate yonunu her calistirmada FIILEN sinar.

    Biri icerde biri disarda iki nokta ile tek bir kare test edilir. Dogru
    yon tam olarak 1 eslesme vermelidir. Shapely surumu degisir ve yon
    degisirse bu test patlar ve sessiz bir SIFIR SAYIM uretilmez.

    Gerekce (MISTAKES.md M-007): predicate yonu varsayildi ve TUM binalar
    icin 0 nokta sayildi. Sonuc bariz yanlis oldugu icin yakalandi; daha
    ince bir sapma olsaydi fark edilmeyebilirdi.
    """
    from shapely.geometry import box as _box
    probe_tree = STRtree([_box(0, 0, 10, 10)])
    probe_pts = shapely.points(np.array([5.0, 50.0]), np.array([5.0, 50.0]))
    hits = probe_tree.query(probe_pts, predicate="within")
    if hits.shape[1] != 1 or hits[0][0] != 0:
        raise RuntimeError(
            f"STRtree predicate yonu beklenenden farkli: 'within' testi "
            f"{hits.shape[1]} eslesme verdi, 1 bekleniyordu. Shapely "
            f"{shapely.__version__} semantigi degismis olabilir."
        )
    logger.info("STRtree predicate yonu dogrulandi ('within', 1/2 nokta esletti)")


def main() -> int:
    logger, run_id, _ = setup_logging("verify_ahn_quality")
    _assert_predicate_direction(logger)
    gate = load_acceptance_criteria()["input_gate_ahn"]
    status_cfg = load_acceptance_criteria()["stage_0_2"]["status_filter"]

    cell = float(gate["method"]["grid_cell_m"])
    hard = float(gate["hard_gate"]["threshold"])
    expect = float(gate["expectation"]["threshold"])
    logger.info("Kapi config'ten okundu | hucre %.0f m | sert kapi >=%.1f | beklenti >=%.1f",
                cell, hard, expect)

    aoi = resolve("root.aoi")
    area_a = shape(json.loads((aoi / "area_A_analysis.geojson").read_text(encoding="utf-8"))
                   ["features"][0]["geometry"])
    area_b = shape(json.loads((aoi / "area_B_context.geojson").read_text(encoding="utf-8"))
                   ["features"][0]["geometry"])

    # --- B icin izgara ---
    bminx, bminy, bmaxx, bmaxy = area_b.bounds
    nx = int(np.ceil((bmaxx - bminx) / cell))
    ny = int(np.ceil((bmaxy - bminy) / cell))
    counts = np.zeros((nx, ny), dtype=np.int64)
    building_counts = np.zeros((nx, ny), dtype=np.int64)
    logger.info("Izgara | %d x %d hucre (%.0f m) | B bbox %.0f x %.0f m",
                nx, ny, cell, bmaxx - bminx, bmaxy - bminy)

    # --- A binalari: ayakizi poligonlari ---
    panden = [
        f for f in json.loads(
            (resolve("data.raw") / "bag" / "bag_pand.geojson").read_text(encoding="utf-8")
        )["features"]
        if f["properties"].get("status") in status_cfg["pand_include"]
        and area_a.contains(shape(f["geometry"]).centroid)
    ]
    geoms = [shape(f["geometry"]) for f in panden]
    tree = STRtree(geoms)
    building_points = np.zeros(len(geoms), dtype=np.int64)
    logger.info("A binasi (status filtreli, centroid): %d", len(geoms))

    class_counter: collections.Counter = collections.Counter()
    total_points = 0
    laz_files = sorted((resolve("data.raw") / "ahn" / "AHN5_T").glob("*.LAZ"))
    logger.info("Islenecek LAZ dosyasi: %d", len(laz_files))

    for path in laz_files:
        with laspy.open(str(path)) as reader:
            file_points = 0
            for chunk in reader.chunk_iterator(CHUNK):
                x = np.asarray(chunk.x)
                y = np.asarray(chunk.y)
                cls = np.asarray(chunk.classification)

                inside = (x >= bminx) & (x < bmaxx) & (y >= bminy) & (y < bmaxy)
                if not inside.any():
                    continue
                x, y, cls = x[inside], y[inside], cls[inside]

                ix = ((x - bminx) / cell).astype(np.int64)
                iy = ((y - bminy) / cell).astype(np.int64)
                np.add.at(counts, (ix, iy), 1)

                # AHN bina sinifi: kod veriden okunur, ASPRS 6 varsayilir ama
                # dagilim ayrica raporlanir (config: class_distribution)
                is_building = cls == 6
                if is_building.any():
                    np.add.at(building_counts, (ix[is_building], iy[is_building]), 1)

                class_counter.update(
                    dict(zip(*[a.tolist() for a in np.unique(cls, return_counts=True)]))
                )
                file_points += len(x)

                # --- bina bazli sayim (vektorel; config: ICINE DUSME) ---
                aminx, aminy, amaxx, amaxy = area_a.bounds
                near = (x >= aminx) & (x <= amaxx) & (y >= aminy) & (y <= amaxy)
                if near.any():
                    # shapely 2.x vektorel nokta uretimi + STRtree sorgusu.
                    # DIKKAT: predicate GIRDI geometrisine uygulanir, yani
                    # input.predicate(tree). Nokta-poligon icin dogru yon
                    # "within" (nokta.within(poligon)); "contains" her zaman
                    # bos doner cunku nokta poligonu iceremez. Bu yon
                    # _assert_predicate_direction() ile her calistirmada sinanir
                    # (MISTAKES.md M-007).
                    pts = shapely.points(x[near], y[near])
                    hit = tree.query(pts, predicate="within")
                    if hit.size:
                        np.add.at(building_points, hit[1], 1)

            total_points += file_points
            logger.info("%s | %d nokta B bbox icinde", path.name, file_points)

    logger.info("Toplam islenen nokta (B bbox): %d", total_points)
    return _report(logger, run_id, gate, counts, building_counts, cell,
                   bminx, bminy, area_b, panden, geoms, building_points,
                   class_counter, total_points, hard, expect)


def _report(logger, run_id, gate, counts, building_counts, cell, bminx, bminy,
            area_b, panden, geoms, building_points, class_counter, total_points,
            hard, expect) -> int:
    """Olculen degerleri esiklerle karsilastirir ve raporu yazar."""
    from shapely.geometry import Point

    nx, ny = counts.shape
    inside_mask = np.zeros_like(counts, dtype=bool)
    prepared_b = prep(area_b)
    for i in range(nx):
        cx = bminx + (i + 0.5) * cell
        for j in range(ny):
            cy = bminy + (j + 0.5) * cell
            if prepared_b.contains(Point(cx, cy)):
                inside_mask[i, j] = True

    cell_area = cell * cell
    dens = counts[inside_mask] / cell_area
    bdens = building_counts[inside_mask] / cell_area

    median_d = float(np.median(dens))
    p10_d = float(np.percentile(dens, 10))
    zero_pct = float(100 * (dens == 0).mean())
    below_hard = float(100 * (dens < hard).mean())
    below_exp = float(100 * (dens < expect).mean())

    logger.info("=== KAPI OLCUMU (B alani, %d hucre) ===", inside_mask.sum())
    logger.info("  medyan yogunluk     %8.2f p/m2", median_d)
    logger.info("  p10                 %8.2f p/m2", p10_d)
    bdens_nonzero = bdens[bdens > 0]
    logger.info("  bina sinifi (kod 6): toplam %d nokta | %.1f%% hucrede var | "
                "o hucrelerde medyan %.2f p/m2",
                int(building_counts[inside_mask].sum()),
                100 * (bdens > 0).mean(),
                float(np.median(bdens_nonzero)) if bdens_nonzero.size else 0.0)
    logger.info("  sifir donuslu hucre %8.2f %%", zero_pct)
    logger.info("  sert kapi altinda   %8.2f %% hucre", below_hard)
    logger.info("  beklenti altinda    %8.2f %% hucre", below_exp)

    gate_pass = median_d >= hard
    exp_pass = median_d >= expect
    logger.info("  0-E SERT KAPI (>=%.1f): %s", hard, "PASS" if gate_pass else "FAIL")
    logger.info("  0-F BEKLENTI  (>=%.1f): %s", expect, "PASS" if exp_pass else "UYARI")

    # --- bina bazli CSV ---
    areas = np.array([g.area for g in geoms])
    roof_dens = np.divide(building_points, areas, out=np.zeros_like(areas), where=areas > 0)
    csv_path = resolve("reports.dir") / "ahn_point_density_by_building.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["bag_id", "footprint_area_m2", "point_count",
                    "roof_density_pts_m2", "below_10", "has_dwellings"])
        for f, a, n, d in zip(panden, areas, building_points, roof_dens):
            p = f["properties"]
            w.writerow([p["identificatie"], f"{a:.2f}", int(n), f"{d:.2f}",
                        "true" if d < 10 else "false",
                        "true" if (p.get("aantal_verblijfsobjecten") or 0) > 0 else "false"])

    b_median = float(np.median(roof_dens))
    b_p10 = float(np.percentile(roof_dens, 10))
    b_below = int((roof_dens < 10).sum())
    logger.info("=== BINA BAZLI CATI YOGUNLUGU (A, %d bina) ===", len(geoms))
    logger.info("  medyan %6.2f | p10 %6.2f | <10 p/m2: %d bina (%%%.1f)",
                b_median, b_p10, b_below, 100 * b_below / max(1, len(geoms)))
    logger.info("  CSV: %s", csv_path.name)

    top = ", ".join(f"{k}:{v}" for k, v in class_counter.most_common(8))
    logger.info("Sinif dagilimi (ilk 8): %s", top)

    report = resolve("reports.dir") / "00_stage_0_3_ahn_gate.md"
    report.write_text(f"""# Asama 0.3 — AHN girdi kalite kapisi

**Karar D-015** · AGENTS.md Bolum 12.12 · run_id `{run_id}`

Esikler `config/acceptance_criteria.yml` -> `input_gate_ahn` altindan okundu.
O blok bu olcumden **once** ayri bir commit ile muhurlendi.

## Kapi sonucu

| Kriter | Kaynak | Esik | Olculen | Sonuc |
|---|---|---|---|---|
| **0-E sert kapi** | ahn.nl resmi spec (AHN4 tabani) | >= {hard:.1f} p/m2 | **{median_d:.2f}** | **{'PASS' if gate_pass else 'FAIL'}** |
| **0-F beklenti** | kendi olcumumuz (37EN1 = 29,3) | >= {expect:.1f} p/m2 | **{median_d:.2f}** | **{'PASS' if exp_pass else 'UYARI'}** |

## B alani yogunluk dagilimi

| Metrik | Deger |
|---|---|
| Olculen hucre (10 x 10 m, merkezi B icinde) | {int(inside_mask.sum())} |
| Medyan yogunluk | {median_d:.2f} p/m2 |
| 10. persentil | {p10_d:.2f} p/m2 |
| Bina sinifi (kod 6) toplam nokta | {int(building_counts[inside_mask].sum()):,} |
| Bina sinifi noktasi olan hucre | {100*(bdens>0).mean():.1f} % |
| O hucrelerde medyan bina yogunlugu | {float(np.median(bdens[bdens>0])) if (bdens>0).any() else 0:.2f} p/m2 |
| Sifir donuslu hucre | {zero_pct:.2f} % |
| Sert kapinin altinda hucre | {below_hard:.2f} % |
| Beklentinin altinda hucre | {below_exp:.2f} % |
| Islenen nokta (B bbox) | {total_points:,} |

**Sifir donuslu hucreler bir hata DEGILDIR:** su yuzeyleri dogal olarak donus
vermez. Su disi kumelenme Asama 1'de BGT su katmaniyla ayristirilacaktir.

## Bina bazli cati yogunlugu (esik yok — raporlanir)

A alanindaki **{len(geoms)}** bina icin, ayakizi poligonu icine dusen nokta /
ayakizi alani:

| Metrik | Deger |
|---|---|
| Medyan | {b_median:.2f} p/m2 |
| 10. persentil | {b_p10:.2f} p/m2 |
| **10 p/m2 altinda** | **{b_below} bina** (%{100*b_below/max(1,len(geoms)):.1f}) |

Tam liste: `reports/ahn_point_density_by_building.csv`

**Esik konulmadi** cunku dusuk cati yogunlugu tek basina hata degildir —
kucuk veya egimli catili binalarda dogal olarak az nokta duser.

**Asama 1'de kullanimi:** `reports/failed_buildings.csv` bu listeyle
karsilastirilacak. Basarisiz VE dusuk yogunluklu -> neden muhtemelen **girdi**;
basarisiz AMA yeterli yogunluklu -> neden muhtemelen **yontem**. Bu ayrim
sonradan yapilamaz.

## Sinif dagilimi (veriden okundu, ASPRS varsayilmadi)

```
{top}
```
""", encoding="utf-8")

    write_meta(report, run_id=run_id,
               parameters={"median_density": median_d, "p10": p10_d,
                           "zero_cells_pct": zero_pct,
                           "buildings_below_10": b_below,
                           "hard_gate": hard, "expectation": expect,
                           "gate_pass": gate_pass, "expectation_pass": exp_pass},
               notes="Esikler config'ten okundu; olcumden once muhurlendi (D-015).")
    logger.info("TAMAM | rapor: %s", report.name)
    return 0 if gate_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
