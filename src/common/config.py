"""Config okuyucu — tum yol, birim ve kabul esigi erisimi BURADAN gecer.

AGENTS.md Bolum 8  : "Yollar config/paths.yml'den okunur, koda gomulmez."
AGENTS.md Bolum 13.2-1: "Esigi koddan degil config dosyasindan oku; esigi kodda
                         sabitlemek yasaktir."

Bu modul o iki kurali tek noktada uygulanabilir kilar. Hicbir script kendi
basina yml acmaz, hicbir script kendi icinde sayisal esik tutmaz.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

# --- Depo koku -------------------------------------------------------------
# Bu dosya <repo>/src/common/config.py konumunda. Iki ust dizin depo kokudur.
REPO_ROOT: Path = Path(__file__).resolve().parents[2]

CONFIG_DIR: Path = REPO_ROOT / "config"

_CONFIG_FILES: dict[str, str] = {
    "paths": "paths.yml",
    "units": "units.yml",
    "acceptance_criteria": "acceptance_criteria.yml",
}

# Esigi henuz onaylanmamis kriterlerin isareti (Karar D-003).
PENDING_THRESHOLD = "TODO_ONAY_BEKLIYOR"


class ConfigError(RuntimeError):
    """Config dosyasi okunamadi, bozuk ya da beklenen anahtar eksik."""


class PendingThresholdError(ConfigError):
    """Esik henuz kullanici tarafindan onaylanmamis (TODO_ONAY_BEKLIYOR).

    Bu hata BILEREK firlatilir: onaylanmamis esikle olcum yapip PASS/FAIL
    beyan etmek AGENTS.md Bolum 12.11'in ihlalidir.
    """


@lru_cache(maxsize=None)
def _load_yaml(name: str) -> dict[str, Any]:
    """Adi verilen config dosyasini okur ve sozluk olarak dondurur.

    Girdi : name — "paths", "units" veya "acceptance_criteria"
    Cikti : dict — dosyanin ayristirilmis icerigi
    Birim : yok (yapilandirma verisi)
    """
    if name not in _CONFIG_FILES:
        raise ConfigError(
            f"Bilinmeyen config adi: {name!r}. Gecerli olanlar: {sorted(_CONFIG_FILES)}"
        )

    path = CONFIG_DIR / _CONFIG_FILES[name]
    if not path.is_file():
        raise ConfigError(f"Config dosyasi bulunamadi: {path}")

    try:
        with path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
    except yaml.YAMLError as exc:
        raise ConfigError(f"{path} ayristirilamadi: {exc}") from exc

    if not isinstance(data, dict):
        raise ConfigError(f"{path} bir sozluk dondurmedi (bos veya bozuk olabilir).")

    return data


def load_paths() -> dict[str, Any]:
    """config/paths.yml icerigini dondurur."""
    return _load_yaml("paths")


def load_units() -> dict[str, Any]:
    """config/units.yml icerigini dondurur."""
    return _load_yaml("units")


def load_acceptance_criteria() -> dict[str, Any]:
    """config/acceptance_criteria.yml icerigini dondurur.

    Bu dosya sonuctan ONCE kilitlenmistir (Bolum 12.2). Okunur, YAZILMAZ.
    """
    return _load_yaml("acceptance_criteria")


def load_all() -> dict[str, dict[str, Any]]:
    """Uc config dosyasini birden yukler.

    Asama 0.1 kabul kriteri 0.1-B bu fonksiyonun hatasiz donmesiyle olculur.

    Cikti: {"paths": {...}, "units": {...}, "acceptance_criteria": {...}}
    """
    return {name: _load_yaml(name) for name in _CONFIG_FILES}


def resolve(dotted_key: str) -> Path:
    """paths.yml icindeki noktali anahtari MUTLAK yola cevirir.

    Girdi : dotted_key — ornek "data.raw", "aoi.area_a", "reports.failed_buildings"
    Cikti : Path — depo kokune gore cozulmus mutlak yol
    Birim : yok

    Not: Yolun VAR OLDUGUNU garanti etmez; yalnizca cozer. Varlik kontrolu
    cagiranin sorumlulugundadir (ornek: AOI dosyalari Asama 0.2'de olusur).
    """
    node: Any = load_paths()
    for part in dotted_key.split("."):
        if not isinstance(node, dict) or part not in node:
            raise ConfigError(f"paths.yml icinde bulunamadi: {dotted_key!r}")
        node = node[part]

    if not isinstance(node, str):
        raise ConfigError(f"{dotted_key!r} bir yol dizgisi degil: {type(node).__name__}")

    return REPO_ROOT / node


def get_criterion(stage: str, criterion_id: str) -> dict[str, Any]:
    """Tek bir kabul kriterini dondurur.

    Girdi : stage        — "stage_0_1", "stage_1", "stage_3" ...
            criterion_id — "1-B", "3-C" ...
    Cikti : dict — kriterin tum alanlari (metric, comparator, threshold, status...)
    """
    criteria = load_acceptance_criteria().get(stage, {}).get("criteria", [])
    for item in criteria:
        if item.get("id") == criterion_id:
            return item
    raise ConfigError(f"Kabul kriteri bulunamadi: {stage} / {criterion_id}")


def get_threshold(stage: str, criterion_id: str) -> Any:
    """Bir kriterin sayisal esigini dondurur.

    Esik hala TODO_ONAY_BEKLIYOR ise PendingThresholdError firlatir — cunku
    onaylanmamis esikle PASS/FAIL beyan etmek yasaktir (Bolum 12.11, Karar D-003).

    Girdi : stage, criterion_id
    Cikti : esigin degeri (float / int / bool)
    Birim : kriterin kendi `unit` alaninda yazilidir (m, pct, ...)
    """
    criterion = get_criterion(stage, criterion_id)
    threshold = criterion.get("threshold")

    if threshold == PENDING_THRESHOLD or criterion.get("status") == PENDING_THRESHOLD:
        raise PendingThresholdError(
            f"{stage}/{criterion_id} esigi henuz onaylanmadi ({PENDING_THRESHOLD}). "
            f"Karar {criterion.get('decision_ref', 'D-003')} — kullanici onayi olmadan "
            f"bu kriterle PASS/FAIL beyan edilemez. "
            f"Engellenen is: {criterion.get('blocking_for', 'bilinmiyor')}"
        )

    return threshold


def expected_crs(kind: str = "planimetric") -> str:
    """units.yml'den beklenen CRS kodunu dondurur.

    Girdi : kind — "planimetric" (EPSG:28992), "with_height" (EPSG:7415)
                   veya "geographic" (EPSG:4326)
    Cikti : str — EPSG kodu

    Bolum 1 kural 6: CRS varsayilmaz. Her okumada bu deger ile karsilastirilir.
    """
    crs_block = load_units().get("crs", {})
    if kind not in crs_block:
        raise ConfigError(f"units.yml crs bloguna '{kind}' anahtari yok.")
    return str(crs_block[kind])


def env_secret(name: str) -> str:
    """Ortam degiskeninden bir API key/credential okur.

    Bolum 8: "API key / token / credential ASLA repoya yazilmaz."
    Deger yoksa acik hata verir — sessizce bos dizgiyle devam etmez.
    """
    value = os.environ.get(name)
    if not value:
        raise ConfigError(
            f"{name} ortam degiskeni tanimli degil. .env.example'i .env olarak "
            f"kopyalayip degeri oraya yazin. .env repoya GIRMEZ."
        )
    return value
