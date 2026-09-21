# AGENTS.md — Delft Kentsel Dijital İkiz Projesi

**Sürüm:** v4 · **Son güncelleme:** 2026-09-21

> Bu dosya, bu depoda çalışan her AI ajanı ve geliştirici için **projeye özel yetkili
> şartnamedir**. Sistem/geliştirici düzeyindeki üst talimatlar ve platform politikaları
> bu dosyadan önceliklidir; bu dosya onların yerine geçmez.
>
> Herhangi bir iş yapmadan önce tamamını oku. Kullanıcının tek tek mesajlarıyla bu dosya
> çelişirse varsayma — sor.

---

## 0. Projenin kimliği

**Ne yapıyoruz:** Hollanda'nın Delft şehrindeki Voorhof mahallesi için, tamamen açık veriyle
üretilmiş, çok alanlı (multi-domain), doğrulanabilir bir **kentsel dijital ikiz**.

**Bu ne DEĞİL:**
- "Vibe coding" projesi değil. Tek bir Python scriptiyle çıkan renkli harita değil.
- Demo değil. **Gerçek teslim edilecek bir mühendislik işi olarak ele alınacak.**
- Sadece görselleştirme değil. Her sayısal çıktının bağımsız bir referansa karşı
  doğrulaması yapılacak.

**Teslim edilen asıl ürün model değil, DOĞRULAMA RAPORUDUR.** 3B model ve web arayüzü
o raporun ekleridir. Bir ajan bu önceliği tersine çevirirse yanlış iş yapıyordur.

**Projeyi yürüten:** Harita mühendisliği öğrencisi (4. sınıf), İzmir. Saha çalışması
yapılamıyor — bu yüzden **her veri uzaktan, ücretsiz ve açık lisanslı olmak zorunda.**

---

## 1. Temel ilke: DOĞRULUK ÖNCE GELİR

Her karar şu soruyla test edilir:

> "Bu çıktının doğru olduğunu bağımsız bir kaynakla kanıtlayabiliyor muyum?"

Cevap hayırsa, o çıktı üretilmez veya açıkça "doğrulanmamış" etiketiyle sunulur.

### Ajanlar için bağlayıcı kurallar

1. **Sayı uydurma.** Hesaplanmamış değeri yazma. Placeholder gerekiyorsa
   `TODO_HESAPLANACAK` yaz, sahte sayı koyma.
2. **Doğrulanmamış sonucu doğrulanmış gibi sunma.** Her çıktı, hangi referansa karşı
   test edildiğini kendi başlığında belirtir.
3. **Veri kaynağını değiştirme.** Bölüm 4 dışında bir kaynak kullanmadan önce kullanıcıya sor.
4. **Kapalı/ticari veri kullanma.** Tek bir ücretli katman bile projeyi tekrarlanamaz yapar.
5. **Belirsizliği gizleme.** Şüpheli sonuç raporda "sınırlama" olarak yazılır.
6. **CRS'i varsayma.** EPSG:28992 (RD New) veya EPSG:7415 (RD New + NAP). Her dönüşüm
   kodda açıkça yazılır.
7. **Kabul kriteri sağlanmadan sonraki aşamaya geçilmez** (Bölüm 6 ve 12.6).
8. **Eşiği sonradan değiştirme.** Bölüm 12.2 bağlayıcıdır.
9. **Kendi sonucunu ölç ve raporla.** Bölüm 13 zorunludur — kullanıcı başında
   olmasa da her aşama sonunda kendini değerlendirir ve PASS/FAIL beyan edersin.
10. **Aynı hatayı iki kez yapma.** Bölüm 14: her oturuma `MISTAKES.md` okuyarak
    başlarsın, her hatadan kural türetirsin.

---

## 2. Pilot bölge: Voorhof, Delft — NEDEN BURASI

### Seçim kriteri
Üç bağımsız doğrulama referansının **aynı anda** çalışması gerekiyordu:

| Referans | Ne doğruluyor | Nerede çalışır |
|---|---|---|
| 3DBAG + AHN nokta bulutu | Geometri | Hollanda'nın her yerinde |
| PC6 agregat gaz/elektrik (Stedin) | Enerji modeli | **Sadece homojen konut dokusunda anlamlı** |
| BAG bouwjaar + gebruiksdoel | Arşetip ataması | Tek yapım-yılı kohortunda güvenilir |

İkinci ve üçüncü kriter, tarihi ve karma kullanımlı merkezleri eliyor.

### Değerlendirilen ve ELENEN alanlar

| Alan | Neden elendi |
|---|---|
| **Delft Binnenstad** | Karma kullanım (dükkân+ofis+konut) → PC6 agregatı konut modeliyle kıyaslanamaz hale gelir. Karmaşık tarihi çatılar → LOD2 RMSE 30-50 cm, hatalı bina oranı %3-5 |
| **TU Delft Campus** | Kurumsal binalar, konut tüketim profiliyle eşleşmez |
| **Tanthof** | Uygun ama düşük yoğunluk → rüzgâr/gölge analizi zayıf. **Yedek alan** |

### SEÇİLEN: Voorhof

| Kriter | Durum | Sonuç |
|---|---|---|
| Çatı geometrisi | Düz/basit (1960-70 modernist) | LOD2 RMSE hedefi **10-20 cm** |
| Kullanım tipi | %90+ konut | PC6 agregat karşılaştırması anlamlı |
| Yapım yılı | 1960-1975 tek kohort | 5-8 arşetip yeterli |
| Bina çeşitliliği | Yüksek blok + sıra ev | Rüzgâr ve gölgeleme analizi anlamlı |
| LiDAR yoğunluğu | AHN5 Randstad: **≥20 nokta/m²** | Ülkedeki en yoğun sınıf |

**Binnenstad projeden atılmadı** — çekirdek bittikten sonra aynı boru hattı orada da
çalıştırılacak, "modern doku vs. tarihi doku" karşılaştırması raporun bir **bulgusu** olacak.
Orada yüksek hata çıkması beklenen sonuçtur, başarısızlık değildir.

**Yedek alanlar:** Delft Tanthof, Rotterdam Ommoord, Rotterdam Prinsenland.

---

## 3. Çalışma alanları — iç içe dört ölçek

| Katman | Boyut | Yaklaşık bina | Ne için | Not |
|---|---|---|---|---|
| **A — Analiz alanı** | ~600 × 600 m | **~400-700** | Güneş + enerji. **Tüm doğrulama burada** | Raporlanan alan |
| **B — Bağlam/tampon** | A + ~300 m halka | ~1.500-2.500 | Gölgeleme ve rüzgâr geometrisi | Simüle edilir, **raporlanmaz** |
| **C — Mikroklima alt-alanı** | ~150 × 150 m | ~30-60 | ENVI-met | LITE 50×50×25 grid sınırı |
| **D — CFD domeni** | H = en yüksek bina: girişte 5H, çıkışta 15H, yanlar/üst 5H | Geometri B'den | OpenFOAM | COST 732 / AIJ kuralı |

**B katmanı atlanamaz.** Tamponsuz simülasyonda kenar binalar gölgelenmemiş görünür ve
güneş potansiyeli **sistematik olarak yüksek** çıkar.

> ⚠️ **AÇIK KARAR:** B ve D boyutları donanıma göre sabitlenecek. RAM/CPU/GPU bilgisi
> henüz alınmadı. Bu bilgi gelene kadar CFD ve ENVI-met aşamalarına **başlanmaz**;
> Aşama 0-3 donanımdan bağımsız ilerler.

---

## 4. Veri envanteri — ÇEKİRDEK

| # | Veri | Ne için | Kaynak | Format | CRS | Kayıt |
|---|---|---|---|---|---|---|
| 1 | **AHN5** (AHN4 yedek) | LiDAR, LOD2 girdisi | `geotiles.citg.tudelft.nl`, `ahn.nl/dataroom`, PDOK ATOM | LAZ, GeoTIFF | EPSG:7415 | Hayır |
| 2 | **BAG** | Ayakizi, bouwjaar, gebruiksdoel | `service.pdok.nl/lv/bag/atom/bag.xml` | GPKG, GML, WFS | EPSG:28992 | Hayır |
| 3 | **3DBAG** | LOD2 tutarlılık referansı | `3dbag.nl`, `api.3dbag.nl` | CityJSON, GPKG | EPSG:7415 | Hayır |
| 4 | **BGT** | Arazi örtüsü (mikroklima) | `app.pdok.nl/lv/bgt/download-viewer/` | GML, CityGML | EPSG:28992 | Hayır |
| 5 | **KNMI saatlik** | Meteoroloji (ist. 344 Rotterdam / 215 Voorschoten) | `knmi.nl` uurgegevens, `dataplatform.knmi.nl` | ASCII, NetCDF | — | API-key ücretsiz |
| 6 | **EPW** | EnergyPlus / ENVI-met girdisi | `climate.onebuilding.org` (TMYx Rotterdam) | EPW/DDY/STAT | WGS84 | Hayır |
| 7 | **Stedin açık veri** | Enerji karşılaştırması — **PC6 agregat** gaz + elektrik | `stedin.net/opendata` | CSV, WFS | — (PC6) | Hayır |
| 8 | **EP-Online** | Enerji etiketi (adres bazında) | `ep-online.nl/PublicData` | XML/CSV/XLSX | — | API-key ücretsiz |
| 9 | **Sentinel-2** | NDVI | `dataspace.copernicus.eu` | JP2/GeoTIFF | UTM31N | Ücretsiz kayıt |
| 10 | **Landsat 8/9** | LST (yüzey sıcaklığı) | `earthexplorer.usgs.gov` | GeoTIFF | UTM | Ücretsiz kayıt |
| 11 | **PVGIS** | Güneş karşılaştırması | `re.jrc.ec.europa.eu` | CSV/API | WGS84 | Hayır |
| 12 | **NWB** | Yol ağı (opsiyonel gürültü) | PDOK | GML, WFS | EPSG:28992 | Hayır |

### 3DBAG kalite öznitelikleri (karşılaştırmada kullanılacak)
`b3_rmse_lod22`, `b3_val3dity_lod22`, `b3_h_maaiveld`, `b3_h_dak_50p/70p/100p`,
`b3_puntdichtheid_ahn4/ahn5`, `b3_nodata_fractie`, `b3_kwaliteitsindicator`,
`b3_volume_lod22`, `b3_dak_type`, `b3_bouwlagen`

### AHN doğruluk referansı
Resmî kwaliteitsbeschrijving: düşey sistematik ≤5 cm, stokastik σ ≤5 cm; yatay ~5 cm
stokastik / ~8 cm sistematik. AHN5 ihale belgesi düşey σ ≤3 cm veriyor —
**bu çelişki raporda açıkça not düşülecek**, sessizce tek değer seçilmeyecek.

---

## 5. Bilinen boşluklar ve dürüst sınırlamalar

Bunlar gizlenmeyecek, raporun "Limitations" bölümünde açıkça yazılacak.

| Boşluk | Gerçek durum | Nasıl ele alınacak |
|---|---|---|
| **Sel ground-truth** | İndirilebilir resmî sel derinliği rasterı yok (LIWO, Klimaateffectatlas çoğunlukla WMS/viewer) | AHN DTM tabanlı **topografik screening**; Klimaateffectatlas ile **görsel** karşılaştırma. "Doğrulanmış hidrolik model" DENMEZ (bkz. 12.5) |
| **İç mekan / BIM** | Delft binaları için açık IFC yok | GeoBIM benchmark / buildingSMART jenerik IFC ile **kavram kanıtı**. "Gerçek bina BIM'i" denmez |
| **Güneş doğrulaması** | Resmî açık ulusal zonnekaart yok (Zonatlas/MapServices ticari) | PVGIS — ama **aynı fiziksel büyüklük kuralı** geçerli (12.4) |
| **Rüzgâr doğrulaması** | Bağımsız açık CFD benchmark zayıf | NEN 8100 literatür vakaları; sonuç en fazla "literatürle tutarlı" |
| **LST çözünürlüğü** | Landsat termal gerçekte 100 m, 30 m'ye resample | Tek mahalle için kaba. ECOSTRESS (~70 m) denenebilir. Sınırlama yazılacak |
| **3DBAG bağımsız değil** | 3DBAG de AHN + roofer ile üretiliyor | Karşılaştırma **"tutarlılık kontrolü"** olarak adlandırılır, "bağımsız doğrulama" değil. Bağımsız kontrol: AHN nokta bulutuna doğrudan z-fark analizi |
| **PC6 bina-level değil** | Stedin verisi en az 10 bağlantı birleştirilmiş anonim agregat | Bina bazında atama YAPILMAZ. Karşılaştırma PC6 kümesi düzeyinde (bkz. 12.3) |

---

## 6. Aşamalar ve KABUL KRİTERLERİ

Kriter sağlanmadan sonraki aşamaya geçilmez. "Bitti" diyen ajan, kriterin sayısal
sonucunu göstermek zorundadır. Başarısızlık halinde Bölüm 12.6 uygulanır.

### Aşama 0 — Veri edinimi
- A ve B alan sınırlarını GeoJSON olarak tanımla (EPSG:28992), `aoi/` altına koy
- BAG GPKG, AHN5 LAZ (ilgili kaartblad), 3DBAG CityJSON indir
- Her dosya için `data/DATA_LOG.md` kaydı (içerik: Bölüm 12.7)

**Kabul:** Her katmanın CRS'i doğrulandı; A alanındaki bina sayısı BAG'den sayıldı ve
loglandı; eksik/bozuk dosya yok; her indirmenin checksum'ı kayıtlı.

### Aşama 1 — LOD2 rekonstrüksiyon
- `roofer` / `geoflow` (Docker) ile BAG ayakizi + AHN5'ten LOD1.2/1.3/2.2 üret
- `val3dity` ile geometri geçerliliği, `cjval` ile CityJSON şeması
- Hatalı binalar boru hattını çökertmez → `reports/failed_buildings.csv` (bkz. 12.8)

**Kabul:**
- val3dity geçerlilik **≥ %97** (referans: 3DBAG genelinde %99,15)
- 3DBAG ile çatı yüksekliği RMSE **≤ 25 cm** (hedef 10-20 cm) — *tutarlılık kontrolü*
- AHN nokta bulutuna doğrudan z-fark analizi — *bağımsız kontrol*
- Başarısız rekonstrüksiyon **≤ %2**
- Üçü de `reports/01_geometry_validation.md`'de tablo halinde

### Aşama 2 — Semantik veritabanı
- PostgreSQL + PostGIS + 3DCityDB v5; CityJSON import
- Her binaya BAG `identificatie` kalıcı ID; BAG öznitelikleri bağlanır
- BAG identifier hiyerarşisi üzerinden adres eşleşmesi (bkz. 12.3)

**Kabul:** A alanındaki her bina sorgulanabilir; ID kaybı yok; belirsiz/çoklu adres
vakaları ayrı raporlandı.

### Aşama 3 — ÇEKİRDEK: Güneş + enerji
- Güneş: QGIS UMEP/SOLWEIG (B alanı tampon dahil)
- Enerji: **arşetip yaklaşımı** — bouwjaar + gebruiksdoel + bina tipine göre 5-8 arşetip,
  her biri bir kez EnergyPlus'ta simüle edilir, geometriyle ölçeklenir.
  **400-700 bina tek tek simüle EDİLMEZ** — profesyonel UBEM pratiği budur.
- Doğrulama **PC6 kümesi düzeyinde**: model çıktısı da aynı PC6'ya toplanır, öyle kıyaslanır

**Kabul:**
- Güneş sonucu PVGIS ile karşılaştırıldı; **karşılaştırılan büyüklüğün aynı olduğu
  `docs/validation_protocol.md`'de gösterildi** (12.4)
- PC6 düzeyinde sapma metrikleri (NMBE, CV(RMSE)) hesaplandı ve dağılım grafiği üretildi
- EP-Online etiket dağılımı ile model tutarlılığı kontrol edildi
- `reports/03_energy_validation.md`

### Aşama 4 — İkincil modüller
- Mikroklima: ENVI-met (C alanı) veya UMEP/SOLWEIG; LST ile **bağlamsal karşılaştırma**
- Rüzgâr: City4CFD + OpenFOAM (D domeni), NEN 8100 kriterleri
- Sel: AHN DTM tabanlı **screening senaryosu**

**Kabul:** Her modül için girdi, çözüm ayarları ve sınırlamalar belgelendi.
CFD için Bölüm 12.9 listesi eksiksiz. Doğrulanamayan modül 12.5'e göre etiketlendi.

### Aşama 5 — Yayın
- `pg2b3dm` ile 3D Tiles; CesiumJS arayüzü
- `ATTRIBUTION.md` otomatik üretildi ve arayüzde gösteriliyor
- Nihai doğrulama raporu

**Kabul:** Arayüz A alanını sorunsuz yüklüyor; gösterilen her değer bir kaynağa ve
doğrulama durumuna bağlı; lisans/attribution şartları karşılanıyor.

---

## 7. Yazılım yığını — LİSANS KATEGORİLERİ AYRI

"Ücretsiz", "açık kaynak", "ticari olmayan kullanım için ücretsiz" ve "öğrenci lisansı"
**farklı kategorilerdir** ve karıştırılmaz.

| Amaç | Araç | Lisans kategorisi |
|---|---|---|
| Nokta bulutu | CloudCompare, PDAL | Açık kaynak |
| LOD2 rekonstrüksiyon | roofer / geoflow | Açık kaynak (GPLv3) |
| Geometri QC | val3dity, cjval, CityDoctor | Açık kaynak |
| GIS | QGIS + UMEP/SOLWEIG + 3DCityDB-Tools | Açık kaynak |
| Veritabanı | PostgreSQL + PostGIS + 3DCityDB v5 | Açık kaynak |
| Enerji | EnergyPlus | Açık kaynak (DOE) |
| Enerji (UBEM) | SimStadt | Ücretsiz / akademik |
| Mikroklima | **ENVI-met LITE** | **Ücretsiz, ticari olmayan kullanım (CC BY-NC-SA)** — açık kaynak DEĞİL. Lisans sistemi 2026'da değişti, kullanımdan önce güncel koşullar kontrol edilecek |
| CFD | OpenFOAM + City4CFD | Açık kaynak |
| Uydu | ESA SNAP | Açık kaynak |
| Yayın | pg2b3dm, CesiumJS | Açık kaynak |

**Rhino gerektirdiği için Ladybug/Honeybee kullanılmaz** — yerine QGIS UMEP.

**Veri lisansı notu:** 3DBAG CC BY 4.0 — attribution zorunlu. Her veri ve yazılımın
kesin lisansı ve yeniden dağıtım kısıtı `ATTRIBUTION.md`'ye yazılır. Bir bileşenin lisansı
web arayüzünün yayınını engelliyorsa **yayın aşamasına geçilmez**, durum raporlanır.

---

## 8. Depo yapısı

```
Voorhof-Digital-Twin/
├── AGENTS.md                      # bu dosya
├── DECISIONS.md                   # metodolojik kararlar: ne, neden, ne zaman, hangi aşamayı etkiler
├── MISTAKES.md                    # hata defteri — kurumsal bellek (Bölüm 14)
├── ENVIRONMENT.md                 # yazılım sürümleri, Docker image/tag, kurulum adımları
├── ATTRIBUTION.md                 # her veri/yazılım: kaynak, lisans, attribution metni, sürüm
├── environment.yml                # conda-forge ortamı (D-001)
├── requirements.txt               # pip tamamlayıcı bağımlılıklar (D-001)
├── .env.example                   # API key isimleri — gerçek değer ASLA repoda durmaz
├── data/
│   ├── DATA_LOG.md                # veri provenance (içerik: 12.7)
│   ├── logs/                      # makine logları (.log)
│   ├── raw/                       # ham veri — ASLA DEĞİŞTİRİLMEZ
│   ├── interim/
│   └── processed/
├── aoi/                           # alan sınırları (A, B, C, D) GeoJSON, EPSG:28992
├── config/
│   ├── paths.yml
│   ├── acceptance_criteria.yml    # eşikler — SONUÇTAN ÖNCE sabitlenir (12.2)
│   └── units.yml                  # birim ve zaman sözlüğü (12.1)
├── src/
│   ├── common/                    # logging, config okuyucu, .meta.json yazıcı (Aşama 0.1)
│   ├── qa/                        # öz-ölçüm araçları (Aşama 0.5 — bkz. 13.6)
│   ├── 00_acquisition/
│   ├── 01_reconstruction/
│   ├── 02_database/
│   ├── 03_solar_energy/
│   ├── 04_microclimate_wind_flood/
│   └── 05_publication/
├── reports/
│   ├── PENDING_DECISIONS.md       # kullanıcı onayı bekleyenler (13.4)
│   ├── 01_geometry_validation.md
│   ├── 03_energy_validation.md
│   ├── failed_buildings.csv
│   └── FINAL_VALIDATION_REPORT.md
├── docs/
│   ├── validation_protocol.md     # neyi neyle karşılaştırıyoruz (12.4)
│   ├── assumptions.md
│   └── manual_steps.md
└── web/
```

### Kodlama kuralları
- `data/raw/` **salt okunur**. Hiçbir script oraya yazmaz.
- Yollar `config/paths.yml`'den okunur, koda gömülmez.
- CRS dönüşümleri açıkça yazılır (`EPSG:28992 → EPSG:7415`).
- `print()` yerine `logging` modülü. Log hem terminale hem `data/logs/*.log`'a yazılır.
  `DATA_LOG.md` insan tarafından okunan kayıttır, makine logu oraya karışmaz.
- Her fonksiyon ve sınıf docstring'li: ne yapar, hangi girdiyi alır, ne döndürür, birimi ne.
- Commit mesajları anlaşılır ve tek konulu olsun (`feat:`, `fix:`, `docs:` öneki tercih edilir).
- Her analiz çıktısının yanına `.meta.json` yazılır:
  `run_id`, `git_commit`, girdi dosyaları + checksum, parametreler, yazılım sürümleri,
  çalıştırma zamanı (UTC), varsa `random_seed`.
- Rastgelelik içeren her işlemde seed sabitlenir ve `.meta.json`'a yazılır. Aynı girdiyle
  iki çalıştırma aynı sonucu vermek zorundadır.
- API key / token / credential **asla** repoya yazılmaz; environment variable kullanılır.

---

## 9. Metodolojik referanslar

- **3DBAG** — Peters et al., "Automated 3D reconstruction of LoD2 and LoD1 models for all
  10 million buildings of the Netherlands" (PE&RS)
- **Çok alanlı iş akışı** — Gothenburg vaka çalışması, *Journal of Building Performance
  Simulation* (2024)
- **CityGML/CityJSON** — Ledoux et al., CityJSON; Kolbe et al., 3DCityDB
- **LOD tanımı** — Biljecki et al., "Formalisation of the level of detail in 3D city modelling"
- **UBEM şablonu** — TU Delft MSc: "Enhancing urban energy applications through semantic
  3D city models and open data: The case of the Netherlands"
- **UBEM doğrulama metrikleri** — ASHRAE Guideline 14 (NMBE, CV(RMSE) eşikleri)
- **CFD domeni ve en iyi uygulama** — COST Action 732, AIJ kılavuzları
- **Rüzgâr konforu** — NEN 8100

---

## 10. Ajan için hızlı kontrol listesi

Başlamadan önce:
- [ ] Bu dosyayı okudum
- [ ] Hangi aşamadayız, öncekinin kabul kriteri sağlandı mı?
- [ ] Kullanacağım veri Bölüm 4'te listeli mi?
- [ ] CRS ve birim (Bölüm 12.1) belli mi?
- [ ] Hangi alanda (A/B/C/D) çalışıyorum?
- [ ] Bu çıktıyı neye karşı, hangi fiziksel büyüklükte doğrulayacağım? (12.4)
- [ ] Donanıma bağlı aşama mı? Öyleyse önce kullanıcıdan RAM/CPU/GPU al

Bitirdikten sonra:
- [ ] Kabul kriterinin sayısal sonucunu raporladım
- [ ] `.meta.json` yazıldı
- [ ] `DATA_LOG.md` / ilgili rapor güncellendi
- [ ] Başarısız kayıtlar `failed_buildings.csv`'ye düştü
- [ ] Sınırlamaları yazdım, gizlemedim
- [ ] Uydurma sayı yok

---

## 11. Açık kararlar (kullanıcı cevaplayacak)

1. **Donanım:** RAM / CPU / GPU? → B ve D alan boyutları buna göre sabitlenecek.
2. **ENVI-met:** Öğrenci lisansı başvurusu mu, LITE limitiyle mi devam?
3. ~~**Proje adı:** Depo adı `delft-twin` placeholder.~~ → **KAPANDI 2026-09-21 (D-004):**
   depo adı `Voorhof-Digital-Twin`. Bölüm 8 ağacı güncellendi.

---

## 12. Mühendislik / Bilimsel QA Kuralları

### 12.1 Birimler ve zaman

Tüm fiziksel değişkenler standart birimlerle saklanır ve `config/units.yml`'de tanımlanır.

| Büyüklük | Birim |
|---|---|
| Mesafe / yükseklik | m |
| Alan | m² |
| Hacim | m³ |
| Sıcaklık | °C |
| Rüzgâr hızı | m/s |
| Işınım (irradiance) | W/m² |
| Işınım toplamı | kWh/m²/yıl |
| Enerji | kWh/yıl |
| Enerji yoğunluğu | kWh/m²/yıl |
| Yağış | mm |

**Zaman:** Depolamada UTC esastır. EPW dosyaları yerel saat, KNMI UTC, Landsat geçiş saati
farklıdır. Her veri kümesinin zaman referansı `DATA_LOG.md`'ye yazılır ve dönüşümler
(UTC ↔ Europe/Amsterdam) kodda açıkça yapılır. Enerji ve mikroklima karşılaştırmalarında
saat kayması ciddi hata kaynağıdır.

### 12.2 Metrikler sonuçtan ÖNCE kilitlenir

Kullanılacak metrik (RMSE, MAE, NMBE, CV(RMSE), MAPE), kabul eşiği, aykırı değer kuralı,
dışlama kuralı ve eşleştirme yöntemi **sonuç görülmeden önce** `config/acceptance_criteria.yml`
içinde sabitlenir.

Eşik sağlanmazsa **eşik değiştirilmez** — failure raporlanır (12.6). Metrik veya eşik
değişikliği yalnızca kullanıcı onayıyla ve `DECISIONS.md`'ye gerekçesi yazılarak yapılır.

### 12.3 Enerji verisi eşleştirmesi — KRİTİK

**Stedin PC6 verisi bina düzeyinde ölçüm DEĞİLDİR.** Veriler anonimleştirilmiş ve
agregedir; satır başına en az 10 bağlantı birleştirilir ve postcode'lar da birleştirilebilir.

Bağlayıcı kurallar:
- PC6 tüketimi **hiçbir koşulda tek bir binaya atanmaz**.
- Karşılaştırma **PC6 kümesi düzeyinde** yapılır: model çıktısı da aynı PC6 kümesine
  toplanır, karşılaştırma iki agregat arasında olur.
- Bir PC6'daki bina sayısı, konut dışı kullanım oranı ve boşluk durumu raporlanır.
- Kullanılan PC6→BAG ilişkilendirme yöntemi `docs/validation_protocol.md`'de açıkça tanımlanır.
- "PC6 ground truth" ifadesi kullanılmaz; doğru ifade "PC6 düzeyinde agregat karşılaştırma".

**EP-Online eşleştirmesi:** Yalnızca geometrik yakınlıkla adres eşleştirilemez.
`BAG pand → verblijfsobject → adresseerbaar object → EP-Online label` hiyerarşisi kullanılır.
Belirsiz veya çoklu adresli vakalar ayrı raporlanır, sessizce bir seçenek seçilmez.

### 12.4 Validation fiziksel olarak karşılaştırılabilir olmalıdır

Bir karşılaştırma yapılmadan önce şu soru cevaplanır ve `docs/validation_protocol.md`'ye
yazılır:

> **"Aynı fiziksel büyüklüğü mü karşılaştırıyorum?"**

- SOLWEIG/UMEP → yüzeye gelen ışınım. PVGIS → belirli bir PV sistem konfigürasyonunun
  üretimi. Gerçek PV üretimi → üçüncü bir büyüklük. Bunlar doğrudan eşitlenemez;
  karşılaştırma ancak aynı büyüklüğe dönüştürüldükten sonra yapılır.
- Landsat **LST = yüzey sıcaklığı**; ENVI-met hava sıcaklığı da üretir. **LST ile hava
  sıcaklığı doğrudan kıyaslanmaz.**
- Karşılaştırma aynı zaman aralığında ve karşılaştırılabilir mekânsal ölçekte yapılır.

Uyumsuz büyüklükler arasındaki kıyas "validation" değil, **"contextual comparison"**
olarak etiketlenir.

### 12.5 Senaryo modelleri

Bağımsız ground truth bulunmayan çıktılar "prediction" veya "validated" olarak
etiketlenmez. Uygun etiket kullanılır: **scenario**, **screening**, **indicative**,
**literature-consistent**.

**Sel modülü:** AHN tabanlı model bir **topografik screening/senaryo modelidir**.
Yağış, drenaj, akış bağlantısı ve referans sel derinlikleri bağımsız doğrulanmadıkça
"doğrulanmış hidrolik sel modeli" veya "sel tahmini" olarak sunulamaz.

### 12.6 Başarısızlık protokolü

Kabul kriteri sağlanmazsa:

1. `reports/` altına **failure report** yaz
2. Nedeni sınıflandır: veri kaynaklı mı, kod kaynaklı mı, parametre kaynaklı mı, yöntem kaynaklı mı
3. Düzeltilebilir ise düzelt ve yeniden çalıştır
4. Yöntem veya eşik değişikliği gerekiyorsa **kullanıcı onayı iste**, kararı `DECISIONS.md`'ye yaz
5. Sonraki aşamaya geçme

**Yasak:** Başarısız sonucu gizlemek, eşiği geriye dönük değiştirmek, sonucu iyileştirmek
için veri seçimini sonradan daraltmak.

### 12.7 Veri provenance — `DATA_LOG.md` içeriği

Her harici veri için:
kaynak URL · sağlayıcı · veri seti adı · sürüm · veri üretim tarihi · yayın tarihi ·
indirme tarihi · indirme yöntemi / API endpoint · sorgu parametreleri veya bounding box ·
CRS · zaman referansı · lisans · attribution şartı · checksum (SHA-256) · uygulanan
dönüşüm/işlem geçmişi.

Ham veri hiçbir şekilde değiştirilmez.

### 12.8 Hata yönetimi ve dayanıklılık

Toplu işlemede (örn. 500 bina için LOD2) **tek bir bozuk binanın boru hattını çökertmesi
kabul edilemez**.

- Hatalar try/except ile yakalanır, işlem devam eder
- Başarısız kayıt `reports/failed_buildings.csv`'ye yazılır:
  `bag_id`, `aşama`, `hata_tipi`, `hata_mesajı`, `zaman`, `run_id`
- Bu dosya aynı zamanda "başarısız rekonstrüksiyon ≤ %2" kriterinin kanıtıdır
- Başarısız oran kriteri aşarsa 12.6 uygulanır; sessizce atlanmaz

### 12.9 CFD kalite güvencesi

**Solver'ın yakınsaması tek başına kabul gerekçesi değildir.** Şunlar belgelenir:

hesaplama domeni · mesh çözünürlüğü · **mesh bağımsızlık (mesh independence) çalışması** ·
sınır koşulları · giriş rüzgâr profili · türbülans modeli · yüzey pürüzlülüğü · y+ değerleri ·
solver ayarları · residual kriterleri · kütle korunumu · yakınsama geçmişi

Mesh bağımsızlık çalışması yapılmadan CFD sonucu raporlanmaz.

### 12.10 Bağımsızlık ve QA

Bir ajan kendi ürettiği çıktıyı yalnızca kendi hesabına dayanarak "validated" ilan edemez.
Aynı ham veriden türetilmiş iki çıktı bağımsız ground truth sayılmaz.

Uygulama: her aşama sonunda **QA kontrol listesi** (Bölüm 10) ayrı bir adım olarak
çalıştırılır ve sonucu rapora yazılır. Mümkün olduğunda ikinci bir hesaplama yolu kullanılır
(örn. geometri için hem 3DBAG karşılaştırması hem AHN nokta bulutuna doğrudan z-fark analizi).

### 12.11 Kullanıcı onayı gereken kararlar

Şunlar kullanıcı onayı olmadan değiştirilemez:

yeni veri kaynağı · yeni AOI · CRS stratejisi · kabul eşiği veya metrik · doğrulama
metodolojisi · lisans koşulu · ücretli veya öğrenci-lisanslı yazılım kullanımı · temel
model varsayımı · çekirdek çıktı tanımı · yüksek hesaplama kaynağı gerektiren çalıştırma

Her onaylanan değişiklik `DECISIONS.md`'ye tarih ve gerekçeyle yazılır.

---

## 13. Ajanın kendini ölçmesi — ZORUNLU

Kullanıcı her zaman başında olmayacak. Bu yüzden ajan, bir iş bitirdiğinde **kendi
çıktısını ölçmek, kurallara uyduğunu kanıtlamak ve dürüstçe PASS/FAIL beyan etmek
zorundadır.** "Bitti" demek yeterli değildir; **ölçülmemiş iş bitmemiş sayılır.**

### 13.1 Aşama Sonu Raporu — standart format

Her aşama ve her önemli alt görev sonunda ajan aşağıdaki bloğu **eksiksiz** üretir ve
`reports/` altına yazar. Boş bırakılan alan = FAIL.

```
=== AŞAMA SONU RAPORU ===
run_id:            RUN-YYYY-MM-DD-NNN
aşama:             [0.3 / 1 / 3 ...]
git_commit:        [hash]
çalıştırma (UTC):  [timestamp]
süre:              [dk]

--- KABUL KRİTERİ ---
| Metrik | Eşik (config'ten) | Ölçülen | Sonuç |
|--------|-------------------|---------|-------|
| ...    | ...               | ...     | PASS/FAIL |

--- ÖLÇÜMÜN KAYNAĞI ---
Her sayı için: hangi script, hangi girdi dosyası (checksum), hangi parametre.
Kaynağı gösterilemeyen sayı rapora YAZILMAZ.

--- SPOT KONTROL ---
Rastgele N=10 kayıt: referans değer / model değeri / fark.
seed: [sabit değer]

--- BAŞARISIZ KAYITLAR ---
toplam işlenen: N
başarısız:      N (%X)
dosya:          reports/failed_buildings.csv
en sık 3 hata tipi: ...

--- KURAL UYUM KONTROLÜ ---
[ ] Uydurma sayı yok, her değer bir hesaptan geliyor
[ ] config/acceptance_criteria.yml DEĞİŞTİRİLMEDİ (git diff temiz)
[ ] Tüm çıktılar .meta.json ile yazıldı
[ ] CRS ve birimler Bölüm 12.1'e uygun
[ ] Karşılaştırılan büyüklükler fiziksel olarak aynı (12.4)
[ ] DATA_LOG.md güncellendi
[ ] Repoya secret yazılmadı
[ ] data/raw/ değiştirilmedi

--- SINIRLAMALAR ---
Bu çıktının bilinen zayıflıkları (en az 1 madde — "yok" kabul edilmez).

--- GENEL SONUÇ: PASS / FAIL ---

--- KULLANICI ONAYI BEKLEYENLER ---
12.11 kapsamına giren kararlar. Yoksa "yok" yaz.
```

### 13.2 Zorunlu öz-ölçüm adımları

Ajan raporu yazmadan önce şunları **fiilen çalıştırır**, tahmin etmez:

1. **Metrik hesabı** — `config/acceptance_criteria.yml`'deki her metriği hesapla.
   Eşiği koddan değil config dosyasından oku; eşiği kodda sabitlemek yasaktır.
2. **Spot kontrol** — `src/qa/spot_check.py` ile sabit seed'li 10 kayıt seç, referansla
   karşılaştır, tabloyu rapora koy. Bu, toplu metriğin gizlediği sistematik hatayı yakalar.
3. **Eşik diff kontrolü** — `git diff config/acceptance_criteria.yml` çalıştır.
   Çıktı boş değilse **FAIL ver ve dur.**
4. **Tekrarlanabilirlik** — aynı scripti iki kez çalıştır, çıktı checksum'ları aynı mı bak.
   Farklıysa determinizm bozuk → FAIL.
5. **Çapraz hesap** — kritik büyüklüklerde (hacim, alan, toplam tüketim) ikinci bir yoldan
   hesapla. Fark %1'i geçiyorsa raporla.

### 13.3 Dürüstlük kuralları (kullanıcı yokken özellikle geçerli)

- **FAIL vermek başarısızlık değildir.** Doğru ölçülmüş bir FAIL, süslenmiş bir PASS'ten
  kat kat değerlidir. Kullanıcı FAIL için ajanı suçlamaz; **gizlenmiş hata için suçlar.**
- Kriter kıl payı kaçtıysa (eşik ≤25 cm, ölçüm 25,4 cm) sonuç **FAIL**'dir. Yuvarlayarak
  geçirme.
- Ölçüm yapılamadıysa PASS verme; `ÖLÇÜLEMEDİ` yaz ve nedenini açıkla.
- "Muhtemelen doğru" diye geçirme; belirsizliği rapora yaz.
- Bir sayının nereden geldiğini gösteremiyorsan o sayıyı silmek, bırakmaktan iyidir.

### 13.4 Kullanıcı başında değilken (unattended mod)

**YAPAR:**
- Planlanmış aşamayı uygular, ölçer, Aşama Sonu Raporu yazar
- PASS ise bir sonraki aşamanın **planını hazırlar, ama başlatmaz**
- FAIL ise 12.6 protokolünü işletir, failure report yazar ve **DURUR**

**YAPMAZ:**
- Eşik, metrik, AOI, veri kaynağı veya metodoloji değiştirmez (12.11)
- Belirsiz durumda kendi kararını verip ilerlemez
- İki aşamayı arka arkaya onaysız tamamlamaz

**BİRİKTİRİR:**
Karar gerektiren her şeyi `reports/PENDING_DECISIONS.md`'ye yazar:

```
[TARİH] [AŞAMA] Soru: ...
  Seçenekler: A / B
  Ajanın önerisi ve gerekçesi: ...
  Bu karar verilmeden ilerlenemeyen işler: ...
```

Kullanıcı döndüğünde tek dosyaya bakıp hepsini cevaplayabilmelidir.

### 13.5 Oturum başı / sonu ritüeli

**Başında:** AGENTS.md + `PENDING_DECISIONS.md` + son Aşama Sonu Raporunu oku.
Nerede kalındığını tek cümleyle özetle, sonra başla.

**Sonunda:** Ne yapıldı / ne ölçüldü / ne bekliyor — üç madde. Yarım iş varsa
`PENDING_DECISIONS.md`'ye düş.

### 13.6 `src/qa/` klasörü

Öz-ölçüm araçları burada durur:

- `spot_check.py` — sabit seed'li N kayıt örnekleme + referans karşılaştırma tablosu
- `check_thresholds.py` — config'ten eşikleri okur, sonuçlarla karşılaştırır, PASS/FAIL döner
- `check_compliance.py` — 13.1 uyum listesini otomatik kontrol eder (config diff,
  .meta.json varlığı, raw dizin bütünlüğü, secret taraması)
- `make_stage_report.py` — Aşama Sonu Raporunu şablona göre üretir

Bu scriptler Aşama 0.4'te yazılır ve **proje boyunca değişmez** — ölçüm aracının kendisi
sonuçlara göre değiştirilemez.

---

## 14. Hata defteri — aynı hatayı tekrarlamama

Ajan oturumlar arasında hatırlamaz. Bu yüzden öğrenme **ajanın hafızasında değil, bu
depodaki dosyada** tutulur. `MISTAKES.md` projenin kurumsal belleğidir.

### 14.1 Temel kural

> **Her hata bir kez yapılabilir. İkinci kez yapılması ayrı ve daha ağır bir ihlaldir.**

Bir hata yakalandığında ajan onu düzeltmekle yetinmez; **tekrarını engelleyecek kuralı
yazar.** Hatanın kendisi bir anıdır, kural ise uygulanabilir bir davranıştır.
Ajan anıyı uygulayamaz, kuralı uygular.

Kötü kayıt: "AHN dosyasını yanlış CRS'te okudum."
İyi kayıt: "Her raster/vektör okumasında CRS loglanacak ve `config`'teki beklenen CRS ile
karşılaştırılacak; uyuşmazsa exception fırlatılacak."

### 14.2 `MISTAKES.md` formatı

Her kayıt şu alanları içerir:

```
## M-007 · [2026-10-14] · Aşama 1.2
Ne oldu:      Bina yükseklikleri 3DBAG'den sistematik 1,2 m düşük çıktı.
Kök neden:    b3_h_maaiveld referansı yerine mutlak z kullanıldı; NAP sıfırı atlandı.
Neden fark edilmedi: Toplu RMSE kabul aralığındaydı; sapma sistematik olduğu için
              ortalama maskeledi.
Türetilen kural: Yükseklik karşılaştırmalarında ortalama fark (bias/NMBE) her zaman
              RMSE ile BİRLİKTE raporlanacak. Yalnız RMSE raporlamak yasak.
Nerede uygulanır: src/qa/check_thresholds.py, tüm geometri raporları
Otomatik kontrol: check_compliance.py → rapor içinde bias alanı var mı?
Durum:        KAPALI (kural eklendi, kontrol otomatikleştirildi)
```

`Otomatik kontrol` alanı en değerli kısımdır: kural insan disiplinine bırakılmaz,
mümkün olan her durumda `src/qa/` içinde bir kontrole dönüştürülür. Otomatikleştirilemeyen
kural, uçuş öncesi kontrol listesine (14.4) eklenir.

### 14.3 Ne zaman kayıt açılır

Şunların hepsi kayıt açmayı gerektirir — "küçük hata" ayrımı yoktur:

- Kabul kriterinin başarısız olması
- Kullanıcının bir hatayı yakalaması veya düzeltmesi
- Yanlış çıkan ve sonradan fark edilen bir sayı
- Boşa giden çalıştırma (yanlış parametre, yanlış girdi, çökme)
- AGENTS.md kuralının ihlal edildiğinin fark edilmesi
- Bir varsayımın yanlış olduğunun anlaşılması

### 14.4 Oturum öncesi kontrol (pre-flight)

Her oturumun **ilk işi**, hiçbir kod yazmadan önce:

1. `MISTAKES.md`'yi oku
2. Bu oturumda çalışılacak aşamayla ilgili **AÇIK** kayıtları listele
3. Her birinin türetilmiş kuralını tek cümleyle tekrarla — kullanıcı hangi derslerin
   aktif olduğunu görsün
4. Ancak ondan sonra başla

Bu adım atlanırsa oturum geçersizdir.

### 14.5 Tekrar eden hata protokolü

Aynı kök nedene sahip bir hata **ikinci kez** olursa:

1. **DUR.** Düzeltip devam etme.
2. Kaydı `TEKRARLANDI` olarak işaretle ve tekrar sayısını artır.
3. Sor: *Kural yetersiz miydi, yanlış yerde mi duruyordu, yoksa hiç uygulanmadı mı?*
4. Kuralı güçlendir ve mümkünse **otomatik kontrole çevir** — insan disiplinine
   güvenmeyi bırak.
5. Kullanıcıya bildir. Tekrarlanan hata, tek seferlik hatadan farklı bir sorundur:
   koddaki değil, **süreçteki** bir boşluğu gösterir.

Aynı hata **üçüncü kez** olursa o adım otomatikleştirilir veya elle yapılacak işler
listesine (`docs/manual_steps.md`) taşınır. Üç kez başarısız olan bir yöntem korunmaz.

### 14.6 Yaygın hata sınıfları (proje başında bilinen riskler)

Aşağıdakiler bu proje tipinde sık görülür. Ajan bunlara karşı **baştan** dikkatli olur;
biri gerçekleşirse normal kayıt açılır.

| Sınıf | Tipik görünüm | Önleyici davranış |
|---|---|---|
| **CRS / yükseklik datumu** | Sessiz 1-2 m kayma, NAP atlanması | Her okumada CRS logla, beklenenle karşılaştır, uyuşmazsa hata fırlat |
| **Sistematik sapma maskelenmesi** | RMSE iyi ama model tümden kaymış | Bias/NMBE'yi RMSE ile birlikte raporla |
| **Birim karışması** | m² ↔ ha, kWh ↔ MJ, W/m² ↔ kWh/m² | Değişken adına birim ekle (`area_m2`, `eui_kwh_m2_yr`) |
| **Zaman dilimi** | UTC ↔ yerel saat, EPW saat kayması | Her zaman serisinde tz açıkça yazılı olsun |
| **Sessiz veri kaybı** | Join sonrası satır sayısı düşmüş | Her join öncesi/sonrası satır sayısını logla |
| **Farklı büyüklük kıyası** | LST ile hava sıcaklığı | 12.4 kontrolü zorunlu |
| **Tampon unutma** | Kenar binalar gölgesiz | Analiz B alanında, rapor A alanında |
| **Kapsam kayması** | Ajan istenmeyen ek işler yapar | Tek görev, tek çıktı; fazlası onay ister |
| **Sessiz atlama** | Hatalı kayıtlar loglanmadan düşürülür | 12.8 — her atlanan kayıt CSV'ye |

### 14.7 Kullanıcının rolü

Kullanıcı bir hata yakaladığında ajan şunu yapar: düzeltir, `MISTAKES.md`'ye kaydeder,
kuralı türetir ve mümkünse otomatik kontrole çevirir. **Sadece düzeltip geçmek yetersizdir** —
kaydedilmeyen hata, birkaç oturum sonra geri gelir.
