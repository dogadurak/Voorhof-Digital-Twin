# T3 (okul) kalibrasyon secimi — amac iddiasi TUTMADI · ONERI

> **Veri donemi:** geometri AHN5 2023-02-08/14 · oznitelik BAG 2026-09 (D-020).
> Muhurlu kural (D-035, a20b15f) uygulandi ve **degistirilmedi**. Bu belge yalnizca kullanicinin SAYIMDAN ONCE karar vermesi icindir (M-016). Kat sayisi henuz yok; hicbir kat yuksekligi hesaplanmadi.

run_id: `RUN-2026-09-27-006` · git_commit: `a20b15f-dirty` · calistirma (UTC): 2026-09-27T08:05:03Z

## Ne oldu

Muhurlu secim her h-tertilinden bir okul aldi. Uygun havuz 8 okul; bunlarin 7'si 3,9-5,9 m (tek katli olcekte), yalnizca biri daha yuksek. Uc tertil de tek katli okullardan olustu; amac iddiasi (secilenlerin araligi havuz p10-p90'in >= yarisi) TUTMADI.

**Neden onemli (CIKARIM):** estimated_lod1 hedefi olan iki yeni okulun kat sayisi bilinmiyor; cok katli iseler tek katli okullardan turetilen deger onlari temsil etmez. Ayrica tek katli binada `known_bias` (plint + parapet / kat sayisi) en buyuktur.

C5 (duz cati) filtresi 9 okulu eledi; bunlarin 6'i h >= 7 m.

## T3 havuzunun tamami (h'ye gore)

| bag_id | alan | bouwjaar | ayakizi m2 | h (m) | span (m) | durum | muhurlu secimde |
|---|---|---|---|---|---|---|---|
| `0503100000002019` | B | 1989 | 583 | 17.100 | 3.900 | C5 egik/cok seviyeli cati (span >= 1,5) |  |
| `0503100000010890` | A | 1964 | 1415 | 12.900 | 6.000 | C5 egik/cok seviyeli cati (span >= 1,5) |  |
| `0503100000035052` | B | 2017 | 3327 | 12.700 | 1.500 | C5 egik/cok seviyeli cati (span >= 1,5) |  |
| `0503100000021574` | B | 1976 | 6004 | 10.100 | 7.600 | C5 egik/cok seviyeli cati (span >= 1,5) |  |
| `0503100000018964` | A | 1965 | 1614 | 9.500 | 0.100 | UYGUN | YEDEK |
| `0503100000000070` | B | 1969 | 1892 | 7.500 | 3.600 | C5 egik/cok seviyeli cati (span >= 1,5) |  |
| `0503100000020130` | A | 1969 | 1325 | 7.200 | 3.700 | C5 egik/cok seviyeli cati (span >= 1,5) |  |
| `0503100000002034` | A | 2020 | 1296 | 4.800 | 8.300 | C5 egik/cok seviyeli cati (span >= 1,5) |  |
| `0503100000018689` | A | 1967 | 465 | 4.300 | 0.100 | UYGUN | ASIL |
| `0503100000025340` | B | 1974 | 1251 | 4.300 | 0.100 | UYGUN | ASIL |
| `0503100000009020` | A | 1967 | 895 | 4.100 | 0.100 | UYGUN | YEDEK |
| `0503100000009022` | A | 1969 | 583 | 4.000 | 0.200 | UYGUN |  |
| `0503100000000145` | B | 1966 | 2021 | 4.000 | 1.300 | UYGUN |  |
| `0503100000001932` | A | 1969 | 583 | 3.900 | 0.000 | UYGUN | YEDEK |
| `0503100000000195` | A | 1969 | 683 | 3.900 | 7.700 | C5 egik/cok seviyeli cati (span >= 1,5) |  |
| `0503100000030808` | A | 1967 | 833 | 3.900 | 0.000 | UYGUN | ASIL |
| `0503100000025343` | A | 1992 | 260 | 3.700 | 1.500 | C5 egik/cok seviyeli cati (span >= 1,5) |  |
| `0503100000038184` | A | 2023 | 997 | — | — | C3 ucus sonrasi/yeniden yapim; olculemedi |  |
| `0503100000038250` | B | 2024 | 2112 | — | — | C3 ucus sonrasi/yeniden yapim; olculemedi |  |
| `0503100000041285` | A | 2026 | 1665 | — | — | C3 ucus sonrasi/yeniden yapim; olculemedi |  |

## Alternatifler (ONERI — hicbiri gecerli degil, kullanici secer)

- **(a) Muhurlu secimi koru.** Sonuc 'tek katli okul' degeri olarak raporlanir; hedef okullar cok katliysa bu SINIRLAMA olur.
- **(b) Uygun havuzdan min / medyan / maks h** (C5 korunur): `0503100000001932` (3.900 m), `0503100000009020` (4.100 m), `0503100000018964` (9.500 m).
- **(c) C5'i T3 icin gevset** (egik catili okullar da girer). DIKKAT: C5'in gerekcesi egik catinin h/kat'i SISTEMATIK buyutmesidir; gevsetmek bu sapmayi geri getirir.

Ajanin onerisi: **(b)** — C5'in gerekcesini korur, araligi kapsar. Karar verilince yeni bir D kaydi + ayri commit; sayimdan ONCE.

---

# T2 (yeni konut) — iddia TUTTU ama secilenler hedeflere BENZEMIYOR · ONERI

Uygun T2 havuzu 174 bina; ayakizi p10/medyan/p90 = 42 / 58 / 75 m2 (tek tek kayitli sira evler). >= 100 m2 olan: **10**.

Muhurlu secimin asillari: `0503100000036839` (20 m2, h 3.500 m), `0503100000033247` (41 m2, h 8.900 m), `0503100000034895` (1166 m2, h 43.000 m).

estimated_lod1 hedeflerinden T2 olanlarin ayakizi 298-496 m2 (post_flight_buildings.csv). Muhurlu amac iddiasi yalnizca h yayilimini olcuyordu; hedef benzerligini olcmuyordu (ajanin tespiti). Siralama olcutu (sinif 6 yogunlugu) kucuk ayakizlerini one cikariyor — kenar etkisi olabilir (CIKARIM, olculmedi).

**(b') ONERI:** ayni tertil kurali, havuz **>= 100 m2** ile sinirli (D-029'daki 'buyuk' esigi — yeni sayi degil):

| bag_id | alan | bouwjaar | ayakizi m2 | gebruiksdoel | h (m) | alternatifte |
|---|---|---|---|---|---|---|
| `0503100000024118` | B | 2007 | 900 | gezondheidszorgfunctie,woonfunctie | 7.700 |  |
| `0503100000034482` | A | 2014 | 4536 | woonfunctie | 15.500 |  |
| `0503100000032908` | A | 2009 | 502 | overige gebruiksfunctie,woonfunctie | 17.300 | ASIL |
| `0503100000019704` | B | 2005 | 375 | woonfunctie | 20.900 |  |
| `0503100000019703` | B | 2005 | 376 | woonfunctie | 21.000 |  |
| `0503100000031229` | B | 2005 | 402 | kantoorfunctie,woonfunctie | 21.100 |  |
| `0503100000038135` | B | 2022 | 598 | winkelfunctie,woonfunctie | 23.800 | ASIL |
| `0503100000035282` | A | 2016 | 959 | winkelfunctie,woonfunctie | 42.900 |  |
| `0503100000034895` | A | 2015 | 1166 | overige gebruiksfunctie,winkelfunctie,woonfunctie | 43.000 | ASIL |
| `0503100000035763` | A | 2018 | 1249 | bijeenkomstfunctie,woonfunctie | 43.100 |  |

DIKKAT: (b') secilirse bu binalar saha listesine EKLENMELIDIR (su an listede degiller) ve karar sayimdan ONCE verilir.
