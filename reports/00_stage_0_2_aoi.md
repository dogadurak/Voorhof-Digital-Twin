# Asama 0.2 — AOI tanimi ve bina istatistikleri

**Karar D-009** · run_id `RUN-2026-09-21-007` · CRS `EPSG:28992`

> **BU RAPORDA ESIK YOKTUR.** A, resmi CBS konut buurt'larindan turedigi icin
> asagidaki sayilar kabul kriteri degil, alanin tanimlayici olcumleridir.
> Hicbiri icin PASS/FAIL beyan edilmez (Karar D-009).

## Calisma alani

Calisma alani = **Voorhof'un (WK050324) 7 resmi konut buurt'u**.
Iki sanayi buurt'u A'nin raporlama kapsamindan dislanmistir.

**Dahil edilen buurt kodlari:** BU05032400, BU05032401, BU05032403, BU05032404, BU05032405, BU05032406, BU05032407

**Dislanan:** BU05032402, BU05032408 (Bedrijventerrein Voorhof,
Bedrijventerrein Vulcanusweg)

**Dislama sadece RAPORLAMA kapsami icindir.** Bu binalar B icinde kalir, LOD2
rekonstruksiyonuna girer, 3B modelde yer alir ve golge/CFD hesaplarina girdi olur.

## Olculen degerler

| Metrik | A (analysis) | context (B \ A) | B (toplam) |
|---|---|---|---|
| Alan (ha, geometrik) | 109.62 | 168.14 | 277.76 |
| Pand sayisi | 1259 | 2776 | 4035 |
| Konut birimi iceren pand | 898 | 1534 | 2432 |
| Konut birimi icermeyen pand | 361 | 1242 | 1603 |
| Verblijfsobject | 8246 | 5505 | 13751 |
| woonfunctie orani (%) | 92.6 | 93.5 | 93.0 |
| bouwjaar 1960-1975 (%) | 75.1 | 42.4 | 62.0 |
| Ortalama bouwjaar | 1977.8 | 1984.0 | 1980.3 |

## Rol atamasi (Asama 2'de her binaya yazilacak)

| Rol | Pand | Anlami |
|---|---|---|
| `analysis` | 1259 | Centroid A icinde. Raporlanir, dogrulamaya girer. |
| `context` | 2776 | Centroid B icinde A disinda. Modelde kalir, raporlanmaz. |

Indirme tamponu fazlasi (B disinda kalan, kullanilmayan): 3622 pand.

## Sanayi buurt'larinin B'deki payi

| | |
|---|---|
| Alan (B icinde) | 17.14 ha |
| Pand | 174 |
| Konut birimi iceren | 164 |
| Verblijfsobject | 673 |
| woonfunctie orani | 84.4% |

Bu binalar `context` rolundedir: catı gunes potansiyelleri **`indicative`**
etiketiyle hesaplanip ikizde gosterilir; enerji tuketimi alani
**"modellenmedi — endustriyel surec yuku acik veriyle bilinemez"** olarak
isaretlenir, bos birakilmaz.

## Status filtresi etkisi (Bolum 12.8 — sessiz atlama yasak)

| Katman | Dislanan kayit |
|---|---|
| pand | 47 |
| verblijfsobject | 668 |

Dahil/haric deger listeleri `config/acceptance_criteria.yml` ->
`stage_0_2.status_filter` altinda; degerler indirilen veriden dogrulanmistir (M-005).

## AGENTS.md Bolum 3 tahmini ile fark

Bolum 3, A icin **~600 x 600 m ve ~400-700 bina** ongoruyordu. Olculen:
**110 ha ve 1259 pand**
(2.3 kat).

**Bu bir basarisizlik degildir** — Bolum 3'un tahmini varsayimsaldi; A artik
resmi sinirdan turiyor. Fark, Bolum 3'un guncellenmesini gerektirir ve Asama 3-4
hesap yukunu dogrudan etkiler (bkz. P-001).

## Kapsama dogrulamasi

B tamamen indirilen bbox icinde; en dar kenar payi **0.0 m**.
Kapsama yetersiz olsaydi bu rapor uretilmezdi.
