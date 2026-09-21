# Nihai dogrulama raporu

**Durum: BOS ISKELET.** Asama 5'te uretilecektir.

> AGENTS.md Bolum 0: **"Teslim edilen asil urun model degil, DOGRULAMA RAPORUDUR."**
> 3B model ve web arayuzu bu raporun ekleridir. Bir ajan bu onceligi tersine
> cevirirse yanlis is yapiyordur.

## Planlanan yapi

1. **Ozet** — hangi ciktilar dogrulandi, hangileri dogrulanmadi
2. **Yontem** — veri, boru hatti, yazilim surumleri
3. **Asama bazli sonuclar** — her kabul kriterinin olculen degeri ve PASS/FAIL
4. **Dogrulama etiketleri** — hangi sonuc `validated`, hangisi `consistency_check`,
   `contextual_comparison`, `screening` veya `literature_consistent`
   (bkz. `docs/validation_protocol.md`)
5. **Limitations** — Bolum 5'teki bilinen bosluklar + proje boyunca eklenenler
6. **Binnenstad karsilastirmasi** — modern doku vs. tarihi doku. Orada yuksek hata
   cikmasi **beklenen sonuctur, basarisizlik degildir** (Bolum 2)
7. **Hata defteri ozeti** — `MISTAKES.md`'den turetilen dersler
8. **Attribution** — `ATTRIBUTION.md`

## Rapora girmeyecek olanlar

- Kaynagi gosterilemeyen sayi (Bolum 13.1)
- "Sinirlama yok" beyani — en az bir sinirlama yazilmasi zorunludur (Bolum 13.1)
- Dogrulanmamis sonucun `validated` etiketiyle sunulmasi (Bolum 1, kural 2)
