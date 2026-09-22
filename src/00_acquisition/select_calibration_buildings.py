"""Kat yuksekligi kalibrasyonu icin 10 bina secer (Karar D-030, P-019).

Asama : 0.3

Secim kurali `config/acceptance_criteria.yml` -> `storey_height_calibration.
selection` altindan OKUNUR. O blok bu scriptten ONCE ayri bir commit ile
muhurlenmistir (commit f2667c1, status: SEALED_BEFORE_OBSERVATION) — yani
kural, hangi binalarin secilecegi GORULMEDEN yazilmistir.

Kural tamamen DETERMINISTIKTIR (rastgelelik yok): uygun binalar olculen
yuksekliklerine gore 10 desile bolunur, her desilden sinif 6 orani en yuksek
bina secilir; 10. desilde EN YUKSEK bina secilir. Seed yalnizca .meta.json'a
kayit icin yazilir.

Cikti : reports/storey_height_calibration.csv  (KAT_SAYISI sutunu BOS —
        kullanici dolduracak) + .meta.json

Calistirma:
    python src/00_acquisition/select_calibration_buildings.py
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import src.common  # noqa: E402,F401

import numpy as np  # noqa: E402

from src.common.config import load_acceptance_criteria, resolve  # noqa: E402
from src.common.logging_setup import setup_logging  # noqa: E402
from src.common.meta import write_meta  # noqa: E402

# Muhurlu kriterlerin SAYISAL karsiliklari (config'teki metinle birebir ayni
# olmali; config metin, burasi uygulama). Degistirilemez — kural muhurlu.
C2_MIN_YEAR, C2_MAX_YEAR = 1960, 1975
C4_MIN_RATIO, C4_MIN_C6 = 0.50, 200
C5_MAX_SPAN = 1.5
C6_MIN_GROUND = 50
C7_MIN_H = 3.0
N_PICK = 10


def _read(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def main() -> int:
    logger, run_id, _ = setup_logging("select_calibration_buildings")
    rep = resolve("reports.dir")

    cal = load_acceptance_criteria()["storey_height_calibration"]
    if cal["status"] != "SEALED_BEFORE_OBSERVATION":
        logger.warning("storey_height_calibration.status = %s", cal["status"])
    seed = int(cal["seed"])
    logger.info("Muhurlu secim | n=%d | seed=%d (yalnizca kayit icin; kural deterministik)",
                int(cal["n_buildings"]), seed)

    heights = {r["bag_id"]: r for r in _read(rep / "building_heights_ahn5.csv")}
    density = {r["bag_id"]: r for r in _read(rep / "ahn_point_density_by_building.csv")}
    logger.info("Girdi | yukseklik %d bina | A yogunluk %d bina", len(heights), len(density))

    # --- C3: dislama listeleri ---
    excl: set[str] = set()
    for name in ("post_flight_buildings.csv", "post_flight_suspects.csv",
                 "rebuild_suspects.csv"):
        ids = {r["bag_id"] for r in _read(rep / name)}
        excl |= ids
        logger.info("C3 dislama | %s: %d bina", name, len(ids))
    scenario_ids = set(load_acceptance_criteria()["building_scenario_rule"]["applies_to"])
    excl |= scenario_ids
    logger.info("C3 dislama | senaryo kurali (3 konut blogu): %d | TOPLAM benzersiz: %d",
                len(scenario_ids), len(excl))

    # --- Kriterleri SIRAYLA uygula, her adimda kac bina kaldigini yaz ---
    funnel: list[tuple[str, int]] = []
    pool = [bid for bid in density]                       # A alani (yogunluk CSV'si A'dir)
    funnel.append(("A alanindaki pand", len(pool)))

    pool = [b for b in pool if density[b]["gebruiksdoel"] == "woonfunctie"]
    funnel.append(("C1 gebruiksdoel tam olarak 'woonfunctie'", len(pool)))

    def year(b: str) -> int:
        v = density[b].get("bouwjaar") or "0"
        return int(v) if str(v).isdigit() else 0

    pool = [b for b in pool if C2_MIN_YEAR <= year(b) <= C2_MAX_YEAR]
    funnel.append((f"C2 bouwjaar {C2_MIN_YEAR}-{C2_MAX_YEAR}", len(pool)))

    pool = [b for b in pool if b not in excl]
    funnel.append(("C3 ucus sonrasi / yeniden yapim listelerinde degil", len(pool)))

    pool = [b for b in pool if b in heights and heights[b]["h_measured_m"]]
    funnel.append(("yuksekligi olculebilmis", len(pool)))

    def f(b: str, col: str) -> float:
        v = heights[b][col]
        return float(v) if v else float("nan")

    pool = [b for b in pool
            if float(density[b]["building_class_ratio"] or 0) >= C4_MIN_RATIO
            and int(heights[b]["class6_points"]) >= C4_MIN_C6]
    funnel.append((f"C4 sinif6 orani >= {C4_MIN_RATIO} ve >= {C4_MIN_C6} nokta", len(pool)))

    pool = [b for b in pool if f(b, "roof_span_m") < C5_MAX_SPAN]
    funnel.append((f"C5 duz cati (p90-p30 < {C5_MAX_SPAN} m)", len(pool)))

    pool = [b for b in pool if int(heights[b]["ground_ring_points"]) >= C6_MIN_GROUND]
    funnel.append((f"C6 halkada >= {C6_MIN_GROUND} zemin noktasi", len(pool)))

    pool = [b for b in pool if f(b, "h_measured_m") >= C7_MIN_H]
    funnel.append((f"C7 h >= {C7_MIN_H} m", len(pool)))

    for label, cnt in funnel:
        logger.info("HUNI | %-52s %5d", label, cnt)

    if len(pool) < N_PICK:
        logger.error("Uygun bina %d < %d — tabakalama yapilamaz.", len(pool), N_PICK)
        return 1

    pool.sort(key=lambda b: (f(b, "h_measured_m"), b))
    hs = np.array([f(b, "h_measured_m") for b in pool])
    logger.info("Uygun havuz | h medyan %.2f m | min %.2f | max %.2f",
                float(np.median(hs)), float(hs.min()), float(hs.max()))

    def ratio(b: str) -> float:
        return float(density[b]["building_class_ratio"])

    def row(b: str, first: object, extra: list) -> list:
        return [first, b, heights[b]["footprint_area_m2"], heights[b]["bouwjaar"],
                heights[b]["h_measured_m"], heights[b]["roof_p70_z_nap_m"],
                heights[b]["ground_z_nap_m"], heights[b]["roof_span_m"],
                density[b]["building_class_ratio"], heights[b]["class6_points"],
                heights[b]["ground_ring_points"]] + extra

    HEAD = ["bag_id", "footprint_area_m2", "bouwjaar", "h_measured_m",
            "roof_p70_z_nap_m", "ground_z_nap_m", "roof_span_m",
            "building_class_ratio", "class6_points", "ground_ring_points"]

    # ==================================================================
    #  GECERLI KURAL (D-031, P-020): YUKSEKLIK SINIFI tabakalamasi
    #  h 1 m'ye yuvarlanir -> sinif; her siniftan sinif6 orani en yuksek
    #  bina. N_PICK'e ulasilmazsa en kalabalik sinifin sonraki en iyileri.
    # ==================================================================
    classes: dict[int, list[str]] = {}
    for b in pool:
        classes.setdefault(int(f(b, "h_measured_m") + 0.5), []).append(b)
    ranked = {k: sorted(v, key=lambda b: (-ratio(b), b)) for k, v in classes.items()}

    picks: list[tuple[int, str]] = [(k, ranked[k][0]) for k in sorted(ranked)]
    biggest = max(ranked, key=lambda k: (len(ranked[k]), -k))
    nth = 1
    while len(picks) < N_PICK and nth < len(ranked[biggest]):
        picks.append((biggest, ranked[biggest][nth]))
        nth += 1
    if len(picks) < N_PICK:
        logger.error("Yalnizca %d bina secilebildi (%d sinif) — %d isteniyordu.",
                     len(picks), len(classes), N_PICK)
        return 1
    picks = picks[:N_PICK]

    logger.info("SECIM (D-031) | %d yukseklik sinifi | siniflar: %s",
                len(classes), sorted(classes))
    for k, b in picks:
        logger.info("Sinif %2d m | %3d aday | SECILEN %s (h %.2f m, oran %.3f)",
                    k, len(ranked[k]), b, f(b, "h_measured_m"), ratio(b))

    ids = [b for _, b in picks]
    if len(set(ids)) != len(ids):
        logger.error("Ayni bina iki kez secildi — kural hatali.")
        return 1

    # --- M-016: kuralin AMAC CUMLESI her calistirmada OLCULUR ---
    # Iddia (config purpose_claim): yayilim havuzun araligini kapsar ve
    # 10 binadan en fazla 3'u ayni 0,5 m bandina duser.
    ph = sorted(f(b, "h_measured_m") for b in ids)
    densest = max(sum(1 for v in ph if abs(v - c) <= 0.25) for c in ph)
    claim_ok = densest <= 3
    logger.info("AMAC OLCUMU (M-016) | secilen h: %s", " ".join(f"{v:.1f}" for v in ph))
    logger.info("AMAC OLCUMU (M-016) | benzersiz h (0,1 m): %d/%d | aralik %.1f-%.1f m "
                "(havuz %.1f-%.1f) | en kalabalik 0,5 m bandi: %d bina | IDDIA: %s",
                len({round(v, 1) for v in ph}), len(ph), ph[0], ph[-1],
                float(hs.min()), float(hs.max()), densest,
                "TUTTU" if claim_ok else "TUTMADI")
    if not claim_ok:
        logger.warning("Amac iddiasi TUTMADI — kural DEGISTIRILMEZ; sonuc oldugu gibi "
                       "raporlanir ve alternatif ONERI olarak ayri dosyaya yazilir "
                       "(M-016, docs/manual_steps.md MS-1).")

    out = rep / "storey_height_calibration.csv"
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["yukseklik_sinifi_m"] + HEAD
                   + ["sinif_aday_sayisi", "KAT_SAYISI_kullanici", "NOT_kullanici",
                      "kat_yuksekligi_m", "tip_grubu"])
        for k, b in picks:
            w.writerow(row(b, k, [len(ranked[k]), "", "", "", ""]))

    # ==================================================================
    #  SUPERSEDED BY P-020 (D-031) — SILINMEZ, kayit icin uretilir.
    #  Desil kurali kendi amacini saglamamisti (M-016). Cikti, kararin
    #  neye dayandigini sonradan gorebilmek icin korunur.
    # ==================================================================
    edges = np.linspace(0, len(pool), N_PICK + 1).astype(int)
    dec: list[tuple[int, str]] = []
    for d in range(N_PICK):
        bin_ids = pool[edges[d]:edges[d + 1]]
        if not bin_ids:
            continue
        if d == N_PICK - 1:
            dec.append((d + 1, sorted(bin_ids, key=lambda b: (-f(b, "h_measured_m"), b))[0]))
        else:
            dec.append((d + 1, sorted(bin_ids, key=lambda b: (-ratio(b), b))[0]))
    sup = rep / "storey_height_calibration_superseded_decile.csv"
    with sup.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["desil"] + HEAD + ["DURUM"])
        for d, b in dec:
            w.writerow(row(b, d, ["SUPERSEDED BY P-020 (D-031) - KULLANILMAZ"]))
    write_meta(sup, run_id=run_id, random_seed=seed,
               parameters={"status": "SUPERSEDED_BY_P-020",
                           "picked": [b for _, b in dec],
                           "h_m": [f(b, "h_measured_m") for _, b in dec]},
               notes=("Eski desil kurali. D-031 ile gecersiz kilindi ama SILINMEDI "
                      "(kullanici talimati). Hicbir hesaba girmez."))
    logger.info("SUPERSEDED kayit | %s | %d bina (kullanilmaz)", sup.name, len(dec))
    logger.info("Iki orneklemin ortak binasi: %d",
                len(set(ids) & {b for _, b in dec}))

    write_meta(out, run_id=run_id, random_seed=seed,
               parameters={"rule": "height_class (D-031)", "n_picked": len(picks),
                           "pool_size": len(pool), "funnel": dict(funnel),
                           "classes": {str(k): len(v) for k, v in sorted(ranked.items())},
                           "criteria": {"C2": [C2_MIN_YEAR, C2_MAX_YEAR],
                                        "C4_ratio": C4_MIN_RATIO, "C4_points": C4_MIN_C6,
                                        "C5_span_m": C5_MAX_SPAN,
                                        "C6_ground_points": C6_MIN_GROUND,
                                        "C7_min_h_m": C7_MIN_H},
                           "picked": ids, "purpose_claim_holds": claim_ok,
                           "h_range_m": [float(hs.min()), float(hs.max())]},
               notes=("Kural: storey_height_calibration.selection.stratification "
                      "(D-031, P-020 ile onaylandi). Deterministik; seed yalnizca "
                      "kayit icindir. KAT_SAYISI kullanici tarafindan doldurulur."))
    logger.info("TAMAM | %s | %d bina", out.name, len(picks))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
