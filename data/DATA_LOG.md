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

*(Asama 0.3'e kadar bos)*

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
