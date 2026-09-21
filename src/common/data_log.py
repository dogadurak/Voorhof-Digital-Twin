"""data/DATA_LOG.md yazici — Bolum 12.7'nin her alanini zorunlu kilar.

AGENTS.md Bolum 8: "DATA_LOG.md INSAN tarafindan okunan kayittir, makine logu oraya
karismaz." Makine loglari `data/logs/*.log` altindadir.

Bolum 12.7 her harici veri icin su alanlarin TAMAMINI istiyor:
kaynak URL, saglayici, veri seti adi, surum, veri uretim tarihi, yayin tarihi,
indirme tarihi, indirme yontemi/endpoint, sorgu parametreleri, CRS, zaman referansi,
lisans, attribution sarti, checksum (SHA-256), uygulanan islem gecmisi.

Bu modul alanlari **isimli parametre** haline getirir: bir alan unutulursa kayit
`TODO_DOLDURULACAK` ile isaretlenir ve eksikligi gorunur olur. Serbest metinle
yazilan kayitlarda alan atlamak sessizce mumkundur; burada degildir.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from .config import resolve
from .meta import sha256

MISSING = "TODO_DOLDURULACAK"

# Kayitlarin ekleneceği baslik. Sablon bolumu korunur.
_ANCHOR = "## Kayitlar"
_PLACEHOLDER = "*(Asama 0.3'e kadar bos)*"


def append_entry(
    dataset: str,
    path: str | Path,
    run_id: str,
    source_url: str,
    provider: str,
    version: str = MISSING,
    query: str = MISSING,
    crs: str = MISSING,
    time_reference: str = MISSING,
    license_: str = MISSING,
    attribution: str = MISSING,
    data_production_date: str = MISSING,
    publication_date: str = MISSING,
    processing: str = "yok (ham indirme, degistirilmedi)",
    notes: str = "",
) -> None:
    """DATA_LOG.md'ye Bolum 12.7 formatinda bir kayit ekler.

    Girdi : dataset  — veri seti adi
            path     — indirilen dosya (checksum ve boyut buradan olculur)
            run_id   — calistirma kimligi
            ...      — Bolum 12.7 alanlari
    Cikti : None (dosyaya yazar)
    Birim : dosya boyutu bytes

    Checksum ve boyut ELLE GECILMEZ, dosyadan hesaplanir — kayit ile dosyanin
    ayrisma ihtimali boylece ortadan kalkar.
    """
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"DATA_LOG kaydi icin dosya bulunamadi: {path}")

    log_path = resolve("data.data_log")
    downloaded_utc = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    try:
        rel = path.resolve().relative_to(resolve("root.data").parent).as_posix()
    except ValueError:
        rel = path.as_posix()

    entry = f"""
## {dataset}  ·  {downloaded_utc}

| Alan | Deger |
|---|---|
| dosya | `{rel}` |
| kaynak_url | {source_url} |
| saglayici | {provider} |
| surum | {version} |
| veri_uretim_tarihi | {data_production_date} |
| yayin_tarihi | {publication_date} |
| indirme_tarihi_utc | {downloaded_utc} |
| indirme_yontemi | WFS GetFeature (OGC Filter Encoding 2.0) |
| sorgu_parametreleri | {query} |
| crs | {crs} |
| zaman_referansi | {time_reference} |
| lisans | {license_} |
| attribution_sarti | {attribution} |
| sha256 | `{sha256(path)}` |
| dosya_boyutu_bytes | {path.stat().st_size} |
| run_id | {run_id} |
| uygulanan_islemler | {processing} |

{notes}

---
"""

    text = log_path.read_text(encoding="utf-8")

    if _PLACEHOLDER in text:
        text = text.replace(_PLACEHOLDER, entry.strip(), 1)
    elif _ANCHOR in text:
        head, _, tail = text.partition(_ANCHOR)
        text = head + _ANCHOR + "\n" + entry + tail.lstrip("\n")
    else:
        text += "\n" + entry

    log_path.write_text(text, encoding="utf-8")
