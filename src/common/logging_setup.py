"""Logging kurulumu — her script bunu cagirir, print() kullanmaz.

AGENTS.md Bolum 8:
  "print() yerine logging modulu. Log hem terminale hem data/logs/*.log'a yazilir.
   DATA_LOG.md insan tarafindan okunan kayittir, makine logu oraya karismaz."

Bolum 13.1: her calistirma bir run_id tasir (RUN-YYYY-MM-DD-NNN) ve bu id hem
loga hem .meta.json'a hem asama raporuna yazilir.
"""

from __future__ import annotations

import logging
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from .config import resolve

_RUN_ID_PATTERN = re.compile(r"^RUN-\d{4}-\d{2}-\d{2}-(\d{3})$")

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"  # UTC — Bolum 12.1: depolamada UTC esastir


class _UtcFormatter(logging.Formatter):
    """Zaman damgasini yerel saat degil UTC yazan formatlayici.

    Bolum 14.6 "Zaman dilimi" hata sinifi: log zamani yerel saat olursa KNMI (UTC)
    ve EPW (yerel standart saat) karsilastirmalarinda iz surmek imkansizlasir.
    """

    converter = staticmethod(lambda ts: datetime.fromtimestamp(ts, tz=timezone.utc).timetuple())


def generate_run_id(now: datetime | None = None) -> str:
    """Gunun bir sonraki sira numarasini alarak run_id uretir.

    Girdi : now — UTC zaman (test icin enjekte edilebilir). None ise su an.
    Cikti : str — "RUN-2026-09-21-001" bicimli calistirma kimligi
    Birim : yok

    Sira numarasi data/logs/ icindeki ayni gune ait loglara bakilarak bulunur,
    boylece iki calistirma ayni id'yi almaz.
    """
    now = now or datetime.now(tz=timezone.utc)
    day = now.strftime("%Y-%m-%d")
    log_dir = resolve("data.logs")

    highest = 0
    if log_dir.is_dir():
        for entry in log_dir.glob(f"RUN-{day}-*.log"):
            match = _RUN_ID_PATTERN.match(entry.stem)
            if match:
                highest = max(highest, int(match.group(1)))

    return f"RUN-{day}-{highest + 1:03d}"


def setup_logging(
    name: str,
    run_id: str | None = None,
    level: int = logging.INFO,
) -> tuple[logging.Logger, str, Path]:
    """Logger'i iki hedefe birden baglar: terminal ve data/logs/<run_id>.log.

    Girdi : name   — cagiran scriptin adi (ornek "download_bag")
            run_id — verilmezse otomatik uretilir
            level  — logging seviyesi (varsayilan INFO)
    Cikti : (logger, run_id, log_file_path)
    Birim : yok

    Asama 0.1 kabul kriteri 0.1-C bu fonksiyonun IKI hedefe birden yazmasiyla
    olculur (log_sinks_working == 2).
    """
    run_id = run_id or generate_run_id()

    log_dir = resolve("data.logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"{run_id}.log"

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False
    logger.handlers.clear()  # tekrar cagrilirsa log satirlari cogalmasin

    formatter = _UtcFormatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    # Terminal akisi UTF-8'e zorlanir (MISTAKES.md M-006).
    # Windows konsolu varsayilan olarak cp1254 kullanir ve kodlayamadigi bir
    # karakterle karsilasinca SATIRI HIC YAZMAZ — hata log'a degil stderr'e
    # dusen bir "Logging error" olarak gider. Bir dogrulama satirinin sessizce
    # kaybolmasi, bu projede kabul edilemez bir hata sinifidir.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass  # yeniden yapilandirilamayan akislar icin asagidaki errors= yeterli

    stream_handler = logging.StreamHandler(stream=sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    file_handler = logging.FileHandler(log_file, encoding="utf-8", errors="replace")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    logger.info("run_id=%s script=%s log=%s", run_id, name, log_file.name)

    # PROJ oz-testi (MISTAKES.md M-003, tekrar 2026-09-22). Her calistirmada
    # FIILEN bir donusum yapilir ve sonuc loglanir. Konsolda pyproj'un
    # "unable to set PROJ database path" uyarisi gorulurse, bu satir onun
    # duzeltilip duzeltilmedigini soyler. Basarisizlik RuntimeError'dur.
    from .proj_env import assert_proj_works
    pj = assert_proj_works()
    logger.info("PROJ dogrulandi | PROJ %s | veri dizini %s | test noktasi geri "
                "donus hatasi %.1e m", pj["proj_version"], pj["data_dir"],
                pj["roundtrip_error_m"])
    return logger, run_id, log_file


def log_crs(logger: logging.Logger, source: str, found_crs: str, expected: str) -> None:
    """Okunan bir katmanin CRS'ini loglar ve beklenenle karsilastirir.

    Girdi : source     — dosya adi veya katman adi
            found_crs  — dosyadan okunan CRS (ornek "EPSG:28992")
            expected   — config/units.yml'den beklenen CRS
    Cikti : None
    Hata  : uyusmazsa ValueError firlatir

    Bolum 14.6 "CRS / yukseklik datumu" onleyici davranisi:
    "Her okumada CRS logla, beklenenle karsilastir, uyusmazsa hata firlat."
    Sessiz 1-2 m kayma bu kontrol olmadan fark edilmez.
    """
    logger.info("CRS kontrol | kaynak=%s | okunan=%s | beklenen=%s", source, found_crs, expected)
    if found_crs != expected:
        raise ValueError(
            f"CRS uyusmazligi: {source} icin {expected} bekleniyordu, {found_crs} bulundu. "
            f"Donusum acikca yapilmadan devam edilmez (AGENTS.md Bolum 1, kural 6)."
        )


def log_rowcount(logger: logging.Logger, label: str, before: int, after: int) -> None:
    """Bir join/filtre isleminin oncesi ve sonrasi satir sayisini loglar.

    Girdi : label  — islemin adi
            before — islem oncesi satir sayisi
            after  — islem sonrasi satir sayisi
    Cikti : None

    Bolum 14.6 "Sessiz veri kaybi" onleyici davranisi:
    "Her join oncesi/sonrasi satir sayisini logla."
    """
    delta = after - before
    logger.info("Satir sayimi | %s | oncesi=%d sonrasi=%d fark=%+d", label, before, after, delta)
    if delta < 0:
        logger.warning("%s isleminde %d kayit DUSTU — nedeni aciklanmali.", label, -delta)
