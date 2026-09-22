# Asama 0.3 — Spot kontrol (bagimsiz ikinci yol)

**run_id** `RUN-2026-09-22-009` · **N = 10** · **seed = 28992** (config'ten:
`input_gate_ahn.visual_check.seed`) · AGENTS.md Bolum 13.2-2 ve 13.2-5

## Yontem — neden bagimsiz

| | Asil hesap (`verify_ahn_quality.py`) | Bu kontrol |
|---|---|---|
| Nokta-poligon | `STRtree.query(..., predicate="within")` | nokta nokta `prepared.contains(Point)`, indeks YOK |
| Nokta uretimi | `shapely.points(...)` vektorel | tek tek `Point(x, y)` |
| Alan | `shapely` poligon alani | **shoelace** formulu, ham koordinatlardan |

Ayni hata iki yolda ayni sekilde tekrarlanmadikca fark gorunur. M-007
(yuklem yonu) tam da bu kontrolle yakalanabilecek bir hataydi.

## Sonuc

| bag_id | alan CSV | alan shapely | alan shoelace | fark | nokta ref | nokta bagimsiz | fark | sinif6 ref | sinif6 bagimsiz | fark |
|---|---|---|---|---|---|---|---|---|---|---|
| `0503100000009009` | 69.91 | 69.905241 | 69.905235 | -0.000005710 | 2,072 | 2,072 | +0 | 1,675 | 1,675 | +0 |
| `0503100000013780` | 51.85 | 51.851558 | 51.851555 | -0.000003129 | 3,934 | 3,934 | +0 | 3,574 | 3,574 | +0 |
| `0503100000014843` | 51.96 | 51.963920 | 51.963924 | +0.000004908 | 1,693 | 1,693 | +0 | 1,582 | 1,582 | +0 |
| `0503100000015418` | 52.80 | 52.804010 | 52.804008 | -0.000001516 | 2,981 | 2,981 | +0 | 2,667 | 2,667 | +0 |
| `0503100000019629` | 52.64 | 52.637205 | 52.637203 | -0.000001784 | 2,045 | 2,045 | +0 | 1,644 | 1,644 | +0 |
| `0503100000019633` | 9.67 | 9.667970 | 9.667965 | -0.000005065 | 340 | 340 | +0 | 296 | 296 | +0 |
| `0503100000019951` | 52.59 | 52.593366 | 52.593365 | -0.000001284 | 1,544 | 1,544 | +0 | 1,264 | 1,264 | +0 |
| `0503100000025343` | 260.13 | 260.129431 | 260.129448 | +0.000016937 | 18,288 | 18,288 | +0 | 13,740 | 13,740 | +0 |
| `0503100000027952` | 47.20 | 47.204032 | 47.204041 | +0.000008527 | 2,447 | 2,447 | +0 | 2,240 | 2,240 | +0 |
| `0503100000031382` | 56.67 | 56.674179 | 56.674175 | -0.000003738 | 2,322 | 2,322 | +0 | 1,982 | 1,982 | +0 |

- Nokta sayimi farkli olan bina: **0 / 10**
- En buyuk bagil alan farki (shoelace vs shapely, ikisi de tam hassasiyet):
  **5.24e-07** — koordinatlar ~84.000 oldugu icin shoelace'te beklenen
  kayan nokta birikimi
- CSV yuvarlamasi (`round(shapely, 2)`) hatali olan bina: **0 / 10**

**SPOT KONTROL: PASS**
