"""Ortak altyapi: config okuma, logging, .meta.json yazma (Asama 0.1).

DIKKAT — ice aktarma yan etkisi (bilerek):
Bu paket ice aktarildiginda `proj_env.ensure_proj_env()` OTOMATIK calisir ve
PROJ/GDAL veri dizinlerini bu conda ortamina sabitler.

Gerekce: bu makinede PostgreSQL/PostGIS sistem geneli PROJ_LIB tanimliyor ve
pyproj'u bozuyor (bkz. MISTAKES.md M-003). Duzeltmeyi acik bir fonksiyon
cagrisina birakmak, tek bir scriptin onu unutmasina ve koordinatlarin sessizce
kaymasina yol acabilirdi. AGENTS.md Bolum 14.6 "CRS / yukseklik datumu" bu
projedeki bir numarali hata sinifi oldugundan, savunma otomatik yapildi.
"""

from .proj_env import ensure_proj_env

ensure_proj_env()
