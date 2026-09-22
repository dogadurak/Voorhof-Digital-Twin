"""PROJ / GDAL veri dizinlerini bu ortamin kendi kurulumuna sabitler.

NEDEN VAR (bkz. MISTAKES.md M-003):
Bu makinede PostgreSQL/PostGIS 3.6 kurulumu sistem genelinde su degiskenleri
tanimliyor:

    PROJ_LIB  = C:\\Program Files\\PostgreSQL\\18\\share\\contrib\\postgis-3.6\\proj
    GDAL_DATA = C:\\Program Files\\PostgreSQL\\18\\gdal-data

Bu degiskenler conda ortamindaki pyproj/rasterio/fiona kurulumunu ele geciriyor.
Sonuc: PROJ kendi surumuyle uyumsuz bir veritabani gorup hic yuklemiyor ve
`CRS.from_user_input("EPSG:28992")` bile `no database context specified`
hatasiyla dusuyor.

NEDEN SESSIZ DEGIL DE TEHLIKELI:
Bu vakada hata GURULTULU (exception). Ama ayni mekanizmanin sessiz varyanti da var:
PROJ_LIB uyumlu ama FARKLI surumde bir veritabanina isaret ederse, donusum calisir
fakat farkli datum/grid kaymasi kullanir. O durumda koordinatlar sessizce 1-2 m
kayar — AGENTS.md Bolum 14.6'daki "CRS / yukseklik datumu" hata sinifinin ta kendisi.
Bu yuzden dizin SADECE duzeltilmez, ayni zamanda LOGLANIR.

Bu modul `src.common` paketi ice aktarildiginda otomatik calisir; boylece hicbir
scriptin bunu cagirmayi unutmasi mumkun degildir.
"""

from __future__ import annotations

import os
from pathlib import Path

# Bu ortamin kendi PROJ/GDAL veri dizinleri (conda env icinde)
_ENV_ROOT = Path(os.sys.prefix)
_PROJ_DIR = _ENV_ROOT / "Library" / "share" / "proj"   # Windows conda yerlesimi
_GDAL_DIR = _ENV_ROOT / "Library" / "share" / "gdal"

# Unix/Linux conda yerlesimi (Docker veya baska makine icin)
_PROJ_DIR_NIX = _ENV_ROOT / "share" / "proj"
_GDAL_DIR_NIX = _ENV_ROOT / "share" / "gdal"


def _pick(primary: Path, fallback: Path) -> Path | None:
    """proj.db / gdal veri dizininden hangisi gercekten varsa onu dondurur."""
    if primary.is_dir():
        return primary
    if fallback.is_dir():
        return fallback
    return None


def ensure_proj_env(verbose: bool = False) -> dict[str, str]:
    """PROJ_LIB / PROJ_DATA / GDAL_DATA degiskenlerini bu ortama sabitler.

    Girdi : verbose — True ise yapilan degisiklikleri stdout'a yazar
    Cikti : dict — uygulanan {degisken: deger} eslemesi
    Birim : yok

    Yan etki: os.environ uzerinde degisiklik yapar. Yalnizca BU surec icin
    gecerlidir; sistem genelindeki PostgreSQL ayarlarina DOKUNMAZ (PostGIS'in
    kendi kurulumu bozulmamalidir).
    """
    applied: dict[str, str] = {}

    proj_dir = _pick(_PROJ_DIR, _PROJ_DIR_NIX)
    if proj_dir is not None and (proj_dir / "proj.db").is_file():
        # PROJ 9+ PROJ_DATA okur, eski surumler PROJ_LIB — ikisi de yazilir.
        os.environ["PROJ_DATA"] = str(proj_dir)
        os.environ["PROJ_LIB"] = str(proj_dir)
        applied["PROJ_DATA"] = str(proj_dir)
        applied["PROJ_LIB"] = str(proj_dir)

    gdal_dir = _pick(_GDAL_DIR, _GDAL_DIR_NIX)
    if gdal_dir is not None:
        os.environ["GDAL_DATA"] = str(gdal_dir)
        applied["GDAL_DATA"] = str(gdal_dir)

    # SIRADAN BAGIMSIZLIK (M-003 TEKRARI, 2026-09-22): ortam degiskenleri
    # yalnizca pyproj HENUZ ice aktarilmamissa etkilidir. `laspy` ve `shapely`
    # pyproj'u kendi ice aktarimlarinda yukler; bir script bunlari src.common'dan
    # ONCE ice aktarirsa pyproj PostgreSQL'in PROJ dizinine kilitlenir ve bu
    # duzeltme SESSIZCE etkisiz kalir. Olculdu: 0.3 boyunca her LAZ scriptinde
    # boyle oldu. Cozum: pyproj'un veri dizinini ACIKCA ayarla; bu cagri pyproj
    # zaten yuklenmis olsa bile baglami duzeltir.
    if proj_dir is not None:
        try:
            import pyproj.datadir as _dd
            _dd.set_data_dir(str(proj_dir))
            applied["pyproj.datadir"] = str(proj_dir)
        except ImportError:
            pass

    if verbose:
        for key, value in applied.items():
            print(f"[proj_env] {key} = {value}")

    return applied


# Oz-test icin referans (TAHMIN DEGIL): Voorhof'ta bir RD noktasi ve Delft'i
# kapsayan gevsek bir enlem/boylam kutusu. Kutu yalnizca KABA hatalari yakalar.
_TEST_RD = (84000.0, 445000.0)
_DELFT_BOX = {"lon": (4.30, 4.45), "lat": (51.95, 52.05)}
_ROUNDTRIP_TOL_M = 0.01


def assert_proj_works() -> dict[str, float | str]:
    """EPSG:28992 <-> EPSG:4326 donusumunu FIILEN calistirip sinar.

    Girdi : yok
    Cikti : dict — veri dizini, test noktasinin lon/lat'i, geri donus hatasi (m)
    Birim : derece (lon/lat), metre (hata)

    Sinar:
      1. Donusum kurulabiliyor mu (veritabani bulunuyor mu) — M-003'un GURULTULU hali
      2. RD -> WGS84 -> RD geri donus hatasi < 1 cm
      3. Test noktasi Delft'i kapsayan kutunun icinde mi — KABA datum hatasi

    SINIRLAMA (acikca): Bu test M-003'un SESSIZ varyantini — uyumlu ama farkli
    surumde bir veritabaninin metre mertebesinde farkli bir datum donusumu
    uygulamasini — YAKALAMAZ. Geri donus tutarli kalir ve kutu metre
    hatalarini gormez. O varyant icin bagimsiz bir referans noktasi gerekir
    (TODO: Asama 5 oncesi, WGS84 ciktisi uretilmeden once).

    Hata durumunda RuntimeError firlatir — sessiz gecmez.
    """
    import pyproj
    import pyproj.datadir as dd
    from pyproj import Transformer

    data_dir = dd.get_data_dir()
    try:
        fwd = Transformer.from_crs("EPSG:28992", "EPSG:4326", always_xy=True)
        inv = Transformer.from_crs("EPSG:4326", "EPSG:28992", always_xy=True)
    except Exception as exc:  # noqa: BLE001 - her hata burada ayni anlama gelir
        raise RuntimeError(
            f"PROJ donusumu kurulamadi (MISTAKES.md M-003). pyproj veri dizini: "
            f"{data_dir}. Hata: {exc}") from exc

    lon, lat = fwd.transform(*_TEST_RD)
    x, y = inv.transform(lon, lat)
    err = abs(x - _TEST_RD[0]) + abs(y - _TEST_RD[1])
    if err > _ROUNDTRIP_TOL_M:
        raise RuntimeError(f"PROJ geri donus hatasi {err:.4f} m > {_ROUNDTRIP_TOL_M} m")
    if not (_DELFT_BOX["lon"][0] <= lon <= _DELFT_BOX["lon"][1]
            and _DELFT_BOX["lat"][0] <= lat <= _DELFT_BOX["lat"][1]):
        raise RuntimeError(f"PROJ test noktasi Delft disina dustu: lon={lon}, lat={lat}")
    return {"data_dir": data_dir, "proj_version": pyproj.proj_version_str,
            "lon": lon, "lat": lat, "roundtrip_error_m": err}


def verify_proj(expected_code: str = "EPSG:28992") -> str:
    """PROJ veritabaninin gercekten calistigini bir CRS olusturarak dogrular.

    Girdi : expected_code — test edilecek EPSG kodu (varsayilan RD New)
    Cikti : str — CRS'in tam adi (ornek "Amersfoort / RD New")
    Hata  : pyproj.exceptions.CRSError — veritabani hala erisilebilir degilse

    Bu fonksiyon "kurulum calisiyor" varsayimini FIILEN test eder
    (MISTAKES.md M-002: cikis kodu basari kaniti sayilmaz).
    """
    from pyproj import CRS  # gec ice aktarma: ensure_proj_env once calissin

    return CRS.from_user_input(expected_code).name


def proj_data_dir() -> str:
    """Pyproj'un fiilen kullandigi PROJ veri dizinini dondurur (loglamak icin)."""
    from pyproj import datadir

    return str(datadir.get_data_dir())
