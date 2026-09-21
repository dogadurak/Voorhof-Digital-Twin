# ATTRIBUTION.md — Veri ve yazilim kaynaklari

> AGENTS.md Bolum 7: "Her veri ve yazilimin kesin lisansi ve yeniden dagitim kisiti
> buraya yazilir. Bir bilesenin lisansi web arayuzunun yayinini engelliyorsa
> **yayin asamasina gecilmez**, durum raporlanir."
>
> Bolum 6, Asama 5: bu dosya otomatik uretilir ve web arayuzunde gosterilir.

**Durum: ISKELET (Asama 0.1).** Asagidaki tablolarda `TODO_0.3` isaretli her alan,
veri fiilen indirilirken kaynagindan dogrulanip doldurulacaktir. AGENTS.md Bolum 1
kural 1 geregi **dogrulanmamis lisans adi yazilmaz** — tahmin edilen bir lisans,
yanlis attribution ve yayin hakki ihlali demektir.

---

## Veri kaynaklari (AGENTS.md Bolum 4)

| # | Veri | Saglayici | Lisans | Attribution metni | Surum / tarih |
|---|---|---|---|---|---|
| 1 | AHN5 (AHN4 yedek) | Rijkswaterstaat / AHN | `TODO_0.3` | `TODO_0.3` | `TODO_0.3` |
| 2 | BAG | Kadaster / PDOK | `TODO_0.3` | `TODO_0.3` | `TODO_0.3` |
| 3 | 3DBAG | TU Delft 3D geoinformation | **CC BY 4.0** | `TODO_0.3` (zorunlu) | `TODO_0.3` |
| 4 | BGT | PDOK | `TODO_0.3` | `TODO_0.3` | `TODO_0.3` |
| 5 | KNMI saatlik | KNMI | `TODO_0.3` | `TODO_0.3` | `TODO_0.3` |
| 6 | EPW (TMYx Rotterdam) | climate.onebuilding.org | `TODO_0.3` | `TODO_0.3` | `TODO_0.3` |
| 7 | Stedin acik veri (PC6) | Stedin | `TODO_0.3` | `TODO_0.3` | `TODO_0.3` |
| 8 | EP-Online | RVO | `TODO_0.3` | `TODO_0.3` | `TODO_0.3` |
| 9 | Sentinel-2 | ESA / Copernicus | `TODO_0.3` | `TODO_0.3` | `TODO_0.3` |
| 10 | Landsat 8/9 | USGS / NASA | `TODO_0.3` | `TODO_0.3` | `TODO_0.3` |
| 11 | PVGIS | EC JRC | `TODO_0.3` | `TODO_0.3` | `TODO_0.3` |
| 12 | NWB | Rijkswaterstaat / PDOK | `TODO_0.3` | `TODO_0.3` | `TODO_0.3` |

**3DBAG notu:** AGENTS.md Bolum 7 bu lisansi acikca veriyor — CC BY 4.0, attribution
**zorunlu**. Arayuzde gorunur attribution olmadan yayin yapilamaz.

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
