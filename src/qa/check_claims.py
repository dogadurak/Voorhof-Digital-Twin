"""Kaynaksiz dis-spesifikasyon sayilarini ve negatif varlik iddialarini bulur.

M-005 kok nedeni ("dogrulanmadan yazmak") dort kez tekrarladi. Son tekrar iki
yeni bicimdeydi (MISTAKES.md, 2026-09-27):
  (a) Bir sartname sayisi ("AHN5 sigma <= 3 cm") kaynagi gorulmeden config'e
      yazildi.
  (b) Negatif bir iddia ("hicbir AHN yayini AHN5 siniflandirmasini
      belgelemiyor") eksik aramanin sonucu olarak olgu gibi yazildi.

Iki kontrol:
  1. SERT (cikis kodu 1): config/acceptance_criteria.yml icinde bir DIS BELGEYE
     (bestek, ihale, spesifikasyon, kwaliteitsbeschrijving, norm, yonetmelik,
     ASHRAE, Bbl ...) atif yapan her blokta — blogun kendisinde, alt
     bloklarinda veya ebeveyninde — `source_verified_at` / `verified_at`
     alani var mi? Hatanin GERCEK bicimi budur: dis belgeye dayanan bir iddia,
     belge gorulmeden yazildi.
     (Ilk surum "her sayisal esikte gerekce alani" ariyordu; "0 bozuk dosya"
      gibi politika esiklerini de hata saydi — yanlis seyi olcuyordu.
      2026-09-27'de bu bicime daraltildi.)
  2. YUMUSAK (yalnizca listeler): .md/.yml metinlerinde negatif varlik
     kaliplari. Ayni paragrafta "aranan" / "bulunamadi" / "aranan kaynaklar"
     gecmiyorsa satir insan incelemesine listelenir (docs/manual_steps.md MS-2).
     Sezgiseldir; kesin karar okumayi gerektirir.

Calistirma:
    python src/qa/check_claims.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import src.common  # noqa: E402,F401

import yaml  # noqa: E402

from src.common.config import REPO_ROOT, resolve  # noqa: E402

EXTERNAL_DOC = re.compile(
    r"(?i)\b(bestek|besteksvoorwaarden|ihale|aanbesteding|spesifikasyon|specificati|"
    r"kwaliteitsbeschrijving|yonetmelik|yönetmelik|besluit|bbl\b|ashrae|nen \d|iso \d)")
VERIFIED_KEYS = {"source_verified_at", "verified_at"}

NEGATIVE_PATTERNS = [
    r"hi[cç]bir\b[^.\n]{0,80}\b(yok|belgelemiyor|vermiyor|kapsam[ıi]yor|yay[ıi]nlam[ıi]yor)",
    r"\bbelgelemiyor\b",
    r"\byay[ıi]nlanmam[ıi][sş]\b",
    r"\bmevcut de[gğ]il\b",
    # 2026-09-27: "resmi spesifikasyon YOKTUR" kalibini kacirdi -> eklendi
    r"(spesifikasyon|belge|kaynak|yay[ıi]n)[^.\n]{0,40}\byok(tur)?\b",
]
# Arama kaniti veya ACIK duzeltme isareti. "olcum"/"olculdu" BILEREK YOK:
# yanlis cikan iddia (AGENTS §5, 2026-09-21) tam da "OLCULDU" etiketiyle
# yaziliydi — o kelimeyi kanit saymak kontrolu kendi kor noktasina geri
# dusurur (olculdu 2026-09-27: ekleyince gercek pozitif listeden kayboldu).
SEARCH_EVIDENCE = re.compile(r"(?i)aranan|arand[ıi]|bulunamad[ıi]|okunamad[ıi]|searched|"
                             r"yanl[ıi][sş]|d[uü]zelt|~~")
SKIP_FILES = {"MISTAKES.md"}           # hata defteri eski iddialari ALINTILAR


def check_thresholds(cfg: dict | None = None) -> list[str]:
    """Dis belgeye atif yapip dogrulama tarihi tasimayan config bloklarini dondurur.

    Girdi : cfg — verilmezse config/acceptance_criteria.yml okunur (oz-sinama icin)
    """
    if cfg is None:
        cfg = yaml.safe_load(resolve("config.acceptance_criteria").read_text(encoding="utf-8"))
    bad: list[str] = []

    def has_verified(node) -> bool:
        if isinstance(node, dict):
            # Dogrulama tarihi VEYA acik "DOGRULANMADI" etiketi kabul edilir:
            # kural, dogrulanmamisligin GIZLENMEMESINI ister, yoklugunu degil.
            if VERIFIED_KEYS & set(node) or any(k.endswith("source_status") for k in node):
                return True
            return any(has_verified(v) for v in node.values())
        if isinstance(node, list):
            return any(has_verified(v) for v in node)
        return False

    def walk(node, path: str, parent) -> None:
        if isinstance(node, dict):
            own = " ".join(v for v in node.values() if isinstance(v, str))
            m = EXTERNAL_DOC.search(own)
            if m and not (has_verified(node) or (isinstance(parent, dict) and VERIFIED_KEYS & set(parent))):
                bad.append(f"{node.get('id') or path}: dis belgeye atif ('{m.group(0)}') "
                           f"ama source_verified_at / verified_at yok")
            for k, v in node.items():
                walk(v, f"{path}.{k}" if path else str(k), node)
        elif isinstance(node, list):
            for i, v in enumerate(node):
                walk(v, f"{path}[{i}]", parent)

    walk(cfg, "", None)
    return bad


def check_negative_claims() -> list[str]:
    """Kaynak/arama kaniti olmayan negatif varlik iddialarini listeler."""
    hits: list[str] = []
    files = [p for p in REPO_ROOT.rglob("*")
             if p.suffix in {".md", ".yml"} and p.name not in SKIP_FILES
             and not any(part in {"data", ".git", "tools"} for part in p.parts)]
    for f in sorted(files):
        text = f.read_text(encoding="utf-8", errors="ignore")
        for para in re.split(r"\n\s*\n", text):
            m = negative_hit(para)
            if m:
                line_no = text[:text.find(para)].count("\n") + 1
                snippet = re.sub(r"\s+", " ", para[max(0, m.start() - 60):m.end() + 60])
                hits.append(f"{f.relative_to(REPO_ROOT)}:{line_no}: …{snippet}…")
    return hits


def negative_hit(para: str) -> re.Match | None:
    """Bir paragrafta arama kaniti OLMAYAN negatif varlik iddiasi varsa eslesmeyi dondurur."""
    if SEARCH_EVIDENCE.search(para):
        return None
    for pat in NEGATIVE_PATTERNS:
        m = re.search(pat, para, re.I)
        if m:
            return m
    return None


# Oz-sinama fiksturleri. Arac sonuca bakilarak gevsetilirse (2026-09-27'de bir kez
# oldu: "olculdu" kanit listesine eklenince gercek pozitif kayboldu) bunlar kirmizi
# yanar. Fikstur SILMEK veya beklenen degeri cevirmek kontrolu gevsetmekle aynidir
# -> docs/reviewer_checklist.md J-1.
SELF_TEST_NEGATIVE = [
    # (paragraf, yakalanmali_mi)
    ("AHN5 icin resmi spesifikasyon yoktur.", True),
    ("OLCULDU 2026-09-21: kwaliteitsbeschrijving AHN5 icin hicbir spesifikasyon vermiyor.", True),
    ("Hicbir AHN yayini AHN5 siniflandirmasini belgelemiyor.", True),
    ("Aranan kaynaklar: ahn.nl, AHN4 bestek — bulunamadi; spesifikasyon yok.", False),
]
SELF_TEST_CONFIG = [
    ({"x": {"threshold": 5, "note": "bestek boyle diyor"}}, 1),
    ({"x": {"note": "bestek boyle diyor", "source_verified_at": "2026-09-27"}}, 0),
    ({"x": {"note": "bestek boyle diyor", "source_status": "DOGRULANMADI"}}, 0),
]


def self_test() -> list[str]:
    """Kontrollerin bilinen gercek hatalari HALA yakaladigini sinar. Bos liste = gecti."""
    fails = []
    for para, expect in SELF_TEST_NEGATIVE:
        if bool(negative_hit(para)) != expect:
            fails.append(f"negatif iddia: {'KACIRDI' if expect else 'YANLIS ALARM'} -> {para!r}")
    for cfg, expect in SELF_TEST_CONFIG:
        got = len(check_thresholds(cfg))
        if got != expect:
            fails.append(f"config: beklenen {expect} bulgu, cikan {got} -> {cfg!r}")
    return fails


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")   # T-1: Windows konsol kodlamasi
    st = self_test()
    print(f"[OZ-SINAMA] {len(SELF_TEST_NEGATIVE) + len(SELF_TEST_CONFIG)} fikstur, "
          f"{len(st)} basarisiz")
    for s in st:
        print("   ARAC HATASI:", s)
    if st:
        print("SONUC: FAIL (olcum araci bilinen hatalari yakalamiyor — sonuclarina guvenilmez)")
        return 2
    bad = check_thresholds()
    neg = check_negative_claims()
    print(f"[SERT] dogrulama tarihi olmayan dis-belge atfi: {len(bad)}")
    for b in bad:
        print("   HATA:", b)
    print(f"[YUMUSAK] arama kaniti olmayan negatif iddia adayi: {len(neg)} "
          f"(insan incelemesi — MS-2)")
    for h in neg:
        print("   ?", h[:240])
    print("SONUC:", "FAIL" if bad else "PASS", "(yumusak adaylar sonucu etkilemez)")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
