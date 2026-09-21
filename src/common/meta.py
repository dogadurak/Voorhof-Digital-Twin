""".meta.json yazici — her analiz ciktisinin yanina tekrarlanabilirlik kaydi.

AGENTS.md Bolum 8:
  "Her analiz ciktisinin yanina .meta.json yazilir: run_id, git_commit,
   girdi dosyalari + checksum, parametreler, yazilim surumleri, calistirma
   zamani (UTC), varsa random_seed."
  "Rastgelelik iceren her islemde seed sabitlenir ve .meta.json'a yazilir.
   Ayni girdiyle iki calistirma ayni sonucu vermek zorundadir."
"""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import REPO_ROOT

CHUNK_SIZE = 1024 * 1024  # 1 MiB — AHN LAZ dosyalari GB mertebesinde olabilir


def sha256(path: str | Path) -> str:
    """Bir dosyanin SHA-256 checksum'ini hesaplar.

    Girdi : path — dosya yolu
    Cikti : str — 64 karakterlik onaltilik ozet
    Birim : yok

    Bolum 12.7: her harici veri icin checksum DATA_LOG.md'ye yazilir.
    Buyuk dosyalar parca parca okunur, bellege tumuyle alinmaz.
    """
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(CHUNK_SIZE), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_commit() -> str:
    """Calisan kodun git commit hash'ini dondurur.

    Cikti : str — kisa hash, calisma agaci kirliyse "<hash>-dirty",
                  git yoksa "UNKNOWN"

    "-dirty" eki onemlidir: commit edilmemis kodla uretilmis bir cikti
    tekrarlanabilir degildir ve rapor bunu gizlememelidir.
    """
    try:
        head = subprocess.run(
            ["git", "-C", str(REPO_ROOT), "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()

        dirty = subprocess.run(
            ["git", "-C", str(REPO_ROOT), "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()

        return f"{head}-dirty" if dirty else head
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "UNKNOWN"


def utc_now() -> str:
    """Su anki UTC zamanini ISO 8601 olarak dondurur (Bolum 12.1)."""
    return datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_meta(
    output_path: str | Path,
    run_id: str,
    inputs: list[str | Path] | None = None,
    parameters: dict[str, Any] | None = None,
    software: dict[str, str] | None = None,
    random_seed: int | None = None,
    notes: str | None = None,
) -> Path:
    """Bir cikti dosyasinin yanina <cikti>.meta.json yazar.

    Girdi : output_path — uretilen cikti dosyasi
            run_id      — setup_logging'den gelen calistirma kimligi
            inputs      — girdi dosyalari; her biri icin checksum hesaplanir
            parameters  — kullanilan parametreler (birimleriyle adlandirilmis)
            software    — {"gdal": "3.9.2", ...} gibi surum sozlugu
            random_seed — rastgelelik varsa SABITLENMIS seed; yoksa None
            notes       — serbest not (ornek: uygulanan CRS donusumu)
    Cikti : Path — yazilan .meta.json dosyasinin yolu

    Rastgelelik iceren bir islemde random_seed None birakilirsa ValueError
    firlatilir: seedsiz rastgelelik tekrarlanabilirligi bozar.
    """
    output_path = Path(output_path)

    input_records: list[dict[str, Any]] = []
    for item in inputs or []:
        item_path = Path(item)
        record: dict[str, Any] = {"path": str(_relative(item_path))}
        if item_path.is_file():
            record["sha256"] = sha256(item_path)
            record["size_bytes"] = item_path.stat().st_size
        else:
            record["sha256"] = None
            record["note"] = "dosya bulunamadi — checksum hesaplanamadi"
        input_records.append(record)

    meta: dict[str, Any] = {
        "run_id": run_id,
        "git_commit": git_commit(),
        "created_utc": utc_now(),
        "output": {"path": str(_relative(output_path))},
        "inputs": input_records,
        "parameters": parameters or {},
        "software": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            **(software or {}),
        },
        "random_seed": random_seed,
        "notes": notes,
    }

    if output_path.is_file():
        meta["output"]["sha256"] = sha256(output_path)
        meta["output"]["size_bytes"] = output_path.stat().st_size

    meta_path = output_path.with_suffix(output_path.suffix + ".meta.json")
    meta_path.parent.mkdir(parents=True, exist_ok=True)
    with meta_path.open("w", encoding="utf-8") as handle:
        json.dump(meta, handle, indent=2, ensure_ascii=False)
        handle.write("\n")

    return meta_path


def _relative(path: Path) -> Path:
    """Yolu mumkunse depo kokune gore goreli yapar.

    Mutlak makine yollari .meta.json'a yazilirsa kayit baska makinede
    anlamsizlasir; goreli yol tasinabilir kalir.
    """
    try:
        return path.resolve().relative_to(REPO_ROOT)
    except ValueError:
        return path
