# DATA_LOG.md — Veri provenance kaydi

> AGENTS.md Bolum 8: "DATA_LOG.md **insan tarafindan okunan** kayittir, makine logu
> oraya karismaz." Makine loglari `data/logs/*.log` altindadir.
>
> Bolum 12.7: her harici veri icin asagidaki alanlarin **tamami** doldurulur.
> **Ham veri hicbir sekilde degistirilmez.**

**Durum: BOS (Asama 0.1).** Ilk kayitlar Asama 0.3'te indirme scriptleri tarafindan
eklenecek. Her indirme scripti kendi kaydini yazar (`download_bag.py`,
`download_ahn.py`, `download_3dbag.py`).

---

## Kayit sablonu (Bolum 12.7 — her alan zorunlu)

```
## <veri-seti-adi>  ·  <indirme-tarihi UTC>
- kaynak_url:            
- saglayici:             
- veri_seti_adi:         
- surum:                 
- veri_uretim_tarihi:    
- yayin_tarihi:          
- indirme_tarihi_utc:    
- indirme_yontemi:       # script adi + API endpoint
- sorgu_parametreleri:   # bounding box / filtre / kaartblad no
- crs:                   # okunan CRS — VARSAYILMAZ, dosyadan okunur
- zaman_referansi:       # UTC / yerel / yok  (bkz. config/units.yml)
- lisans:                
- attribution_sarti:     
- sha256:                
- dosya_boyutu_bytes:    
- run_id:                
- uygulanan_islemler:    # donusum/kirpma gecmisi — ham dosyaya DEGIL, tureve uygulanir
```

---

## Kayitlar

## 3DBAG LOD2 — SABITLENMIS SURUM v2025.09.03  ·  2026-09-22T18:53:09Z

| Alan | Deger |
|---|---|
| dosya | `data/raw/3dbag_v20250903/metadata.json` |
| kaynak_url | https://data.3dbag.nl/v20250903/tiles/... |
| saglayici | TU Delft 3D geoinformation |
| surum | v2025.09.03 (URL yolunda sabit; metadata.json edition ve oznitelik parmak izi TUTARLI) |
| veri_uretim_tarihi | TODO_DOLDURULACAK |
| yayin_tarihi | TODO_DOLDURULACAK |
| indirme_tarihi_utc | 2026-09-22T18:53:09Z |
| indirme_yontemi | WFS GetFeature (OGC Filter Encoding 2.0) |
| sorgu_parametreleri | tile_index.fgb bbox=83323.9,444466.0,85102.5,446843.6 (EPSG:28992) = B + 50 m; 30 fayans |
| crs | EPSG:7415 |
| zaman_referansi | metadata.json: BAG 2.0 Extract ve AHN kaynak tarihleri yayin meta verisinde |
| lisans | CC BY 4.0 (AGENTS.md Bolum 7) - attribution ZORUNLU |
| attribution_sarti | TODO_0.3: 3DBAG resmi attribution metni kaynagindan alinacak |
| sha256 | `ba4ca7e323a009c98f290ea0447c9de31753c8bf1b4d1e7634891648ac76b0e7` |
| dosya_boyutu_bytes | 6313 |
| run_id | RUN-2026-09-22-007 |
| uygulanan_islemler | yok (ham indirme, .city.json.gz olarak saklandi) |

30 fayans, 40283 Building nesnesi, 40283 benzersiz pand. Her dosyanin SHA-256'si fayans indeksindeki `cj_sha256` ile DOGRULANDI (checksum yayincidan gelir, bizim uretmedigimiz bagimsiz bir degerdir). b3_pw_bron: {'ahn5': 38003, 'ahn4': 936, 'ahn3': 1344}. Oznitelik parmak izi: ['2025.09.03'].

---
## 3DBAG LOD2 (CityJSONFeature)  ·  2026-09-21T14:59:55Z

| Alan | Deger |
|---|---|
| dosya | `data/raw/3dbag/3dbag_pand.city.jsonl` |
| kaynak_url | https://api.3dbag.nl/collections/pand/items |
| saglayici | TU Delft 3D geoinformation |
| surum | **BELIRSIZ** (duzeltildi 2026-09-22). Ham metadata `collection_version: 2.0` = CityJSON SEMA surumu, dataset surumu degil. API `/collections/pand` etiketi `v2023.10.08` der, ama oznitelik parmak izi yalnizca **2025.09.03** ile tutarli (2024.12.16'da eklenen 5 oznitelik VAR, 2025.09.03'te kaldirilan `b3_succes` YOK). Etiket icerikle CELISIYOR. 2026-09-21'deki 'v2023.10.08, dogrulandi' notu YANLISTI: yalnizca API'nin kendi beyani okunmustu (MISTAKES.md M-013) |
| veri_uretim_tarihi | TODO_DOLDURULACAK |
| yayin_tarihi | TODO_DOLDURULACAK |
| indirme_tarihi_utc | 2026-09-21T14:59:55Z |
| indirme_yontemi | WFS GetFeature (OGC Filter Encoding 2.0) |
| sorgu_parametreleri | bbox=83323.9,444466.0,85102.5,446843.6 (EPSG:28992) = B + 50 m; sayfalama limit=1000 |
| crs | EPSG:7415 |
| zaman_referansi | b3_pw_datum dagilimi: {'2023': 6999, '2020': 116, '2014': 261} |
| lisans | CC BY 4.0 (AGENTS.md Bolum 7) - attribution ZORUNLU |
| attribution_sarti | TODO: 3DBAG resmi attribution metni kaynagindan alinacak |
| sha256 | `48055908c04de127bd49ce88e4a9937a7fef7476b60840e9b369a272a3c61457` |
| dosya_boyutu_bytes | 43246008 |
| run_id | RUN-2026-09-21-014 |
| uygulanan_islemler | yok (ham indirme) |

7376 CityJSONFeature, 7376 benzersiz pand. numberMatched=14754 CityObject sayar (Building + BuildingPart), pand DEGIL. NOKTA BULUTU KAYNAGI (b3_pw_bron): {'ahn5': 6999, 'ahn4': 116, 'ahn3': 261}. Yil (b3_pw_datum): {'2023': 6999, '2020': 116, '2014': 261}. Bizim girdimiz AHN5'tir (D-013); AHN5 payi %94.9. OZNITELIKLER (62): b3_bag_bag_overlap, b3_bouwlagen, b3_dak_type, b3_extrusie, b3_h_dak_50p, b3_h_dak_70p, b3_h_dak_max, b3_h_dak_min, b3_h_maaiveld, b3_h_nok, b3_is_glas_dak, b3_kas_warenhuis, b3_kwaliteitsindicator, b3_mutatie_ahn3_ahn4, b3_mutatie_ahn4_ahn5, b3_n_nok, b3_n_vlakken, b3_nodata_fractie_ahn3, b3_nodata_fractie_ahn4, b3_nodata_fractie_ahn5, b3_nodata_radius_ahn3, b3_nodata_radius_ahn4, b3_nodata_radius_ahn5, b3_opp_buitenmuur, b3_opp_dak_plat, b3_opp_dak_schuin, b3_opp_grond, b3_opp_scheidingsmuur, b3_puntdichtheid_ahn3, b3_puntdichtheid_ahn4, b3_puntdichtheid_ahn5, b3_pw_bron, b3_pw_datum, b3_pw_onvoldoende, b3_pw_selectie_reden, b3_rmse_lod12, b3_rmse_lod13, b3_rmse_lod22, b3_t_run, b3_val3dity_lod12, b3_val3dity_lod13, b3_val3dity_lod22, b3_volume_lod12, b3_volume_lod13, b3_volume_lod22, begingeldigheid, documentdatum, documentnummer, eindgeldigheid, eindregistratie, fid, geconstateerd, identificatie, oorspronkelijkbouwjaar, status, tijdstipeindregistratielv, tijdstipinactief, tijdstipinactieflv, tijdstipnietbaglv, tijdstipregistratie, tijdstipregistratielv, voorkomenidentificatie

---
## AHN5 LAZ nokta bulutu (GeoTiles alt-fayanslari)  ·  2026-09-21T14:53:49Z

| Alan | Deger |
|---|---|
| dosya | `data/raw/ahn/AHN5_T/37EN1_14.LAZ` |
| kaynak_url | https://geotiles.citg.tudelft.nl/AHN5_T |
| saglayici | AHN (Rijkswaterstaat/provincies/waterschappen) - fayanslama: TU Delft GeoTiles |
| surum | AHN5, kampanya etiketi '2023_C' (dosya adindan) |
| veri_uretim_tarihi | 2023 kampanyasi (etiket) / 2022-12-13 (LAS basligi) |
| yayin_tarihi | TODO_DOLDURULACAK |
| indirme_tarihi_utc | 2026-09-21T14:53:49Z |
| indirme_yontemi | WFS GetFeature (OGC Filter Encoding 2.0) |
| sorgu_parametreleri | B bbox + 50 m (D-010); secilen alt-fayanslar: 37EN1_14, 37EN1_19, 37EN1_24, 37EN1_15, 37EN1_20, 37EN1_25, 37EN2_11, 37EN2_16, 37EN2_21 |
| crs | EPSG:7415 |
| zaman_referansi | CELISKI: dosya adi kampanyasi '2023_C' ama LAS basligi 'file creation day/year 347/2022' (13 Aralik 2022). Ikisi de kaydedildi; sessizce tek deger SECILMEDI (AGENTS.md Bolum 4 tutumu). |
| lisans | TODO: AHN lisans kosulu ahn.nl'den dogrulanacak |
| attribution_sarti | TODO |
| sha256 | `184a4c766f35642c1561681cac5ae63dc16c21420a1277d5c2047e2f7861594e` |
| dosya_boyutu_bytes | 307816585 |
| run_id | RUN-2026-09-21-012 |
| uygulanan_islemler | yok (ham indirme). Alt-fayanslar 20 m ortusme tasir (GeoTiles tasarimi). |

9 alt-fayans, toplam 420007378 nokta, 3.12 GB. Kapsama B+50 m icin DOGRULANDI. Her dosyanin boyutu indirme sonrasi Content-Length ile karsilastirildi. CRS dosya ici WKT'den okundu: EPSG:7415 (RD New + NAP). KAYNAK NOTU: PDOK ATOM AHN4 RASTER sunar, LAZ sunmaz; AHN5 LAZ icin GeoTiles kullanildi.

---
## ON KOSUL OLCUMU — disk alani  ·  2026-09-21

Asama 0.3 indirmelerinin on kosulu (P-003). Tahmin degil, `shutil.disk_usage`
ile **olculmustur**.

| Alan | Deger |
|---|---|
| surucu | `C:` |
| toplam | 452,9 GB |
| kullanilan | 325,4 GB |
| **bos** | **127,5 GB** |
| hedef | >= 80 GB |
| sonuc | **SAGLANDI** |
| onceki olcum | 31,6 GB (P-003 acilisinda) |
| kazanilan | 95,9 GB |

Not: Asama 0.3'te her indirme oncesi beklenen boyut `Content-Length` veya
`resultType=hits` ile olculecek ve bos alanla karsilastirilacaktir (M-004
kural 3). Disk doluysa indirme yarida kesilir ve bozuk dosya olusur.

---


## AOI — B — baglam/tampon  ·  2026-09-21T12:08:36Z

| Alan | Deger |
|---|---|
| dosya | `aoi/area_B_context.geojson` |
| kaynak_url | turetilmis (CBS Wijken en Buurten 2025'ten) |
| saglayici | Voorhof Digital Twin / Karar D-009 |
| surum | D-009 |
| veri_uretim_tarihi | TODO_DOLDURULACAK |
| yayin_tarihi | TODO_DOLDURULACAK |
| indirme_tarihi_utc | 2026-09-21T12:08:36Z |
| indirme_yontemi | WFS GetFeature (OGC Filter Encoding 2.0) |
| sorgu_parametreleri | A.buffer(300) |
| crs | EPSG:28992 |
| zaman_referansi | yok (idari sinir, CBS 2025) |
| lisans | TODO_0.3: CBS kaynak lisansindan turer |
| attribution_sarti | TODO_0.3 |
| sha256 | `23a13eca32f47a8542a8d063780ecc213e141a83fd9fb3cf8a7227ce14c624a0` |
| dosya_boyutu_bytes | 8620 |
| run_id | RUN-2026-09-21-011 |
| uygulanan_islemler | unary_union + buffer(300 m) |

A + 300 m tampon, programatik uretildi. Sanayi buurt'larinin 17.14 ha'i (100%) B icinde ve modelde KALIYOR (golge/CFD girdisi). B raporlanmaz.

---
## AOI — A — analiz alani  ·  2026-09-21T12:08:36Z

| Alan | Deger |
|---|---|
| dosya | `aoi/area_A_analysis.geojson` |
| kaynak_url | turetilmis (CBS Wijken en Buurten 2025'ten) |
| saglayici | Voorhof Digital Twin / Karar D-009 |
| surum | D-009 |
| veri_uretim_tarihi | TODO_DOLDURULACAK |
| yayin_tarihi | TODO_DOLDURULACAK |
| indirme_tarihi_utc | 2026-09-21T12:08:36Z |
| indirme_yontemi | WFS GetFeature (OGC Filter Encoding 2.0) |
| sorgu_parametreleri | buurtcode in ['BU05032400', 'BU05032401', 'BU05032403', 'BU05032404', 'BU05032405', 'BU05032406', 'BU05032407'] |
| crs | EPSG:28992 |
| zaman_referansi | yok (idari sinir, CBS 2025) |
| lisans | TODO_0.3: CBS kaynak lisansindan turer |
| attribution_sarti | TODO_0.3 |
| sha256 | `f501b26fa4632784e35a5820c3a05e6f8da8bf4786360a3feff76dd1e774599b` |
| dosya_boyutu_bytes | 6330 |
| run_id | RUN-2026-09-21-011 |
| uygulanan_islemler | unary_union |

7 resmi konut buurt'unun birlesimi: BU05032400, BU05032401, BU05032403, BU05032404, BU05032405, BU05032406, BU05032407. Dislanan 2 sanayi buurt'u: BU05032402, BU05032408. A ∩ sanayi = 0.0000 ha. Tek parca, gecerli geometri. CBS kara alani 107 ha, geometrik alan 109.62 ha (fark su yuzeyi).

---
## BAG — bag:verblijfsobject  ·  2026-09-21T10:08:17Z

| Alan | Deger |
|---|---|
| dosya | `data/raw/bag/bag_verblijfsobject.geojson` |
| kaynak_url | https://service.pdok.nl/lv/bag/wfs/v2_0 |
| saglayici | Kadaster / PDOK |
| surum | WFS v2_0 (surum etiketi servis tarafinda yok) |
| veri_uretim_tarihi | TODO_DOLDURULACAK |
| yayin_tarihi | TODO_DOLDURULACAK |
| indirme_tarihi_utc | 2026-09-21T10:08:17Z |
| indirme_yontemi | WFS GetFeature (OGC Filter Encoding 2.0) |
| sorgu_parametreleri | bbox=83373.7,444516.0,85086.3,446943.9 (EPSG:28992) = Voorhof bbox + 300 m tampon; sayfalama count=1000 |
| crs | EPSG:28992 |
| zaman_referansi | yok (BAG durum verisi; indirme anindaki gecerli kayit) |
| lisans | TODO_0.3: PDOK/Kadaster lisans kosulu kaynagindan dogrulanacak |
| attribution_sarti | TODO_0.3 |
| sha256 | `a9987407b49d74d027a4aaa84ada52d507928cef58802c9e485d13ceb19a4182` |
| dosya_boyutu_bytes | 13185218 |
| run_id | RUN-2026-09-21-004 |
| uygulanan_islemler | yok (ham indirme, degistirilmedi) |

Ozellik sayisi: 19346. bbox ciktidan dogrulandi (M-004 kural 2). Ham dosya degistirilmedi. OZNITELIKLER (14): bouwjaar, gebruiksdoel, huisletter, huisnummer, identificatie, openbare_ruimte, oppervlakte, pandidentificatie, pandstatus, postcode, rdf_seealso, status, toevoeging, woonplaats. STATUS DAGILIMI: Verblijfsobject in gebruik: 18644 · Verblijfsobject gevormd: 668 · Verbouwing verblijfsobject: 34. Status filtresi config/acceptance_criteria.yml -> stage_0_2.status_filter altinda tanimlidir (Karar D-008); degerler bu dagilimdan dogrulanmistir (M-005).

---
## BAG — bag:pand  ·  2026-09-21T10:07:46Z

| Alan | Deger |
|---|---|
| dosya | `data/raw/bag/bag_pand.geojson` |
| kaynak_url | https://service.pdok.nl/lv/bag/wfs/v2_0 |
| saglayici | Kadaster / PDOK |
| surum | WFS v2_0 (surum etiketi servis tarafinda yok) |
| veri_uretim_tarihi | TODO_DOLDURULACAK |
| yayin_tarihi | TODO_DOLDURULACAK |
| indirme_tarihi_utc | 2026-09-21T10:07:46Z |
| indirme_yontemi | WFS GetFeature (OGC Filter Encoding 2.0) |
| sorgu_parametreleri | bbox=83373.7,444516.0,85086.3,446943.9 (EPSG:28992) = Voorhof bbox + 300 m tampon; sayfalama count=1000 |
| crs | EPSG:28992 |
| zaman_referansi | yok (BAG durum verisi; indirme anindaki gecerli kayit) |
| lisans | TODO_0.3: PDOK/Kadaster lisans kosulu kaynagindan dogrulanacak |
| attribution_sarti | TODO_0.3 |
| sha256 | `c934461cd06459d3a6b9a34359cf9445fbcc413d323a6332c364b3252ef079c1` |
| dosya_boyutu_bytes | 5151041 |
| run_id | RUN-2026-09-21-004 |
| uygulanan_islemler | yok (ham indirme, degistirilmedi) |

Ozellik sayisi: 7704. bbox ciktidan dogrulandi (M-004 kural 2). Ham dosya degistirilmedi.

**KAYNAK VERI TUTARSIZLIGI (olculdu 2026-09-22):** VBO `0503010000032819` (kantoorfunctie) `pandidentificatie = 0503100000001130` der, ama bu pand indirmede yok. Sunucu `hits = 7704`, indirilen 7704 — **indirme eksiksiz**. Pand tek-kayit FES sorgusuyla PDOK'tan cekildi: status `Pand in gebruik`, bouwjaar 1972; geometrisi indirme dikdortgeninin tamamen **batisinda** (en dogu x = 83.371,0 < dikdortgen baslangici 83.373,7). VBO noktasi **kendi pand'inin 14,6 m disinda** — BAG'in kendi icinde bir tutarsizlik. Konum B'nin 121,2 m disinda; A/B analizini **etkilemez**. `report_uncertain_geometry.py` artik yetim VBO'yu B icindeyse WARNING, disindaysa uzakligiyla INFO olarak loglar. OZNITELIKLER (8): aantal_verblijfsobjecten, bouwjaar, gebruiksdoel, identificatie, oppervlakte_max, oppervlakte_min, rdf_seealso, status. STATUS DAGILIMI: Pand in gebruik: 7576 · Verbouwing pand: 77 · Bouwvergunning verleend: 31 · Bouw gestart: 15 · Pand in gebruik (niet ingemeten): 4 · Sloopvergunning verleend: 1. Status filtresi config/acceptance_criteria.yml -> stage_0_2.status_filter altinda tanimlidir (Karar D-008); degerler bu dagilimdan dogrulanmistir (M-005).

---
## CBS Wijken en Buurten 2025 — wijkenbuurten:buurten  ·  2026-09-21T08:58:27Z

| Alan | Deger |
|---|---|
| dosya | `data/raw/cbs/voorhof_buurten.geojson` |
| kaynak_url | https://service.pdok.nl/cbs/wijkenbuurten/2025/wfs/v1_0 |
| saglayici | CBS / PDOK |
| surum | 2025 |
| veri_uretim_tarihi | TODO_DOLDURULACAK |
| yayin_tarihi | TODO_DOLDURULACAK |
| indirme_tarihi_utc | 2026-09-21T08:58:27Z |
| indirme_yontemi | WFS GetFeature (OGC Filter Encoding 2.0) |
| sorgu_parametreleri | bbox + buurtcode on eki BU050324 |
| crs | EPSG:28992 |
| zaman_referansi | yok (yillik idari sinir) |
| lisans | TODO_0.3: PDOK lisans kosulu kaynagindan dogrulanacak |
| attribution_sarti | TODO_0.3 |
| sha256 | `972383b7da84c6e7699c49c2731da9a7cf4522e4836c03749b678d458449fb97` |
| dosya_boyutu_bytes | 31765 |
| run_id | RUN-2026-09-21-002 |
| uygulanan_islemler | yok (ham indirme, degistirilmedi) |

Resmi ad 'Wijk 24 Voorhof' — 'Voorhof' ile tam esleme sorgusu 0 dondurur (M-004). Sorgu wijkcode uzerinden yapildi. Filtre ciktidan dogrulandi. Ham dosya degistirilmedi.

---
## CBS Wijken en Buurten 2025 — wijkenbuurten:wijken  ·  2026-09-21T08:58:27Z

| Alan | Deger |
|---|---|
| dosya | `data/raw/cbs/voorhof_wijk.geojson` |
| kaynak_url | https://service.pdok.nl/cbs/wijkenbuurten/2025/wfs/v1_0 |
| saglayici | CBS / PDOK |
| surum | 2025 |
| veri_uretim_tarihi | TODO_DOLDURULACAK |
| yayin_tarihi | TODO_DOLDURULACAK |
| indirme_tarihi_utc | 2026-09-21T08:58:27Z |
| indirme_yontemi | WFS GetFeature (OGC Filter Encoding 2.0) |
| sorgu_parametreleri | filter: wijkcode=WK050324 |
| crs | EPSG:28992 |
| zaman_referansi | yok (yillik idari sinir) |
| lisans | TODO_0.3: PDOK lisans kosulu kaynagindan dogrulanacak |
| attribution_sarti | TODO_0.3 |
| sha256 | `9adbda8872bf60cadecb96d8bdc6bc47d66b71b1d148abb9361bac8089c720d5` |
| dosya_boyutu_bytes | 6863 |
| run_id | RUN-2026-09-21-002 |
| uygulanan_islemler | yok (ham indirme, degistirilmedi) |

Resmi ad 'Wijk 24 Voorhof' — 'Voorhof' ile tam esleme sorgusu 0 dondurur (M-004). Sorgu wijkcode uzerinden yapildi. Filtre ciktidan dogrulandi. Ham dosya degistirilmedi.

---

---

## Kontrol kurallari

Asagidakiler Asama 0'in kabul kriterleridir (`config/acceptance_criteria.yml` →
`stage_0`) ve `verify_data.py` (Asama 0.4) tarafindan otomatik denetlenir:

| Kriter | Kural |
|---|---|
| 0-A | Her katmanin CRS'i okundu ve beklenenle **eslesti** (uyusmazsa exception) |
| 0-B | A alanindaki bina sayisi BAG'den sayildi ve loglandi |
| 0-C | Eksik veya bozuk dosya yok |
| 0-D | Her indirmenin SHA-256 checksum'i kayitli |

**Bina sayisi notu:** AGENTS.md Bolum 3 A alani icin ~400-700 bina bekliyor. Bu bir
**esik degil, akil saglamasidir**. Sayim bu araligin disinda cikarsa AOI siniri veya
BAG filtresi sorgulanir — sayi araliga uydurulmaz.

**Zaman referansi notu (Bolum 12.1):** Kaynaklarin zaman referanslari birbirinden
farklidir ve `config/units.yml` → `time.source_time_reference` altinda tanimlidir.
Ozellikle: KNMI saatlik veri UTC'dir ve saatleri **1-24** araligindadir (0-23 degil);
EPW yerel standart saattir ve **DST icermez**; Stedin PC6 yillik agregattir, saatlik
kiyasa uygun **degildir**.
