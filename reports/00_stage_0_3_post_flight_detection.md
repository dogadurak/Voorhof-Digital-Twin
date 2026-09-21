# Ucus sonrasi bina tespiti — A ve B alanlari

**Karar D-022** · run_id `RUN-2026-09-21-023` · muhur commit'i `d4cf95b`

> **VERI DONEMI (D-020).** Geometri AHN5 **2023-02-08 / 02-14**; BAG
> oznitelikleri **2026-09**. Arada 3,5 yil var.

Esikler config'ten okundu ve bu hesaptan **once** muhurlendi:
**K1 <= 0.02** · **K2 >= 0.7** · **K3 < 1.0 p/m2** · **R1 bouwjaar >= 2023**

Kapsam: **B alanindaki 4,035 pand** (status filtreli, centroid kurali);
bunlarin **1,259**'i A alaninda. Toplam ayakizi 600,499 m2.

## 1. Sonuc — HEM SAYI HEM ALAN (Bolum 14.6)

| Grup | Bina | Bina payi | Alan m2 | Alan payi |
|---|---|---|---|---|
| **Ucus sonrasi aday** (K1+K2+K3) | **30** | %0.74 | 5,870 | **%0.98** |
| **Supheli** (3 kosuldan tam 2'si) | **60** | %1.49 | 2,137 | %0.36 |
| **Olasi yeniden yapim** (R1) | **50** | %1.24 | 10,377 | %1.73 |

## 2. Ucus sonrasi adaylar

Kullanim islevi:

| gebruiksdoel | Bina | Pay |
|---|---|---|
| woonfunctie | 20 | %66.7 |
| (islev yok) | 6 | %20.0 |
| onderwijsfunctie | 2 | %6.7 |
| kantoorfunctie,woonfunctie | 2 | %6.7 |

Etkiye (alana) gore en buyuk 5:

| # | bag_id | m2 | alan | gebruiksdoel | bouwjaar | sinif 6 orani | sinif 6 kapsama |
|---|---|---|---|---|---|---|---|
| 1 | `0503100000038250` | 2,111.9 | B | onderwijsfunctie | 2024 | 0.000 | 0.000 |
| 2 | `0503100000038184` | 996.5 | A | onderwijsfunctie | 2023 | 0.000 | 0.000 |
| 3 | `0503100000038253` | 496.1 | B | woonfunctie | 2025 | 0.000 | 0.000 |
| 4 | `0503100000038699` | 340.0 | B | kantoorfunctie,woonfunctie | 2026 | 0.000 | 0.000 |
| 5 | `0503100000038426` | 336.7 | B | kantoorfunctie,woonfunctie | 2026 | 0.000 | 0.000 |

Tam liste: `reports/post_flight_buildings.csv`

## 3. Supheli (3 kosuldan tam 2'si) — KARAR VERILMEDI

| gebruiksdoel | Bina | Pay |
|---|---|---|
| (islev yok) | 59 | %98.3 |
| onderwijsfunctie,sportfunctie | 1 | %1.7 |

Etkiye gore en buyuk 5:

| # | bag_id | m2 | alan | gebruiksdoel | bouwjaar | sinif 6 orani | sinif 6 kapsama |
|---|---|---|---|---|---|---|---|
| 1 | `0503100000041285` | 1,665.0 | A | onderwijsfunctie,sportfunctie | 2026 | 0.000 | 0.000 |
| 2 | `0503100000038212` | 28.5 | A | (islev yok) | 2023 | 0.000 | 0.000 |
| 3 | `0503100000038664` | 25.3 | B | (islev yok) | 2022 | 0.000 | 0.000 |
| 4 | `0503100000038258` | 24.2 | A | (islev yok) | 2023 | 0.000 | 0.000 |
| 5 | `0503100000039606` | 15.4 | A | (islev yok) | 2002 | 0.000 | 0.000 |

Hangi kosullarin saglandigi CSV'de sutun olarak: `post_flight_suspects.csv`

## 4. Olasi yeniden yapim (sloop-nieuwbouw) — KARAR VERILMEDI

`bouwjaar >= 2023` **VE** ucus sonrasi aday **degil**. Bu binalarda LiDAR
**eski catiyi** gormus olabilir; Asama 1'de eski geometri yeni binaya
giydirilirse **sessiz hata** olur (D-022).

**39 binada `bouwjaar == 2023` ve bu BELIRSIZDIR:** BAG
yalnizca yil verir, ucus Subat 2023'tedir; bina ucustan once de sonra da
yapilmis olabilir.

| gebruiksdoel | Bina | Pay |
|---|---|---|
| woonfunctie | 26 | %52.0 |
| (islev yok) | 14 | %28.0 |
| kantoorfunctie,woonfunctie | 3 | %6.0 |
| bijeenkomstfunctie,overige gebruiksfunctie,woonfunctie | 2 | %4.0 |
| gezondheidszorgfunctie,woonfunctie | 1 | %2.0 |
| overige gebruiksfunctie | 1 | %2.0 |
| kantoorfunctie,winkelfunctie,woonfunctie | 1 | %2.0 |
| winkelfunctie,woonfunctie | 1 | %2.0 |

Etkiye gore en buyuk 5:

| # | bag_id | m2 | alan | gebruiksdoel | bouwjaar | sinif 6 orani | sinif 6 kapsama |
|---|---|---|---|---|---|---|---|
| 1 | `0503100000037335` | 1,961.8 | A | woonfunctie | 2023 | 0.744 | 0.859 |
| 2 | `0503100000041285` | 1,665.0 | A | onderwijsfunctie,sportfunctie | 2026 | 0.000 | 0.000 |
| 3 | `0503100000037336` | 1,251.6 | A | bijeenkomstfunctie,overige gebruiksfunctie,woonfunctie | 2023 | 0.565 | 0.994 |
| 4 | `0503100000037573` | 1,078.2 | B | bijeenkomstfunctie,overige gebruiksfunctie,woonfunctie | 2024 | 0.754 | 1.000 |
| 5 | `0503100000038177` | 819.9 | A | winkelfunctie,woonfunctie | 2025 | 0.785 | 0.988 |

Tam liste: `reports/rebuild_suspects.csv`

**`class6_footprint_coverage` nasil okunur:** ayakizi icindeki 2 m hucrelerden
icinde en az bir sinif 6 noktasi bulunanlarin orani. **Dusuk deger**, eski
catinin yeni ayakizini ortmedigini — yani ayakizinin degistigini — dusundurur.
**SINIRLAMA:** bitisik nizamda komsu binanin cati noktalari ayakizina tasip
orani **yukseltebilir**; Voorhof'ta bitisik nizam yaygindir. Bu metrik tek
basina karar vermez (D-022).

## 5. Ne yapilmadi

- Bu rapor **hicbir bina icin karar vermez**. Ucus sonrasi adaylar D-020
  geregi `estimated_lod1` veya `footprint_only` olur; supheli ve yeniden
  yapim listeleri **yalnizca uyaridir**.
- Yeniden yapim listesi **gorsel olarak dogrulanmamistir** (Bolum 12.13).
  Amacli ornek `0503100000038177` gorsel orneklemdedir.
