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
    # Ayni ayakizi icinde YALNIZCA sinif 6 (bina) noktalari. Gerekce:
    # roof_density TUM siniflari sayar, yani catiyi orten AGAC noktalari da
    # "cati noktasi" gibi gorunur ve yogunluk tam da rekonstruksiyonun
    # bozulacagi binalarda IYI cikar (kullanici talimati 2026-09-21).
    building_points_cls6 = np.zeros(len(geoms), dtype=np.int64)
    # Ayakizi icindeki ZEMIN (sinif 2) noktalari. Yuksek zemin orani, o
    # ayakizinde UCUS ANINDA BINA OLMADIGININ dogrudan gostergesidir: lazer
    # yere ulasmissa ustunde cati yoktur. 2026-09-21 incelemesinde iki buyuk
    # yapinin bu yolla aciklanmasi uzerine eklendi (bkz. reports/
    # 00_stage_0_3_zero_ratio_investigation.md).
    building_points_cls2 = np.zeros(len(geoms), dtype=np.int64)
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
                        # hit[0] = pts dizisindeki indeks, hit[1] = geoms indeksi.
                        # Ayni eslesmeleri sinif 6 maskesiyle yeniden sayiyoruz;
                        # ikinci bir mekansal sorgu YOK, sadece filtre - yani
                        # iki sayim tanimi geregi AYNI nokta kumesi uzerinde.
                        cls_near = cls[near]
                        is_b6 = cls_near[hit[0]] == 6
                        if is_b6.any():
                            np.add.at(building_points_cls6, hit[1][is_b6], 1)
                        is_g = cls_near[hit[0]] == 2
                        if is_g.any():
                            np.add.at(building_points_cls2, hit[1][is_g], 1)

            total_points += file_points
            logger.info("%s | %d nokta B bbox icinde", path.name, file_points)

    logger.info("Toplam islenen nokta (B bbox): %d", total_points)
    return _report(logger, run_id, gate, counts, building_counts, cell,
                   bminx, bminy, area_b, panden, geoms, building_points,
                   building_points_cls6, building_points_cls2,
                   class_counter, total_points, hard, expect)


def _write_visual_check(logger, panden, geoms, areas, is_zero, big_zero,
                        building_points, cls6_ratio, cls2_ratio) -> None:
    """Sifir grubunu disa aktarir ve gorsel dogrulama ornegini secer.

    AGENTS.md Bolum 12.13 / MISTAKES.md M-011: bu yapilarin NE OLDUGU bir
    CIKARIMDIR ve P-012 kararini etkiler. Karardan once bagimsiz yoldan
    dogrulanmasi gerekir. Orneklem SABIT SEED ile secilir (config'ten okunur)
    ki kullanici ayni listeyi yeniden uretebilsin.
    """
    import random

    cfg = load_acceptance_criteria()["input_gate_ahn"]["visual_check"]
    seed = int(cfg["seed"])
    idx_zero = [int(i) for i in np.where(is_zero)[0]]

    # --- GeoJSON: 67 binanin tamami ---
    feats = []
    for i in idx_zero:
        pr = panden[i]["properties"]
        feats.append({
            "type": "Feature",
            "geometry": panden[i]["geometry"],
            "properties": {
                "bag_id": pr["identificatie"],
                "footprint_area_m2": round(float(areas[i]), 2),
                "has_verblijfsobject": (pr.get("aantal_verblijfsobjecten") or 0) > 0,
                "aantal_verblijfsobjecten": pr.get("aantal_verblijfsobjecten"),
                "gebruiksdoel": pr.get("gebruiksdoel") or "",
                "bouwjaar": pr.get("bouwjaar"),
                "status": pr.get("status"),
                "point_count": int(building_points[i]),
                "building_class_ratio": round(float(cls6_ratio[i]), 4),
                "ground_class_ratio": round(float(cls2_ratio[i]), 4),
                "alt_grup": "B_buyuk" if big_zero[i] else "A_kucuk",
            },
        })
    gj_path = resolve("root.aoi") / "qa" / "zero_class6_buildings.geojson"
    gj_path.parent.mkdir(parents=True, exist_ok=True)
    gj_path.write_text(json.dumps({
        "type": "FeatureCollection",
        "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:EPSG::28992"}},
        "features": feats,
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    logger.info("Gorsel dogrulama | GeoJSON: %d bina -> %s", len(feats), gj_path.name)

    # --- Orneklem: 2 buyuk (her zaman) + n_small rastgele kucuk ---
    always = [str(v) for v in cfg["big_always_include"]]
    by_id = {panden[i]["properties"]["identificatie"]: i for i in idx_zero}
    chosen = [by_id[b] for b in always if b in by_id]
    missing = [b for b in always if b not in by_id]
    if missing:
        # Bolum 12.8: sessizce atlama yok.
        raise RuntimeError(
            f"visual_check.big_always_include'daki su id'ler sifir grubunda "
            f"bulunamadi: {missing}. Config ile veri uyusmuyor."
        )

    small_pool = sorted(i for i in idx_zero if not big_zero[i])
    rng = random.Random(seed)          # SABIT seed - tekrarlanabilir
    n_small = min(int(cfg["n_small"]), len(small_pool))
    chosen += rng.sample(small_pool, n_small)

    # --- AMACLI (purposive) ornekler ---
    # Rastgele cekilisten SONRA eklenir ve havuzda olmadiklari icin seed'i
    # BOZMAZLAR (havuz = sifir grubundaki kucuk yapilar). Ayri etiketlenir.
    all_ids = {f["properties"]["identificatie"]: j for j, f in enumerate(panden)}
    purposive = []
    for item in (cfg.get("purposive_include") or []):
        bid = str(item["bag_id"])
        if bid not in all_ids:
            raise RuntimeError(f"purposive_include: {bid} panden listesinde yok")
        purposive.append((all_ids[bid], item))

    csv_path = resolve("reports.dir") / "visual_check_sample.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["sira", "bag_id", "alt_grup", "footprint_area_m2",
                    "has_verblijfsobject", "gebruiksdoel", "bouwjaar", "status",
                    "point_count", "building_class_ratio", "ground_class_ratio",
                    "merkez_x_rd", "merkez_y_rd",
                    "CIKARIM", "GOZLEM_kullanici", "NOT_kullanici"])
        seq = [(i, None) for i in chosen] + purposive
        for n, (i, item) in enumerate(seq, 1):
            pr = panden[i]["properties"]
            cen = geoms[i].centroid
            if item is not None:
                grp = item.get("label", "AMACLI")
                inference = " ".join(str(item["reason"]).split())[:160]
            else:
                grp = "B_buyuk" if big_zero[i] else "A_kucuk"
                inference = ("ucus sonrasi yapildi (bina yoktu)" if big_zero[i]
                             else "depo/kulube (berging)")
            w.writerow([n, pr["identificatie"], grp,
                        f"{areas[i]:.2f}",
                        "true" if (pr.get("aantal_verblijfsobjecten") or 0) > 0 else "false",
                        pr.get("gebruiksdoel") or "", pr.get("bouwjaar") or "",
                        pr.get("status") or "", int(building_points[i]),
                        f"{cls6_ratio[i]:.4f}", f"{cls2_ratio[i]:.4f}",
                        f"{cen.x:.1f}", f"{cen.y:.1f}",
                        inference, "", ""])
    logger.info("Gorsel dogrulama | orneklem: %d bina (%d buyuk + %d rastgele "
                "kucuk + %d AMACLI, seed=%d) -> %s",
                len(chosen) + len(purposive), len(always), n_small,
                len(purposive), seed, csv_path.name)
    for i, item in purposive:
        logger.info("  AMACLI | %s | %s",
                    panden[i]["properties"]["identificatie"],
                    " ".join(str(item["question"]).split())[:110])
    logger.info("  ETIKETLER: %s", " / ".join(cfg["labels"]))


def _report(logger, run_id, gate, counts, building_counts, cell, bminx, bminy,
            area_b, panden, geoms, building_points, building_points_cls6,
            building_points_cls2, class_counter, total_points, hard, expect) -> int:
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
    # Sinif 6 orani. point_count = 0 ise oran TANIMSIZDIR (0/0); NaN birakilir
    # ve CSV'de bos yazilir. Yapay 0 yazmak "cati tamamen agac altinda" ile
    # "hic nokta yok" durumlarini ayirt edilemez hale getirirdi (config:
    # per_building_class_ratio.undefined_case).
    cls6_ratio = np.divide(
        building_points_cls6.astype(float), building_points.astype(float),
        out=np.full(len(geoms), np.nan), where=building_points > 0,
    )
    cls2_ratio = np.divide(
        building_points_cls2.astype(float), building_points.astype(float),
        out=np.full(len(geoms), np.nan), where=building_points > 0,
    )
    csv_path = resolve("reports.dir") / "ahn_point_density_by_building.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        # DIKKAT: onceki surumde `has_dwellings` adli bir sutun vardi ve
        # aantal_verblijfsobjecten > 0 olmasini "konut" sayiyordu. YANLISTI:
        # bir VBO okul, dukkan veya ofis de olabilir. Sutun
        # `has_verblijfsobject` olarak duzeltildi ve gercek kullanim islevi
        # `gebruiksdoel` olarak ayrica yazilir (MISTAKES.md M-010).
        w.writerow(["bag_id", "footprint_area_m2", "point_count",
                    "roof_density_pts_m2", "below_10",
                    "has_verblijfsobject", "gebruiksdoel", "bouwjaar", "status",
                    "building_class_points", "building_class_ratio",
                    "ground_class_points", "ground_class_ratio"])
        for f, a, n, d, n6, r, n2, r2 in zip(
                panden, areas, building_points, roof_dens,
                building_points_cls6, cls6_ratio, building_points_cls2, cls2_ratio):
            p = f["properties"]
            w.writerow([p["identificatie"], f"{a:.2f}", int(n), f"{d:.2f}",
                        "true" if d < 10 else "false",
                        "true" if (p.get("aantal_verblijfsobjecten") or 0) > 0 else "false",
                        p.get("gebruiksdoel") or "", p.get("bouwjaar") or "",
                        p.get("status") or "",
                        int(n6), "" if np.isnan(r) else f"{r:.4f}",
                        int(n2), "" if np.isnan(r2) else f"{r2:.4f}"])

    b_median = float(np.median(roof_dens))
    b_p10 = float(np.percentile(roof_dens, 10))
    b_below = int((roof_dens < 10).sum())
    logger.info("=== BINA BAZLI CATI YOGUNLUGU (A, %d bina) ===", len(geoms))
    logger.info("  medyan %6.2f | p10 %6.2f | <10 p/m2: %d bina (%%%.1f)",
                b_median, b_p10, b_below, 100 * b_below / max(1, len(geoms)))
    logger.info("  CSV: %s", csv_path.name)

    defined = ~np.isnan(cls6_ratio)
    r_median = float(np.median(cls6_ratio[defined])) if defined.any() else float("nan")
    r_p10 = float(np.percentile(cls6_ratio[defined], 10)) if defined.any() else float("nan")
    undefined_n = int((~defined).sum())
    # Oran dagiliminda esik yok; kac binanin nerede oldugu raporlanir.
    ratio_bands = [(t_, int((cls6_ratio[defined] < t_).sum()))
                   for t_ in (0.001, 0.10, 0.25, 0.50)]

    # BERABERLIK BOZMA: cok sayida bina TAM 0,000'da esit cikiyor (olculdu:
    # 67 bina). Salt orana gore siralarsak "en dusuk 10" listesi bag_id
    # sirasina duser, yani KEYFI olur ve en onemli vakalari gostermez.
    # Bu yuzden esitlik NOKTA SAYISINA gore bozulur: ayni oranda, icinde daha
    # cok nokta olan bina Asama 1 icin daha buyuk risktir.
    order = np.lexsort((
        -building_points,                                   # ikincil: cok nokta once
        np.where(defined, cls6_ratio, np.inf),              # birincil: dusuk oran
    ))
    lowest = [int(i) for i in order if defined[i]][:10]
    n_zero = int((cls6_ratio[defined] < 0.001).sum())

    # Sifir grubunun PROFILI. Amac: "dusuk oran = agac ortusu" varsayimini
    # sinamak. Eger dogruysa sifir grubu normal konutlardan olusmali; degilse
    # baska bir mekanizma is basinda demektir (olculdu: oyle cikti, bkz. D-016).
    is_zero = defined & (cls6_ratio < 0.001)
    has_vbo = np.array(
        [(f["properties"].get("aantal_verblijfsobjecten") or 0) > 0 for f in panden])
    bouwjaar = np.array(
        [int(f["properties"].get("bouwjaar") or 0) for f in panden])

    def _profile(mask):
        return (float(np.median(areas[mask])),
                int((areas[mask] < 50).sum()), int(mask.sum()),
                100.0 * has_vbo[mask].mean(),
                int(np.median(bouwjaar[mask])))

    # Alt grup ayrimi: 100 m2 esigi bir KABUL KRITERI DEGILDIR, yalnizca
    # raporlama icin buyuk/kucuk ayrimidir. Verideki bosluk buradadir:
    # sifir grubunda 28,5 m2 ile 109,0 m2 arasinda hic bina yoktur.
    big_zero = is_zero & (areas >= 100)
    small_zero = is_zero & (areas < 100)
    n_big_zero, n_small_zero = int(big_zero.sum()), int(small_zero.sum())
    big_zero_rows = "\n".join(
        ["| bag_id | ayakizi m2 | bouwjaar | status | gebruiksdoel |",
         "|---|---|---|---|---|"] +
        [f"| `{panden[i]['properties']['identificatie']}` | {areas[i]:.1f} | "
         f"{panden[i]['properties'].get('bouwjaar')} | "
         f"{panden[i]['properties'].get('status')} | "
         f"{panden[i]['properties'].get('gebruiksdoel') or '(islev yok)'} |"
         for i in np.argsort(-areas * big_zero)[:n_big_zero]]
    )
    # ETKI-AGIRLIKLI OZET (Bolum 14.6, M-010). Sayica ozet yaniltir:
    # 67 binanin 64'u kucuktur ama toplam alanin ~%80'i 2 binadadir.
    zero_area_total = float(areas[is_zero].sum())
    pct_small_n = 100.0 * n_small_zero / max(1, n_zero)
    pct_big_n = 100.0 * n_big_zero / max(1, n_zero)
    small_area = float(areas[small_zero].sum())
    big_area = float(areas[big_zero].sum())
    zero_order = np.argsort(np.where(is_zero, -areas, np.inf))
    top5 = [int(i) for i in zero_order[:5] if is_zero[i]]
    area_share_top2 = 100 * float(areas[top5[:2]].sum()) / zero_area_total
    area_share_top5 = 100 * float(areas[top5].sum()) / zero_area_total
    big_area_share = 100 * float(areas[big_zero].sum()) / zero_area_total
    small_area_share = 100 * float(areas[small_zero].sum()) / zero_area_total
    logger.info("  ALT GRUP | buyuk (>=100 m2): %d (alanin %%%.1f'i) | "
                "kucuk (<100 m2): %d (alanin %%%.1f'i)",
                n_big_zero, big_area_share, n_small_zero, small_area_share)
    logger.info("  ETKI | sifir grubu toplam alan %.0f m2 | en buyuk 2 = %%%.1f | "
                "en buyuk 5 = %%%.1f", zero_area_total, area_share_top2, area_share_top5)

    top5_rows = "\n".join(
        f"| {r_+1} | `{panden[i]['properties']['identificatie']}` | {areas[i]:,.1f} | "
        f"%{100*areas[i]/zero_area_total:.1f} | "
        f"{panden[i]['properties'].get('gebruiksdoel') or '**(islev kaydi yok)**'} | "
        f"{panden[i]['properties'].get('bouwjaar')} | {cls2_ratio[i]:.3f} |"
        for r_, i in enumerate(top5)
    )

    z_area, z_small, z_n, z_vbo, z_year = _profile(is_zero)
    o_area, o_small, o_n, o_vbo, o_year = _profile(defined & ~is_zero)
    small_all = areas < 50
    small_ratio_med = float(np.median(cls6_ratio[defined & small_all]))
    large_ratio_med = float(np.median(cls6_ratio[defined & ~small_all]))
    logger.info("  SIFIR grubu profili | n=%d | ayakizi medyan %.1f m2 | "
                "<50 m2: %d | konut %%%.1f | bouwjaar medyan %d",
                z_n, z_area, z_small, z_vbo, z_year)
    logger.info("  DIGERLERI           | n=%d | ayakizi medyan %.1f m2 | "
                "<50 m2: %d | konut %%%.1f | bouwjaar medyan %d",
                o_n, o_area, o_small, o_vbo, o_year)
    logger.info("  KONTROL | A'daki tum kucuk binalar (<50 m2) oran medyani %.3f, "
                "buyukler %.3f -> kuculuk tek basina sebep DEGIL",
                small_ratio_med, large_ratio_med)
    logger.info("=== SINIF 6 ORANI (esik yok, raporlanir) ===")
    logger.info("  medyan %.3f | p10 %.3f | tanimsiz (0 nokta): %d bina",
                r_median, r_p10, undefined_n)
    for t_, n_ in ratio_bands:
        logger.info("  oran < %.3f : %4d bina (%%%.1f)",
                    t_, n_, 100 * n_ / max(1, int(defined.sum())))
    for i in lowest:
        logger.info("  dusuk oran | %s | %.3f | %d/%d nokta | %.1f m2",
                    panden[i]["properties"]["identificatie"], cls6_ratio[i],
                    int(building_points_cls6[i]), int(building_points[i]), areas[i])

    band_rows = "\n".join(
        f"| Oran < {t_:.3f} | {n_} bina (%{100*n_/max(1,int(defined.sum())):.1f}) |"
        for t_, n_ in ratio_bands
    )
    lowest_rows = "\n".join(
        f"| `{panden[i]['properties']['identificatie']}` | {areas[i]:.1f} | "
        f"{int(building_points[i]):,} | {int(building_points_cls6[i]):,} | "
        f"**{cls6_ratio[i]:.3f}** | {cls2_ratio[i]:.3f} | "
        # KESME YOK (M-010 tekrari 2026-09-22): kesilen gebruiksdoel metni
        # 260 konutlu bir binayi "bijeenkomst, overige" gosterdi.
        f"{panden[i]['properties'].get('gebruiksdoel') or '(islev yok)'} |"
        for i in lowest
    )

    top = ", ".join(f"{k}:{v}" for k, v in class_counter.most_common(8))
    logger.info("Sinif dagilimi (ilk 8): %s", top)

    _write_visual_check(logger, panden, geoms, areas, is_zero, big_zero,
                        building_points, cls6_ratio, cls2_ratio)

    report = resolve("reports.dir") / "00_stage_0_3_ahn_gate.md"
    report.write_text(f"""# Asama 0.3 — AHN girdi kalite kapisi

**Karar D-015** · AGENTS.md Bolum 12.12 · run_id `{run_id}`

> **VERI DONEMI (D-020).** Bu projede **geometri** AHN5 ucus donemini
> (**2023-02-08 / 2023-02-14**, LAZ `gps_time`'dan olculdu) temsil eder;
> **oznitelikler** BAG anlik goruntusudur (**2026-09**). Arada **3,5 yil**
> vardir. Ucustan sonra yapilmis veya degismis binalarin geometrisi
> uretilemez; bunlar **"geometrisi yok (ucus sonrasi)"** etiketiyle listelenir
> ve modellenmez.

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

### Bina sinifi (kod 6) orani — esik yok, raporlanir

`roof_density_pts_m2` ayakizi icindeki **tum siniflari** sayar. Catiyi orten
agac noktalari (sinif 1) da "cati noktasi" olarak sayilir; bu yuzden yogunluk
**tam da rekonstruksiyonun bozulacagi binalarda iyi gorunur**. Asagidaki oran
o kor noktayi kapatir.

`building_class_ratio` = ayakizi icindeki sinif 6 noktasi / ayakizi icindeki
tum noktalar. Ikisi de ayni `within` sorgusundan gelir.

| Metrik | Deger |
|---|---|
| Medyan `building_class_ratio` | {r_median:.3f} |
| 10. persentil | {r_p10:.3f} |
| Tanimsiz (ayakizi icinde 0 nokta) | {undefined_n} bina |
{band_rows}

**En dusuk oranli 10 bina.** DIKKAT: **{n_zero} bina tam 0,000'da esittir**, yani
"en dusuk 10" tek basina anlamli bir siralama vermez. Esitlik **nokta sayisina**
gore bozulmustur: ayni oranda icinde daha cok nokta bulunan bina Asama 1 icin
daha buyuk risktir. Tam liste CSV'dedir.

| bag_id | ayakizi m2 | toplam nokta | sinif 6 nokta | sinif 6 orani | zemin orani | gebruiksdoel |
|---|---|---|---|---|---|---|
{lowest_rows}

Dusuk oran = cati muhtemelen **bitki ortusuyle kapali** veya **siniflandirma
eksik**. Tek basina hata degildir. Asama 1'de `failed_buildings.csv` ile
karsilastirilacak **ucuncu eksen** budur: yogunluk yeterli ama sinif 6 orani
dusukse, basarisizligin nedeni "az nokta" degil **"yanlis nokta"**dir.

#### Beklenmeyen bulgu: sifir grubu agac ortusu DEGIL

Oran tam 0 cikan {n_zero} binanin profili, "cati agac altinda kalmis konut"
beklentisine **uymuyor**:

| | Sifir grubu (n={z_n}) | Digerleri (n={o_n}) |
|---|---|---|
| Ayakizi medyani | **{z_area:.1f} m2** | {o_area:.1f} m2 |
| < 50 m2 olan | {z_small}/{z_n} | {o_small}/{o_n} |
| Konut VBO'lu | **%{z_vbo:.1f}** | %{o_vbo:.1f} |
| Bouwjaar medyani | **{z_year}** | {o_year} |

Bunlar **kucuk, konut olmayan, sonradan yapilmis yardimci yapilardir**
(berging, bisiklet deposu, bahce evi).

**Kucukluk tek basina sebep DEGILDIR:** A'daki tum kucuk binalarin (<50 m2)
sinif 6 orani medyani **{small_ratio_med:.3f}**, buyuklerinki
**{large_ratio_med:.3f}** — neredeyse esit. Sorun kucukluk degil, bu belirli
alt gruptur.

#### Sifir grubu: SAYIYA gore ve ETKIYE gore — iki farkli tablo

> **Bolum 14.6 / M-010 geregi.** Bu grup once yalnizca medyanla ozetlenmis ve
> "kucuk, konut disi yardimci yapilar" diye genellenmisti. Medyan **cogunlugu**
> anlatir, **etkisi buyuk azinligi gizler**. Asagida ayni grup iki ayri
> agirlikla verilir.

| Alt grup | Sayica | Alanca |
|---|---|---|
| **A — kucuk yapilar** (< 100 m2) | **{n_small_zero}** bina (%{pct_small_n:.1f}) | {small_area:,.0f} m2 (**%{small_area_share:.1f}**) |
| **B — buyuk yapilar** (>= 100 m2) | **{n_big_zero}** bina (%{pct_big_n:.1f}) | {big_area:,.0f} m2 (**%{big_area_share:.1f}**) |
| **Toplam** | {n_zero} bina | {zero_area_total:,.0f} m2 |

**Tablo agirliga gore tersine donuyor:** sayica grubun %{pct_small_n:.1f}'i kucuk
yapilardir, ama toplam alanin **%{area_share_top2:.1f}'i yalnizca 2 binadadir**.

**Etkiye gore en buyuk 5 uye (tek tek):**

| # | bag_id | ayakizi m2 | alan payi | gebruiksdoel | bouwjaar | zemin orani |
|---|---|---|---|---|---|---|
{top5_rows}

Ilk ikisi **okuldur** (`onderwijsfunctie`) ve tek tek teshis edilmistir:
**`reports/00_stage_0_3_zero_ratio_investigation.md`**.

#### Alt grup B — teshis edildi, mekanizma tek degil

- **2 yapi (1.665,0 ve 996,5 m2, ikisi de OKUL):** ayakizinde AHN5 ucusu
  (**2023-02-08/14**) sirasinda **hicbir bina yoktu**. Kanit **olcumdur**,
  cikarim degil: zemin (sinif 2) noktasi orani %62,1 ve %98,9; >8 m
  noktalarin **%99,8 ve %100'u cok donuslu** (kontrol binasinda %2,4 — bitki
  ortusu imzasi); ikisi de **3DBAG'de yok**. Sebep girdi kalitesi degil,
  **zamansal uyusmazliktir** (D-020).
- **1 yapi (109,0 m2, bouwjaar 2002):** 8 m ustu hic noktasi yok, cok donuslu
  orani %3,0 — orada alcak, kati bir yapi var ve AHN onu **maaiveld/overig**
  saymis. Alt grup A ile **ayni mekanizmanin** buyuk ornegi.

**Karar (D-019, kullanici onayi):** bu **3 yapi Asama 1'den dislanir** ve
sinirlama olarak raporlanir. Karar dogrudan olcume dayandigi icin Bolum 12.13
kapsaminda **degildir**; gorsel dogrulamayi beklemez.

#### Alt grup A — aciklama bir CIKARIMDIR, dogrulanmayi bekliyor

> ### CIKARIM (Bolum 12.13 — dogrulanmadan karara baglanmaz)
>
> 64 kucuk yapinin **berging / bisiklet deposu / bahce evi** oldugu
> dusunulmektedir. Dayanak: ayakizi medyani {z_area:.1f} m2, `gebruiksdoel`
> **{n_small_zero}/{n_small_zero}'unde tamamen bos**, woonfunctie **sifir**.
>
> **Bu bir OLCUM DEGILDIR.** BAG'de `gebruiksdoel` bos olmasi, yapinin depo
> oldugunu degil, **bir kullanim islevi kaydedilmedigini** soyler. Ikisi ayni
> sey degildir (MISTAKES.md **M-011**).
>
> **Dogrulama:** sabit seed ile secilmis 12 binalik gorsel orneklem —
> `reports/visual_check_sample.csv`, `aoi/qa/zero_class6_buildings.geojson`,
> sonuclar `docs/visual_check_zero_class6.md`.
> **P-012 bu dogrulama bitmeden karara baglanmayacaktir.**

Destekleyici belge (kanit degil): AHN4 sartnamesi Bolum 9.2, BAG'de olmayan
"tuinhuisjes zonder fundering" gibi nesnelerin **"overig" (=1)**
siniflandirilmasini emreder. Ancak bu yapilar BAG'de **vardir**, yani kural
birebir uymuyor; AHN5'in siniflandirici davranisi belgelenmemistir (bkz.
`docs/ahn_class_codes.md`).

**Asama 1'e etkisi:** bu {n_zero} bina basarisiz olursa sebep **ne girdi
yogunlugu ne bizim yontemimizdir** — AHN'in siniflandirma politikasidir.
Bu **ucuncu neden kategorisi** Bolum 12.6'nin "nedeni siniflandir" adimina
eklenmistir. Sinif 1'in rekonstruksiyona alinip alinmayacagi **P-012**'de
acik karardir: bu yapilar sinif 1 dislanirsa **hic nokta gormez**.

**Esik konulmadi** cunku dusuk cati yogunlugu tek basina hata degildir —
kucuk veya egimli catili binalarda dogal olarak az nokta duser.

**Asama 1'de kullanimi:** `reports/failed_buildings.csv` bu listeyle
karsilastirilacak. Basarisiz VE dusuk yogunluklu -> neden muhtemelen **girdi**;
basarisiz AMA yeterli yogunluklu -> neden muhtemelen **yontem**. Bu ayrim
sonradan yapilamaz.

## Olcum tanimindan gelen bilinen yanlilik

Bina bazli sayim, ayakizi poligonunun **icine dusen** noktalari alir
(`within`, kesisim degil). Iki ayri mekanizma bunu asagi cekiyor:

1. **Sinir noktalari elenir.** Elenen bolge **cevreyle**, sayilan bolge
   **alanla** orantilidir; bu yuzden kucuk ayakizlerinde yogunluk sistematik
   olarak biraz dusuk cikar (MISTAKES.md M-007 ikincil bulgu).
2. **Sinif 6 noktalari ayakizinin disina dusebilir.** AHN4 sartnamesi Bolum
   9.2 bunu acikca soyler: "ook al ligt een deel van de punten buiten het vlak
   dat in de BAG als pand ... wordt aangeduid". Yani binaya ait noktalarin bir
   kismini kaciriyoruz, bir kismini da **komsu binaya** yaziyoruz.

Ikisi de veri sorunu DEGILDIR; olcum tanimindan gelir ve Asama 1'de dusuk
degerler yorumlanirken akilda tutulmalidir.

## Sinif dagilimi — ASPRS varsayilmadi, belgeden dogrulandi

```
{top}
```

Kod anlamlari `docs/ahn_class_codes.md`de **belgeden** dogrulanmistir (D-017).
Ozet:

| Kod | Anlam | Kanit |
|---|---|---|
| 1, 2, 6, 9, **26** | Overig, Maaiveld, Bebouwing, Water, **Kunstwerken** | **BELGELENMIS** — AHN4 Besteksvoorwaarden Bolum 9 |
| **14** | hoogspanningsleiding (tel) | **CIKARIM** — AHN belgesinde yok; ASPRS LAS 1.4 + veri kaniti |

**Iki uyari Asama 1 icin kritiktir:**
- **Sinif 6 "cati" degildir** — cepheler, dakkapeller, balkonlar ve gunes
  panelleri de 6'dir (sartname Bolum 9.2).
- **AHN5 icin sinif spesifikasyonu yoktur.** Yorumlar AHN4'ten tasinmistir;
  ahn.nl tanimlarin surumler arasi degistigini kendi dipnotunda soyluyor.
""", encoding="utf-8")

    write_meta(report, run_id=run_id,
               parameters={"median_density": median_d, "p10": p10_d,
                           "zero_cells_pct": zero_pct,
                           "buildings_below_10": b_below,
                           "cls6_ratio_median": r_median,
                           "cls6_ratio_p10": r_p10,
                           "cls6_ratio_undefined": undefined_n,
                           "hard_gate": hard, "expectation": expect,
                           "gate_pass": gate_pass, "expectation_pass": exp_pass},
               notes="Esikler config'ten okundu; olcumden once muhurlendi (D-015).")
    logger.info("TAMAM | rapor: %s", report.name)
    return 0 if gate_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
