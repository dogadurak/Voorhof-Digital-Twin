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
| ~~P-008~~ | 0.2 | ~~"Verbouwing pand" sayima girsin mi?~~ | — | **KAPANDI 2026-09-21** |
| P-009 | 3 | Sanayi buurt'lariyla bolunmus PC6'lar | Asama 3 enerji karsilastirmasi | Asama 2 sonunda |
| P-010 | 3 | CBS Kerncijfers buurt duzeyi tuketim (ikinci referans) | Yok (oneri) | Asama 3 oncesi |
| P-011 | 0.3 | C alani secimi (yukseklik esigi KAPANDI -> D-012) | C alani (Asama 4) | **0.3 sonrasi** |
| P-012 | 1 | Asama 1 rekonstruksiyonuna hangi AHN siniflari girecek | Asama 1 tamami | **GORSEL DOGRULAMAYI BEKLIYOR** (M-011) |
| ~~P-013~~ | 1 | AHN5'te karsiligi olmayan binalar (3 yapi) | — | **KAPANDI -> D-019** (secenek a) |
| ~~P-014~~ | 1 | Ucus sonrasi binalar icin yukseklik kaynagi | — | **KAPANDI -> D-025** (kalan sorular P-018, P-019) |
| P-015 | 5 | EPSG:28992 -> 4326 icin bagimsiz referans noktasi (M-003 sessiz varyanti) | Asama 5 WGS84 ciktisi | **Asama 5 oncesi** |
| ~~P-016~~ | 1 | Kriter 1-B icin 3DBAG referans surumu | — | **KAPANDI -> D-027** (v2025.09.03 sabitlendi) |
| ~~P-017~~ | 1 | "karar veremedim" durumu | — | **KAPANDI -> D-028** (ihtiyatli dislama) |
| ~~P-018~~ | 1 | Buyuk (>=100 m2) ucus sonrasi yapilar | — | **KAPANDI -> D-029** (estimated_lod1) |
| ~~P-019~~ | 1 | Kat yuksekligi degeri ve belirsizligi | — | **KAPANDI -> D-030** (yerel kalibrasyon + sayim kurali) |
| ~~P-020~~ | 1 | Kalibrasyon orneklemi | — | **KAPANDI -> D-031** (yukseklik sinifi; desil superseded) |

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

## [2026-09-21] [0.2] P-008 — "Verbouwing pand"  ·  **KAPANDI**

**Karar (kullanici, 2026-09-21):** `Verbouwing pand` (77) ve `Verbouwing
verblijfsobject` (34) sayima **DAHIL**. Ajanin uyguladigi okuma onaylandi.
Config `stage_0_2.status_filter` aynen kaliyor; degisiklik gerekmedi.

<details><summary>Acilis kaydi</summary>

**Durum: TEYIT BEKLIYORDU.** Ajan bir okuma secti ve uyguladi; adim 4'ten once
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

**Eger DISLANSIN denseydi:** config'te iki satir cikarilacakti; hesap yapilmamisti,
Bolum 12.2 ihlali olusmayacakti.

</details>

---

## [2026-09-21] [3] P-009 — Sanayi buurt'lariyla bolunmus PC6 kumeleri

**Baglam (Karar D-009):** A, Voorhof'un 7 konut buurt'udur; `BU05032402` ve
`BU05032408` dislandi. Bir PC6 kumesi bu sinirin iki tarafina bolunmus olabilir.

**Karar verilmis kisim (kullanici, 2026-09-21):** Sanayi buurt'lariyla kesisen
PC6'lar Asama 3 karsilastirmasindan **dislanir** ve **sayilari raporlanir**.
`docs/validation_protocol.md` Bolum 3.1b'ye islendi.

**Acik kalan:** Dislama oraninin kabul edilebilir ust siniri.

PC6 sinirlari henuz indirilmedi (Stedin verisi Asama 3'te gelecek), bu yuzden
kac PC6'nin bolundugu **HENUZ BILINMIYOR**. Tahmin yazilmiyor (Bolum 1 kural 1).

**Ajanin onerisi:** Asama 2 sonunda, PC6 sinirlari elde edildikten sonra olcum
yapilir ve esik o zaman kullanici onayiyla belirlenir. Dislama orani yuksek
cikarsa bu, karsilastirmanin gucunu dusuren bir **sinirlama** olarak raporlanir —
dislama kurali gevsetilmez (Bolum 12.2).

**Bu karar verilmeden ilerlenemeyen isler:** Asama 3 enerji karsilastirmasinin
kapsam beyani. Asama 0-2 etkilenmez.

---

## [2026-09-21] [3] P-010 — CBS Kerncijfers buurt duzeyi tuketim: ikinci enerji referansi?

**ONERI — VERI KAYNAGI OLARAK EKLENMEDI.** Kullanici acikca "simdilik veri
kaynagi olarak ekleme (Bolum 12.11), sadece Asama 3 oncesi degerlendirilmek uzere
oneri olarak dus" dedi. AGENTS.md Bolum 4 envanteri **degistirilmemistir**.

**Fikir:** A artik buurt sinirlariyla tam hizali oldugu icin, **CBS Kerncijfers
Wijken en Buurten**'deki buurt duzeyi ortalama gaz/elektrik tuketimi, Stedin PC6
agregatinin yaninda **ikinci bir bagimsiz enerji referansi** olabilir.

**Neden cekici:**
- A = 7 buurt'un birlesimi; buurt duzeyi veri A ile **birebir** ortusur,
  PC6'daki bolunme sorunu (P-009) burada YOKTUR.
- Stedin'den **farkli bir saglayici ve farkli bir agregasyon yontemi** — Bolum
  12.10 "mumkun oldugunda ikinci bir hesaplama yolu kullanilir" ilkesine uyar.

**Karar verilmeden once cevaplanmasi gerekenler:**
1. **Ayni fiziksel buyukluk mu?** (Bolum 12.4) Kerncijfers "ortalama tuketim"
   veriyor — hane basina mi, baglanti basina mi, konut basina mi? Model ciktisi
   bina duzeyinde toplam kWh/yil. Donusum gosterilemezse bu bir `validation`
   degil `contextual comparison` olur.
2. **Bagimsiz mi?** CBS bu rakamlari sebeke isletmecilerinden (Stedin dahil)
   aliyor olabilir. Oyleyse Stedin ile **ayni ham kaynaktan** turemis olur ve
   Bolum 12.10 geregi bagimsiz ground truth SAYILMAZ — "tutarlilik kontrolu"
   olarak etiketlenir. **Bu arastirilmadan kaynak eklenmemelidir.**
3. Gizlilik esikleri nedeniyle kac buurt'un degeri gizlenmis?
4. Referans yili model yiliyla ortusuyor mu? (Bolum 12.1 zaman uyumu)

**Ajanin onerisi:** Asama 2 sonunda arastirilir; 2. madde olumlu cikarsa
(gercekten bagimsiz) Bolum 12.11 kapsaminda yeni veri kaynagi olarak onaya
sunulur. Olumsuzsa ikincil tutarlilik kontrolu olarak kullanilabilir ama
"bagimsiz dogrulama" DENMEZ.

**Bu karar verilmeden ilerlenemeyen isler:** Yok. Mevcut plan (Stedin PC6)
degismeden ilerler; bu yalnizca bir guclendirme firsatidir.

---

## [2026-09-21] [0.3] P-011 — C alani secimi ve ENVI-met yukseklik esigi

**Durum: 0.3 SONRASI CALISTIRILACAK.** Kurallar muhurlendi
(`config/acceptance_criteria.yml` -> `stage_0_2_c`, `SEALED_NOT_EXECUTED`),
**aday hesabi calistirilmadi**. Karar D-011.

**Neden bekliyor:** ENVI-met LITE'in 25 dikey hucre siniri, secilecek karenin en
yuksek binasina ust sinir koyuyor. Yukseklik verisi (3DBAG `b3_h_dak_max`) Asama
0.3'te gelecek. Once secip sonra yukseklik kontrolu yapmak ikinci bir secim turu
gerektirebilirdi.

### ~~Onay bekleyen: yukseklik esigi~~ -> **KAPANDI 2026-09-21 (D-012)**

**Karar:** birincil **25 m** (dz <= 2 m), on-kayitli yedek **37,5 m** (dz <= 3 m).
Yedek tetikleyicileri T-A (sifir aday) ve T-B (baskin yukseklik sinifi hicbir
adayda temsil edilmiyor). "Temsil" kriteri hesaptan once tanimlandi ve
muhurlendi — bkz. `config/acceptance_criteria.yml` -> `stage_0_2_c_height`.

**Acik kalan tek sey: C aday hesabinin 0.3 sonrasi calistirilmasi.**

<details><summary>Acilis kaydi</summary>

#### Onay bekleyen: yukseklik esigi (kriter C-6)

ENVI-met belgelerinden **dogrulandi** (2026-09-21):

| Belgelenmis kural | Deger |
|---|---|
| LITE grid siniri | 50 x 50 x 25 hucre |
| Model tepesi | en yuksek binanin **en az 2 kati**, en az 30 m |
| Telescoping | ancak en yuksek bina yuksekliginden itibaren baslayabilir |

**Ajanin turettigi oneri** (sayi belgede yok, aritmetik ajana ait):

| Hedef dz | Model yuksekligi | Izin verilen H_max |
|---|---|---|
| <= 2 m | 50 m | **25 m (onerilen)** |
| <= 3 m | 75 m | 37,5 m |

**Secenekler:**
- **A — H_max <= 25 m** *(ajanin onerisi)*: dz <= 2 m, duzgun grid. En saglam;
  hicbir dogrulanmamis varsayim icermiyor.
- **B — H_max <= 37,5 m**: dz <= 3 m kabul edilir. Daha fazla aday, daha kaba
  dikey cozunurluk. ENVI-met'in yaya seviyesi analizinde 3 m kaba sayilabilir.
- **C — Telescoping ile daha yuksek sinir**: belgede telescoping'in izin verildigi
  yaziyor ama **buyume katsayisi dogrulanamadi**. Katsayi ENVI-met surumunden
  teyit edilmeden esik olarak onerilmez (M-005 kurali).

**Bilinen risk (her secenek icin):** Voorhof-Hoogbouw (`BU05032406`) yuksek
bloklar iceriyor. Dar bir esik A'nin bu bolumunu C adayi olmaktan cikarir. Bu
kabul edilebilir (C bir alt-alandir) ama yuksek bloklar tamamen dislanirsa C'nin
A'yi temsil etme iddiasi zayiflar ve **sinirlama olarak raporlanir**.

</details>

**Bu karar verilmeden ilerlenemeyen isler:** C aday hesabi ve dolayisiyla
Asama 4 mikroklima modulu. **Asama 0.3 ve Asama 1-3 etkilenmez.**


---

## [2026-09-21] [1] P-012 — Asama 1 rekonstruksiyonuna hangi AHN siniflari girecek?

**Durum:** ACIK · **Engelledigi is:** Asama 1 LOD2 rekonstruksiyonu

**Baglam:** Sinif kodlari `docs/ahn_class_codes.md`de belgeden dogrulandi
(D-017). Artik hangilerinin girdi olacagina karar verilebilir.

**Onerim (onay bekliyor):**

| Kod | Oneri | Gerekce |
|---|---|---|
| 6 | **DAHIL** | bina. DIKKAT: cepheler de 6'dir, cati ayrimi dikeylik olcutuyle yapilmali |
| 2 | **DAHIL**, yalniz zemin kotu referansi icin | bina yuksekligi maaiveld'e gore olculur |
| 1 | **HARIC**, ama izlenir | bitki ortusu + siniflandirilamayan her sey |
| 26 | **HARIC** | kunstwerk (kopru/vlonder) — bina degil |
| 9 | **HARIC** | su |
| 14 | **HARIC** | tel/bilinmeyen — her halukarda cati degil |

**Karar gerektiren asil nokta — sinif 1:**
Sinif 1 (64,9 milyon nokta, %38,8) hem bitki ortusunu hem de AHN'in
siniflandiramadigi **gercek bina parcalarini** icerir. D-016'da bulunan 67
binada ayakizi icindeki noktalarin **tamami** sinif 1'dir; bu yapilar sinif 1
dislanirsa **hic nokta gormez ve kesinlikle basarisiz olur**.

Iki secenek:
- **(a) Kati:** yalniz sinif 6. Temiz ama 67 yapiyi bastan kaybeder.
- **(b) Genis:** sinif 6 + ayakizi icindeki sinif 1, ek bir geometrik filtreyle
  (orn. yerel maaiveld'den >1,5 m yukseklik). Daha cok bina kurtarir ama
  agac noktasi sizma riski tasir.

Secim **Asama 1'in ilk adiminda, hesaptan once** muhurlenmelidir (Bolum 12.2).
Iki secenegi de calistirip iyi gorunen sonucu secmek **yasaktir**.

**Benim onerim:** (b), ama **her iki grup ayri raporlanarak** — sinif 6'dan
kurulan binalar ana metrigi olusturur, sinif 1 katkisiyla kurtarilanlar ayri
satirda verilir. Boylece secim sonuclara gore degil, bastan tanimlanmis olur.


---

## [2026-09-21] [1] P-013 — AHN5'te karsiligi olmayan binalar ne yapilacak?

**Durum:** ACIK · **Engelledigi is:** Asama 1 rekonstruksiyon filtresi,
Asama 3 enerji kapsami

**Baglam:** A'da 3 yapinin ayakizinde AHN5 (Subat 2023) verisinde bina
**yoktur** — ikisi okul (996 m2 ve 1.665 m2), biri 109 m2'lik alcak yapi.
Ayrinti: `reports/00_stage_0_3_zero_ratio_investigation.md`, D-018.

**Karar gereken uc nokta:**

**1 — Filtre nasil kurulacak?** `bouwjaar` **kullanilamaz** (kanit: D-018).
Onerim: `ground_class_ratio` ve `building_class_ratio` uzerinden, esik Asama 1
basinda hesaptan once muhurlenir. Iki esigi deneyip iyi gorunen sonucu secmek
**yasaktir** (Bolum 12.2).

**2 — Bu binalar modele girecek mi?** Secenekler:
- (a) Tamamen disla, sinirlama olarak raporla
- (b) 3DBAG/BAG yuksekliginden basit bir kutu (LOD1) uret, LOD2 iddia etme
- (c) Daha yeni bir yukseklik kaynagi ara (yeni bir veri kaynagi = Bolum 12.11
  geregi ayri kullanici onayi)

**Benim onerim: (a)**, cunku (b) olculmemis bir geometriyi olculmus gibi
gosterir ve `0503100000041285`'in ayakizi zaten `niet ingemeten`'dir.

**3 — Enerji analizine (Asama 3) etkisi:** ikisi de **okul**, yani konut disi.
A'nin enerji karsilastirmasi PC6 konut tuketimi uzerinden kuruldugu icin bu
yapilar muhtemelen zaten kapsam disidir — ama bu **acikca yazilmalidir**,
sessizce dusurulmemelidir (Bolum 12.8).

**Mutasyon tarihi gerekirse:** PDOK BAG WFS `documentdatum` dondurmuyor,
3DBAG donduruyor ama bu binalar 3DBAG'de yok. **BAG Individuele Bevragingen
API** ayri bir veri kaynagi olarak eklenmelidir — Bolum 12.11 geregi
kullanici karari.


---

## [2026-09-21] P-013 KAPANDI -> D-019

Kullanici secenek **(a)**'yi onayladi: 3 yapi Asama 1'den **dislanir**,
sinirlama olarak raporlanir, LOD1 kutu uretilmez.

**Onemli gerekce notu:** Bu karar gorsel dogrulamayi **beklemedi**, cunku
dogrudan olcume dayaniyor (nokta sinifi, dz dagilimi, cok donus orani) —
bir cikarima degil. Bolum 12.13 yalnizca **cikarim** temelli kararlari
bekletir. Bkz. D-019.

---

## [2026-09-21] [1] P-012 — GORSEL DOGRULAMA BEKLIYOR

> **YENI KANIT (2026-09-22, D-026):** 3DBAG'in AHN5'i "yetersiz" bulup AHN3'e
> dustugu 30 A binasinda noktalarin **~%93'u sinif 1'de** (bizim
> sinif 2+6 payimiz medyan 0,068). Yani sinif 6 disindaki noktalari
> dislemek, 64 kucuk yapinin yaninda **3DBAG'in de zorlandigi binalari**
> etkiler. Bu, P-012 secenek (b) lehine bir kanittir — gorsel dogrulama hala
> beklenir.

**Durum:** ACIK · **Bekledigi sey:** `docs/visual_check_zero_class6.md`

P-012 (Asama 1'e hangi AHN siniflari girecek) sorusunun kritik bileseni,
sinif 6 orani sifir cikan **64 kucuk yapinin gercekte ne oldugudur**. Sinif 1
dislanirsa bu yapilar **hic nokta gormez**.

Bu yapilarin "berging/depo" oldugu su an bir **CIKARIMDIR** (MISTAKES.md
M-011) ve yalnizca BAG ozniteliklerinden turetilmistir. Bolum 12.13 geregi
karardan once bagimsiz yoldan dogrulanmalidir.

**Dogrulama paketi hazir:**
- `aoi/qa/zero_class6_buildings.geojson` — 67 binanin tamami (EPSG:28992)
- `reports/visual_check_sample.csv` — 12 bina (2 okul + 10 rastgele kucuk),
  seed **28992**, config'te muhurlu
- `docs/visual_check_zero_class6.md` — kullanicinin dolduracagi sablon

**Iki okul orneklemde neden var:** guncel Luchtfoto'da (2025/2026) okul
binasi **goruluyorsa**, "ucustan sonra yapildi" aciklamasi bagimsiz olarak
dogrulanmis olur. Yani ayni orneklem hem alt grup A'nin cikarimini hem alt
grup B'nin olcumunu sinar.


---

## [2026-09-22] [1] P-014 — Ucus sonrasi binalar icin yukseklik kaynagi

**Durum:** ACIK — **ARASTIRMA YAPILDI, KARAR YOK** (kullanici talimati: "sadece
arastirma, karar yok"). Karar gorsel kontroller bittikten sonra.

> **Kayit notu (M-008 tekrari):** Bu kayit 2026-09-21'den beri AGENTS.md
> Bolum 5, D-019, D-021, D-022 ve D-023'te **atif yapilmasina ragmen hic
> acilmamisti.** 2026-09-22'de acildi. Bkz. MISTAKES.md M-008.

**Kapsam (olculdu, D-022):** 30 ucus sonrasi aday, 5.870 m2 (B'nin %0,98'i);
A'da 2 (ikisi de okul, 0 konut VBO), B\A'da 28 (92 konut VBO). Gorsel kontrol
S2/S3 derse A'daki 3 konut blogu (412 konut VBO) da bu kapsama girer.

**Lineage kurali (D-022, muhurlu):** `estimated_lod1` icin `height_source`,
`height_method`, `height_uncertainty_m` ZORUNLU; biri bos ise `footprint_only`.

### Arastirma sonuclari — her biri kaynagindan dogrulandi

| # | Kaynak | Durum (2026-09-22) | Kanit |
|---|---|---|---|
| 1 | **AHN6** (olculmus nokta bulutu) | **Delft icin YOK** | Yalnizca kuzeydogu yayinda (ucus 2025, yayin 13-10-2025). Voorhof, AHN6 2025 serit dis sinirlarinin **icinde degil — en yakin serit 66 km** (`AHN6_2025_omhullen_clip.gpkg`, 855 serit, olculdu). Voorhof AHN6 edinim **blogu 1**'de (`AHN6_percelen.gpkg`), ama dosyada yil yok. AHN sayfalari "2026 en 2027" verisinden soz ediyor; Delft icin **yil yazmiyor**. Dataroom'da 2026 serit dosyasi **yok** |
| 2 | **3DBAG** (daha yeni surum) | **Kaynak DEGIL** | Surum notlari: hicbir surum AHN6 kullanmaz; 2025.09.03 bilinen sorunu "BAG features without 3D model (typically due to a lack of elevation data) are missing from the output" (D-023) |
| 3 | **3DBAG `b3_bouwlagen`** (kat sayisi tahmini) | **Kaynak DEGIL** | Ucus sonrasi binalar 3DBAG ciktisinda yok |
| 4 | **BAG VBO `oppervlakte` toplami / ayakizi** -> kat sayisi -> yukseklik | **Uygulanabilir, TAHMIN** | Yeni veri kaynagi gerektirmez (BAG zaten Bolum 4'te). Varsayimlar: brut/net alan orani, kat yuksekligi. Konut disi yapilarda (okul) VBO alani kat sayisini iyi temsil etmeyebilir |
| 5 | **Street View / Luchtfoto** gorsel kat sayimi x kat yuksekligi | **Uygulanabilir, TAHMIN, ELLE** | Kullanicinin gorsel kontrol sirasinda toplayabilecegi bir alan. Kaynak: gozlem; `height_method = "gorsel kat sayimi x kat yuksekligi"` |
| 6 | **OSM `building:levels` / `height`** | **Arastirilmadi** | **Yeni veri kaynagi** (ODbL) — Bolum 12.11 geregi kullanici onayi olmadan sorgulanmadi |
| 7 | **AHN6'yi beklemek** | **Zaman belirsiz** | Delft ucusu yayinlanmis bir tarihe bagli degil |

**Kat yuksekligi** (secenek 4 ve 5 icin): bir norm veya olculmus referans
gerekir. **Bu arastirmada bir deger dogrulanmadi — varsayim yazilmadi.**
Karar verilirse kaynagi ayrica dogrulanacaktir (M-005, M-013).

### Karar icin sorular (kullaniciya)

1. `estimated_lod1` hic kullanilacak mi, yoksa tum ucus sonrasi binalar
   `footprint_only` mi kalacak? (Konut etkisi A'da **sifir** — iki okul;
   B\A'da 92 konut VBO, ama B raporlanmaz, yalnizca golge/ruzgar baglami.)
2. Kullanilacaksa: secenek 4 (BAG'den turetilmis) mi, 5 (gorsel) mi, ikisi
   capraz kontrol olarak mi?
3. AHN6 Delft'e geldiginde yeniden calistirma planlansin mi?

**Onerim YOK** (talimat geregi). Tek gozlem: A'da konut etkisi sifir oldugu
icin bu karar A'nin **dogrulama** sonuclarini etkilemez; yalnizca B'deki
golge/ruzgar **baglam** geometrisini etkiler.

---

## [2026-09-22] [5] P-015 — WGS84 donusumu icin bagimsiz referans noktasi

**Durum:** ACIK · **Engelledigi is:** Asama 5 (CesiumJS/3D Tiles WGS84 ciktisi)

M-003 tekrarinin ardindan eklenen `assert_proj_works()` oz-testi, PROJ
veritabaninin **yuklenmedigi** durumu ve **kaba** datum hatalarini yakalar.
**Metre mertebesindeki sessiz datum farkini YAKALAMAZ** (geri donus tutarli
kalir, Delft kutusu genistir).

**Soru:** Bu sessiz varyant icin bagimsiz bir referans noktasi (RD ve ETRS89/
WGS84 koordinatlari resmi olarak yayinlanmis bir nokta, orn. bir RD
kenmerk / NSGI referansi) test'e eklensin mi? Hangi kaynaktan?

Su an WGS84 ciktisi yalnizca gorsel kontrol icin `lat/lon` alanlarinda
(gezinme amacli); metre hatasi orada sonucu etkilemez.

---

## [2026-09-22] [1] P-016 — Kriter 1-B icin 3DBAG referans surumu

**Durum:** ACIK · **Engelledigi is:** Kriter 1-B (3DBAG ile cati yuksekligi RMSE)

**Baglam (D-023):** Indirdigimiz 3DBAG verisinin surumu BELIRSIZ: API etiketi
`v2023.10.08`, icerik parmak izi yalnizca **2025.09.03** ile tutarli. API
"experimental/beta"dir ve kendi surumunu yanlis etiketliyor olabilir. Indirme
sayfasi belirli surumleri sunuyor (2023.10.08'den itibaren).

**Secenekler:**
- (a) Mevcut API verisini kullan, surumu "belirsiz, parmak izi 2025.09.03"
  diye raporla
- (b) Indirme sayfasindan **acikca adlandirilmis** bir surumu (orn.
  2025.09.03) B bbox'i icin indir ve referansi ona sabitle — tekrarlanabilirlik
  icin en guclusu
- (c) Iki surumu da indir, kriter 1-B'yi ikisine karsi raporla

**Neden onemli:** Kriter 1-B bir **tutarlilik kontrolu**dur; referansin kimligi
belirsizse sonuc tekrarlanamaz (Bolum 8 "ayni girdiyle iki calistirma ayni
sonucu vermek zorundadir"). API ayrica yarin baska bir surum sunabilir.

**Onerim:** (b) — ama bu yeni bir indirme ve bir referans secimidir, Bolum
12.11 geregi kullanici karari. Ayrica 3DBAG'in 377 binada neden AHN5'i
yetersiz buldugu (D-021, geri cekilen aciklama) belki adlandirilmis surumun
metadata'sindan okunabilir.


---

## [2026-09-22] [1] P-017 — Gorsel kontrolde "karar veremedim" cikarsa ne olur?

**Durum:** ACIK · **Engelledigi is:** D-024'un 3 binaya uygulanmasi

D-024 S1/S2/S3'u tanimliyor. `docs/visual_check_a_residential.md`'de dorduncu
bir secenek var: **"karar veremedim"**. Kural bu durumda ne olacagini
soylemiyor. Ajan boslugu kendi karariyla doldurmadi (Bolum 12.11).

**Secenekler:**
- (a) **S2/S3 gibi davran** (ihtiyatli): dogrulamadan ve PC6 karsilastirmasindan
  dislanir, `estimated_lod1`. Hata payi: gercekte S1 olan bir binayi kaybeder.
- (b) **S1 gibi davran**: dahil edilir. Hata payi: yanlis geometri dogrulama
  istatistigine girer — Bolum 12.10 acisindan daha tehlikeli yon.
- (c) Bolum 12.13-4: karar "cikarima dayali" isaretlenir, **(a)** uygulanir ve
  Bolum 5'e sinirlama olarak yazilir.

**Onerim:** (c). Gerekce: belirsiz bir binayi dogrulama istatistigine sokmak,
dogrulamanin kendisini belirsizlestirir; disarida birakmak yalnizca kapsami
daraltir ve raporlanir.


---

## [2026-09-22] P-014 KAPANDI -> D-025

Kullanici karari: 3 konut blogu (S2/S3 ise) Street View kat sayisi x kat
yuksekligi; diger ucus sonrasi yapilar `footprint_only`; OSM kullanilmaz.
Uygulamada iki acik soru cikti -> P-018, P-019.

---

## [2026-09-22] [1] P-018 — Buyuk ucus sonrasi yapilar icin de tahmini yukseklik mi?

**Durum:** ACIK · **Gecici uygulama:** `footprint_only` (lineage varsayilani)

Talimat "diger ucus sonrasi **kucuk** yapilar footprint_only" idi. Olculdu:
30 adayin **6'si >= 100 m2** (4.580 m2, 74 konut VBO):

| bag_id | m2 | alan | bouwjaar | konut VBO | islev |
|---|---|---|---|---|---|
| `0503100000038250` | 2.111,9 | B | 2024 | 0 | onderwijsfunctie |
| `0503100000038184` | 996,5 | A | 2023 | 0 | onderwijsfunctie |
| `0503100000038253` | 496,1 | B | 2025 | 33 | woonfunctie |
| `0503100000038699` | 340,0 | B | 2026 | 18 | kantoorfunctie,woonfunctie |
| `0503100000038426` | 336,7 | B | 2026 | 15 | kantoorfunctie,woonfunctie |
| `0503100000040432` | 298,3 | B | 2026 | 8 | woonfunctie |

*(Tablo bu kaydi yazan yama scriptinde `reports/post_flight_buildings.csv` ve
BAG VBO katmanindan hesaplandi — elle aktarilmadi.)*

**Neden onemli:** `footprint_only` binalar 3B hacim olarak modele girmez ->
**B'deki golge geometrisinden duserler.** B'nin varlik nedeni kenar binalarin
golgelenmesidir (AGENTS.md Bolum 3). Etkisi, A'nin kenarindaki binalarin gunes
potansiyelinde **sistematik yukari sapma** olabilir.

**Secenekler:** (a) `footprint_only` kalsin, sinirlama olarak raporlansin ·
(b) ayni Street View yontemi bunlara da uygulansin · (c) yalnizca A'ya yakin
olanlara uygulansin (mesafe olculur).

**Onerim:** (b) veya (c) — Asama 3 gunes analizi B'deki golge hacimlerine
dayanir. Ama kullanicinin is yukunu arttirir; karar kullanicinin.

---

## [2026-09-22] [1] P-019 — Kat yuksekligi: hangi deger, hangi belirsizlik?

**Durum:** ACIK · **Kat sayimindan ONCE** cevaplanmali (yontemi belirler)

**Dogrulanan (D-025):** Bbl Art. 4.164 lid 4 / Tabel 4.162 -> yeni konut icin
doseme ustu serbest yukseklik **>= 2,6 m**. Bu bir **alt sinirdir**; kat-kat
arasi yuksekligi **vermez** (doseme kalinligi yok). Tipik bir deger veren resmi
bir kaynak **bulunamadi**. `b3_bouwlagen` dongusel oldugu icin reddedildi.

**Onerim — yerel kalibrasyon (olculmus, bagimsiz):**
Kullanici zaten Street View'da kat sayacak. Ayni oturumda, **olculmus AHN5
yuksekligi olan** ve benzer tipte (yakin tarihli, cok katli konut) **8-10
kontrol binasinin** katlarini da sayarsa:
`kat_yuksekligi = olculmus_cati_yuksekligi / sayilan_kat`
Dagilimin medyani deger, p10-p90 araligi `height_uncertainty_m`'nin kaynagi
olur. Kontrol binalari **sabit seed ile** secilir ve secim kurali **kat
sayimindan once** muhurlenir (Bolum 12.2, 12.13-3).

Bbl'nin 2,6 m alt siniri bir **tutarlilik kontrolu** olarak kullanilir:
kalibre edilen deger 2,6 m + makul bir doseme payinin altinda cikarsa bir sey
yanlistir.

**Alternatif:** tek bir literatur degeri — ama dogrulanmis bir kaynak
bulunmadan yazilmaz (M-005, M-013).


---

## [2026-09-22] P-016 KAPANDI -> D-027

`v2025.09.03` indirildi (30 fayans, 41 MB), yayincinin sha256
degerleriyle dogrulandi, kapsama API kumesine karsi sinandi (0 eksik).
API karsilastirmasi: 7,376 ortak binada **0 fark** —
API'nin etiketi yanlis, icerigi 2025.09.03.


---

## [2026-09-22] P-017, P-018, P-019 KAPANDI

| P | Karar | Nereye yazildi |
|---|---|---|
| P-017 | "Karar veremedim" = ihtiyatli dislama, S2/S3 gibi islenir, AYRI raporlanir | D-028 · `building_scenario_rule.scenarios.UNDECIDED` |
| P-018 | 6 buyuk ucus sonrasi yapi `estimated_lod1` (kat sayimi yapilir); 24 kucuk yapi `footprint_only` | D-029 · `building_lineage.assignment` |
| P-019 | Kat yuksekligi YEREL KALIBRASYON ile; 11 maddelik kat sayim kurali sayimdan ONCE muhurlendi | D-030 · `storey_counting_rule`, `storey_height_calibration` |

**Bunlarla birlikte acilan yeni sey yok.** P-012 halinde acik ve gorsel
kontrolu bekliyor; kullanici 2026-09-22'de "(b) yonunde egilimliyim ama karari
gorsel kontrolden sonra verecegim" dedi — bu bir karar DEGILDIR, kayit olarak
tutulur.


---

## [2026-09-22] [1] P-020 — Kalibrasyon orneklemi: desil mi, yukseklik sinifi mi

**Soru:** Kat yuksekligi kalibrasyonunda hangi 10 bina kullanilacak?

**Neden soruyorum:** Muhurledigim **desil** tabakalamasi kendi amacini
saglamadi (M-016). Uygun havuzun (514 bina) %66'si 5,7-6,0 m bandinda oldugu
icin desillerin 6'si ayni bandan bina secti. Kullanicinin talimati "farkli
kat sayisinda 10 bina" idi.

**Olculen havuz dagilimi** (h 1 m'ye yuvarlanmis -> bina sayisi):

| h | 3 m | 6 m | 8 m | 9 m | 11 m | 14 m | 26 m | 35 m | 37 m |
|---|---|---|---|---|---|---|---|---|---|
| bina | 3 | 337 | 97 | 46 | 5 | 4 | 9 | 3 | 10 |

**Secenekler:**

- **(a) ONERI — yukseklik sinifi.** h 1 m'ye yuvarlanarak siniflara bolunur,
  her siniftan sinif 6 orani en yuksek bina; 10. bina en kalabalik sinifin
  (6 m, 337 bina) ikinci en iyisi. Cikti:
  `reports/storey_height_calibration_proposal_p020.csv`.
  Secilen yukseklikler: 3,2 · 5,8 · 5,8 · 8,0 · 8,5 · 10,6 · 14,3 · 25,8 ·
  34,7 · 36,6 m. **Ajanin onerisi budur.**
- **(b)** Muhurlu desil kurali korunur. Secilen yukseklikler: 3,2 · 5,8 ·
  5,8 · 5,9 · 5,9 · 6,0 · 8,0 · 8,5 · 8,5 · 36,8 m.

**Gerekce (a) icin:** (b)'de dogrusal uyumun tum agirligi iki noktada
toplanir (6 m civari ve 36,8 m); aradaki 8-35 m bos kalir. Tek bir yuksek
bina, hem ortalamayi hem de ikincil tani uyumunu tek basina belirler
(leverage). (a) araligi dengeli kapsar.

**Gerekce (b) icin:** Kural muhurluydu ve sonuc gorulmeden yazilmisti;
korunmasi en muhafazakar davranistir. Bu durumda M-016 bir **sinirlama**
olarak raporlanir.

**Bu karar verilmeden ilerlenemeyen isler:** kat yuksekligi ortalamasinin ve
standart sapmasinin HESAPLANMASI. **Sayim devam edebilir** — saha listesi
iki orneklemin BIRLESIMINI (15 bina) iceriyor.

**Kritik zamanlama:** Karar, hesaptan ONCE verilmelidir. Iki orneklemi de
hesaplayip "hangisi daha iyi durdu" diye secmek, esigi sonuca gore secmenin
ta kendisidir (Bolum 12.2).


---

## [2026-09-22] P-020 KAPANDI -> D-031

**Karar:** yukseklik sinifi tabakalamasi. Muhurlu desil kurali
`SUPERSEDED_BY_P-020` olarak isaretlendi, **silinmedi**; ciktisi
`reports/storey_height_calibration_superseded_decile.csv` olarak duruyor.

**Ek:** kat yuksekliginin bina tipine gore degisip degismedigi de
raporlanacak. Karar kurali (grup tanimi, n >= 3 sarti, sd_pooled kriteri)
**sayimdan once** muhurlendi — D-031.

**Not:** Kullanicinin mesajindaki secenek harfleri ajanin yazdigiyla ters
dusuyordu (ajanda (a) = yukseklik sinifi onerisi). Gerekce metni niyeti
tereddutsuz gosterdigi icin ("yalnizca 2 katlilardan turetilmis bir kat
yuksekligi ... yanlis olur") yukseklik sinifi secenegi uygulandi ve bu fark
burada kayda gecirildi.
