"""Cephe sinif olcumu — SONRADAN (post-hoc) KESIF ANALIZI. MUHURLU KARARI DEGISTIRMEZ.

Asama : 1 hazirlik (P-012 girdisi) · M-016 protokolu
Neden : Muhurlu olcum (measure_facade_classes.py) MIXED verdi ve bina SAYISINA
        gore ozet (medyan sinif 6 payi ~0,40) ile ETKIYE gore ozet (havuz ~0,23,
        en buyuk bloklarda 0,01-0,27) ayristi (M-010). Aday aciklama — CIKARIM:
        egimli catili binalarda sacak/cati kenari noktalari (sinif 6) cephe
        bolgesine dusuyor, cunku BAG ayakizi cati disi siniridir ve sacak
        'p30 - 1 m' ust sinirinin altinda kalabilir.
Sinama: Sinif 6 payini 3DBAG v2025.09.03 `b3_dak_type` katmanlarina gore kirar.
        Aciklama dogruysa duz catilarda (horizontal) sinif 6 payi belirgin
        dusuk, egimli catilarda (slanted) yuksek cikmalidir.
        Katman 3DBAG'den alinir (bizim ciktimiz degil), olcumden ONCE var olan
        sabit bir oznitelik.

Cikti : reports/01_prep_facade_class_posthoc.md (+ .meta.json)
        Etiket: ONERI / KESIF — muhurlu okuma kurali ve karari (MIXED) aynen gecerli.
"""

from __future__ import annotations

import csv
import gzip
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import src.common  # noqa: E402,F401

from src.common.config import resolve  # noqa: E402
from src.common.logging_setup import setup_logging  # noqa: E402
from src.common.meta import git_commit, utc_now, write_meta  # noqa: E402

CLS = [1, 2, 6, 9, 14, 26]


def main() -> int:
    logger, run_id, _ = setup_logging("facade_class_posthoc")
    rep = resolve("reports.dir")
    fcsv = rep / "facade_class_measurement_ahn5.csv"
    rows = list(csv.DictReader(fcsv.open(encoding="utf-8")))
    ids = {r["bag_id"] for r in rows}

    dak: dict[str, str] = {}
    tiles = sorted((resolve("data.raw") / "3dbag_v20250903").glob("*.city.json.gz"))
    for f in tiles:
        cj = json.loads(gzip.open(f, "rt", encoding="utf-8").read())
        for o in cj["CityObjects"].values():
            if o.get("type") != "Building":
                continue
            a = o["attributes"]
            bid = str(a.get("identificatie", "")).split(".")[-1]
            if bid in ids and bid not in dak:
                dak[bid] = a.get("b3_dak_type") or "null"
    logger.info("3DBAG dak_type eslesen: %d / %d", len(dak), len(ids))

    def tot(r, side):
        return sum(int(r[f"facade_{side}_c{c}"]) for c in CLS) + int(r[f"facade_{side}_other"])

    groups: dict[str, list] = defaultdict(list)
    for r in rows:
        groups[dak.get(r["bag_id"], "3DBAG'de yok")].append(r)

    lines = ["| 3DBAG b3_dak_type | bina | cephe noktasi | havuz s6 ic | havuz s6 dis | "
             "bina basina s6 medyan | s1 duvar yogunlasmasi |",
             "|---|---|---|---|---|---|---|"]
    summary = {}
    for g in sorted(groups, key=lambda k: -len(groups[k])):
        rs = groups[g]
        n_in = sum(tot(r, "in") for r in rs)
        n_out = sum(tot(r, "out") for r in rs)
        s6_in = sum(int(r["facade_in_c6"]) for r in rs) / n_in if n_in else float("nan")
        s6_out = sum(int(r["facade_out_c6"]) for r in rs) / n_out if n_out else float("nan")
        c1 = sum(int(r["facade_in_c1"]) + int(r["facade_out_c1"]) for r in rs)
        wc1 = sum(int(r["wall_c1"]) for r in rs) / c1 if c1 else float("nan")
        per = [float(r["facade_class6_share"]) for r in rs if r["facade_class6_share"]]
        med = float(np.median(per)) if per else float("nan")
        summary[g] = {"n": len(rs), "s6_in": s6_in, "s6_out": s6_out, "median": med, "wc1": wc1}
        lines.append(f"| {g} | {len(rs):,} | {n_in + n_out:,} | {s6_in:.3f} | {s6_out:.3f} | "
                     f"{med:.3f} | {wc1:.3f} |")
        logger.info("%s | n=%d | s6 ic %.3f dis %.3f | medyan %.3f | wc1 %.3f",
                    g, len(rs), s6_in, s6_out, med, wc1)

    md = [
        "# Cephe sinif olcumu — SONRADAN KESIF ANALIZI (ONERI)",
        "",
        "> **Veri donemi:** geometri AHN5 2023-02-08/14 · oznitelik BAG 2026-09 (D-020).",
        "> ⚠️ **Bu analiz sonuc GORULDUKTEN SONRA tasarlandi.** Muhurlu olcumun karari "
        "(`reports/01_prep_facade_class_measurement.md`: **MIXED**) DEGISMEZ. Burada "
        "yalnizca MIXED'in olasi bir aciklamasi sinaniyor (M-016 protokolu: kural "
        "degistirilmez, alternatif ayri cikti olarak ONERI etiketiyle uretilir).",
        "",
        f"run_id: `{run_id}` · git_commit: `{git_commit()}` · calistirma (UTC): {utc_now()}",
        "",
        "**Sinanan aciklama (CIKARIM):** egimli catilarda sacak/cati kenari noktalari "
        "(sinif 6) cephe bolgesine dusuyor. Dogruysa `horizontal` katmaninda sinif 6 "
        "payi dusuk, `slanted` katmaninda yuksek olmali.",
        "",
        "**Katman kaynagi:** 3DBAG v2025.09.03 `b3_dak_type` — bizim ciktimiz degil, "
        "olcumden once var olan sabit oznitelik.",
        "",
        *lines,
        "",
        "## Sinirlamalar",
        "",
        "- Post-hoc: katmanlama sonuc gorulduktan sonra secildi; kanit degeri muhurlu "
        "olcumden DUSUKTUR.",
        "- 3DBAG cati tipi bir rekonstruksiyon ciktisidir (roofer); yanlis tiplenmis "
        "binalar katmanlar arasinda karisir.",
        "- Katman icinde bile sinif 6 noktalarinin sacak mi, balkon mu, dakkapel mi "
        "oldugu ayirt edilmedi.",
        "",
    ]
    out = rep / "01_prep_facade_class_posthoc.md"
    out.write_text("\n".join(md), encoding="utf-8")
    write_meta(out, run_id=run_id, inputs=[fcsv],
               parameters={"stratifier": "3DBAG v2025.09.03 b3_dak_type", "summary": summary,
                           "label": "POST-HOC / ONERI — muhurlu karari degistirmez"},
               notes="3DBAG fayanslari: data/raw/3dbag_v20250903 (checksum'lar D-027'de).")
    logger.info("TAMAM | %s", out.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
