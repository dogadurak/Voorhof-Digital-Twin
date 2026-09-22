"""config/acceptance_criteria.yml YAPISINI dogrular (M-015 otomatik kontrolu).

Neden var:
  M-015'te muhurlu bir blogun anahtarlari BASKA bir blogun icine dustu. YAML
  bunu bir hata olarak gormez: 4 bosluk girintili bir anahtar, kendinden once
  gelen 2 bosluk girintili anahtarin degerine sessizce baglanir. Dosya gecerli
  kalir, `git diff` "eklendi" der, kimse fark etmez.

Ne yapar:
  1. Dosyayi ayristirir (YAML gecerliligi).
  2. Asagidaki BEKLENEN YOL listesindeki her anahtar yolunun hala var oldugunu
     ve dogru ebeveynin altinda durdugunu dogrular.
  3. Muhurlu bloklarin `status` alanlarinin beklenen degerde oldugunu dogrular.
  4. Bir muhurlu blogun icinde TODO_ONAY_BEKLIYOR kalmissa listeler (hata
     degildir; acik karar demektir, sessizce unutulmasin diye yazdirilir).

Yeni bir muhurlu blok eklendiginde yolu buraya da eklenir. Liste elle tutulur
ama kontrol otomatiktir: yol kaybolursa test kirmizi yanar.

Calistirma:
    python src/qa/check_config_structure.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import src.common  # noqa: E402,F401

import yaml  # noqa: E402

from src.common.config import resolve  # noqa: E402

# (yol, aciklama) — yol nokta ile ayrilmis anahtar zinciri
EXPECTED_PATHS: list[tuple[str, str]] = [
    ("input_gate_ahn.hard_gate.threshold", "0-E sert kapi"),
    ("input_gate_ahn.expectation.threshold", "0-F beklenti"),
    ("input_gate_ahn.per_building_density.csv_columns", "bina bazli yogunluk sutunlari"),
    ("input_gate_ahn.per_building_density.csv_scope_note", "M-015 ile geri tasindi"),
    ("input_gate_ahn.per_building_density.purpose", "M-015 ile geri tasindi"),
    ("input_gate_ahn.per_building_density.why_no_threshold", "M-015 ile geri tasindi"),
    ("input_gate_ahn.per_building_class_ratio.definition", "sinif 6 orani tanimi"),
    ("input_gate_ahn.visual_check.seed", "gorsel orneklem seed'i"),
    ("post_flight_detection.post_flight_candidate.criteria", "K1/K2/K3"),
    ("post_flight_detection.rebuild_suspect.definition", "yeniden yapim supheli"),
    ("building_scenario_rule.scenarios.S1", "senaryo S1"),
    ("building_scenario_rule.scenarios.S2", "senaryo S2"),
    ("building_scenario_rule.scenarios.S3", "senaryo S3"),
    ("building_scenario_rule.scenarios.UNDECIDED.handling", "P-017 karari"),
    ("building_scenario_rule.pc6_exclusion.scope", "PC6 dislama kapsami"),
    ("building_lineage.values.measured_lod2", "koken: olculmus"),
    ("building_lineage.values.estimated_lod1", "koken: tahmini"),
    ("building_lineage.values.footprint_only", "koken: yalnizca ayakizi"),
    ("building_lineage.assignment.post_flight_small.lineage", "P-018 kucuk"),
    ("building_lineage.assignment.post_flight_large.lineage", "P-018 buyuk"),
    ("building_lineage.storey_height_evidence.regulation.value_m", "Bbl alt siniri"),
    ("storey_counting_rule.rules", "kat sayim kurali (D-030)"),
    ("storey_counting_rule.status", "kat sayim kurali muhur durumu"),
    ("storey_counting_rule.blind_counting.rule", "korlemesine sayim (D-030 EK 1)"),
    ("storey_height_calibration.selection", "kalibrasyon secim kurali"),
    ("storey_height_calibration.selection.stratification", "tabakalama (D-031)"),
    ("storey_height_calibration.selection.stratification_superseded_p020.status",
     "eski desil kurali — SILINMEMELI"),
    ("storey_height_calibration.selection.type_breakdown.decision_rule",
     "tip bazli kirilim karar kurali (D-031)"),
    ("storey_height_calibration.formula", "kat yuksekligi formulu"),
]

EXPECTED_STATUS: dict[str, str] = {
    "input_gate_ahn": "SEALED",
    "building_scenario_rule": "SEALED_BEFORE_OBSERVATION",
    "building_lineage": "SEALED",
    "storey_counting_rule": "SEALED_BEFORE_OBSERVATION",
    "storey_height_calibration": "SEALED_BEFORE_OBSERVATION",
}


def _dig(cfg: dict, path: str):
    """Nokta ile ayrilmis yolu izler; bulunamazsa KeyError yerine sentinel doner."""
    node = cfg
    for key in path.split("."):
        if not isinstance(node, dict) or key not in node:
            return None, False
        node = node[key]
    return node, True


def main() -> int:
    path = resolve("config.acceptance_criteria")
    cfg = yaml.safe_load(path.read_text(encoding="utf-8"))

    bad: list[str] = []
    for dotted, label in EXPECTED_PATHS:
        _, found = _dig(cfg, dotted)
        if not found:
            bad.append(f"EKSIK YOL: {dotted}  ({label})")

    for block, want in EXPECTED_STATUS.items():
        got, found = _dig(cfg, f"{block}.status")
        if not found:
            bad.append(f"EKSIK: {block}.status")
        elif got != want:
            bad.append(f"STATUS: {block}.status = {got!r}, beklenen {want!r}")

    todo: list[str] = []

    def walk(node, prefix: str) -> None:
        if isinstance(node, dict):
            for k, v in node.items():
                walk(v, f"{prefix}.{k}" if prefix else str(k))
        elif isinstance(node, str) and node.startswith("TODO_"):
            todo.append(f"{prefix} = {node}")

    walk(cfg, "")

    print(f"config: {path}")
    print(f"beklenen yol: {len(EXPECTED_PATHS)} | dogrulanan: {len(EXPECTED_PATHS) - len([b for b in bad if b.startswith('EKSIK YOL')])}")
    for line in bad:
        print("  HATA:", line)
    if todo:
        print(f"\nAcik TODO ({len(todo)}) — hata degil, karar bekliyor:")
        for line in todo:
            print("  -", line)

    print("\nSONUC:", "FAIL" if bad else "PASS")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
