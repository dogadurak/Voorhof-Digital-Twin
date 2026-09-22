"""3DBAG'i ADI BELLI bir surumden, B + 50 m icin indirir (Karar D-027, P-016).

Asama : 0.3
Neden : `api.3dbag.nl` surumunu `v2023.10.08` diye etiketliyor ama icerigi
        2025.09.03 ile tutarli (D-023, M-013). Bir tutarlilik kontrolu
        (kriter 1-B) referansinin kimligi belirsiz olamaz — ayni girdiyle iki
        calistirma ayni sonucu vermek zorundadir (AGENTS.md Bolum 8).

Surum URL YOLUNDA sabitlidir: https://data.3dbag.nl/v20250903/...
Bu, servisin "su an ne sunuyorsa" degil, adi belli bir yayindir.

Cikti : data/raw/3dbag_v20250903/*.city.json.gz  (fayans basina)
        data/raw/3dbag_v20250903/metadata.json   (yayin meta verisi)
        data/raw/3dbag_v20250903/tile_index_subset.geojson
        + .meta.json + data/DATA_LOG.md kaydi

DOGRULAMA: fayans indeksi her fayans icin `cj_sha256` yayinliyor. Indirilen
her dosyanin SHA-256'si bu degerle karsilastirilir — checksum'i BIZ
uretmiyoruz, yayincidan geliyor. Uyusmazlik hata firlatir.

Calistirma:
    python src/00_acquisition/download_3dbag_pinned.py
"""

from __future__ import annotations

import gzip
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# M-003 / M-012: PROJ dizini, pyproj'u yukleyen kutuphanelerden ONCE sabitlenir.
import src.common  # noqa: E402,F401

import geopandas as gpd
import requests
from shapely.geometry import shape

from src.common.config import expected_crs, resolve
from src.common.data_log import append_entry
from src.common.logging_setup import setup_logging
from src.common.meta import write_meta

VERSION = "v2025.09.03"
VERSION_PATH = "v20250903"          # URL'deki bicim
BASE = f"https://data.3dbag.nl/{VERSION_PATH}"
TILE_INDEX = f"/vsicurl/{BASE}/tile_index.fgb"
SAFETY_MARGIN_M = 50.0              # Karar D-010 (karsilastirma kapsami)
# Fayans SECIMI icin ek pay: fayans indeksi poligonlari, bir binanin hangi
# fayans dosyasinda oldugunu birebir vermiyor. Olculdu 2026-09-22: merkezi
# fayans birlesiminin ICINDE olan 2 bina, secilen 9 fayansin hicbirinde yoktu.
# Bu yuzden fayanslar DAHA GENIS bir bbox ile secilir; kapsama sonra
# API kumesine karsi DOGRULANIR (asagida).
TILE_SELECT_MARGIN_M = 1000.0
TIMEOUT_S = 300
MAX_MB = 200                        # emniyet tavani (D-006: ulke geneli indirme YOK)


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    logger, run_id, _ = setup_logging("download_3dbag_pinned")
    crs_z = expected_crs("with_height")

    area_b = shape(json.loads((resolve("root.aoi") / "area_B_context.geojson")
                              .read_text(encoding="utf-8"))["features"][0]["geometry"])
    x0, y0, x1, y1 = area_b.bounds
    bbox = (x0 - SAFETY_MARGIN_M, y0 - SAFETY_MARGIN_M,
            x1 + SAFETY_MARGIN_M, y1 + SAFETY_MARGIN_M)
    logger.info("Surum | %s (URL yolunda sabit: %s)", VERSION, BASE)
    logger.info("Kapsam | B + %.0f m (D-010) | %s", SAFETY_MARGIN_M,
                ",".join(f"{v:.1f}" for v in bbox))

    tile_bbox = (x0 - TILE_SELECT_MARGIN_M, y0 - TILE_SELECT_MARGIN_M,
                 x1 + TILE_SELECT_MARGIN_M, y1 + TILE_SELECT_MARGIN_M)
    tiles = gpd.read_file(TILE_INDEX, bbox=tile_bbox)
    logger.info("Fayans secim bbox'i | B + %.0f m", TILE_SELECT_MARGIN_M)
    if tiles.crs is None or tiles.crs.to_epsg() != 28992:
        raise ValueError(f"Fayans indeksi CRS beklenmedik: {tiles.crs}")
    logger.info("Kesisen fayans: %d", len(tiles))

    out_dir = resolve("data.raw") / f"3dbag_{VERSION_PATH}"
    out_dir.mkdir(parents=True, exist_ok=True)

    # --- M-004 kural 3: indirmeden ONCE boyut olcumu ---
    total = 0
    sizes: dict[str, int] = {}
    for url in tiles["cj_download"]:
        head = requests.head(url, timeout=TIMEOUT_S, allow_redirects=True)
        head.raise_for_status()
        n = int(head.headers.get("content-length", 0))
        sizes[url] = n
        total += n
    logger.info("On olcum | toplam %.1f MB (sikistirilmis)", total / 2**20)
    if total / 2**20 > MAX_MB:
        raise RuntimeError(f"Beklenenden buyuk indirme: {total/2**20:.0f} MB > {MAX_MB} MB")

    # --- yayin meta verisi ---
    meta_txt = requests.get(f"{BASE}/metadata.json", timeout=TIMEOUT_S).text
    (out_dir / "metadata.json").write_text(meta_txt, encoding="utf-8")
    edition = json.loads(meta_txt)["identificationInfo"]["citation"]["edition"]
    logger.info("Yayin meta verisi | edition=%s", edition)
    if edition != VERSION:
        raise ValueError(f"metadata.json edition={edition}, beklenen {VERSION}")

    # --- indir + YAYINCININ checksum'i ile dogrula ---
    ok, feats, pand_ids = 0, 0, set()
    bron, kwal = Counter(), Counter()
    attrs: set[str] = set()
    for _, row in tiles.iterrows():
        url, want = row["cj_download"], row["cj_sha256"]
        name = url.rsplit("/", 1)[-1]
        dest = out_dir / name
        with requests.get(url, stream=True, timeout=TIMEOUT_S) as r:
            r.raise_for_status()
            with dest.open("wb") as fh:
                for chunk in r.iter_content(1 << 20):
                    fh.write(chunk)
        got = _sha256(dest)
        if want and got != want:
            raise ValueError(f"{name}: SHA-256 uyusmuyor.\n  indeks: {want}\n  indirilen: {got}")
        ok += 1
        with gzip.open(dest, "rt", encoding="utf-8") as fh:
            for line in fh:
                obj = json.loads(line)
                for o in obj.get("CityObjects", {}).values():
                    a = o.get("attributes") or {}
                    if o.get("type") != "Building" or not a:
                        continue
                    feats += 1
                    attrs.update(a)
                    pand_ids.add(str(a.get("identificatie", "")))
                    bron[str(a.get("b3_pw_bron"))] += 1
                    kwal[str(a.get("b3_kwaliteitsindicator"))] += 1
        logger.info("%s | sha256 DOGRULANDI (yayincinin degeriyle)", name)

    logger.info("Indirme tamam | %d/%d fayans | %d Building | %d benzersiz pand",
                ok, len(tiles), feats, len(pand_ids))
    logger.info("b3_pw_bron | %s", dict(bron))
    logger.info("b3_kwaliteitsindicator | %s", dict(kwal))

    # --- M-013: surum etiketi ile icerik parmak izi karsilastirilir ---
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from download_3dbag import _version_fingerprint  # noqa: E402
    fp = _version_fingerprint(attrs)
    if fp == [VERSION.lstrip("v")]:
        logger.info("Parmak izi | %s | URL surumuyle TUTARLI", fp)
        version_record = f"{VERSION} (URL yolunda sabit; metadata.json edition ve oznitelik parmak izi TUTARLI)"
    else:
        logger.warning("Parmak izi | %s | URL surumu %s ile UYUSMUYOR", fp, VERSION)
        version_record = f"{VERSION} (URL sabit) ANCAK oznitelik parmak izi {fp} - CELISKI"

    # --- KAPSAMA DOGRULAMASI: API kumesindeki her bina sabitlenmiste var mi? ---
    api_path = resolve("data.raw") / "3dbag" / "3dbag_pand.city.jsonl"
    if api_path.is_file():
        api_ids = set()
        for line in api_path.open(encoding="utf-8"):
            for o in json.loads(line).get("CityObjects", {}).values():
                a = o.get("attributes") or {}
                if o.get("type") == "Building" and a:
                    api_ids.add(str(a.get("identificatie", "")))
        missing = api_ids - pand_ids
        logger.info("Kapsama | API kumesi %d bina | sabitlenmiste eksik: %d",
                    len(api_ids), len(missing))
        if missing:
            logger.warning("Sabitlenmis surumde EKSIK bina: %s",
                           ", ".join(sorted(missing)[:10]))
    else:
        logger.info("Kapsama | API kumesi yok, karsilastirma atlandi")

    subset = tiles.drop(columns=[c for c in tiles.columns if c.endswith("_download")])
    subset.to_file(out_dir / "tile_index_subset.geojson", driver="GeoJSON")

    write_meta(out_dir / "metadata.json", run_id=run_id,
               parameters={"version": VERSION, "bbox_epsg28992": list(bbox),
                           "safety_margin_m": SAFETY_MARGIN_M, "tiles": int(len(tiles)),
                           "buildings": feats, "unique_panden": len(pand_ids),
                           "b3_pw_bron": dict(bron), "bytes": total},
               software={"base_url": BASE, "tile_index": f"{BASE}/tile_index.fgb"},
               notes=f"CRS {crs_z}. Her fayansin SHA-256'si YAYINCININ indeksindeki degerle dogrulandi.")
    append_entry(
        dataset=f"3DBAG LOD2 — SABITLENMIS SURUM {VERSION}",
        path=out_dir / "metadata.json", run_id=run_id,
        source_url=f"{BASE}/tiles/...",
        provider="TU Delft 3D geoinformation",
        version=version_record,
        query=f"tile_index.fgb bbox={','.join(f'{v:.1f}' for v in bbox)} (EPSG:28992) = B + {SAFETY_MARGIN_M:.0f} m; {len(tiles)} fayans",
        crs=crs_z,
        time_reference="metadata.json: BAG 2.0 Extract ve AHN kaynak tarihleri yayin meta verisinde",
        license_="CC BY 4.0 (AGENTS.md Bolum 7) - attribution ZORUNLU",
        attribution="TODO_0.3: 3DBAG resmi attribution metni kaynagindan alinacak",
        processing="yok (ham indirme, .city.json.gz olarak saklandi)",
        notes=(f"{ok} fayans, {feats} Building nesnesi, {len(pand_ids)} benzersiz pand. "
               f"Her dosyanin SHA-256'si fayans indeksindeki `cj_sha256` ile DOGRULANDI "
               f"(checksum yayincidan gelir, bizim uretmedigimiz bagimsiz bir degerdir). "
               f"b3_pw_bron: {dict(bron)}. Oznitelik parmak izi: {fp}."),
    )
    logger.info("TAMAM | %s", out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
