# 3DBAG'in nokta bulutu kaynağı — ölçüm sonucu

**Tarih:** 2026-09-21 · **Aşama:** 0.3 madde 3 · **Karar:** D-013, D-021

> **VERİ DÖNEMİ (D-020).** Geometri AHN5 uçuş dönemini (**2023-02-08 / 02-14**)
> temsil eder; BAG öznitelikleri **2026-09** anlık görüntüsüdür. 3DBAG sürümü
> **v2023.10.08** (BAG anlık görüntüsü ~2023).

Kapsam: B alanı + 50 m, **7.376 bina** (`Building` nesnesi).

---

## 1. Hangi AHN sürümü kullanılmış?

| `b3_pw_bron` | Bina | Pay | `b3_pw_datum` |
|---|---|---|---|
| **ahn5** | 6.999 | **%94,9** | 2023 |
| ahn3 | 261 | %3,5 | **2014** |
| ahn4 | 116 | %1,6 | 2020 |

**Seçim gerekçesi** (`b3_pw_selectie_reden`):

| Gerekçe | Bina |
|---|---|
| `PREFERRED_AND_LATEST` | 7.317 (%99,2) |
| `_HIGHEST_YET_INSUFFICIENT_COVERAGE` | 49 |
| `_LATEST` | 10 |

`b3_pw_onvoldoende` = `False` (7.376/7.376) — 3DBAG hiçbir bina için nokta
bulutunu "yetersiz" işaretlememiş.

`b3_kwaliteitsindicator`: **True 7.278** / **False 98**.

---

## 2. 3DBAG'in kendi nokta yoğunluğu ölçümü

`b3_puntdichtheid_*` her bina için **üç sürüm birden** ölçülmüş (n = 7.376,
geçersiz değer yok):

| Sürüm | Medyan | p10 | p90 | Maks |
|---|---|---|---|---|
| ahn3 | 14,55 | 7,68 | 17,67 | 38,58 |
| **ahn4** | **33,02** | 21,85 | 50,12 | 90,79 |
| **ahn5** | **22,42** | 14,65 | 34,91 | 69,75 |

### Beklenmeyen sonuç: AHN4 yoğunluğu AHN5'ten YÜKSEK

3DBAG'in kendi tutarlı ölçümünde, aynı ayakizleri üzerinde **AHN4 (33,02)
AHN5'ten (22,42) daha yoğun**. Bu, AGENTS.md §2'nin "AHN5 Randstad ≥20 p/m²"
beklentisinin ardındaki örtük varsayımı — yeni sürüm daha yoğundur —
**desteklemiyor**.

**Bizim ölçümümüzle karşılaştırılamaz:** bizim medyanımız 35,89 p/m²; ama o,
B alanındaki **10×10 m hücrelerde tüm sınıflar** üzerinden. 3DBAG'inki **bina
ayakizi** başına ve kendi filtresiyle. İki sayı farklı şeyi ölçüyor; buradaki
anlamlı karşılaştırma **3DBAG'in kendi içindeki** sürüm sıralamasıdır (aynı
yöntem, aynı binalar).

**Eşiklere etkisi yok:** kriter 0-E (≥10) ve 0-F (≥20) resmî AHN4 tabanına ve
kendi kaartblad ölçümümüze dayanıyordu; ikisi de PASS. Bu bulgu eşiği
değiştirmez, **gerekçeyi** düzeltir.

---

## 3. "AHN5 kapsaması yetersiz" iddiası — bizim verimizde SINANDI

3DBAG'in eski sürüm kullandığı binalarda `b3_nodata_fractie_ahn5`:

| 3DBAG kaynağı | n | AHN5 nodata payı (medyan) |
|---|---|---|
| ahn5 | 6.999 | 0,000 |
| ahn4 | 116 | 0,104 |
| **ahn3** | 261 | **0,696** |

Yani 3DBAG, `ahn3` kullandığı binalarda ayakizinin **%69,6'sında AHN5 verisi
olmadığını** söylüyor.

**Bu, bizim kendi ölçümümüzle çelişiyor:** B alanında sıfır dönüşlü hücre oranı
yalnızca **%0,09**. Çelişki varsayımla kapatılmadı, **doğrudan sınandı**.

### Sınama: bu binaların ayakizi içinde BİZİM AHN5'imiz ne veriyor?

BAG'de ayakizi bulunan **349** bina için ölçüldü (aynı `within` kuralı,
M-007 yön testi geçti):

| 3DBAG kaynağı | n | Bizim AHN5 yoğunluğumuz (medyan) | p10 | Hiç noktası olmayan |
|---|---|---|---|---|
| ahn3 | 240 | **29,93 p/m²** | 18,02 | **0 bina** |
| ahn4 | 109 | **25,11 p/m²** | 16,75 | **0 bina** |
| Toplam | 349 | 27,63 p/m² | — | **0 bina** |

(A alanındaki normal binaların medyanı 38,22 p/m².)

### Sonuç — bu bir KARŞILAŞTIRMA sınırlaması, GİRDİ sınırlaması değil

Bizim AHN5 verimiz bu 349 binanın **tamamını** iyi kapsıyor; hiçbirinde boşluk
yok. Dolayısıyla 3DBAG'in `INSUFFICIENT_COVERAGE` gerekçesi **kendi AHN5 anlık
görüntüsüne** aittir — 3DBAG v2023.10.08 Ekim 2023'te yayınlandı ve o tarihte
AHN5 ülke genelinde hâlâ uçuluyordu.

**D-013'ün güncellenmesi gerekiyor:** 377 binalık ayrıştırma kuralı korunur,
ama gerekçesi değişir:

| | Eski çerçeve | Ölçülmüş çerçeve |
|---|---|---|
| Sorun kimde | belirsiz | **3DBAG'in girdisinde** |
| Bizim girdimiz | belirsiz | **sağlam** (0 boşluk) |
| Kriter 1-B'de anlamı | "girdi farkı" | **"referansın kendisi eski"** |

Yani bu binalarda 1-B'de çıkacak fark, **bizim rekonstrüksiyonumuzun hatası
değil, 3DBAG modelinin 2014/2020 verisine dayanmasıdır.** Ayrıştırma bu yüzden
*daha da* gereklidir.

---

## 4. Yan bulgular

**4.1 — `collection_version` alanı yanlış etiketliydi.**
`data/raw/3dbag/3dbag_metadata.json` ve `DATA_LOG.md` sürümü **"2.0"** olarak
kaydetmişti. Bu değer **CityJSON şema sürümüdür**, dataset sürümü değil.
Gerçek dataset sürümü API'den doğrulandı: **`v2023.10.08`**
(`/collections/pand` → `version.collection`). Düzeltildi.

> Bu, M-010 ek bulgusuyla **aynı aile**: alan adının söylediği ile içindeki
> değer farklıydı. Fark şu ki bu sefer sürüm etiketi bir **provenans**
> kaydıydı — yanlış kalsaydı hangi 3DBAG sürümüyle karşılaştırdığımız
> belgelenmemiş olurdu.

**4.2 — 3DBAG API'sinde daha yeni sürüm YOK.**
`https://api.3dbag.nl/collections/pand` bugün (2026-09-21) hâlâ
**`v2023.10.08`** döndürüyor. Yani daha güncel bir 3DBAG sürümüne geçme
seçeneği **mevcut değil**; bu, P-014'ün (uçuş sonrası binalar için yükseklik
kaynağı) bir kapısını kapatır.

**4.3 — 3DBAG'de olup BAG'imizde olmayan 28 bina.**
3DBAG 377 bina için eski AHN kullanmış, ama bunların yalnızca **349**'u
güncel BAG indirmemizde var. Kalan **28** bina 3DBAG'in 2023 BAG anlık
görüntüsünde vardı, 2026 BAG'inde yok — muhtemelen **yıkılmış**. Bu, D-020'nin
**ters yönüdür**: uçuş sonrası yapılanlar kadar, uçuştan sonra **yıkılanlar**
da vardır. Aşama 1'de 3DBAG karşılaştırması yapılırken bu 28 bina eşleşmeyecek
ve **"eksik" sayılmamalıdır**.

---

## 5. Kriter 1-B için bağlayıcı sonuç

1. RMSE ve bias **`b3_pw_bron`'a göre ayrıştırılarak** raporlanır: `ahn5`
   tabanlı 6.999 bina ana metrik; `ahn3`/`ahn4` tabanlı 377 bina **ayrı
   satır** (D-013, `docs/validation_protocol.md` §1.1b).
2. Ayrıştırmanın gerekçesi **güncellendi**: fark bizim girdimizden değil,
   **3DBAG'in eski girdisinden** kaynaklanıyor (bkz. §3).
3. `b3_kwaliteitsindicator = False` olan **98** bina da ayrı işaretlenir.
4. 3DBAG'de olup BAG'de olmayan **28** bina eşleşme dışıdır, kayıp sayılmaz.
