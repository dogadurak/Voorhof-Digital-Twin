"""Belirsiz geometrili binalarin A / B\\A ve konut kirilimi.

Asama : 0.3  (Karar D-022; raporlama kurali Bolum 14.6 / M-010)
Girdi : reports/post_flight_buildings.csv, post_flight_suspects.csv,
        rebuild_suspects.csv  (detect_post_flight_buildings.py ciktisi)
Cikti : reports/00_stage_0_3_uncertain_geometry_breakdown.md
        aoi/qa/a_residential_uncertain.geojson

ASIL SORU: A'daki KONUT STOKUNUN ne kadari belirsiz geometriye sahip?

"Konut" tanimi D-008'in `exact_match` kuralidir: bir verblijfsobject'in
gebruiksdoel'u TAM OLARAK "woonfunctie" ise konuttur. Coklu islevli kayitlar
("woonfunctie,winkelfunctie") konut SAYILMAZ. Pand duzeyindeki gebruiksdoel
kullanilmaz — bu bir toplamdir ve konut SAYISINI vermez.

Bu script LAZ OKUMAZ; tespit zaten yapilmistir.

Calistirma:
    python src/00_acquisition/report_uncertain_geometry.py
"""

from __future__ import annotations

import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import numpy as np
from pyproj import Transformer
from shapely.geometry import shape

from src.common.config import load_acceptance_criteria, resolve
from src.common.logging_setup import setup_logging, log_rowcount
from src.common.meta import write_meta

GROUPS = {
    "post_flight": ("post_flight_buildings.csv", "ucus sonrasi aday"),
    "suspect": ("post_flight_suspects.csv", "supheli (2/3)"),
    "rebuild": ("rebuild_suspects.csv", "olasi yeniden yapim"),
}


def main() -> int:
    logger, run_id, _ = setup_logging("report_uncertain_geometry")
    cfg = load_acceptance_criteria()
    sf = cfg["stage_0_2"]["status_filter"]
    rep = resolve("reports.dir")
    aoi = resolve("root.aoi")

    area_a = shape(json.loads((aoi / "area_A_analysis.geojson").read_text(
        encoding="utf-8"))["features"][0]["geometry"])
    area_b = shape(json.loads((aoi / "area_B_context.geojson").read_text(
        encoding="utf-8"))["features"][0]["geometry"])

    # --- panden (B icinde, status filtreli) ---
    raw = json.loads((resolve("data.raw") / "bag" / "bag_pand.geojson")
                     .read_text(encoding="utf-8"))["features"]
    panden = [f for f in raw
              if f["properties"].get("status") in sf["pand_include"]
              and area_b.contains(shape(f["geometry"]).centroid)]
    log_rowcount(logger, "bag_pand -> B icinde + status filtreli", len(raw), len(panden))

    # Bolum 14.6: dusen satirlarin NEDENI ayristirilir, yalnizca sayilmaz.
    drop = Counter()
    for f in raw:
        ok_s = f["properties"].get("status") in sf["pand_include"]
        ok_b = area_b.contains(shape(f["geometry"]).centroid)
        if not (ok_s and ok_b):
            drop[("status disi" if not ok_s else "status uygun") + " / " +
                 ("B disi" if not ok_b else "B ici")] += 1
    for k, v in sorted(drop.items()):
        logger.info("  dusen pand | %-28s %5d", k, v)

    geoms = {f["properties"]["identificatie"]: shape(f["geometry"]) for f in panden}
    props = {f["properties"]["identificatie"]: f["properties"] for f in panden}
    feat_by_id = {f["properties"]["identificatie"]: f for f in panden}
    in_a = {k: area_a.contains(g.centroid) for k, g in geoms.items()}

    # --- VBO -> pand, D-008 exact_match ---
    vbo_raw = json.loads((resolve("data.raw") / "bag" / "bag_verblijfsobject.geojson")
                         .read_text(encoding="utf-8"))["features"]
    woon = Counter()
    vbo_all = Counter()
    kept = 0
    for f in vbo_raw:
        p = f["properties"]
        if p.get("status") not in sf["vbo_include"]:
            continue
        kept += 1
        pid = p.get("pandidentificatie")
        if pid is None:
            continue
        for one in str(pid).split(","):           # bir VBO birden cok pand'a bagli olabilir
            one = one.strip()
            vbo_all[one] += 1
            if (p.get("gebruiksdoel") or "").strip() == "woonfunctie":
                woon[one] += 1
    log_rowcount(logger, "VBO -> status filtreli", len(vbo_raw), kept)
    vbo_drop = Counter(f["properties"].get("status") for f in vbo_raw
                       if f["properties"].get("status") not in sf["vbo_include"])
    for k, v in vbo_drop.items():
        logger.info("  dusen VBO | %-28s %5d (D-008 geregi dislanir)", k, v)
    # Bolum 14.6 sessiz veri kaybi: pand indirmesinde karsiligi olmayan VBO'lar
    all_pand_ids = {f["properties"]["identificatie"] for f in raw}
    orphan = sorted(k for k in vbo_all if k not in all_pand_ids)
    if orphan:
        logger.warning("Pand indirmesinde karsiligi OLMAYAN VBO pand_id: %d adet -> %s",
                       len(orphan), ", ".join(orphan[:5]))
    logger.info("Konut VBO (exact_match) tasiyan pand: %d | toplam konut VBO: %d",
                sum(1 for v in woon.values() if v > 0), sum(woon.values()))

    # --- gruplar ---
    grp_ids: dict[str, set[str]] = {}
    for key, (fname, _) in GROUPS.items():
        ids = set()
        with (rep / fname).open(encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                ids.add(row["bag_id"])
        grp_ids[key] = ids
        logger.info("%s | %d bina", fname, len(ids))

    # bir bina birden cok gruba girebilir mi? rebuild ile post_flight disjoint
    # (R2 geregi) ama supheli ile rebuild ortusebilir -> olculur, varsayilmaz
    overlap = grp_ids["suspect"] & grp_ids["rebuild"]
    logger.info("supheli ∩ yeniden yapim = %d bina (ortusme OLCULDU)", len(overlap))
    assert not (grp_ids["post_flight"] & grp_ids["rebuild"]), \
        "post_flight ile rebuild ortusmemeli (R2)"

    # --- kirilim ---
    def stats(ids):
        n = len(ids)
        a = sum(geoms[i].area for i in ids if i in geoms)
        v = sum(woon.get(i, 0) for i in ids)
        vt = sum(vbo_all.get(i, 0) for i in ids)
        return n, a, v, vt

    all_a = {k for k, v in in_a.items() if v}
    all_ba = {k for k, v in in_a.items() if not v}
    res_a = {k for k in all_a if woon.get(k, 0) > 0}       # A'da konut VBO'lu
    non_a = all_a - res_a

    tot_a = stats(all_a); tot_ba = stats(all_ba)
    tot_res_a = stats(res_a)
    logger.info("=== TABAN ===")
    logger.info("  A      : %d bina | %.0f m2 | %d konut VBO", *tot_a[:3])
    logger.info("  B\\A    : %d bina | %.0f m2 | %d konut VBO", *tot_ba[:3])
    logger.info("  A konut: %d bina | %.0f m2 | %d konut VBO", *tot_res_a[:3])

    lines = []
    head = ("| Grup | Bina | Bina payi | Alan m2 | Alan payi | Konut VBO | Konut VBO payi |\n"
            "|---|---|---|---|---|---|---|")

    def block(title, universe, tot):
        out = [f"\n### {title}\n", head]
        for key, (_, label) in GROUPS.items():
            s = stats(grp_ids[key] & universe)
            out.append(
                f"| {label} | **{s[0]}** | %{100*s[0]/max(1,tot[0]):.2f} | "
                f"{s[1]:,.0f} | %{100*s[1]/max(1e-9,tot[1]):.2f} | "
                f"**{s[2]}** | **%{100*s[2]/max(1,tot[2]):.2f}** |")
        u = (grp_ids["post_flight"] | grp_ids["suspect"] | grp_ids["rebuild"]) & universe
        s = stats(u)
        out.append(f"| **BIRLESIM (tekil)** | **{s[0]}** | %{100*s[0]/max(1,tot[0]):.2f} | "
                   f"{s[1]:,.0f} | %{100*s[1]/max(1e-9,tot[1]):.2f} | "
                   f"**{s[2]}** | **%{100*s[2]/max(1,tot[2]):.2f}** |")
        out.append(f"\nTaban: {tot[0]:,} bina · {tot[1]:,.0f} m2 · {tot[2]:,} konut VBO")
        return "\n".join(out), s

    b_a, u_a = block("A alani (raporlama alani)", all_a, tot_a)
    b_ba, _ = block("B \\ A (yalniz baglam)", all_ba, tot_ba)
    b_res, u_res = block("A alani — YALNIZCA konut VBO'lu binalar", res_a, tot_res_a)
    b_non, _ = block("A alani — konut VBO'su OLMAYAN binalar", non_a, stats(non_a))

    lines += [b_a, b_ba, b_res, b_non]

    # --- A'daki belirsiz konut binalari -> GeoJSON ---
    uncertain_res = sorted((grp_ids["post_flight"] | grp_ids["suspect"]
                            | grp_ids["rebuild"]) & res_a)
    tf = Transformer.from_crs("EPSG:28992", "EPSG:4326", always_xy=True)
    feats = []
    for bid in uncertain_res:
        g = geoms[bid]; p = props[bid]
        grp = [lbl for k, (_, lbl) in GROUPS.items() if bid in grp_ids[k]]
        lon, lat = tf.transform(g.centroid.x, g.centroid.y)
        feats.append({
            "type": "Feature",
            "geometry": feat_by_id[bid]["geometry"],
            "properties": {
                "bag_id": bid,
                "grup": " + ".join(grp),
                "bouwjaar": p.get("bouwjaar"),
                "status": p.get("status"),
                "gebruiksdoel_pand": p.get("gebruiksdoel") or "",
                "woonfunctie_vbo": int(woon.get(bid, 0)),
                "vbo_toplam": int(vbo_all.get(bid, 0)),
                "footprint_area_m2": round(g.area, 2),
                "lat": round(lat, 7),
                "lon": round(lon, 7),
                "gozlem": "",          # kullanici dolduracak
            },
        })
    gj = aoi / "qa" / "a_residential_uncertain.geojson"
    gj.parent.mkdir(parents=True, exist_ok=True)
    gj.write_text(json.dumps({
        "type": "FeatureCollection",
        "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:EPSG::28992"}},
        "features": feats,
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    logger.info("A'da belirsiz geometrili KONUT binasi: %d -> %s", len(feats), gj.name)

    csv_path = rep / "a_residential_uncertain.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["bag_id", "grup", "bouwjaar", "status", "woonfunctie_vbo",
                    "vbo_toplam", "footprint_area_m2", "lat", "lon", "gozlem"])
        for f in sorted(feats, key=lambda f: -f["properties"]["woonfunctie_vbo"]):
            p = f["properties"]
            w.writerow([p["bag_id"], p["grup"], p["bouwjaar"], p["status"],
                        p["woonfunctie_vbo"], p["vbo_toplam"],
                        p["footprint_area_m2"], p["lat"], p["lon"], ""])

    grp_count = Counter(f["properties"]["grup"] for f in feats)
    top = sorted(feats, key=lambda f: -f["properties"]["woonfunctie_vbo"])[:5]

    out = rep / "00_stage_0_3_uncertain_geometry_breakdown.md"
    out.write_text(f"""# Belirsiz geometri — A / B\\\\A ve konut kirilimi

**Karar D-022** · run_id `{run_id}` · LAZ okunmadi, tespit ciktisi kullanildi

> **VERI DONEMI (D-020).** Geometri AHN5 **2023-02-08 / 02-14**; BAG
> oznitelikleri **2026-09**.

**"Konut" tanimi (D-008 `exact_match`):** bir verblijfsobject'in
`gebruiksdoel`'u **tam olarak** `woonfunctie` ise konuttur. Coklu islevli
kayitlar konut sayilmaz. Pand duzeyindeki `gebruiksdoel` **kullanilmadi** —
o bir toplamdir, konut SAYISI vermez.

## ASIL SORU: A'daki konut stokunun ne kadari belirsiz geometriye sahip?

| | Deger |
|---|---|
| A'daki toplam konut VBO | **{tot_a[2]:,}** |
| Bunlardan belirsiz geometrili binalarda olan | **{u_a[2]:,}** |
| **Pay** | **%{100*u_a[2]/max(1,tot_a[2]):.2f}** |
| Etkilenen bina sayisi | {u_a[0]} |
| Etkilenen ayakizi alani | {u_a[1]:,.0f} m2 (A'nin %{100*u_a[1]/max(1e-9,tot_a[1]):.2f}'i) |

{chr(10).join(lines)}

## Satir kaybi — nedenleriyle (Bolum 14.6 "sessiz veri kaybi")

| Adim | Once | Sonra | Dusen | Neden |
|---|---|---|---|---|
| BAG pand -> B ici + status | {len(raw):,} | {len(panden):,} | {len(raw)-len(panden):,} | {"; ".join(f"{k}: {v:,}" for k, v in sorted(drop.items()))} |
| VBO -> status | {len(vbo_raw):,} | {kept:,} | {len(vbo_raw)-kept:,} | {"; ".join(f"{k}: {v:,}" for k, v in vbo_drop.items())} (D-008) |
| VBO -> pand eslesmesi | — | — | {len(orphan)} | pand indirmesinde karsiligi yok: {", ".join(orphan) or "—"} |

"B disi" satirlarinin tamami beklenendir: BAG indirmesi **B + 300 m
dikdortgeni** icindi (D-006), B ise bir **poligondur**; dikdortgenin
kosesindeki binalar B'ye girmez.

## Gruplarin ortusmesi

`post_flight` ∩ `rebuild` = **0** (kural geregi, R2).
`supheli` ∩ `rebuild` = **{len(overlap)}** bina — **olculdu, varsayilmadi**.
Birlesim satirlari tekil sayar.

## A'daki belirsiz geometrili KONUT binalari

**{len(feats)} bina**, toplam **{sum(f['properties']['woonfunctie_vbo'] for f in feats):,} konut VBO**.

Grup dagilimi:

| Grup | Bina |
|---|---|
{chr(10).join(f'| {k} | {v} |' for k, v in grp_count.most_common())}

Konut VBO sayisina gore en buyuk 5 (Bolum 14.6):

| # | bag_id | konut VBO | m2 | bouwjaar | grup |
|---|---|---|---|---|---|
{chr(10).join(f"| {i} | `{f['properties']['bag_id']}` | **{f['properties']['woonfunctie_vbo']}** | {f['properties']['footprint_area_m2']:,.1f} | {f['properties']['bouwjaar']} | {f['properties']['grup']} |" for i, f in enumerate(top, 1))}

**Ciktilar:**
- `aoi/qa/a_residential_uncertain.geojson` (EPSG:28992, `lat`/`lon`
  oznitelik olarak da var; `gozlem` sutunu bos birakildi)
- `reports/a_residential_uncertain.csv`

## Ne yapilmadi

Bu rapor **karar vermez**. Gruplarin hicbiri icin dislama/dahil etme
uygulanmamistir; P-012, P-013 ve P-014 acik kararlardir.
""", encoding="utf-8")

    write_meta(out, run_id=run_id,
               parameters={"A_konut_vbo": tot_a[2], "belirsiz_konut_vbo": u_a[2],
                           "belirsiz_konut_bina": len(feats),
                           "A_bina": tot_a[0], "BA_bina": tot_ba[0],
                           "supheli_rebuild_overlap": len(overlap)},
               notes="LAZ okunmadi; detect_post_flight_buildings.py ciktisi kullanildi.")
    logger.info("TAMAM | %s", out.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
