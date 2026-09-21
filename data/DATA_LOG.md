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

## BAG — bag:verblijfsobject  ·  2026-09-21T08:59:05Z

| Alan | Deger |
|---|---|
| dosya | `data/raw/bag/bag_verblijfsobject.geojson` |
| kaynak_url | https://service.pdok.nl/lv/bag/wfs/v2_0 |
| saglayici | Kadaster / PDOK |
| surum | WFS v2_0 (surum etiketi servis tarafinda yok) |
| veri_uretim_tarihi | TODO_DOLDURULACAK |
| yayin_tarihi | TODO_DOLDURULACAK |
| indirme_tarihi_utc | 2026-09-21T08:59:05Z |
| indirme_yontemi | WFS GetFeature (OGC Filter Encoding 2.0) |
| sorgu_parametreleri | bbox=83373.7,444516.0,85086.3,446943.9 (EPSG:28992) = Voorhof bbox + 300 m tampon; sayfalama count=1000 |
| crs | EPSG:28992 |
| zaman_referansi | yok (BAG durum verisi; indirme anindaki gecerli kayit) |
| lisans | TODO_0.3: PDOK/Kadaster lisans kosulu kaynagindan dogrulanacak |
| attribution_sarti | TODO_0.3 |
| sha256 | `a9987407b49d74d027a4aaa84ada52d507928cef58802c9e485d13ceb19a4182` |
| dosya_boyutu_bytes | 13185218 |
| run_id | RUN-2026-09-21-003 |
| uygulanan_islemler | yok (ham indirme, degistirilmedi) |

Ozellik sayisi: 19346. bbox ciktidan dogrulandi (M-004 kural 2). Ham dosya degistirilmedi. NOT: gebruiksdoel yalnizca verblijfsobject katmanindadir; woonfunctie orani pand->verblijfsobject join'i ile hesaplanir.

---
## BAG — bag:pand  ·  2026-09-21T08:58:42Z

| Alan | Deger |
|---|---|
| dosya | `data/raw/bag/bag_pand.geojson` |
| kaynak_url | https://service.pdok.nl/lv/bag/wfs/v2_0 |
| saglayici | Kadaster / PDOK |
| surum | WFS v2_0 (surum etiketi servis tarafinda yok) |
| veri_uretim_tarihi | TODO_DOLDURULACAK |
| yayin_tarihi | TODO_DOLDURULACAK |
| indirme_tarihi_utc | 2026-09-21T08:58:42Z |
| indirme_yontemi | WFS GetFeature (OGC Filter Encoding 2.0) |
| sorgu_parametreleri | bbox=83373.7,444516.0,85086.3,446943.9 (EPSG:28992) = Voorhof bbox + 300 m tampon; sayfalama count=1000 |
| crs | EPSG:28992 |
| zaman_referansi | yok (BAG durum verisi; indirme anindaki gecerli kayit) |
| lisans | TODO_0.3: PDOK/Kadaster lisans kosulu kaynagindan dogrulanacak |
| attribution_sarti | TODO_0.3 |
| sha256 | `c934461cd06459d3a6b9a34359cf9445fbcc413d323a6332c364b3252ef079c1` |
| dosya_boyutu_bytes | 5151041 |
| run_id | RUN-2026-09-21-003 |
| uygulanan_islemler | yok (ham indirme, degistirilmedi) |

Ozellik sayisi: 7704. bbox ciktidan dogrulandi (M-004 kural 2). Ham dosya degistirilmedi. NOT: gebruiksdoel yalnizca verblijfsobject katmanindadir; woonfunctie orani pand->verblijfsobject join'i ile hesaplanir.

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
