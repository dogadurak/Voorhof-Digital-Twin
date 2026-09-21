# Asama 0.2 — Asama Sonu Raporu

> Format: AGENTS.md Bolum 13.1. Elle yazildi (Karar D-005).
> `src/qa/make_stage_report.py` Asama 0.5'te yazilacaktir.

```
=== ASAMA SONU RAPORU ===
run_id:            RUN-2026-09-21-007 (rapor uretimi)
asama:             0.2 — Alan sinirlari (A ve B)
git_commit:        fc60c87 + bu commit
calistirma (UTC):  2026-09-21
sure:              tek oturum
```

---

## KABUL KRITERI

**Bu asamada SAYISAL ESIK YOKTUR.** Karar D-009 ile A resmi CBS buurt
sinirlarindan turedigi icin bina sayisi, woonfunctie orani ve bouwjaar dagilimi
kabul kriteri degil, **tanimlayici olcumlerdir**. `stage_0_2`'nin eski aday
kriterleri `superseded_by: D-009` olarak isaretlendi ve **hicbir zaman
calistirilmadi**.

Yerine, geometrinin ve kapsamanin dogrulugu sinandi:

| # | Dogrulama | Beklenen | Olculen | Sonuc |
|---|---|---|---|---|
| V-1 | A geometrisi gecerli | `is_valid == True` | True | **PASS** |
| V-2 | A tek parca | 1 | 1 (`Polygon`) | **PASS** |
| V-3 | A ile dislanan sanayi buurt'lari kesismiyor | 0,00 ha | **0,0000 ha** | **PASS** |
| V-4 | B geometrisi gecerli | `is_valid == True` | True | **PASS** |
| V-5 | Kaynak CRS beklenenle esti | EPSG:28992 | EPSG:28992 | **PASS** |
| V-6 | Indirilen BAG kapsami B'yi tamamen iceriyor | icerir | icerir (pay 0,0 m) | **PASS** (bkz. sinirlama 2) |
| V-7 | Dahil edilen buurt sayisi | 7 | 7 | **PASS** |
| V-8 | Dislanan buurt sayisi | 2 | 2 | **PASS** |

---

## OLCUMUN KAYNAGI

| Deger | Script | Girdi |
|---|---|---|
| A, B geometrileri ve alanlar | `src/00_acquisition/build_aoi.py` | `data/raw/cbs/voorhof_buurten.geojson` |
| Bina istatistikleri | `src/00_acquisition/report_aoi_stats.py` | `bag_pand.geojson`, `bag_verblijfsobject.geojson` |
| Kapsama kontrolu | `report_aoi_stats.py` | `bag_pand.geojson.meta.json` -> `bbox_epsg28992` |
| Status filtresi degerleri | `wfs.describe_attributes()` | indirilen veriden dogrulandi (M-005) |

Metrik paydalari Karar **D-008**'den, status filtresi `stage_0_2.status_filter`
blogundan okundu; koda gomulmedi.

---

## OLCULEN DEGERLER (esik yok — tanimlayici)

| Metrik | A (analysis) | context (B \ A) | B (toplam) |
|---|---|---|---|
| Alan (ha) | 109,62 | 168,14 | 277,76 |
| Pand | 1.259 | 2.776 | 4.035 |
| Konutlu pand | 898 | 1.534 | 2.432 |
| Verblijfsobject | 8.246 | 5.505 | 13.751 |
| woonfunctie (%) | 92,6 | 93,5 | 93,0 |
| bouwjaar 1960-1975 (%) | 75,1 | 42,4 | 62,0 |
| Ortalama bouwjaar | 1977,8 | 1984,0 | 1980,3 |

Ayrinti: `reports/00_stage_0_2_aoi.md`

---

## SPOT KONTROL

| # | Test | Beklenen | Olculen | Sonuc |
|---|---|---|---|---|
| 1 | A alani, CBS kara alani toplamiyla tutarli mi | ~107 ha | 109,62 ha (fark 2,62 ha = su yuzeyi) | PASS |
| 2 | Sanayi buurt'lari B icinde mi | %100 | **%100** (17,14 ha) | PASS |
| 3 | Dahil buurt kodlari veriden dogrulandi | 7 kod | BU05032400/01/03/04/05/06/07 | PASS |
| 4 | Kesisim log satiri iki sink'e de ulasti | 2 sink | 2 sink (M-006 sonrasi) | PASS |
| 5 | ASCII disi karakter testi | 2 sink | `∩ ≤ °C m²` iki sink'te | PASS |
| 6 | `DATA_LOG` idempotans (tekrar calistirma) | kopya yok | 2 kayit sabit | PASS |
| 7 | AOI dosyalari CRS uyesi tasiyor | EPSG:28992 | EPSG:28992 | PASS |
| 8 | Status filtresi degerleri veriden mi | evet | 6 pand + 3 VBO degeri sayildi | PASS |

**seed:** Bu asamada rastgelelik yoktur; seed uygulanmaz.

---

## BASARISIZ KAYITLAR

```
toplam islenen:   7.704 pand + 19.346 VBO
status filtresiyle dislanan:  47 pand (%0,61) + 668 VBO (%3,45)
bozuk/okunamayan: 0
dosya:            reports/failed_buildings.csv (bos — bu asamada rekonstruksiyon yok)
```

Dislanan kayitlar sessizce atilmadi: sayilari loglandi, `excluded_by_status_count`
olarak raporlanmak uzere config'e metrik tanimlandi (Bolum 12.8).

**Sureclerde uc hata olustu, ucu de `MISTAKES.md`'ye kaydedildi:**

| ID | Konu | Durum |
|---|---|---|
| M-004 | WFS filtresi sessizce yok sayildi, 61 MB bosa indi | KAPALI |
| M-005 | Servis semasi dogrulanmadan config'e olgu yazildi (3. tekrar -> Bolum 14.5) | KAPALI |
| M-006 | Konsol kodlamasi bir DOGRULAMA log satirini sessizce dusurdu | KAPALI |

---

## KURAL UYUM KONTROLU

- [x] Uydurma sayi yok — her deger bir olcumden geliyor
- [x] `config/acceptance_criteria.yml`'deki mevcut kilitli esiklere **dokunulmadi**
      (tum degisiklikler ekleme; `git diff` silme satiri gostermedi)
- [x] Tum ciktilar `.meta.json` ile yazildi (A, B, rapor)
- [x] CRS ve birimler Bolum 12.1'e uygun; her okumada CRS karsilastirildi
- [x] Karsilastirilan buyuklukler fiziksel olarak ayni (12.4) — *bu asamada
      dogrulama karsilastirmasi yapilmadi; protokol kurallari yazildi*
- [x] `DATA_LOG.md` guncellendi (4 kayit: 2 CBS, 2 BAG + 2 AOI)
- [x] Repoya secret yazilmadi
- [x] `data/raw/` degistirilmedi — AOI ciktilari `aoi/` altina yazildi

---

## SINIRLAMALAR

1. **Bu asamanin PASS'i esik gecmek degil, dogrulama gecmektir.** Sayisal kabul
   esigi yoktur (D-009). "A dogru secildi" iddiasi olculmus degildir; A,
   **tanimi geregi** resmi buurt birlesimidir. Dogrulugu tanimin
   tekrarlanabilirliginden gelir, bir olcumden degil.

2. **B'nin guney kenarinda indirme payi 0,0 m.** Kapsama saglaniyor ama teget.
   A veya tampon degisirse ilk kirilacak yer burasidir. Karar **D-010** ile
   Asama 0.3'te AHN/3DBAG icin +50 m guvenlik payi zorunlu kilindi.

3. **"Sanayi buurt'u" nitelendirmesi yanlisti.** Dislanan iki buurt'taki 174
   pand'in 164'u konut birimi tasiyor, VBO woonfunctie orani %84,4, icinde 970
   kisi yasiyor. Dislama korundu (olculebilir iyilesme) ama gerekce **karma
   kullanim**dir, sanayi degil. `assumptions.md` V-001 (CURUTULDU).

4. **AGENTS.md Bolum 3'un tahmini 2,3 kat sapti.** A icin ~400-700 bina
   ongoruluyordu, olculen 1.259. Bolum 3 guncellendi. Bu, Asama 3-4 hesap yukunu
   dogrudan buyutur ve P-001'i (B/D boyutlari, 15,7 GB RAM) daha kritik yapar.

5. **C alani bu asamada secilmedi.** Kurallari muhurlendi ama hesap
   calistirilmadi (D-011); ENVI-met yukseklik siniri 3DBAG verisi olmadan
   uygulanamiyor. 0.2, C olmadan kapatildi (kullanici karari).

6. **Olcum araci yine olculen isle ayni oturumda yazildi** (Bolum 12.10).
   Bagimsiz Reviewer dogrulamasi gerekir.

---

## GENEL SONUC: **PASS**

Sekiz dogrulamanin sekizi de gecti. A ve B uretildi, CRS'leri dogrulandi,
kapsama sinandi. Hicbir esik degistirilmedi, hicbir sayi uydurulmadi.

---

## KULLANICI ONAYI BEKLEYENLER

| ID | Konu | Aciliyet |
|---|---|---|
| **P-011** | **C secimi + ENVI-met yukseklik esigi (oneri: H_max <= 25 m)** | **0.3 sonrasi** |
| P-001 | B ve D boyutlari — olcek 3,5x buyudugu icin daha kritik | Asama 3 sonu |
| P-002 | ENVI-met lisansi | Asama 3 sonu |
| P-004 | AHN z-fark esigi | Asama 0 sonu |
| P-005 | NMBE / CV(RMSE) esikleri | Asama 2 sonu |
| P-007 | BAG WFS nevenadres eksikligi | Asama 1 sonu |
| P-009 | Bolunmus PC6 dislama orani | Asama 2 sonu |
| P-010 | CBS Kerncijfers ikinci referans (oneri) | Asama 3 oncesi |

---

## SONRAKI ASAMANIN PLANI (baslatilmadi — Bolum 13.4)

**Asama 0.3 — Indirme scriptleri.** Ilk is: bos disk alanini **fiilen olcup**
`DATA_LOG.md`'ye yazmak (P-003 on kosulu, hedef >= 80 GB). Ardindan ayri
scriptler: `download_ahn.py`, `download_3dbag.py`. Kapsam **B bbox + 50 m**
(D-010); her script kendi `DATA_LOG` kaydini, checksum'ini ve oznitelik listesini
yazar (M-005 otomatiklestirmesi).
