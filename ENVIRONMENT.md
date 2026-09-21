# ENVIRONMENT.md — Yazilim surumleri ve kurulum

> AGENTS.md Bolum 8: bu dosya yazilim surumlerini, Docker image/tag bilgisini ve
> kurulum adimlarini tutar.
>
> **MISTAKES.md M-002 kurali:** buradaki her surum numarasi `conda run` / `--version`
> ciktisindan **kopyalanir**, elle yazilmaz. Kurulum komutunun cikis kodu basari
> kaniti sayilmaz; ortam fiilen yoklanir.

**Son olcum: 2026-09-21** · Asama 0.1

---

## 1. Donanim (olculen)

| Bilesen | Deger |
|---|---|
| CPU | Intel Core i5-12450H |
| Cekirdek | 8 fiziksel / 12 mantiksal |
| RAM | 15,7 GB |
| GPU 1 | NVIDIA GeForce RTX 3050 Laptop — 4 GB VRAM (sürücü 32.0.16.1078) |
| GPU 2 | Intel UHD Graphics — tumlesik (sürücü 31.0.101.5592) |
| Disk (C:) | 452,9 GB toplam / **31,6 GB bos** |
| OS | Windows 11 Home Single Language 10.0.26200 |

### Donanim kisitlarinin projeye etkisi

| Kisit | Etki | Nerede ele alindi |
|---|---|---|
| **31,6 GB bos disk** | AHN5 LAZ + 3DBAG + Asama 4 ciktilari icin dar. Indirme yarida kesilirse bozuk dosya olusur | `reports/PENDING_DECISIONS.md` → **P-003 (YUKSEK aciliyet)** |
| **15,7 GB RAM** | Kentsel CFD icin dar butce; mesh hucre sayisi bellek testiyle olculmeli | P-001 |
| 8 fiziksel cekirdek | OpenFOAM paralel bolme sayisini sinirlar | P-001 |
| 4 GB VRAM | OpenFOAM CPU tabanlidir; GPU burada belirleyici **degil** | P-001 |

**B ve D alan boyutlari bu olcumle SABITLENMEMISTIR.** AGENTS.md Bolum 3'e gore D
domeni en yuksek bina yuksekligi H'ye baglidir ve H, Asama 0.3'te BAG/3DBAG
indirilmeden bilinemez. Karar Asama 3 sonuna ertelendi — bkz. P-001.

---

## 2. Sistem araclari (olculen)

| Arac | Surum | Konum / not |
|---|---|---|
| git | 2.x | `C:\Program Files\Git\cmd\git.exe` |
| conda | 26.1.0 | miniconda3 |
| Docker | 29.7.2 (build a7dcaa6) | Asama 1 roofer/geoflow icin gerekli |
| Sistem Python | 3.13.14 | **Proje icin kullanilmaz** — `voorhof-twin` ortami kullanilir |
| QGIS | **KURULU DEGIL** | Asama 0.2 (AOI cizimi) ve Asama 3 (UMEP/SOLWEIG) icin gerekecek |
| PDAL | **KURULU DEGIL** | `voorhof-twin` ortamina eklenecek veya Docker ile |
| gh (GitHub CLI) | **KURULU DEGIL** | Zorunlu degil; git uzerinden calisiliyor |

---

## 3. Python ortami (Karar D-001)

**Ortam adi:** `voorhof-twin` · **Kanal:** conda-forge · **Tanim:** `environment.yml`

```bash
conda env create -f environment.yml     # kurulum
conda activate voorhof-twin             # aktive
conda env update -f environment.yml --prune   # guncelleme
```

### Kurulum sonrasi ZORUNLU dogrulama (M-002)

```bash
conda run -n voorhof-twin python -c "import yaml, geopandas, rasterio, laspy, pyproj"
```

`conda env create` **basarisiz olsa bile cikis kodu 0 donebilir.** Ortamin kuruldugu
yalnizca bu import testiyle dogrulanir.

### Cozulen paket surumleri (olculen 2026-09-21)

Asagidaki surumler kurulu ortamdan `importlib.metadata` ile **okunmustur**,
elle yazilmamistir (M-001 / M-002 kurali).

| Paket | Surum |
|---|---|
| python | 3.12.14 |
| pyyaml | 6.0.3 |
| numpy | 2.5.3 |
| pandas | 3.0.6 |
| geopandas | 1.1.4 |
| shapely | 2.1.2 |
| fiona | 1.10.1 |
| pyproj | 3.8.0 |
| rasterio | 1.5.1 |
| laspy | 2.7.0 |
| lazrs-python | 0.8.2 |
| gdal | 3.13.3 |
| requests | 2.34.2 |
| python-dotenv | 1.2.3 |
| pytest | 9.1.1 |

**Paket adi tuzagi (M-002):** LAZ arka ucunun PyPI adi `lazrs`, conda-forge adi
`lazrs-python`. Kurulu dagitimin metadata adi ise `lazrs`.

**Kesin kilit dosyasi:** `conda env export` ciktisi henuz commit edilmedi.
`TODO_ASAMA_0_5`: ortam stabillestiginde `environment.lock.yml` uretilecek.

---

## 3.1 PROJ / GDAL veri dizini — KRITIK DUZELTME

**Sorun (MISTAKES.md M-003):** Bu makinedeki PostgreSQL/PostGIS 3.6 kurulumu sistem
genelinde `PROJ_LIB` ve `GDAL_DATA` tanimliyor ve conda ortamindaki PROJ'u ele
geciriyor. Duzeltme olmadan `EPSG:28992` **hic olusturulamiyor**.

**Cozum:** `src/common/proj_env.py`, `src.common` paketi ice aktarildiginda otomatik
calisir ve bu degiskenleri conda ortaminin kendi dizinine sabitler. Sistem genelindeki
PostgreSQL ayarlarina **dokunulmaz** (PostGIS kurulumu bozulmaz).

**Dogrulama (duzeltme sonrasi, olculen):**

| Test | Sonuc |
|---|---|
| PROJ veri dizini | `<conda-env>/Library/share/proj` |
| EPSG:28992 | Amersfoort / RD New |
| EPSG:7415 | Amersfoort / RD New + NAP height |
| EPSG:4326 | WGS 84 |
| RD(84000, 447000) -> WGS84 | lon 4.353121, lat 52.006822 (Delft) |

**Uyari:** `import pyproj` basarili olmasi PROJ'un calistigini **gostermez**.
Ortam dogrulamasi her zaman gercek bir CRS olusturarak yapilir.

---

## 4. Docker image'lari (Asama 1+)

| Amac | Image | Tag | Durum |
|---|---|---|---|
| LOD2 rekonstruksiyon | roofer / geoflow | `TODO_ASAMA_1` | Henuz cekilmedi |
| Geometri QC | val3dity | `TODO_ASAMA_1` | Henuz cekilmedi |
| Veritabani | 3DCityDB v5 + PostGIS | `TODO_ASAMA_2` | Henuz cekilmedi |
| CFD | OpenFOAM | `TODO_ASAMA_4` | Donanim karari bekliyor (P-001) |

Tag'ler `latest` olarak birakilmaz — cekilen imajin **kesin digest'i** buraya yazilir.
`latest` tekrarlanabilirligi bozar.

---

## 5. Ortam degiskenleri

Gercek degerler `.env` dosyasinda tutulur, **repoya girmez**. Sablon:
`.env.example`. Gerekli anahtarlar: `KNMI_API_KEY`, `EPONLINE_API_KEY`,
`CDSE_USERNAME`/`CDSE_PASSWORD`, `USGS_USERNAME`/`USGS_TOKEN`.

Okuma: `src/common/config.py` → `env_secret(name)`. Degisken tanimsizsa acik hata
verir, sessizce bos dizgiyle devam etmez.
