# Aşama 0.3 — Aşama Sonu Raporu

```
=== AŞAMA SONU RAPORU ===
run_id:            RUN-2026-09-21-021 (kapı ölçümü), çoklu çalıştırma
aşama:             0.3 — AHN5 ve 3DBAG veri edinimi + girdi kalite kapısı
git_commit:        fbb2cd0 (+ bu rapor commit'i)
çalıştırma (UTC):  2026-09-21
veri dönemi:       geometri AHN5 2023-02-08/14 · öznitelik BAG 2026-09 ·
                   3DBAG sürümü BELİRSİZ: API etiketi v2023.10.08, içerik
                   parmak izi 2025.09.03 ile tutarlı (D-023)        (D-020)
```

> **Bu rapor elle yazılmıştır** (D-005: Aşama 0 raporları elle, 0.5'ten sonra
> otomatik).

---

## 1. Kabul kriteri sonuçları

| Kriter | Kaynak | Eşik (config'ten) | Ölçülen | Sonuç |
|---|---|---|---|---|
| **0-E** sert kapı | ahn.nl resmî spec (AHN4 tabanı) | medyan ≥ 10,0 p/m² | **35,89** | **PASS** |
| **0-F** beklenti | kendi ölçümümüz (37EN1 = 29,3) | medyan ≥ 20,0 p/m² | **35,89** | **PASS** |

**§12.2 denetim izi:** mühür commit'i `77fdfbb` → ölçüm commit'i `0efe40b`.
Mühür ölçümden **önce** gelir; git sırasıyla doğrulanabilir.

> D-015 kaydı bu sırada **eksikti** ve geriye dönük yazıldı (M-008). Git
> sırası bozulmamıştır; eksik olan gerekçe metniydi.

**Eşiksiz raporlanan ölçümler:** p10 = 17,79 · sıfır dönüşlü hücre %0,09 ·
sert kapı altında hücre %1,22 · beklenti altında hücre %14,13 ·
işlenen nokta 167.326.080 (B bbox) · 27.784 hücre (10×10 m).

---

## 2. Plan maddeleriyle karşılaştırma — YAPILAN / ERTELENEN / YAPILMAYAN

Onaylanan 0.3 planı 5 maddeydi. Hiçbir madde sessizce düşmesin diye tek tek:

### Madde 1 — AHN sürümü → **YAPILDI**
AHN5 seçildi ve D-013 ile mühürlendi ("3DBAG hangi sürümü kullanmış olursa
olsun, kapsama tamsa girdimiz AHN5'tir"). Delft için AHN5 kampanya 2023
doğrulandı. Uçuş tarihi LAZ `gps_time`'dan ölçüldü: **2023-02-08 / 02-14**.

### Madde 2 — Alt-fayanslar ve beklenen boyut → **YAPILDI**
9 alt-fayans (37EN1: 14,15,19,20,24,25 · 37EN2: 11,16,21), **3,12 GB**,
~420M nokta. Her alt-fayansın gerçek sınırı `.txt` yan dosyasından indirme
**öncesi** doğrulandı; kapsama kontrolü yapıldı; boş disk alanı karşılaştırıldı.
B alanı 37EN1'i taştığı için 37EN2 de gerekti.

### Madde 3 — 3DBAG sürümü ve kullandığı AHN sürümü → **YAPILDI (bu raporla tamamlandı)**
`b3_pw_bron` ölçümü 0.3 sırasında yapılmış ve D-013 / validation_protocol
§1.1b / AGENTS.md §5'e yazılmıştı. **Ancak** `b3_puntdichtheid_*` dağılımı
ölçülmemişti ve sonuç tek bir yerde toplanmamıştı — 0.3'ün aşama sonu raporu
olmadığı için. İkisi de **2026-09-21'de tamamlandı**:
`reports/00_stage_0_3_3dbag_source.md`, karar **D-021**.

Özet: %94,9 ahn5 · %3,5 ahn3 (2014) · %1,6 ahn4 (2020). 3DBAG'in "AHN5
kapsaması yetersiz" gerekçesi **bizim verimizde sınandı ve geçerli çıkmadı**
(o 349 binada bizim yoğunluğumuz 25–30 p/m², sıfır boşluk). Bu bir
**karşılaştırma** sınırlamasıdır, girdi sınırlaması değil.

### Madde 4 — LAZ bütünlük kontrolü, eşik hesaptan önce config'e → **YAPILDI**
İki kademeli kapı (0-E sert / 0-F beklenti) mühürlendi ve ölçüldü. Bkz. §1.
Bu, AGENTS.md **§12.12 girdi kalite kapısı** ilkesinin ilk uygulamasıdır
(D-014).

### Madde 5 — C aday hesabı 0.3'ün son adımı mı, ayrı 0.3b mi → **KARAR VERİLDİ: 0.3b**
Kullanıcı ayrımı onayladı. **C aday hesabı bu aşamada ÇALIŞTIRILMADI** —
ertelendi, bkz. §3.

### Plan dışı eklenenler (kullanıcı talimatıyla)
- **AGENTS.md §12.12** girdi kalite kapısı ilkesi (D-014) — **YAPILDI**
- **Bina bazlı çatı yoğunluğu CSV'si** (eşiksiz rapor metriği) — **YAPILDI**
- **`building_class_ratio`** sınıf 6 oranı sütunu (D-016) — **YAPILDI**
- **Sınıf kodu doğrulaması** (26 belgeli / 14 çıkarım, D-017) — **YAPILDI**
- **Sıfır grubu incelemesi + 2 okulun teşhisi** (D-018, D-019) — **YAPILDI**
- **Veri dönemi kararı** (D-020) — **YAPILDI**

---

## 3. ERTELENEN işler — neden ve neyi bekliyor

| İş | Durum | Neden | Neyi bekliyor |
|---|---|---|---|
| **0.3b — C aday hesabı** | **ERTELENDİ** | Kullanıcı onaylı ayrım; yükseklik kuralı (D-012) `b3_h_dak_max` gerektiriyordu, o da 3DBAG indirildikten sonra hazır oldu | Şimdi çalıştırılabilir — engeli yok |
| **P-012** Aşama 1'e hangi AHN sınıfları girecek | **ERTELENDİ** | 64 küçük yapının ne olduğu bir **ÇIKARIM**; §12.13 gereği karardan önce doğrulanmalı | Kullanıcının görsel kontrolü (`docs/visual_check_zero_class6.md`) |
| **Uçuş sonrası tespitinin A+B geneline yayılması** | **BAŞLAMADI** | Eşikler (K1/K2/K3) önerildi ama **onaylanmadı**; §12.2 gereği hesaptan önce mühürlenmeli | Kullanıcının eşik onayı |
| **P-014** uçuş sonrası binalar için yükseklik kaynağı | **BAŞLAMADI** | Kapsam ölçümünden sonra karar verilecek (kullanıcı sırası) | Yukarıdaki kapsam ölçümü |
| **Lineage özniteliği** (`measured_lod2` / `estimated_lod1` / `footprint_only`) | **BAŞLAMADI** | Tanımlanacak, henüz yazılmadı | — (bir sonraki iş) |
| **P-011** C alanı seçimi | **ERTELENDİ** | Planlı: 0.3b sonrası kullanıcı görsel onayı | 0.3b çıktısı |

## 4. YAPILMAYAN işler

| İş | Neden yapılmadı |
|---|---|
| **AHN sınıf 26 ve 14'ün AHN5 belgesinden doğrulanması** | **Belge yok.** AHN5 için sınıflandırma spesifikasyonu yayınlanmamış; doğrulama AHN4 şartnamesinden yapıldı ve bu sınırlama AGENTS.md §5'e yazıldı (D-017). Kod 14 hiçbir AHN belgesinde geçmiyor — **çıkarım** olarak etiketlendi |
| **Son mutasyon tarihi (iki okul için)** | PDOK BAG WFS `documentdatum` döndürmüyor; 3DBAG döndürüyor ama bu binalar 3DBAG'de yok. BAG Individuele Bevragingen API'si **yeni bir veri kaynağıdır** → §12.11 gereği kullanıcı kararı (P-013 notu) |
| **ATTRIBUTION.md / DATA_LOG.md `TODO_0.3` lisans alanları** | **Açık kaldı.** 3DBAG ve AHN attribution metinleri kaynaklarından alınmadı. Aşama 5 yayın kabul kriterini etkiler; şimdi kapatılmalı |

---

## 5. Sınırlamalar (AGENTS.md §5'e işlendi)

1. **Veri dönemi farkı 3,5 yıl** — geometri 2023-02, öznitelik 2026-09 (D-020)
2. **AHN5 için sınıflandırma spesifikasyonu yok** — yorumlar AHN4'ten taşındı
3. **AHN sınıf 6 BAG'den türer** — bağımsız doğrulama olarak kullanılamaz
4. **3DBAG karışık AHN kaynağı** — 377 bina; referans eski, girdimiz sağlam (D-021)
5. **3 yapı Aşama 1'den dışlanır** — AHN5'te karşılığı yok (D-019)
6. **Sıfır grubu açıklaması çıkarım** — doğrulanmamış (M-011, AÇIK)

## 6. Bu aşamada açılan hata kayıtları

| Kayıt | Konu | Durum |
|---|---|---|
| M-007 | Mekânsal yüklem yönü varsayıldı | KAPALI |
| M-008 | Config `decision_ref` karşılığı olmayan D kaydı | KAPALI |
| M-009 | Metrik ölçmesi gerekeni ölçmüyordu | KAPALI |
| M-010 | Özet istatistikle genelleme (+ sütun adı ek bulgusu) | KAPALI |
| M-011 | Karar veren çıkarım doğrulanmadı | **AÇIK** |

## 7. Aşama 0.3 sonucu

**PASS** — kabul kriterleri 0-E ve 0-F sağlandı, veri indirildi ve doğrulandı,
girdi kalite kapısı çalıştı.

**Aşama 1'e geçiş için kapatılması gerekenler:** P-012 (görsel doğrulama),
lineage tanımı, `TODO_0.3` attribution alanları. **P-013 kapandı** (D-019).
0.3b (C aday hesabı) Aşama 1'i engellemez; Aşama 4'ü engeller.


---

## 8. GÜNCELLEME — 2026-09-22 (rapor yazıldıktan sonra yapılanlar ve bulunanlar)

Bu bölüm §3'teki tabloyu **geçersiz kılar**; orijinal tablo tarihsel kayıt
olarak bırakıldı.

| İş | 2026-09-21 durumu | 2026-09-22 durumu |
|---|---|---|
| Uçuş sonrası tespitinin A+B'ye yayılması | BAŞLAMADI | **YAPILDI** — mühür `d4cf95b` → ölçüm `227d717` (D-022). 30 aday, 60 şüpheli, 50 olası yeniden yapım |
| Lineage özniteliği | BAŞLAMADI | **TANIMLANDI ve mühürlendi** (D-022) |
| A / B\A / konut kırılımı | — | **YAPILDI** — A'nın konut stokunun **%5,39'u (412 konut VBO)** belirsiz geometride; tamamı **3 binada**, hepsi "olası yeniden yapım" |
| P-014 yükseklik kaynağı | BAŞLAMADI | **ARAŞTIRILDI, karar yok** — AHN6 Delft için yok (en yakın 2025 şeridi 66 km); 3DBAG kaynak değil |
| Görsel kontroller | — | **HAZIR, kullanıcıda** — `docs/visual_check_zero_class6.md` (13 bina), `docs/visual_check_a_residential.md` (3 bina) |

### 2026-09-22'de bulunan ve düzeltilen hatalar

| Kayıt | Ne |
|---|---|
| **M-003 TEKRARI** | PROJ düzeltmesi import sırasına bağlıydı; `laspy` pyproj'u önce yüklediği için 0.3'ün **her LAZ scriptinde etkisizdi**. Geçmiş sonuçlar etkilenmedi (hiçbir script CRS dönüşümü yapmamıştı — tasarım değil şans). Sıradan bağımsız düzeltme + her çalıştırmada öz-test |
| **M-010 TEKRARI** | Kesilen (`[:40]`) bir metin, **260 konutlu** bir binayı raporda konut dışı gösterdi |
| **M-012** | Yukarıdaki PROJ uyarısını her komutta `grep -v` ile **ben sildim** |
| **M-013** | 3DBAG sürümünü API'nin kendi etiketinden okuyup "doğrulandı" yazdım; içerik 2025.09.03 ile tutarlı. Ayrıca `data/raw` altında bir dosyayı **elle** düzenlemiştim — geri alındı |
| **M-008 TEKRARI** | P-014'e 5 dosyada atıf yapıldı, kayıt hiç açılmamıştı. `src/qa/check_refs.py` yazıldı |

### §1 sonucuna etkisi

**Yok.** Kriter 0-E ve 0-F **PASS** olarak kalır: ölçümler AHN5 LAZ üzerinden,
yerel RD koordinatlarında yapıldı; ne PROJ hatası ne 3DBAG sürüm belirsizliği
bu ölçümlere girmiyor.

### §5 sınırlamalarına ekler

7. **3DBAG sürümü belirsiz** — API etiketi `v2023.10.08`, içerik 2025.09.03 (D-023, P-016)
8. **Aynı ayakizi üzerinde yeniden yapım ve inşaat halindeki binalar** (S2/S3)
   yalnızca görsel kontrolle ayırt edilebiliyor (D-022, `docs/visual_check_a_residential.md`)
9. **PROJ öz-testi sessiz datum farkını yakalamaz** (P-015)
