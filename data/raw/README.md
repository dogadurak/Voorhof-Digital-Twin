# data/raw/ — SALT OKUNUR

AGENTS.md Bolum 8: **"data/raw/ salt okunur. Hicbir script oraya yazmaz."**
Bolum 12.7: **"Ham veri hicbir sekilde degistirilmez."**

Buraya yalnizca `src/00_acquisition/` altindaki indirme scriptleri dosya birakir.
Indirilen her dosya indirildigi haliyle kalir; donusum, kirpma, yeniden projeksiyon
gibi islemler ciktilarini `data/interim/` veya `data/processed/` altina yazar.

Dosyalarin kendisi git ile izlenmez (bkz. `.gitignore`). Her dosyanin kaynak URL'si,
surumu, indirme tarihi, CRS'i, lisansi ve SHA-256 checksum'i `data/DATA_LOG.md`
icinde tutulur — kayit repoda, veri diskte.
