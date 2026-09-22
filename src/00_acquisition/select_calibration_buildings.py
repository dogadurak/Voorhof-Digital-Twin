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

    # --- Tabakalama: h'ye gore 10 desil, her desilden 1 bina ---
    pool.sort(key=lambda b: (f(b, "h_measured_m"), b))
    hs = np.array([f(b, "h_measured_m") for b in pool])
    logger.info("Uygun havuz | h medyan %.2f m | min %.2f | max %.2f",
                float(np.median(hs)), float(hs.min()), float(hs.max()))

    edges = np.linspace(0, len(pool), N_PICK + 1).astype(int)
    picks: list[tuple[int, str]] = []
    for d in range(N_PICK):
        lo, hi = edges[d], edges[d + 1]
        bin_ids = pool[lo:hi]
        if not bin_ids:
            logger.error("Desil %d bos — bu kural altinda olamaz.", d + 1)
            return 1
        if d == N_PICK - 1:                       # muhurlu istisna: en yuksek bina
            # esitlikte bag_id kucuk olan: once -h, sonra bag_id artan
            chosen = sorted(bin_ids, key=lambda b: (-f(b, "h_measured_m"), b))[0]
        else:
            chosen = sorted(bin_ids,
                            key=lambda b: (-float(density[b]["building_class_ratio"]), b))[0]
        picks.append((d + 1, chosen))
        logger.info("Desil %2d | %3d aday | h %.2f-%.2f m | SECILEN %s (h %.2f m, oran %.3f)",
                    d + 1, len(bin_ids), f(bin_ids[0], "h_measured_m"),
                    f(bin_ids[-1], "h_measured_m"), chosen, f(chosen, "h_measured_m"),
                    float(density[chosen]["building_class_ratio"]))

    ids = [b for _, b in picks]
    if len(set(ids)) != len(ids):
        logger.error("Ayni bina birden fazla desilde secildi — kural hatali.")
        return 1

    # --- M-016: kuralin AMAC CUMLESI her calistirmada OLCULUR ---
    # Amac (config): "orneklem farkli YUKSEKLIKLERI ... kapsar". Bu bir iddiadir;
    # yayilim burada sayiya dokulur. Karar elle verilir (docs/manual_steps.md MS-1).
    ph = sorted(f(b, "h_measured_m") for b in ids)
    uniq = len({round(v, 1) for v in ph})
    logger.info("AMAC OLCUMU (M-016) | secilen h: %s",
                " ".join(f"{v:.1f}" for v in ph))
    logger.info("AMAC OLCUMU (M-016) | benzersiz yukseklik (0,1 m): %d/%d | "
                "aralik %.1f-%.1f m | en kalabalik 0,5 m bandinda %d bina",
                uniq, len(ph), ph[0], ph[-1],
                max(sum(1 for v in ph if abs(v - c) <= 0.25) for c in ph))

    out = rep / "storey_height_calibration.csv"
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["sira", "desil", "bag_id", "footprint_area_m2", "bouwjaar",
                    "h_measured_m", "roof_p70_z_nap_m", "ground_z_nap_m",
                    "roof_span_m", "building_class_ratio", "class6_points",
                    "ground_ring_points", "KAT_SAYISI_kullanici", "NOT_kullanici",
                    "kat_yuksekligi_m"])
        for i, (d, b) in enumerate(picks, 1):
            w.writerow([i, d, b, heights[b]["footprint_area_m2"], heights[b]["bouwjaar"],
                        heights[b]["h_measured_m"], heights[b]["roof_p70_z_nap_m"],
                        heights[b]["ground_z_nap_m"], heights[b]["roof_span_m"],
                        density[b]["building_class_ratio"], heights[b]["class6_points"],
                        heights[b]["ground_ring_points"], "", "", ""])

    # ------------------------------------------------------------------
    #  ONERI (P-020) — MUHURLU DEGILDIR, KULLANILMAZ, ONAY BEKLER
    #  Muhurlu desil kurali kendi AMACINI tutturamadi: desiller NUFUSU izler,
    #  ARALIGI degil. Havuzun %66'si tek bir yukseklik bandinda (5,7-6,0 m)
    #  oldugu icin 10 binanin 6'si ayni tip sira evden secildi. Kullanicinin
    #  talimati "farkli kat sayisinda 10 bina" idi.
    #  Kural SONUCTAN SONRA degistirilmez (Bolum 12.2) — bu yuzden muhurlu
    #  cikti oldugu gibi birakilir ve alternatif AYRI bir dosyaya, ONERI
    #  olarak yazilir. Hangisinin kullanilacagina kullanici karar verir ve
    #  karar ORTALAMA HESAPLANMADAN once verilir.
    #  Oneri kurali: h 1 m'ye yuvarlanarak SINIFLARA bolunur, her siniftan
    #  sinif 6 orani en yuksek bina; 10. bina en kalabalik sinifin ikinci
    #  en iyisi (o tip A'nin baskin konut stokudur, tekrar hak eder).
    # ------------------------------------------------------------------
    classes: dict[int, list[str]] = {}
    for b in pool:
        classes.setdefault(int(f(b, "h_measured_m") + 0.5), []).append(b)
    ranked = {k: sorted(v, key=lambda b: (-float(density[b]["building_class_ratio"]), b))
              for k, v in classes.items()}
    prop = [(k, ranked[k][0]) for k in sorted(ranked)]
    biggest = max(ranked, key=lambda k: (len(ranked[k]), -k))
    if len(prop) < N_PICK and len(ranked[biggest]) > 1:
        prop.append((biggest, ranked[biggest][1]))
    logger.info("ONERI (P-020) | %d yukseklik sinifi | %d bina | siniflar: %s",
                len(classes), len(prop), sorted(classes))
    for k, b in prop:
        logger.info("ONERI | sinif %2d m | %3d aday | %s (h %.2f m, oran %.3f)",
                    k, len(ranked[k]), b, f(b, "h_measured_m"),
                    float(density[b]["building_class_ratio"]))

    prop_path = rep / "storey_height_calibration_proposal_p020.csv"
    with prop_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["sira", "yukseklik_sinifi_m", "bag_id", "footprint_area_m2",
                    "bouwjaar", "h_measured_m", "roof_span_m", "building_class_ratio",
                    "sinif_aday_sayisi", "DURUM"])
        for i, (k, b) in enumerate(prop, 1):
            w.writerow([i, k, b, heights[b]["footprint_area_m2"], heights[b]["bouwjaar"],
                        heights[b]["h_measured_m"], heights[b]["roof_span_m"],
                        density[b]["building_class_ratio"], len(ranked[k]),
                        "ONERI - MUHURLU DEGIL - P-020 ONAYI BEKLIYOR"])

    write_meta(prop_path, run_id=run_id, random_seed=seed,
               parameters={"status": "ONERI - MUHURLU DEGIL - P-020",
                           "classes": {str(k): len(v) for k, v in sorted(ranked.items())},
                           "picked": [b for _, b in prop]},
               notes=("P-020 onerisi. Muhurlu kural DEGILDIR ve onaylanmadan "
                      "hicbir hesaba girmez (M-016)."))

    write_meta(out, run_id=run_id, random_seed=seed,
               parameters={"n_picked": len(picks), "pool_size": len(pool),
                           "funnel": dict(funnel),
                           "criteria": {"C2": [C2_MIN_YEAR, C2_MAX_YEAR],
                                        "C4_ratio": C4_MIN_RATIO, "C4_points": C4_MIN_C6,
                                        "C5_span_m": C5_MAX_SPAN,
                                        "C6_ground_points": C6_MIN_GROUND,
                                        "C7_min_h_m": C7_MIN_H},
                           "picked": ids,
                           "h_range_m": [float(hs.min()), float(hs.max())]},
               notes=("Muhurlu kural: storey_height_calibration.selection (commit "
                      "f2667c1, secimden ONCE). Kural deterministiktir; seed yalnizca "
                      "kayit icindir. KAT_SAYISI sutunu kullanici tarafindan doldurulur."))
    logger.info("TAMAM | %s | %d bina", out.name, len(picks))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
