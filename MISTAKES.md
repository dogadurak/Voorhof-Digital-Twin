# MISTAKES.md — Hata defteri

> Bu dosya projenin **kurumsal bellegidir** (AGENTS.md Bolum 14).
> Ajan oturumlar arasinda hatirlamaz; ogrenme ajanin hafizasinda degil burada tutulur.
>
> **Temel kural (14.1):** Her hata bir kez yapilabilir. Ikinci kez yapilmasi ayri ve
> daha agir bir ihlaldir.
>
> **Her oturumun ilk isi (14.4):** Bu dosyayi oku, calisilacak asamayla ilgili ACIK
> kayitlari listele, her birinin turetilmis kuralini tek cumleyle tekrarla. Bu adim
> atlanirsa oturum gecersizdir.

Kayit formati Bolum 14.2'de tanimlidir. "Kucuk hata" ayrimi yoktur (14.3).

---

## Ozet tablo

| ID | Tarih | Asama | Konu | Durum | Tekrar |
|---|---|---|---|---|---|
| M-001 | 2026-09-21 | 0.1 | Dogrulanmamis paket surumu yazildi | KAPALI | 0 |
| M-002 | 2026-09-21 | 0.1 | conda-forge'da olmayan paket adi varsayildi | KAPALI | 0 |
| M-003 | 2026-09-21 | 0.1 | Sistem PROJ_LIB pyproj'u ele gecirdi, CRS tamamen bozuktu | KAPALI | 0 |
| M-004 | 2026-09-21 | 0.2a | WFS filtresi sessizce yok sayildi, 61 MB ulke geneli veri indi | KAPALI | 0 |
| M-005 | 2026-09-21 | 0.2a | Servis semasi dogrulanmadan config'e olgu yazildi | KAPALI | 0 |
| M-006 | 2026-09-21 | 0.2 | Konsol kodlamasi bir DOGRULAMA log satirini sessizce dusurdu | KAPALI | 0 |

---

## M-001 · [2026-09-21] · Asama 0.1

**Ne oldu:**
`requirements.txt` yazilirken CityJSON dogrulayicisi icin `cjvalpy==0.5.0` satiri
eklendi. Ne paket adi ne de surum numarasi PyPI'da dogrulanmisti; surum numarasi
tamamen uydurulmustu.

**Kok neden:**
"Makul gorunen" bir surum numarasi yazmak, hicbir sey yazmamaktan daha tamamlanmis
hissettirdi. Oysa AGENTS.md Bolum 1 kural 1 acikca sayi uydurmayi yasakliyor ve
bir paket surumu de bir sayidir.

**Neden fark edilmedi (edilseydi):**
Hata commit'ten once ajanin kendi kontrolunde yakalandi, ama kurulum denenmis olsaydi
`pip install` cozunurluk hatasiyla dusecek ve zaman kaybettirecekti. Daha kotusu:
var olan ama YANLIS bir surum secilseydi sessizce kurulur ve Asama 1'de beklenmedik
davranis olarak geri donerdi.

**Turetilen kural:**
Bir paket adi veya surumu bir bagimlilik dosyasina yazilmadan once paket dizininde
(PyPI / conda-forge) **fiilen dogrulanir**. Dogrulanamiyorsa sayi yazilmaz;
`TODO_ASAMA_N` notu birakilir ve o asamada cozulur.

**Nerede uygulanir:** `requirements.txt`, `environment.yml`, `ENVIRONMENT.md`

**Otomatik kontrol:**
`src/qa/check_compliance.py` (Asama 0.5) — bagimlilik dosyalarinda pin'li her satirin
karsiligi kurulu ortamda var mi, surum eslesiyior mu?

**Durum:** KAPALI (satir kaldirildi, yerine `TODO_ASAMA_1` notu yazildi)

---

## M-002 · [2026-09-21] · Asama 0.1

**Ne oldu:**
`environment.yml` icine `lazrs` paketi eklendi. Bu, `laspy` icin LAZ sikistirma arka
ucunun **PyPI'daki** adidir; conda-forge'da bu adda paket yoktur. `conda env create`
solver asamasinda `PackagesNotFoundError` ile dustu, ortam kurulmadi.

**Kok neden:**
PyPI paket adi ile conda-forge paket adinin ayni oldugu varsayildi. Bu varsayim
genelde dogru, ama sistematik degil — ve M-001 ile ayni kok nedene sahip:
**dogrulanmadan yazmak.**

**Neden fark edilmedi:**
Iki katmanli bir maskeleme oldu:
1. Komut arka planda calistirildi, cikti aninda okunmadi.
2. **`conda env create` basarisiz olmasina ragmen cikis kodu 0 dondu.** Arka plan
   gorevi "completed (exit code 0)" olarak bildirildi; basarili sanildi. Hata ancak
   ortamdan surum okunmaya calisilirken (`EnvironmentLocationNotFound`) ortaya cikti.

**Turetilen kural (iki parcali):**
1. Bir paket conda-forge'a eklenmeden once `conda search -c conda-forge <ad>` ile
   varligi dogrulanir. PyPI adi conda adi sayilmaz.
2. **Kurulum komutlarinin cikis kodu basari kaniti sayilmaz.** Her ortam kurulumundan
   sonra ortam FIILEN yoklanir: `conda run -n <env> python -c "import <paket>"`.
   Bu, AGENTS.md Bolum 13.2'nin "tahmin etme, fiilen calistir" kuralinin ortam
   kurulumuna uygulanmis halidir.

**Nerede uygulanir:** `environment.yml`, `ENVIRONMENT.md`, her ortam kurulum adimi

**Otomatik kontrol:**
`src/qa/check_compliance.py` (Asama 0.5) — `environment.yml`'deki her bagimlilik
kurulu ortamda import edilebiliyor mu? ENVIRONMENT.md'deki surumler `conda run`
ciktisiyla birebir esliyor mu?

**Durum:** KAPALI (dogru paket adi arastirildi ve `environment.yml` duzeltildi;
ortam kurulumu fiilen dogrulandi)

**Not — ortak kok neden:**
M-001 ve M-002 ayni koke sahip: *dogrulanmadan yazmak*. Ucuncu kez tekrarlanirsa
Bolum 14.5 geregi bu adim otomatiklestirilir veya `docs/manual_steps.md`'ye tasinir.
Mevcut ortak savunma: **bagimlilik dosyalarina yazilan her ad ve surum, once paket
dizininde aranir, sonra kurulumdan sonra ortamda dogrulanir.**

---

## M-003 · [2026-09-21] · Asama 0.1

**Ne oldu:**
Yeni kurulan conda ortaminda `pyproj` hicbir CRS'i olusturamiyordu.
`CRS.from_user_input("EPSG:28992")` su hatayla dusuyordu:
`Internal Proj Error: proj_create: no database context specified`.
Yani projenin temel CRS'i (RD New) bile tanimlanamiyordu.

**Kok neden:**
Makinede kurulu PostgreSQL/PostGIS 3.6, sistem genelinde iki ortam degiskeni
tanimliyor:

    PROJ_LIB  = C:/Program Files/PostgreSQL/18/share/contrib/postgis-3.6/proj
    GDAL_DATA = C:/Program Files/PostgreSQL/18/gdal-data

Bu degiskenler conda ortamindaki PROJ kurulumunu ele geciriyor. Conda ortaminin
kendi `proj.db` dosyasi mevcut ve saglam (10,3 MB), ama PROJ onun yerine
PostGIS'in veritabanina yonlendiriliyor ve surum uyumsuzlugu nedeniyle onu hic
yukleyemiyor.

**Neden fark edilmedi (neredeyse):**
Paket import testi (`import pyproj`) **GECTI**. Kurulumun saglikli oldugu
izlenimi verdi. Ariza yalnizca gercek bir CRS olusturulmaya calisildiginda
ortaya cikti. Yani "paket import ediliyor" kontrolu bu ariza sinifi icin
YETERSIZDIR.

**Tehlikeli sessiz varyanti:**
Bu vakada hata gurultuluydu (exception firladi) ve bu SANSTI. `PROJ_LIB` uyumlu
ama FARKLI surumde bir veritabanina isaret etseydi, donusumler calisir fakat
farkli datum/grid kaymasi kullanirdi. Koordinatlar sessizce 1-2 m kayardi ve bu,
AGENTS.md Bolum 14.6'daki **"CRS / yukseklik datumu"** hata sinifinin tam olarak
kendisidir: toplu RMSE bu kaymayi maskeler.

**Turetilen kural (uc parcali):**
1. Proje PROJ/GDAL veri dizinlerini **kendi ortamina sabitler**; sistem genelindeki
   degiskenlere guvenilmez. Uygulama: `src/common/proj_env.py`, `src.common` paketi
   ice aktarildiginda **otomatik** calisir — bir scriptin unutmasi mumkun degil.
2. Ortam dogrulamasi `import <paket>` ile BITMEZ. Kutuphanenin **fiili isini**
   yapabildigi test edilir: bu projede `EPSG:28992` olusturulabiliyor ve bilinen
   bir koordinat dogru donusuyor mu?
3. Kullanilan PROJ veri dizini her calistirmada **loglanir**. Dizin degisirse
   sonuclar degisebilir; bu bilgi `.meta.json`'a da girer.

**Nerede uygulanir:** `src/common/proj_env.py`, `src/common/__init__.py`,
`ENVIRONMENT.md`, her CRS donusumu yapan script

**Otomatik kontrol:**
`src/qa/check_compliance.py` (Asama 0.5) — PROJ veri dizini conda ortaminin icinde
mi? `EPSG:28992` ve `EPSG:7415` olusturulabiliyor mu? Bilinen referans koordinat
beklenen degere donuyor mu?

**Dogrulama (2026-09-21, duzeltme sonrasi):**

| Test | Sonuc |
|---|---|
| PROJ veri dizini | `<conda-env>/Library/share/proj` (ortam ici) |
| EPSG:28992 | Amersfoort / RD New |
| EPSG:7415 | Amersfoort / RD New + NAP height |
| RD(84000, 447000) -> WGS84 | lon 4.353121, lat 52.006822 — Delft, dogru konum |

**Durum:** KAPALI (duzeltme yazildi, otomatiklestirildi ve fiilen dogrulandi)

---

## M-004 · [2026-09-21] · Asama 0.2a

**Ne oldu:**
PDOK CBS WFS'ine `CQL_FILTER=gemeentenaam='Delft'` parametresiyle sorgu atildi.
Servis parametreyi **sessizce yok saydi**, HTTP 200 dondu ve **61,7 MB** ile
Hollanda'nin TUM wijken katmani indi. Ayni hata `cql_filter` (kucuk harf) ile
tekrarlandi ve 2,9 MB daha indi.

**Kok neden:**
Bu PDOK WFS'i GeoServer CQL eklentisini sunmuyor; yalnizca standart **OGC Filter
Encoding** (`filter=<fes:Filter>...`) destekliyor. Desteklenmeyen parametre hata
dondurmuyor, **yok sayiliyor** — istek gecerli bir "filtresiz GetFeature" olarak
islenip tum katmani donduruyor.

**Neden tehlikeli:**
1. **HTTP 200 basari sanildi.** M-002'nin ayni kaliba sahip tekrari: cikis kodu /
   durum kodu, istenen isin yapildiginin kaniti degil.
2. **D-006'nin korudugu hata sinifinin ta kendisi.** D-006 "hicbir veri kumesi ulke
   geneli indirilmez" diyor. Sessizce yok sayilan bir bbox/filtre, bu karari
   kullanici hicbir sey yanlis yapmadan ihlal ettirir.
3. Asama 0.3'te ayni sey AHN veya BAG'de olsaydi, 31 GB'lik diskte onlarca GB'lik
   ulke geneli indirme baslar ve diski doldururdu.

**Turetilen kural (uc parcali):**
1. **Her WFS/API sorgusuna daima bir ust sinir konur** (`count=N`, `maxFeatures`,
   `Range` vb.). Filtre calismazsa zarar sinirli kalir.
2. **Filtrenin uygulandigi ciktidan DOGRULANIR**, istekten degil: donen kayitlarin
   filtre kosulunu gercekten sagladigi kontrol edilir. Saglamiyorsa indirme
   gecersizdir ve `data/raw/`'a yazilmaz.
3. **Indirme oncesi beklenen boyut kontrol edilir** (HTTP `Content-Length` veya
   ozellik sayisi sorgusu `resultType=hits`). Beklenenden buyukse indirme yapilmaz,
   durum raporlanir.

**Nerede uygulanir:** `src/00_acquisition/` altindaki tum indirme scriptleri

**Otomatik kontrol:**
`src/qa/check_compliance.py` (Asama 0.5) — `DATA_LOG.md`'deki her kayit icin: sorgu
parametresi yazilmis mi, donen ozellik sayisi beklenen mertebede mi, filtre
dogrulamasi yapilmis mi?

**Ek bulgu (ayni oturumda dogrulandi):** Ad tahmin etmek de ayni tuzak.
`wijknaam='Voorhof'` sorgusu 0 kayit dondu; CBS'teki gercek ad **"Wijk 24 Voorhof"**.
Filtre dogru calistigi icin bu sessiz degil gurultulu bir hataydi — kural 2 sayesinde
yakalandi.

**Durum:** KAPALI (OGC Filter Encoding'e gecildi, `count` siniri ve cikti dogrulamasi
uygulandi; bos indirmeler `data/raw/`'a yazilmadi)

---

## M-005 · [2026-09-21] · Asama 0.2a

**Ne oldu:**
Kullanicinin 0.2 planini degerlendirirken "gebruiksdoel BAG pand uzerinde DEGIL,
verblijfsobject uzerindedir" denildi ve bu **olgu olarak** muhurlenen config'e yazildi
(stage_0_2 -> kriter 0.2-B -> computation). Veri indirildiginde PDOK'un bag:pand
katmaninin gebruiksdoel, bouwjaar ve aantal_verblijfsobjecten alanlarini **tasidigi**
goruldu.

**Kok neden:**
BAG'in kavramsal veri modeli ile PDOK WFS'inin sundugu sema karistirildi. Kavramsal
modelde gebruiksdoel gercekten verblijfsobject ozniteligidir; PDOK bu WFS'te veriyi
denormalize edip pand'a da tasimistir. Iddia, servisin DescribeFeatureType ciktisi
veya bir ornek kaydi **gorulmeden** yazildi.

**M-001/M-002 ile ayni kok neden: dogrulanmadan yazmak. UCUNCU TEKRAR.**
Bolum 14.5 geregi bu adim artik insan disiplinine birakilmaz, otomatik kontrole baglanir.

**Neden fark edilmedi:**
Sema dogrulamasi yapildi ama yalnizca **katman adi** duzeyinde (GetCapabilities).
**Oznitelik** duzeyinde dogrulama CBS katmani icin yapildi, BAG icin atlandi.
Kismi dogrulama, tam dogrulama sanildi.

**Sonucu — yanlis gerekce, dogru yontem:**
Olcum, verblijfsobject kullanmanin dogru secim oldugunu gosterdi ama **bambaska bir
nedenle**: pand'larin %40,6'si (3.124 adet) aantal_verblijfsobjecten = 0 olan yardimci
yapilardir (garaj, trafo, depo, otopark) ve gebruiksdoel'leri bostur. Pand duzeyinde
woonfunctie orani bu yuzden %50,5'te kalir ve **>=%90 esigi hicbir karede saglanamaz** —
kriter matematiksel olarak uygulanamaz hale gelirdi.

Gerekce duzeltilmeden birakilamaz: sonraki oturum yanlis gerekceye dayanip yanlis
genelleme yapabilir.

**Turetilen kural:**
Bir veri kaynaginin semasi hakkindaki her iddia, o kaynagin **kendi ciktisindan**
dogrulanir; kavramsal veri modeli bilgisi yeterli degildir. Uygulama: her yeni katman
icin indirmeden once DescribeFeatureType veya count=1 ile ornek kayit cekilir,
oznitelik listesi loglanir ve DATA_LOG.md'ye yazilir.

**Nerede uygulanir:** src/00_acquisition/ tum indirme scriptleri,
config/acceptance_criteria.yml icindeki her computation notu

**Otomatik kontrol:**
src/qa/check_compliance.py (Asama 0.5) — config'te bir oznitelik adi geciyorsa,
o oznitelik ilgili ham dosyada gercekten var mi?

**Durum:** KAPALI (2026-09-21).
- Config'teki yanlis gerekce duzeltildi: `computation_correction` alani eklendi,
  dogru gerekce (`why_not_pand_level`) yazildi. Karar D-008.
- **Bolum 14.5 uygulandi** (ucuncu tekrar -> otomatiklestirme, kullanici onayi
  2026-09-21): indirme scriptleri bundan sonra her katmanin **oznitelik listesini**
  loglar ve `DATA_LOG.md`'ye yazar. Artik bir sema iddiasi, o katmanin gercek
  oznitelik listesi kayda gecmeden config'e giremez.
- Ayni oturumda kural fiilen ise yaradi: status alan adi ve degerleri indirilen
  veriden dogrulandi ve kullanicinin "yikilmis binalar var" varsayiminin bu veri
  icin gecersiz oldugu olculdu (D-008).

---

## M-006 · [2026-09-21] · Asama 0.2

**Ne oldu:**
`build_aoi.py` calisirken `A ∩ sanayi = 0.0000 ha` satiri **terminale hic
yazilmadi**. Bu satir, dislanan sanayi buurt'larinin A ile kesismedigini kanitlayan
DOGRULAMA satiriydi. Yerine stderr'e bir `--- Logging error ---` izi dustu.

**Kok neden:**
Windows + Turkce yerel ayar -> konsol kodlamasi **cp1254**. `logging.StreamHandler`
varsayilan olarak `sys.stdout`'un kodlamasini kullanir; cp1254 `∩` (U+2229)
karakterini kodlayamaz ve `UnicodeEncodeError` firlatir. `logging` bu hatayi
yutar, satiri ATLAR ve calismaya devam eder. Cikis kodu 0'dir.

**Neden tehlikeli:**
Kaybolan satir bir suslemeydi degil, bir **kanitti**. Log'a bakan biri satiri
gormedigi icin "kontrol yapilmadi" mi yoksa "kontrol yapildi ama yazilamadi" mi
oldugunu ayirt edemez. Dosya logu UTF-8 oldugu icin orada duruyordu — yani iki
sink AYRISMISTI ve bu ayrisma sessizdi. Asama 0.1 kabul kriteri 0.1-C "iki sink'e
de yaziliyor" diyordu; o test yalnizca ASCII bir satirla yapilmisti.

**Turetilen kural (iki katmanli, tek katman yeterli degil):**
1. `logging_setup.py` konsol akisini UTF-8'e zorlar:
   `sys.stdout.reconfigure(encoding="utf-8", errors="replace")`.
   `errors="replace"` kritiktir: kodlanamayan karakter olsa bile satir **asla
   dusmez**, karakter yerine isaret konur.
2. `environment.yml` -> `variables: PYTHONUTF8: "1"`. Ortam aktive edildiginde
   Python'un tum I/O'su UTF-8 olur.

Iki katman gerekli cunku conda ortam degiskenleri **yalnizca aktivasyonla** gelir;
`python.exe` dogrudan cagrildiginda (bu oturumda yapildigi gibi) `PYTHONUTF8`
uygulanmaz. Kod icindeki duzeltme o durumu da kapsar.

**Ek ders — hatali test:**
Ilk dogrulama denemem `contextlib.redirect_stdout` ile yapildi. Bu, `sys.stdout`'u
`StringIO` ile degistirdigi icin `reconfigure` cagrisi `AttributeError` firlatti,
sessizce yutuldu ve test **gercek konsolu hic sinamadan** "GECTI" dedi.
**Bir kodlama sorununu, akisi degistirerek test edemezsin.** Dogru test, gercek
`sys.stdout` uzerinde yapilir ve `sys.stdout.encoding` degerini kontrol eder.

**Nerede uygulanir:** `src/common/logging_setup.py`, `environment.yml`,
`ENVIRONMENT.md` T-1

**Otomatik kontrol (kullanici talimati):**
`src/qa/check_compliance.py` (Asama 0.5) — logging testi ASCII disi karakter
iceren bir satir (`∩ ≤ °C m²`) loglar ve **iki sink'e de**
ulastigini dogrular. `sys.stdout.encoding` ayrica raporlanir. Kriter 0.1-C bu
testle guclendirilir; yalnizca ASCII ile yapilan sink testi yetersizdir.

**Dogrulandi (2026-09-21):**

| Senaryo | Baslangic kodlama | setup_logging sonrasi | `∩ ≤ °C m²` iki sink |
|---|---|---|---|
| `python.exe` dogrudan | cp1254 | utf-8 | GECTI |
| `PYTHONUTF8=1` | utf-8 | utf-8 | GECTI |

`build_aoi.py` yeniden calistirildi; `A ∩ sanayi = 0.0000 ha` satiri hem
terminalde hem disk logunda gorundu, `Logging error` izi kalmadi.

**Durum:** KAPALI (iki katmanli duzeltme yazildi ve fiilen dogrulandi;
kalici otomatik kontrol Asama 0.5'e planlandi)
