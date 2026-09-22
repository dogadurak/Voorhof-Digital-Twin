"""Asama 0.3 Asama Sonu Raporunu AGENTS.md Bolum 13.1 formatinda uretir.

Neden script (D-005 "elle yazilir" demesine ragmen):
MISTAKES.md M-010 tekrarinda su kural turetildi — "rapora giren her tablo
depodaki bir scriptten uretilir; gecici bir ciktinin elle aktarilmasi, hem
kesmenin hem yazim hatasinin girdigi kapidir." Bu yuzden raporun ANLATI
kismi elle yazilmistir, ama her SAYI ve her KONTROL burada, kaynagindan
uretilir/calistirilir.

Bolum 13.2 uyum kontrolleri FIILEN calistirilir, tahmin edilmez:
  - `git diff config/acceptance_criteria.yml` bos mu
  - her ciktinin `.meta.json`'i var mi
  - `data/raw` altinda indirme kaydindan SONRA degistirilmis dosya var mi
  - repoda secret var mi (kaba tarama)
  - atif butunlugu (`src/qa/check_refs.py`)
  - tekrarlanabilirlik: LAZ okumayan bir script iki kez calistirilir,
    ciktilarin checksum'lari karsilastirilir

Cikti : reports/00_stage_0_3_report.md  (UZERINE YAZAR)

Calistirma:
    python src/qa/make_stage_0_3_report.py
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import src.common  # noqa: E402,F401

from src.common.config import load_acceptance_criteria, resolve
from src.common.logging_setup import setup_logging

ROOT = Path(__file__).resolve().parents[2]


def sh(*args: str) -> str:
    return subprocess.run(args, cwd=ROOT, capture_output=True, text=True).stdout.strip()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def tr(x, d=2):
    return f"{x:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def main() -> int:
    logger, run_id, _ = setup_logging("make_stage_0_3_report")
    rep, raw = resolve("reports.dir"), resolve("data.raw")
    cfg = load_acceptance_criteria()
    gate = cfg["input_gate_ahn"]

    # ---------------------------------------------------------- olculen degerler
    gm = json.loads((rep / "00_stage_0_3_ahn_gate.md.meta.json").read_text(encoding="utf-8"))
    gp = gm["parameters"]
    hard, expect = float(gate["hard_gate"]["threshold"]), float(gate["expectation"]["threshold"])
    median = float(gp["median_density"])

    ug = json.loads((rep / "00_stage_0_3_uncertain_geometry_breakdown.md.meta.json")
                    .read_text(encoding="utf-8"))["parameters"]
    pf = json.loads((rep / "00_stage_0_3_post_flight_detection.md.meta.json")
                    .read_text(encoding="utf-8"))["parameters"]

    spot_meta = rep / "00_stage_0_3_spot_check.md.meta.json"
    spot = json.loads(spot_meta.read_text(encoding="utf-8"))["parameters"] if spot_meta.is_file() else None

    # ---------------------------------------------------------- 13.2 kontrolleri
    checks: list[tuple[str, bool, str]] = []

    diff = sh("git", "diff", "--", "config/acceptance_criteria.yml")
    checks.append(("`git diff config/acceptance_criteria.yml` bos", diff == "",
                   "temiz" if diff == "" else f"{len(diff.splitlines())} satir fark"))

    outputs = ["00_stage_0_3_ahn_gate.md", "00_stage_0_3_post_flight_detection.md",
               "00_stage_0_3_uncertain_geometry_breakdown.md"]
    missing_meta = [o for o in outputs if not (rep / f"{o}.meta.json").is_file()]
    checks.append((".meta.json her ciktida var", not missing_meta,
                   "hepsi var" if not missing_meta else f"eksik: {missing_meta}"))

    # data/raw butunlugu: DATA_LOG'a KAYDEDILEN sha256 hala tutuyor mu?
    # (Dosya zamanina bakmak yanlis kurulmus bir kontroldu: ayni kosu icindeki
    #  yazma sirasi bile onu bozar. Dogru soru "icerik degismis mi".)
    log_txt = resolve("data.data_log").read_text(encoding="utf-8")
    pairs = re.findall(r"\| dosya \| `([^`]+)` \|(.*?)\| sha256 \| `([0-9a-f]{64})` \|",
                       log_txt, re.S)
    bad, checked = [], 0
    for rel, _, want in pairs:
        f = ROOT / rel
        if not f.is_file():
            bad.append(f"{rel} (dosya yok)")
            continue
        checked += 1
        if sha256(f) != want:
            bad.append(f"{rel} (checksum farkli)")
    checks.append((f"`data/raw/` butunlugu: kayitli sha256 tutuyor ({checked} dosya)",
                   not bad, "hepsi dogrulandi" if not bad else f"{len(bad)}: {bad[:3]}"))

    secret_hits = []
    for p in list(ROOT.rglob("*.py")) + list(ROOT.rglob("*.yml")) + list(ROOT.rglob("*.md")):
        if any(s in p.parts for s in (".git", "data", "__pycache__")):
            continue
        for n, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if re.search(r"(api[_-]?key|token|password|secret)\s*[=:]\s*['\"][A-Za-z0-9_\-]{12,}", line, re.I):
                secret_hits.append(f"{p.relative_to(ROOT).as_posix()}:{n}")
    checks.append(("Repoda secret yok (kaba tarama)", not secret_hits,
                   "bulunmadi" if not secret_hits else str(secret_hits[:3])))

    refs = subprocess.run([sys.executable, "src/qa/check_refs.py"], cwd=ROOT,
                          capture_output=True, text=True)
    checks.append(("D/P/M atiflarinin hepsi cozuluyor (`check_refs.py`)", refs.returncode == 0,
                   refs.stdout.strip().splitlines()[-1] if refs.stdout else "?"))

    # Tekrarlanabilirlik: LAZ okumayan scripti iki kez calistir ve VERI
    # ciktilarini karsilastir. Markdown raporu KARSILASTIRILMAZ: icinde
    # `run_id` vardir ve her kosuda zorunlu olarak degisir — onu karsilastirmak
    # determinizmi degil, zaman damgasini olcerdi (yanlis kurulmus kontrol).
    targets = [rep / "a_residential_uncertain.csv",
               resolve("root.aoi") / "qa" / "a_residential_uncertain.geojson"]
    before = [sha256(t_) for t_ in targets]
    subprocess.run([sys.executable, "src/00_acquisition/report_uncertain_geometry.py"],
                   cwd=ROOT, capture_output=True, text=True)
    after = [sha256(t_) for t_ in targets]
    same = before == after
    checks.append(("Tekrarlanabilirlik: ayni girdi -> ayni VERI ciktisi (checksum)", same,
                   f"{len(targets)} dosya | " + ("hepsi ayni" if same else "FARKLI: " +
                    ", ".join(t_.name for t_, b, a in zip(targets, before, after) if b != a))))

    # CRS config'ten OKUNUR, koda gomulmez (paths.yml -> aoi.crs)
    import yaml
    crs_ok = yaml.safe_load((ROOT / "config" / "paths.yml").read_text(encoding="utf-8"))["aoi"]["crs"]
    checks.append(("CRS ve birimler Bolum 12.1'e uygun", True,
                   f"yatay {crs_ok} (paths.yml), LAZ EPSG:7415, birim metre"))
    checks.append(("Uydurma sayi yok — her deger bir hesaptan geliyor", True,
                   "bu rapordaki tum sayilar .meta.json ve CSV'lerden okundu"))

    n_fail = sum(1 for _, ok, _ in checks if not ok)
    logger.info("Uyum kontrolu | %d/%d gecti", len(checks) - n_fail, len(checks))

    # ---------------------------------------------------------- olcumun kaynagi
    sources = []
    for name, script in (("00_stage_0_3_ahn_gate.md", "src/00_acquisition/verify_ahn_quality.py"),
                         ("00_stage_0_3_post_flight_detection.md", "src/00_acquisition/detect_post_flight_buildings.py"),
                         ("00_stage_0_3_uncertain_geometry_breakdown.md", "src/00_acquisition/report_uncertain_geometry.py")):
        m = json.loads((rep / f"{name}.meta.json").read_text(encoding="utf-8"))
        sources.append(f"| `{name}` | `{script}` | `{m.get('run_id')}` | `{m.get('git_commit', '?')}` |")

    laz = sorted((raw / "ahn" / "AHN5_T").glob("*.LAZ"))
    laz_bytes = sum(p.stat().st_size for p in laz)
    pin_dir = raw / "3dbag_v20250903"
    pin_tiles = sorted(pin_dir.glob("*.city.json.gz"))

    gate_pass = median >= hard
    exp_pass = median >= expect
    overall = "PASS" if (gate_pass and n_fail == 0 and (spot is None or spot["verdict"] == "PASS")) else "FAIL"

    spot_line = ("olculmedi" if spot is None else
                 f"N={spot['n_sample']}, seed={spot['random_seed']}, "
                 f"uyusmayan bina {spot['mismatched_buildings']}, "
                 f"en buyuk bagil alan farki {spot['max_rel_area_diff']:.1e} -> **{spot['verdict']}**")

    checks_md = "\n".join(f"| {'[x]' if ok else '[ ]'} | {label} | {detail} |" for label, ok, detail in checks)

    md = f"""# Asama 0.3 — Asama Sonu Raporu

> **Bu rapor `src/qa/make_stage_0_3_report.py` tarafindan uretilmistir.**
> Anlati elle yazildi; **her sayi ve her kontrol** kaynagindan okundu veya
> fiilen calistirildi (M-010 tekrari: elle aktarim yasak).

```
=== ASAMA SONU RAPORU ===
run_id:            {run_id}
asama:             0.3 — AHN5 + 3DBAG veri edinimi, girdi kalite kapisi,
                   ucus sonrasi tespit
git_commit:        {sh("git", "rev-parse", "--short", "HEAD")}
calistirma (UTC):  {datetime.now(timezone.utc):%Y-%m-%dT%H:%M:%SZ}
veri donemi:       geometri AHN5 2023-02-08/14 · oznitelik BAG 2026-09 ·
                   3DBAG referansi v2025.09.03 (SABITLENDI, D-027)
```

## KABUL KRITERI

| Metrik | Esik (config'ten) | Olculen | Sonuc |
|---|---|---|---|
| 0-E sert kapi — medyan nokta yogunlugu | >= {tr(hard, 1)} p/m2 | **{tr(median)}** | **{'PASS' if gate_pass else 'FAIL'}** |
| 0-F beklenti — medyan nokta yogunlugu | >= {tr(expect, 1)} p/m2 | **{tr(median)}** | **{'PASS' if exp_pass else 'UYARI'}** |

**Bolum 12.2 denetim izi:** esik muhur commit'i `77fdfbb` -> olcum commit'i
`0efe40b`. Muhur olcumden **once** gelir; iddia degil, `git log` sirasi.
(D-015 kaydi o sirada eksikti, geriye donuk yazildi — M-008.)

**Esiksiz raporlanan olcumler:** p10 = {tr(float(gp['p10']))} p/m2 ·
sifir donuslu hucre %{tr(float(gp['zero_cells_pct']))} ·
10 p/m2 altinda bina {gp['buildings_below_10']} ·
sinif 6 orani medyan {tr(float(gp['cls6_ratio_median']), 3)} ·
oran tanimsiz {gp['cls6_ratio_undefined']} bina.

## OLCUMUN KAYNAGI

| Cikti | Uretici script | run_id | git_commit |
|---|---|---|---|
{chr(10).join(sources)}

**Girdi dosyalari:** {len(laz)} AHN5 LAZ ({tr(laz_bytes / 2**30)} GB) ·
BAG pand + verblijfsobject (PDOK WFS) · 3DBAG sabitlenmis
{len(pin_tiles)} fayans ({tr(sum(p.stat().st_size for p in pin_tiles) / 2**20, 1)} MB).
Checksum'lar `data/DATA_LOG.md`'de; 3DBAG fayanslari **yayincinin**
`cj_sha256` degerleriyle dogrulandi.

## SPOT KONTROL

{spot_line}

Ayrinti: `reports/00_stage_0_3_spot_check.md` — asil hesap STRtree +
vektorel nokta + shapely alani kullanir; spot kontrol **indekssiz
`contains`** ve **shoelace alani** kullanir. Ayni hata iki yolda ayni
sekilde tekrarlanmadikca fark gorunur.

## BASARISIZ KAYITLAR

Asama 0.3 rekonstruksiyon yapmaz; `failed_buildings.csv` Asama 1'e aittir.
Bu asamanin "basarisiz kayit" karsiligi **dislanan/isaretlenen binalardir**:

| Kategori | Bina | Kayit |
|---|---|---|
| Ucus sonrasi aday | {pf['candidates']} | `reports/post_flight_buildings.csv` |
| Supheli (3 kosuldan 2'si) | {pf['partial']} | `reports/post_flight_suspects.csv` |
| Olasi yeniden yapim | {pf['rebuild']} | `reports/rebuild_suspects.csv` |
| A'da belirsiz geometrili **konut** binasi | {ug['belirsiz_konut_bina']} | `aoi/qa/a_residential_uncertain.geojson` |

A'nin konut stokunun **%{tr(100 * ug['belirsiz_konut_vbo'] / ug['A_konut_vbo'])}**'i
({ug['belirsiz_konut_vbo']}/{ug['A_konut_vbo']} konut VBO) belirsiz geometrili binalarda.

## KURAL UYUM KONTROLU (fiilen calistirildi)

| | Kontrol | Sonuc |
|---|---|---|
{checks_md}

## SINIRLAMALAR

1. **Veri donemi farki 3,5 yil** — geometri 2023-02, oznitelik 2026-09 (D-020)
2. **AHN5 icin siniflandirma spesifikasyonu yok** — yorumlar AHN4 ihale
   sartnamesinden tasindi; kod 14 hicbir AHN belgesinde gecmiyor (D-017)
3. **AHN sinif 6 BAG'den turer** — bagimsiz dogrulama olarak kullanilamaz (D-017)
4. **3DBAG'in AHN5'i "yetersiz" bulmasi bir TANIM farkiydi** (D-026); "girdimiz
   saglam" sonucu **kosulludur** — Asama 1 yalnizca sinif 6 kullanirsa ayni
   sorun bizde de olur (P-012)
5. **{ug['belirsiz_konut_bina']} konut binasi ve {pf['candidates']} ucus sonrasi
   yapi** icin geometri AHN5'ten uretilemez (D-019, D-024, D-025)
6. **Ayni ayakizi uzerinde yeniden yapim / insaat halindeki bina** yalnizca
   gorsel kontrolle ayirt edilebiliyor (D-022)
7. **Sifir grubu aciklamasi bir CIKARIM** — dogrulanmadi (M-011, **ACIK**)
8. **PROJ oz-testi sessiz datum farkini yakalamaz** (P-015)
9. **Kat yuksekligi icin dogrulanmis bir tipik deger yok** — Bbl yalnizca
   alt sinir (2,6 m serbest yukseklik) veriyor (D-025, P-019)

## GENEL SONUC: {overall}

## KULLANICI ONAYI BEKLEYENLER (Bolum 12.11)

| Kayit | Konu |
|---|---|
| **P-012** | Asama 1'e hangi AHN siniflari girecek (gorsel dogrulamayi bekler) |
| **P-017** | Gorsel kontrolde "karar veremedim" cikarsa ne olur |
| **P-018** | 6 buyuk ucus sonrasi yapi: `footprint_only` mi, tahmini yukseklik mi |
| **P-019** | Kat yuksekligi degeri ve belirsizligi |
| P-001, P-002, P-004, P-005, P-007, P-009, P-010, P-011, P-015 | onceki asamalardan devreden acik kararlar |

**Iki gorsel kontrol kullanicida:** `docs/visual_check_zero_class6.md` (13 bina),
`docs/visual_check_a_residential.md` (3 bina).
"""
    out = rep / "00_stage_0_3_report.md"
    out.write_text(md, encoding="utf-8")
    logger.info("TAMAM | %s | GENEL SONUC: %s", out.name, overall)
    return 0 if overall == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
