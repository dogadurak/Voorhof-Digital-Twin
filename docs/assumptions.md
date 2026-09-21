# assumptions.md — Varsayimlar

> AGENTS.md Bolum 1 kural 5: "Belirsizligi gizleme. Supheli sonuc raporda
> *sinirlama* olarak yazilir."
> Bolum 12.11: temel model varsayimi kullanici onayi olmadan degistirilemez.
> Bolum 14.3: bir varsayimin yanlis oldugunun anlasilmasi MISTAKES.md kaydi acar.

**Durum: ISKELET (Asama 0.1).** Her varsayim, yapildigi anda buraya kaydedilir.
Kaydedilmemis varsayim, birkac oturum sonra "bilinen gercek" gibi davranmaya baslar.

## Kayit sablonu

```
### V-00N  ·  [TARIH]  ·  Asama X
Varsayim:      Ne varsayildi?
Neden gerekli: Bu varsayim olmadan hangi is yapilamiyordu?
Dayanak:       Kaynak / literatur / muhendislik gerekcesi. Yoksa "DAYANAKSIZ" yaz.
Etkiledigi cikti: Hangi sayilar bu varsayima bagli?
Yanlissa ne olur: Hata buyuklugu ve yonu (sistematik mi, rastgele mi?)
Nasil test edilebilir: Varsa dogrulama yolu.
Durum:         ACIK / DOGRULANDI / CURUTULDU
```

## Bilinen yapisal varsayimlar (AGENTS.md'den devralinan)

Bunlar proje tanimindan gelir, ajan tarafindan secilmemistir — ama yine de
varsayimdir ve raporun "Limitations" bolumunde gorunur.

| # | Varsayim | Kaynak | Risk |
|---|---|---|---|
| S-1 | Voorhof %90+ konut kullanimidir | AGENTS.md Bolum 2 | Konut disi oran beklenenden yuksekse PC6 karsilastirmasi bozulur |
| S-2 | 1960-1975 tek yapim-yili kohortu 5-8 arsetiple temsil edilebilir | Bolum 2, 6 | Arsetip sayisi yetersizse enerji sapmasi sistematik olur |
| S-3 | Cati geometrisi duz/basit, LOD2 RMSE 10-20 cm hedefi gercekci | Bolum 2 | Hedef tutmazsa Asama 1 FAIL — esik degistirilmez (12.2) |
| S-4 | B alani ~300 m tampon golgeleme icin yeterli | Bolum 3 | Yetersizse kenar binalarda golge eksik kalir, gunes potansiyeli YUKSEK cikar |
| S-5 | AHN5 Randstad yogunlugu >=20 nokta/m2 | Bolum 2 | Gercek yogunluk dusukse LOD2 kalitesi duser |

**S-4 ozel notu:** Tamponsuz veya yetersiz tamponlu simulasyon, gunes potansiyelini
**sistematik olarak yuksek** gosterir (Bolum 3). Bu, yon bilinen bir hatadir:
tampon yetersizse sonuc iyimser taraftan yanlistir.

**S-5 ozel notu:** 3DBAG `b3_puntdichtheid_ahn5` ozniteligi bu varsayimi Asama 1'de
dogrudan test etmeye imkan verir.

## Ajan tarafindan yapilan varsayimlar

*(Asama 0.1 itibariyle yok. Yapilan her varsayim yukaridaki sablonla buraya eklenir.)*
