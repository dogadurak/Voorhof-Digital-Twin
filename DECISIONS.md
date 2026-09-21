# DECISIONS.md — Metodolojik kararlar

> AGENTS.md Bolum 12.11: asagidakiler kullanici onayi olmadan degistirilemez —
> yeni veri kaynagi, yeni AOI, CRS stratejisi, kabul esigi veya metrik, dogrulama
> metodolojisi, lisans kosulu, ucretli/ogrenci-lisansli yazilim, temel model
> varsayimi, cekirdek cikti tanimi, yuksek hesaplama kaynagi gerektiren calistirma.
>
> **Her onaylanan degisiklik buraya tarih ve gerekceyle yazilir.**

> **SONRAKI BOS ID: D-021**  — yeni karar yazmadan once bu satiri oku ve guncelle.
> (Numara cakismasi iki kez yasandi; ID'yi gorunur tutmak bunun onlemidir.)

| ID | Tarih | Konu | Durum |
|---|---|---|---|
| D-001 | 2026-09-21 | Python ortami: conda-forge | ONAYLANDI |
| D-002 | 2026-09-21 | Asama 0.4 kapsami | ONAYLANDI |
| D-003 | 2026-09-21 | Sayisi verilmemis esikler | ONAYLANDI |
| D-004 | 2026-09-21 | Depo adi | ONAYLANDI |
| D-005 | 2026-09-21 | Asama 0 raporu elle yazilir | ONAYLANDI |
| D-006 | 2026-09-21 | Indirmeler B alani bbox'i ile sinirlanir | ONAYLANDI |
| D-007 | 2026-09-21 | AOI merkezi kural tabanli secilir + kor karsilastirma | ONAYLANDI |
| D-008 | 2026-09-21 | 0.2a metrik paydalari ve status filtresi | ONAYLANDI |
| D-009 | 2026-09-21 | AOI = 7 resmi konut buurt'u; aday izgarasi iptal | ONAYLANDI |
| D-010 | 2026-09-21 | AHN/3DBAG indirmelerine +50 m guvenlik payi | ONAYLANDI |
| D-011 | 2026-09-21 | C alani kural tabanli secilir; hesap 0.3 sonrasina | ONAYLANDI |
| D-012 | 2026-09-21 | C yukseklik esigi: 25 m birincil, 37,5 m on-kayitli yedek | ONAYLANDI |
| D-013 | 2026-09-21 | Girdimiz AHN5 (kapsama tamsa), 3DBAG surumunden bagimsiz | ONAYLANDI |
| D-014 | 2026-09-21 | Girdi kalite kapisi ilkesi (AGENTS.md 12.12) | ONAYLANDI |

---

## D-001 · [2026-09-21] · Python ortami conda-forge ile kurulur

**Karar:** Asil ortam dosyasi `environment.yml` (kanal: conda-forge, ortam adi
`voorhof-twin`). `requirements.txt` yalnizca conda-forge'da bulunmayan pip paketleri
icin tamamlayici olarak tutulur.

**Gerekce:** GDAL, rasterio, fiona, laspy ve PDAL Windows'ta pip ile kaynaktan
derleme gerektiriyor ve derleyici zinciri olmadan kurulum kiriliyor. conda-forge
bu paketleri hazir binary olarak sunuyor. Makinede conda 26.1.0 zaten kurulu.

**Etkiledigi asamalar:** 0.3 (indirme scriptleri), 0.4 (dogrulama), 1+ (geometri).

**Alternatif ve neden secilmedi:** Saf pip/venv daha tasinabilir olurdu ancak
Windows'ta geospatial yigin kurulumu yuksek olasilikla basarisiz olur. Tam Docker
yaklasimi maksimum tekrarlanabilirlik verirdi ama QGIS masaustu entegrasyonunu
(Asama 3, UMEP/SOLWEIG) zorlastirir; Asama 1'de zaten Docker kullanilacak.

**Onay:** Kullanici, 2026-09-21.

---

## D-002 · [2026-09-21] · Asama 0.4 yalnizca `verify_data.py` kapsar

**Karar:** Asama 0.4 = `src/00_acquisition/verify_data.py`. AGENTS.md Bolum 13.6'da
sayilan dort oz-olcum scripti (`spot_check.py`, `check_thresholds.py`,
`check_compliance.py`, `make_stage_report.py`) **Asama 0.5** olarak ayrilir.

**Gerekce:** AGENTS.md Bolum 13.6 bu scriptlerin "Asama 0.4'te yazilacagini" soyluyor,
kullanicinin asama plani ise 0.4'u `verify_data.py` olarak tanimliyor. Ikisi ayni is
degil. Bes scripti tek adimda yazmak Bolum 14.6'daki "kapsam kaymasi" hata sinifina
girer ve tek oturumda kontrol edilemez. Tek gorev, tek cikti ilkesi korundu.

**Etkiledigi asamalar:** 0.4, 0.5 (yeni), 1 (baslangic on kosulu).

**Sonucu:** Asama 0.5 tamamlanmadan Asama 1'e gecilmez, cunku Bolum 13.1'deki Asama
Sonu Raporunu ureten `make_stage_report.py` 0.5'te yazilir.

**Onay:** Kullanici, 2026-09-21.

---

## D-003 · [2026-09-21] · Sayisi verilmemis esikler TODO_ONAY_BEKLIYOR kalir

**Karar:** AGENTS.md'nin sayisal deger vermedigi kabul esikleri
`config/acceptance_criteria.yml` icinde `TODO_ONAY_BEKLIYOR` olarak birakilir.
Ilgili asama baslamadan once kullanici kaynak gostererek onaylar.

**Etkilenen kriterler:**

| Kriter | Metrik | Ne zaman gerekli |
|---|---|---|
| 1-C | `ahn_z_diff_rmse_m` | Asama 1 baslangici |
| 3-B | `nmbe_pct` | Asama 3 baslangici |
| 3-C | `cv_rmse_pct` | Asama 3 baslangici |

**Gerekce:** Iki kural carpisiyordu. Bolum 12.2 esiklerin sonuctan once
kilitlenmesini istiyor; Bolum 12.11 esik belirlemeyi kullanici onayina bagliyor ve
Bolum 1 kural 1 sayi uydurmayi yasakliyor. Cozum: esik slotu simdi acilir ve
kilitlenir, sayisi ilgili asama baslamadan once onayla doldurulur. Boylece ne sayi
uydurulmus olur ne de esik sonuc gorulduikten sonra belirlenir.

**Onemli not (Kriter 1-C):** AGENTS.md Bolum 4 bir celiski iceriyor — resmi AHN
kwaliteitsbeschrijving duseyde stokastik sigma <=5 cm verirken AHN5 ihale belgesi
sigma <=3 cm diyor. Bu celiski raporda acikca not dusulecek, sessizce tek deger
secilmeyecek. Esik bu celiski cozulmeden sayisallastirilmaz.

**Uygulama:** `src/common/config.py` icindeki `get_threshold()`, onaylanmamis bir
esik okunmaya calisildiginda `PendingThresholdError` firlatir. Onaysiz esikle
PASS/FAIL beyan etmek teknik olarak engellenmistir.

**Onay:** Kullanici, 2026-09-21.

---

## D-004 · [2026-09-21] · Depo adi `Voorhof-Digital-Twin`

**Karar:** Proje/depo adi `Voorhof-Digital-Twin`
(https://github.com/dogadurak/Voorhof-Digital-Twin).

**Gerekce:** AGENTS.md Bolum 8'deki `delft-twin` bir placeholder'di ve Bolum 11-3
acik karar olarak isaretlenmisti. Kullanici depoyu bu adla olusturdu.

**Sonucu:** AGENTS.md Bolum 8 agaci ve Bolum 11-3 guncellendi; Bolum 11-3 KAPANDI.
Bolum 8 agacina ayrica, diger bolumlerin zaten zorunlu kildigi ama agacta eksik olan
ogeler islendi: `MISTAKES.md` (Bolum 14), `src/qa/` (Bolum 13.6), `src/common/`,
`reports/PENDING_DECISIONS.md` (Bolum 13.4), `environment.yml`, `requirements.txt`,
`.env.example`. Bu bir metodoloji degisikligi degil, belge ici tutarlilik duzeltmesidir.

**Onay:** Kullanici, 2026-09-21.

---

## D-005 · [2026-09-21] · Asama 0'in sonu raporu elle yazilir

**Karar:** Asama 0'in Bolum 13.1 formatindaki Asama Sonu Raporu elle yazilir.
Asama 0.5'ten sonraki tum raporlar `src/qa/make_stage_report.py` ile uretilir.

**Gerekce:** D-002 geregi rapor ureticisi 0.5'te yazilacak; 0.1-0.4 kendi raporlarini
uretecek araca sahip degil. Rapor formatinin kendisi degismez, yalnizca uretim yontemi
gecici olarak eldir.

**Risk ve nasil ele alindi:** Elle yazilan rapor, otomatik raporun yakaladigi eksik
alanlari kacirabilir. Bu yuzden Bolum 13.1 sablonunun her alani elle raporda da
eksiksiz doldurulur; bos birakilan alan FAIL sayilir.

**Onay:** Kullanici, 2026-09-21.

---

## D-006 · [2026-09-21] · Tum indirmeler B alani bbox'i ile sinirlanir

> **Numaralandirma notu:** Kullanici bu karari "D-004" olarak istemisti. D-004
> numarasi daha once depo adi karari icin kullanilmis ve AGENTS.md Bolum 11-3 ile
> commit 61e4677 mesajinda ona atif yapilmisti. Referanslari kirmamak icin bu karar
> **D-006** olarak kaydedildi. Icerik kullanicinin talimatiyla aynidir.

**Karar:** Hicbir veri kumesi ulke geneli olarak indirilmez. Her indirme, **B alani
(baglam/tampon) bounding box'i** ile sinirlanir.

| Veri | Sinirlama yontemi |
|---|---|
| **BAG** | PDOK **WFS bbox sorgusu**. Ulke geneli ATOM/full download KULLANILMAZ. |
| **AHN5** | Yalnizca B alanini kesen **alt-fayanslar (subtiles)**. Tam kaartblad gereksizse indirilmez. |
| **3DBAG** | Yalnizca ilgili **tile'lar** (tile indeksinden secim / `api.3dbag.nl`). |
| Diger (BGT, NWB) | Ayni ilke: bbox veya tile bazli secim. |

**Gerekce (uc katmanli):**

1. **Disk.** Sistem diskinde olculen bos alan 31,6 GB idi (2026-09-21). Kullanici
   en az 80 GB'a cikaracak, ancak bbox sinirlamasi **disk durumundan bagimsiz olarak
   gecerlidir** — yer acilmasi ulke geneli indirmeyi mesru kilmaz.
2. **Sure ve tekrarlanabilirlik.** Kucuk ve tanimli bir bbox, indirmeyi tekrarlanabilir
   kilar. Kullanilan bbox `data/DATA_LOG.md`'ye **sorgu parametresi** olarak yazilir
   (Bolum 12.7) ve boylece ucuncu bir kisi ayni veriyi yeniden cekebilir.
3. **Ham veri butunlugu.** Yarida kesilen buyuk indirme bozuk dosya uretir; bozuk dosya
   checksum kontrolunden gecmez ama zaman kaybettirir (Asama 0 kriteri 0-C).

**NEDEN A DEGIL DE B:** AGENTS.md Bolum 3 tampon katmanini zorunlu kiliyor —
"B katmani atlanamaz. Tamponsuz simulasyonda kenar binalar golgelenmemis gorunur ve
gunes potansiyeli **sistematik olarak yuksek** cikar." Indirme kapsamini A ile
sinirlamak bu hatayi veri ediniminde kalici hale getirirdi. Bu nedenle bbox'in
**alt siniri B'dir**, A degil.

**D domeni icin yeterli mi:** Evet. Bolum 3, D (CFD domeni) icin "Geometri B'den"
diyor; ayrica geometri indirilmesi gerekmez.

**Uygulama kurallari (Asama 0.3):**
- bbox degeri `aoi/area_B_context.geojson` dosyasindan **turetilir**, koda gomulmez
  (Bolum 8: yollar ve parametreler config'ten okunur).
- bbox CRS'i **EPSG:28992**'dir ve sorguya acikca yazilir (Bolum 1, kural 6).
- Fayans/tile secimi kacinilmaz olarak bbox'tan biraz genis olur (fayanslar ayriktir).
  Bu fazlalik atilmaz, ham haliyle saklanir — `data/raw/` degistirilmez (Bolum 12.7).
  Kirpma yapilacaksa ciktisi `data/interim/` altina yazilir.
- Secilen her fayans/tile kimligi `DATA_LOG.md`'ye yazilir.

**Dogrulama (Asama 0.4, `verify_data.py`):** Indirilen kapsamin B alanini **tamamen**
icerdigi kontrol edilir. Icermiyorsa bbox dar demektir ve Bolum 12.6 uygulanir —
eksik veriyle devam edilmez.

**Risk:** bbox hatali daraltilirsa kenar binalar eksik kalir ve golgeleme yine
sistematik olarak iyimser cikar. Bu, yonü bilinen bir hatadir; yukaridaki 0.4
kontrolu bunun icin vardir.

**Onay:** Kullanici, 2026-09-21.

---

## D-007 · [2026-09-21] · AOI merkezi kural tabanli secilir, kor karsilastirmayla dogrulanir

> **Numaralandirma notu:** Kullanici bu karari "D-005" olarak istemisti; o numara
> Aşama 0 raporunun elle yazilmasi karari icin kullanilmisti. Referansi kirmamak
> icin **D-007** olarak kaydedildi. Icerik kullanicinin talimatiyla aynidir.
> Tekrari onlemek icin dosyanin basina "SONRAKI BOS ID" satiri eklendi.

**Karar:** Asama 0.2'de A alaninin merkezi QGIS'te gozle secilmez. Merkez,
config'te kilitli kurallarla **hesaplanir**; kullanici sonucu gorsel dogrular.
Asama iki parcaya ayrilir:

- **0.2a (ajan):** resmi sinir indirilir, aday izgarasi uretilir, metrikler hesaplanir,
  en iyi 3 aday raporlanir.
- **0.2b (kullanici):** 3 aday QGIS'te hava fotografiyla kontrol edilir, biri secilir.
  C alani (150 m) secilen A icinde kullanici tarafindan belirlenir.

**Gerekce:** Gozle secim tekrarlanabilir degildir ve gerekcesi belgelenemez. Kural
tabanli secim hem tekrarlanabilir hem de kriterleri sonuctan once kilitli (Bolum 12.2).

### Kor karsilastirma protokolu

Kullanici QGIS'te **bagimsiz olarak** kendi merkezini secer ve **ajanin ciktisini
gormeden once** commit'ler. Iki yontemin yakinsamasi (veya ayrismasi) bir bulgudur
ve bu dosyaya yazilir.

Zamanlama (kullanici karari 2026-09-21): 0.2a'nin aday **uretmeyen** adimlari
(sema dogrulama, config, indirme) hemen yapilir; **aday hesabi kullanicinin secimi
commit'lendikten SONRA** calistirilir. Boylece kullanicinin secimi yapildigi anda
ajanin ciktisi hicbir bicimde var olmaz.

### Kilitlenen parametreler (hesaptan ONCE — Bolum 12.2)

| Parametre | Deger |
|---|---|
| Kare kenari | 600 m |
| Izgara adimi | 25 m |
| Bina sayisi araligi | 400-700 |
| woonfunctie orani | >= %90 |
| Voorhof ici alan orani | >= %80 |
| **Sayim kurali** | **pand centroid kare icinde** (kesisim DEGIL) |
| bouwjaar 1960-1975 | raporlanir + skora girer |
| Siralama | bilesik skor, esit agirlik (1/3 woonfunctie + 1/3 bouwjaar + 1/3 Voorhof ici) |
| Aday minimum ayrikligi | >= 300 m |
| CRS | EPSG:28992 |

Bu parametreler `config/acceptance_criteria.yml` -> `stage_0_2` altinda tutulur ve
**aday hesabindan once ayri bir commit ile muhurlenir**. Boylece esiklerin sonuclardan
once sabitlendigi git gecmisinden kanitlanir; beyana dayanmaz.

### Yeni veri kaynagi onayi (Bolum 1 kural 3 / Bolum 12.11)

**CBS Wijken en Buurten** AGENTS.md Bolum 4'teki 12 kaynakta yoktur. Bu kararla
resmi kaynak olarak eklenir:

| Alan | Deger (dogrulandi 2026-09-21) |
|---|---|
| Servis | `https://service.pdok.nl/cbs/wijkenbuurten/2025/wfs/v1_0` |
| Katmanlar | `wijkenbuurten:wijken`, `wijkenbuurten:buurten` |
| CRS | EPSG:28992 (DefaultCRS) |
| Surum | 2025 (2023 ve 2024 de mevcut; en guncel secildi) |
| Filtre | OGC Filter Encoding. **CQL_FILTER DESTEKLENMIYOR** (bkz. M-004) |

**Voorhof resmi kimligi (olculdu):** `WK050324` — **"Wijk 24 Voorhof"**.
Dikkat: ad "Voorhof" degildir; tam esleme sorgusu 0 kayit dondurur.

### Olculen baglam ve planin sonuclari

| Olcum | Deger |
|---|---|
| Voorhof kara alani | 124 ha |
| bbox | 1113 m (D-B) x 1828 m (K-G) |
| buurt sayisi | 9 |
| **Bedrijventerrein Voorhof + Vulcanusweg** | **17 ha = %14 sanayi/is alani** |

Iki sonuc:

1. **`assumptions.md` S-1 varsayimi ("Voorhof %90+ konut") wijk duzeyinde olculebilir
   bicimde tartismalidir.** A alani bu bolgelerden kacinabilir, ama varsayim
   duzeltilmeden birakilamaz — S-1 guncellenecek ve raporun Limitations bolumune girecek.
2. bbox genisligi 1113 m oldugundan 600 m karelerin merkezleri x ekseninde ~500 m
   araliga sikisir; 300 m ayriklikla uc aday buyuk olcude kuzey-guney dizilecektir.

### BAG indirme kapsami — plandaki eksigin duzeltilmesi

Merkezi Voorhof icinde olan bir 600 m kare, sinirdan **300 m disari tasabilir**
(kriter zaten %20'ye kadar tasmaya izin veriyor). Bu nedenle BAG indirmesi Voorhof
bbox'i degil, **bbox + 300 m tampon** ile yapilir. Aksi halde kenardaki adaylarin
bina sayimi eksik cikar ve secim sistematik olarak merkeze kayar.

**Not (D-006 ile iliski):** Bu tampon 0.2a'ya ozguduir. Asama 0.3'teki proje verisi
indirmeleri D-006 uyarinca secilen **B alani** bbox'i ile sinirlanir.

### Onemli epistemik sonuc — kriter 0-B artik bagimsiz kontrol DEGIL

`config/acceptance_criteria.yml` kriter **0-B**'de "400-700 bina" bir **akil
saglamasi** olarak yazilmisti: sayim aralik disinda cikarsa AOI sorgulanir. Bu kararla
AOI, bu araliga girecek sekilde **secilmektedir**.

Sonuc: **Asama 0 raporunda "bina sayisi beklenen aralikta, demek ki AOI dogru"
denemez.** Bu dongusel olur. Kriter 0-B bundan sonra bir tutarlilik kaydidir,
bagimsiz dogrulama degildir. Not `acceptance_criteria.yml` ve
`docs/validation_protocol.md` icine islenmistir.

**Onay:** Kullanici, 2026-09-21.

---

## D-008 · [2026-09-21] · Asama 0.2a metrik paydalari ve status filtresi

**Karar:** 0.2a'nin metrikleri asagidaki gibi tanimlanir. **Esikler degismemistir**
(400-700 ve >=%90 aynen durur); tanimlanan sey **hangi buyuklugun olculdugudur.**

| Metrik | Payda / kural | Kullanici secimi |
|---|---|---|
| Bina sayisi (0.2-A) | **TUM panden** (yardimci yapilar dahil) | evet |
| woonfunctie orani (0.2-B) | **VBO duzeyi** — karedeki panden'a bagli verblijfsobject'ler | evet |
| Coklu islevli VBO | **TAM ESLESME** — "woonfunctie,winkelfunctie" konut SAYILMAZ | evet (ajan onerisinden farkli) |
| bouwjaar 1960-1975 | VBO duzeyi (0.2-B ile ayni payda) | ajan, tutarlilik gerekcesiyle |
| panden_with_dwellings | aantal_verblijfsobjecten > 0 — **raporlanir, esik degil** | evet |

**Coklu islevli VBO notu:** Ajan "woonfunctie iceriyorsa say" (%93,3) onermisti;
kullanici daha kati olan tam eslesmeyi (%93,2) secti. Fark 0,09 puan.

**bouwjaar paydasi neden VBO:** Bilesik skorda toplanan iki oran farkli paydalara
sahip olursa skor yorumlanamaz. Olculen fark buyuktur: pand duzeyi %22,2,
VBO duzeyi %48,5.

### woonfunctie icin neden VBO duzeyi

Pand duzeyi **yanlis oldugu icin degil, KULLANILAMAZ oldugu icin** elendi:
indirilen panden'in **%40,6'si (3.124 adet)** `aantal_verblijfsobjecten = 0` olan
yardimci yapilardir (garaj, trafo, depo, otopark) ve gebruiksdoel'leri bostur.
Pand duzeyinde oran %50,5'te kalir; **>=%90 esigi hicbir karede saglanamaz** ve
secim sifir aday uretirdi.

### Bina sayisi icin neden TUM panden

Indirilen alanda yogunluk 1.852 pand/km2. 600x600 m = 0,36 km2 -> kare basina
**~667 pand**, yani AGENTS.md Bolum 3'un verdigi **400-700 araligina dogal olarak
oturuyor**. Yalnizca konutlu panden sayilsaydi kare basina ~337 duser ve alt sinirin
altinda kalirdi. Bu, Bolum 3'teki sayinin tum panden'i kastettigine dair gucli isaret.

### Status filtresi (kullanici talimati)

Degerler **indirilen veriden dogrulanmistir**, tahmin edilmemistir (M-005 kurali).

| Katman | Dahil | Haric |
|---|---|---|
| pand | Pand in gebruik (7576), Pand in gebruik (niet ingemeten) (4), **Verbouwing pand (77)** | Bouwvergunning verleend (31), Bouw gestart (15), Sloopvergunning verleend (1) |
| verblijfsobject | Verblijfsobject in gebruik (18644), **Verbouwing verblijfsobject (34)** | Verblijfsobject gevormd (668) |

**Kullanicinin varsayiminin duzeltilmesi:** "BAG WFS yikilmis binalari da iceriyor"
denilmisti. **OLCUM: indirilen 7.704 pand icinde yikilmis durum kaydi YOKTUR.**
PDOK bu WFS'te onlari sunmuyor. Dislanan durumlar aslinda **henuz insa edilmemis**
yapilardir. Filtre yine de yazildi: hem bu yapilari disliyor hem de veri surumu
degisirse savunma sagliyor.

**ACIK NOKTA — "Verbouwing pand" (P-008):** Kullanicinin literal listesi bunu
dislardi; belirtilen amac ise fiilen var olmayan yapilari dislamakti. Tadilattaki
bina **fiziksel olarak mevcuttur** ve catisi gunes/golge analizine girer. Ajan
amaca gore DAHIL etti ve karari onaya sundu. Dislansaydi 77 gercek bina (%1,0)
sayim disi kalirdi.

### Bilinen kaynak sinirlamasi

PDOK BAG WFS, BAG'in **kismi secimidir**; coklu adresli nesnelerde yalnizca
**hoofdadres** sunulur. 0.2 icin etkisi yok; **Asama 2 EP-Online eslestirmesinde
ciddi olabilir** (Bolum 12.3 hiyerarsisi nevenadres gerektirebilir).
AGENTS.md Bolum 5'e islendi; azaltim plani PENDING_DECISIONS -> P-007.

**Onay:** Kullanici, 2026-09-21.

---

## D-009 · [2026-09-21] · A = Voorhof'un 7 resmi konut buurt'u; aday izgarasi iptal

**Karar:** Calisma alani **aranmaz, resmi birimlerden birlestirilir**.

| Alan | Tanim | Olculen |
|---|---|---|
| **A** | Voorhof (WK050324) **7 resmi konut buurt'unun birlesimi** | 109,62 ha · 1.259 pand |
| **B** | A + 300 m tampon (programatik) | 277,76 ha · 4.035 pand |
| **C** | A icinde 150 x 150 m, kullanici secer | Asama 4 |
| **D** | COST 732 / AIJ, H olculunce | Asama 3 sonu (P-001) |

**Dahil edilen buurt kodlari** (veriden dogrulandi, 7 adet):
`BU05032400` Poptahof-Noord · `BU05032401` Poptahof-Zuid · `BU05032403`
Mythologiebuurt · `BU05032404` Aart van der Leeuwbuurt · `BU05032405` Roland
Holstbuurt · `BU05032406` Voorhof-Hoogbouw · `BU05032407` Multatulibuurt

**Dislanan:** `BU05032402` Bedrijventerrein Voorhof · `BU05032408`
Bedrijventerrein Vulcanusweg

**Raporda kullanilacak tanim:** *"Calisma alani = Voorhof'un 7 resmi konut
buurt'u; iki sanayi buurt'u dislanmistir."* Alan **turetilmis** degil, resmi
birimlerin birlesimidir — elle cizilmis hicbir cizgi yoktur, tekrarlanabilirdir.

### Aday izgarasi ve kor karsilastirma IPTAL

D-007'nin 25 m izgara aramasi ve kor karsilastirmasi kaldirildi. Gerekce:
secimde **oznel karar kalmadi**, dolayisiyla dogrulanacak bir secim de yok.
`config/acceptance_criteria.yml` -> `stage_0_2` blogu **silinmedi**,
`superseded_by: D-009` ile isaretlendi; esiklerin sonuctan once kilitlendigi iz
korunuyor (Bolum 12.2). O kriterlerle **hicbir hesap calistirilmadi**;
`aoi/candidates/` hicbir zaman olusmadi.

**400-700 bina araligi artik ESIK DEGILDIR.** A resmi sinirdan turedigi icin
bina sayisi raporlanan bir olcumdur. Kriter 0-B'nin dongusellik uyarisi
**cozuldu** olarak guncellendi.

### Kararin tetikleyicisi hatali bir gozlemdi (kullanici notu)

Karar, "Voorhof ~450-550 m eninde, 600 m kare her durumda tasiyor" gozlemiyle
tetiklendi. **Bu gozlem yanlisti.** Olcum:

| Iddia | Olculen |
|---|---|
| ~450-550 m en | medyan **814 m** (kesitlerin yalnizca %27'si 600 m'den dar) |
| kare her durumda tasar | **137 konumda kare tamamen A icinde** |
| tasarsa sanayiye girer | bu 137 karenin **58'i sanayiye hic degmiyor** |

Kullanici hatayi kabul etti ve kaydedilmesini istedi. **Karar yine de
korundu, cunku dogru gerekce baskaydi:** kareyi "en iyi skoru veren yere"
koymak, AOI'yi enerji dogrulamasi iyi gorunsun diye secmektir. Resmi sinir bu
yanliligi tamamen ortadan kaldirir. Yani sonuc dogru yone gitti, ama
**DECISIONS'a yazilan gerekce tasma degil, yanlilik olmamasidir.**

Bu, M-005 ile ayni kalip: yanlis gerekce, dogru yontem. Gerekce duzeltilmeden
birakilsaydi sonraki oturum "kare sigmiyor" diye yanlis bir kisit tasiyacakti.

### Dislamanin olculen etkisi — durustce

| | Tum poligon (9 buurt) | A (7 konut buurt'u) |
|---|---|---|
| pand | 1.433 | 1.259 |
| woonfunctie orani | %92,0 | **%92,6** |
| bouwjaar 1960-1975 | %71,3 | **%75,1** |

Iyilesme **gercek ama mutevazi**: woonfunctie +0,6 puan, kohort +3,8 puan.

**Onemli nitelendirme:** Dislanan iki "bedrijventerrein"in kendisi saf sanayi
DEGILDIR — icindeki 174 pand'in 164'u konut birimi tasiyor ve VBO woonfunctie
orani **%84,4**. CBS'in "Bedrijventerrein" etiketi arazi kullanim sinifidir,
bina kullanimini birebir yansitmaz. Dislama yine de savunulabilir (kohort ve
konut orani olculebilir bicimde iyilesiyor, PC6 homojenligi guclenir), ama
"sanayi alanlarini cikardik" ifadesi bu veriyle **tam dogru degildir**.
Raporda bu nitelendirme yer alacaktir.

**Dislamanin dogru cercevesi: KARMA KULLANIM (kullanici notu, 2026-09-21).**
Gerekce "sanayi" degil, **karma kullanim**dir. Bu, AGENTS.md Bolum 2'nin
Binnenstad'i eleme gerekcesiyle **birebir ayni ilkedir**: "Karma kullanim
(dukkan+ofis+konut) -> PC6 agregati konut modeliyle kiyaslanamaz hale gelir."
Ayni ilke Voorhof'un ici icin de tutarli bicimde uygulanmis olur. Bu cerceve
hem olculen veriye uyar (dislanan buurt'lar %84,4 konut, yani saf sanayi degil
karma) hem de projenin kendi elemek olcutuyle celismez.

### SANAYI BUURT'LARI MODELDEN CIKARILMIYOR

Dislama **yalnizca A'nin raporlama ve dogrulama kapsami** icindir.

- B icinde kalan sanayi binalari indirilir, LOD2 rekonstruksiyonuna girer,
  3B modelde yer alir, gunes/golge ve CFD hesaplarina **girdi olur**.
- Olculen: sanayi buurt'larinin **%100'u (17,14 ha) B icinde**; 174 pand.
- Asama 2'de her binaya `role` ozniteligi yazilir: **`analysis`** (centroid A
  icinde, raporlanir) / **`context`** (centroid B icinde A disinda, raporlanmaz).
  Web arayuzunde context binalari farkli stilde gosterilir.
- B = A + 300 m kurali degismedi.

### Gunes ve enerji ayrimi

| Cikti | `analysis` | `context` (sanayi dahil) |
|---|---|---|
| Cati gunes potansiyeli | hesaplanir, dogrulama istatistigine girer | **hesaplanir ve ikizde gosterilir**, `indicative` etiketli, dogrulama istatistigine GIRMEZ |
| Enerji tuketimi | hesaplanir (yalnizca konut) | **hesaplanmaz**; alan "modellenmedi — endustriyel surec yuku acik veriyle bilinemez" olarak isaretlenir, **bos birakilmaz** |

Gunes potansiyeli bir fiziksel buyukluktur ve kullanim tipinden bagimsizdir;
bu yuzden context binalari icin de uretilir. Bos birakilan bir enerji alani
"hesaplanmadi" ile "sifir" arasindaki farki gizler — Bolum 1 kural 5 bunu yasaklar.

### PC6 riski

Sanayi buurt'lariyla kesisen PC6 kumeleri Asama 3 karsilastirmasindan
**dislanacak ve sayilari raporlanacaktir**. `docs/validation_protocol.md`'ye
islendi; acik kalem P-009.

**Onay:** Kullanici, 2026-09-21.

---

## D-010 · [2026-09-21] · AHN ve 3DBAG indirmelerine +50 m guvenlik payi

**Karar:** Asama 0.3'te **AHN ve 3DBAG** indirilirken sorgu kapsami
**B bbox + 50 m** olur. BAG icin ek pay gerekmez (gerekce asagida).

```
AHN / 3DBAG sorgu kapsami = bbox(B) genisletilmis 50 m
```

**Gerekce — olculen sorun:** Asama 0.2'de B'nin guney kenarinda indirme
kapsamiyla arasindaki pay **0,0 m** olctuldu (B tam tegetti). Vektor BAG icin bu
sorun degildi: WFS bbox'a **degen** ozellikleri butun halinde doner, bina
geometrisi kesilmez.

**AHN ve 3DBAG icin ayni sey gecerli DEGILDIR:**
- **AHN** bir nokta bulutu/raster'dir. Sinirda kirpilirsa B'nin kenarindaki
  binalarin **catisi eksik nokta ile** rekonstruksiyona girer. Sonuc sessizdir:
  bina uretilir ama cati yuzeyi eksik nokta uzerinden uydurulur; `b3_nodata_fractie`
  yukselir ve yukseklik hatasi **kenarda sistematik** olur.
- **3DBAG** fayans (tile) tabanlidir. Sinira tegen bir bbox, kenardaki bir binanin
  ait oldugu fayansi **secim disi birakabilir**.

**Neden 50 m:** Bir binanin plan boyutu ve cati sacagi icin yeterli; indirme
hacmini anlamli olcude buyutmez. Sayi olculmus bir esik degil, muhendislik
paydir ve boyle kaydedilir.

**D-006 ile iliski — CELISMEZ:** D-006 "hicbir veri kumesi ulke geneli indirilmez,
kapsam B bbox'i ile sinirlanir" diyor. D-010 bu ilkeyi degistirmez; ayni sinirin
uzerine dar bir guvenlik payi ekler. Kapsam hala B merkezlidir.

**Raporlanan alan degismez:** Pay yalnizca **indirme** kapsamini etkiler.
Analiz B'de, **raporlama A'da** kalir (Bolum 3). Fazladan inen veri atilmaz,
`data/raw/` icinde ham haliyle durur (Bolum 12.7).

**Dogrulama (Asama 0.4, `verify_data.py`):** indirilen AHN/3DBAG kapsaminin
B'yi **en az 50 m payla** icerdigi kontrol edilir. Pay saglanmiyorsa Bolum 12.6
uygulanir; eksik kapsamla devam edilmez.

**Onay:** Kullanici, 2026-09-21.

---

## D-011 · [2026-09-21] · C alani kural tabanli secilir; hesap 0.3 sonrasina birakildi

**Karar:** C alani (mikroklima, 150 x 150 m) QGIS'te gozle secilmez; config'te
kilitli kurallarla hesaplanir. **Kurallar simdi muhurlendi, aday hesabi
CALISTIRILMADI.** Hesap Asama 0.3'te 3DBAG yukseklik verisi geldikten sonra,
yukseklik kurali da eklenerek **tek seferde** yapilacaktir.

**Neden ertelendi:** ENVI-met LITE'in 25 dikey hucre siniri, secilebilecek
karenin en yuksek binasina bir ust sinir koyuyor. Yukseklik verisi (3DBAG
`b3_h_dak_max`) Asama 0.3'te gelecek. Once secip sonra yukseklik kontrolu yapmak,
kuralin ihlal edildigi durumda **ikinci bir secim turu** gerektirirdi; kullanici
bunu istemedi. Tek seferde dogru secim yapilacak.

**Kullanicinin gozlemleri (yontem degisikliginin tetikleyicisi):**
- Uzun bloklar eksenlere hizali oldugu icin kare kenarinin bina kesmesi
  kacinilmaz gorunuyor.
- Denenen konumda **De Eglantier okulu** (`onderwijsfunctie`) kareye giriyordu.

### Muhurlenen kurallar

`config/acceptance_criteria.yml` -> `stage_0_2_c`, `status: SEALED_NOT_EXECUTED`.
Kare 150 m, eksenlere hizali, 10 m izgara adimi, A sinirina >= 50 m, sinirdan
gecen pand yok, konut disi VBO yok, en az 2 konutlu pand, adaylar arasi
>= 150 m (hic ortusmeme).

### Yardimci yapi esigi — kullanicinin onerisi OLCUMLE CURUTULDU

Kullanici "taban alani < 30 m2" onermisti. A'daki pand taban alani dagilimi
olculdu:

| | |
|---|---|
| Konutsuz pand (n=361) | p50 = 9,2 m2 · p95 = 16,5 m2 · p99 = 85,3 m2 · maks 266,6 m2 |
| **30 m2 esiginin bedeli** | **KONUTLU panden'in %16,9'u (152 gercek ev) "yardimci yapi" sayilirdi** |

Taban alani tek basina ayirmiyor: A'daki konutlarin %10'u 16,8 m2'nin altinda.

**Kabul edilen tanim:** `aantal_verblijfsobjecten == 0 AND taban_alani < 50 m2`.
Birinci kosul semantik olarak dogru ayiricidir ("icinde konut birimi yok");
ikincisi yalnizca guvenlik kapagidir — konutsuz panden'in en buyugu 266,6 m2'dir
(otopark/trafo olabilir) ve boyle bir yapi mikroklimayi etkiler.

### Temsil edicilik referansi

Referans **A geneli degerdir** (kullanici onayi): bina yogunlugu **0,1755**
(taban alani/alan) ve bouwjaar 1960-1975 orani **%75,1**. Aday kumesinin medyani
DEGIL — medyan referansi aday kumesine baglar, kural degisirse referans da kayar.

### On-kayitli yedek set (post-hoc ayar DEGIL)

Birincil set sifir aday verirse **onceden yazilmis** yedek uygulanir:
C-3 kurali "kare sinirini kesen pand yok" -> **"ic 120 x 120 m cekirdegi kesen
pand yok"**.

Gerekce hesaptan once kayda gecirilmistir: dis 15 m serit ENVI-met sonuclarinda
zaten yorumlanmayacaktir, dolayisiyla o seridi kesen bir bina yorumlanan
cekirdegi etkilemez. Hangi setin uygulandigi raporda acikca belirtilir.
**Ikisi de basarisiz olursa Bolum 12.6 failure raporu yazilir ve durulur;
kural kendiliginden daha fazla gevsetilmez.**

### Yukseklik kurali — ONAY BEKLIYOR

ENVI-met belgelerinden **dogrulanan** (tahmin edilmeyen) kurallar:

| Kural | Deger |
|---|---|
| LITE grid siniri | **50 x 50 x 25 hucre** |
| Model tepesi | **en yuksek binanin EN AZ 2 KATI**, en az 30 m |
| Telescoping | ancak **en yuksek bina yuksekliginden itibaren** baslayabilir |

Kaynak: envi-met.info bilgi bankasi (Total Model Height, Vertical Grid Layout)
ve envi-met.com LITE surum tanimi. Dogrulama tarihi 2026-09-21.

**Ajanin turettigi oneri** (aritmetik ajana ait, sayi belgede YOK):

| Hedef dz | Model yuksekligi (25 hucre) | Izin verilen H_max |
|---|---|---|
| <= 2 m | 50 m | **25 m** |
| <= 3 m | 75 m | 37,5 m |

**Onerilen: H_max <= 25 m.** Telescoping bu siniri yukari cekebilir ama
telescoping buyume katsayisi belgeden dogrulanamadi; dogrulanmamis katsayiya
dayali esik onerilmez (M-005 kurali).

**Bilinen risk:** Voorhof-Hoogbouw (`BU05032406`) yuksek bloklar iceriyor.
25 m kurali A'nin bu bolumunu C adayi olmaktan cikarabilir. Bu kabul edilebilir
— C, A'yi temsil eden bir ALT-ALANDIR — ancak yuksek bloklar tamamen dislanirsa
C'nin A'yi temsil etme iddiasi zayiflar ve bu **sinirlama olarak raporlanir**.

**Onay:** Kullanici, 2026-09-21 (kurallar ve erteleme). Yukseklik esigi
**onay bekliyor** — bkz. PENDING_DECISIONS P-011.

---

## D-012 · [2026-09-21] · C yukseklik esigi: 25 m birincil, 37,5 m on-kayitli yedek

**Karar:**

| Set | H_max | Hedef dz | Model yuksekligi (25 hucre) |
|---|---|---|---|
| **Birincil** | **25,0 m** | <= 2 m | 50 m |
| **Yedek (on-kayitli)** | **37,5 m** | <= 3 m | 75 m |

Dayanak: ENVI-met'in belgelenmis kurallari — LITE grid siniri 50 x 50 x 25;
model tepesi en yuksek binanin **en az 2 kati**; telescoping ancak en yuksek
bina yuksekliginden itibaren baslayabilir. (envi-met.info bilgi bankasi,
dogrulama 2026-09-21.)

### Yedek ne zaman uygulanir

| Tetikleyici | Kosul |
|---|---|
| **T-A** | Birincil kuralla gecerli aday sayisi **== 0** |
| **T-B** | Gecen adaylarin **hicbirinde** A'nin baskin yukseklik sinifi temsil edilmiyor |

`T-A VEYA T-B` -> yedek uygulanir. **Hangi setin ve hangi tetikleyicinin
calistigi raporda acikca belirtilir**; rapor bu ifadeyi tasimadan kapatilamaz.

### "Temsil" kriteri — hesaptan ONCE tanimlandi

**Yukseklik siniflari** (Hollanda yapi pratigi):

| Sinif | Aralik | Yaklasik kat |
|---|---|---|
| laagbouw | <= 10 m | 1-3 |
| middelhoogbouw | 10-25 m | 4-8 |
| hoogbouw | > 25 m | 9+ |

25 m siniri **bilerek** birincil esikle ayni secildi: boylece "hoogbouw baskinsa
birincil kural onu tanim geregi temsil edemez" iliskisi gorunur olur.

**Baskin sinif** = A'daki toplam **VBO** icinde payi en yuksek olan sinif.
Bina sayisi kullanilmadi: bina sayisi kucuk sira evler ve yardimci yapilar
tarafindan domine edilir; 200 daireli bir kule tek pand olarak sayilir. VBO payi
mahallenin fiilen nerede yasadigini yansitir ve D-008'in paydasiyla tutarlidir.
Seffaflik icin bina sayisi ve taban alani paylari da raporlanir; farkli sonuc
veriyorlarsa bu rapora yazilir.

**Bir aday baskin sinifi temsil ediyor sayilir ancak ve ancak:**

1. Adayin icinde o siniftan **en az 1 pand** varsa, **VE**
2. O sinifin adaydaki VBO payi, ayni sinifin A'daki VBO payinin **en az yarisi**
   ise (`share_in_candidate / share_in_A >= 0,50`).

Tek basina (1) yetersizdir — tek bir sinir binasi "temsil" sayilmamalidir.
Tek basina (2) de yetersizdir — A'daki pay cok kucukse oran kolayca saglanir.
**0,50 orani bir muhendislik secimidir, olculmus bir esik degildir** ve boyle
kaydedilmistir.

### Ozel durum: baskin sinif hoogbouw ise

Birincil kural (25 m) hoogbouw'u **tanim geregi** iceremez; T-B otomatik
tetiklenir. Yedek (37,5 m) yalnizca 25-37,5 m araligini kapsar. A'nin hoogbouw'u
37,5 m'yi asiyorsa **yedek de temsil saglayamaz** ve Bolum 12.6 isler.

O durumda kullaniciya sunulacak secenekler (simdiden kayitli):
(a) ENVI-met tam lisans — 25 hucre siniri kalkar (P-002 ile baglantili);
(b) C'nin iddiasini daraltmak — "A'nin dusuk katli bolumunu temsil eden
alt-alan" olarak yeniden tanimlamak;
(c) dz > 3 m kabul etmek — yaya seviyesi cozunurlugu duser.

### Bu gercek bir on-kayittir

Blok, A'nin yukseklik dagilimi **henuz bilinmeden** yazildi; 3DBAG verisi Asama
0.3'te inecek. Dolayisiyla "baskin sinif" ve "temsil" tanimlari sonuca bakilarak
ayarlanamamistir. **Git gecmisi bunu kanitlar:** bu commit, 3DBAG indirme
commit'inden oncedir. Bolum 12.2'nin istedigi sey tam olarak budur.

**Onay:** Kullanici, 2026-09-21.

---

## D-013 · [2026-09-21] · Girdimiz AHN5'tir; 3DBAG'in AHN surumunden bagimsiz

**Karar (3DBAG'e BAKILMADAN, on-kayit):** AHN5 B alanini **tam kapsiyorsa**
rekonstruksiyon girdimiz **AHN5** olur. 3DBAG'in hangi AHN surumunu kullandigi
bu secimi **degistirmez**.

**Gerekce:**

1. **Zamansal uyum.** AHN5, AHN4'e gore BAG anlik goruntusune (2026-09-21) daha
   yakindir. Aradaki fark ne kadar kucukse, Asama 1'de "BAG'da var ama nokta
   bulutunda yok" (veya tersi) turunden basarisiz rekonstruksiyon o kadar az olur.
2. **Birincil bagimsiz kontrolumuz 3DBAG DEGILDIR.** AGENTS.md Bolum 6, Asama 1
   icin iki kontrol tanimliyor: 3DBAG karsilastirmasi (**tutarlilik kontrolu**,
   cunku 3DBAG de AHN + roofer ile uretiliyor — Bolum 5 ve 12.10) ve **AHN nokta
   bulutuna dogrudan z-fark analizi** (bagimsiz kontrol). Girdi surumunu 3DBAG'e
   gore secmek, bagimli olani bagimsiz olanin onune koymak olurdu.

**Surum farki cikarsa ne yapilir:**
- Kriter **1-B** zaten `consistency_check` etiketlidir; bu etiket korunur.
- Olculen fark (3DBAG'in `b3_puntdichtheid_ahn4` / `b3_puntdichtheid_ahn5`
  alanlarindan) **AGENTS.md Bolum 5'e sinirlama olarak** ve
  `reports/01_geometry_validation.md`'ye yazilir.
- Raporda acikca belirtilir: 1-B'deki sapmanin bir kismi **bizim rekonstruksiyon
  kalitemizden degil, AHN4 ile AHN5 arasindaki farktan** kaynaklaniyor olabilir.
  Bu fark ayristirilamaz; ayristirilmis gibi sunulmaz.

**Dikkat — iki yonlu etki, ikisi de yazilacak:** Farkli AHN surumu kullanmak
karsilastirmayi bir anlamda **daha bagimsiz** yapar (farkli girdi verisi), ama
**daha az yorumlanabilir** kilar (fark konfaunde olur). Rapor iki yonu de belirtir;
yalnizca lehte olani yazmak Bolum 1 kural 5'in (belirsizligi gizleme) ihlalidir.

**Kapsama tam degilse:** D-014 oncesi 0.3 planinda kararlastirildigi gibi
**AHN4'e tamamen dusulur**; AHN4 ve AHN5 fayanslari **karistirilmaz**. Karisik
kullanim B icinde nokta yogunlugu ve ucus tarihinde mekansal sureksizlik yaratir;
Asama 1 yukseklik hatasi o sinirda sistematik olur ve sonradan ayristirilamaz.

### OLCULEN SONUC (2026-09-21, 3DBAG indirildikten sonra)

3DBAG collection **v2023.10.08**. B+50 m icindeki 7.376 bina icin `b3_pw_bron`:

| Kaynak | Bina | Pay | `b3_pw_datum` |
|---|---|---|---|
| **ahn5** | 6.999 | **%94,9** | 2023 |
| ahn3 | 261 | %3,5 | **2014** |
| ahn4 | 116 | %1,6 | 2020 |

`b3_pw_onvoldoende` = False (7.376/7.376) - 3DBAG nokta bulutunu tum binalar
icin yeterli bulmus.

**Sonuc:** Binalarin %94,9'unda 3DBAG bizimle **ayni kaynagi** (AHN5, 2023)
kullanmis. Kalan **377 bina** icin surum farki var ve bu, D-013'te ongorulen
sinirlamanin somut halidir. Kriter 1-B bu binalar icin **ayristirilarak**
raporlanacaktir (bkz. docs/validation_protocol.md 1.1b ve AGENTS.md Bolum 5).

**Onay:** Kullanici, 2026-09-21.

---

## D-014 · [2026-09-21] · Girdi kalite kapisi — genel ilke

**Karar:** AGENTS.md'ye **Bolum 12.12** olarak eklendi ve Bolum 1'in baglayici
kurallarina **11. kural** olarak islendi.

> Her asamada, girdi verisi islenmeden ONCE kalitesi olculur ve kaydedilir —
> kapsama, eksik deger, cozunurluk/yogunluk, tarih. Olcum, o veri tipinin resmi
> spesifikasyonu veya makul bir beklentiyle karsilastirilir; esik hesaptan once
> config'e yazilir. Girdi kapisini gecmeyen veriyle modelleme yapilmaz.

**Amac:** Sonraki asamada cikan bir hatanin **girdi mi yontem mi** kaynakli
oldugunu bastan ayirt edebilmek. Bu, Bolum 12.6'nin "nedeni siniflandir: veri
kaynakli mi, kod kaynakli mi, parametre mi, yontem mi" adimini **uygulanabilir**
kilar. Girdi kalitesi olculmemisse o siniflandirma sonradan yapilamaz.

**Ilk uygulama:** Asama 0.3'teki LAZ butunluk kontrolu (nokta yogunlugu, sinif
dagilimi, kapsama bosluklari, ucus tarihi).

**Planlanan sonraki uygulamalar** (kullanici tarafindan belirtildi):

| Veri | Kapi olcumu |
|---|---|
| KNMI saatlik | eksik saat orani, kesinti kumeleri |
| Sentinel-2 / Landsat | bulut orani, sahne kapsamasi, gecis tarihi |
| Stedin PC6 | bos/gizlenmis PC6 orani, birlestirilmis PC6 sayisi |

**Neden bu bir metodoloji degisikligi sayilir (Bolum 12.11):** Ilke, her asamanin
kabul kriterlerine yeni bir sinif ekliyor — "cikti kalitesi" yaninda **"girdi
kalitesi"**. Bu yuzden karar olarak kaydedildi ve AGENTS.md'ye islendi.

**Onay:** Kullanici, 2026-09-21.

---

## D-015 · [2026-09-21] · AHN LAZ girdi kalite kapisi: iki kademeli esik

> **GECIKMIS KAYIT.** Bu karar `config/acceptance_criteria.yml` ->
> `input_gate_ahn` blogunda `decision_ref: D-015` olarak ANILIYORDU ama
> DECISIONS.md'ye hic yazilmamisti. 2026-09-21'de sinif kodu dogrulamasi
> sirasinda fark edildi ve geriye donuk yazildi. Muhurleme commit'i
> (`77fdfbb`) olcum commit'inden (`0efe40b`) once gelir; Bolum 12.2 denetim
> izi bozulmamistir. Eksik olan yalnizca gerekce metniydi.
> Turetilen kural: bir config blogu `decision_ref` tasiyorsa, o D kaydi
> AYNI commit'te var olmalidir (bkz. MISTAKES.md M-008).

**Karar:** AHN LAZ verisi icin girdi kapisi **iki kademelidir**:

| Kademe | Kriter | Esik | Kaynak | Basarisizlikta |
|---|---|---|---|---|
| Sert kapi | 0-E | medyan >= 10 p/m2 | ahn.nl resmi spec (AHN4 tabani) | **FAIL** — Asama 1'e gecilmez |
| Beklenti | 0-F | medyan >= 20 p/m2 | kendi olcumumuz (37EN1 = 29,3) | **UYARI** — engellemez |

**Gerekce:** AHN5 icin resmi spesifikasyon **yoktur**. Tek belgelenmis sayi
AHN4'un tabanidir (10) ve gercek veriye gore cok gevsektir; bu yuzden bir kapi
degil **regresyon alarmi** olarak konmustur. Ikinci kademe bu boslugu doldurur
ama kaynagi kendi olcumumuz oldugu icin FAIL uretmez. AGENTS.md Bolum 2'deki
">=20 nokta/m2" ifadesi **kaynaksizdir** ve esik olarak KULLANILMAMISTIR
(M-005).

**Olculen (2026-09-21):** medyan **35,89 p/m2** -> 0-E PASS, 0-F PASS.

**Onay:** Kullanici, 2026-09-21 ("Iki kademeli onay").

---

## D-016 · [2026-09-21] · Bina sinifi (kod 6) orani ek raporlama sutunu

**Karar:** `reports/ahn_point_density_by_building.csv` dosyasina iki sutun
eklenir: `building_class_points` (ayakizi icindeki yalnizca sinif 6 noktalari)
ve `building_class_ratio` (bunlarin tum noktalara orani). **Esik yoktur**;
Asama 1'de `failed_buildings.csv` ile karsilastirilacaktir.

**Gerekce (kullanici tespiti):** Mevcut `roof_density_pts_m2` ayakizi icindeki
**tum siniflari** sayiyordu. Catiyi orten agac noktalari (sinif 1) da "cati
noktasi" olarak sayiliyordu; bu yuzden yogunluk **tam da rekonstruksiyonun
bozulmasi beklenen binalarda iyi gorunuyordu**. Metrik en cok ihtiyac duyulan
yerde yaniltiyordu.

**Bolum 12.2 ile iliskisi:** Bu bir **esik degildir** ve hicbir PASS/FAIL
kararina girmez; var olan bir esigi de gevsetmez. Olcumden sonra eklenmis
olmasi Bolum 12.2'yi ihlal etmez. Config'e `per_building_class_ratio` olarak
`threshold: none` ile yazilmistir.

**Olculen sonuc (2026-09-21):** medyan **0,874**, p10 **0,482**.
**67 bina (%5,3) tam 0,000** — yani ayakizi icinde bol nokta var ama **hicbiri
sinif 6 degil**.

**Beklenmeyen bulgu — neden "agac ortusu" DEGIL:** Sifir grubunun profili:

| | Sifir grubu (67) | Digerleri (1.192) |
|---|---|---|
| Ayakizi medyani | **8,0 m2** | 52,3 m2 |
| < 50 m2 olan | 64/67 | - |
| Konut VBO'lu | **%3,0** | %75,2 |
| Bouwjaar medyani | **2014** | 1966 |

Yani bunlar **kucuk, konut olmayan, sonradan yapilmis yardimci yapilardir**
(berging, bisiklet deposu, bahce evi) — agac altinda kalmis konutlar degil.
Kucuk ayakizi tek basina sebep DEGILDIR: A'daki 516 kucuk binanin (<50 m2)
sinif 6 orani medyani 0,854 ile buyuklerinkine (0,884) neredeyse esittir.
Sorun kucukluk degil, bu **belirli alt grup**tur.

**Muhtemel mekanizma (kesin degil):** AHN4 sartnamesi Bolum 9.2, BAG
pandenkaart'inda olmayan "tuinhuisjes zonder fundering" gibi nesnelerin
**"overig" (=1)** siniflandirilmasini emreder. Bu 67 yapi BAG'de vardir, yani
kural birebir uymuyor; AHN5'in siniflandirici davranisi belgelenmemistir.
**Sebep Asama 1'de kapatilacaktir**, simdi varsayim yazilmaz.

**Asama 1'e etkisi:** Bu 67 bina icin rekonstruksiyon basarisiz olursa, sebep
**ne girdi yogunlugu ne de bizim yontemimizdir** — AHN'in siniflandirma
politikasidir. Bu ucuncu kategori, Bolum 12.6'nin "nedeni siniflandir" adimina
eklenmistir.

**Onay:** Kullanici talimati, 2026-09-21.

---

## D-017 · [2026-09-21] · AHN sinif kodlari: 26 belgelendi, 14 cikarimdir

**Karar:** Sinif kodlarinin anlami `docs/ahn_class_codes.md` dosyasinda
belgeden dogrulanarak kayda gecirilir. Kanit duzeyi **acikca ayrilir**:

| Kod | Anlam | Kanit duzeyi |
|---|---|---|
| 0, 1, 2, 6, 9, **26** | nvt, Overig, Maaiveld, Bebouwing, Water, **Kunstwerken** | **BELGELENMIS** — AHN4 Besteksvoorwaarden Bolum 9 tablosu |
| **14** | hoogspanningsleiding (tel) | **CIKARIM** — AHN belgesinde YOK |

**Normatif kaynak:** *Besteksvoorwaarden inwinning landsdekkende dataset
AHN2020-2022*, Definitief v1.0, 28-05-2019, Bolum 9. ahn.nl'in **web
sayfalarinin hicbiri sayisal kod vermez**; yalnizca bu ihale sartnamesi verir.

**14 icin durum:** Sartname "ASPRS LAS 1.4 Standard LIDAR Point Classes"a uyum
sart kosar (orada 14 = Wire-Conductor) ve ahn.nl Dataroom "Vanaf het AHN4 zijn
ook hoogspanningsleidingen onderscheiden" der — ama **tabloya eklenmemistir**.
Veri kaniti cikarimi guclu bicimde destekler: maaiveld ustu medyan 17,31 m,
5 m hucre basina yalnizca 25,8 nokta, 407 x 1.235 m'lik dar bir koridor.
Yine de bu **belge degil cikarimdir** ve oyle etiketlenir (M-005).

**AHN5 SINIRLAMASI:** Hicbir kaynak **AHN5**'in siniflandirmasini
belgelemiyor. Yukaridaki yorumlar AHN4'ten tasinmistir; onlari destekleyen sey
belge degil, kendi veri olcumumuzdur. `ahn.nl/kwaliteitsbeschrijving` ayrica
"de definitie van de klasse gebouwen en de klasse kunstwerken in het AHN3 en
het AHN4 niet identiek is" diye uyarir — tanimlar surumler arasi degisiyor.
AGENTS.md Bolum 5'e sinirlama olarak islenmistir.

**Asama 1'i dogrudan etkileyen uc tanim** (ayrinti: `docs/ahn_class_codes.md`
Bolum 5):
1. **Sinif 6 "cati" degildir** — cepheler, dakkapeller, balkonlar ve gunes
   panelleri de 6'dir. Cati duzlemi ayrimi Asama 1'de yapilmalidir.
2. **Sinif 6 noktalari ayakizinin disina dusebilir** — sartname bunu acikca
   soyler. Kati `within` olcumumuz onlari kaciriyor; M-007'nin kenar etkisine
   ikinci bir mekanizma ekler.
3. **Sinif 6 BAG'den turetilmistir** — "ten tijde van de vlucht" BAG
   pandenkaart'i kullanilir. Dolayisiyla sinif 6, BAG'den **bagimsiz** bir
   gozlem DEGILDIR ve `building_class_ratio` BAG ayakizinin bagimsiz denetimi
   olarak kullanilamaz (Bolum 12.10).

**Asama 1 sinif secimi onerisi** P-012 olarak kayda alindi; **onaylanmamistir**.

**Onay:** Kullanici talimati ("Sinif 26 ve 14'u de AHN belgelerinden dogrula,
Asama 1 oncesi kapansin"), 2026-09-21.

---

## D-018 · [2026-09-21] · Sifir oran grubu iki alt gruba ayrilir; zemin orani sutunu eklenir

**Karar:** `building_class_ratio` sifir cikan binalar **tek bir grup olarak
raporlanmaz**. Ayakizi buyuklugune gore ikiye ayrilir ve buyuk olanlar
**tek tek** listelenir. Ayrica CSV'ye `ground_class_points` /
`ground_class_ratio` (ayakizi icindeki sinif 2 noktalari) eklenir.

| Alt grup | n | Tanim | Mekanizma |
|---|---|---|---|
| A | 64 | < 100 m2, `gebruiksdoel` **tamamen bos** | AHN siniflandirmasi bina saymamis |
| B | 3 | >= 100 m2 | **ucus sirasinda o ayakizinda bina yoktu** (2'si) / alcak yapi maaiveld sayilmis (1'i) |

100 m2 **bir kabul kriteri degildir**, raporlama ayrimidir; veride dogal
bosluk oradadir (sifir grubunda 28,5 m2 ile 109,0 m2 arasi bostur).

**Gerekce:** Onceki raporda 67 bina medyanlarla ozetlenmis ve "kucuk yardimci
yapilar" diye genellenmisti. Grupta 996 m2 ve 1.665 m2'lik **iki okul** vardi
(MISTAKES.md M-010). Ozet istatistik onlari tanim geregi gizledi.

**Inceleme sonucu** (`reports/00_stage_0_3_zero_ratio_investigation.md`):

| | `0503100000038184` | `0503100000041285` |
|---|---|---|
| gebruiksdoel | onderwijsfunctie | onderwijsfunctie, sportfunctie |
| bouwjaar / status | 2023 / in gebruik | 2026 / **niet ingemeten** |
| ayakizi ici zemin (sinif 2) orani | **%98,9** | **%62,1** |
| >8 m noktalarin cok donuslu orani | %100 | **%99,8** (kontrol binasi: %2,4) |
| 3DBAG kaydi | **yok** | **yok** |
| Sonuc | **Subat 2023'te bos arazi** | **Subat 2023'te agaclik/acik alan** |

**AHN5 ucus tarihi 2023-02-08/14** olarak LAZ `gps_time` alanindan olculdu
(baslik bayragi yanlis; ayrinti raporda).

**`bouwjaar` filtre olarak KULLANILMAZ:** A'da `bouwjaar >= 2023` olan 9
panddan 4'unun sinif 6 orani 0,57-0,82 arasindadir; `0503100000038177`
bouwjaar **2025** olmasina ragmen orani 0,785'tir. Dogru belirteç dogrudan
olcumdur (`building_class_ratio`, `ground_class_ratio`).

**Asama 1'e baglayici etkisi:** bu yapilarin basarisizligi `failed_buildings`
karsilastirmasinda **ucuncu kategori — kaynak/zaman uyusmazligi** olarak
etiketlenir; "girdi yogunlugu" veya "yontem" sayilmaz. Esik ve filtre
kurallari Asama 1 basinda, **hesaptan once** muhurlenir (P-013).

**Onay:** Kullanici talimati, 2026-09-21 ("Asama 1'e bu iki bina
aciklanmadan gecme").

---

## D-019 · [2026-09-21] · AHN5'te karsiligi olmayan 3 yapi Asama 1'den dislanir

**Karar:** P-013 secenek **(a)** onaylandi. Asagidaki 3 yapi Asama 1
rekonstruksiyonuna **girmez** ve AGENTS.md Bolum 5'te sinirlama olarak
raporlanir. Yerlerine basit kutu (LOD1) **uretilmez**.

| bag_id | ayakizi m2 | gebruiksdoel | bouwjaar | mekanizma |
|---|---|---|---|---|
| `0503100000041285` | 1.665,0 | onderwijs + sport | 2026 | ucus sirasinda bina yoktu |
| `0503100000038184` | 996,5 | onderwijs | 2023 | ucus sirasinda bina yoktu |
| `0503100000039655` | 109,0 | (islev kaydi yok) | 2002 | alcak yapi, maaiveld sayilmis |

**Gerekce — bu karar bir CIKARIMA DEGIL, DOGRUDAN OLCUME dayanir** (kullanici
tespiti): ayakizi ici nokta sinifi (sinif 6 = 0), maaiveld ustu yukseklik
dagilimi, zemin sinifi orani (%62,1 / %98,9) ve cok donuslu nokta orani
(%99,8 ve %100; kontrol binasinda %2,4). Bunlar gozlemdir. Bu yuzden karar
**Bolum 12.13 kapsamina girmez** ve gorsel dogrulamayi **beklemez**.

> Ayrim onemlidir: "bu ayakizinde sinif 6 noktasi yok ve noktalarin %98,9'u
> zemin sinifi" bir **olcumdur**; "bu yapi bir depodur" bir **cikarimdir**.
> Birincisi karar verebilir, ikincisi dogrulanmadan veremez.

**Neden LOD1 kutu uretilmiyor:** olculmemis bir geometriyi olculmus gibi
gosterirdi. Ayrica `0503100000041285`'in BAG ayakizi zaten
**`niet ingemeten`** statusundedir — yani sinirinin kendisi de gecicidir.

**Asama 3 (enerji) etkisi:** ucu de konut disidir (ikisi okul, birinin islev
kaydi yok). A'nin enerji karsilastirmasi PC6 **konut** tuketimi uzerinden
kuruldugu icin muhtemelen zaten kapsam disindalar — ama bu **acikca yazilir**,
sessizce dusurulmez (Bolum 12.8).

**Ayrica:** `building_class_ratio` sifir cikan yapilarin ne oldugu bir
cikarimdir ve **gorsel dogrulama ornegi** olusturulmustur. Orneklem seed'i
`config/acceptance_criteria.yml -> input_gate_ahn.visual_check.seed` altinda
**muhurludur** (28992). Bu dogrulama **P-012'yi** bekletir, D-019'u degil.

**Onay:** Kullanici, 2026-09-21.

---

## D-020 · [2026-09-21] · Dijital ikizin VERI DONEMI

**Karar:** Dijital ikizin **geometrisi** AHN5 ucus donemini temsil eder:
**2023-02-08 – 2023-02-14**. **Oznitelikler** BAG anlik goruntusudur:
**2026-09**. Arada **3,5 yil** vardir ve bu fark **her raporda acikca
yazilir**.

**Ucustan sonra yapilmis veya degismis binalar:**
- **"geometrisi yok (ucus sonrasi)"** etiketiyle **listelenir**
- **modellenmez**
- web arayuzunde **ayri isaretlenir** (ayri katman/renk, bag_id ve gerekce
  tiklanabilir)

**Gerekce:** Model "bugunun Voorhof'u" degildir; **2023 basinin geometrisi +
2026 oznitelikleridir**. Bu fark gizlenirse, Asama 1'de basarisiz cikan bir
bina "yontem hatasi" sanilir; Asama 3'te bir tuketim sapmasi "model hatasi"
sanilir. Oysa sebep veri donemidir. Bolum 12.6'nin "nedeni siniflandir" adimi
bu ayrim olmadan uygulanamaz.

**Ucus tarihi nasil belirlendi:** LAZ nokta kayitlarindaki `gps_time`
alanindan. `global_encoding` bit 0 "GPS hafta zamani" diyor ama **bayrak
yanlistir** — degerler hafta zamani ust siniri olan 604.800'un cok uzerinde
(359,9-360,4 milyon). `lasinfo` ayni celiskiyi kendi uyarisiyla bildiriyor.
Adjusted Standard GPS Time olarak cozuldugunde Subat 2023 cikiyor; bu, Delft
icin bilinen AHN5 kampanyasiyla tutarlidir.

**Nereye islendi:**
- `AGENTS.md` Bolum 5 — sinirlama satiri
- `AGENTS.md` Bolum 13.1 — asama sonu raporu formatina `veri donemi` alani
- `AGENTS.md` Asama 5 — web arayuzu gereksinimi
- `AGENTS.md` Bolum 10 — kontrol listesi maddesi
- Her raporun basina "VERI DONEMI" notu

**Kapsam notu:** Bu karar AHN5'e ozgu degildir. KNMI, Sentinel/Landsat ve
Stedin verileri eklendiginde her birinin **kendi donemi** ayni bicimde
yazilacaktir; "veri donemi" notu tek bir tarih degil, **kaynak basina
donem listesi** haline gelir.

**Onay:** Kullanici, 2026-09-21.
