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
