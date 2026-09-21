# PENDING_DECISIONS.md — Kullanici onayi bekleyenler

> AGENTS.md Bolum 13.4: ajan karar gerektiren her seyi buraya yazar. Kullanici
> dondugunde tek dosyaya bakip hepsini cevaplayabilmelidir.
>
> Format: `[TARIH] [ASAMA] Soru / Secenekler / Ajanin onerisi ve gerekcesi /
> Bu karar verilmeden ilerlenemeyen isler`

| ID | Asama | Konu | Engelledigi is | Aciliyet |
|---|---|---|---|---|
| P-001 | 4 | B ve D alan boyutlari | Asama 4 (CFD, mikroklima) | Asama 3 sonunda |
| P-002 | 4 | ENVI-met lisansi | Asama 4 mikroklima | Asama 3 sonunda |
| P-003 | 0.3 | Disk alani yetersizligi riski | Asama 0.3 indirmeleri | **YUKSEK — hemen** |
| P-004 | 1 | AHN z-fark esigi (Kriter 1-C) | Asama 1 baslangici | Asama 0 sonunda |
| P-005 | 3 | NMBE / CV(RMSE) esikleri (3-B, 3-C) | Asama 3 baslangici | Asama 2 sonunda |

---

## [2026-09-21] [0.3] P-003 — Disk alani yetersiz olabilir

**Soru:** Ham veri nereye indirilecek? Sistem diskinde yalnizca **31,6 GB** bos alan var
(toplam 452,9 GB, olculdu 2026-09-21).

**Neden onemli:** Asama 0.3'te AHN5 LAZ kaartblad'lari, BAG GPKG ve 3DBAG CityJSON
indirilecek. AHN5 nokta bulutu Randstad'da >=20 nokta/m2 yogunlukla ulkedeki en yogun
sinifta (AGENTS.md Bolum 2) — LAZ kaartblad dosyalari buyuk. Asama 4'te OpenFOAM
mesh ve cozum ciktilari da GB mertebesinde birikir.

**Dosya boyutlari henuz OLCULMEDI** — indirme oncesi HTTP `Content-Length` ile
olculecek ve `DATA_LOG.md`'ye yazilacak. Tahmini rakam yazilmiyor (Bolum 1, kural 1).

**Secenekler:**
- **A —** Harici disk / ikinci surucu baglanir, `config/paths.yml` icindeki
  `data.raw` oraya yonlendirilir. *(Ajanin onerisi)*
- **B —** Sistem diskinde yer acilir (>=100 GB hedef) ve mevcut yapida devam edilir.
- **C —** Asama 0.3 once yalnizca A alanini kapsayan minimum veriyle calistirilir,
  B alani ve Asama 4 verisi sonra indirilir.

**Ajanin onerisi ve gerekcesi:** A. `paths.yml` zaten tum yollari tek noktadan
yonetiyor, hedef degistirmek tek satir. Disk dolarsa indirme yarida kesilir ve bozuk
dosya olusur; bozuk dosya checksum kontrolunden gecmez ama zaman kaybettirir.

**Bu karar verilmeden ilerlenemeyen isler:** Asama 0.3'un tamami.

**Not:** Asama 0.1-0.2 bu karardan etkilenmez, devam edilebilir.

---

## [2026-09-21] [4] P-001 — B ve D alan boyutlari

**Soru:** B (baglam/tampon) ve D (CFD domeni) alanlari hangi boyutta sabitlenecek?

**Olculen donanim (2026-09-21, bu makine):**

| Bilesen | Deger |
|---|---|
| CPU | Intel Core i5-12450H — 8 fiziksel / 12 mantiksal cekirdek |
| RAM | 15,7 GB |
| GPU | NVIDIA RTX 3050 Laptop (4 GB VRAM) + Intel UHD (tumlesik) |
| Disk (C:) | 452,9 GB toplam / 31,6 GB bos |
| OS | Windows 11 Home Single Language 10.0.26200 |

**Ajanin onerisi: BU KARAR SIMDI VERILMEMELI.** Gerekcesi:

1. **D domeni hesaplanamaz.** AGENTS.md Bolum 3'e gore D, en yuksek binanin
   yuksekligi H'ye bagli: girişte 5H, cikista 15H, yanlar/ust 5H (COST 732 / AIJ).
   **H henuz bilinmiyor** — Voorhof'un en yuksek binasi ancak Asama 0.3'te BAG/3DBAG
   indirildikten sonra olculecek. H olcmeden D boyutu yazmak sayi uydurmak olur.

2. **RAM butcesi olculmeli, tahmin edilmemeli.** 15,7 GB, kentsel CFD icin dar bir
   butce. Kac milyon hucreye kadar cikabilecegi bu makinede bir bellek testiyle
   olculmelidir; literaturden alinan genel bir "hucre basina bellek" katsayisi bu
   makinede dogrulanmadan kullanilmaz.

3. **GPU CFD'yi hizlandirmaz.** OpenFOAM varsayilan olarak CPU tabanlidir; 4 GB VRAM
   burada belirleyici degil. Belirleyici olan RAM ve 8 fiziksel cekirdek.

**Onerilen yol:** Bu karar Asama 3 sonuna ertelenir. O noktada H olculmus,
bina sayisi kesinlesmis ve bir bellek testi yapilmis olur; boyutlar olculen veriyle
sabitlenir. AGENTS.md Bolum 3 zaten "Asama 0-3 donanimdan bagimsiz ilerler" diyor.

**Bu karar verilmeden ilerlenemeyen isler:** Asama 4 (CFD + ENVI-met). Asama 0-3
etkilenmez.

**Not:** C alani (~150 x 150 m) ENVI-met LITE'in 50x50x25 grid siniriyla zaten
sabitlenmis durumda; ayrica karar gerektirmiyor.

---

## [2026-09-21] [4] P-002 — ENVI-met lisansi

**Soru:** ENVI-met icin ogrenci lisansina mi basvurulacak, yoksa LITE limitiyle mi
devam edilecek? (AGENTS.md Bolum 11-2)

**Secenekler:**
- **A —** LITE ile devam. 50x50x25 grid siniri; C alani buna gore zaten boyutlandirildi.
- **B —** Ogrenci lisansi basvurusu. Daha buyuk grid, ama basvuru suresi belirsiz.

**Ajanin onerisi:** A, bir uyariyla. AGENTS.md Bolum 7 ENVI-met LITE'in
**acik kaynak OLMADIGINI** ve CC BY-NC-SA (ticari olmayan kullanim) oldugunu
belirtiyor; ayrica **lisans sisteminin 2026'da degistigini** ve kullanimdan once
guncel kosullarin kontrol edilmesi gerektigini soyluyor.

**Kritik bagimlilik:** Bolum 7 ayrica "bir bilesenin lisansi web arayuzunun yayinini
engelliyorsa YAYIN ASAMASINA GECILMEZ" diyor. ENVI-met ciktisinin Asama 5'te
yayinlanip yayinlanamayacagi lisans kosullarina bagli. Bu, Asama 4'e baslamadan
once netlesmeli — aksi halde uretilen sonuc yayinlanamaz.

**Bu karar verilmeden ilerlenemeyen isler:** Asama 4 mikroklima modulu; dolayli
olarak Asama 5'te mikroklima katmaninin yayini.

---

## [2026-09-21] [1] P-004 — AHN z-fark esigi (Kriter 1-C)

**Soru:** `config/acceptance_criteria.yml` kriter 1-C'deki `ahn_z_diff_rmse_m` esigi
hangi sayi olacak? (Karar D-003 geregi `TODO_ONAY_BEKLIYOR`)

**Cozulmesi gereken celiski (AGENTS.md Bolum 4):** Resmi AHN kwaliteitsbeschrijving
duseyde sistematik <=5 cm ve stokastik sigma <=5 cm veriyor; AHN5 ihale belgesi
sigma <=3 cm diyor. AGENTS.md bu celiskinin "raporda acikca not dusulecegini,
sessizce tek deger secilmeyecegini" soyluyor.

**Ajanin onerisi:** Asama 0 sonunda, indirilen AHN5 metaverisi ve gercek nokta
yogunlugu olculdukten sonra karar verilir. O noktada hangi belgenin bu kaartblad
icin gecerli oldugu somut olarak gorulur. Simdi sayi secmek, iki celiskili kaynaktan
birini gerekcesiz tercih etmek olur.

**Bu karar verilmeden ilerlenemeyen isler:** Asama 1 kapanisi (kriter 1-C olculemez).

---

## [2026-09-21] [3] P-005 — NMBE ve CV(RMSE) esikleri (Kriter 3-B, 3-C)

**Soru:** PC6 duzeyinde enerji karsilastirmasi icin NMBE ve CV(RMSE) kabul esikleri
hangi sayilar olacak? (Karar D-003 geregi `TODO_ONAY_BEKLIYOR`)

**Durum:** AGENTS.md Bolum 9 referans olarak ASHRAE Guideline 14'u gosteriyor ama
sayisal esik vermiyor. Ajan bu sayilari kendi basina yazamaz (Bolum 12.11).

**Ajanin onerisi:** Asama 2 sonunda karara baglanir. Onaylanirken:
- Esigin alindigi kaynak (belge adi, surum, sayfa/tablo) `DECISIONS.md`'ye yazilir.
- Aylik mi saatlik mi kalibrasyon yapildigi belirtilir — ASHRAE G14 bu ikisi icin
  farkli esikler tanimlar ve hangisinin gecerli oldugu veri cozunurluguyle belirlenir.
- **Stedin PC6 verisi yillik agregat** (`config/units.yml` → `Stedin_PC6.tz: null`).
  Saatlik kalibrasyon esigi bu veriye UYGULANAMAZ. Esik secimi bu kisiti dikkate
  almalidir.

**Bu karar verilmeden ilerlenemeyen isler:** Asama 3 kapanisi (cekirdek cikti).
