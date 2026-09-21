# Görsel doğrulama — sınıf 6 oranı sıfır çıkan yapılar

**Amaç:** AGENTS.md §12.13 / MISTAKES.md **M-011**. Bu yapıların ne olduğu şu an
bir **ÇIKARIM**'dır ve yalnızca BAG özniteliklerinden türetilmiştir. **P-012**
(Aşama 1'e hangi AHN sınıfları girecek) bu doğrulama bitmeden karara
bağlanmayacaktır.

**Dolduracak:** kullanıcı · **Tarih:** _______

---

## Nasıl doldurulur

1. `aoi/qa/zero_class6_buildings.geojson` dosyasını QGIS'e yükle (EPSG:28992,
   67 bina). Arka plan: **PDOK Luchtfoto 8 cm** (güncel).
2. `reports/visual_check_sample.csv` içindeki **12 binayı** sırayla aç.
   Koordinatlar `merkez_x_rd` / `merkez_y_rd` sütunlarında (RD New).
3. Her biri için aşağıdaki tabloya **GÖZLEM** yaz. Etiketler:
   **`depo/kulube`** · **`ev`** · **`baska`** · **`goruntude yok`**
4. Emin olamadığın yerde Street View'a da bak, NOT sütununa yaz.

> Örneklem **sabit seed** ile seçilmiştir (`seed = 28992`,
> `config/acceptance_criteria.yml → input_gate_ahn.visual_check`). Aynı liste
> istendiğinde yeniden üretilebilir.

---

## Doldurulacak tablo

| # | bag_id | alt grup | m² | bouwjaar | zemin oranı | **ÇIKARIM (benim tahminim)** | **GÖZLEM (senin)** | NOT |
|---|---|---|---|---|---|---|---|---|
| 1 | `0503100000041285` | B büyük | 1.665,0 | 2026 | 0,621 | **uçuş sonrası yapıldı** | | |
| 2 | `0503100000038184` | B büyük | 996,5 | 2023 | 0,989 | **uçuş sonrası yapıldı** | | |
| 3 | `0503100000039626` | A küçük | 3,1 | 2009 | 0,168 | depo/kulübe | | |
| 4 | `0503100000038679` | A küçük | 4,5 | 2007 | 0,041 | depo/kulübe | | |
| 5 | `0503100000039603` | A küçük | 7,8 | 1988 | 0,035 | depo/kulübe | | |
| 6 | `0503100000039621` | A küçük | 5,0 | 1998 | 0,062 | depo/kulübe | | |
| 7 | `0503100000039618` | A küçük | 4,7 | 1997 | 0,114 | depo/kulübe | | |
| 8 | `0503100000038260` | A küçük | 4,2 | 2023 | **0,996** | **uçuş sonrası yapıldı** ⚠️ | | |
| 9 | `0503100000039604` | A küçük | 13,8 | 2020 | 0,114 | depo/kulübe | | |
| 10 | `0503100000039608` | A küçük | 13,8 | 2001 | 0,063 | depo/kulübe | | |
| 11 | `0503100000039629` | A küçük | 2,8 | 2022 | 0,156 | depo/kulübe | | |
| 12 | `0503100000039630` | A küçük | 2,1 | 2016 | 0,157 | depo/kulübe | | |

---

## Bu örneklem iki ayrı şeyi aynı anda sınıyor

### Sınama 1 — iki okul (satır 1-2): ÖLÇÜMÜ doğrular

Bu ikisi rastgele seçilmedi, **her zaman dahil** edilir. Güncel Luchtfoto'da
(2025/2026) **okul binası görünüyorsa**, "AHN5 uçuşundan (2023-02) sonra
yapıldı" açıklaması **bağımsız olarak doğrulanmış** olur.

- **Beklenen:** ikisinde de **bina var** (2026 hava fotoğrafında), ama AHN5'te
  yoktu.
- **Beklenmeyen sonuç ne anlama gelir:** eğer Luchtfoto'da da bina yoksa,
  BAG kaydı gerçeği yansıtmıyor demektir ve D-019 yeniden değerlendirilir.

### Sınama 2 — 10 küçük yapı: ÇIKARIMI sınar

Bunlar "berging/depo" olduğu **varsayılan** yapılar. Doğrulanması gereken tam
olarak bu.

- **Beklenen:** çoğunlukla `depo/kulube`.
- **`ev` çıkarsa:** çıkarım yanlış demektir. Bu yapılar konut ise, sınıf 1'in
  Aşama 1'de dışlanması gerçek konutları kaybettirir — **P-012 yanıtı değişir**.
- **`goruntude yok` çıkarsa:** BAG'de var ama sahada yok; başka bir veri
  kalitesi bulgusudur.

---

## Ölçülmüş tahmin: `ground_class_ratio` alt grup A'yı ikiye bölüyor

Doğrulamadan **önce** kaydedilir, sonradan "zaten öyle diyordum" denmesin diye
(§12.13-3).

64 küçük yapının ayakizi içindeki **zemin (sınıf 2) noktası oranı** son derece
keskin ayrılıyor — arada hiç yapı yok:

| Zemin oranı | n | Yorum |
|---|---|---|
| **< 0,30** | **63** | Ayakizinde zemin olmayan bir şey var → **yapı mevcut, AHN sınıf 1 saymış** |
| 0,30 – 0,70 | **0** | — |
| **> 0,70** | **1** | Lazer yere ulaşmış → **uçuş anında yapı yoktu** |

Tek istisna: **`0503100000038260`** (4,2 m², bouwjaar **2023**, zemin oranı
**0,996**) — profili okullarla aynı, küçük yapılarla değil. Örneklemde
**8 numara** olarak yer alıyor.

**Tahminim:**
1. 3-7 ve 9-12 numaralar (zemin oranı 0,03-0,17) → **`depo/kulube`**, yapı
   fiziksel olarak orada.
2. **8 numara → `depo/kulube` görünür ama 2023'te yapılmıştır**; yani alt grup
   A'da değil, **D-020 kapsamında** ("geometrisi yok, uçuş sonrası") olmalıdır.

Bu tahmin tutarsa, `ground_class_ratio` Aşama 1 için **ucuz ve güvenilir bir
ayırıcı** demektir: "yapı var ama yanlış sınıflanmış" ile "uçuşta yapı yoktu"
ayrımını tek sayıyla verir. Tutmazsa, ayrım başka bir yolla kurulmalıdır.

---

## Sonuç (kullanıcı dolduracak)

**Özet:**

| Etiket | Kaç bina |
|---|---|
| `depo/kulube` | |
| `ev` | |
| `baska` | |
| `goruntude yok` | |

**Çıkarım doğrulandı mı?** ☐ Evet ☐ Kısmen ☐ Hayır

**İki okul güncel Luchtfoto'da görünüyor mu?** ☐ İkisi de ☐ Biri ☐ Hiçbiri

**`ground_class_ratio` tahmini tuttu mu?** ☐ Evet ☐ Hayır

**P-012 için sonuç:**

_______________________________________________

---

> Bu dosya doldurulduktan sonra: ajan sonucu
> `reports/00_stage_0_3_ahn_gate.md`'ye "görsel doğrulama örneklemi" olarak
> işler, M-011'i **KAPALI**'ya çeker ve P-012'yi karara açar.
> Doğrulama yapılamazsa çıkarım "çıkarıma dayalı" işaretiyle AGENTS.md §5
> sınırlamalarına girer (§12.13-4).
