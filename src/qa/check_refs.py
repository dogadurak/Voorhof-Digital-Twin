"""Karar / bekleyen karar / hata kaydi atiflarinin cozulup cozulmedigini denetler.

Neden var (MISTAKES.md M-008 ve tekrari):
- M-008 (2026-09-21): config `decision_ref: D-015` diyordu, D-015 yoktu.
- Tekrar (2026-09-22): P-014'e bes dosyada atif yapildi, P-014 hic acilmamisti.
M-008'in otomatik kontrolu Asama 0.5'e ertelenmisti; ertelenen kontrol
yazilana kadar ayni hata tekrarlandi. Bolum 14.5-4 geregi simdi yazildi.
Asama 0.4/0.5'te `check_compliance.py` bu scripti cagiracaktir.

Denetlenenler:
  D-xxx -> DECISIONS.md icinde "## D-xxx" basligi
  P-xxx -> reports/PENDING_DECISIONS.md icinde tablo satiri veya baslik
  M-xxx -> MISTAKES.md icinde "## M-xxx" basligi
  DECISIONS.md "SONRAKI BOS ID" > var olan en buyuk D

Cikti : cozulmeyen her atif icin dosya:satir; cikis kodu 1 (varsa) / 0
Birim : yok

Calistirma:
    python src/qa/check_refs.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCAN_SUFFIXES = {".md", ".yml", ".yaml", ".py"}
SKIP_DIRS = {".git", "data", "__pycache__", ".claude"}
REF = re.compile(r"\b([DPM])-(\d{3})\b")


def _defined() -> dict[str, set[str]]:
    """Her kayit turu icin tanimli kimlikleri dondurur."""
    dec = (ROOT / "DECISIONS.md").read_text(encoding="utf-8")
    pen = (ROOT / "reports" / "PENDING_DECISIONS.md").read_text(encoding="utf-8")
    mis = (ROOT / "MISTAKES.md").read_text(encoding="utf-8")
    return {
        "D": set(re.findall(r"^## (D-\d{3})\b", dec, re.M)),
        "P": set(re.findall(r"^\|\s*~*(P-\d{3})~*\s*\|", pen, re.M))
             | set(re.findall(r"^##.*?\b(P-\d{3})\b", pen, re.M)),
        "M": set(re.findall(r"^## (M-\d{3})\b", mis, re.M)),
    }


def main() -> int:
    defined = _defined()
    dangling: list[str] = []
    for path in sorted(ROOT.rglob("*")):
        if path.suffix not in SCAN_SUFFIXES or not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.relative_to(ROOT).parts):
            continue
        rel = path.relative_to(ROOT).as_posix()
        for n, line in enumerate(path.read_text(encoding="utf-8", errors="replace")
                                 .splitlines(), 1):
            if "SONRAKI BOS ID" in line:   # tanim geregi henuz var olmayan tek atif
                continue
            for kind, num in REF.findall(line):
                ref = f"{kind}-{num}"
                if ref not in defined[kind]:
                    dangling.append(f"{rel}:{n}: {ref}")

    dec = (ROOT / "DECISIONS.md").read_text(encoding="utf-8")
    m = re.search(r"SONRAKI BOS ID:\s*D-(\d{3})", dec)
    max_d = max(int(d[2:]) for d in defined["D"])
    next_ok = m is not None and int(m.group(1)) > max_d

    print(f"Tanimli: D={len(defined['D'])} P={len(defined['P'])} M={len(defined['M'])}")
    print(f"SONRAKI BOS ID: D-{m.group(1) if m else '???'} | en buyuk D: D-{max_d:03d} | "
          f"{'TAMAM' if next_ok else 'HATALI'}")
    if dangling:
        print(f"COZULMEYEN ATIF: {len(dangling)}")
        for d in dangling:
            print("  " + d)
    else:
        print("Cozulmeyen atif yok.")
    return 1 if (dangling or not next_ok) else 0


if __name__ == "__main__":
    raise SystemExit(main())
