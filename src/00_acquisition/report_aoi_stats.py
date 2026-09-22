"""A ve B alanlarinin bina istatistiklerini olcer ve raporlar.

Asama : 0.2  (Karar D-009)
Cikti : reports/00_stage_0_2_aoi.md

ESIK YOKTUR. Karar D-009: A resmi konut buurt'larindan turedigi icin bu
metrikler kabul kriteri degil, alanin TANIMLAYICI OLCUMLERIDIR. Hicbiri icin
PASS/FAIL beyan edilmez. Olculen bina sayisi AGENTS.md Bolum 3'un ~400-700
tahmininin disinda cikarsa bu bir BASARISIZLIK DEGILDIR; tahmin ile gercegin
farki olarak raporlanir.

Metrik tanimlari Karar D-008'den gelir (payda ve status filtresi), config'ten
okunur, koda gomulmez.

ROL ATAMASI (Karar D-009):
  analysis = centroid A icinde   -> raporlanir, dogrulamaya girer
  context  = centroid B icinde, A disinda -> modelde kalir (golge/CFD girdisi),
             raporlanmaz, dogrulama istatistiklerine girmez

ONKOSUL GUARD: B'nin indirilen veri kapsaminin disina tasip tasmadigi ONCE
kontrol edilir. Tasiyorsa rapor URETILMEZ — eksik veriyle hesaplanan bir istatistik,
hesaplanmamis olmaktan daha kotudur (kenar binalar eksik kalir ve sayim sistematik
olarak dusuk cikar).

Calistirma:
    python src/00_acquisition/report_aoi_stats.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# M-003 / M-012: PROJ dizini, pyproj'u yukleyen laspy/shapely/pyproj'dan ONCE
# sabitlenmeli. Aksi halde pyproj PostgreSQL'in PROJ dizinine kilitlenir ve her
# calistirmada "unable to set PROJ database path" uyarisi basar.
import src.common  # noqa: E402,F401

from shapely.geometry import box, shape
from shapely.ops import unary_union

from src.common.config import load_acceptance_criteria, resolve, expected_crs
from src.common.logging_setup import log_rowcount, setup_logging
from src.common.meta import write_meta

M2_PER_HA = 10_000.0


def _stats(panden, vbos_by_pand, status_cfg, logger, label):
    """Bir bina kumesinin tanimlayici istatistiklerini hesaplar.

    Girdi : panden        — (feature, ) listesi, status filtresi UYGULANMIS
            vbos_by_pand  — {pandidentificatie: [vbo, ...]}
            status_cfg    — config status_filter blogu
    Cikti : dict — olculen metrikler
    Birim : sayimlar adet, oranlar pct
    """
    pand_ids = {f["properties"]["identificatie"] for f in panden}
    vbos = [v for pid in pand_ids for v in vbos_by_pand.get(pid, [])]

    with_dwellings = sum(
        1 for f in panden if (f["properties"].get("aantal_verblijfsobjecten") or 0) > 0
    )
    # D-008: TAM ESLESME — "woonfunctie,winkelfunctie" konut sayilmaz
    woon = sum(1 for v in vbos if v["properties"].get("gebruiksdoel") == "woonfunctie")
    years = [int(v["properties"]["bouwjaar"]) for v in vbos if v["properties"].get("bouwjaar")]
    cohort = sum(1 for y in years if 1960 <= y <= 1975)

    stats = {
        "pand_count": len(panden),
        "panden_with_dwellings": with_dwellings,
        "panden_without_dwellings": len(panden) - with_dwellings,
        "verblijfsobjecten": len(vbos),
        "woonfunctie_ratio_pct": round(100 * woon / len(vbos), 1) if vbos else None,
        "bouwjaar_1960_1975_ratio_pct": round(100 * cohort / len(years), 1) if years else None,
        "mean_bouwjaar": round(sum(years) / len(years), 1) if years else None,
    }
    logger.info("%s | %s", label, stats)
    return stats


def main() -> int:
    logger, run_id, _ = setup_logging("report_aoi_stats")
    target_crs = expected_crs("planimetric")
    criteria = load_acceptance_criteria()
    status_cfg = criteria["stage_0_2"]["status_filter"]
    aoi_cfg = criteria["aoi_definition"]

    aoi_dir = resolve("root.aoi")
    raw = resolve("data.raw")
    area_a = shape(json.loads((aoi_dir / "area_A_analysis.geojson").read_text(encoding="utf-8"))
                   ["features"][0]["geometry"])
    area_b = shape(json.loads((aoi_dir / "area_B_context.geojson").read_text(encoding="utf-8"))
                   ["features"][0]["geometry"])

    pand_path = raw / "bag" / "bag_pand.geojson"
    vbo_path = raw / "bag" / "bag_verblijfsobject.geojson"
    pand_raw = json.loads(pand_path.read_text(encoding="utf-8"))["features"]
    vbo_raw = json.loads(vbo_path.read_text(encoding="utf-8"))["features"]

    # ---------- ONKOSUL: indirilen kapsam B'yi tamamen iceriyor mu? ----------
    meta = json.loads((pand_path.parent / "bag_pand.geojson.meta.json").read_text(encoding="utf-8"))
    dminx, dminy, dmaxx, dmaxy = meta["parameters"]["bbox_epsg28992"]
    download_box = box(dminx, dminy, dmaxx, dmaxy)
    bminx, bminy, bmaxx, bmaxy = area_b.bounds

    logger.info("Indirme kapsami | x %.1f..%.1f y %.1f..%.1f", dminx, dmaxx, dminy, dmaxy)
    logger.info("B siniri        | x %.1f..%.1f y %.1f..%.1f", bminx, bmaxx, bminy, bmaxy)

    if not download_box.contains(area_b):
        outside_ha = area_b.difference(download_box).area / M2_PER_HA
        logger.error(
            "KAPSAMA YETERSIZ: B'nin %.2f ha'i indirilen bbox disinda. "
            "Rapor URETILMEDI. download_bag.py'yi genisletilmis bbox ile yeniden calistirin.",
            outside_ha,
        )
        return 1
    margin = min(bminx - dminx, dmaxx - bmaxx, bminy - dminy, dmaxy - bmaxy)
    logger.info(
        "Kapsama DOGRULANDI | B tamamen indirme bbox'i icinde | en dar kenar payi %.1f m", margin
    )

    # ---------- status filtresi ----------
    pand = [f for f in pand_raw if f["properties"].get("status") in status_cfg["pand_include"]]
    vbo = [f for f in vbo_raw if f["properties"].get("status") in status_cfg["vbo_include"]]
    log_rowcount(logger, "status filtresi (pand)", len(pand_raw), len(pand))
    log_rowcount(logger, "status filtresi (vbo)", len(vbo_raw), len(vbo))
    excluded_counts = {
        "pand": len(pand_raw) - len(pand),
        "verblijfsobject": len(vbo_raw) - len(vbo),
    }

    vbos_by_pand: dict[str, list] = {}
    for v in vbo:
        vbos_by_pand.setdefault(v["properties"].get("pandidentificatie"), []).append(v)

    # ---------- rol atamasi ----------
    in_a, in_context, outside = [], [], []
    for f in pand:
        centroid = shape(f["geometry"]).centroid
        if area_a.contains(centroid):
            in_a.append(f)
        elif area_b.contains(centroid):
            in_context.append(f)
        else:
            outside.append(f)
    logger.info(
        "Rol atamasi | analysis=%d | context=%d | B disinda=%d (indirme tamponu fazlasi)",
        len(in_a), len(in_context), len(outside),
    )

    stats_a = _stats(in_a, vbos_by_pand, status_cfg, logger, "A (analysis)")
    stats_ctx = _stats(in_context, vbos_by_pand, status_cfg, logger, "context (B \\ A)")
    stats_b = _stats(in_a + in_context, vbos_by_pand, status_cfg, logger, "B (toplam)")

    # ---------- sanayi buurt'larinin B'deki payi ----------
    buurten = json.loads((raw / "cbs" / "voorhof_buurten.geojson").read_text(encoding="utf-8"))
    excluded_codes = {b["code"] for b in aoi_cfg["area_a"]["excluded_buurten"]}
    industry = unary_union([
        shape(f["geometry"]) for f in buurten["features"]
        if f["properties"]["buurtcode"] in excluded_codes
    ])
    ind_pand = [f for f in in_context if industry.contains(shape(f["geometry"]).centroid)]
    ind_stats = _stats(ind_pand, vbos_by_pand, status_cfg, logger, "sanayi buurt'lari (B icinde)")
    ind_ha = industry.intersection(area_b).area / M2_PER_HA

    # ---------- rapor ----------
    report = resolve("reports.dir") / "00_stage_0_2_aoi.md"
    rows = [
        ("Alan (ha, geometrik)", f"{area_a.area/M2_PER_HA:.2f}",
         f"{(area_b.area-area_a.area)/M2_PER_HA:.2f}", f"{area_b.area/M2_PER_HA:.2f}"),
        ("Pand sayisi", stats_a["pand_count"], stats_ctx["pand_count"], stats_b["pand_count"]),
        ("Konut birimi iceren pand", stats_a["panden_with_dwellings"],
         stats_ctx["panden_with_dwellings"], stats_b["panden_with_dwellings"]),
        ("Konut birimi icermeyen pand", stats_a["panden_without_dwellings"],
         stats_ctx["panden_without_dwellings"], stats_b["panden_without_dwellings"]),
        ("Verblijfsobject", stats_a["verblijfsobjecten"],
         stats_ctx["verblijfsobjecten"], stats_b["verblijfsobjecten"]),
        ("woonfunctie orani (%)", stats_a["woonfunctie_ratio_pct"],
         stats_ctx["woonfunctie_ratio_pct"], stats_b["woonfunctie_ratio_pct"]),
        ("bouwjaar 1960-1975 (%)", stats_a["bouwjaar_1960_1975_ratio_pct"],
         stats_ctx["bouwjaar_1960_1975_ratio_pct"], stats_b["bouwjaar_1960_1975_ratio_pct"]),
        ("Ortalama bouwjaar", stats_a["mean_bouwjaar"],
         stats_ctx["mean_bouwjaar"], stats_b["mean_bouwjaar"]),
    ]
    table = "\n".join(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} |" for r in rows)

    codes = aoi_cfg["area_a"].get("included_buurtcodes") or sorted(
        f["properties"]["buurtcode"] for f in buurten["features"]
        if f["properties"]["buurtcode"] not in excluded_codes
    )

    report.write_text(f"""# Asama 0.2 — AOI tanimi ve bina istatistikleri

**Karar D-009** · run_id `{run_id}` · CRS `{target_crs}`

> **BU RAPORDA ESIK YOKTUR.** A, resmi CBS konut buurt'larindan turedigi icin
> asagidaki sayilar kabul kriteri degil, alanin tanimlayici olcumleridir.
> Hicbiri icin PASS/FAIL beyan edilmez (Karar D-009).

## Calisma alani

Calisma alani = **Voorhof'un (WK050324) {len(codes)} resmi konut buurt'u**.
Iki sanayi buurt'u A'nin raporlama kapsamindan dislanmistir.

**Dahil edilen buurt kodlari:** {', '.join(codes)}

**Dislanan:** {', '.join(sorted(excluded_codes))} (Bedrijventerrein Voorhof,
Bedrijventerrein Vulcanusweg)

**Dislama sadece RAPORLAMA kapsami icindir.** Bu binalar B icinde kalir, LOD2
rekonstruksiyonuna girer, 3B modelde yer alir ve golge/CFD hesaplarina girdi olur.

## Olculen degerler

| Metrik | A (analysis) | context (B \\ A) | B (toplam) |
|---|---|---|---|
{table}

## Rol atamasi (Asama 2'de her binaya yazilacak)

| Rol | Pand | Anlami |
|---|---|---|
| `analysis` | {len(in_a)} | Centroid A icinde. Raporlanir, dogrulamaya girer. |
| `context` | {len(in_context)} | Centroid B icinde A disinda. Modelde kalir, raporlanmaz. |

Indirme tamponu fazlasi (B disinda kalan, kullanilmayan): {len(outside)} pand.

## Sanayi buurt'larinin B'deki payi

| | |
|---|---|
| Alan (B icinde) | {ind_ha:.2f} ha |
| Pand | {ind_stats['pand_count']} |
| Konut birimi iceren | {ind_stats['panden_with_dwellings']} |
| Verblijfsobject | {ind_stats['verblijfsobjecten']} |
| woonfunctie orani | {ind_stats['woonfunctie_ratio_pct']}% |

Bu binalar `context` rolundedir: catı gunes potansiyelleri **`indicative`**
etiketiyle hesaplanip ikizde gosterilir; enerji tuketimi alani
**"modellenmedi — endustriyel surec yuku acik veriyle bilinemez"** olarak
isaretlenir, bos birakilmaz.

## Status filtresi etkisi (Bolum 12.8 — sessiz atlama yasak)

| Katman | Dislanan kayit |
|---|---|
| pand | {excluded_counts['pand']} |
| verblijfsobject | {excluded_counts['verblijfsobject']} |

Dahil/haric deger listeleri `config/acceptance_criteria.yml` ->
`stage_0_2.status_filter` altinda; degerler indirilen veriden dogrulanmistir (M-005).

## AGENTS.md Bolum 3 tahmini ile fark

Bolum 3, A icin **~600 x 600 m ve ~400-700 bina** ongoruyordu. Olculen:
**{area_a.area/M2_PER_HA:.0f} ha ve {stats_a['pand_count']} pand**
({stats_a['pand_count']/550:.1f} kat).

**Bu bir basarisizlik degildir** — Bolum 3'un tahmini varsayimsaldi; A artik
resmi sinirdan turiyor. Fark, Bolum 3'un guncellenmesini gerektirir ve Asama 3-4
hesap yukunu dogrudan etkiler (bkz. P-001).

## Kapsama dogrulamasi

B tamamen indirilen bbox icinde; en dar kenar payi **{margin:.1f} m**.
Kapsama yetersiz olsaydi bu rapor uretilmezdi.
""", encoding="utf-8")

    write_meta(
        report, run_id=run_id, inputs=[pand_path, vbo_path],
        parameters={
            "area_a_ha": round(area_a.area / M2_PER_HA, 2),
            "area_b_ha": round(area_b.area / M2_PER_HA, 2),
            "stats_a": stats_a, "stats_context": stats_ctx,
            "industry_in_b_ha": round(ind_ha, 2),
            "excluded_by_status": excluded_counts,
        },
        notes="Esik uygulanmadi (D-009). Metrik tanimlari D-008.",
    )
    logger.info("TAMAM | rapor: %s", report.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
