# Cephe sinif olcumu — SONRADAN KESIF ANALIZI (ONERI)

> **Veri donemi:** geometri AHN5 2023-02-08/14 · oznitelik BAG 2026-09 (D-020).
> ⚠️ **Bu analiz sonuc GORULDUKTEN SONRA tasarlandi.** Muhurlu olcumun karari (`reports/01_prep_facade_class_measurement.md`: **MIXED**) DEGISMEZ. Burada yalnizca MIXED'in olasi bir aciklamasi sinaniyor (M-016 protokolu: kural degistirilmez, alternatif ayri cikti olarak ONERI etiketiyle uretilir).

run_id: `RUN-2026-09-27-001` · git_commit: `7b2ca3f-dirty` · calistirma (UTC): 2026-09-27T07:40:17Z

**Sinanan aciklama (CIKARIM):** egimli catilarda sacak/cati kenari noktalari (sinif 6) cephe bolgesine dusuyor. Dogruysa `horizontal` katmaninda sinif 6 payi dusuk, `slanted` katmaninda yuksek olmali.

**Katman kaynagi:** 3DBAG v2025.09.03 `b3_dak_type` — bizim ciktimiz degil, olcumden once var olan sabit oznitelik.

| 3DBAG b3_dak_type | bina | cephe noktasi | havuz s6 ic | havuz s6 dis | bina basina s6 medyan | s1 duvar yogunlasmasi |
|---|---|---|---|---|---|---|
| slanted | 1,302 | 1,701,943 | 0.278 | 0.231 | 0.461 | 0.761 |
| multiple horizontal | 179 | 185,598 | 0.126 | 0.087 | 0.353 | 0.749 |
| horizontal | 155 | 93,528 | 0.022 | 0.065 | 0.008 | 0.742 |
| unknown | 2 | 83,764 | 0.241 | 0.215 | 0.235 | 0.834 |
| 3DBAG'de yok | 1 | 299 | 0.197 | 0.116 | 0.150 | 0.348 |

## Sinirlamalar

- Post-hoc: katmanlama sonuc gorulduktan sonra secildi; kanit degeri muhurlu olcumden DUSUKTUR.
- 3DBAG cati tipi bir rekonstruksiyon ciktisidir (roofer); yanlis tiplenmis binalar katmanlar arasinda karisir.
- Katman icinde bile sinif 6 noktalarinin sacak mi, balkon mu, dakkapel mi oldugu ayirt edilmedi.
