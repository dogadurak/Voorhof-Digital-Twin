"""WFS istemcisi — sayfalama, filtre dogrulama ve boyut kontrolu.

Bu modul MISTAKES.md **M-004**'un uc kuralini tek noktada uygular:

1. Her sorguya ust sinir konur (`count`), filtre calismazsa zarar sinirli kalir.
2. Filtrenin uygulandigi CIKTIDAN dogrulanir, istekten degil.
3. Indirme oncesi beklenen buyukluk `resultType=hits` ile olculur.

Gerekce: PDOK WFS'leri desteklemedikleri parametreyi (ornek `CQL_FILTER`) hata
dondurmeden **sessizce yok sayar** ve tum katmani doner. 2026-09-21'de bu sekilde
61,7 MB ulke geneli veri bosa indirildi. Sessizce yok sayilan bir filtre, Karar
D-006'yi (ulke geneli indirme yasagi) kullanici hicbir sey yanlis yapmadan ihlal
ettirir.

Bu servisler **OGC Filter Encoding 2.0** kullanir; CQL DESTEKLENMEZ.
"""

from __future__ import annotations

import logging
from typing import Any, Callable, Iterable

import requests

# Tek bir sorgunun donebilecegi ozellik sayisi ust siniri.
# Bu asilirsa indirme YAPILMAZ; sorgu daraltilir (M-004 kural 3).
MAX_FEATURES_HARD_LIMIT = 50_000

# PDOK BAG WFS CountDefault degeri (GetCapabilities'ten okundu, 2026-09-21)
DEFAULT_PAGE_SIZE = 1000

REQUEST_TIMEOUT_S = 120


class WfsError(RuntimeError):
    """WFS sorgusu basarisiz oldu veya beklenmeyen sonuc dondu."""


class FilterIgnoredError(WfsError):
    """Servis filtreyi uygulamadi — donen kayitlar filtre kosulunu saglamiyor.

    Bu hata BILEREK firlatilir. Filtresiz donen veri `data/raw/`'a YAZILMAZ.
    """


def property_equals_filter(field: str, value: str) -> str:
    """Tek alan esitligi icin OGC Filter Encoding 2.0 XML'i uretir.

    Girdi : field — oznitelik adi (ornek "wijkcode")
            value — aranan deger (ornek "WK050324")
    Cikti : str — <fes:Filter> XML'i
    Birim : yok
    """
    return (
        '<fes:Filter xmlns:fes="http://www.opengis.net/fes/2.0">'
        "<fes:PropertyIsEqualTo>"
        f"<fes:ValueReference>{field}</fes:ValueReference>"
        f"<fes:Literal>{value}</fes:Literal>"
        "</fes:PropertyIsEqualTo>"
        "</fes:Filter>"
    )


def bbox_param(minx: float, miny: float, maxx: float, maxy: float, crs: str) -> str:
    """WFS 2.0 bbox parametresini CRS'i ACIKCA yazarak uretir.

    Girdi : minx, miny, maxx, maxy — EPSG:28992 metre cinsinden sinirlar
            crs — "EPSG:28992" bicimli kod
    Cikti : str — "minx,miny,maxx,maxy,urn:ogc:def:crs:EPSG::28992"
    Birim : m

    CRS bbox'a acikca yazilir; varsayilana birakilmaz (AGENTS.md Bolum 1, kural 6).
    Eksen sirasi hatasi bu sekilde onlenir.
    """
    authority, code = crs.split(":")
    return f"{minx:.3f},{miny:.3f},{maxx:.3f},{maxy:.3f},urn:ogc:def:crs:{authority}::{code}"


def count_hits(
    service: str,
    typename: str,
    version: str = "2.0.0",
    filter_xml: str | None = None,
    bbox: str | None = None,
    logger: logging.Logger | None = None,
) -> int:
    """Indirmeden ONCE kac ozellik donecegini olcer (`resultType=hits`).

    Cikti : int — eslesen ozellik sayisi
    Birim : adet

    M-004 kural 3: beklenen buyukluk indirmeden once bilinmelidir. Bu cagri
    geometri indirmez, yalnizca sayi doner.
    """
    params: dict[str, str] = {
        "service": "WFS",
        "version": version,
        "request": "GetFeature",
        "typeNames": typename,
        "resultType": "hits",
    }
    if filter_xml:
        params["filter"] = filter_xml
    if bbox:
        params["bbox"] = bbox

    response = requests.get(service, params=params, timeout=REQUEST_TIMEOUT_S)
    response.raise_for_status()

    text = response.text
    marker = "numberMatched="
    if marker not in text:
        raise WfsError(f"resultType=hits yanitinda numberMatched yok: {text[:200]}")

    raw = text.split(marker, 1)[1].lstrip('"').split('"', 1)[0]
    if raw == "unknown":
        raise WfsError("Servis numberMatched='unknown' dondu; boyut onceden olculemiyor.")

    hits = int(raw)
    if logger:
        logger.info("WFS hits | katman=%s | eslesen=%d", typename, hits)
    return hits


def fetch_features(
    service: str,
    typename: str,
    version: str = "2.0.0",
    filter_xml: str | None = None,
    bbox: str | None = None,
    page_size: int = DEFAULT_PAGE_SIZE,
    max_features: int = MAX_FEATURES_HARD_LIMIT,
    verify: Callable[[dict[str, Any]], bool] | None = None,
    logger: logging.Logger | None = None,
) -> dict[str, Any]:
    """Bir WFS katmanini sayfalayarak GeoJSON olarak indirir.

    Girdi : service     — WFS endpoint
            typename    — katman adi (ornek "bag:pand")
            filter_xml  — OGC Filter Encoding XML (CQL DEGIL)
            bbox        — bbox_param() ciktisi
            page_size   — sayfa basina ozellik (servis CountDefault'u asamaz)
            max_features— guvenlik siniri; asilirsa indirme YAPILMAZ
            verify      — her ozellik icin filtre kosulunu sinayan fonksiyon
    Cikti : dict — GeoJSON FeatureCollection
    Birim : yok

    Once `resultType=hits` ile boyut olculur (M-004 kural 3). Sinir asilirsa
    WfsError firlatilir ve hicbir sey indirilmez.
    """
    log = logger or logging.getLogger(__name__)

    expected = count_hits(service, typename, version, filter_xml, bbox, log)
    if expected > max_features:
        raise WfsError(
            f"{typename} icin {expected} ozellik eslesti, ust sinir {max_features}. "
            f"Indirme YAPILMADI — sorguyu daraltin (Karar D-006: ulke geneli indirme yasak)."
        )
    if expected == 0:
        raise WfsError(
            f"{typename} icin 0 ozellik eslesti. Filtre veya bbox yanlis olabilir; "
            f"bos sonuc data/raw/'a yazilmaz."
        )

    features: list[dict[str, Any]] = []
    crs_name: str | None = None
    start = 0

    while start < expected:
        params: dict[str, str] = {
            "service": "WFS",
            "version": version,
            "request": "GetFeature",
            "typeNames": typename,
            "outputFormat": "application/json",
            "count": str(page_size),          # M-004 kural 1: her zaman ust sinir
            "startIndex": str(start),
        }
        if filter_xml:
            params["filter"] = filter_xml
        if bbox:
            params["bbox"] = bbox

        response = requests.get(service, params=params, timeout=REQUEST_TIMEOUT_S)
        response.raise_for_status()
        page = response.json()

        batch = page.get("features", [])
        if not batch:
            log.warning("Sayfa bos dondu (startIndex=%d); sayfalama sonlandiriliyor.", start)
            break

        if crs_name is None:
            crs_name = page.get("crs", {}).get("properties", {}).get("name")

        features.extend(batch)
        start += len(batch)
        log.info("WFS sayfa | katman=%s | %d/%d", typename, len(features), expected)

    # --- M-004 kural 2: filtre CIKTIDAN dogrulanir ---
    if verify is not None:
        bad = [f for f in features if not verify(f)]
        if bad:
            raise FilterIgnoredError(
                f"{typename}: {len(bad)}/{len(features)} kayit filtre kosulunu SAGLAMIYOR. "
                f"Servis filtreyi yok saymis olabilir. Veri data/raw/'a YAZILMADI. "
                f"Ornek: {bad[0].get('properties', {})}"
            )
        log.info("Filtre dogrulandi | %d kayit kosulu sagliyor", len(features))

    if len(features) != expected:
        log.warning(
            "Beklenen %d ozellik, indirilen %d. Fark aciklanmali.", expected, len(features)
        )

    return {
        "type": "FeatureCollection",
        "crs": {"type": "name", "properties": {"name": crs_name}},
        "features": features,
    }


def crs_urn_to_epsg(urn: str | None) -> str:
    """WFS'in dondurdugu CRS URN'unu "EPSG:xxxxx" bicimine cevirir.

    Girdi : urn — "urn:ogc:def:crs:EPSG::28992" gibi
    Cikti : str — "EPSG:28992", cozulemezse "BILINMIYOR"

    Bu deger log_crs() ile beklenen CRS'e karsi sinanir (Bolum 14.6).
    """
    if not urn:
        return "BILINMIYOR"
    if "EPSG" in urn:
        return "EPSG:" + urn.rsplit(":", 1)[-1]
    return urn


def bounds_of(features: Iterable[dict[str, Any]]) -> tuple[float, float, float, float]:
    """Bir ozellik kumesinin bbox'ini hesaplar.

    Cikti : (minx, miny, maxx, maxy)
    Birim : m (EPSG:28992)
    """
    xs: list[float] = []
    ys: list[float] = []

    def walk(coords: Any) -> None:
        if coords and isinstance(coords[0], (int, float)):
            xs.append(coords[0])
            ys.append(coords[1])
        else:
            for part in coords:
                walk(part)

    for feature in features:
        geometry = feature.get("geometry")
        if geometry:
            walk(geometry["coordinates"])

    if not xs:
        raise WfsError("Ozelliklerde geometri bulunamadi; bbox hesaplanamadi.")
    return min(xs), min(ys), max(xs), max(ys)
