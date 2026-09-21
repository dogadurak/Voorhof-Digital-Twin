# DECISIONS.md — Metodolojik kararlar

> AGENTS.md Bolum 12.11: asagidakiler kullanici onayi olmadan degistirilemez —
> yeni veri kaynagi, yeni AOI, CRS stratejisi, kabul esigi veya metrik, dogrulama
> metodolojisi, lisans kosulu, ucretli/ogrenci-lisansli yazilim, temel model
> varsayimi, cekirdek cikti tanimi, yuksek hesaplama kaynagi gerektiren calistirma.
>
> **Her onaylanan degisiklik buraya tarih ve gerekceyle yazilir.**

> **SONRAKI BOS ID: D-009**  — yeni karar yazmadan once bu satiri oku ve guncelle.
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
