# AHN nokta bulutu sinif kodlari — belgeden dogrulama

**Tarih:** 2026-09-21 · **Asama:** 0.3 (Asama 1 oncesi kapanmasi istendi)
**Kural:** M-005 — varsayma, dogrula. ASPRS standardi **varsayilmadi**; AHN'in
kendi belgesi arandi.

Bu dosya, `data/raw/ahn/AHN5_T/*.LAZ` icinde **veriden okunan** sinif kodlarinin
ne anlama geldigini kaydeder.

## Veride bulunan kodlar (B alani, olculdu 2026-09-21)

| Kod | Nokta | Pay |
|---|---|---|
| 2 | 74.128.027 | %44,3 |
| 1 | 64.953.951 | %38,8 |
| 6 | 27.504.797 | %16,4 |
| 26 | 634.292 | %0,38 |
| 9 | 92.091 | %0,055 |
| 14 | 12.922 | %0,0077 |

---

## 1. Normatif kaynak

**Besteksvoorwaarden inwinning landsdekkende dataset AHN2020-2022**,
Definitief versie 1.0, 28-05-2019, Bolum 9 "Definities".
Kaynak: `https://basisdata.nl/hwh-ahn/AUX/bestekken/AHN4_inwinning.pdf`
(ahn.nl Dataroom sayfasindan baglanti verilmistir).

Bu, **AHN4 ihale sartnamesidir** — yani AHN'in yukleniciye dayattigi baglayici
tanim. Web sayfalarindan (ahn.nl/kwaliteitsbeschrijving, /4-classificatie,
/producten, /dataroom, geotiles.citg.tudelft.nl, pdok.nl) **hicbiri sayisal kod
vermez**; yalnizca sinif adlarini Hollandaca yazar. Sayisal tabloyu veren tek
resmi belge budur.

Belgenin acik ifadesi (Bolum 9, aynen):

> "De classificatiewaarden moet voldoen aan de standaard zoals deze voor LAS 1.4
> vastgesteld is (ASPRS Standard LIDAR Point Classes)."

Tablo (aynen):

| Classificatiecode | Betekenis (EN) | Overeenkomstige definitie (NL) |
|---|---|---|
| 0 | Created, never classified | nvt |
| 1 | Unclassified | Overig |
| 2 | Ground | Maaiveld |
| 6 | Building | Bebouwing |
| 9 | Water | Water |
| **26** | **Civil structure** | **Kunstwerken** |

---

## 2. Kod 26 — **DOGRULANDI**

**26 = Civil structure / Kunstwerken.** Yukaridaki normatif tabloda aciktir.
Tanim (Bolum 9.3, aynen):

> "Een kunstwerk wordt gedefinieerd als een civieltechnische constructie of
> installatie in de infrastructuur die geen waterkerende functie vervult."

Kapsam: bruggen (beweegbaar en vast), aquaducten, viaducten, ecoducten,
steigers/vlonders (belirli kosullarla). **Kapsam disi:** sluizen, stuwen,
dammen, dijken.

**Bagimsiz veri kaniti** (alt-fayans `37EN1_14`, 113.629 nokta):
maaiveld ustu yukseklik medyani **4,38 m**, p90 5,26 m, maks 8,32 m; yalnizca
**484 adet 5 m hucreye** yayilmis (nokta/hucre 235). Kopru/viyaduk/vlonder
profiliyle tutarli: alcak, yogun, dar seritler halinde. Belge ve veri ayni
seyi soyluyor.

---

## 3. Kod 14 — **BELGEDE YOK, CIKARIM**

**AHN'in hicbir belgesinde kod 14 gecmiyor.** Yukaridaki normatif tablo
0/1/2/6/9/26 ile biter. Elimizdeki kanit:

1. Sartname, degerlerin **ASPRS LAS 1.4 Standard LIDAR Point Classes**'a uymasi
   gerektigini soyluyor. O standartta **14 = Wire – Conductor (Phase)**.
2. ahn.nl Dataroom, aynen: **"Vanaf het AHN4 zijn ook hoogspanningsleidingen
   onderscheiden."** (AHN4'ten itibaren yuksek gerilim hatlari da ayirt edilir.)
   Yani AHN4'ten sonra tabloya eklenmis, ama tablo guncellenmemis.
3. Veri kaniti: bkz. asagida.

**Veri kaniti (tum 9 alt-fayans tarandi, 2026-09-21):** alt-fayanslarin
tamaminda 29.595 nokta, yalnizca **2 alt-fayansta** (`37EN1_25`, `37EN2_21`).
(Yukaridaki tablodaki 12.922 sayisi bundan kucuktur cunku o, yalnizca **B
alani bbox'i icindeki** noktalari sayar; buradaki tarama alt-fayansin
tamamini kapsar. Iki sayi celismez.)

| Olcut | Sinif 14 | Sinif 26 (karsilastirma) |
|---|---|---|
| Maaiveld ustu medyan | **17,31 m** | 4,38 m |
| p10 / p90 | 8,95 / 27,54 m | 0,01 / 5,26 m |
| Maks | 35,36 m | 8,32 m |
| Nokta / 5 m hucre | **25,8** (seyrek) | 234,8 (yogun) |
| Kapladigi bbox | **407 x 1.235 m** (dar, uzun) | - |

Yani: **havada yuksek, cok seyrek, ince ve uzun bir koridor boyunca.** Bu,
bir hava hatti iletkeninin profilidir; ne cati (sinif 6, medyan 7,56 m,
yogun ve alansal) ne de kunstwerk (alcak ve yogun) boyle gorunur.

**Durum:** `14 = hoogspanningsleiding (iletken tel)` **guclu veri kaniti ve
ASPRS LAS 1.4 ile desteklenen bir cikarimdir, ancak bir AHN belgesinin acik
beyani DEGILDIR.** Bu ayrim korunur (M-005): belgelenmis olan 26'dir,
cikarim olan 14'tur.

**Asama 1 icin sonuc:** kod 14 toplam noktalarin %0,0077'sidir ve
rekonstruksiyona **girmemelidir**. Hangi yorum dogru olursa olsun (tel, ya da
bilinmeyen bir sinif) bina catisi degildir; dislanmasi guvenlidir.

---

## 4. **AHN5 icin sinif spesifikasyonu YOKTUR**

Bizim girdimiz **AHN5**'tir (D-013). Aranan hicbir kaynak AHN5'in nokta bulutu
siniflandirmasini belgelemiyor — ne sayisal ne sozel:

- `ahn.nl/kwaliteitsbeschrijving` AHN4'te biter (AHN4'ten hala gelecek zamanla
  soz eder: "Het AHN4 zal tussen 2020 en 2022 worden ingemeten").
- `ahn.nl/4-classificatie` yalnizca **AHN3**'u sayar.
- `ahn.nl/dataroom` AHN5/AHN6'yi kapsar ama sadece raster/tegel/servis icin.
- GeoTiles (fayanslarimizin ureticisi) kendi siniflandirma belgesi yayinlamaz;
  `ahn.nl/kwaliteitsbeschrijving`'e yonlendirir.
- AHN5 ihale belgeleri tenderned.nl'de, dogrudan PDF olarak yayinda degil.

**Yani yukaridaki 26 yorumu AHN4'ten AHN5'e TASINMISTIR.** Bunu destekleyen sey,
belge degil, yukaridaki bagimsiz veri kanitidir.

Ayrica `ahn.nl/kwaliteitsbeschrijving` kendi dipnotunda uyariyor (aynen):

> "Let op dat de definitie van de klasse gebouwen en de klasse kunstwerken in het
> AHN3 en het AHN4 niet identiek is!"

Tanimlar surumler arasinda **degisiyor**. AHN5'te tekrar degismis olabilir ve
bunu dogrulayacak belge yok. Bu bir **sinirlamadir**, AGENTS.md Bolum 5'e
islenmistir.

---

## 5. Asama 1'i dogrudan etkileyen uc tanim (Bolum 9.2, aynen)

### 5.1 Sinif 6 "cati" DEGILDIR — cepheler de dahildir

> "Alle laserpunten die een gebouw raken, **dus ook de zijkanten van een
> gebouw**, dienen te worden geclassificeerd als bebouwing, ook dakkapellen en
> uitstekende balkons."
>
> "Zonnepanelen die bevestigd zijn aan objecten die aan de gebouwdefinitie
> voldoen dienen als bebouwing geclassificeerd te worden."

ahn.nl'de yayimlanan bir sunum da ayni seyi soyler ("Gevels zijn onderdeel van
klasse building (6) en daarmee niet gescheiden van daken" — Tobias Wittwer,
*Classificatie van puntenwolken en het AHN*, ahn.nl CDN).

**Sonuc:** "sinif 6 = cati noktasi" **yanlistir**. Cephe, dakkapel, balkon ve
gunes paneli noktalari da 6'dir. Asama 1'de cati duzlemi cikarilirken bu
ayrilmalidir (dikeylik olcutu). `building_class_ratio` metrigimiz de "cati
orani" degil, "bina sinifi orani"dir — adi bu yuzden boyle konmustur.

### 5.2 Sinif 6 noktalari ayakizinin DISINA dusebilir

> "Alle laserpunten die een gebouw raken dienen te worden geclassificeerd als
> bebouwing, **ook al ligt een deel van de punten buiten het vlak dat in de BAG
> als pand of ligplaats wordt aangeduid.**"

**Sonuc:** kati `within` olcumumuz, binaya ait olup ayakizi disina dusen sinif 6
noktalarini **sistematik olarak kaciriyor** — ve komsu binanin ayakizine dusen
noktalari o komsuya yaziyor. Bu, M-007'nin ikincil bulgusunu (kucuk
ayakizlerinde kenar etkisi) **guclendirir** ve ona ikinci bir mekanizma ekler.

### 5.3 Sinif 6, BAG'den TURETILMISTIR — bagimsiz bir gozlem degildir

> "Voor de definitie van bebouwing wordt **de BAG pandenkaart ten tijde van de
> vlucht** gehanteerd."
>
> "Alle objecten die niet in de BAG pandenkaart of BAG ligplaatsenkaart ten
> tijde van de opname aanwezig zijn, zoals o.a. **tuinhuisjes zonder fundering**,
> straalzendmasten, hoogspanningsmasten, straatmeubilair: deze dienen als
> **"overig"** (=1) te worden geclassificeerd."

**Sonuc — Bolum 12.10 (bagimsizlik) acisindan onemli:** AHN sinif 6, BAG'den
bagimsiz bir "burada bina var mi" olcumu **degildir**; kismen BAG'in kendisinden
turer. Dolayisiyla `building_class_ratio`, BAG ayakizinin dogrulugunun bagimsiz
bir denetimi olarak **kullanilamaz**. Girdi kalitesi gostergesi olarak
kullanilabilir; bagimsiz dogrulama olarak kullanilamaz.

---

## 6. Asama 1'e girecek siniflar — oneri (onay bekliyor)

| Kod | Karar | Gerekce |
|---|---|---|
| 6 | **DAHIL** | bina (cephe dahil; cati ayrimi Asama 1'de dikeylikle yapilir) |
| 2 | **DAHIL** (yalniz zemin kotu icin) | bina yuksekligi maaiveld referansi |
| 1 | **HARIC** (ama izlenir) | bitki ortusu + siniflandirilamayan her sey |
| 26 | **HARIC** | kunstwerk (kopru/vlonder), bina degil |
| 9 | **HARIC** | su |
| 14 | **HARIC** | tel/bilinmeyen; her halukarda cati degil |

Bu oneri **onaylanmamistir**; Asama 1 baslangicinda karara baglanacaktir
(PENDING_DECISIONS P-012).
