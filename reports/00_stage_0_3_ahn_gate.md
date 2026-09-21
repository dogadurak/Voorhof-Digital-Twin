# Asama 0.3 — AHN girdi kalite kapisi

**Karar D-015** · AGENTS.md Bolum 12.12 · run_id `RUN-2026-09-21-024`

> **VERI DONEMI (D-020).** Bu projede **geometri** AHN5 ucus donemini
> (**2023-02-08 / 2023-02-14**, LAZ `gps_time`'dan olculdu) temsil eder;
> **oznitelikler** BAG anlik goruntusudur (**2026-09**). Arada **3,5 yil**
> vardir. Ucustan sonra yapilmis veya degismis binalarin geometrisi
> uretilemez; bunlar **"geometrisi yok (ucus sonrasi)"** etiketiyle listelenir
> ve modellenmez.

Esikler `config/acceptance_criteria.yml` -> `input_gate_ahn` altindan okundu.
O blok bu olcumden **once** ayri bir commit ile muhurlendi.

## Kapi sonucu

| Kriter | Kaynak | Esik | Olculen | Sonuc |
|---|---|---|---|---|
| **0-E sert kapi** | ahn.nl resmi spec (AHN4 tabani) | >= 10.0 p/m2 | **35.89** | **PASS** |
| **0-F beklenti** | kendi olcumumuz (37EN1 = 29,3) | >= 20.0 p/m2 | **35.89** | **PASS** |

## B alani yogunluk dagilimi

| Metrik | Deger |
|---|---|
| Olculen hucre (10 x 10 m, merkezi B icinde) | 27784 |
| Medyan yogunluk | 35.89 p/m2 |
| 10. persentil | 17.79 p/m2 |
| Bina sinifi (kod 6) toplam nokta | 20,053,799 |
| Bina sinifi noktasi olan hucre | 41.2 % |
| O hucrelerde medyan bina yogunlugu | 13.89 p/m2 |
| Sifir donuslu hucre | 0.09 % |
| Sert kapinin altinda hucre | 1.22 % |
| Beklentinin altinda hucre | 14.13 % |
| Islenen nokta (B bbox) | 167,326,080 |

**Sifir donuslu hucreler bir hata DEGILDIR:** su yuzeyleri dogal olarak donus
vermez. Su disi kumelenme Asama 1'de BGT su katmaniyla ayristirilacaktir.

## Bina bazli cati yogunlugu (esik yok — raporlanir)

A alanindaki **1259** bina icin, ayakizi poligonu icine dusen nokta /
ayakizi alani:

| Metrik | Deger |
|---|---|
| Medyan | 38.22 p/m2 |
| 10. persentil | 28.27 p/m2 |
| **10 p/m2 altinda** | **1 bina** (%0.1) |

Tam liste: `reports/ahn_point_density_by_building.csv`

### Bina sinifi (kod 6) orani — esik yok, raporlanir

`roof_density_pts_m2` ayakizi icindeki **tum siniflari** sayar. Catiyi orten
agac noktalari (sinif 1) da "cati noktasi" olarak sayilir; bu yuzden yogunluk
**tam da rekonstruksiyonun bozulacagi binalarda iyi gorunur**. Asagidaki oran
o kor noktayi kapatir.

`building_class_ratio` = ayakizi icindeki sinif 6 noktasi / ayakizi icindeki
tum noktalar. Ikisi de ayni `within` sorgusundan gelir.

| Metrik | Deger |
|---|---|
| Medyan `building_class_ratio` | 0.874 |
| 10. persentil | 0.482 |
| Tanimsiz (ayakizi icinde 0 nokta) | 0 bina |
| Oran < 0.001 | 67 bina (%5.3) |
| Oran < 0.100 | 67 bina (%5.3) |
| Oran < 0.250 | 76 bina (%6.0) |
| Oran < 0.500 | 128 bina (%10.2) |

**En dusuk oranli 10 bina.** DIKKAT: **67 bina tam 0,000'da esittir**, yani
"en dusuk 10" tek basina anlamli bir siralama vermez. Esitlik **nokta sayisina**
gore bozulmustur: ayni oranda icinde daha cok nokta bulunan bina Asama 1 icin
daha buyuk risktir. Tam liste CSV'dedir.

| bag_id | ayakizi m2 | toplam nokta | sinif 6 nokta | sinif 6 orani | zemin orani | gebruiksdoel |
|---|---|---|---|---|---|---|
| `0503100000041285` | 1665.0 | 124,119 | 0 | **0.000** | 0.621 | onderwijsfunctie,sportfunctie |
| `0503100000038184` | 996.5 | 81,963 | 0 | **0.000** | 0.989 | onderwijsfunctie |
| `0503100000038212` | 28.5 | 9,324 | 0 | **0.000** | 0.261 | (islev yok) |
| `0503100000039655` | 109.0 | 3,601 | 0 | **0.000** | 0.014 | (islev yok) |
| `0503100000038258` | 24.2 | 2,515 | 0 | **0.000** | 0.296 | (islev yok) |
| `0503100000038676` | 8.8 | 1,336 | 0 | **0.000** | 0.072 | (islev yok) |
| `0503100000039608` | 13.8 | 1,249 | 0 | **0.000** | 0.063 | (islev yok) |
| `0503100000039647` | 16.8 | 1,158 | 0 | **0.000** | 0.058 | (islev yok) |
| `0503100000039640` | 9.7 | 1,100 | 0 | **0.000** | 0.031 | (islev yok) |
| `0503100000039645` | 17.1 | 969 | 0 | **0.000** | 0.107 | (islev yok) |

Dusuk oran = cati muhtemelen **bitki ortusuyle kapali** veya **siniflandirma
eksik**. Tek basina hata degildir. Asama 1'de `failed_buildings.csv` ile
karsilastirilacak **ucuncu eksen** budur: yogunluk yeterli ama sinif 6 orani
dusukse, basarisizligin nedeni "az nokta" degil **"yanlis nokta"**dir.

#### Beklenmeyen bulgu: sifir grubu agac ortusu DEGIL

Oran tam 0 cikan 67 binanin profili, "cati agac altinda kalmis konut"
beklentisine **uymuyor**:

| | Sifir grubu (n=67) | Digerleri (n=1192) |
|---|---|---|
| Ayakizi medyani | **8.0 m2** | 52.3 m2 |
| < 50 m2 olan | 64/67 | 452/1192 |
| Konut VBO'lu | **%3.0** | %75.2 |
| Bouwjaar medyani | **2014** | 1966 |

Bunlar **kucuk, konut olmayan, sonradan yapilmis yardimci yapilardir**
(berging, bisiklet deposu, bahce evi).

**Kucukluk tek basina sebep DEGILDIR:** A'daki tum kucuk binalarin (<50 m2)
sinif 6 orani medyani **0.854**, buyuklerinki
**0.885** — neredeyse esit. Sorun kucukluk degil, bu belirli
alt gruptur.

#### Sifir grubu: SAYIYA gore ve ETKIYE gore — iki farkli tablo

> **Bolum 14.6 / M-010 geregi.** Bu grup once yalnizca medyanla ozetlenmis ve
> "kucuk, konut disi yardimci yapilar" diye genellenmisti. Medyan **cogunlugu**
> anlatir, **etkisi buyuk azinligi gizler**. Asagida ayni grup iki ayri
> agirlikla verilir.

| Alt grup | Sayica | Alanca |
|---|---|---|
| **A — kucuk yapilar** (< 100 m2) | **64** bina (%95.5) | 621 m2 (**%18.3**) |
| **B — buyuk yapilar** (>= 100 m2) | **3** bina (%4.5) | 2,771 m2 (**%81.7**) |
| **Toplam** | 67 bina | 3,392 m2 |

**Tablo agirliga gore tersine donuyor:** sayica grubun %95.5'i kucuk
yapilardir, ama toplam alanin **%78.5'i yalnizca 2 binadadir**.

**Etkiye gore en buyuk 5 uye (tek tek):**

| # | bag_id | ayakizi m2 | alan payi | gebruiksdoel | bouwjaar | zemin orani |
|---|---|---|---|---|---|---|
| 1 | `0503100000041285` | 1,665.0 | %49.1 | onderwijsfunctie,sportfunctie | 2026 | 0.621 |
| 2 | `0503100000038184` | 996.5 | %29.4 | onderwijsfunctie | 2023 | 0.989 |
| 3 | `0503100000039655` | 109.0 | %3.2 | **(islev kaydi yok)** | 2002 | 0.014 |
| 4 | `0503100000038212` | 28.5 | %0.8 | **(islev kaydi yok)** | 2023 | 0.261 |
| 5 | `0503100000038258` | 24.2 | %0.7 | **(islev kaydi yok)** | 2023 | 0.296 |

Ilk ikisi **okuldur** (`onderwijsfunctie`) ve tek tek teshis edilmistir:
**`reports/00_stage_0_3_zero_ratio_investigation.md`**.

#### Alt grup B — teshis edildi, mekanizma tek degil

- **2 yapi (1.665,0 ve 996,5 m2, ikisi de OKUL):** ayakizinde AHN5 ucusu
  (**2023-02-08/14**) sirasinda **hicbir bina yoktu**. Kanit **olcumdur**,
  cikarim degil: zemin (sinif 2) noktasi orani %62,1 ve %98,9; >8 m
  noktalarin **%99,8 ve %100'u cok donuslu** (kontrol binasinda %2,4 — bitki
  ortusu imzasi); ikisi de **3DBAG'de yok**. Sebep girdi kalitesi degil,
  **zamansal uyusmazliktir** (D-020).
- **1 yapi (109,0 m2, bouwjaar 2002):** 8 m ustu hic noktasi yok, cok donuslu
  orani %3,0 — orada alcak, kati bir yapi var ve AHN onu **maaiveld/overig**
  saymis. Alt grup A ile **ayni mekanizmanin** buyuk ornegi.

**Karar (D-019, kullanici onayi):** bu **3 yapi Asama 1'den dislanir** ve
sinirlama olarak raporlanir. Karar dogrudan olcume dayandigi icin Bolum 12.13
kapsaminda **degildir**; gorsel dogrulamayi beklemez.

#### Alt grup A — aciklama bir CIKARIMDIR, dogrulanmayi bekliyor

> ### CIKARIM (Bolum 12.13 — dogrulanmadan karara baglanmaz)
>
> 64 kucuk yapinin **berging / bisiklet deposu / bahce evi** oldugu
> dusunulmektedir. Dayanak: ayakizi medyani 8.0 m2, `gebruiksdoel`
> **64/64'unde tamamen bos**, woonfunctie **sifir**.
>
> **Bu bir OLCUM DEGILDIR.** BAG'de `gebruiksdoel` bos olmasi, yapinin depo
> oldugunu degil, **bir kullanim islevi kaydedilmedigini** soyler. Ikisi ayni
> sey degildir (MISTAKES.md **M-011**).
>
> **Dogrulama:** sabit seed ile secilmis 12 binalik gorsel orneklem —
> `reports/visual_check_sample.csv`, `aoi/qa/zero_class6_buildings.geojson`,
> sonuclar `docs/visual_check_zero_class6.md`.
> **P-012 bu dogrulama bitmeden karara baglanmayacaktir.**

Destekleyici belge (kanit degil): AHN4 sartnamesi Bolum 9.2, BAG'de olmayan
"tuinhuisjes zonder fundering" gibi nesnelerin **"overig" (=1)**
siniflandirilmasini emreder. Ancak bu yapilar BAG'de **vardir**, yani kural
birebir uymuyor; AHN5'in siniflandirici davranisi belgelenmemistir (bkz.
`docs/ahn_class_codes.md`).

**Asama 1'e etkisi:** bu 67 bina basarisiz olursa sebep **ne girdi
yogunlugu ne bizim yontemimizdir** — AHN'in siniflandirma politikasidir.
Bu **ucuncu neden kategorisi** Bolum 12.6'nin "nedeni siniflandir" adimina
eklenmistir. Sinif 1'in rekonstruksiyona alinip alinmayacagi **P-012**'de
acik karardir: bu yapilar sinif 1 dislanirsa **hic nokta gormez**.

**Esik konulmadi** cunku dusuk cati yogunlugu tek basina hata degildir —
kucuk veya egimli catili binalarda dogal olarak az nokta duser.

**Asama 1'de kullanimi:** `reports/failed_buildings.csv` bu listeyle
karsilastirilacak. Basarisiz VE dusuk yogunluklu -> neden muhtemelen **girdi**;
basarisiz AMA yeterli yogunluklu -> neden muhtemelen **yontem**. Bu ayrim
sonradan yapilamaz.

## Olcum tanimindan gelen bilinen yanlilik

Bina bazli sayim, ayakizi poligonunun **icine dusen** noktalari alir
(`within`, kesisim degil). Iki ayri mekanizma bunu asagi cekiyor:

1. **Sinir noktalari elenir.** Elenen bolge **cevreyle**, sayilan bolge
   **alanla** orantilidir; bu yuzden kucuk ayakizlerinde yogunluk sistematik
   olarak biraz dusuk cikar (MISTAKES.md M-007 ikincil bulgu).
2. **Sinif 6 noktalari ayakizinin disina dusebilir.** AHN4 sartnamesi Bolum
   9.2 bunu acikca soyler: "ook al ligt een deel van de punten buiten het vlak
   dat in de BAG als pand ... wordt aangeduid". Yani binaya ait noktalarin bir
   kismini kaciriyoruz, bir kismini da **komsu binaya** yaziyoruz.

Ikisi de veri sorunu DEGILDIR; olcum tanimindan gelir ve Asama 1'de dusuk
degerler yorumlanirken akilda tutulmalidir.

## Sinif dagilimi — ASPRS varsayilmadi, belgeden dogrulandi

```
2:74128027, 1:64953951, 6:27504797, 26:634292, 9:92091, 14:12922
```

Kod anlamlari `docs/ahn_class_codes.md`de **belgeden** dogrulanmistir (D-017).
Ozet:

| Kod | Anlam | Kanit |
|---|---|---|
| 1, 2, 6, 9, **26** | Overig, Maaiveld, Bebouwing, Water, **Kunstwerken** | **BELGELENMIS** — AHN4 Besteksvoorwaarden Bolum 9 |
| **14** | hoogspanningsleiding (tel) | **CIKARIM** — AHN belgesinde yok; ASPRS LAS 1.4 + veri kaniti |

**Iki uyari Asama 1 icin kritiktir:**
- **Sinif 6 "cati" degildir** — cepheler, dakkapeller, balkonlar ve gunes
  panelleri de 6'dir (sartname Bolum 9.2).
- **AHN5 icin sinif spesifikasyonu yoktur.** Yorumlar AHN4'ten tasinmistir;
  ahn.nl tanimlarin surumler arasi degistigini kendi dipnotunda soyluyor.
