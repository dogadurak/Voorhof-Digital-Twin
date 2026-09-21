# Asama 0.3 — AHN girdi kalite kapisi

**Karar D-015** · AGENTS.md Bolum 12.12 · run_id `RUN-2026-09-21-016`

Esikler `config/acceptance_criteria.yml` -> `input_gate_ahn` altindan okundu.
O blok bu olcumden **once** ayri bir commit ile muhurlendi.

## Kapi sonucu

| Kriter | Kaynak | Esik | Olculen | Sonuc |
|---|---|---|---|---|
| **0-E sert kapi** | ahn.nl resmi spec (AHN4 tabani) | >= 10.0 p/m2 | **35.89** | **PASS** |
| **0-F beklenti** | kendi olcumumuz (37EN1 = 29,3) | >= 20.0 p/m2 | **35.89** | **PASS** |

## B alani yogunluk dagilimi

| Metrik | Deger |
|---|---|
| Olculen hucre (10 x 10 m, merkezi B icinde) | 27784 |
| Medyan yogunluk | 35.89 p/m2 |
| 10. persentil | 17.79 p/m2 |
| Bina sinifi (kod 6) toplam nokta | 20,053,799 |
| Bina sinifi noktasi olan hucre | 41.2 % |
| O hucrelerde medyan bina yogunlugu | 13.89 p/m2 |
| Sifir donuslu hucre | 0.09 % |
| Sert kapinin altinda hucre | 1.22 % |
| Beklentinin altinda hucre | 14.13 % |
| Islenen nokta (B bbox) | 167,326,080 |

**Sifir donuslu hucreler bir hata DEGILDIR:** su yuzeyleri dogal olarak donus
vermez. Su disi kumelenme Asama 1'de BGT su katmaniyla ayristirilacaktir.

## Bina bazli cati yogunlugu (esik yok — raporlanir)

A alanindaki **1259** bina icin, ayakizi poligonu icine dusen nokta /
ayakizi alani:

| Metrik | Deger |
|---|---|
| Medyan | 38.22 p/m2 |
| 10. persentil | 28.27 p/m2 |
| **10 p/m2 altinda** | **1 bina** (%0.1) |

Tam liste: `reports/ahn_point_density_by_building.csv`

**Esik konulmadi** cunku dusuk cati yogunlugu tek basina hata degildir —
kucuk veya egimli catili binalarda dogal olarak az nokta duser.

**Asama 1'de kullanimi:** `reports/failed_buildings.csv` bu listeyle
karsilastirilacak. Basarisiz VE dusuk yogunluklu -> neden muhtemelen **girdi**;
basarisiz AMA yeterli yogunluklu -> neden muhtemelen **yontem**. Bu ayrim
sonradan yapilamaz.

## Sinif dagilimi (veriden okundu, ASPRS varsayilmadi)

```
2:74128027, 1:64953951, 6:27504797, 26:634292, 9:92091, 14:12922
```


## Olcum tanimindan gelen bilinen yanlilik

Bina bazli yogunluk, ayakizi poligonunun **icine dusen** noktalari sayar
(`within`; kesisim degil). Poligon sinirindaki noktalar elenir. Elenen bolge
**cevreyle**, sayilan bolge **alanla** orantili oldugundan, kucuk ayakizlerinde
yogunluk sistematik olarak biraz dusuk cikar.

Bu bir veri sorunu degildir, olcum tanimindan gelir. 10 p/m2 altindaki tek bina
(`0503100000011569`) 18,03 m2 ile kucuk bir yapidir ve bu etkiden paylarina
dusen olcude etkilenmistir. Asama 1'de dusuk yogunluklu binalar yorumlanirken
akilda tutulmalidir (bkz. MISTAKES.md M-007 ikincil bulgu).

## Sinif kodlari — ASPRS varsayilmadi, veriden okundu

| Kod | Nokta | Yorum |
|---|---|---|
| 2 | 74.128.027 | zemin (ASPRS 2 ile tutarli) |
| 1 | 64.953.951 | siniflandirilmamis |
| 6 | 27.504.797 | bina (ASPRS 6 ile tutarli) |
| 26 | 634.292 | **ASPRS disi** - AHN'e ozgu sinif |
| 9 | 92.091 | su (ASPRS 9 ile tutarli) |
| 14 | 12.922 | ASPRS disi / ayrilmis |

Kod 26 ve 14'un anlami AHN belgelerinden **dogrulanmamistir**; Asama 1'de
rekonstruksiyona girecek siniflar secilirken teyit edilmelidir.
