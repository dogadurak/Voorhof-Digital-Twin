# manual_steps.md — Elle yapilacak isler

> AGENTS.md Bolum 14.5: bir yontem ucuncu kez basarisiz olursa otomatiklestirilir
> **veya bu listeye tasinir**. "Uc kez basarisiz olan bir yontem korunmaz."
>
> Bolum 13.1: elle yapilan her adimin sonucu da olculur ve raporlanir. Elle yapilmis
> olmasi, olculmemis olmasinin gerekcesi degildir.

## Neden bazi adimlar elle yapilir

Her is otomatiklestirilmez. Bir adim su durumlarda elle kalir:
- Insan yargisi gerektirir (ornek: mahalle sinirinin nereden gecirilecegi)
- Arac yalnizca GUI sunar (ornek: ENVI-met LITE, QGIS bazi eklentileri)
- Otomasyonun maliyeti, tekrar sayisina degmez (bir kez yapilacak is)

---

## MS-001 · Alan sinirlarinin cizilmesi (Asama 0.2)

**Neden elle:** Voorhof'un merkezinin nereye konulacagi ve A alaninin hangi sokaklari
kapsayacagi kartografik bir yargidir. Otomatik centroid, mahalle dokusunu bilmez.

**Nasil yapilir:**
1. QGIS'te PDOK BAG WMS/WFS katmanini ac, CRS'i **EPSG:28992** (RD New) olarak ayarla.
2. Voorhof merkezini sec.
3. Merkezden **600 x 600 m** kare olustur → A alani.
4. A'ya **~300 m halka** ekleyerek yaklasik **1200 x 1200 m** kare olustur → B alani.
5. GeoJSON olarak kaydet:
   - `aoi/area_A_analysis.geojson`
   - `aoi/area_B_context.geojson`
6. Her iki dosyanin da CRS'inin EPSG:28992 oldugunu QGIS katman ozelliklerinden **dogrula**.

**Kabul:** Dosyalar mevcut, CRS EPSG:28992, A alani B alaninin icinde kalir,
A alanindaki bina sayisi (Asama 0.4'te olculecek) ~400-700 araliginda.

**C ve D alanlari:** Bu asamada cizilmez. C (~150 x 150 m) Asama 4'te, D (CFD domeni)
en yuksek bina yuksekligi H olculdukten sonra hesaplanir — bkz.
`reports/PENDING_DECISIONS.md` → P-001.

**D-006 nedeniyle ek onem:** B alani artik yalnizca simulasyon tamponu degil,
**indirme kapsamini da belirliyor** (bkz. `DECISIONS.md` → D-006). Asama 0.3'teki
BAG WFS sorgusu, AHN alt-fayans secimi ve 3DBAG tile secimi bu dosyanin bbox'indan
turetilecek. B dar cizilirse kenar binalar hic indirilmez ve golgeleme sistematik
olarak iyimser cikar — bu hata veri ediniminde kalici hale gelir.

Bu yuzden B cizilirken A'nin her yonunde **en az ~300 m** halka biraktigindan emin ol;
supheye dusersen genis tarafta kal. Fazla veri atilabilir, eksik veri sonradan fark
edilmez.

**Kim yapar:** Kullanici (ajan yapmaz).
**Durum:** BEKLIYOR

---

## Elle yapilacak kontroller (otomatiklestirilemeyenler)

### MS-1 · Orneklem kuralinin AMACI saglandi mi? (M-016)

**Ne zaman:** Bir `stratification` / `sampling` kurali her calistirildiginda.

**Neden elle:** Kuralin amaci bir METINDIR ("orneklem farkli yukseklikleri
kapsasin"). Script yayilimi (min, max, benzersiz deger sayisi) loglar ama
"amac saglandi mi" sorusuna karar veremez — o karar okumayi gerektirir.

**Adim:**
1. Scriptin logundaki yayilim satirini oku.
2. Kuralin config'teki amac cumlesini oku.
3. Yayilim amaci saglamiyorsa: **kurali DEGISTIRME.** Sonucu oldugu gibi
   birak, alternatifi AYRI dosyaya ONERI olarak yaz, PENDING'e soru ac ve
   karari hesaptan ONCE kullaniciya birak.

**Ornek (2026-09-22):** desil tabakalamasi "farkli yukseklikleri kapsar"
diyordu; 10 binanin 6'si ayni bandan cikti -> M-016, P-020.

---

## Tasinan adimlar (uc kez basarisiz olanlar)

*(Asama 0.1 itibariyle yok.)*
