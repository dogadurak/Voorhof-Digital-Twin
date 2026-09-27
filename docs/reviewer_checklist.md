# Bağımsız Reviewer kontrol listesi

**Son güncelleme:** 2026-09-27 (H ve I bölümleri eklendi)

**Amaç:** AGENTS.md §12.10 — bir ajan kendi ürettiği çıktıyı yalnızca kendi
hesabına dayanarak "doğrulandı" ilan edemez. Bu liste, **ayrı bir oturumda**
çalışan Reviewer'ın ne arayacağını tanımlar.

**Kullanım:** Reviewer bu listeyi tek tek işler ve her maddeye
`GEÇTİ / KALDI / UYGULANMAZ` + bir cümle gerekçe yazar. Boş bırakılan madde
= KALDI.

---

## A. Eşik disiplini (§12.2)

- [ ] **A-1** Her eşik `config/acceptance_criteria.yml`'de mi, kodda gömülü değil mi?
- [ ] **A-2** Eşiği mühürleyen commit, ölçümü yapan commit'ten **önce** mi?
      (`git log` sırasıyla doğrula — iddiaya değil git'e bak)
- [ ] **A-3** Sonuç görüldükten sonra gevşetilmiş bir eşik var mı?
- [ ] **A-4** Config'deki her `decision_ref: D-xxx` için DECISIONS.md'de
      gerçekten o kayıt var mı? (M-008)
- [ ] **A-5** "SONRAKI BOŞ ID" satırı, var olan en büyük D kaydından büyük mü?

## B. Ölçüm ile çıkarım ayrımı (§12.13)

- [ ] **B-1** Rapordaki her çıkarım **"ÇIKARIM"** olarak etiketli mi?
- [ ] **B-2** Bir kararı (dışlama, sınıflandırma, metodoloji) etkileyen her
      çıkarım, karardan **önce** bağımsız bir yoldan doğrulanmış mı?
- [ ] **B-3** Doğrulama gerçekten **bağımsız** mı — aynı veri kaynağının
      içinden türetilmiş ikinci bir gösterge değil mi? (§12.10)
- [ ] **B-4** Örneklem sabit `seed` ile mi seçilmiş, seed config'de mi?
- [ ] **B-5** Doğrulanamayan çıkarımlar §5 sınırlamalarına girmiş mi?
- [ ] **B-6** Doğrulamayı **ajan mı önerdi**, yoksa kullanıcı mı sordu? (M-011)

## C. Genelleme ve özet istatistik (§14.6, M-010)

- [ ] **C-1** Bir grup hakkında "hepsi / çoğu / genelde" denmişse, grup hem
      **sayıya** hem **etkiye** göre özetlenmiş mi?
- [ ] **C-2** Etkiye göre en büyük **5 üye tek tek** listelenmiş mi?
- [ ] **C-3** Genellemeye uymayan üye var mı? Varsa alt gruba bölünmüş veya
      istisna açıkça yazılmış mı?
- [ ] **C-4** Raporun kendi tabloları, raporun kendi metniyle çelişiyor mu?
      (M-010 tam olarak böyle kaçtı)

## D. Adlandırma

- [ ] **D-1** Her sütun/değişken adı, hesapladığı ifadeyi **birebir** söylüyor mu?
      (M-010 ek bulgu: `has_dwellings` aslında `VBO > 0` ölçüyordu)
- [ ] **D-2** Birim, ada yazılı mı (`area_m2`, `eui_kwh_m2_yr`)? (§14.6)
- [ ] **D-3** Raporda **kesilmiş** kategorik değer var mı (`[:N]`)? Rapordaki her tablo depodaki bir scriptten mi üretilmiş, yoksa elle mi aktarılmış? (M-010 tekrarı: kesilen metin 260 konutlu bir binayı konut dışı gösterdi)

## E. Veri dönemi ve kaynak (D-020, §5)

- [ ] **E-1** Raporun başında **veri dönemi** notu var mı?
- [ ] **E-2** Geometri (AHN5 2023-02) ile öznitelik (BAG 2026-09) arasındaki
      fark, sonuçları etkilediği her yerde belirtilmiş mi?
- [ ] **E-3** "Geometrisi yok (uçuş sonrası)" binaları listelenmiş mi,
      sessizce düşürülmemiş mi? (§12.8)

## F. Sınıf ve girdi kalitesi

- [ ] **F-1** AHN sınıf kodu yorumları `docs/ahn_class_codes.md`'ye dayanıyor
      mu; belgelenen (26) ile çıkarım olan (14) ayrı mı? (D-017)
- [ ] **F-2** Sınıf 6'nın ne içerdiği **hangi AHN sürümüne göre** yazılmış?
      AHN4'te cepheler sınıf 6'dır; **AHN5'te cepheler sınıf 1'dir** (WP1 2024).
      Bizim verimizde hangisinin geçerli olduğu ölçüldü mü? (M-005 tekrarı)
      → Ölçüldü 2026-09-27: **MIXED** (D-017 EK 1). Reviewer kontrol eder:
      yöntem commit'i (4b6ad61, b353121) ölçüm commit'inden **önce** mi? Post-hoc
      çatı-tipi analizi (`reports/01_prep_facade_class_posthoc.md`) mühürlü
      kararın yerine **geçirilmiş mi**? (Geçirilmemeli.)
- [ ] **F-5** Dış bir spesifikasyondan gelen her sayının yanında belge + bölüm
      + doğrulama tarihi var mı? "Kullanıcı yazdı" doğrulama sayılmış mı?
      Negatif iddialar ("hiçbir belge yok") aranan kaynakları sayıyor mu?
      (`python src/qa/check_claims.py`)
- [ ] **F-3** `building_class_ratio` bağımsız doğrulama olarak kullanılmış mı?
      (Kullanılmamalı — sınıf 6 BAG'den türer, §12.10.)
- [ ] **F-4** Girdi kalite kapısı (§12.12) ilgili aşamada **işlemeden önce**
      çalıştırılmış mı?

## G. Genel

- [ ] **G-1** Uydurma sayı, sürüm veya paket adı var mı? (M-001, M-005)
- [ ] **G-2** Exit code 0, "başarılı" kanıtı olarak kullanılmış mı? (M-002)
- [ ] **G-3** Mekânsal yüklem kullanan her yerde yön testi var mı? (M-007)
- [ ] **G-6** Log/konsol çıktısında **uyarı** var mı ve açıklanmış mı? Ajanın komutlarında uyarıları silen `grep -v` var mı? (M-012)
- [ ] **G-7** Her logda `PROJ dogrulandi` satırı var mı? (M-003 tekrarı)
- [ ] **G-4** Sınırlamalar yazılmış mı, gizlenmiş mi?
- [ ] **G-5** Başarısız kayıtlar CSV'ye düşmüş mü? (§12.8)

## H. Mühür, örneklem ve körlük (D-024 … D-032, M-015, M-016)

- [ ] **H-1** Her mühürlü blok, **kendi commit'inde** ve gözlemden/ölçümden
      **önce** mi? Kontrol edilecek sıra (git'e bak, iddiaya değil):
      D-024 `4093217` → görsel kontrol (henüz yok) ·
      D-030 `f2667c1` → yükseklik ölçümü + seçim `fe62b93` ·
      D-032 `20ab104` → yedek seçimi `b92cb5d`.
- [ ] **H-2** Mühürlü bir kural sonradan değiştirildiyse, eski metin
      **silinmeden** duruyor mu ve değişiklik **gözlemden önce** mi yapılmış?
      (D-030 EK 1 `blind_counting`; D-031 `stratification_superseded_p020`)
- [ ] **H-3** `python src/qa/check_config_structure.py` PASS mı? Mühürlü bir
      anahtar başka bir bloğun içine düşmüş mü? (M-015 — YAML girinti yutması)
- [ ] **H-4** Örneklem kuralının **amaç cümlesi** ölçülmüş mü? Logda
      `AMAC OLCUMU (M-016) ... IDDIA: TUTTU` satırı var mı? (M-016)
- [ ] **H-5** Saha listesinde (`docs/field_check_list.md`) **ölçülen yükseklik
      YOK** mu? (Olmamalı — kat sayımı demirlenmesin, D-030 EK 1)
- [ ] **H-6** Yedek binalar (D-032) yalnızca asılın **kullanılamaması** ile
      mi tetikleniyor, değeriyle değil mi?
- [ ] **H-7** "Karar veremedim" (D-028) S2/S3 ile **aynı satırda** sayılmış
      mı? (Sayılmamalı — ölçüme değil kararsızlığa dayanır, ayrı raporlanır.)

## I. Aşama 3 öncesi (araştırmadan çıkan boşluklar, 2026-09-26)

- [ ] **I-1** Stedin verisi "ölçülmüş tüketim" diye mi anılıyor? (Değil:
      SJV = normalleştirilmiş yılda **beklenen** tüketim. P-022)
- [ ] **I-2** PC6 dışlama kuralları (PV salderen, blok ısıtması) Stedin
      değerlerine **bakılmadan önce** mi mühürlendi? (P-023)
- [ ] **I-3** Kalibrasyon ve doğrulama **aynı veriyle** mi yapıldı? (P-025)
- [ ] **I-4** Beklenen sapma yönü (fizik modeli ölçümden **yüksek**) sonuçtan
      önce yazılmış mı? (P-025 ön-kayıt notu)

## J. Ölçüm araçlarının kendisi (§13.6 — "araç sonuca göre değiştirilemez")

> Kullanıcı talebi (2026-09-27): "check_claims.py'yi bir kez gevşetip gerçek
> hatayı gizlediğini söyledin — bunu Reviewer'ın özellikle bakacağı listeye ekle."

- [ ] **J-1** `src/qa/check_claims.py` **gevşetilmiş mi?** Olay: 2026-09-27'de
      ajan, aracın çıktısını gördükten sonra "ölçüldü" kelimesini arama kanıtı
      listesine ekledi; bu, düzeltilmesi gereken gerçek hatayı (AGENTS §5'teki
      "ÖLÇÜLDÜ … AHN5 için hiçbir spesifikasyon vermiyor") listeden **sildi**.
      Ajan fark edip geri aldı. Reviewer şunlara bakar:
      - `git log -p -- src/qa/check_claims.py`: `SEARCH_EVIDENCE`,
        `NEGATIVE_PATTERNS`, `EXTERNAL_DOC`, `VERIFIED_KEYS` veya `SKIP_FILES`'ta
        **daraltan/gevşeten** bir değişiklik var mı; varsa gerekçesi aracın
        **çıktısına bakmadan** mı yazılmış?
      - Oz-sınama fikstürleri (`SELF_TEST_NEGATIVE`, `SELF_TEST_CONFIG`)
        silinmiş ya da beklenen değerleri çevrilmiş mi? (Çevirmek = gevşetmek.)
      - Araç `[OZ-SINAMA] … 0 basarisiz` basıyor mu? Oz-sınama, gevşetmenin
        aynısı bellekte yeniden yapılarak denendi ve **kırmızı yandı**
        (2026-09-27).
- [ ] **J-2** Bilinen açık gevşeklik (ajanın kendi tespiti, 2026-09-27):
      `SEARCH_EVIDENCE` "yanlış", "düzelt" ve `~~` içeren **her** paragrafı
      atlıyor — kelime başka bir konu için geçse bile. Bu paragraflardaki
      negatif iddialar hiç denetlenmiyor. Reviewer bu paragrafları elle okur
      (`grep -n "yanl\|düzelt\|~~"` ile listelenir) veya kuralın
      daraltılmasını önerir.
- [ ] **J-3** Diğer `src/qa/` araçlarında (`check_config_structure.py`,
      `check_refs`, …) aynı soru: bir kontrol, çıktısı görüldükten sonra
      kapsamı daraltılarak mı "geçti"?
- [ ] **J-4** İlk tasarım hatası da kayıtlı mı? `check_claims.py`'nin ilk
      sürümü **yanlış şeyi ölçüyordu** ("== 0" politika eşiklerini hata
      sayıyordu). Yeniden tasarım dosyanın docstring'inde yazılı; Reviewer
      yeni tasarımın gerçek hata biçimini (dış belgeye dayanan, doğrulama
      tarihi olmayan iddia) yakaladığını fikstürlerden teyit eder.

- [ ] **J-5** Kodun içine gömülü **sabit iddia cümleleri** (M-005 5. tekrar,
      2026-09-27): `grep -rn "okundu\|olculdu\|dogrulandi" src/` ile bulunan
      her `notes=`/log metni için, iddia edilen okuma/karşılaştırma **aynı
      kodda gerçekten yapılıyor mu**? `data_log.append_entry` çağrılarının
      hepsi `method=` veriyor mu? (DATA_LOG'da AHN5 "347/2022 ÇELİŞKİ" ve
      "WFS GetFeature" kayıtları bu yoldan yanlış yazılmıştı.)
- [ ] **J-6** `.githooks/pre-commit` etkin mi (`git config --get
      core.hooksPath` → `.githooks`)? Commit geçmişinde kanca sonrası
      `--no-verify` izi var mı? (M-008 2. tekrar)

---

## Reviewer'ın bilmesi gereken açık maddeler

| Kayıt | Konu | Durum |
|---|---|---|
| M-011 | Sıfır grubu "depo" çıkarımı | **AÇIK** — görsel doğrulama bekleniyor (kullanıcı yapacak, P-021 kapandı) |
| P-012 | Aşama 1'e hangi AHN sınıfları girecek | **AÇIK** — M-011'i bekler |
| — | Kat sayımı (22 bina + 3 yedek) | **BEKLİYOR** — kullanıcı, `docs/field_check_list.md` |
| P-022 … P-026 | Aşama 3 boşlukları (Stedin SJV, PC6 kuralları, yıl, kalibrasyon, ağaç gölgesi) | AÇIK — Aşama 3 öncesi |
| P-027 | "Dijital ikiz" teriminin düzeyi | AÇIK — Aşama 5 öncesi |
| P-001 | B/D alan boyutları | AÇIK — Aşama 3 sonu |
| P-002 | ENVI-met lisansı | AÇIK |
| P-004 | 1-C için AHN z-fark eşiği | AÇIK |
| P-005 | NMBE / CV(RMSE) eşikleri | AÇIK |
| P-007 | BAG WFS nevenadres | AÇIK |
| P-009 | Bölünmüş PC6 dışlama oranı | AÇIK |
| P-010 | CBS Kerncijfers ikinci referans | AÇIK (veri kaynağı olarak **eklenmedi**) |
| P-011 | C alanı seçimi | AÇIK — 0.3b sonrası |
