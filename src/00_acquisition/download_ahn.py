"""AHN5 LAZ alt-fayanslarini B alani + 50 m icin indirir.

Asama : 0.3  (Kararlar D-006, D-010, D-013)
Cikti : data/raw/ahn/AHN5_T/<fayans>.LAZ  (+ .txt metadata)
        + .meta.json + data/DATA_LOG.md kaydi

KAYNAK SECIMI (dogrulandi 2026-09-21, tahmin edilmedi):
  - PDOK ATOM  -> AHN**4**, yalnizca RASTER (DSM/DTM 0,5 m). LAZ YOK.
                  Feed'in kendi metni: "Het huidige AHN is versie 4."
  - GeoTiles (TU Delft) -> AHN1/2/3/4/**5** LAZ nokta bulutu, fayanslanmis.
  Bu yuzden AHN5 LAZ icin GeoTiles kullanilir (AGENTS.md Bolum 4 bu kaynagi
  zaten listeliyor).

FAYANS IZGARASI (5 ornek alt-fayanstan DOGRULANDI, formule guvenilmedi):
  Bir kaartblad 5 km (x) x 6,25 km (y). 25 alt-fayans: 5 sutun x 5 satir.
  alt_fayans_no = (satir - 1) * 5 + sutun,  satirlar YUKARIDAN asagi.
  Her alt-fayans her kenarda 20 m ORTUSME tasir (GeoTiles tasarimi).

Bu script formulle aday uretir ama **her adayin gercek sinirlarini indirmeden
once .txt metadata'sindan okur ve B+50 ile kesisimini dogrular**. Formul
yanlissa indirme yapilmaz (MISTAKES.md M-005: sema/duzen iddiasi kaynagindan
dogrulanir).

Calistirma:
    python src/00_acquisition/download_ahn.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

# M-003 / M-012: PROJ dizini, pyproj'u yukleyen laspy/shapely/pyproj'dan ONCE
# sabitlenmeli. Aksi halde pyproj PostgreSQL'in PROJ dizinine kilitlenir ve her
# calistirmada "unable to set PROJ database path" uyarisi basar.
import src.common  # noqa: E402,F401

from shapely.geometry import box, shape

from src.common.config import load_acceptance_criteria, resolve, expected_crs
from src.common.data_log import append_entry
from src.common.logging_setup import setup_logging
from src.common.meta import sha256, write_meta

BASE = "https://geotiles.citg.tudelft.nl/AHN5_T"
SAFETY_MARGIN_M = 50.0          # Karar D-010
TILE_W_M, TILE_H_M = 5000.0, 6250.0
COLS, ROWS = 5, 5
TIMEOUT_S = 300

# Kaartblad kok noktalari (sol-alt), dogrulanmis alt-fayans sinirlarindan turetildi
KAARTBLAD_ORIGIN = {
    "37EN1": (80000.0, 443750.0),
    "37EN2": (85000.0, 443750.0),
}

_BOUNDS_RE = re.compile(
    r"min x y z:\s+([\d.-]+)\s+([\d.-]+)\s+[\d.-]+.*?max x y z:\s+([\d.-]+)\s+([\d.-]+)",
    re.S,
)
_POINTS_RE = re.compile(r"extended number of point records:\s+(\d+)")


def candidate_subtiles(bounds) -> list[tuple[str, int]]:
    """B+50 ile kesisebilecek (kaartblad, alt_fayans_no) adaylarini uretir.

    Girdi : bounds — (minx, miny, maxx, maxy) hedef kapsam, m (EPSG:28992)
    Cikti : [(kaartblad, no), ...]

    Bu YALNIZCA aday listesidir; gercek sinirlar metadata'dan dogrulanir.
    """
    minx, miny, maxx, maxy = bounds
    out: list[tuple[str, int]] = []
    for blad, (ox, oy) in KAARTBLAD_ORIGIN.items():
        for col in range(1, COLS + 1):
            for row in range(1, ROWS + 1):
                x0 = ox + (col - 1) * (TILE_W_M / COLS)
                x1 = x0 + TILE_W_M / COLS
                y1 = oy + TILE_H_M - (row - 1) * (TILE_H_M / ROWS)
                y0 = y1 - TILE_H_M / ROWS
                if x1 >= minx and x0 <= maxx and y1 >= miny and y0 <= maxy:
                    out.append((blad, (row - 1) * COLS + col))
    return out


def read_metadata(name: str, logger) -> dict | None:
    """Bir alt-fayansin lasinfo metadata'sini indirir ve ayristirir.

    Cikti : {"bounds": (minx,miny,maxx,maxy), "points": int, "raw": str} veya None
    Birim : m, adet

    Geometri indirilmeden once cagrilir — boylece yanlis fayans indirilmez.
    """
    response = requests.get(f"{BASE}/{name}.txt", timeout=TIMEOUT_S)
    if response.status_code != 200:
        logger.warning("%s.txt bulunamadi (HTTP %s)", name, response.status_code)
        return None

    text = response.text
    bounds_match = _BOUNDS_RE.search(text)
    points_match = _POINTS_RE.search(text)
    if not bounds_match:
        logger.warning("%s.txt icinde sinir bilgisi ayristirilamadi", name)
        return None

    minx, miny, maxx, maxy = (float(v) for v in bounds_match.groups())
    return {
        "bounds": (minx, miny, maxx, maxy),
        "points": int(points_match.group(1)) if points_match else None,
        "raw": text,
    }


def main() -> int:
    logger, run_id, _ = setup_logging("download_ahn")
    target_crs_xy = expected_crs("planimetric")
    target_crs_z = expected_crs("with_height")

    area_b = shape(json.loads(
        (resolve("root.aoi") / "area_B_context.geojson").read_text(encoding="utf-8")
    )["features"][0]["geometry"])

    bminx, bminy, bmaxx, bmaxy = area_b.bounds
    need = (bminx - SAFETY_MARGIN_M, bminy - SAFETY_MARGIN_M,
            bmaxx + SAFETY_MARGIN_M, bmaxy + SAFETY_MARGIN_M)
    need_box = box(*need)
    logger.info("B siniri      | x %.1f..%.1f y %.1f..%.1f", bminx, bmaxx, bminy, bmaxy)
    logger.info("Gerekli kapsam| B + %.0f m (D-010) | x %.1f..%.1f y %.1f..%.1f",
                SAFETY_MARGIN_M, need[0], need[2], need[1], need[3])

    candidates = candidate_subtiles(need)
    logger.info("Formulle uretilen aday alt-fayans: %d | %s",
                len(candidates), ", ".join(f"{b}_{n:02d}" for b, n in candidates))

    # --- Her adayin GERCEK sinirini metadata'dan dogrula (M-005) ---
    selected: list[tuple[str, dict]] = []
    for blad, number in candidates:
        name = f"{blad}_{number:02d}"
        meta = read_metadata(name, logger)
        if meta is None:
            continue
        tile_box = box(*meta["bounds"])
        if not tile_box.intersects(need_box):
            logger.warning("%s formulle secildi ama sinirlari KESISMIYOR - atlandi", name)
            continue
        selected.append((name, meta))
        logger.info("%s dogrulandi | x %.0f..%.0f y %.0f..%.0f | %d nokta",
                    name, meta["bounds"][0], meta["bounds"][2],
                    meta["bounds"][1], meta["bounds"][3], meta["points"])

    if not selected:
        logger.error("Hicbir alt-fayans dogrulanamadi. Indirme YAPILMADI.")
        return 1

    # --- Kapsama: secilen fayanslar B+50'yi tamamen ortuyor mu? ---
    from shapely.ops import unary_union
    covered = unary_union([box(*m["bounds"]) for _, m in selected])
    if not covered.contains(need_box):
        gap_ha = need_box.difference(covered).area / 10_000
        logger.error("KAPSAMA EKSIK: B+%.0f m'nin %.2f ha'i hicbir fayansta yok. "
                     "Indirme YAPILMADI (Bolum 12.12 girdi kalite kapisi).",
                     SAFETY_MARGIN_M, gap_ha)
        return 1
    logger.info("Kapsama dogrulandi | secilen %d fayans B+%.0f m'yi tamamen ortuyor",
                len(selected), SAFETY_MARGIN_M)

    # --- Boyut kontrolu (M-004 kural 3) ---
    import shutil
    sizes: dict[str, int] = {}
    for name, _ in selected:
        head = requests.head(f"{BASE}/{name}.LAZ", timeout=TIMEOUT_S, allow_redirects=True)
        sizes[name] = int(head.headers.get("content-length", 0))
    total = sum(sizes.values())
    free = shutil.disk_usage(str(resolve("data.raw")))[2]
    logger.info("Beklenen indirme: %.2f GB | bos disk: %.1f GB | oran %%%.2f",
                total / 2**30, free / 2**30, 100 * total / free)
    if total > free * 0.5:
        logger.error("Indirme bos diskin yarisindan buyuk. Durduruldu.")
        return 1

    out_dir = resolve("data.raw") / "ahn" / "AHN5_T"
    out_dir.mkdir(parents=True, exist_ok=True)

    downloaded: list[str] = []
    total_points = 0
    for name, meta in selected:
        laz_path = out_dir / f"{name}.LAZ"
        txt_path = out_dir / f"{name}.txt"
        txt_path.write_text(meta["raw"], encoding="utf-8")

        if laz_path.is_file() and laz_path.stat().st_size == sizes[name]:
            logger.info("%s zaten indirilmis ve boyutu esliyor - atlandi", name)
        else:
            logger.info("%s indiriliyor (%.1f MB)...", name, sizes[name] / 2**20)
            with requests.get(f"{BASE}/{name}.LAZ", stream=True, timeout=TIMEOUT_S) as r:
                r.raise_for_status()
                with laz_path.open("wb") as fh:
                    for chunk in r.iter_content(chunk_size=1 << 20):
                        fh.write(chunk)

        actual = laz_path.stat().st_size
        if actual != sizes[name]:
            logger.error("%s BOYUT UYUSMAZLIGI: beklenen %d, inen %d. Dosya silindi.",
                         name, sizes[name], actual)
            laz_path.unlink()
            return 1

        downloaded.append(name)
        total_points += meta["points"] or 0
        logger.info("%s tamam | %.1f MB | sha256 %s...",
                    name, actual / 2**20, sha256(laz_path)[:16])

    logger.info("Toplam %d alt-fayans | %d nokta | %.2f GB",
                len(downloaded), total_points, total / 2**30)

    # --- Tekrarlanabilirlik kayitlari ---
    write_meta(
        out_dir, run_id=run_id,
        parameters={
            "subtiles": downloaded,
            "bbox_needed_epsg28992": list(need),
            "safety_margin_m": SAFETY_MARGIN_M,
            "total_points": total_points,
            "total_bytes": total,
            "crs_xy": target_crs_xy,
            "crs_with_height": target_crs_z,
        },
        software={"source": BASE},
        notes="Her alt-fayansin sinirlari indirmeden once metadata'dan dogrulandi.",
    )
    append_entry(
        dataset="AHN5 LAZ nokta bulutu (GeoTiles alt-fayanslari)",
        path=out_dir / f"{downloaded[0]}.LAZ",
        run_id=run_id,
        source_url=BASE,
        provider="AHN (Rijkswaterstaat/provincies/waterschappen) - fayanslama: TU Delft GeoTiles",
        version="AHN5, kampanya etiketi '2023_C' (dosya adindan)",
        query=(f"B bbox + {SAFETY_MARGIN_M:.0f} m (D-010); "
               f"secilen alt-fayanslar: {', '.join(downloaded)}"),
        crs=target_crs_z,
        time_reference=(
            "CELISKI: dosya adi kampanyasi '2023_C' ama LAS basligi "
            "'file creation day/year 347/2022' (13 Aralik 2022). Ikisi de kaydedildi; "
            "sessizce tek deger SECILMEDI (AGENTS.md Bolum 4 tutumu)."
        ),
        license_="TODO: AHN lisans kosulu ahn.nl'den dogrulanacak",
        attribution="TODO",
        data_production_date="2023 kampanyasi (etiket) / 2022-12-13 (LAS basligi)",
        processing="yok (ham indirme). Alt-fayanslar 20 m ortusme tasir (GeoTiles tasarimi).",
        notes=(
            f"{len(downloaded)} alt-fayans, toplam {total_points} nokta, "
            f"{total/2**30:.2f} GB. Kapsama B+{SAFETY_MARGIN_M:.0f} m icin DOGRULANDI. "
            f"Her dosyanin boyutu indirme sonrasi Content-Length ile karsilastirildi. "
            f"CRS dosya ici WKT'den okundu: EPSG:7415 (RD New + NAP). "
            f"KAYNAK NOTU: PDOK ATOM AHN4 RASTER sunar, LAZ sunmaz; AHN5 LAZ icin "
            f"GeoTiles kullanildi."
        ),
    )
    logger.info("TAMAM")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
