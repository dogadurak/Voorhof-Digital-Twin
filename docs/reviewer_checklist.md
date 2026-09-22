# Bağımsız Reviewer kontrol listesi

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
- [ ] **F-2** "Sınıf 6 = çatı" varsayımı yapılmış mı? (Yapılmamalı — cepheler
      de sınıf 6'dır.)
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

---

## Reviewer'ın bilmesi gereken açık maddeler

| Kayıt | Konu | Durum |
|---|---|---|
| M-011 | Sıfır grubu "depo" çıkarımı | **AÇIK** — görsel doğrulama bekleniyor |
| P-012 | Aşama 1'e hangi AHN sınıfları girecek | **AÇIK** — M-011'i bekler |
| P-001 | B/D alan boyutları | AÇIK — Aşama 3 sonu |
| P-002 | ENVI-met lisansı | AÇIK |
| P-004 | 1-C için AHN z-fark eşiği | AÇIK |
| P-005 | NMBE / CV(RMSE) eşikleri | AÇIK |
| P-007 | BAG WFS nevenadres | AÇIK |
| P-009 | Bölünmüş PC6 dışlama oranı | AÇIK |
| P-010 | CBS Kerncijfers ikinci referans | AÇIK (veri kaynağı olarak **eklenmedi**) |
| P-011 | C alanı seçimi | AÇIK — 0.3b sonrası |
