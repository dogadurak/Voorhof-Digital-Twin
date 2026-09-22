"""docs/field_check_list.md — tek saha kontrol listesi (kullanici doldurur).

Asama : 0.3
Kaynak: dort ayri grup TEK tabloda birlestirilir (kullanici talimati 2026-09-22)
  G1  sifir sinif-6 orani orneklemi          reports/visual_check_sample.csv
  G2  A'daki belirsiz geometrili konut bloklari  reports/a_residential_uncertain.csv
  G3  buyuk (>=100 m2) ucus sonrasi yapilar  reports/post_flight_buildings.csv
  G4  kat yuksekligi kalibrasyonu            reports/storey_height_calibration.csv
                                             + ..._proposal_p020.csv (ONERI)

Ayni bina birden fazla gruba giriyorsa TEK SATIR yazilir ve gruplar birlestirilir
(kullanici ayni binaya iki kez bakmasin).

OLCULEN YUKSEKLIK BU LISTEDE YOKTUR — bilerek. Kat sayarken "36 m" yazan bir
sutun gormek sayimi demirler (anchoring); o zaman sayim bagimsiz bir gozlem
olmaktan cikar ve kalibrasyon kendi girdisini dogrulamis olur (Bolum 12.10).
Yukseklikler reports/building_heights_ahn5.csv icindedir; sayimdan SONRA
yan yana raporlanir (Bolum 12.13-3).

UZERINE YAZMA KORUMASI: dosyada doldurulmus bir hucre varsa script DURUR.
Kullanicinin saha calismasi bir yeniden calistirmayla silinemez.

Calistirma:
    python src/00_acquisition/make_field_check_list.py
"""

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import src.common  # noqa: E402,F401

from pyproj import Transformer  # noqa: E402
from shapely.geometry import shape  # noqa: E402

from src.common.config import load_acceptance_criteria, resolve  # noqa: E402
from src.common.logging_setup import setup_logging  # noqa: E402
from src.common.meta import write_meta  # noqa: E402

OUT = "field_check_list.md"
LARGE_M2 = 100.0            # D-029: ucus sonrasi "buyuk" siniri

GROUPS = {
    "G1": "sifir sinif-6 orneklemi",
    "G2": "belirsiz konut blogu",
    "G3": "buyuk ucus sonrasi",
    "G4": "kalibrasyon (muhurlu)",
    "G4p": "kalibrasyon (ONERI P-020)",
}


def _read(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _guard(path: Path, logger) -> None:
    """Doldurulmus bir tablo uzerine YAZMAZ (saha calismasi korunur)."""
    if not path.is_file():
        return
    txt = path.read_text(encoding="utf-8")
    # YALNIZCA veri satirlari: icinde `<16 haneli bag_id>` gecen tablo satirlari.
    # (Dosyadaki diger tablolar — ozet, kural listesi — yanlis alarm vermesin.)
    filled = 0
    for line in txt.splitlines():
        if not line.startswith("| ") or not re.search(r"`\d{16}`", line):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) >= 4 and any(c not in ("", "—") for c in cells[-4:]):
            filled += 1
    if filled:
        raise SystemExit(
            f"DURDURULDU: {path} icinde {filled} satir DOLDURULMUS. Uzerine "
            f"yazmak saha calismasini siler. Once dosyayi baska bir ada kopyala, "
            f"sonra bu scripti tekrar calistir.")
    logger.info("Uzerine yazma kontrolu | dolu satir yok, uretim guvenli")


def main() -> int:
    logger, run_id, _ = setup_logging("make_field_check_list")
    rep = resolve("reports.dir")
    docs = Path("docs")
    out = docs / OUT
    _guard(out, logger)

    cfg = load_acceptance_criteria()
    rules = cfg["storey_counting_rule"]["rules"]
    n_small = cfg["building_lineage"]["assignment"]["post_flight_small"]["count_measured"]

    # --- BAG'den geometri ve oznitelik (tek kaynak) ---
    bag = {f["properties"]["identificatie"]: f for f in json.loads(
        (resolve("data.raw") / "bag" / "bag_pand.geojson").read_text(
            encoding="utf-8"))["features"]}
    tf = Transformer.from_crs("EPSG:28992", "EPSG:4326", always_xy=True)

    rows: dict[str, dict] = {}

    def add(bid: str, grp: str, **extra) -> None:
        r = rows.setdefault(bid, {"bag_id": bid, "groups": [], "notlar": []})
        if grp not in r["groups"]:
            r["groups"].append(grp)
        r.update({k: v for k, v in extra.items() if v})

    for r in _read(rep / "visual_check_sample.csv"):
        add(r["bag_id"], "G1", alt_grup=r["alt_grup"])
    for r in _read(rep / "a_residential_uncertain.csv"):
        add(r["bag_id"], "G2", konut_vbo=r["woonfunctie_vbo"])
    n_large = 0
    for r in _read(rep / "post_flight_buildings.csv"):
        if float(r["footprint_area_m2"]) >= LARGE_M2:
            add(r["bag_id"], "G3", alan_ab=r["alan"])
            n_large += 1
    for r in _read(rep / "storey_height_calibration.csv"):
        add(r["bag_id"], "G4", desil=r["desil"])
    prop_path = rep / "storey_height_calibration_proposal_p020.csv"
    for r in _read(prop_path):
        add(r["bag_id"], "G4p", sinif=r["yukseklik_sinifi_m"])

    logger.info("Gruplar | G1=%d G2=%d G3=%d G4=%d G4p=%d | benzersiz bina=%d",
                sum("G1" in r["groups"] for r in rows.values()),
                sum("G2" in r["groups"] for r in rows.values()), n_large,
                sum("G4" in r["groups"] for r in rows.values()),
                sum("G4p" in r["groups"] for r in rows.values()), len(rows))
    if n_large != 6:
        logger.warning("Buyuk ucus sonrasi yapi sayisi %d, D-029'da 6 yaziyor", n_large)

    # --- BAG'den doldur: alan, bouwjaar, gebruiksdoel, lat/lon ---
    missing = [b for b in rows if b not in bag]
    if missing:
        raise SystemExit(f"BAG'de bulunamayan bina: {missing}")
    for bid, r in rows.items():
        pr = bag[bid]["properties"]
        g = shape(bag[bid]["geometry"])
        c = g.centroid
        lon, lat = tf.transform(c.x, c.y)
        r.update(area=g.area, bouwjaar=pr.get("bouwjaar") or "",
                 gebruiksdoel=pr.get("gebruiksdoel") or "—",
                 lat=lat, lon=lon, x=c.x, y=c.y)

    order = {"G2": 0, "G3": 1, "G4": 2, "G4p": 2, "G1": 3}
    ordered = sorted(rows.values(),
                     key=lambda r: (min(order[g] for g in r["groups"]), -r["area"]))

    def links(r: dict) -> str:
        sv = (f"https://www.google.com/maps/@?api=1&map_action=pano"
              f"&viewpoint={r['lat']:.7f},{r['lon']:.7f}")
        mp = (f"https://www.google.com/maps/search/?api=1"
              f"&query={r['lat']:.7f},{r['lon']:.7f}")
        return f"[SV]({sv}) · [Harita]({mp})"

    body = []
    for i, r in enumerate(ordered, 1):
        grp = " + ".join(GROUPS[g].split(" (")[0] if g.startswith("G4") else GROUPS[g]
                         for g in r["groups"])
        if "G4" in r["groups"] and "G4p" in r["groups"]:
            grp = "kalibrasyon (ikisinde de)"
        elif "G4" in r["groups"]:
            grp = "kalibrasyon (muhurlu)"
        elif "G4p" in r["groups"]:
            grp = "kalibrasyon (ONERI)"
        need_obs = "G1" in r["groups"] or "G2" in r["groups"]
        need_2023 = need_obs or "G3" in r["groups"]
        body.append(
            f"| {i} | {grp} | `{r['bag_id']}` | {r['area']:.0f} | {r['bouwjaar']} | "
            f"{r['gebruiksdoel']} | {r['lat']:.6f}, {r['lon']:.6f} | {links(r)} | "
            f"{'' if need_obs else '—'} | {'' if need_2023 else '—'} |  |  |"
        )

    rule_lines = "\n".join(
        f"| **{k.split('_')[0]}** | {v['text'].strip()} | "
        f"{(v.get('note_required') or v.get('why') or v.get('test') or '').strip()} |"
        for k, v in rules.items())

    md = f"""# Saha kontrol listesi — Voorhof

**Dolduracak:** kullanici · **Tarih:** _______ · **run_id:** `{run_id}`
**Uretildi:** `src/00_acquisition/make_field_check_list.py` (elle yazilmadi)

> **VERI DONEMI (D-020).** Geometri AHN5 **2023-02-08 / 02-14**; BAG
> oznitelikleri **2026-09**. "2023'te var miydi" sorusu **Subat 2023**'u
> kasteder.

> ⚠️ **BU DOSYA BIR KEZ URETILIR.** Doldurduktan sonra script yeniden
> calistirilsa bile uzerine YAZMAZ (dolu hucre gorurse durur). Yine de once
> bir kopyasini almak iyi fikirdir.

---

## Bu listede ne var

| Grup | Ne | Kac bina | Ne soruluyor |
|---|---|---|---|
| **belirsiz konut blogu** | A'daki 3 buyuk konut blogu (412 konut VBO) | {sum("G2" in r["groups"] for r in rows.values())} | 2023'te bu bina mi vardi? **kat sayisi** |
| **buyuk ucus sonrasi** | Ayakizi >= {LARGE_M2:.0f} m2, ucustan sonra yapilmis (D-029) | {n_large} | 2023'te var miydi? **kat sayisi** |
| **kalibrasyon** | Kat yuksekligini olcmek icin (D-030) | {sum("G4" in r["groups"] or "G4p" in r["groups"] for r in rows.values())} | **yalnizca kat sayisi** |
| **sifir sinif-6 orneklemi** | AHN5'te cati noktasi olmayan yapilar (D-019) | {sum("G1" in r["groups"] for r in rows.values())} | bu ne? 2023'te var miydi? |

Toplam **{len(rows)} bina**. Ayni bina birden fazla gruptaysa **tek satir**
yazildi.

**Kucuk ucus sonrasi yapilar ({n_small} adet) bu listede YOKTUR** — D-029
geregi `footprint_only` kalirlar, kat sayilmaz.

---

## ⚠️ ONCE BUNU OKU — kat sayim kurali (D-030, sayimdan ONCE muhurlendi)

Bu kural **sen saymaya baslamadan once** `config/acceptance_criteria.yml`'ye
yazildi ve commit edildi (`f2667c1`). Sayim sonucuna gore degistirilemez.

| # | Kural | Not / gerekce |
|---|---|---|
{rule_lines}

**Ozet:** zemin kat **1'dir**; bodrum **sayilmaz**; cati ustu makine dairesi
**sayilmaz**; pilotis ve cekme kat **sayilir**; emin degilsen **bos birak**.

---

## ⚠️ Kalibrasyon binalarinda YUKSEKLIK BILEREK GOSTERILMEDI

Kalibrasyon, senin saydigin kat sayisini **bizim olctugumuz yukseklige**
bolerek kat yuksekligini bulur. Eger listede "36,8 m" yazsaydi, sayim o sayiya
**demirlenirdi** (12 kat mi? o zaman 12 yazayim) ve sonuc kendi girdisini
dogrulamis olurdu — Bolum 12.10'un yasakladigi sey.

Yukseklikler `reports/building_heights_ahn5.csv` icinde duruyor ve sayimdan
**sonra** yan yana raporlanacak.

---

## ⚠️ KARAR GEREKIYOR (P-020) — saymaya baslamadan once

Kalibrasyon orneklemi icin muhurledigim **desil** kurali kendi amacini
tutturamadi. Kural "farkli yukseklikleri kapsasin" diyordu ama desiller
**nufusu** izler, **araligi** degil: uygun havuzun (514 bina) **%66'si**
5,7-6,0 m bandinda (ayni tip sira ev). Sonuc: muhurlu 10 binanin **6'si ayni
yukseklikte**.

Havuzda aslinda zengin bir dagilim var (olculdu):

| h (yuvarlanmis) | 3 m | 6 m | 8 m | 9 m | 11 m | 14 m | 26 m | 35 m | 37 m |
|---|---|---|---|---|---|---|---|---|---|
| bina | 3 | 337 | 97 | 46 | 5 | 4 | 9 | 3 | 10 |

**Kurali sonucu gordukten sonra degistirmedim** (Bolum 12.2). Muhurlu cikti
oldugu gibi duruyor; alternatifi **ONERI** olarak ayri dosyaya yazdim
(`reports/storey_height_calibration_proposal_p020.csv`): her yukseklik
sinifindan 1 bina.

**Bu listede ikisinin BIRLESIMI var.** Ne yapmak istedigini soyle:

- **(a)** Oneriyi onayla -> kural yeni bir D kaydi ile degisir, ornekleme yukseklik
  siniflari girer. **Onerim bu.**
- **(b)** Muhurlu desil kurali kalsin.

**Karar ORTALAMA HESAPLANMADAN once verilmelidir.** Iki orneklemi de sayip
sonra "hangisi daha iyi sonuc verdi" diye secmek, esigi sonuca gore secmenin
ta kendisi olur (Bolum 12.2).

---

## Tablo

**Doldurulacak dort sutun sagda.** Doldurma kilavuzu tablonun altinda.

| # | grup | bag_id | m2 | bouwjaar | gebruiksdoel | lat, lon | harita | GOZLEM | 2023'te var miydi | KAT | NOT |
|---|---|---|---|---|---|---|---|---|---|---|---|
{chr(10).join(body)}

---

## Sutunlari nasil dolduracaksin

**GOZLEM** (yalnizca "sifir sinif-6" ve "belirsiz konut blogu" satirlari):

| Grup | Yazilacak degerler |
|---|---|
| sifir sinif-6 orneklemi | `depo/kulube` · `ev` · `baska` · `goruntude yok` |
| belirsiz konut blogu | `S1` (ayni bina) · `S2` (yikilip yeniden yapildi) · `S3` (2023'te insaat halindeydi) · `karar veremedim` |

> **Iki gruba birden giren bina** (`grup` sutununda "+" isareti varsa):
> **S1/S2/S3** sozlugunu kullan. O bina zaten hem sifir orneklemine hem de
> belirsiz bloga girdigi icin asil soru "bu 2023'teki bina mi" sorusudur.

> `karar veremedim` gecerli bir cevaptir ve ne yapilacagi **onceden**
> kararlastirildi (D-028): bina ihtiyatli olarak S2/S3 gibi islenir ve bu
> durum raporda **ayri** yazilir. Tahmin etmeye calisma.

**2023'te var miydi:** `E` / `H` / `?` — Subat 2023 kastediliyor.
Street View'da zaman tuneli (goruntu tarihine tikla) ve guncel hava
fotografi birlikte kullanilir. **Goruntu tarihini NOT'a yaz** (kural R11).

**KAT:** yukaridaki kurala gore tam sayi. Sayamiyorsan **bos birak** ve
NOT'a `sayilamadi` yaz (kural R10). Tahmin yazma.

**NOT:** kural R3/R4/R6/R7/R9'un istedigi etiketler (`souterrain sayildi`,
`cati kati: dormer`, `pilotis`, `cekme kat`, `N katli ek var`), goruntu
tarihi ve aklina takilan her sey.

---

## Bittiginde

Bu dosyayi kaydet ve bana soyle. Ben:
1. `KAT` sutununu `reports/storey_height_calibration.csv`'ye tasirim,
2. kat yuksekligini ve standart sapmasini hesaplarim (D-030 formulu),
3. 3 konut blogunu S1/S2/S3/karar-veremedim'e gore siniflarim (D-024/D-028),
4. 9 binaya (`3 blok + 6 buyuk yapi`) `estimated_lod1` yuksekligi yazarim,
5. P-012'yi (hangi AHN siniflari Asama 1'e girecek) karara baglariz.
"""
    out.write_text(md, encoding="utf-8")
    write_meta(out, run_id=run_id,
               parameters={"buildings": len(rows), "groups": {
                   k: sum(k in r["groups"] for r in rows.values()) for k in GROUPS},
                   "large_post_flight": n_large,
                   "sources": ["visual_check_sample.csv", "a_residential_uncertain.csv",
                               "post_flight_buildings.csv", "storey_height_calibration.csv",
                               "storey_height_calibration_proposal_p020.csv"]},
               notes=("Olculen yukseklik BILEREK yazilmadi (sayim demirlenmesin, "
                      "Bolum 12.10). Uzerine yazma korumasi: dolu hucre varsa durur."))
    logger.info("TAMAM | %s | %d bina", out, len(rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
