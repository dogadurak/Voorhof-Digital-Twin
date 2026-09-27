"""3DBAG'in kendi uyum artigi (b3_rmse_lod22) dagilimini A alaninda ozetler.

Asama : 1 hazirlik (P-004 / D-034 — kriter 1-C-a esik ONERISININ referansi)
Neden : Kullanici talimati (2026-09-27): "Esikleri 3DBAG b3_rmse_lod22
        referansina bakarak oner, hesaptan once muhurle."
Ne DEGIL: Bizim sonucumuz degil. 3DBAG v2025.09.03'un yayimladigi, roofer'in
        hesapladigi bina basina RMSE'dir. Tanim (docs.3dbag.nl, 2026-09-27
        okundu): "Root Mean Square Error of the 3D distances between the point
        cloud and the LoD2.2 model"; 2024.12.16'dan beri "all the AHN building
        points" ile hesaplanir.

Karsilastirma kumesi: A alanindaki binalar, 3DBAG `b3_pw_bron == ahn5` (bizim
girdimizle ayni nokta bulutu). Katman: 3DBAG `b3_dak_type` (sabit, olcumden
once var olan oznitelik).

Cikti : reports/01_prep_3dbag_rmse_reference.csv (+ .meta.json)
        reports/01_prep_3dbag_rmse_reference.md (+ .meta.json)
"""

from __future__ import annotations

import csv
import gzip
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import src.common  # noqa: E402,F401

from src.common.config import resolve  # noqa: E402
from src.common.logging_setup import setup_logging  # noqa: E402
from src.common.meta import git_commit, sha256, utc_now, write_meta  # noqa: E402

PCTS = [10, 25, 50, 75, 90, 95]
STRATA = ["horizontal", "multiple horizontal", "slanted"]


def summarize(v: np.ndarray) -> dict:
    """Bina basina RMSE vektorunu ozetler. Birim: m (oranlar haric)."""
    q = np.percentile(v, PCTS)
    return {"n": int(v.size), **{f"p{p}": float(x) for p, x in zip(PCTS, q)},
            "max": float(v.max()), "rms_unweighted": float(np.sqrt((v ** 2).mean())),
            "share_le_0.10": float(np.mean(v <= 0.10)),
            "share_le_0.25": float(np.mean(v <= 0.25))}


def main() -> int:
    logger, run_id, _ = setup_logging("reference_rmse_3dbag")
    hcsv = resolve("reports.dir") / "building_heights_ahn5.csv"
    area = {r["bag_id"]: r["alan"] for r in csv.DictReader(hcsv.open(encoding="utf-8"))}

    tiles = sorted((resolve("data.raw") / "3dbag_v20250903").glob("*.city.json.gz"))
    recs: dict[str, dict] = {}
    for f in tiles:
        cj = json.loads(gzip.open(f, "rt", encoding="utf-8").read())
        for o in cj["CityObjects"].values():
            if o.get("type") != "Building":
                continue
            a = o["attributes"]
            bid = str(a.get("identificatie", "")).split(".")[-1]
            if area.get(bid) == "A" and bid not in recs:
                recs[bid] = a
    n_a = sum(1 for v in area.values() if v == "A")
    logger.info("A alani: %d bina | 3DBAG'de eslesen: %d", n_a, len(recs))

    sel = {b: r for b, r in recs.items() if r.get("b3_pw_bron") == "ahn5"}
    n_other = len(recs) - len(sel)
    n_null = sum(1 for r in sel.values() if r.get("b3_rmse_lod22") is None)
    logger.info("pw_bron=ahn5: %d | baska nokta bulutu (kume disi): %d | rmse null: %d",
                len(sel), n_other, n_null)

    out_csv = resolve("reports.dir") / "01_prep_3dbag_rmse_reference.csv"
    with out_csv.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["bag_id", "b3_dak_type", "b3_rmse_lod22_m", "b3_pw_bron",
                    "b3_mutatie_ahn4_ahn5", "b3_kwaliteitsindicator"])
        for b in sorted(recs):
            r = recs[b]
            w.writerow([b, r.get("b3_dak_type"), r.get("b3_rmse_lod22"), r.get("b3_pw_bron"),
                        r.get("b3_mutatie_ahn4_ahn5"), r.get("b3_kwaliteitsindicator")])

    stats = {}
    groups = {"TUMU (pw_bron=ahn5)": list(sel)} | {
        s: [b for b in sel if sel[b].get("b3_dak_type") == s] for s in STRATA}
    other_types = sorted({str(sel[b].get("b3_dak_type")) for b in sel} - set(STRATA))
    for t in other_types:
        groups[f"diger: {t}"] = [b for b in sel if str(sel[b].get("b3_dak_type")) == t]
    for g, ids in groups.items():
        v = np.array([float(sel[b]["b3_rmse_lod22"]) for b in ids
                      if sel[b].get("b3_rmse_lod22") is not None])
        if v.size:
            stats[g] = summarize(v)
            logger.info("%s | n=%d | medyan %.3f | p90 %.3f", g, v.size,
                        stats[g]["p50"], stats[g]["p90"])

    head = ("| Katman (3DBAG b3_dak_type) | n | p10 | p25 | **medyan** | p75 | **p90** | p95 | "
            "max | RMS (agirliksiz) | <=0,10 m | <=0,25 m |")
    lines = [head, "|" + "---|" * 12]
    for g, s in stats.items():
        lines.append(f"| {g} | {s['n']} | {s['p10']:.3f} | {s['p25']:.3f} | **{s['p50']:.3f}** | "
                     f"{s['p75']:.3f} | **{s['p90']:.3f}** | {s['p95']:.3f} | {s['max']:.2f} | "
                     f"{s['rms_unweighted']:.3f} | {s['share_le_0.10']:.3f} | "
                     f"{s['share_le_0.25']:.3f} |")
    md = [
        "# 3DBAG uyum artigi referansi — b3_rmse_lod22, A alani",
        "",
        "> **Veri donemi:** geometri AHN5 2023-02-08/14 · oznitelik BAG 2026-09 (D-020).",
        "> **Bu bizim sonucumuz DEGILDIR.** 3DBAG v2025.09.03'un yayimladigi, roofer'in "
        "hesapladigi bina basina RMSE (3B nokta-model uzakligi, tum AHN bina noktalari). "
        "Kriter 1-C-a esik ONERISININ referansidir (P-004, D-034). Bir referansin "
        "uyum artigidir; bagimsiz dogrulama degildir.",
        "",
        f"run_id: `{run_id}` · git_commit: `{git_commit()}` · calistirma (UTC): {utc_now()}",
        "",
        f"A alani {n_a} bina · 3DBAG'de eslesen {len(recs)} · kume (pw_bron=ahn5) {len(sel)} · "
        f"baska nokta bulutundan uretilmis (kume disi) {n_other} · rmse null {n_null}.",
        "",
        *lines,
        "",
        "## Okuma",
        "",
        "- Dagilim **agir kuyruklu**: toplu RMS medyanin ~10 kati. Tek bir havuz RMSE "
        "esigi, 3DBAG'in kendisini bile kaldirirdi; kuyruk egimli ve cok seviyeli "
        "catilardan gelir.",
        "- Katman 3DBAG'in cati tipidir (bir rekonstruksiyon ciktisi); yanlis "
        "tiplenmis binalar katmanlar arasinda karisabilir.",
        "",
    ]
    out_md = resolve("reports.dir") / "01_prep_3dbag_rmse_reference.md"
    out_md.write_text("\n".join(md), encoding="utf-8")
    params = {"set": "A & b3_pw_bron == ahn5", "stratifier": "b3_dak_type", "stats": stats}
    for t in (out_csv, out_md):
        write_meta(t, run_id=run_id, inputs=[hcsv, *tiles], parameters=params,
                   notes="3DBAG v2025.09.03 sabitlenmis kopya (D-027).")
    logger.info("TAMAM | %s | %s", out_csv.name, out_md.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
