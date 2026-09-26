# ATTRIBUTION.md — Veri ve yazilim kaynaklari

> AGENTS.md Bolum 7: "Her veri ve yazilimin kesin lisansi ve yeniden dagitim kisiti
> buraya yazilir. Bir bilesenin lisansi web arayuzunun yayinini engelliyorsa
> **yayin asamasina gecilmez**, durum raporlanir."
>
> Bolum 6, Asama 5: bu dosya otomatik uretilir ve web arayuzunde gosterilir.

**Durum (2026-09-27):** Asama 0.3'te **indirilen** verilerin (AHN5, BAG, CBS, 3DBAG)
lisans ve atif alanlari kaynagindan dogrulanip dolduruldu. Henuz **indirilmemis**
veriler `TODO_EDINIMDE` olarak isaretli: surumu secilmemis bir verinin lisansi
dogrulanamaz; bu alanlar veri fiilen indirilirken doldurulur. AGENTS.md Bolum 1
kural 1 geregi **dogrulanmamis lisans adi yazilmaz** — tahmin edilen bir lisans,
yanlis attribution ve yayin hakki ihlali demektir.

---

## Veri kaynaklari (AGENTS.md Bolum 4)

| # | Veri | Saglayici | Lisans | Attribution metni | Surum / tarih |
|---|---|---|---|---|---|
| 1 | AHN5 nokta bulutu, **GeoTiles alt-fayanslari** (`AHN5_T`) | AHN; dagitim: GeoTiles (TU Delft, Optical and Laser Remote Sensing) | **CC BY 4.0** (NGR resmi kaydi + GeoTiles beyani) | "AHN5 puntenwolk — Actueel Hoogtebestand Nederland; sub-tiles: GeoTiles (TU Delft), CC BY 4.0" | AHN5, ucus 2023-02-08/14; 9 alt-fayans, sha256 DATA_LOG'da |
| 2 | BAG (`bag:pand`, `bag:verblijfsobject`, PDOK WFS v2_0) | Kadaster / PDOK | **CC0 1.0** | zorunlu degil; onerilen: "BAG — Kadaster, via PDOK" | anlik goruntu 2026-09 |
| 3 | 3DBAG | 3D geoinformation onderzoeksgroep (TU Delft) en 3DGI | **CC BY 4.0** | **ZORUNLU, verbatim:** "Naamensvermelding verplicht, 3DBAG door de 3D geoinformation onderzoeksgroep (TU Delft) en 3DGI" [sic] | **v2025.09.03** (D-027) |
| 3a | CBS Wijken en Buurten 2025 (AOI A ve B'nin kaynagi, PDOK WFS) | CBS / PDOK | **CC0 1.0** | zorunlu degil; onerilen: "Wijk- en buurtkaart 2025 — CBS, via PDOK" | 2025 |
| 4 | BGT | PDOK | `TODO_EDINIMDE` | `TODO_EDINIMDE` | `TODO_EDINIMDE` |
| 5 | KNMI saatlik | KNMI | `TODO_EDINIMDE` | `TODO_EDINIMDE` | `TODO_EDINIMDE` |
| 6 | EPW (TMYx Rotterdam) | climate.onebuilding.org | `TODO_EDINIMDE` | `TODO_EDINIMDE` | `TODO_EDINIMDE` |
| 7 | Stedin acik veri (PC6) | Stedin | `TODO_EDINIMDE` | `TODO_EDINIMDE` | `TODO_EDINIMDE` |
| 8 | EP-Online | RVO | `TODO_EDINIMDE` | `TODO_EDINIMDE` | `TODO_EDINIMDE` |
| 9 | Sentinel-2 | ESA / Copernicus | `TODO_EDINIMDE` | `TODO_EDINIMDE` | `TODO_EDINIMDE` |
| 10 | Landsat 8/9 | USGS / NASA | `TODO_EDINIMDE` | `TODO_EDINIMDE` | `TODO_EDINIMDE` |
| 11 | PVGIS | EC JRC | `TODO_EDINIMDE` | `TODO_EDINIMDE` | `TODO_EDINIMDE` |
| 12 | NWB | Rijkswaterstaat / PDOK | `TODO_EDINIMDE` | `TODO_EDINIMDE` | `TODO_EDINIMDE` |

**3DBAG notu:** CC BY 4.0, atif **zorunlu**. Atif metni sabitlenen surumun kendi
meta verisinden **verbatim** alindi (data/raw/3dbag_v20250903/metadata.json -> identificationInfo.resourceConstraints[0].otherConstraints[0]). Kaynaktaki "Naamensvermelding"
yazimi aynen korundu [sic]. Arayuzde gorunur atif olmadan yayin yapilamaz.

**AHN notu — COZULDU (2026-09-27, ayni gun):** Birincil kaynak bulundu: Nationaal Georegister, "Actueel Hoogtebestand Nederland 5 (AHN5)", kayit 4995e338-fec7-425e-bb86-eea3875cf114, dateStamp 2025-11-19. Kayit `otherConstraints` alaninda `http://creativecommons.org/licenses/by/4.0/deed.nl` baglantisiyla "Naamsvermelding verplicht, organisatienaam" diyor. **AHN5 = CC BY 4.0, atif zorunlu.** PDOK AHN WCS'teki CC0 o **raster servisine** aittir. Asagidaki tablo, cozumden onceki durumu kayit icin korur.

**AHN notu — ilk durum (celiski):**

| Kaynak | Ne diyor |
|---|---|
| GeoTiles sayfasi (https://geotiles.citg.tudelft.nl/ (Small print, copyright & disclaimer)) | "This index and derived products (spatial index, colored point clouds, **sub-tiles**, etc.) are copyright GeoTiles and are distributed under the **CC BY 4.0** license." Ayni sayfa: "Please confirm the applicable license with the source before integrating the data." |
| PDOK AHN WCS (https://service.pdok.nl/rws/ahn/wcs/v1_0 GetCapabilities -> AccessConstraints) | "otherRestrictions; Geen beperkingen; http://creativecommons.org/publicdomain/zero/1.0/deed.nl" (**CC0**) — AHN **raster servisi** icin |
| 3DBAG v2025.09.03 meta verisi, lineage | AHN3 ve AHN4 puntenwolk: **CC0**; **AHN5 puntenwolk: CC BY 4.0** (ikincil kaynak) |
| ahn.nl | **okunamadi** — sayfa JavaScript ile yukleniyor, sunucu 841 karakterlik iskelet dondu |

**Uygulanan kural:** Bizim dosyalarimiz GeoTiles **alt-fayanslaridir** ve GeoTiles
bunlari acikca CC BY 4.0 ile dagitiyor. Bu yuzden **daha kati olan CC BY 4.0
uygulanir** ve hem AHN'ye hem GeoTiles'a atif yapilir. Bu, AHN5'in kendi
lisansi CC0 cikarsa da dogru kalan tek secenektir (fazla atif lisans ihlali
degildir; eksik atif ihlaldir). ahn.nl birincil metni okunana kadar
AHN5'in **kendi** lisansi "CELISKILI" olarak kalir.

**Asama 5 etkisi:** Arayuzde artik **iki** zorunlu atif var: 3DBAG ve
AHN5/GeoTiles.

---

## Yazilim (AGENTS.md Bolum 7)

Lisans kategorileri **ayridir ve karistirilmaz**: "ucretsiz", "acik kaynak",
"ticari olmayan kullanim icin ucretsiz" ve "ogrenci lisansi" farkli seylerdir.

| Amac | Arac | Lisans kategorisi (Bolum 7) |
|---|---|---|
| Nokta bulutu | CloudCompare, PDAL | Acik kaynak |
| LOD2 rekonstruksiyon | roofer / geoflow | Acik kaynak (GPLv3) |
| Geometri QC | val3dity, cjval, CityDoctor | Acik kaynak |
| GIS | QGIS + UMEP/SOLWEIG + 3DCityDB-Tools | Acik kaynak |
| Veritabani | PostgreSQL + PostGIS + 3DCityDB v5 | Acik kaynak |
| Enerji | EnergyPlus | Acik kaynak (DOE) |
| Enerji (UBEM) | SimStadt | Ucretsiz / akademik |
| Mikroklima | **ENVI-met LITE** | **Ucretsiz, ticari olmayan (CC BY-NC-SA) — ACIK KAYNAK DEGIL** |
| CFD | OpenFOAM + City4CFD | Acik kaynak |
| Uydu | ESA SNAP | Acik kaynak |
| Yayin | pg2b3dm, CesiumJS | Acik kaynak |

### Yayin riski — ENVI-met

AGENTS.md Bolum 7: ENVI-met LITE **acik kaynak degildir**, CC BY-NC-SA kapsamindadir
ve **lisans sistemi 2026'da degismistir**; kullanimdan once guncel kosullar kontrol
edilecektir. Bu, Asama 5 yayinini dogrudan etkileyebilecek tek bilesendir.
Bkz. `reports/PENDING_DECISIONS.md` → P-002.

### Kullanilmayan araclar ve nedeni

- **Ladybug / Honeybee** — Rhino (ticari) gerektirdigi icin kullanilmaz.
  Yerine QGIS UMEP kullanilir (Bolum 7).

---

## Doldurma kurali

Her satir, ilgili veri `src/00_acquisition/` scriptleriyle indirildigi anda
`data/DATA_LOG.md` kaydiyla **es zamanli** doldurulur. Lisans alani bos veya
`TODO` olan bir veri, Asama 5 yayinina dahil edilemez.
