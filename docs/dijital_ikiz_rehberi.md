# Uçtan uca kentsel dijital ikiz — öğrenme rehberi ve boşluk analizi

**Kimin için:** projeyi yürüten öğrenci (ilk kez bir dijital ikiz yapıyor) ve
Reviewer. **Tarih:** 2026-09-26.

**Bu belge ne DEĞİL:** sistematik bir literatür taraması değil. Hızlı bir
kaynak taramasıdır (aşağıda listelenen ~15 kaynak). Kaynaktan gelen her
iddianın yanında kaynağı vardır; **kaynaksız cümleler benim sentezimdir** ve
öyle okunmalıdır.

> **VERİ DÖNEMİ (D-020).** Geometri AHN5 **2023-02-08/14**; BAG öznitelikleri
> **2026-09**.

---

## 1. Dijital ikiz nedir — ve bizimki tam olarak ne?

### Terim üç ayrı şey anlatabilir

Literatürde "dijital ikiz" kelimesi gevşek kullanılıyor. Ayrımı veri akışının
yönü yapıyor [Singh 2021; Gaffinet 2025]:

| Düzey | Fiziksel → dijital veri akışı | Dijital → fiziksel geri besleme | Örnek |
|---|---|---|---|
| **Dijital model** | elle / tek seferlik | yok | bir anlık görüntüden üretilmiş 3B model |
| **Dijital gölge** (shadow) | **otomatik**, sürekli | yok | sensörle güncellenen model |
| **Dijital ikiz** (dar anlam) | otomatik, sürekli | **var** (kontrol / karar) | fabrikada makineyi yöneten model |

Singh ve ark. dar anlamdaki ikizi, fiziksel nesneyle **gerçek zamanlı veri
alışverişi** olan sanal kopya olarak tanımlıyor [Singh 2021].

**Bizim projemiz bu tabloda "dijital model" satırındadır.** Geometri 2023
uçuşundan, öznitelikler 2026 BAG'inden tek seferlik alındı; canlı veri akışı
yok. Bu bir kusur değil — kentsel ikizlerin çoğu bu düzeyde başlar — ama
**raporda "dijital ikiz" kelimesini kullanıyorsak hangi düzeyde olduğunu
açıkça yazmak zorundayız** (AGENTS kural 2: doğrulanmamışı doğrulanmış gibi
sunma). Bunu karar olarak **P-027**'ye yazdım.

### Kentsel dijital ikizin katmanları

Albalkhy ve ark., 228 yayını tarayarak yapılı çevredeki ikizleri dört katmanda
tanımlıyor: **fiziksel, dijital, uygulama, kullanıcı** [Albalkhy 2024]. Bizde:

| Katman | Voorhof'ta karşılığı |
|---|---|
| Fiziksel | Voorhof'un binaları, zemini, bitki örtüsü |
| Dijital | AHN5 nokta bulutu, BAG, 3DBAG, bizim LOD2 modelimiz (Aşama 1-2) |
| Uygulama | güneş, enerji, mikroklima, rüzgâr, sel analizleri (Aşama 3-4) |
| Kullanıcı | CesiumJS web arayüzü + **doğrulama raporu** (Aşama 5) |

---

## 2. Uçtan uca iş akışı — genel şema ve bizim aşamalarımız

Aşağıdaki adımlar benim sentezimdir; iki sistematik taramanın zorluk
kategorileriyle ve 3DBAG üretim iş akışıyla örtüşüyor [Lei 2023; Weil 2023;
Peters 2021].

| # | Adım | Ne soruluyor | Bizde | Durum |
|---|---|---|---|---|
| 1 | **Amaç** | İkiz hangi soruyu cevaplayacak? | güneş + enerji çekirdek, diğerleri ikincil (AGENTS §0, §6) | tanımlı |
| 2 | **Alan** | Nerede, hangi ölçekte? | A (analiz) / B (tampon) / C / D (AGENTS §3) | A, B sabit |
| 3 | **Veri envanteri** | Hangi açık veri var, lisansı ne? | AGENTS §4 | tanımlı |
| 4 | **Edinim + köken** | İndir, checksum, sürüm sabitle | Aşama 0.3, DATA_LOG | yapıldı |
| 5 | **Girdi kalitesi** | Veri yeterince iyi mi, ne zamana ait? | girdi kapısı 0-E/0-F, uçuş dönemi | yapıldı |
| 6 | **3B rekonstrüksiyon** | Ayakizi + LiDAR → LOD1/LOD2 | Aşama 1 (roofer) | **sırada** |
| 7 | **Semantik zenginleştirme** | Her binaya kalıcı ID + öznitelik | Aşama 2 (3DCityDB, BAG ID) | planlı |
| 8 | **Analiz / simülasyon** | Güneş, enerji, mikroklima | Aşama 3-4 | planlı |
| 9 | **Doğrulama** | Sonuç bağımsız bir kaynağa karşı doğru mu? | her aşamada kabul kriteri | sürekli |
| 10 | **Yayın** | İnsanlar nasıl görecek? | Aşama 5 (3D Tiles, Cesium) | planlı |
| 11 | **Bakım / güncelleme** | Yeni veri gelince ne olur? | — | **plan yok** (bkz. §5) |

**3DBAG'den alınacak ders:** Peters ve ark., tüm Hollanda'yı modelleyen iş
akışını, yeni girdi geldiğinde **hızlıca yeniden çalıştırılabilecek** şekilde
kurduklarını ve **çıktı kalitesinin büyük ölçüde girdi kalitesine bağlı
olduğunu**, bu yüzden kaliteyi birkaç adımda izlediklerini yazıyor
[Peters 2021]. Bizim girdi kalite kapımız (Aşama 0.3) ve her çıktının
`.meta.json`'u tam olarak bunun uygulaması.

---

## 3. Başkaları nerede zorlanıyor?

İki bağımsız sistematik tarama aynı yere işaret ediyor:

- **Weil ve ark.** 8 zorluk kategorisi buluyor; en çok vurgulananlar
  **veri/model semantiği, eksik veri, veri kalitesi ve modelleme** [Weil 2023].
- **Lei ve ark.** literatür taramasını bir Delphi uzman anketiyle
  birleştirip 14 teknik + 9 teknik olmayan zorluk buluyor; en ağır olanlar
  **birlikte çalışabilirlik** (farklı semantik standartlar) ve **pratik
  değer** [Lei 2023].

**Bizim için anlamı:** ikizin zor kısmı güzel bir 3B model üretmek değil;
verinin **ne olduğunu doğru anlamak** ve **doğru şeyle karşılaştırmak**.
Aşağıdaki boşlukların çoğu tam olarak bu türden.

---

## 4. Temel kavramlar (kısa sözlük)

| Kavram | Ne demek | Projede nerede |
|---|---|---|
| **LOD** (Level of Detail) | Bina modelinin ayrıntı düzeyi. LOD1 = düz çatılı kutu, LOD2 = çatı biçimi var | Aşama 1: LOD1.2/1.3/2.2 |
| **CityJSON** | 3B şehir modelleri için JSON formatı; CityGML'den hafif. OGC tarafından standart olarak kabul edildi [Geonovum] | 3DBAG, bizim çıktımız |
| **Semantik model** | Geometri + "bu yüzey çatı, bu duvar" + öznitelikler | Aşama 2 |
| **Tutarlılık kontrolü vs bağımsız doğrulama** | Aynı ham veriden türeyen iki ürünü karşılaştırmak doğrulama değildir | AGENTS §5, §12.10 (3DBAG de AHN'den türer) |
| **Arşetip** (UBEM) | Binaları tiplere ayırıp her tipi bir kez simüle etmek | Aşama 3 |
| **UBEM** | Kentsel ölçekte bina enerji modellemesi | Aşama 3 |
| **Kalibrasyon vs doğrulama** | Kalibrasyon = modeli ölçüme uydurmak; doğrulama = uydurulmamış veriyle sınamak. **Aynı veri ikisine birden kullanılamaz** | §5 boşluk E-4 |
| **Ön-kayıt** (pre-registration) | Eşiği ve yöntemi sonucu görmeden sabitlemek | AGENTS §12.2, bütün "mühür"lerimiz |

**Arşetip yaklaşımı literatürde standart:** Sokol ve ark. UBEM'in en yaygın
kuruluş biçimini "stoku arşetiplere bölmek, her birini tanımlamak ve modeli
**toplulaştırılmış ölçülmüş tüketimle** karşılaştırarak doğrulamak" olarak
tarif ediyor [Sokol 2016]. Bizim PC6 düzeyinde karşılaştırmamız (AGENTS §12.3)
bu çizgide. Mattsson ve ark. daha az arşetipli basit modellerin, daha ayrıntılı
modellere yakın sonuç verebildiğini gösteriyor [Mattsson 2025] — AGENTS'taki
"5-8 arşetip" hedefiyle uyumlu.

---

## 5. BOŞLUK ANALİZİ — planımızda olmayan ama olması gerekenler

Bu bölüm bu belgenin asıl işi. Aşağıdakilerin **hiçbiri** repoda kayıtlı
değildi (2026-09-26'da `SJV`, `salder`, `stadsverwarming`, `CDSM`, `vegetat`
terimleri arandı; tek eşleşme ilgisiz bir sınıf kodu belgesiydi).

Her satırda **olgu** (kaynaktan doğrulandı) ile **çıkarım** (benim
yorumum) ayrı yazıldı (AGENTS §12.13).

### E — Enerji karşılaştırması (Aşama 3) — en yüksek etki

**E-1 · Stedin verisi ölçülmüş tüketim DEĞİL, "standaardjaarverbruik" (SJV).**
- **OLGU** (Stedin veri açıklaması, 2026-09-26'da okundu): SJV, "bir
  bağlantıdaki beklenen yıllık tüketimdir, **standartlaştırılmış koşullarda ve
  normalleştirilmiş bir yıla göre**"; ve "önceki yılın tüketimine
  dayanır". Referans tarihi her zaman 1 Ocak'tır [Stedin].
- **ÇIKARIM:** Modeli **gerçek bir yılın** hava verisiyle (ör. KNMI 2023)
  çalıştırıp SJV ile karşılaştırmak farklı büyüklükleri karşılaştırmak olur
  (AGENTS §12.4). Model **normalleştirilmiş bir yıl** için çalıştırılmalı.
  Ama "normalleştirilmiş yıl"ın tam tanımı (hangi derece-gün tabanı, hangi
  profil) Stedin sayfasında **yok** → Aşama 3'ten önce kaynağından
  bulunmalı. TMYx EPW'nin bu tanımla aynı olup olmadığı **bilinmiyor.**
- → **P-022**

**E-2 · Gaz SJV'si m³ cinsinden ve yalnızca ısıtma değil.**
- **OLGU:** SJV gaz için m³, elektrik için kWh [Stedin].
- **ÇIKARIM:** Bir konut gaz bağlantısı tipik olarak ısıtma + sıcak su +
  (varsa) pişirme içerir. Model yalnızca alan ısıtması çıkarırsa sistematik
  olarak düşük kalır. m³ → kWh dönüşümü için kaynaklı bir ısıl değer
  gerekir (**henüz seçilmedi, sayı yazmıyorum**).
- → **P-022**

**E-3 · Elektrik SJV'si güneş panelleriyle kısmen "salderen" edilmiş olabilir.**
- **OLGU:** Eski tip (geri dönen) sayaçlarda SJV **net** (üretim düşülmüş);
  diğer tüm durumlarda yalnızca tüketime dayanır. Veri,
  `LEVERINGSRICHTING_PERC` sütununda net tüketimi olan bağlantıların oranını
  verir ve bu oran "geri beslemeyle (ör. güneş panelleri) düşer" [Stedin].
- **ÇIKARIM:** Güneş paneli yoğun PC6'larda elektrik karşılaştırması
  karışık bir büyüklükle yapılır. PC6 dışlama kuralı, **veriye bakmadan
  önce** mühürlenmeli.
- → **P-023**

**E-4 · Blok ısıtması (blokverwarming) küçük tüketim dosyasında görünmeyebilir.**
- **OLGU:** Küçük tüketim (kleinverbruik) gaz bağlantısı **en fazla G25**'tir
  (40 m³/saat); üstü büyük tüketimdir [ENGIE]. Stedin açık verisi yalnızca
  küçük tüketim bağlantılarını içerir [Stedin]. Blokverwarming'de **bir gaz
  bağlantısı** bütün bir bloğa ısı ve çoğu zaman sıcak su verir [Woonbond,
  overstappen.nl].
- **ÇIKARIM (doğrulanmadı):** Voorhof'un 1960'lı yüksek bloklarında blok
  ısıtması varsa ve kazan bağlantısı G25'i aşıyorsa, **o blokların ısıtma
  gazı PC6 verisinde hiç yoktur.** Model ise o ısıtmayı üretir → model,
  ölçümden sistematik olarak yüksek çıkar ve bunun sebebi modelin hatası
  değil verinin kapsamıdır.
- **Doğrulama yolu (ben öneriyorum):** Her PC6 için Stedin gaz
  **bağlantı sayısı** ile BAG'deki **konut VBO sayısı** karşılaştırılır. Oran
  1'in çok altındaysa o PC6 toplu ısıtmalıdır (blok / şehir ısıtması / tümüyle
  elektrikli). Oran eşiği **veriye bakmadan önce** mühürlenmeli.
- → **P-023**

**E-5 · Hangi Stedin yılı?**
- **OLGU:** Stedin her yıl 1 Ocak referans tarihli bir dosya yayınlıyor;
  sitede "Verbruiksdata 2026" listeleniyor [Stedin].
- **ÇIKARIM:** Geometrimiz Şubat 2023. 1 Ocak 2024 referanslı dosya 2023
  tüketimine dayanır → geometriyle aynı dönem. 2026 dosyası, arada
  yenilenen / yalıtılan / ısı pompasına geçen binaları içerir.
- → **P-024**

**E-6 · Kalibrasyon ile doğrulama ayrılmalı.**
- **OLGU:** Amsterdam'da posta kodu düzeyinde bir ısıtma çalışması,
  kalibrasyon için **6 yıl**, doğrulama için **ayrı 2 yıl** kullanıyor
  [Wang 2020]. Bayesçi arşetip kalibrasyonu da ayrı eğitim ve test
  kümeleriyle doğrulanıyor [Sokol 2016].
- **ÇIKARIM:** Arşetip parametrelerini Stedin'e göre ayarlar, sonra aynı
  Stedin verisiyle "doğrularsak" bu doğrulama değildir — model zaten ona
  uydurulmuştur. Ya **hiç kalibrasyon yapılmaz** (saf fizik tabanlı model,
  sonuç olduğu gibi raporlanır) ya da PC6'lar / yıllar **önceden** eğitim ve
  test olarak ayrılır.
- → **P-025**

**E-7 · Beklenen sapmanın yönü önceden yazılmalı (Hollanda'ya özgü).**
- **OLGU:** ~200.000 Hollanda konutunda, **enerji etiketi kötü** konutlar
  etiketin öngördüğünden **çok daha az**, verimli olanlar **daha fazla**
  tüketiyor [Majcen 2013a]. Almanya'da 3.400 konutta ortalama **%30** daha az
  ısıtma enerjisi ölçülmüş ve buna "prebound etkisi" denmiş
  [Sunikka-Blank 2012]. Teorik gaz tüketimini en çok **iç sıcaklık,
  havalandırma oranı ve U-değeri doğruluğu** etkiliyor [Majcen 2013b].
- **ÇIKARIM:** Voorhof 1960-1975 stoku, büyük olasılıkla kötü etiketli.
  Standart kullanım varsayımıyla kurulan fizik tabanlı bir arşetip modeli
  **ölçümden yüksek** çıkmaya eğilimli olacaktır. Bu beklenen yön, sonuç
  görülmeden rapora yazılmalı — sonuç gelince "zaten biliyorduk" denemesin
  (§12.13-3). **Bu bir karar değil, bir ön-kayıttır;** P-025'e not olarak
  eklendi.

### G — Güneş analizi (Aşama 3)

**G-1 · Ağaç gölgesi planda yok.**
- **OLGU:** SOLWEIG bitki örtüsünü iki ayrı raster ile alır: kanopi yüzeyi
  (**CDSM**) ve gövde bölgesi (**TDSM**); CDSM zemin üstü yükseklik olarak,
  ağaç olmayan piksellerde 0 olmalı. UMEP'in LiDAR'dan bu girdileri üretme
  eğitimi var [UMEP]. Austin'de yapılan bir çalışmada bağlam (ağaçlar)
  dahil edilmediğinde ortalama yıllık çatı ışınımı **%9,3** yüksek çıkmış
  [Waqas 2023].
- **ÇIKARIM:** AHN5'imizde bitki örtüsü noktaları zaten var (sınıf 1'in
  büyük kısmı). Onları kullanmazsak ağaç altındaki çatıların güneş
  potansiyeli sistematik olarak yüksek çıkar — AGENTS §3'ün tampon için
  uyardığı hatanın aynısı, bu sefer ağaç için.
- → **P-026**

### T — Terim ve iddia

**T-1 · "Dijital ikiz" hangi düzeyde?** §1'de anlatıldı. Rapor başlığında ve
özetinde düzey açıkça yazılmalı. → **P-027**

### B — Bakım

**B-1 · Güncelleme planı yok.** AHN6 Delft'i henüz kapsamıyor (0.3'te
ölçüldü); geldiğinde ne olacağı tanımlı değil. Bizim boru hattımız
scriptlerle kurulduğu için yeniden çalıştırmak teknik olarak kolay; eksik
olan bir **karar**: hangi girdi değişince hangi aşama yeniden koşulur.
Aciliyeti yok, Aşama 5 öncesi yazılmalı. *(P açılmadı — not olarak burada.)*

---

## 6. Görsel kontrolü kim, neyle yapar?

Kullanıcı sordu: "Google Maps'e sen bakamaz mısın?"

**Olgular:**
- Google Maps / Street View'u açıp gezinecek bir tarayıcım yok. Street View'u
  programla çekmek ücretli bir API anahtarı gerektirir ve Google görüntüleri
  kapalı veridir (AGENTS kural 4).
- **PDOK'un açık hava fotoğrafı servisi** var: WMS katmanları arasında
  **2022, 2023, 2024, 2025, 2026** ortofotoları listeleniyor; servis ücret ve
  erişim kısıtı olmadığını beyan ediyor (GetCapabilities, 2026-09-26).
- Hava fotoğrafı **yukarıdan** bakar. "Bu yapı ne?" ve "2023'te orada mıydı?"
  sorularına cevap verebilir; **kat sayısını veremez** — kat sayımı cephe
  görüntüsü ister.

**ÇIKARIM ve öneri:** Kullanıcının işini ikiye bölmek mümkün:

| İş | Kim | Kaynak |
|---|---|---|
| 22 yapı: "ne?" + "2022/2023'te var mıydı?" (13 sıfır örneği + 3 blok + 6 uçuş sonrası) | **ajan ilk geçiş**, kullanıcı sabit seed'li bir alt kümeyi kontrol eder | PDOK Luchtfoto 2022 / 2023 / 2026 |
| 22 bina: kat sayısı (10 kalibrasyon + 3 blok + 6 büyük yapı + gerekirse 3 yedek) | **kullanıcı** | Street View |

**İki çekince:**
1. **Bağımsızlık.** "Bu depo" / "uçuştan sonra yapıldı" çıkarımlarını ben
   yaptım. Aynı çıkarımı yine ben doğrularsam kör bir gözlemci değilim —
   ne beklediğimi biliyorum. Bu yüzden benim etiketlerimin **sabit seed'li bir
   alt kümesini kullanıcının kontrol etmesi** şart (§12.13-2).
2. **Fotoğrafın çekim tarihi.** "2023 ortofotosu"nun Şubat uçuşundan önce mi
   sonra mı çekildiği **doğrulanmadı**. Katman meta verisinden bakılmadan
   "2023'te vardı" denemez.

PDOK Luchtfoto AGENTS §4 envanterinde **yok** → yeni veri kaynağı → kullanıcı
onayı gerekir (kural 3). → **P-021**

---

## 7. Öğrenme yolu — hangi sırayla ne okumalı

Önerim (benim sentezim), projenin aşamalarıyla aynı sırada:

1. **Kavram:** Singh 2021 (terimler) → Albalkhy 2024 (katmanlar) → Lei 2023
   (zorluklar). Bu üçü "dijital ikiz ne, ne değil" sorusunu kapatır.
2. **Geometri (Aşama 1'den önce):** Peters 2021 — 3DBAG'in nasıl üretildiği.
   Bizim Aşama 1'imiz bunun küçük ölçekli bir tekrarı.
3. **Enerji (Aşama 3'ten önce):** Sokol 2016 (arşetip + kalibrasyon) →
   Majcen 2013a (Hollanda'da teori ile gerçek arasındaki fark) → Wang 2020
   (Amsterdam, posta kodu düzeyi, eğitim/doğrulama ayrımı). Üçüncüsü bizim
   yapacağımız işe en yakın örnek.
4. **3DBAG ile enerji:** TU Delft'ten (Stoter ekibi) bir çalışma 3DBAG 2.0'ı
   SimStadt ve CitySim ile deniyor, sonuçları 3DCityDB'ye Energy ADE ile
   yazıyor [Stoter 2021] — bizim Aşama 2-3 zincirinin neredeyse aynısı.

---

## Kaynaklar

- **[Albalkhy 2024]** [Digital twins in the built environment: Definition, applications, and challenges](https://consensus.app/papers/details/0e49eabf569351adb0dd695273a8a0c1/?utm_source=claude_code) — Albalkhy ve ark., *Automation in Construction*
- **[Gaffinet 2025]** [Human Digital Twins: A systematic literature review and concept disambiguation for industry 5.0](https://consensus.app/papers/details/30e1d0c6ad5354288601fa06136dc33a/?utm_source=claude_code) — *Computers in Industry* (model / gölge / ikiz ayrımı için)
- **[Lei 2023]** [Challenges of urban digital twins: A systematic review and a Delphi expert survey](https://consensus.app/papers/details/b9892c278b715071a569404eb9d73256/?utm_source=claude_code) — *Automation in Construction*
- **[Stoter 2021]** [Testing the new 3D BAG dataset for energy demand estimation of residential buildings](https://consensus.app/papers/details/e3f6bf92dce35c2babb6c7c9add2708c/?utm_source=claude_code) — *ISPRS Archives* (arama kaydında yazar olarak J. Stoter görünüyor; tam yazar listesi doğrulanmadı)
- **[Majcen 2013a]** [Theoretical vs. actual energy consumption of labelled dwellings in the Netherlands](https://consensus.app/papers/details/7309122e25a05309b632cf106407df51/?utm_source=claude_code) — *Energy Policy*
- **[Majcen 2013b]** [Actual and theoretical gas consumption in Dutch dwellings: What causes the differences?](https://consensus.app/papers/details/f619321bca185e1eaaafc482a4aa4b6e/?utm_source=claude_code) — *Energy Policy*
- **[Mattsson 2025]** [Archetypes-based calibration for urban building energy modelling](https://consensus.app/papers/details/f6946038c6c4574b9e4558597d3033cc/?utm_source=claude_code) — *Energy and Buildings*
- **[Peters 2021]** [Automated 3D reconstruction of LoD2 and LoD1 models for all 10 million buildings of the Netherlands](https://consensus.app/papers/details/e01a365ebd3c52d1a6406151a9017297/?utm_source=claude_code) — arXiv (AGENTS §9'daki 3DBAG referansı)
- **[Singh 2021]** [Digital Twin: Origin to Future](https://consensus.app/papers/details/4ec44da71fbe5e158f339d106a116738/?utm_source=claude_code) — *Applied System Innovation*
- **[Sokol 2016]** [Validation of a Bayesian-based method for defining residential archetypes in urban building energy models](https://consensus.app/papers/details/c2074d983fde57a49137b97e636cef4b/?utm_source=claude_code) — *Energy and Buildings*
- **[Sunikka-Blank 2012]** [Introducing the prebound effect](https://consensus.app/papers/details/e86b5044074951f0aaf439ccde7e30e0/?utm_source=claude_code) — *Building Research & Information*
- **[Wang 2020]** [Bayesian calibration at the urban scale: Amsterdam](https://consensus.app/papers/details/8eae07e1512456d18e4189ce688aa544/?utm_source=claude_code) — *Journal of Building Performance Simulation*
- **[Waqas 2023]** [An Integrated Approach for 3D Solar Potential Assessment at the City Scale](https://consensus.app/papers/details/d071d6b103bc562c8bbd39645a03c2e1/?utm_source=claude_code) — *Remote Sensing*
- **[Weil 2023]** [A Systemic Review of Urban Digital Twin Challenges](https://consensus.app/papers/details/525b7b846e5c57718b966a54b8369260/?utm_source=claude_code) — *Sustainable Cities and Society*
- **[Stedin]** [Verbruiksgegevens — Open data | Stedin](https://www.stedin.net/zakelijk/open-data/verbruiksgegevens) — SJV tanımı, `LEVERINGSRICHTING_PERC`, salderen notu (okundu 2026-09-26)
- **[ENGIE]** [Wat is een kleinverbruikaansluiting?](https://www.engie.nl/klantenservice/kleinverbruikaansluiting) — G25 sınırı
- **[Woonbond]** [Grip op energierekening bij blokverwarming](https://www.woonbond.nl/thema/huren-en-geld/grip-op-energierekening-bij-blokverwarming/) · **[overstappen.nl]** [Blokverwarming](https://www.overstappen.nl/energie/blokverwarming/)
- **[UMEP]** [Generating UMEP input data from a LiDAR point cloud](https://umep-docs.readthedocs.io/projects/tutorial/en/latest/Tutorials/LidarProcessing.html) · [SOLWEIG Manual](https://umep-docs.readthedocs.io/en/latest/OtherManuals/SOLWEIG.html)
- **[Geonovum]** [3D: Wat is er al, wat kies je en wat kan er straks nog meer?](https://www.geonovum.nl/over-geonovum/actueel/3d-wat-is-er-al-wat-kies-je-en-wat-kan-er-straks-nog-meer) — CityJSON'ın OGC kabulü
- **Hollanda'daki gerçek örnekler:** [Rotterdam Open Urban Platform](https://www.rotterdam.nl/digitale-stad) · [VNG — Digital twin voor alle gemeenten](https://vng.nl/praktijkvoorbeelden/digital-twin-voor-alle-gemeenten)
