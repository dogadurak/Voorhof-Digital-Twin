# PENDING_DECISIONS.md — Kullanici onayi bekleyenler

> AGENTS.md Bolum 13.4: ajan karar gerektiren her seyi buraya yazar. Kullanici
> dondugunde tek dosyaya bakip hepsini cevaplayabilmelidir.
>
> Format: `[TARIH] [ASAMA] Soru / Secenekler / Ajanin onerisi ve gerekcesi /
> Bu karar verilmeden ilerlenemeyen isler`

| ID | Asama | Konu | Engelledigi is | Aciliyet |
|---|---|---|---|---|
| P-001 | 4 | B ve D alan boyutlari | Asama 4 (CFD, mikroklima) | Asama 3 sonunda — **erteleme ONAYLANDI** |
| P-002 | 4 | ENVI-met lisansi | Asama 4 mikroklima | Asama 3 sonunda |
| ~~P-003~~ | 0.3 | ~~Disk alani yetersizligi~~ | — | **KAPANDI 2026-09-21** |
| P-004 | 1 | AHN z-fark esigi (Kriter 1-C) | Asama 1 baslangici | Asama 0 sonunda |
| P-005 | 3 | NMBE / CV(RMSE) esikleri (3-B, 3-C) | Asama 3 baslangici | Asama 2 sonunda |
| ~~P-006~~ | 0.2a | ~~woonfunctie ve bina sayimi paydalari~~ | — | **KAPANDI 2026-09-21 (D-008)** |
| P-007 | 2 | PDOK BAG WFS kismi — nevenadres yok | Asama 2 EP-Online eslestirmesi | Asama 1 sonunda |
| P-008 | 0.2a | "Verbouwing pand" sayima girsin mi? | Aday hesabi (teyit) | **Adim 4'ten once** |

---

## [2026-09-21] [0.3] P-003 — Disk alani  ·  **KAPANDI**

**Cozum (kullanici, 2026-09-21):** Sistem diskinde yer acilacak, hedef **en az 80 GB bos**.
Harici diske tasima gerekmiyor; `config/paths.yml` degismedi.

**Ek ve daha onemli karar:** Indirmeler disk durumundan **bagimsiz olarak** B alani
bbox'i ile sinirlanacak — bkz. `DECISIONS.md` → **D-006**. Yer acilmasi ulke geneli
indirmeyi mesru kilmaz.

**Asama 0.3 on kosulu:** Indirmeye baslamadan once bos alan fiilen olculur ve
>= 80 GB oldugu dogrulanir. Olculen deger `DATA_LOG.md`'ye yazilir.

<details>
<summary>Orijinal kayit</summary>

### P-003 (acilis kaydi) — Disk alani yetersiz olabilir

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

</details>

---

## [2026-09-21] [4] P-001 — B ve D alan boyutlari  ·  **ERTELEME ONAYLANDI**

**Kullanici karari (2026-09-21):** Bu kararin Asama 3 sonuna ertelenmesi onaylandi.
Gerekce asagida — ozetle: D domeni en yuksek bina H'ye bagli ve H henuz olculmedi.
Asama 0-3 donanimdan bagimsiz ilerler (AGENTS.md Bolum 3).

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

---

## [2026-09-21] [0.2a] P-006 — woonfunctie ve bina sayimi paydalari  ·  **KAPANDI**

**Karar (kullanici, 2026-09-21):** VBO duzeyi + tum panden + tam eslesme.
Ayrintilar `DECISIONS.md` -> **D-008**. Asagisi acilis kaydidir.

### P-006 (acilis kaydi)

**Durum: ADAY HESABINI BLOKLUYOR.** Karar verilmeden hesaplanamaz (Bolum 12.11:
metrik tanimi kullanici onayina baglidir). Bkz. MISTAKES.md M-005.

**Olculen gercek** (indirilen bbox geneli — kare bazinda hicbir hesap yapilmadi):

| Olcum | Deger |
|---|---|
| Toplam pand | 7.704 |
| Toplam verblijfsobject (VBO) | 19.346 |
| **aantal_verblijfsobjecten = 0 olan pand** | **3.124 (%40,6)** — garaj, trafo, depo, otopark |
| woonfunctie orani, **pand** duzeyi | **%50,5** |
| woonfunctie orani, **VBO** duzeyi | **%93,2** |
| bouwjaar 1960-1975, pand duzeyi | %22,2 |
| bouwjaar 1960-1975, VBO duzeyi | %48,5 |
| Coklu islevli VBO (virgullu) | 61 (%0,32) |
| VBO -> pand join eslesmesi | 19.345/19.346 (%100,0) |

### Soru 1 — woonfunctie orani hangi birim uzerinden? (kriter 0.2-B, esik >=%90)

- **A — VBO duzeyi** *(ajanin onerisi)*: karedeki panden'a bagli VBO'lardan
  woonfunctie olanlarin orani. Gerekce: bbox genelinde %93,2, yani **>=%90 esigi
  anlamli ve ayirt edici**. Ayrica gercek konut yogunlugunu yansitir — 200 daireli
  bir blok 1 pand ama 200 konuttur.
- **B — pand duzeyi**: karedeki panden'dan gebruiksdoel'u woonfunctie olanlarin orani.
  **UYARI: bbox genelinde %50,5.** Yardimci yapilar paydayi sisirdigi icin **>=%90
  esigi hicbir karede saglanamaz**; 0.2a sifir aday uretir.
- **C — yardimci yapilari dislayan pand duzeyi**: yalnizca aantal_verblijfsobjecten > 0
  olan panden uzerinden. Ara cozum; secilirse esik yeniden degerlendirilmeli.

### Soru 2 — bina sayimi hangi panden'i kapsiyor? (kriter 0.2-A, aralik 400-700)

- **A — TUM panden** *(ajanin onerisi)*: yardimci yapilar dahil. Indirilen alanda
  yogunluk 1.852 pand/km2; 600x600 m = 0,36 km2 -> **kare basina ~667 pand**, yani
  AGENTS.md Bolum 3'un verdigi **400-700 araligina dogal olarak oturuyor**. Bu, Bolum
  3'teki sayinin tum panden'i kastettigine dair gucli bir isarettir.
- **B — yalnizca konut birimi iceren panden**: yogunluk ~935/km2 -> kare basina ~337,
  **400 alt sinirinin altinda kalir**. Secilirse 400-700 araligi da yeniden
  degerlendirilmelidir.

### Soru 3 — coklu islevli VBO'lar nasil sayilsin?

61 kayit (%0,32) "woonfunctie,winkelfunctie" gibi virgullu deger tasiyor.

- **A — woonfunctie ICERIYORSA say** *(ajanin onerisi)*: %93,3
- **B — tam olarak woonfunctie ise say**: %93,2

Fark **0,09 puan**; sonucu degistirmez. Yine de kural yazilmali — yazilmazsa bir
sonraki oturum farkli davranir ve sonuc tekrarlanamaz olur.

### Ajanin toplu onerisi: 1-A + 2-A + 3-A

Bu kombinasyon hem AGENTS.md Bolum 3'un bina araligiyla hem Bolum 2'nin "%90+ konut"
ifadesiyle tutarli tek kombinasyondur.

**Bu, esigin sonuca gore ayarlanmasi DEGILDIR (Bolum 12.2 ihlali degil).** Esikler
(400-700 ve >=%90) degismiyor; **hangi buyuklugun olculdugu** tanimlaniyor. Tanim,
kare bazinda hicbir hesap yapilmadan yalnizca bbox geneli dagilimlara bakilarak
netlestirildi; aday skoru uretilmemistir.

### Bu karar verilmeden ilerlenemeyen isler

Asama 0.2a adim 4-5 (aday uretimi ve siralama). **Kullanicinin QGIS secimi bu karardan
bagimsizdir ve beklemez.**

---

## [2026-09-21] [2] P-007 — PDOK BAG WFS kismi: nevenadres yok

**Sorun (kullanici tespiti, 2026-09-21):** PDOK BAG WFS, BAG'in **kismi secimidir**.
Coklu adresli nesnelerde yalnizca **hoofdadres** sunulur; nevenadressen yoktur.

**Asama 0.2 etkisi:** Yok. Bina sayimi ve woonfunctie orani icin hoofdadres yeterli;
bir VBO'nun kac adresi oldugu bu metrikleri degistirmez.

**Asama 2 etkisi — ciddi olabilir.** Bolum 12.3 EP-Online eslestirmesini
`BAG pand -> verblijfsobject -> adresseerbaar object -> EP-Online label`
hiyerarsisine bagliyor ve "belirsiz veya coklu adresli vakalar AYRI RAPORLANIR,
sessizce bir secenek secilmez" diyor. Nevenadres eksikligi tam da bu vakalari
gorunmez kilabilir — yani kural ihlal edilmeden de eksik eslesme uretilebilir.

**Secenekler:**
- **A — Asama 2'den once tam BAG dagitimi ile karsilastir** *(ajanin onerisi)*:
  LVBAG extract / ATOM indirilir, WFS ile fark olculur ve raporlanir. Fark ihmal
  edilebilirse WFS ile devam edilir; degilse tam dagitima gecilir.
- **B — Bastan tam BAG dagitimina gec**: daha guvenli ama cok daha buyuk indirme
  (disk kisiti, D-006) ve 0.2a'da gereksiz.
- **C — WFS ile devam, sinirlamayi rapora yaz**: en hizli, ama Asama 2'nin kabul
  kriteri 2-C'yi ("coklu adresli vakalar ayri raporlandi") zayiflatir.

**Ajanin onerisi:** A. Sinirlama zaten AGENTS.md Bolum 5'e islendi; karar Asama 1
sonunda, Asama 2 baslamadan verilir.

**Bu karar verilmeden ilerlenemeyen isler:** Asama 2 EP-Online eslestirmesi.
Asama 0.2 ve 0.3 etkilenmez.

---

## [2026-09-21] [0.2a] P-008 — "Verbouwing pand" sayima girsin mi?

**Durum: TEYIT BEKLIYOR.** Ajan bir okuma secti ve uyguladi; adim 4'ten once
teyit edilmeli. Yanlissa config duzeltilir (hesap henuz yapilmadi).

**Ayrisma:** Talimatin **lafzi** sayima yalnizca "Pand in gebruik" ve
"Pand in gebruik (niet ingemeten)" girsin diyordu. Talimatin **amaci** ise fiilen
var olmayan yapilari dislamakti.

**Olculen:** `Verbouwing pand` = **77 kayit (%1,0)**. Bu binalar **fiziksel olarak
mevcuttur**, yalnizca tadilattadir.

**Ajanin uyguladigi okuma:** DAHIL. Gerekce: tadilattaki binanin catisi gunes ve
golge analizine girer; dislansaydi 77 gercek bina sayim disi kalirdi ve kare basina
~6-7 bina eksik sayilirdi. Ayni mantikla `Verbouwing verblijfsobject` (34 kayit)
de dahil edildi.

**Kesin olarak dislananlar** (henuz insa edilmemis): `Bouwvergunning verleend` (31),
`Bouw gestart` (15), `Sloopvergunning verleend` (1), `Verblijfsobject gevormd` (668).

**Ek bulgu:** Indirilen 7.704 pand icinde **yikilmis (gesloopt) durum kaydi YOKTUR** —
PDOK bu WFS'te onlari sunmuyor. Filtrenin fiili islevi yikilmislari elemek degil,
**henuz yapilmamislari** elemektir.

**Eger DISLANSIN dersen:** config'te `pand_include` ve `vbo_include` listelerinden
iki satir cikarilir; hesap henuz yapilmadigi icin Bolum 12.2 ihlali olusmaz.
