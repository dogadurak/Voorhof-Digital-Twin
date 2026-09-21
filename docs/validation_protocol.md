# validation_protocol.md — Neyi neyle karsilastiriyoruz?

> AGENTS.md Bolum 12.4: bir karsilastirma yapilmadan **once** su soru cevaplanir ve
> buraya yazilir:
>
> ### "Ayni fiziksel buyuklugu mu karsilastiriyorum?"
>
> Uyumsuz buyuklukler arasindaki kiyas "validation" degil,
> **"contextual comparison"** olarak etiketlenir.

**Durum: ISKELET (Asama 0.1).** Her bolum, ilgili asama baslamadan **once** doldurulur.
Bos birakilmis bir bolumle o asamanin karsilastirmasi yapilamaz.

---

## 0. Etiket sozlugu (Bolum 12.5)

Her karsilastirma asagidaki etiketlerden **birini** alir. Etiketsiz sonuc raporlanmaz.

| Etiket | Ne zaman kullanilir |
|---|---|
| `validated` | Bagimsiz ground truth var, ayni fiziksel buyukluk, ayni zaman/olcek |
| `consistency_check` | Referans bagimsiz **degil** (ayni ham veriden turemis) |
| `contextual_comparison` | Buyuklukler farkli; yalnizca baglamsal kiyas |
| `screening` | Senaryo/tarama modeli, dogrulanmis tahmin degil |
| `literature_consistent` | Yalnizca literatur vakalariyla tutarlilik |
| `indicative` | Gosterge niteliginde |

---

## 1. Geometri — Asama 1

### 1.1 3DBAG cati yuksekligi karsilastirmasi → `consistency_check`

**Neden `validated` DEGIL:** 3DBAG de AHN + roofer ile uretiliyor. Ayni ham veriden
turemis iki cikti bagimsiz ground truth sayilmaz (Bolum 5 ve 12.10).

| Alan | Bizim cikti | Referans |
|---|---|---|
| Fiziksel buyukluk | `TODO_ASAMA_1` | `TODO_ASAMA_1` |
| Yukseklik datumu | `TODO_ASAMA_1` | `TODO_ASAMA_1` |
| Ayni mi? | `TODO_ASAMA_1` | — |

**Kritik uyari:** 3DBAG `b3_h_maaiveld` (zemin kotu) referansi ile mutlak z
karistirilmamalidir. NAP sifirinin atlanmasi sistematik ~1 m mertebesinde kayma
uretir ve bu kayma toplu RMSE tarafindan maskelenir. Bu nedenle
`config/acceptance_criteria.yml` → `global_rules.bias_with_rmse` geregi
**bias her zaman RMSE ile birlikte** raporlanir.

### 1.2 AHN nokta bulutuna dogrudan z-fark → `validated` (bagimsiz)

Bu, projedeki **tek gercekten bagimsiz** geometri kontrolu. Esik henuz onaylanmadi
(`TODO_ONAY_BEKLIYOR`, Karar D-003, bkz. `reports/PENDING_DECISIONS.md` → P-004).

`TODO_ASAMA_1`: nokta secim kurali, aykiri deger kurali, cati yuzeyi izolasyonu.

---

## 2. Gunes — Asama 3

### 2.1 UMEP/SOLWEIG ↔ PVGIS → etiket `TODO_ASAMA_3`

**Bolum 12.4'un acik uyarisi:** bunlar **uc ayri buyukluktur**:

| Kaynak | Uretilen buyukluk |
|---|---|
| SOLWEIG / UMEP | Yuzeye gelen **isinim** (W/m2, kWh/m2/yil) |
| PVGIS | Belirli bir **PV sistem konfigurasyonunun uretimi** (kWh) |
| Gercek PV uretimi | Ucuncu bir buyukluk |

**Bunlar dogrudan esitlenemez.** Karsilastirma ancak ayni buyukluge donusturuldukten
sonra yapilir. Donusum zinciri burada acikca gosterilmelidir:

`TODO_ASAMA_3`: donusum zinciri (sistem verimi, kayiplar, egim/azimut, ayni zaman
araligi, ayni mekansal olcek). Donusum gosterilemezse etiket
`contextual_comparison` olur ve `validated` KULLANILMAZ.

---

## 3. Enerji — Asama 3 (CEKIRDEK)

### 3.1 PC6 agregat karsilastirmasi → `consistency_check` / agregat

**BAGLAYICI KURAL (Bolum 12.3):**

- Stedin PC6 verisi **bina duzeyinde olcum DEGILDIR** — satir basina en az 10
  baglanti birlestirilmis anonim agregattir, postcode'lar da birlestirilebilir.
- PC6 tuketimi **hicbir kosulda tek bir binaya atanmaz**.
- Karsilastirma **PC6 kumesi duzeyinde** yapilir: model ciktisi da ayni PC6 kumesine
  toplanir, kiyas iki agregat arasindadir.
- **"PC6 ground truth" ifadesi kullanilmaz.** Dogru ifade:
  **"PC6 duzeyinde agregat karsilastirma"**.

**Her PC6 icin raporlanacak baglam:**

| Alan | Deger |
|---|---|
| PC6'daki bina sayisi | `TODO_ASAMA_3` |
| Konut disi kullanim orani | `TODO_ASAMA_3` |
| Bosluk (vacancy) durumu | `TODO_ASAMA_3` |

**PC6 → BAG iliskilendirme yontemi:** `TODO_ASAMA_3` — yontem burada acikca
tanimlanmadan karsilastirma yapilamaz.

**Zaman uyumu:** Stedin PC6 **yillik agregattir** (`config/units.yml` →
`Stedin_PC6.tz: null`). Saatlik model ciktisi yillik toplama indirilmeden
karsilastirilamaz; saatlik kalibrasyon esikleri bu veriye uygulanamaz.

### 3.2 EP-Online etiket eslestirmesi

**Yalnizca geometrik yakinlikla adres eslestirilemez** (Bolum 12.3). Kullanilacak
hiyerarsi:

`BAG pand → verblijfsobject → adresseerbaar object → EP-Online label`

Belirsiz veya coklu adresli vakalar **ayri raporlanir**, sessizce bir secenek
secilmez. `TODO_ASAMA_3`: belirsiz vaka sayisi ve ele alma kurali.

---

## 4. Mikroklima ve LST — Asama 4

### 4.1 Landsat LST ↔ ENVI-met → `contextual_comparison` (ZORUNLU etiket)

**Landsat LST = YUZEY sicakligi. ENVI-met HAVA sicakligi da uretir.
Bu ikisi dogrudan kiyaslanmaz** (Bolum 12.4).

Ek sinirlama (Bolum 5): Landsat termal bandi **gercekte 100 m** cozunurluktedir,
30 m'ye resample edilmistir. Tek bir mahalle icin kabadir. ECOSTRESS (~70 m)
denenebilir. Bu sinirlama rapordan **cikarilmaz**.

### 4.2 Ruzgar → `literature_consistent`

Bagimsiz acik CFD benchmark zayif (Bolum 5). Sonuc en fazla "NEN 8100 literatur
vakalariyla tutarli" olarak sunulur. Mesh bagimsizlik calismasi yapilmadan CFD
sonucu **raporlanmaz** (Bolum 12.9).

### 4.3 Sel → `screening`

AHN DTM tabanli **topografik screening senaryosudur**. Klimaateffectatlas ile
yalnizca **gorsel** karsilastirma yapilir (indirilebilir resmi sel derinligi rasteri
yok — Bolum 5).

**Yasak ifadeler:** "dogrulanmis hidrolik sel modeli", "sel tahmini".
