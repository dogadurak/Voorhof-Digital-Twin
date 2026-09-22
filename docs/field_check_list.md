# Saha kontrol listesi — Voorhof

**Dolduracak:** kullanici · **Tarih:** _______ · **run_id:** `RUN-2026-09-22-028`
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
| **belirsiz konut blogu** | A'daki 3 buyuk konut blogu (412 konut VBO) | 3 | 2023'te bu bina mi vardi? **kat sayisi** |
| **buyuk ucus sonrasi** | Ayakizi >= 100 m2, ucustan sonra yapilmis (D-029) | 6 | 2023'te var miydi? **kat sayisi** |
| **kalibrasyon** | Kat yuksekligini olcmek icin (D-030/D-031) | 10 | **yalnizca kat sayisi** |
| **ATLA** | Gecersiz kilinan eski orneklem (D-031) — sayma | 5 | — |
| **sifir sinif-6 orneklemi** | AHN5'te cati noktasi olmayan yapilar (D-019) | 13 | bu ne? 2023'te var miydi? |

Toplam **35 bina**. Ayni bina birden fazla gruptaysa **tek satir**
yazildi.

**Kucuk ucus sonrasi yapilar (24 adet) bu listede YOKTUR** — D-029
geregi `footprint_only` kalirlar, kat sayilmaz.

---

## ⚠️ ONCE BUNU OKU — kat sayim kurali (D-030, sayimdan ONCE muhurlendi)

Bu kural **sen saymaya baslamadan once** `config/acceptance_criteria.yml`'ye
yazildi ve commit edildi (`f2667c1`). Sayim sonucuna gore degistirilemez.

| # | Kural | Not / gerekce |
|---|---|---|
| **R1** | Zemin kat DAHILDIR ve 1. kat sayilir. |  |
| **R2** | Bodrum (kelder) SAYILMAZ. | Olculen yukseklik (LiDAR) maaiveld USTUNU olcer; bodrum sayilirsa payda buyur ve kat yuksekligi YAPAY OLARAK DUSER. |
| **R3** | Yariya yakini zemin ustunde kalan kat (souterrain): pencere ALT kenari sokak kotunun USTUNDEYSE SAYILIR, degilse sayilmaz. | Sayildiysa NOT sutununa 'souterrain sayildi' yazilir. |
| **R4** | Egik cati altindaki hacim, cephede KENDI TAM BOY PENCERESI olan ve yanindaki katlarla ayni yukseklikte gorunen bir kat ise SAYILIR. Yalnizca dormer (dakkapel) veya cati penceresi varsa SAYILMAZ. | Her iki durumda da NOT sutununa 'cati kati: var/dormer/yok' yazilir. |
| **R5** | Asansor makine dairesi, merdiven kulesi, havalandirma, dakopbouw KAT SAYILMAZ. |  |
| **R6** | Kolonlar uzerinde bos birakilmis acik zemin kat 1 kat SAYILIR. | NOT sutununa 'pilotis' yazilir. |
| **R7** | Ust kat daha kucuk taban alanina sahipse (terugliggende bouwlaag / setback) yine 1 kat SAYILIR. | NOT sutununa 'cekme kat' yazilir. |
| **R8** | Kat sayisi ANA GIRISIN bulundugu cepheden sayilir. Baska bir cephede kat sayisi FARKLI gorunuyorsa fark NOT'a yazilir ve bina kalibrasyon orneklemINDEN CIKARILIR. | Voorhof duz arazidir; bu kural yine de yazildi cunku souterrain ve gomulu garaj ayni etkiyi uretir. Kalibrasyonda belirsiz bir bina, ortalamayi sessizce kaydirir. |
| **R9** | Bir BAG pand'i farkli yukseklikte bolumler iceriyorsa (L blok, alcak ek yapi) EN YUKSEK bolumun kat sayisi yazilir. | NOT'a 'N katli ek var' yazilir. |
| **R10** | Sayim yapilamiyorsa (Street View yok, agac/duvar kapatiyor, goruntu cok eski) kat sayisi BOS birakilir ve NOT'a "sayilamadi" yazilir. | Bolum 13.3: olculemeyen deger tahmin edilmez, bos birakilir. |
| **R11** | Street View goruntusunun TARIHI (ekranin kosesinde yazar) NOT sutununa yazilir. | Ucus sonrasi yapilarda kritik: 2023 oncesi bir goruntude bina henuz yoktur. Ayrica "2023'te var miydi" sorusunun cevabi goruntu tarihinden BAGIMSIZ okunamaz. |

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

## P-020 KARARA BAGLANDI (D-031) — orneklem yukseklik sinifina gore

Ilk muhurledigim **desil** kurali kendi amacini tutturamadi (M-016): desiller
**nufusu** izler, **araligi** degil. Uygun havuzun (514 bina) **%66'si**
5,7-6,0 m bandinda oldugu icin secilen 10 binanin 6'si ayni yukseklikteydi.

**Kullanici karari (2026-09-22):** yukseklik araligina gore tabakalama.
Gerekce: kalibrasyon asil **yuksek binalar** icin (3 konut blogu, okullar)
kullanilacak; yalnizca iki katlilardan turetilmis bir kat yuksekligi tam
ihtiyac duyulan yerde yanlis olur.

Havuzun olculen dagilimi ve gecerli orneklem:

| h sinifi | 3 m | 6 m | 8 m | 9 m | 11 m | 14 m | 26 m | 35 m | 37 m |
|---|---|---|---|---|---|---|---|---|---|
| havuzdaki bina | 3 | 337 | 97 | 46 | 5 | 4 | 9 | 3 | 10 |
| orneklemde | 1 | 2 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |

Eski desil orneklemi **silinmedi**, `SUPERSEDED` olarak duruyor
(`reports/storey_height_calibration_superseded_decile.csv`). Yalnizca eski
orneklemde olan binalar bu listede **ATLA** etiketiyle en sonda; sayma.

## Ek: kat yuksekligi bina tipine gore degisiyor mu? (D-031)

Sonuc **iki grupta ayri** raporlanacak: `laag` (kat <= 4, sira ev/portiekflat)
ve `hoog` (kat >= 5, galerijflat/hoogbouw). Tip bazli deger ancak **her iki
grupta da n >= 3** ve **gruplar arasi fark, binalar arasi sacilmadan buyuk**
ise kullanilir; aksi halde tek ortalama kullanilir ve fark **sinirlama**
olarak yazilir. Bu kural da **sayimdan once** muhurlendi.

---

## Tablo

**Doldurulacak dort sutun sagda.** Doldurma kilavuzu tablonun altinda.

| # | grup | bag_id | m2 | bouwjaar | gebruiksdoel | lat, lon | harita | GOZLEM | 2023'te var miydi | KAT | NOT |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | belirsiz konut blogu | `0503100000037335` | 1962 | 2023 | woonfunctie | 51.999653, 4.359225 | [SV](https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=51.9996530,4.3592248) · [Harita](https://www.google.com/maps/search/?api=1&query=51.9996530,4.3592248) |  |  |  |  |
| 2 | belirsiz konut blogu | `0503100000037336` | 1252 | 2023 | bijeenkomstfunctie,overige gebruiksfunctie,woonfunctie | 51.996568, 4.353681 | [SV](https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=51.9965683,4.3536810) · [Harita](https://www.google.com/maps/search/?api=1&query=51.9965683,4.3536810) |  |  |  |  |
| 3 | sifir sinif-6 orneklemi + belirsiz konut blogu | `0503100000038177` | 820 | 2025 | winkelfunctie,woonfunctie | 51.995368, 4.353292 | [SV](https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=51.9953681,4.3532921) · [Harita](https://www.google.com/maps/search/?api=1&query=51.9953681,4.3532921) |  |  |  |  |
| 4 | buyuk ucus sonrasi | `0503100000038250` | 2112 | 2024 | onderwijsfunctie | 51.998034, 4.347362 | [SV](https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=51.9980344,4.3473621) · [Harita](https://www.google.com/maps/search/?api=1&query=51.9980344,4.3473621) | — |  |  |  |
| 5 | sifir sinif-6 orneklemi + buyuk ucus sonrasi | `0503100000038184` | 997 | 2023 | onderwijsfunctie | 51.989415, 4.353578 | [SV](https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=51.9894151,4.3535777) · [Harita](https://www.google.com/maps/search/?api=1&query=51.9894151,4.3535777) |  |  |  |  |
| 6 | buyuk ucus sonrasi | `0503100000038253` | 496 | 2025 | woonfunctie | 52.002753, 4.357402 | [SV](https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=52.0027531,4.3574025) · [Harita](https://www.google.com/maps/search/?api=1&query=52.0027531,4.3574025) | — |  |  |  |
| 7 | buyuk ucus sonrasi | `0503100000038699` | 340 | 2026 | kantoorfunctie,woonfunctie | 52.001612, 4.357907 | [SV](https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=52.0016119,4.3579068) · [Harita](https://www.google.com/maps/search/?api=1&query=52.0016119,4.3579068) | — |  |  |  |
| 8 | buyuk ucus sonrasi | `0503100000038426` | 337 | 2026 | kantoorfunctie,woonfunctie | 52.001461, 4.358039 | [SV](https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=52.0014607,4.3580386) · [Harita](https://www.google.com/maps/search/?api=1&query=52.0014607,4.3580386) | — |  |  |  |
| 9 | buyuk ucus sonrasi | `0503100000040432` | 298 | 2026 | woonfunctie | 52.002171, 4.358270 | [SV](https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=52.0021712,4.3582695) · [Harita](https://www.google.com/maps/search/?api=1&query=52.0021712,4.3582695) | — |  |  |  |
| 10 | kalibrasyon | `0503100000000022` | 853 | 1962 | woonfunctie | 51.999907, 4.349070 | [SV](https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=51.9999067,4.3490703) · [Harita](https://www.google.com/maps/search/?api=1&query=51.9999067,4.3490703) | — | — |  |  |
| 11 | kalibrasyon | `0503100000023053` | 676 | 1961 | woonfunctie | 51.999876, 4.352619 | [SV](https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=51.9998760,4.3526192) · [Harita](https://www.google.com/maps/search/?api=1&query=51.9998760,4.3526192) | — | — |  |  |
| 12 | kalibrasyon | `0503100000019685` | 323 | 1971 | woonfunctie | 51.992038, 4.354816 | [SV](https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=51.9920378,4.3548159) · [Harita](https://www.google.com/maps/search/?api=1&query=51.9920378,4.3548159) | — | — |  |  |
| 13 | kalibrasyon | `0503100000019378` | 209 | 1968 | woonfunctie | 51.989944, 4.357364 | [SV](https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=51.9899438,4.3573643) · [Harita](https://www.google.com/maps/search/?api=1&query=51.9899438,4.3573643) | — | — |  |  |
| 14 | kalibrasyon | `0503100000026771` | 62 | 1966 | woonfunctie | 51.993278, 4.352712 | [SV](https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=51.9932783,4.3527120) · [Harita](https://www.google.com/maps/search/?api=1&query=51.9932783,4.3527120) | — | — |  |  |
| 15 | kalibrasyon | `0503100000023497` | 61 | 1969 | woonfunctie | 51.997559, 4.359394 | [SV](https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=51.9975592,4.3593943) · [Harita](https://www.google.com/maps/search/?api=1&query=51.9975592,4.3593943) | — | — |  |  |
| 16 | kalibrasyon | `0503100000026852` | 60 | 1965 | woonfunctie | 51.994497, 4.351481 | [SV](https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=51.9944974,4.3514812) · [Harita](https://www.google.com/maps/search/?api=1&query=51.9944974,4.3514812) | — | — |  |  |
| 17 | kalibrasyon | `0503100000010265` | 53 | 1969 | woonfunctie | 51.990137, 4.353666 | [SV](https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=51.9901372,4.3536655) · [Harita](https://www.google.com/maps/search/?api=1&query=51.9901372,4.3536655) | — | — |  |  |
| 18 | kalibrasyon | `0503100000019104` | 53 | 1966 | woonfunctie | 51.991486, 4.359850 | [SV](https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=51.9914856,4.3598500) · [Harita](https://www.google.com/maps/search/?api=1&query=51.9914856,4.3598500) | — | — |  |  |
| 19 | kalibrasyon | `0503100000018892` | 52 | 1966 | woonfunctie | 51.992115, 4.361096 | [SV](https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=51.9921151,4.3610961) · [Harita](https://www.google.com/maps/search/?api=1&query=51.9921151,4.3610961) | — | — |  |  |
| 20 | sifir sinif-6 orneklemi | `0503100000041285` | 1665 | 2026 | onderwijsfunctie,sportfunctie | 51.994720, 4.350444 | [SV](https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=51.9947202,4.3504437) · [Harita](https://www.google.com/maps/search/?api=1&query=51.9947202,4.3504437) |  |  |  |  |
| 21 | sifir sinif-6 orneklemi | `0503100000039604` | 14 | 2020 | — | 51.990788, 4.362701 | [SV](https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=51.9907885,4.3627008) · [Harita](https://www.google.com/maps/search/?api=1&query=51.9907885,4.3627008) |  |  |  |  |
| 22 | sifir sinif-6 orneklemi | `0503100000039608` | 14 | 2001 | — | 51.990575, 4.361834 | [SV](https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=51.9905746,4.3618338) · [Harita](https://www.google.com/maps/search/?api=1&query=51.9905746,4.3618338) |  |  |  |  |
| 23 | sifir sinif-6 orneklemi | `0503100000039603` | 8 | 1988 | — | 51.990791, 4.362820 | [SV](https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=51.9907913,4.3628204) · [Harita](https://www.google.com/maps/search/?api=1&query=51.9907913,4.3628204) |  |  |  |  |
| 24 | sifir sinif-6 orneklemi | `0503100000039621` | 5 | 1998 | — | 51.992559, 4.361258 | [SV](https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=51.9925590,4.3612581) · [Harita](https://www.google.com/maps/search/?api=1&query=51.9925590,4.3612581) |  |  |  |  |
| 25 | sifir sinif-6 orneklemi | `0503100000039618` | 5 | 1997 | — | 51.992572, 4.361581 | [SV](https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=51.9925718,4.3615815) · [Harita](https://www.google.com/maps/search/?api=1&query=51.9925718,4.3615815) |  |  |  |  |
| 26 | sifir sinif-6 orneklemi | `0503100000038679` | 4 | 2007 | — | 51.993098, 4.361731 | [SV](https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=51.9930978,4.3617315) · [Harita](https://www.google.com/maps/search/?api=1&query=51.9930978,4.3617315) |  |  |  |  |
| 27 | sifir sinif-6 orneklemi | `0503100000038260` | 4 | 2023 | — | 51.999812, 4.351567 | [SV](https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=51.9998121,4.3515669) · [Harita](https://www.google.com/maps/search/?api=1&query=51.9998121,4.3515669) |  |  |  |  |
| 28 | sifir sinif-6 orneklemi | `0503100000039626` | 3 | 2009 | — | 51.994442, 4.360563 | [SV](https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=51.9944424,4.3605626) · [Harita](https://www.google.com/maps/search/?api=1&query=51.9944424,4.3605626) |  |  |  |  |
| 29 | sifir sinif-6 orneklemi | `0503100000039629` | 3 | 2022 | — | 51.994421, 4.360254 | [SV](https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=51.9944209,4.3602540) · [Harita](https://www.google.com/maps/search/?api=1&query=51.9944209,4.3602540) |  |  |  |  |
| 30 | sifir sinif-6 orneklemi | `0503100000039630` | 2 | 2016 | — | 51.994447, 4.360078 | [SV](https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=51.9944466,4.3600779) · [Harita](https://www.google.com/maps/search/?api=1&query=51.9944466,4.3600779) |  |  |  |  |
| 31 | **ATLA** (superseded) | `0503100000019296` | 302 | 1971 | woonfunctie | 51.989955, 4.355578 | [SV](https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=51.9899548,4.3555781) · [Harita](https://www.google.com/maps/search/?api=1&query=51.9899548,4.3555781) | — | — |  |  |
| 32 | **ATLA** (superseded) | `0503100000018905` | 69 | 1966 | woonfunctie | 51.991066, 4.362030 | [SV](https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=51.9910662,4.3620304) · [Harita](https://www.google.com/maps/search/?api=1&query=51.9910662,4.3620304) | — | — |  |  |
| 33 | **ATLA** (superseded) | `0503100000001547` | 53 | 1969 | woonfunctie | 51.990182, 4.353637 | [SV](https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=51.9901824,4.3536367) · [Harita](https://www.google.com/maps/search/?api=1&query=51.9901824,4.3536367) | — | — |  |  |
| 34 | **ATLA** (superseded) | `0503100000019105` | 53 | 1966 | woonfunctie | 51.991463, 4.359768 | [SV](https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=51.9914632,4.3597678) · [Harita](https://www.google.com/maps/search/?api=1&query=51.9914632,4.3597678) | — | — |  |  |
| 35 | **ATLA** (superseded) | `0503100000018987` | 52 | 1966 | woonfunctie | 51.991648, 4.361646 | [SV](https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=51.9916485,4.3616460) · [Harita](https://www.google.com/maps/search/?api=1&query=51.9916485,4.3616460) | — | — |  |  |

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
