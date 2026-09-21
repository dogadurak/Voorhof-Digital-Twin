# DECISIONS.md — Metodolojik kararlar

> AGENTS.md Bolum 12.11: asagidakiler kullanici onayi olmadan degistirilemez —
> yeni veri kaynagi, yeni AOI, CRS stratejisi, kabul esigi veya metrik, dogrulama
> metodolojisi, lisans kosulu, ucretli/ogrenci-lisansli yazilim, temel model
> varsayimi, cekirdek cikti tanimi, yuksek hesaplama kaynagi gerektiren calistirma.
>
> **Her onaylanan degisiklik buraya tarih ve gerekceyle yazilir.**

| ID | Tarih | Konu | Durum |
|---|---|---|---|
| D-001 | 2026-09-21 | Python ortami: conda-forge | ONAYLANDI |
| D-002 | 2026-09-21 | Asama 0.4 kapsami | ONAYLANDI |
| D-003 | 2026-09-21 | Sayisi verilmemis esikler | ONAYLANDI |
| D-004 | 2026-09-21 | Depo adi | ONAYLANDI |
| D-005 | 2026-09-21 | Asama 0 raporu elle yazilir | ONAYLANDI |
| D-006 | 2026-09-21 | Indirmeler B alani bbox'i ile sinirlanir | ONAYLANDI |

---

## D-001 · [2026-09-21] · Python ortami conda-forge ile kurulur

**Karar:** Asil ortam dosyasi `environment.yml` (kanal: conda-forge, ortam adi
`voorhof-twin`). `requirements.txt` yalnizca conda-forge'da bulunmayan pip paketleri
icin tamamlayici olarak tutulur.

**Gerekce:** GDAL, rasterio, fiona, laspy ve PDAL Windows'ta pip ile kaynaktan
derleme gerektiriyor ve derleyici zinciri olmadan kurulum kiriliyor. conda-forge
bu paketleri hazir binary olarak sunuyor. Makinede conda 26.1.0 zaten kurulu.

**Etkiledigi asamalar:** 0.3 (indirme scriptleri), 0.4 (dogrulama), 1+ (geometri).

**Alternatif ve neden secilmedi:** Saf pip/venv daha tasinabilir olurdu ancak
Windows'ta geospatial yigin kurulumu yuksek olasilikla basarisiz olur. Tam Docker
yaklasimi maksimum tekrarlanabilirlik verirdi ama QGIS masaustu entegrasyonunu
(Asama 3, UMEP/SOLWEIG) zorlastirir; Asama 1'de zaten Docker kullanilacak.

**Onay:** Kullanici, 2026-09-21.

---

## D-002 · [2026-09-21] · Asama 0.4 yalnizca `verify_data.py` kapsar

**Karar:** Asama 0.4 = `src/00_acquisition/verify_data.py`. AGENTS.md Bolum 13.6'da
sayilan dort oz-olcum scripti (`spot_check.py`, `check_thresholds.py`,
`check_compliance.py`, `make_stage_report.py`) **Asama 0.5** olarak ayrilir.

**Gerekce:** AGENTS.md Bolum 13.6 bu scriptlerin "Asama 0.4'te yazilacagini" soyluyor,
kullanicinin asama plani ise 0.4'u `verify_data.py` olarak tanimliyor. Ikisi ayni is
degil. Bes scripti tek adimda yazmak Bolum 14.6'daki "kapsam kaymasi" hata sinifina
girer ve tek oturumda kontrol edilemez. Tek gorev, tek cikti ilkesi korundu.

**Etkiledigi asamalar:** 0.4, 0.5 (yeni), 1 (baslangic on kosulu).

**Sonucu:** Asama 0.5 tamamlanmadan Asama 1'e gecilmez, cunku Bolum 13.1'deki Asama
Sonu Raporunu ureten `make_stage_report.py` 0.5'te yazilir.

**Onay:** Kullanici, 2026-09-21.

---

## D-003 · [2026-09-21] · Sayisi verilmemis esikler TODO_ONAY_BEKLIYOR kalir

**Karar:** AGENTS.md'nin sayisal deger vermedigi kabul esikleri
`config/acceptance_criteria.yml` icinde `TODO_ONAY_BEKLIYOR` olarak birakilir.
Ilgili asama baslamadan once kullanici kaynak gostererek onaylar.

**Etkilenen kriterler:**

| Kriter | Metrik | Ne zaman gerekli |
|---|---|---|
| 1-C | `ahn_z_diff_rmse_m` | Asama 1 baslangici |
| 3-B | `nmbe_pct` | Asama 3 baslangici |
| 3-C | `cv_rmse_pct` | Asama 3 baslangici |

**Gerekce:** Iki kural carpisiyordu. Bolum 12.2 esiklerin sonuctan once
kilitlenmesini istiyor; Bolum 12.11 esik belirlemeyi kullanici onayina bagliyor ve
Bolum 1 kural 1 sayi uydurmayi yasakliyor. Cozum: esik slotu simdi acilir ve
kilitlenir, sayisi ilgili asama baslamadan once onayla doldurulur. Boylece ne sayi
uydurulmus olur ne de esik sonuc gorulduikten sonra belirlenir.

**Onemli not (Kriter 1-C):** AGENTS.md Bolum 4 bir celiski iceriyor — resmi AHN
kwaliteitsbeschrijving duseyde stokastik sigma <=5 cm verirken AHN5 ihale belgesi
sigma <=3 cm diyor. Bu celiski raporda acikca not dusulecek, sessizce tek deger
secilmeyecek. Esik bu celiski cozulmeden sayisallastirilmaz.

**Uygulama:** `src/common/config.py` icindeki `get_threshold()`, onaylanmamis bir
esik okunmaya calisildiginda `PendingThresholdError` firlatir. Onaysiz esikle
PASS/FAIL beyan etmek teknik olarak engellenmistir.

**Onay:** Kullanici, 2026-09-21.

---

## D-004 · [2026-09-21] · Depo adi `Voorhof-Digital-Twin`

**Karar:** Proje/depo adi `Voorhof-Digital-Twin`
(https://github.com/dogadurak/Voorhof-Digital-Twin).

**Gerekce:** AGENTS.md Bolum 8'deki `delft-twin` bir placeholder'di ve Bolum 11-3
acik karar olarak isaretlenmisti. Kullanici depoyu bu adla olusturdu.

**Sonucu:** AGENTS.md Bolum 8 agaci ve Bolum 11-3 guncellendi; Bolum 11-3 KAPANDI.
Bolum 8 agacina ayrica, diger bolumlerin zaten zorunlu kildigi ama agacta eksik olan
ogeler islendi: `MISTAKES.md` (Bolum 14), `src/qa/` (Bolum 13.6), `src/common/`,
`reports/PENDING_DECISIONS.md` (Bolum 13.4), `environment.yml`, `requirements.txt`,
`.env.example`. Bu bir metodoloji degisikligi degil, belge ici tutarlilik duzeltmesidir.

**Onay:** Kullanici, 2026-09-21.

---

## D-005 · [2026-09-21] · Asama 0'in sonu raporu elle yazilir

**Karar:** Asama 0'in Bolum 13.1 formatindaki Asama Sonu Raporu elle yazilir.
Asama 0.5'ten sonraki tum raporlar `src/qa/make_stage_report.py` ile uretilir.

**Gerekce:** D-002 geregi rapor ureticisi 0.5'te yazilacak; 0.1-0.4 kendi raporlarini
uretecek araca sahip degil. Rapor formatinin kendisi degismez, yalnizca uretim yontemi
gecici olarak eldir.

**Risk ve nasil ele alindi:** Elle yazilan rapor, otomatik raporun yakaladigi eksik
alanlari kacirabilir. Bu yuzden Bolum 13.1 sablonunun her alani elle raporda da
eksiksiz doldurulur; bos birakilan alan FAIL sayilir.

**Onay:** Kullanici, 2026-09-21.

---

## D-006 · [2026-09-21] · Tum indirmeler B alani bbox'i ile sinirlanir

> **Numaralandirma notu:** Kullanici bu karari "D-004" olarak istemisti. D-004
> numarasi daha once depo adi karari icin kullanilmis ve AGENTS.md Bolum 11-3 ile
> commit 61e4677 mesajinda ona atif yapilmisti. Referanslari kirmamak icin bu karar
> **D-006** olarak kaydedildi. Icerik kullanicinin talimatiyla aynidir.

**Karar:** Hicbir veri kumesi ulke geneli olarak indirilmez. Her indirme, **B alani
(baglam/tampon) bounding box'i** ile sinirlanir.

| Veri | Sinirlama yontemi |
|---|---|
| **BAG** | PDOK **WFS bbox sorgusu**. Ulke geneli ATOM/full download KULLANILMAZ. |
| **AHN5** | Yalnizca B alanini kesen **alt-fayanslar (subtiles)**. Tam kaartblad gereksizse indirilmez. |
| **3DBAG** | Yalnizca ilgili **tile'lar** (tile indeksinden secim / `api.3dbag.nl`). |
| Diger (BGT, NWB) | Ayni ilke: bbox veya tile bazli secim. |

**Gerekce (uc katmanli):**

1. **Disk.** Sistem diskinde olculen bos alan 31,6 GB idi (2026-09-21). Kullanici
   en az 80 GB'a cikaracak, ancak bbox sinirlamasi **disk durumundan bagimsiz olarak
   gecerlidir** — yer acilmasi ulke geneli indirmeyi mesru kilmaz.
2. **Sure ve tekrarlanabilirlik.** Kucuk ve tanimli bir bbox, indirmeyi tekrarlanabilir
   kilar. Kullanilan bbox `data/DATA_LOG.md`'ye **sorgu parametresi** olarak yazilir
   (Bolum 12.7) ve boylece ucuncu bir kisi ayni veriyi yeniden cekebilir.
3. **Ham veri butunlugu.** Yarida kesilen buyuk indirme bozuk dosya uretir; bozuk dosya
   checksum kontrolunden gecmez ama zaman kaybettirir (Asama 0 kriteri 0-C).

**NEDEN A DEGIL DE B:** AGENTS.md Bolum 3 tampon katmanini zorunlu kiliyor —
"B katmani atlanamaz. Tamponsuz simulasyonda kenar binalar golgelenmemis gorunur ve
gunes potansiyeli **sistematik olarak yuksek** cikar." Indirme kapsamini A ile
sinirlamak bu hatayi veri ediniminde kalici hale getirirdi. Bu nedenle bbox'in
**alt siniri B'dir**, A degil.

**D domeni icin yeterli mi:** Evet. Bolum 3, D (CFD domeni) icin "Geometri B'den"
diyor; ayrica geometri indirilmesi gerekmez.

**Uygulama kurallari (Asama 0.3):**
- bbox degeri `aoi/area_B_context.geojson` dosyasindan **turetilir**, koda gomulmez
  (Bolum 8: yollar ve parametreler config'ten okunur).
- bbox CRS'i **EPSG:28992**'dir ve sorguya acikca yazilir (Bolum 1, kural 6).
- Fayans/tile secimi kacinilmaz olarak bbox'tan biraz genis olur (fayanslar ayriktir).
  Bu fazlalik atilmaz, ham haliyle saklanir — `data/raw/` degistirilmez (Bolum 12.7).
  Kirpma yapilacaksa ciktisi `data/interim/` altina yazilir.
- Secilen her fayans/tile kimligi `DATA_LOG.md`'ye yazilir.

**Dogrulama (Asama 0.4, `verify_data.py`):** Indirilen kapsamin B alanini **tamamen**
icerdigi kontrol edilir. Icermiyorsa bbox dar demektir ve Bolum 12.6 uygulanir —
eksik veriyle devam edilmez.

**Risk:** bbox hatali daraltilirsa kenar binalar eksik kalir ve golgeleme yine
sistematik olarak iyimser cikar. Bu, yonü bilinen bir hatadir; yukaridaki 0.4
kontrolu bunun icin vardir.

**Onay:** Kullanici, 2026-09-21.
