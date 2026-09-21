# Sinif 6 orani sifir cikan BUYUK yapilarin incelemesi

**Tarih:** 2026-09-21 · **Asama:** 0.3 · **Karar:** D-018
**Tetikleyen:** Kullanici, "sifir grubu = kucuk yardimci yapilar" genellemesinin
iki buyuk bina icin tutmadigini tespit etti.

---

## 0. Once bir duzeltme: bu binalar KONUT DEGIL

Onceki raporda bu iki yapi "konut: evet" olarak listelendi. **Bu yanlisti ve
hata bendeydi.** CSV'deki `has_dwellings` sutunu aslinda
`aantal_verblijfsobjecten > 0` olmasini olcuyordu; bir verblijfsobject ise okul,
dukkan veya ofis de olabilir. Sutun `has_verblijfsobject` olarak duzeltildi ve
gercek kullanim islevi (`gebruiksdoel`) ayri bir sutun olarak eklendi
(MISTAKES.md **M-010**).

Ikisi de **okuldur**:

| bag_id | gebruiksdoel |
|---|---|
| `0503100000038184` | `onderwijsfunctie` |
| `0503100000041285` | `onderwijsfunctie,sportfunctie` |

Enerji analizi acisindan onemli olduklari dogrudur — ama konut stogu olarak
degil, **konut disi buyuk tuketici** olarak.

---

## 1. BAG oznitelikleri

| | `0503100000038184` | `0503100000041285` |
|---|---|---|
| bouwjaar | **2023** | **2026** |
| status | Pand in gebruik | **Pand in gebruik (niet ingemeten)** |
| gebruiksdoel | onderwijsfunctie | onderwijsfunctie, sportfunctie |
| oppervlakte (BAG) | 978 m2 | 1.275-1.646 m2 |
| ayakizi (geometrik) | 996,5 m2 | 1.665,0 m2 |
| VBO sayisi | 1 | 3 |

**`niet ingemeten` (041285):** geometri henuz olculmemistir, yani ayakizi
poligonu **gecicidir**. Asama 1'de bu binanin sinirina guvenilemez.

**Son mutasyon tarihi — elimizdeki veriden okunamiyor.** Dogrulandi
(DATA_LOG.md oznitelik kaydi, M-005):

- **PDOK BAG WFS `bag:pand`** yalnizca **8** oznitelik donuyor:
  `aantal_verblijfsobjecten, bouwjaar, gebruiksdoel, identificatie,
  oppervlakte_max, oppervlakte_min, rdf_seealso, status`.
  `documentdatum` **yok**.
- **3DBAG** bu alanlari tasiyor (`documentdatum`, `voorkomenidentificatie`,
  `begingeldigheid`, `tijdstipregistratie`, `oorspronkelijkbouwjaar` — 62
  oznitelik icinde). **Ama bu iki bina 3DBAG'de yok** (bkz. Bolum 4), yani
  bu yol da kapali.

Tahmin yazilmamistir. Mutasyon tarihi gerekirse **BAG Individuele
Bevragingen API**'si ayri bir veri kaynagi olarak eklenmelidir; bu Bolum
12.11 geregi **kullanici kararidir** (P-013).

**Not:** B alanindaki 7.704 pandin yalnizca **4**'u `Pand in gebruik (niet
ingemeten)` statusundedir; `0503100000041285` bunlardan biridir.

---

## 2. AHN5 ucus tarihi

**2023-02-08 – 2023-02-14 UTC** (kaartblad 37EN1, alt-fayans 19 ve 20).

**Nasil olculdu:** LAZ nokta kayitlarindaki `gps_time` alanindan.
`global_encoding` bit 0 = 0, yani baslik "GPS hafta zamani" diyor — **ama bu
bayrak yanlistir**: degerler 359.859.899 – 360.425.735 araligindadir ve hafta
zamani en fazla 604.800 olabilir. `lasinfo` da ayni celiskiyi kendi uyarisiyla
bildiriyor:

> `WARNING: range violates GPS week time specified by global encoding bit 0`

Degerler **Adjusted Standard GPS Time**'dir (gercek deger + 10^9). Donusum
(GPS epoch 1980-01-06, 18 artik saniye) Subat 2023 veriyor; bu, Delft icin
bilinen AHN5 kampanyasiyla (2023) tutarlidir.

> Ilk hesabimda +10^9 ofsetini uygulamadim ve **1991** sonucu cikti. Sonuc
> bariz imkansiz oldugu icin yakalandi ve **raporlanmadi**.

**Ucusun kis ayinda olmasi onemlidir:** Subat = yaprak dokumu donemi. Yani
"agac ortusu catiyi kapatti" aciklamasi bu veri icin zaten **en zayif oldugu
donemde** olculmustur.

---

## 3. Ayakizi icindeki noktalarin sinif ve yukseklik dagilimi

Yerel maaiveld (sinif 2) medyani: **-1,23 m NAP** (041285 icin -1,37 m).

### 3.1 `0503100000038184` — 81.963 nokta

| Sinif | Nokta | Pay |
|---|---|---|
| **2 (Maaiveld)** | 81.067 | **%98,9** |
| 1 (Overig) | 896 | %1,1 |
| 6 (Bebouwing) | **0** | **%0,0** |

| Maaiveld ustu yukseklik | Nokta | Pay |
|---|---|---|
| **zemin seviyesi (< 0,5 m)** | 81.081 | **%98,9** |
| 0,5-3 m | 0 | %0,0 |
| 3-8 m | 586 | %0,7 |
| > 8 m | 296 | %0,4 |

Medyan yukseklik **-1,04 m** — yani noktalar zeminin kendisidir.
**Bu ayakizinde Subat 2023'te hicbir yapi yoktu; duz, acik arazi vardi.**
Kalan %1,1 muhtemelen kenardaki agaclardir (>8 m noktalarin **%100'u cok
donusludur**, bkz. 3.3).

### 3.2 `0503100000041285` — 124.119 nokta

| Sinif | Nokta | Pay |
|---|---|---|
| **2 (Maaiveld)** | 77.121 | **%62,1** |
| 1 (Overig) | 46.998 | %37,9 |
| 6 (Bebouwing) | **0** | **%0,0** |

| Maaiveld ustu yukseklik | Nokta | Pay |
|---|---|---|
| **zemin seviyesi (< 0,5 m)** | 72.964 | **%58,8** |
| 0,5-3 m | 5.515 | %4,4 |
| 3-8 m | 11.017 | %8,9 |
| > 8 m | 34.623 | %27,9 (maks 32,33 m) |

Burada **yuksek malzeme var** — ama bina degil (bkz. 3.3). Yuksekligin
dagilimi 8 m'den 30 m'ye kadar **surekli**dir; cati duzlemi olsa bir plato
gorulurdu:

| Bant | Nokta |
|---|---|
| 8-12 m | 17.562 |
| 12-16 m | 6.934 |
| 16-20 m | 3.997 |
| 20-25 m | 4.784 |
| 25-30 m | 1.881 |
| > 30 m | 131 |

Ayrica noktalarin **%58,8'i zemin seviyesinde** — yani lazer ayakizinin
buyuk kismindan **yere ulasmis**. Bir cati bunu engellerdi.

### 3.3 Kesin ayrim: donus yapisi

Ayni pulse birden cok donus veriyorsa isin **yari gecirgen** bir seyden
gecmistir (bitki ortusu). Kati cati tek donus verir.

| Bina | >8 m noktalar | **cok donuslu orani** |
|---|---|---|
| `0503100000001494` (**kontrol**, normal konut) | 3.064 | **%2,4** |
| `0503100000041285` | 35.289 | **%99,8** |
| `0503100000038184` | 394 | **%100,0** |

**Kontrol binasi ile arada 40 kat fark var.** 041285'in ayakizindaki yuksek
malzeme **kesinlikle bitki ortusudur**, cati degil.

---

## 4. 3DBAG'de var mi?

**Ikisi de 3DBAG v2023.10.08'de YOKTUR.**

Dolayisiyla `b3_kwaliteitsindicator` dahil hicbir `b3_*` oznitelik
mevcut degildir — deger dusuk degil, **kayit yok**.

Dogrulama: arama `NL.IMBAG.Pand.` onekiyle yapildi (3DBAG kimlikleri bu oneki
tasir) ve ayni sorgu kontrol binasi `0503100000001494` icin **kayit
dondurdu** (`b3_kwaliteitsindicator = True`, `b3_pw_bron = ahn5`,
`b3_pw_datum = 2023`, `b3_h_dak_max = 7,05 m`). Yani yokluk sorgu hatasi
degildir.

> Ilk denemem oneksiz kimlikle yapildi ve "yok" sonucu verdi — **dogru sonuc,
> yanlis yontemle**. Kontrol grubu eklenerek tekrarlandi.

Bu, bagimsiz bir teyittir: 3DBAG de (BAG anlik goruntusu ~2023 + AHN)
bu binalari uretememis.

---

## 5. Sonuc

| | `0503100000038184` | `0503100000041285` |
|---|---|---|
| Ayakizinda ne var (Subat 2023) | **duz, acik arazi** | **agaclik / acik alan** |
| Sinif 6 noktasi | 0 | 0 |
| Zemin noktasi orani | %98,9 | %62,1 |
| 3DBAG kaydi | yok | yok |
| **Aciklama** | **bina ucustan sonra yapildi** | **bina ucustan sonra yapildi** |

**Bu bir girdi KALITESI sorunu degildir.** AHN5 verisi bu ayakizlerinde
kusursuz calismistir — sadece olculdugu tarihte orada bina yoktu. Sorun
**zamansal uyusmazliktir**: BAG (2026 anlik goruntusu) ile AHN5 (Subat 2023)
arasinda 3 yil vardir.

### 5.1 `bouwjaar` tek basina bir belirteç DEGILDIR

A'da `bouwjaar >= 2023` olan **9** pand vardir, ama hepsi sifir oran vermiyor:

| bag_id | bouwjaar | ayakizi m2 | sinif 6 orani | gebruiksdoel |
|---|---|---|---|---|
| `0503100000041285` | 2026 | 1.665,0 | **0,000** | onderwijs, sport |
| `0503100000038184` | 2023 | 996,5 | **0,000** | onderwijs |
| `0503100000038212` | 2023 | 28,5 | **0,000** | (islev yok) |
| `0503100000038258` | 2023 | 24,2 | **0,000** | (islev yok) |
| `0503100000038260` | 2023 | 4,2 | **0,000** | (islev yok) |
| `0503100000038383` | 2023 | 37,4 | 0,815 | overige |
| `0503100000037335` | 2023 | 1.961,8 | 0,744 | **woonfunctie** |
| `0503100000037336` | 2023 | 1.251,6 | 0,566 | bijeenkomst, overige |
| `0503100000038177` | **2025** | 819,9 | 0,785 | winkel, **woonfunctie** |

`0503100000038177` **bouwjaar 2025** olmasina ragmen sinif 6 orani 0,785 —
yani Subat 2023'te o ayakizinda bir bina **vardi**. Demek ki `bouwjaar`,
"AHN5 ucusu sirasinda bina var miydi" sorusunu **cevaplamaz** (yenileme,
yeniden yapim veya BAG kayit pratigi).

**Bu yuzden filtre `bouwjaar` uzerinden kurulmamalidir.** Dogru belirteç
**dogrudan olcumdur**: `building_class_ratio` ve yeni eklenen
`ground_class_ratio`. Ikisi de artik CSV'dedir.

### 5.2 Ucuncu buyuk yapi: `0503100000039655`

Ayni alt grupta ucuncu bir yapi daha var: **109,0 m2, bouwjaar 2002,
gebruiksdoel bos**. Profili digerlerinden **farklidir**: 3.601 nokta, **hicbiri
8 m'nin uzerinde degil**, cok donuslu orani yalnizca %3,0. Yani orada alcak,
kati bir yapi vardir ve AHN onu **maaiveld/overig** saymistir — zamansal
uyusmazlik degil, **siniflandirma davranisidir**. Alt grup A ile ayni
mekanizma, sadece daha buyuk bir ornegi.

---

## 6. Asama 1'e etkisi (baglayici)

1. **Bu 3 yapi rekonstruksiyona girerse kesinlikle basarisiz olur.**
   Basarisizliklari `failed_buildings.csv` karsilastirmasinda **girdi
   yogunlugu** veya **yontem** olarak degil, **ucuncu kategori: kaynak
   uyusmazligi** olarak etiketlenmelidir.
2. **Filtre `bouwjaar` ile kurulmaz** (bkz. 5.1); `building_class_ratio` ve
   `ground_class_ratio` ile kurulur. Esik **Asama 1 basinda, hesaptan once**
   muhurlenecektir (Bolum 12.2) — P-013.
3. **`0503100000041285`'in ayakizi gecicidir** (`niet ingemeten`). Modele
   girerse geometrisi ayrica isaretlenmelidir.
4. **Enerji analizi (Asama 3):** bu iki okul A'nin enerji tuketiminde yer
   alacaksa, 3D geometrileri AHN5'ten **uretilemez**. Ya konut disi olarak
   kapsam disinda birakilirlar ya da baska bir yukseklik kaynagi gerekir.
   Bu bir **kullanici kararidir** (P-013).
