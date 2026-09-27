# Cephe noktasi sinif olcumu — AHN5 (Asama 1 hazirlik)

> **Veri donemi:** geometri AHN5 2023-02-08/14 · oznitelik BAG 2026-09 (D-020).
> **Yontem:** `config/acceptance_criteria.yml` -> `facade_class_measurement`, olcumden ONCE muhurlendi (commit 4b6ad61, b353121). Bu rapor o yontemi DEGISTIRMEDEN uygular.
> **Ne dogrulaniyor:** WP1 (2024) calisma raporundaki AHN5 sinif taniminin bizim veride gecerliligi. Referans bir BELGE tanimidir; bu olcum bagimsiz bir ground truth DEGILDIR (ayni AHN5 noktalari).

run_id: `RUN-2026-09-26-008` · git_commit: `7b2ca3f-dirty` · calistirma (UTC): 2026-09-27T07:39:54Z

## Sonuc (muhurlu okuma kurali)

**MIXED**

| Olcu | Deger | Muhurlu esik |
|---|---|---|
| Kontrol (cati) bolgesi sinif 6 payi | 0.975 | >= 0.8 (yorum sarti) |
| Cephe bolgesi sinif 6 payi — ic yari (d<0) | 0.252 | WP1: < 0.2 · AHN4: > 0.5 |
| Cephe bolgesi sinif 6 payi — dis yari (d>0) | 0.209 | WP1: < 0.2 · AHN4: > 0.5 |
| Sinif 1 noktalarinin duvar cizgisinde (abs(d) <= 0.2 m) payi | 0.762 | WP1: > 0.6 |
| Sinif 6 noktalarinin duvar cizgisinde payi | 0.514 | — (yalniz raporlanir) |
| Duzgun dagilimda beklenen duvar payi (yaklasik, 0.2/0.5) | 0.40 | — (baglam) |

## Kapsam

- Yukseklik tablosunda 4,035 bina; secilen **1,639**.
- Dislanan: h < 6.0 m: 2,052 · cephe bolgesi < 2.0 m: 73 · BAG geometrisi bulunamadi: 0 · yuksekligi olculemeyen binalar zaten tabloda bos (kapsam disi).
- Komsu ayakizi cikarilan bina: 1,497 / 1,639.
- Cephe bolgesinde hic noktasi olmayan bina: 0.

## Havuzlanmis sinif dagilimi (nokta agirlikli)

| Bolge | toplam | sinif 1 | sinif 2 | sinif 6 | sinif 9 | sinif 14 | sinif 26 | diger |
|---|---|---|---|---|---|---|---|---|
| cephe — ic yari | 1,254,658 | 938,638 (0.748) | 34 (0.000) | 315,978 (0.252) | 0 (0.000) | 0 (0.000) | 8 (0.000) | 0 |
| cephe — dis yari | 810,474 | 640,051 (0.790) | 923 (0.001) | 169,475 (0.209) | 0 (0.000) | 0 (0.000) | 25 (0.000) | 0 |
| cephe — toplam | 2,065,132 | 1,578,689 (0.764) | 957 (0.000) | 485,453 (0.235) | 0 (0.000) | 0 (0.000) | 33 (0.000) | 0 |
| duvar cizgisi abs(d)<=0.2 | 1,452,473 | 1,202,491 (0.828) | 367 (0.000) | 249,602 (0.172) | 0 (0.000) | 0 (0.000) | 13 (0.000) | 0 |
| KONTROL: cati | 9,190,209 | 229,283 (0.025) | 0 (0.000) | 8,960,926 (0.975) | 0 (0.000) | 0 (0.000) | 0 (0.000) | 0 |

## Bina basina sinif 6 payi (sayiya gore)

Noktasi olan 1,639 bina: medyan 0.397 · p10 0.000 · p90 0.733.

Cephe bolgesinde en cok noktasi olan 5 bina (etkiye gore, Bolum 14.6):

| bag_id | alan | h (m) | cephe noktasi | sinif 6 payi | sinif 1 payi |
|---|---|---|---|---|---|
| `0503100000019841` | A | 51.100 | 68,898 | 0.156 | 0.844 |
| `0503100000019818` | B | 14.100 | 47,863 | 0.203 | 0.797 |
| `0503100000000020` | A | 50.600 | 45,749 | 0.046 | 0.954 |
| `0503100000019845` | A | 51.100 | 40,281 | 0.008 | 0.992 |
| `0503100000000010` | B | 12.400 | 35,901 | 0.267 | 0.733 |

## Okuma kurali (muhurlu metin, degistirilmedi)

- WP1_AHN5_DEFINITION_HOLDS: Cephe bolgesinde havuzlanmis sinif 6 payi ic VE dis yarida < 0,20 VE sinif 1 noktalarinin wall_concentration degeri > 0,60.
- AHN4_DEFINITION_HOLDS: Havuzlanmis sinif 6 payi ic VE dis yarida > 0,50.
- MIXED: Diger her durum — sonuc olduğu gibi raporlanir, yorum kullaniciya birakilir.
- Kontrol sarti: Kontrol bolgesinde sinif 6 payi < 0,80 ise yorum YAPILMAZ (UNINTERPRETABLE): sinif eslemesi beklenenden farkli demektir.

## Sinirlamalar

- Sinif 1 AHN5'te bitki ortusunu da icerir. Duvara yakin agac/cali noktalari cephe bolgesine dusebilir; duvar yogunlasmasi olcusu bunu kismen ayirir, tamamen ayiramaz.
- BAG ayakizi bovenaanzicht (ust gorunus) sinirdir; sacak tasmasi olan binalarda duvar ayakizinin ICINDE kalir. Ic/dis yari bu yuzden ayri raporlanir.
- Balkon, galeri (galerijflat) ve sacak noktalari cephe bolgesine duser; bunlarin 'cati' mi 'cephe' mi sayildigi WP1'de tanimli degildir.
- Iki secili binanin bantlari (ayakizlari disinda) cakisabilir; o noktalar iki binaya da sayilir.
- Esikler (0,20 / 0,50 / 0,60 / 0,80) ajanin on-kaydidir, bir belgeden alinmamistir.
- Bu olcum AHN5'in BESTEK'ini degil, calisma raporundaki tanimi sinar; bestek okunmadi.
