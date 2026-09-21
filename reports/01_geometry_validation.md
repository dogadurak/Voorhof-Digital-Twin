# 01 — Geometri dogrulama raporu

**Durum: BOS ISKELET.** Bu rapor **Asama 1**'de uretilecektir.

AGENTS.md Bolum 6, Asama 1 kabul kriterleri bu dosyada **tablo halinde** raporlanir:

| Kriter | Metrik | Esik | Olculen | Sonuc |
|---|---|---|---|---|
| 1-A | val3dity gecerlilik | >= %97 | `TODO` | `TODO` |
| 1-B | 3DBAG cati yuksekligi RMSE (+ **bias**) | <= 0,25 m | `TODO` | `TODO` |
| 1-C | AHN z-fark (bagimsiz) | `TODO_ONAY_BEKLIYOR` | `TODO` | `TODO` |
| 1-D | Basarisiz rekonstruksiyon | <= %2 | `TODO` | `TODO` |

**Zorunlu notlar (yazilirken silinmeyecek):**
- 1-B bir **tutarlilik kontrolu**dur, bagimsiz dogrulama degildir (Bolum 5, 12.10).
- 1-B icin **bias RMSE ile birlikte** raporlanir; yalniz RMSE yasak
  (`acceptance_criteria.yml` → `global_rules.bias_with_rmse`).
- 1-C esigi onaylanmadan bu rapor kapatilamaz (Karar D-003, P-004).
