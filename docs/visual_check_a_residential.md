# Görsel kontrol — A'daki belirsiz geometrili KONUT binaları

**Amaç:** AGENTS.md §12.13 · D-022 · `reports/00_stage_0_3_uncertain_geometry_breakdown.md`
**Dolduracak:** kullanıcı · **Tarih:** _______

> **VERİ DÖNEMİ (D-020).** Geometri AHN5 **2023-02-08 / 02-14**; BAG
> öznitelikleri **2026-09**.

---

## Neden hepsi, neden örneklem değil

A'nın konut stoku **7.637 konut VBO**. Bunların **412'si (%5,39)** belirsiz
geometrili binalarda — ve **412'sinin tamamı yalnızca 3 binada**. Uçuş sonrası
ve şüpheli gruplarında A'da **hiç** konut yok.

3 bina örneklemesiz, tek tek kontrol edilebilir.

| # | bag_id | konut VBO | m² | bouwjaar | lat | lon |
|---|---|---|---|---|---|---|
| 1 | `0503100000037336` | **260** | 1.251,6 | 2023 ⚠️ belirsiz | 51.9965683 | 4.3536810 |
| 2 | `0503100000037335` | **94** | 1.961,8 | 2023 ⚠️ belirsiz | 51.9996530 | 4.3592248 |
| 3 | `0503100000038177` | **58** | 819,9 | 2025 | 51.9953681 | 4.3532921 |

Üçü de **"olası yeniden yapım"** grubunda (D-022: `bouwjaar ≥ 2023` ve uçuş
sonrası aday değil). **1 ve 2'de `bouwjaar == 2023` belirsizdir** — BAG yıl
verir, uçuş Şubat 2023'tedir. **3 numara**, önceki örneklemdeki AMAÇLI 13
numarayla aynı binadır.

---

## Ölçülenler (kontrolden ÖNCE kaydedildi — §12.13-3)

| # | sınıf 6 oranı | zemin oranı | tek dönüşlü >2 m (p/m²) | sınıf 6 kapsama |
|---|---|---|---|---|
| 1 | **0,566** | 0,002 | 48,47 | 0,994 |
| 2 | 0,744 | 0,097 | 23,61 | 0,859 |
| 3 | 0,785 | 0,002 | 69,58 | 0,988 |

**Ne söylüyor:** Şubat 2023'te üçünün de ayakizinde, bugünkü ayakizinin
%86–99'unu örten **katı bir çatı** vardı (tek dönüşlü yoğunluk yüksek → bitki
örtüsü değil).

**Ne söylemiyor:** o yapının **bugünkü bina olup olmadığını**.

---

## Açık olan ÜÇ senaryo (ikisi değil)

D-022'deki yeniden yapım kuralı iki senaryoyu ayırmak için yazıldı. Bu üç
binaya bakınca **üçüncü bir senaryo** ortaya çıkıyor ve kural onu ayrı
adlandırmıyor:

| | Senaryo | AHN5'in gördüğü | Aşama 1 riski |
|---|---|---|---|
| **S1** | Bina 2023 öncesinden beri **aynı**; `bouwjaar` bir kayıt/tadilat olayı | bugünkü bina | yok |
| **S2** | Eski bina **yıkıldı, yerine yenisi yapıldı** (sloop-nieuwbouw) | **eski** bina | eski geometri yeni binaya giydirilir |
| **S3** | Bina Şubat 2023'te **inşaat halindeydi**, 2023'te tamamlandı | **yarım** bina (eksik kat / eksik çatı) | yükseklik ve çatı biçimi **eksik** çıkar |

**S3 neden olası:** 1 ve 2, 260 ve 94 konutlu bloklar ve `bouwjaar 2023`.
BAG'de bouwjaar genellikle **tamamlanma** yılıdır. Bu ölçekte bir blok 2023'te
tamamlandıysa, Şubat 2023'te büyük olasılıkla iskelet/kaba inşaat halindeydi.

**1 numarada dikkat çeken ölçüm:** sınıf 6 oranı **0,566** — diğerlerinden
belirgin düşük — ama kapsama **0,994** ve zemin oranı **0,002**. Yani çatı
her yerde var ama noktaların ~%43'ü bina sınıfında değil. Bu **S3 ile
uyumludur** (AHN, uçuş anındaki BAG pandenkaart'ına göre sınıflar — §9.2;
henüz kayıtlı olmayan bir inşaat "overig" sayılabilir), ama **başka
açıklamalarla da** uyumludur (yeşil çatı, çatı üstü tesisat). **Bu bir
ÇIKARIMDIR**, ölçüm değil.

---

## Doldurulacak tablo

Kaynaklar: **PDOK Luchtfoto** — 2023 ve güncel yıl; mümkünse **Street View**
tarih geçmişi.

| # | bag_id | 2023 hava fotoğrafında ne var? | Güncel fotoğrafta ne var? | **Senaryo** (S1 / S2 / S3 / karar veremedim) | NOT |
|---|---|---|---|---|---|
| 1 | `0503100000037336` | | | | |
| 2 | `0503100000037335` | | | | |
| 3 | `0503100000038177` | | | | |

> ⚠️ **Luchtfoto 2023'ün çekim tarihini kontrol et.** Hava fotoğrafı AHN5
> uçuşuyla (Şubat 2023) aynı gün çekilmemiştir. Luchtfoto 2023 Şubat'tan
> **sonra** çekildiyse, S3'teki bir inşaat fotoğrafta daha ileri bir aşamada
> görünür. Fotoğrafın tarihini NOT sütununa yaz. (Çekim tarihini ben
> doğrulamadım — varsayım yazmıyorum.)

---

## Sonuç ne değiştirir

| Sonuç | Aşama 1'de ne olur |
|---|---|
| **S1** | Bina `measured_lod2` olarak normal rekonstrüksiyona girer |
| **S2** veya **S3** | AHN5 geometrisi **bugünkü binayı temsil etmiyor**. Bina `measured_lod2` **olamaz**; P-014'e göre `estimated_lod1` veya `footprint_only` olur ve **doğrulama istatistiklerinin dışında kalır** (D-022) |
| **Karar veremedim** | §12.13-4: karar "çıkarıma dayalı" işaretlenir ve §5 sınırlamasına girer |

**Etki büyüklüğü:** üçü birlikte A'nın konut stokunun **%5,39'u**. S2/S3
çıkarsa bu, Aşama 3'teki PC6 enerji karşılaştırmasında ilgili PC6'ları
**doğrudan** etkiler — bu binaların PC6'ları ayrıca işaretlenmelidir.

---

## Sonuç (kullanıcı dolduracak)

**Senaryolar:** 1 = ___ · 2 = ___ · 3 = ___

**Luchtfoto 2023 çekim tarihi:** _______

**`rebuild_suspect` kuralı gerçek bir riski yakaladı mı?** ☐ Evet ☐ Hayır

**S3 (inşaat halinde) gerçek mi?** ☐ Evet → D-022'ye üçüncü senaryo olarak
eklenir ☐ Hayır
