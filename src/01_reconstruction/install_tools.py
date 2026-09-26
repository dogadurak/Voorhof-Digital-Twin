"""Asama 1 araclarini (roofer, val3dity) Windows derlemeleriyle kurar (Karar D-033).

Asama : 1 (hazirlik — rekonstruksiyon DEGIL)

Ne yapar:
  1. Surumu SABIT URL'den zip'i indirir.
  2. SHA-256'yi YAYINCININ GitHub'da ilan ettigi degerle karsilastirir
     (checksum'i biz uretmiyoruz — D-027'deki 3DBAG dogrulamasinin aynisi).
     Uyusmazlik hata firlatir; dosya kullanilmaz.
  3. `tools/<ad>/` altina acar.
  4. Araci FIILEN calistirir (`--version` / `--help`). Exit code 0 tek basina
     kanit sayilmaz (M-002): ciktida surum dizgisi aranir.
  5. `tools/MANIFEST.json`'a surum, URL, yayinci checksum'i, olculen checksum
     ve calisma kaniti yazilir.

Ag erisimi yalnizca sabit URL'lere yapilir; kurulum sistem genelinde
DEGIL, depo icindeki `tools/` klasorune yapilir (git'e girmez).

Calistirma:
    python src/01_reconstruction/install_tools.py
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import src.common  # noqa: E402,F401

import requests  # noqa: E402

from src.common.config import resolve  # noqa: E402
from src.common.logging_setup import setup_logging  # noqa: E402

# Surum ve yayinci checksum'i SABITTIR (D-033'te kayitli). Degistirmek yeni bir
# karar demektir; sessizce "latest"e gecilmez.
TOOLS = [
    {
        "name": "roofer",
        "version": "v1.0.0",
        "url": "https://github.com/3DBAG/roofer/releases/download/v1.0.0/"
               "roofer-windows-x86_64-v1.0.0.zip",
        "publisher_sha256": "143413f13f347138dae731b345b8bcdc70f66e3f8bf77da260068f577b40ae7f",
        "exe": "roofer.exe",
        "probe_args": [["--version"], ["--help"]],
        "expect": "1.0.0",
        "license": "GPLv3 (AGENTS Bolum 7)",
    },
    {
        "name": "val3dity",
        "version": "2.7.0",
        "url": "https://github.com/tudelft3d/val3dity/releases/download/2.7.0/"
               "val3dity-win64.zip",
        "publisher_sha256": "cf8d3f025cd52aafc9ea370296a2430baa4aa39ce44a8b3ba1d8b3a540d8a5a7",
        "exe": "val3dity.exe",
        "probe_args": [["--version"], ["--help"]],
        "expect": "2.7",
        "license": "GPLv3 (AGENTS Bolum 7: acik kaynak)",
    },
]
TIMEOUT_S = 300


def _sha256(path: Path) -> str:
    """Dosyanin SHA-256 ozetini dondurur (hex)."""
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _probe(exe: Path, arg_sets: list[list[str]], expect: str, logger) -> dict:
    """Araci fiilen calistirir; ciktida beklenen surum dizgisini arar.

    Girdi : exe yolu, denenecek arguman listeleri, beklenen dizgi
    Cikti : {"args", "returncode", "found_expected", "first_lines"}
    """
    last: dict = {}
    for args in arg_sets:
        try:
            r = subprocess.run([str(exe), *args], capture_output=True, text=True,
                               timeout=60, cwd=str(exe.parent))
        except (OSError, subprocess.TimeoutExpired) as e:
            last = {"args": args, "returncode": None, "error": repr(e),
                    "found_expected": False, "first_lines": []}
            logger.warning("%s %s calistirilamadi: %r", exe.name, " ".join(args), e)
            continue
        out = (r.stdout or "") + (r.stderr or "")
        lines = [ln for ln in out.splitlines() if ln.strip()][:8]
        last = {"args": args, "returncode": r.returncode,
                "found_expected": expect in out, "first_lines": lines}
        logger.info("%s %s | exit %s | '%s' ciktida %s", exe.name, " ".join(args),
                    r.returncode, expect, "VAR" if expect in out else "YOK")
        for ln in lines[:4]:
            logger.info("    | %s", ln[:160])
        if expect in out:
            return last
    return last


def main() -> int:
    logger, run_id, _ = setup_logging("install_tools")
    tools_dir = resolve("tools.dir")
    tools_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = resolve("tools.manifest")

    manifest = {"decision_ref": "D-033", "run_id": run_id,
                "installed_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "tools": []}
    failures = 0

    for t in TOOLS:
        logger.info("=== %s %s ===", t["name"], t["version"])
        zpath = tools_dir / Path(t["url"]).name
        with requests.get(t["url"], stream=True, timeout=TIMEOUT_S) as r:
            r.raise_for_status()
            with zpath.open("wb") as fh:
                for chunk in r.iter_content(1 << 20):
                    fh.write(chunk)
        got = _sha256(zpath)
        if got != t["publisher_sha256"]:
            logger.error("%s: SHA-256 UYUSMUYOR\n  yayinci: %s\n  indirilen: %s",
                         t["name"], t["publisher_sha256"], got)
            failures += 1
            continue
        logger.info("%s | %d bayt | sha256 DOGRULANDI (yayincinin degeriyle)",
                    zpath.name, zpath.stat().st_size)

        dest = tools_dir / t["name"]
        with zipfile.ZipFile(zpath) as z:
            z.extractall(dest)
        exes = sorted(dest.rglob(t["exe"]))
        # val3dity-win64.zip ICINDE yine val3dity-win64.zip var (olculdu
        # 2026-09-27). Calistirilabilir bulunamazsa bir kademe ic zip acilir;
        # ic zip'in checksum'i da manifest'e yazilir (yayinci onu ilan etmiyor).
        inner_sha: dict[str, str] = {}
        if not exes:
            for inner in sorted(dest.rglob("*.zip")):
                inner_sha[inner.name] = _sha256(inner)
                logger.info("Ic zip bulundu: %s | sha256 %s (yayinci ilan etmiyor, "
                            "yalnizca kayit)", inner.name, inner_sha[inner.name])
                with zipfile.ZipFile(inner) as z:
                    z.extractall(inner.parent / (inner.stem + "_inner"))
            exes = sorted(dest.rglob(t["exe"]))
        if not exes:
            logger.error("%s: zip icinde %s bulunamadi. Icerik: %s", t["name"], t["exe"],
                         [p.name for p in dest.rglob("*")][:30])
            failures += 1
            continue
        exe = exes[0]
        logger.info("Calistirilabilir: %s", exe.relative_to(tools_dir.parent))

        probe = _probe(exe, t["probe_args"], t["expect"], logger)
        if not probe.get("found_expected"):
            logger.error("%s: calisti ama ciktida beklenen '%s' YOK — kurulum "
                         "DOGRULANMADI (exit code tek basina kanit degil, M-002)",
                         t["name"], t["expect"])
            failures += 1

        manifest["tools"].append({
            "name": t["name"], "version": t["version"], "url": t["url"],
            "license": t["license"],
            "publisher_sha256": t["publisher_sha256"], "measured_sha256": got,
            "sha256_verified": got == t["publisher_sha256"],
            "inner_zip_sha256": inner_sha,
            "exe": str(exe.relative_to(tools_dir.parent)).replace("\\", "/"),
            "probe": probe,
        })

    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False),
                             encoding="utf-8")
    logger.info("MANIFEST yazildi: %s", manifest_path.relative_to(tools_dir.parent))
    logger.info("SONUC: %s", "PASS" if failures == 0 else f"FAIL ({failures} arac)")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
