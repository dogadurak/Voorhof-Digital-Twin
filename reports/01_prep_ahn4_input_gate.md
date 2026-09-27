# AHN4 girdi kalite kapisi (Bolum 12.12) — kriter 1-C-c on-kosulu

> **Veri donemi:** 1-C-c modeli AHN5 2023-02-08/14'ten kurar; bu kapi AHN4'u olcer.
> **Kural:** `config/acceptance_criteria.yml` -> `input_gate_ahn4`, olcumden ONCE muhurlendi (5342d47). Bu rapor 1-C-c'nin SONUCUNU icermez; yalnizca girdiyi olcer.

run_id: `RUN-2026-09-27-012` · git_commit: `5342d47-dirty` · calistirma (UTC): 2026-09-27T08:21:57Z

## Genel sonuc: **PASS**

| Kontrol | Olculen | Muhurlu kural | Sonuc |
|---|---|---|---|
| G4-A yogunluk (sert) | medyan 36.58 p/m2 (p10 23.88) | >= 10.0 | **PASS** |
| G4-B yogunluk (beklenti) | medyan 36.58 p/m2 | >= 20.0 (UYARI) | **PASS** |
| G4-C ucus tarihi | 2020-03-17 .. 2020-04-07 UTC; ucus gunleri 2 | cozulebilir VE < 2023-02-08 | **PASS** |
| G4-D sinif dagilimi | 1: 43,139,190, 2: 82,466,029, 6: 34,994,560, 9: 352,395, 26: 584,560 | sinif 6 var | **PASS** |
| G4-E kapsama | sifir donuslu hucre %0.07; 1-C-c kumesi 1159 bina, >=20 sinif-6 noktasi olan 950 | esik yok (rapor) | **PASS** |
| G4-F lisans | ATTRIBUTION.md satir 1b dolu | birincil kaynaktan okunmus | **PASS** |

**1-C-c kumesi icin AHN4 ucus yili (muhurlu: en erken yil): 2020.** 1-C-a kumesi 1170 bina -> daraltma sonrasi bos 4 -> bouwjaar >= 2020 cikan 4 -> mutasyon bayragi True/bilinmeyen cikan 5 -> **1-C-c kumesi 1159**, bunlardan >= 20 sinif-6 noktasi olan 950.

## Ucus gunleri (serit baslangicina gore)

| Ucus gunu (UTC) | serit sayisi |
|---|---|
| 2020-03-17 | 3 |
| 2020-04-07 | 1 |
NGR RWS DTM kaydinin zamansal kapsami 2019-11-30 / 2022-03-25; olculen aralik bu kapsamin **icinde**.


## Sinirlamalar

- gps_time Adjusted Standard GPS Time varsayilarak cozuldu (AHN5 ile ayni; global_encoding bayragi AHN5'te yanlisti). Sonuc tarihleri NGR kaydinin zamansal kapsamiyla (2019-11-30 / 2022-03-25) karsilastirilmalidir — asagida.
- Yogunluk tum siniflarla olculdu (AHN5 kapisiyla ayni yontem).
- Lisans: bu script lisansi YAZMAZ; ATTRIBUTION.md'deki insan kaydini denetler.
