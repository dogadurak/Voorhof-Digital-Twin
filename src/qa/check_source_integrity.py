"""Kaynak dosya butunlugu: derlenebilirlik + gorunmez kontrol karakterleri (T-8 otomasyonu).

Neden var (MISTAKES M-017, 2026-09-27):
  Git Bash heredoc/printf ters egik cizgiyi bozdu: `\\b` -> 0x08 karakteri
  (check_claims regex'i sessizce degisti), `"\\n"` -> gercek satir sonu
  (SyntaxError). Ayni oturumda dort kez oldu; ucuncusundan sonra tuzak
  ENVIRONMENT T-8'e yazilmisti ve yine tekrarlandi. Insan disiplini yetmedi.

Ne yapar:
  1. `src/` altindaki her .py dosyasini derler (py_compile) — SyntaxError yakalanir.
  2. src/, config/ ve kok .md/.yml dosyalarinda sekme/satir sonu/CR DISINDAKI
     C0 kontrol karakterlerini (0x00-0x1F) arar — 0x08 gibi sessiz bozulmalar.

Cikis: 0 = temiz, 1 = sorun var.

Calistirma:
    python src/qa/check_source_integrity.py
"""

from __future__ import annotations

import py_compile
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ALLOWED = {0x09, 0x0A, 0x0D}


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")   # T-1
    bad: list[str] = []
    py = sorted((ROOT / "src").rglob("*.py"))
    for f in py:
        try:
            py_compile.compile(str(f), doraise=True, cfile=None)
        except py_compile.PyCompileError as exc:
            bad.append(f"DERLENMIYOR {f.relative_to(ROOT)}: {exc.msg.strip().splitlines()[-1]}")
    texts = py + sorted((ROOT / "config").glob("*.yml")) + sorted(ROOT.glob("*.md")) \
        + sorted((ROOT / "docs").glob("*.md"))
    for f in texts:
        data = f.read_bytes()
        ctrl = [(i, b) for i, b in enumerate(data) if b < 0x20 and b not in ALLOWED]
        if ctrl:
            line = data[:ctrl[0][0]].count(b"\n") + 1
            bad.append(f"KONTROL KARAKTERI {f.relative_to(ROOT)}: {len(ctrl)} adet, "
                       f"ilki 0x{ctrl[0][1]:02X} satir {line}")
    print(f"[KAYNAK] {len(py)} .py derlendi, {len(texts)} dosya tarandi, sorun: {len(bad)}")
    for b in bad:
        print("   HATA:", b)
    print("SONUC:", "FAIL" if bad else "PASS")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
