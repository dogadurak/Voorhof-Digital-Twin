# Belirsiz geometri — A / B\\A ve konut kirilimi

**Karar D-022** · run_id `RUN-2026-09-22-005` · LAZ okunmadi, tespit ciktisi kullanildi

> **VERI DONEMI (D-020).** Geometri AHN5 **2023-02-08 / 02-14**; BAG
> oznitelikleri **2026-09**.

**"Konut" tanimi (D-008 `exact_match`):** bir verblijfsobject'in
`gebruiksdoel`'u **tam olarak** `woonfunctie` ise konuttur. Coklu islevli
kayitlar konut sayilmaz. Pand duzeyindeki `gebruiksdoel` **kullanilmadi** —
o bir toplamdir, konut SAYISI vermez.

## ASIL SORU: A'daki konut stokunun ne kadari belirsiz geometriye sahip?

| | Deger |
|---|---|
| A'daki toplam konut VBO | **7,637** |
| Bunlardan belirsiz geometrili binalarda olan | **412** |
| **Pay** | **%5.39** |
| Etkilenen bina sayisi | 27 |
| Etkilenen ayakizi alani | 6,916 m2 (A'nin %3.60'i) |


### A alani (raporlama alani)

| Grup | Bina | Bina payi | Alan m2 | Alan payi | Konut VBO | Konut VBO payi |
|---|---|---|---|---|---|---|
| ucus sonrasi aday | **2** | %0.16 | 1,001 | %0.52 | **0** | **%0.00** |
| supheli (2/3) | **21** | %1.67 | 1,845 | %0.96 | **0** | **%0.00** |
| olasi yeniden yapim | **7** | %0.56 | 5,788 | %3.01 | **412** | **%5.39** |
| **BIRLESIM (tekil)** | **27** | %2.14 | 6,916 | %3.60 | **412** | **%5.39** |

Taban: 1,259 bina · 192,349 m2 · 7,637 konut VBO

### B \ A (yalniz baglam)

| Grup | Bina | Bina payi | Alan m2 | Alan payi | Konut VBO | Konut VBO payi |
|---|---|---|---|---|---|---|
| ucus sonrasi aday | **28** | %1.01 | 4,870 | %1.19 | **92** | **%1.79** |
| supheli (2/3) | **39** | %1.40 | 292 | %0.07 | **0** | **%0.00** |
| olasi yeniden yapim | **43** | %1.55 | 4,588 | %1.12 | **206** | **%4.00** |
| **BIRLESIM (tekil)** | **103** | %3.71 | 9,710 | %2.38 | **298** | **%5.79** |

Taban: 2,776 bina · 408,149 m2 · 5,147 konut VBO

### A alani — YALNIZCA konut VBO'lu binalar

| Grup | Bina | Bina payi | Alan m2 | Alan payi | Konut VBO | Konut VBO payi |
|---|---|---|---|---|---|---|
| ucus sonrasi aday | **0** | %0.00 | 0 | %0.00 | **0** | **%0.00** |
| supheli (2/3) | **0** | %0.00 | 0 | %0.00 | **0** | **%0.00** |
| olasi yeniden yapim | **3** | %0.43 | 4,033 | %2.57 | **412** | **%5.39** |
| **BIRLESIM (tekil)** | **3** | %0.43 | 4,033 | %2.57 | **412** | **%5.39** |

Taban: 692 bina · 156,639 m2 · 7,637 konut VBO

### A alani — konut VBO'su OLMAYAN binalar

| Grup | Bina | Bina payi | Alan m2 | Alan payi | Konut VBO | Konut VBO payi |
|---|---|---|---|---|---|---|
| ucus sonrasi aday | **2** | %0.35 | 1,001 | %2.80 | **0** | **%0.00** |
| supheli (2/3) | **21** | %3.70 | 1,845 | %5.17 | **0** | **%0.00** |
| olasi yeniden yapim | **4** | %0.71 | 1,755 | %4.91 | **0** | **%0.00** |
| **BIRLESIM (tekil)** | **24** | %4.23 | 2,883 | %8.07 | **0** | **%0.00** |

Taban: 567 bina · 35,710 m2 · 0 konut VBO

## Satir kaybi — nedenleriyle (Bolum 14.6 "sessiz veri kaybi")

| Adim | Once | Sonra | Dusen | Neden |
|---|---|---|---|---|
| BAG pand -> B ici + status | 7,704 | 4,035 | 3,669 | status disi / B disi: 9; status disi / B ici: 38; status uygun / B disi: 3,622 |
| VBO -> status | 19,346 | 18,678 | 668 | Verblijfsobject gevormd: 668 (D-008) |
| VBO -> pand eslesmesi | — | — | 1 | pand indirmesinde karsiligi yok: 0503100000001130 |

"B disi" satirlarinin tamami beklenendir: BAG indirmesi **B + 300 m
dikdortgeni** icindi (D-006), B ise bir **poligondur**; dikdortgenin
kosesindeki binalar B'ye girmez.

## Gruplarin ortusmesi

`post_flight` ∩ `rebuild` = **0** (kural geregi, R2).
`supheli` ∩ `rebuild` = **10** bina — **olculdu, varsayilmadi**.
Birlesim satirlari tekil sayar.

## A'daki belirsiz geometrili KONUT binalari

**3 bina**, toplam **412 konut VBO**.

Grup dagilimi:

| Grup | Bina |
|---|---|
| olasi yeniden yapim | 3 |

Konut VBO sayisina gore en buyuk 5 (Bolum 14.6):

| # | bag_id | konut VBO | m2 | bouwjaar | grup |
|---|---|---|---|---|---|
| 1 | `0503100000037336` | **260** | 1,251.6 | 2023 | olasi yeniden yapim |
| 2 | `0503100000037335` | **94** | 1,961.8 | 2023 | olasi yeniden yapim |
| 3 | `0503100000038177` | **58** | 819.9 | 2025 | olasi yeniden yapim |

**Ciktilar:**
- `aoi/qa/a_residential_uncertain.geojson` (EPSG:28992, `lat`/`lon`
  oznitelik olarak da var; `gozlem` sutunu bos birakildi)
- `reports/a_residential_uncertain.csv`

## Ne yapilmadi

Bu rapor **karar vermez**. Gruplarin hicbiri icin dislama/dahil etme
uygulanmamistir; P-012, P-013 ve P-014 acik kararlardir.
