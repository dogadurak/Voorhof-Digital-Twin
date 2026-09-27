"""T2/T3 kalibrasyon secimi icin ONERI ciktisi (M-016) — muhurlu secimi DEGISTIRMEZ.

T3: amac iddiasi TUTMADI (secilen 3 okul tek katli).
T2: amac iddiasi (h yayilimi) TUTTU, ama secilenler hedeflere benzemiyor: havuz
    medyan ayakizi 58 m2 (sira ev), secilen asil 20 ve 41 m2; hedefler 300-500 m2
    bloklar. Iddia yalnizca yayilimi olcuyordu, hedef benzerligini degil
    (ajanin tespiti, 2026-09-27).


Asama : 0.3 · D-035
Durum : select_calibration_type_strata.py muhurlu kurali uyguladi; secilen 3 okul
        h 3,9-4,3 m (tek katli), amac iddiasi (kapsama >= 0,5) TUTMADI. Kural
        DEGISTIRILMEZ. Bu script yalnizca kullanicinin karar verebilmesi icin
        T3 havuzunun TAMAMINI (C5 ile elenenler dahil) ve iki alternatifi yazar.
        Hicbir secimi gecerli kilmaz; karar sayimdan ONCE kullanicinindir.

Cikti : reports/00_stage_0_3_type_calibration_ONERI.md (+ .meta.json)
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import src.common  # noqa: E402,F401

from src.common.config import resolve  # noqa: E402
from src.common.logging_setup import setup_logging  # noqa: E402
from src.common.meta import git_commit, utc_now, write_meta  # noqa: E402


def _read(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def main() -> int:
    logger, run_id, _ = setup_logging("propose_t3_alternative")
    rep = resolve("reports.dir")
    H = _read(rep / "building_heights_ahn5.csv")
    sel = {r["bag_id"]: r["rol"] for r in _read(rep / "storey_height_calibration_types.csv")
           if r["tip"] == "T3_okul"}
    excl: set[str] = set()
    for name in ("post_flight_buildings.csv", "post_flight_suspects.csv", "rebuild_suspects.csv"):
        excl |= {r["bag_id"] for r in _read(rep / name)}

    rows = []
    for r in H:
        fn = {x.strip() for x in (r["gebruiksdoel"] or "").split(",")}
        if "onderwijsfunctie" in fn and "woonfunctie" not in fn and float(r["footprint_area_m2"]) >= 100:
            why = []
            if r["bag_id"] in excl:
                why.append("C3 ucus sonrasi/yeniden yapim")
            if not r["h_measured_m"]:
                why.append("olculemedi")
            else:
                if float(r["roof_span_m"]) >= 1.5:
                    why.append("C5 egik/cok seviyeli cati (span >= 1,5)")
                if int(r["ground_ring_points"]) < 50:
                    why.append("C6")
            rows.append((r, "; ".join(why) or "UYGUN"))
    rows.sort(key=lambda x: -float(x[0]["h_measured_m"] or 0))
    elig = [r for r, w in rows if w == "UYGUN"]

    tbl = ["| bag_id | alan | bouwjaar | ayakizi m2 | h (m) | span (m) | durum | muhurlu secimde |",
           "|---|---|---|---|---|---|---|---|"]
    for r, w in rows:
        tbl.append(f"| `{r['bag_id']}` | {r['alan']} | {r['bouwjaar']} | {float(r['footprint_area_m2']):.0f} | "
                   f"{r['h_measured_m'] or '—'} | {r['roof_span_m'] or '—'} | {w} | "
                   f"{sel.get(r['bag_id'], '')[:5]} |")
    hs = sorted(elig, key=lambda r: (float(r["h_measured_m"]), r["bag_id"]))
    alt1 = [hs[0], hs[len(hs) // 2], hs[-1]] if len(hs) >= 3 else hs
    n_c5 = sum(1 for _, w in rows if "C5" in w and "C3" not in w)
    n_c5_tall = sum(1 for r, w in rows if "C5" in w and "C3" not in w and float(r["h_measured_m"]) >= 7.0)

    md = [
        "# T3 (okul) kalibrasyon secimi — amac iddiasi TUTMADI · ONERI",
        "",
        "> **Veri donemi:** geometri AHN5 2023-02-08/14 · oznitelik BAG 2026-09 (D-020).",
        "> Muhurlu kural (D-035, a20b15f) uygulandi ve **degistirilmedi**. Bu belge yalnizca "
        "kullanicinin SAYIMDAN ONCE karar vermesi icindir (M-016). Kat sayisi henuz yok; "
        "hicbir kat yuksekligi hesaplanmadi.",
        "",
        f"run_id: `{run_id}` · git_commit: `{git_commit()}` · calistirma (UTC): {utc_now()}",
        "",
        "## Ne oldu",
        "",
        "Muhurlu secim her h-tertilinden bir okul aldi. Uygun havuz 8 okul; bunlarin "
        "7'si 3,9-5,9 m (tek katli olcekte), yalnizca biri daha yuksek. Uc tertil de tek "
        "katli okullardan olustu; amac iddiasi (secilenlerin araligi havuz p10-p90'in "
        ">= yarisi) TUTMADI.",
        "",
        "**Neden onemli (CIKARIM):** estimated_lod1 hedefi olan iki yeni okulun kat "
        "sayisi bilinmiyor; cok katli iseler tek katli okullardan turetilen deger onlari "
        "temsil etmez. Ayrica tek katli binada `known_bias` (plint + parapet / kat sayisi) "
        "en buyuktur.",
        "",
        f"C5 (duz cati) filtresi {n_c5} okulu eledi; bunlarin {n_c5_tall}'i h >= 7 m.",
        "",
        "## T3 havuzunun tamami (h'ye gore)",
        "",
        *tbl,
        "",
        "## Alternatifler (ONERI — hicbiri gecerli degil, kullanici secer)",
        "",
        "- **(a) Muhurlu secimi koru.** Sonuc 'tek katli okul' degeri olarak raporlanir; "
        "hedef okullar cok katliysa bu SINIRLAMA olur.",
        "- **(b) Uygun havuzdan min / medyan / maks h** (C5 korunur): "
        + ", ".join(f"`{r['bag_id']}` ({r['h_measured_m']} m)" for r in alt1) + ".",
        "- **(c) C5'i T3 icin gevset** (egik catili okullar da girer). DIKKAT: C5'in "
        "gerekcesi egik catinin h/kat'i SISTEMATIK buyutmesidir; gevsetmek bu sapmayi "
        "geri getirir.",
        "",
        "Ajanin onerisi: **(b)** — C5'in gerekcesini korur, araligi kapsar. Karar "
        "verilince yeni bir D kaydi + ayri commit; sayimdan ONCE.",
        "",
    ]
    # ---------------- T2: >= 100 m2 alternatifi ----------------
    import numpy as np
    t2sel = {r["bag_id"]: r for r in _read(rep / "storey_height_calibration_types.csv")
             if r["tip"] == "T2_yeni_konut"}
    field_ids = set()   # ayni dislama: C3 + tip + filtreler; saha listesi burada onemsiz
    t2 = []
    for r in H:
        fn = {x.strip() for x in (r["gebruiksdoel"] or "").split(",")}
        yr = int(r["bouwjaar"]) if r["bouwjaar"].isdigit() else 0
        if ("woonfunctie" in fn and yr >= 2000 and r["bag_id"] not in excl and r["h_measured_m"]
                and int(r["class6_points"]) >= 200 and float(r["roof_span_m"]) < 1.5
                and int(r["ground_ring_points"]) >= 50 and float(r["h_measured_m"]) >= 3.0):
            t2.append(r)
    areas = np.array([float(r["footprint_area_m2"]) for r in t2])
    big = sorted([r for r in t2 if float(r["footprint_area_m2"]) >= 100],
                 key=lambda r: (float(r["h_measured_m"]), r["bag_id"]))
    alt_t2 = []
    for chunk in np.array_split(np.array(big, dtype=object), 3):
        ranked = sorted(chunk.tolist(), key=lambda r: (-int(r["class6_points"]) / float(r["footprint_area_m2"]),
                                                         r["bag_id"]))
        if ranked:
            alt_t2.append(ranked[0])
    t2tbl = ["| bag_id | alan | bouwjaar | ayakizi m2 | gebruiksdoel | h (m) | alternatifte |",
             "|---|---|---|---|---|---|---|"]
    for r in big:
        t2tbl.append(f"| `{r['bag_id']}` | {r['alan']} | {r['bouwjaar']} | {float(r['footprint_area_m2']):.0f} | "
                     f"{r['gebruiksdoel']} | {r['h_measured_m']} | {'ASIL' if r in alt_t2 else ''} |")
    sel_t2 = [r for r in t2sel.values() if r["rol"] == "ASIL"]
    md += [
        "---",
        "",
        "# T2 (yeni konut) — iddia TUTTU ama secilenler hedeflere BENZEMIYOR · ONERI",
        "",
        f"Uygun T2 havuzu {len(t2)} bina; ayakizi p10/medyan/p90 = "
        f"{np.percentile(areas, 10):.0f} / {np.percentile(areas, 50):.0f} / {np.percentile(areas, 90):.0f} m2 "
        f"(tek tek kayitli sira evler). >= 100 m2 olan: **{len(big)}**.",
        "",
        "Muhurlu secimin asillari: " + ", ".join(
            f"`{r['bag_id']}` ({float(r['footprint_area_m2']):.0f} m2, h {r['h_measured_m']} m)" for r in sel_t2) + ".",
        "",
        "estimated_lod1 hedeflerinden T2 olanlarin ayakizi 298-496 m2 (post_flight_buildings.csv). "
        "Muhurlu amac iddiasi yalnizca h yayilimini olcuyordu; hedef benzerligini olcmuyordu "
        "(ajanin tespiti). Siralama olcutu (sinif 6 yogunlugu) kucuk ayakizlerini one cikariyor "
        "— kenar etkisi olabilir (CIKARIM, olculmedi).",
        "",
        "**(b') ONERI:** ayni tertil kurali, havuz **>= 100 m2** ile sinirli (D-029'daki "
        "'buyuk' esigi — yeni sayi degil):",
        "",
        *t2tbl,
        "",
        "DIKKAT: (b') secilirse bu binalar saha listesine EKLENMELIDIR (su an listede degiller) "
        "ve karar sayimdan ONCE verilir.",
        "",
    ]
    out = rep / "00_stage_0_3_type_calibration_ONERI.md"
    out.write_text("\n".join(md), encoding="utf-8")
    write_meta(out, run_id=run_id, inputs=[rep / "building_heights_ahn5.csv",
                                           rep / "storey_height_calibration_types.csv"],
               parameters={"eligible": [r["bag_id"] for r in elig],
                           "alt_b": [r["bag_id"] for r in alt1],
                           "t2_alt_b_prime": [r["bag_id"] for r in alt_t2], "label": "ONERI (M-016)"})
    logger.info("ONERI yazildi | uygun %d | alt (b): %s", len(elig), [r["bag_id"] for r in alt1])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
