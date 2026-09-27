# 3DBAG uyum artigi referansi — b3_rmse_lod22, A alani

> **Veri donemi:** geometri AHN5 2023-02-08/14 · oznitelik BAG 2026-09 (D-020).
> **Bu bizim sonucumuz DEGILDIR.** 3DBAG v2025.09.03'un yayimladigi, roofer'in hesapladigi bina basina RMSE (3B nokta-model uzakligi, tum AHN bina noktalari). Kriter 1-C-a esik ONERISININ referansidir (P-004, D-034). Bir referansin uyum artigidir; bagimsiz dogrulama degildir.

run_id: `RUN-2026-09-27-011` · git_commit: `efc9a6d-dirty` · calistirma (UTC): 2026-09-27T08:10:36Z

A alani 1259 bina · 3DBAG'de eslesen 1218 · kume (pw_bron=ahn5) 1174 · baska nokta bulutundan uretilmis (kume disi) 44 · rmse null 0.

| Katman (3DBAG b3_dak_type) | n | p10 | p25 | **medyan** | p75 | **p90** | p95 | max | RMS (agirliksiz) | <=0,10 m | <=0,25 m |
|---|---|---|---|---|---|---|---|---|---|---|---|
| TUMU (pw_bron=ahn5) | 1174 | 0.017 | 0.025 | **0.050** | 0.158 | **0.741** | 1.029 | 4.45 | 0.522 | 0.705 | 0.796 |
| horizontal | 748 | 0.015 | 0.020 | **0.031** | 0.055 | **0.090** | 0.130 | 0.94 | 0.120 | 0.926 | 0.965 |
| multiple horizontal | 63 | 0.036 | 0.057 | **0.165** | 0.803 | **1.077** | 1.945 | 3.40 | 0.843 | 0.413 | 0.540 |
| slanted | 363 | 0.046 | 0.071 | **0.257** | 0.753 | **1.272** | 2.089 | 4.45 | 0.854 | 0.300 | 0.493 |

## Okuma

- Dagilim **agir kuyruklu**: toplu RMS medyanin ~10 kati. Tek bir havuz RMSE esigi, 3DBAG'in kendisini bile kaldirirdi; kuyruk egimli ve cok seviyeli catilardan gelir.
- Katman 3DBAG'in cati tipidir (bir rekonstruksiyon ciktisi); yanlis tiplenmis binalar katmanlar arasinda karisabilir.
## 1-C-a degerlendirme kumesi ve DONDURULAN esikler (R, D-036)

Kume: A & pw_bron=ahn5 (1174) eksi lineage'i bekleyen / ucus sonrasi binalar (4) = **1170** bina (`reports/01_prep_1Ca_eval_set.csv`). Tolerans: medyan +0,05 m, p90 +0,10 m.

| Katman | n | 3DBAG medyan | 3DBAG p90 | **esik medyan <=** | **esik p90 <=** |
|---|---|---|---|---|---|
| horizontal | 747 | 0.031 | 0.090 | **0.081** | **0.190** |
| multiple_horizontal | 63 | 0.165 | 1.077 | **0.215** | **1.177** |
| slanted | 360 | 0.253 | 1.271 | **0.303** | **1.371** |

Config ile karsilastirma: **AYNI**.

