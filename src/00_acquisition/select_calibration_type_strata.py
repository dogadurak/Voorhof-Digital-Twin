"""Kat yuksekligi kalibrasyonu icin T2 (yeni konut) ve T3 (okul) binalarini secer (D-035).

Asama : 0.3

Kural `config/acceptance_criteria.yml` -> `storey_height_calibration.
function_type_stratification` altindadir ve bu scriptten ONCE ayri commit ile
muhurlenmistir (a20b15f, status: SEALED_BEFORE_OBSERVATION) — hangi binalarin
secilecegi GORULMEDEN.

Her tip icin havuz h_measured_m'ye gore uc esit sayili dilime (tertil) bolunur;
her dilimde sinif 6 nokta yogunlugu en yuksek bina ASIL, ikinci YEDEK olur.
Tamamen deterministiktir. T1 (eski konut) = mevcut 10 bina, burada secilmez.

Cikti : reports/storey_height_calibration_types.csv (+ .meta.json)
        KAT_SAYISI sutunu BOS — kullanici dolduracak.

Calistirma:
    python src/00_acquisition/select_calibration_type_strata.py
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import src.common  # noqa: E402,F401

import numpy as np  # noqa: E402

from src.common.config import load_acceptance_criteria, resolve  # noqa: E402
from src.common.logging_setup import setup_logging  # noqa: E402
from src.common.meta import write_meta  # noqa: E402

# Muhurlu metnin SAYISAL karsiliklari (config metin, burasi uygulama). Mevcut
# kalibrasyon kriterleriyle AYNI degerler (select_calibration_buildings.py).
C4_MIN_C6 = 200
C5_MAX_SPAN = 1.5
C6_MIN_GROUND = 50
C7_MIN_H = 3.0
T2_MIN_YEAR = 2000
T3_MIN_AREA_M2 = 100.0
N_TERTILES = 3


def _read(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _funcs(r: dict) -> set[str]:
    return {x.strip() for x in (r.get("gebruiksdoel") or "").split(",") if x.strip()}


def _year(r: dict) -> int:
    v = r.get("bouwjaar") or ""
    return int(v) if v.isdigit() else 0


def main() -> int:
    logger, run_id, _ = setup_logging("select_calibration_type_strata")
    rep = resolve("reports.dir")
    cal = load_acceptance_criteria()["storey_height_calibration"]
    fts = cal["function_type_stratification"]
    if fts["status"] != "SEALED_BEFORE_OBSERVATION":
        raise RuntimeError(f"function_type_stratification.status = {fts['status']} — "
                           "muhursuz kuralla secim yapilmaz (Bolum 12.2)")
    seed = int(cal["seed"])

    H = {r["bag_id"]: r for r in _read(rep / "building_heights_ahn5.csv")}

    excl: set[str] = set()
    for name in ("post_flight_buildings.csv", "post_flight_suspects.csv", "rebuild_suspects.csv"):
        excl |= {r["bag_id"] for r in _read(rep / name)}
    excl |= set(load_acceptance_criteria()["building_scenario_rule"]["applies_to"])
    field_ids = set(re.findall(r"`(\d{16})`",
                               resolve("docs.manual_steps").parent.joinpath(
                                   "field_check_list.md").read_text(encoding="utf-8")))
    logger.info("C3 dislama: %d bina | saha listesinde zaten olan: %d", len(excl), len(field_ids))

    types = {
        "T2_yeni_konut": lambda r: "woonfunctie" in _funcs(r) and _year(r) >= T2_MIN_YEAR,
        "T3_okul": lambda r: ("onderwijsfunctie" in _funcs(r) and "woonfunctie" not in _funcs(r)
                              and float(r["footprint_area_m2"]) >= T3_MIN_AREA_M2),
    }

    def f(b: str, col: str) -> float:
        v = H[b][col]
        return float(v) if v else float("nan")

    def dens6(b: str) -> float:
        return int(H[b]["class6_points"]) / float(H[b]["footprint_area_m2"])

    out_rows: list[list] = []
    params: dict = {}
    for tname, rule in types.items():
        funnel = []
        pool = [b for b, r in H.items() if rule(r)]
        funnel.append((f"{tname} tip kurali", len(pool)))
        pool = [b for b in pool if b not in excl]
        funnel.append(("C3 ucus sonrasi / yeniden yapim / senaryo listelerinde degil", len(pool)))
        pool = [b for b in pool if H[b]["h_measured_m"]]
        funnel.append(("yuksekligi olculmus", len(pool)))
        pool = [b for b in pool if int(H[b]["class6_points"]) >= C4_MIN_C6]
        funnel.append((f"C4 sinif 6 >= {C4_MIN_C6} nokta", len(pool)))
        pool = [b for b in pool if f(b, "roof_span_m") < C5_MAX_SPAN]
        funnel.append((f"C5 duz cati (span < {C5_MAX_SPAN} m)", len(pool)))
        pool = [b for b in pool if int(H[b]["ground_ring_points"]) >= C6_MIN_GROUND]
        funnel.append((f"C6 halkada >= {C6_MIN_GROUND} zemin noktasi", len(pool)))
        pool = [b for b in pool if f(b, "h_measured_m") >= C7_MIN_H]
        funnel.append((f"C7 h >= {C7_MIN_H} m", len(pool)))
        pool = [b for b in pool if b not in field_ids]
        funnel.append(("saha listesinde henuz yok", len(pool)))
        for label, cnt in funnel:
            logger.info("HUNI %s | %-58s %5d", tname, label, cnt)

        if len(pool) < N_TERTILES * 2:
            logger.error("%s: havuz %d < %d — her tertilden asil+yedek secilemez",
                         tname, len(pool), N_TERTILES * 2)
            return 1
        pool.sort(key=lambda b: (f(b, "h_measured_m"), b))
        hs = np.array([f(b, "h_measured_m") for b in pool])
        picks, reserves = [], []
        for k, chunk in enumerate(np.array_split(np.array(pool), N_TERTILES), start=1):
            ranked = sorted(chunk.tolist(), key=lambda b: (-dens6(b), b))
            picks.append((k, ranked[0], len(chunk)))
            reserves.append((k, ranked[1], len(chunk)))
            logger.info("%s tertil %d | %d aday | h %.1f-%.1f | ASIL %s (h %.2f) | YEDEK %s (h %.2f)",
                        tname, k, len(chunk), f(chunk[0], "h_measured_m"),
                        f(chunk[-1], "h_measured_m"), ranked[0], f(ranked[0], "h_measured_m"),
                        ranked[1], f(ranked[1], "h_measured_m"))

        # --- M-016: amac iddiasi OLCULUR ---
        ph = [f(b, "h_measured_m") for _, b, _ in picks]
        p10, p90 = np.percentile(hs, [10, 90])
        cover = (max(ph) - min(ph)) / (p90 - p10) if p90 > p10 else float("nan")
        distinct = len({k for k, _, _ in picks}) == N_TERTILES
        ok = distinct and cover >= 0.5
        logger.info("AMAC OLCUMU (M-016) %s | secilen h %s | havuz p10-p90 %.1f-%.1f | "
                    "kapsama %.2f | farkli tertil: %s | IDDIA: %s", tname,
                    " ".join(f"{v:.1f}" for v in sorted(ph)), p10, p90, cover, distinct,
                    "TUTTU" if ok else "TUTMADI")
        if not ok:
            logger.warning("%s amac iddiasi TUTMADI — kural DEGISTIRILMEZ (M-016); "
                           "ONERI ayri cikti olarak uretilmeli.", tname)

        for role, items in (("ASIL", picks), ("YEDEK - yalnizca asil KULLANILAMAZSA (D-035/D-032)",
                                               reserves)):
            for k, b, n in items:
                r = H[b]
                out_rows.append([tname, k, role, b, r["alan"], r["footprint_area_m2"], r["bouwjaar"],
                                 r["gebruiksdoel"], r["h_measured_m"], r["roof_span_m"],
                                 r["class6_points"], f"{dens6(b):.2f}", n, "", ""])
        params[tname] = {"funnel": dict(funnel), "pool": len(pool),
                         "picked": [b for _, b, _ in picks], "reserves": [b for _, b, _ in reserves],
                         "purpose_claim_holds": ok, "coverage_ratio": cover}

    out = rep / "storey_height_calibration_types.csv"
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["tip", "tertil", "rol", "bag_id", "alan", "footprint_area_m2", "bouwjaar",
                    "gebruiksdoel", "h_measured_m", "roof_span_m", "class6_points",
                    "class6_density_p_m2", "tertil_aday_sayisi", "KAT_SAYISI_kullanici",
                    "NOT_kullanici"])
        w.writerows(out_rows)
    write_meta(out, run_id=run_id, random_seed=seed, inputs=[rep / "building_heights_ahn5.csv"],
               parameters=params,
               notes=("Kural: function_type_stratification (D-035, muhur a20b15f). "
                      "Deterministik; seed yalnizca kayit icindir."))
    logger.info("TAMAM | %s | %d satir", out.name, len(out_rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
