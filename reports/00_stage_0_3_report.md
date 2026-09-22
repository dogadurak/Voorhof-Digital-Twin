# Asama 0.3 — Asama Sonu Raporu

> **Bu rapor `src/qa/make_stage_0_3_report.py` tarafindan uretilmistir.**
> Anlati elle yazildi; **her sayi ve her kontrol** kaynagindan okundu veya
> fiilen calistirildi (M-010 tekrari: elle aktarim yasak).

```
=== ASAMA SONU RAPORU ===
run_id:            RUN-2026-09-22-015
asama:             0.3 — AHN5 + 3DBAG veri edinimi, girdi kalite kapisi,
                   ucus sonrasi tespit
git_commit:        ee7800e
calistirma (UTC):  2026-09-22T19:04:58Z
veri donemi:       geometri AHN5 2023-02-08/14 · oznitelik BAG 2026-09 ·
                   3DBAG referansi v2025.09.03 (SABITLENDI, D-027)
```

## KABUL KRITERI

| Metrik | Esik (config'ten) | Olculen | Sonuc |
|---|---|---|---|
| 0-E sert kapi — medyan nokta yogunlugu | >= 10,0 p/m2 | **35,89** | **PASS** |
| 0-F beklenti — medyan nokta yogunlugu | >= 20,0 p/m2 | **35,89** | **PASS** |

**Bolum 12.2 denetim izi:** esik muhur commit'i `77fdfbb` -> olcum commit'i
`0efe40b`. Muhur olcumden **once** gelir; iddia degil, `git log` sirasi.
(D-015 kaydi o sirada eksikti, geriye donuk yazildi — M-008.)

**Esiksiz raporlanan olcumler:** p10 = 17,79 p/m2 ·
sifir donuslu hucre %0,09 ·
10 p/m2 altinda bina 1 ·
sinif 6 orani medyan 0,874 ·
oran tanimsiz 0 bina.

## OLCUMUN KAYNAGI

| Cikti | Uretici script | run_id | git_commit |
|---|---|---|---|
| `00_stage_0_3_ahn_gate.md` | `src/00_acquisition/verify_ahn_quality.py` | `RUN-2026-09-21-024` | `d4cf95b-dirty` |
| `00_stage_0_3_post_flight_detection.md` | `src/00_acquisition/detect_post_flight_buildings.py` | `RUN-2026-09-21-023` | `d4cf95b-dirty` |
| `00_stage_0_3_uncertain_geometry_breakdown.md` | `src/00_acquisition/report_uncertain_geometry.py` | `RUN-2026-09-22-016` | `ee7800e-dirty` |

**Girdi dosyalari:** 9 AHN5 LAZ (3,12 GB) ·
BAG pand + verblijfsobject (PDOK WFS) · 3DBAG sabitlenmis
30 fayans (41,1 MB).
Checksum'lar `data/DATA_LOG.md`'de; 3DBAG fayanslari **yayincinin**
`cj_sha256` degerleriyle dogrulandi.

## SPOT KONTROL

N=10, seed=28992, uyusmayan bina 0, en buyuk bagil alan farki 5.2e-07 -> **PASS**

Ayrinti: `reports/00_stage_0_3_spot_check.md` — asil hesap STRtree +
vektorel nokta + shapely alani kullanir; spot kontrol **indekssiz
`contains`** ve **shoelace alani** kullanir. Ayni hata iki yolda ayni
sekilde tekrarlanmadikca fark gorunur.

## BASARISIZ KAYITLAR

Asama 0.3 rekonstruksiyon yapmaz; `failed_buildings.csv` Asama 1'e aittir.
Bu asamanin "basarisiz kayit" karsiligi **dislanan/isaretlenen binalardir**:

| Kategori | Bina | Kayit |
|---|---|---|
| Ucus sonrasi aday | 30 | `reports/post_flight_buildings.csv` |
| Supheli (3 kosuldan 2'si) | 60 | `reports/post_flight_suspects.csv` |
| Olasi yeniden yapim | 50 | `reports/rebuild_suspects.csv` |
| A'da belirsiz geometrili **konut** binasi | 3 | `aoi/qa/a_residential_uncertain.geojson` |

A'nin konut stokunun **%5,39**'i
(412/7637 konut VBO) belirsiz geometrili binalarda.

## KURAL UYUM KONTROLU (fiilen calistirildi)

| | Kontrol | Sonuc |
|---|---|---|
| [x] | `git diff config/acceptance_criteria.yml` bos | temiz |
| [x] | .meta.json her ciktida var | hepsi var |
| [x] | `data/raw/` butunlugu: kayitli sha256 tutuyor (9 dosya) | hepsi dogrulandi |
| [x] | Repoda secret yok (kaba tarama) | bulunmadi |
| [x] | D/P/M atiflarinin hepsi cozuluyor (`check_refs.py`) | Cozulmeyen atif yok. |
| [x] | Tekrarlanabilirlik: ayni girdi -> ayni VERI ciktisi (checksum) | 2 dosya | hepsi ayni |
| [x] | CRS ve birimler Bolum 12.1'e uygun | yatay EPSG:28992 (paths.yml), LAZ EPSG:7415, birim metre |
| [x] | Uydurma sayi yok — her deger bir hesaptan geliyor | bu rapordaki tum sayilar .meta.json ve CSV'lerden okundu |

## SINIRLAMALAR

1. **Veri donemi farki 3,5 yil** — geometri 2023-02, oznitelik 2026-09 (D-020)
2. **AHN5 icin siniflandirma spesifikasyonu yok** — yorumlar AHN4 ihale
   sartnamesinden tasindi; kod 14 hicbir AHN belgesinde gecmiyor (D-017)
3. **AHN sinif 6 BAG'den turer** — bagimsiz dogrulama olarak kullanilamaz (D-017)
4. **3DBAG'in AHN5'i "yetersiz" bulmasi bir TANIM farkiydi** (D-026); "girdimiz
   saglam" sonucu **kosulludur** — Asama 1 yalnizca sinif 6 kullanirsa ayni
   sorun bizde de olur (P-012)
5. **3 konut binasi ve 30 ucus sonrasi
   yapi** icin geometri AHN5'ten uretilemez (D-019, D-024, D-025)
6. **Ayni ayakizi uzerinde yeniden yapim / insaat halindeki bina** yalnizca
   gorsel kontrolle ayirt edilebiliyor (D-022)
7. **Sifir grubu aciklamasi bir CIKARIM** — dogrulanmadi (M-011, **ACIK**)
8. **PROJ oz-testi sessiz datum farkini yakalamaz** (P-015)
9. **Kat yuksekligi icin dogrulanmis bir tipik deger yok** — Bbl yalnizca
   alt sinir (2,6 m serbest yukseklik) veriyor (D-025, P-019)

## GENEL SONUC: PASS

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
