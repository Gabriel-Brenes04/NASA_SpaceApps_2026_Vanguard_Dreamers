# -*- coding: utf-8 -*-
"""Baja de DONKI (la base de clima espacial de la NASA) las fulguraciones y los eventos de partículas
reales, y guarda una selección dentro del juego: game/data/donki.json.

    python tools/bajar_donki.py              (desde enero de 2024 hasta hoy)
    python tools/bajar_donki.py 2023-01      (desde otro mes)

Fuente: NASA CCMC DONKI, Moon to Mars Space Weather Analysis Office.
API: https://ccmc.gsfc.nasa.gov/DONKI-API/get/FLR y /get/SEP (pide de a un mes: rangos largos dan error).
Lo que se guarda son datos REALES ya pasados («guardados»): el juego nunca los presenta como en vivo.
"""
import datetime as dt
import json
import os
import sys
import time
import urllib.error
import urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API = "https://ccmc.gsfc.nasa.gov/DONKI-API/get/{tipo}?startDate={ini}&endDate={fin}"
SALIDA = os.path.join(RAIZ, "data", "donki.json")


def pedir(tipo, ini, fin):
    url = API.format(tipo=tipo, ini=ini, fin=fin)
    req = urllib.request.Request(url, headers={"User-Agent": "base-lunar-data-fetch"})
    for intento in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                texto = r.read().decode("utf-8")
                return json.loads(texto) if texto.strip() else []
        except (urllib.error.URLError, TimeoutError) as e:
            if intento == 2:
                raise
            print("  reintento:", e)
            time.sleep(3)
    return []


def meses(desde, hasta):
    a = dt.date(desde.year, desde.month, 1)
    while a <= hasta:
        sig = dt.date(a.year + (a.month == 12), a.month % 12 + 1, 1)
        yield a, min(sig - dt.timedelta(days=1), hasta)
        a = sig


def potencia(clase):
    """C1.0 → 1, M1.0 → 10, X1.0 → 100 (cada letra es 10 veces la anterior: NASA Science)."""
    try:
        return {"A": 0.01, "B": 0.1, "C": 1, "M": 10, "X": 100}[clase[0]] * float(clase[1:])
    except (KeyError, ValueError, IndexError):
        return 0.0


def main():
    desde = dt.date.fromisoformat((sys.argv[1] + "-01") if len(sys.argv) > 1 else "2024-01-01")
    hoy = dt.date.today() - dt.timedelta(days=1)
    flr, sep = [], []
    for ini, fin in meses(desde, hoy):
        f = pedir("FLR", ini.isoformat(), fin.isoformat())
        s = pedir("SEP", ini.isoformat(), fin.isoformat())
        flr += f
        sep += s
        print(f"{ini:%Y-%m}: {len(f)} fulguraciones, {len(s)} eventos de partículas")
    con_particulas = set()
    for s in sep:
        for le in s.get("linkedEvents") or []:
            if "FLR" in le.get("activityID", ""):
                con_particulas.add(le["activityID"])
    eventos = []
    for f in flr:
        clase = (f.get("classType") or "").strip()
        p = potencia(clase)
        trajo = f.get("flrID") in con_particulas
        if p >= 50 or trajo:                     # M5 o más fuertes, o las que trajeron partículas
            eventos.append({"id": f.get("flrID"), "clase": clase, "potencia": p,
                            "pico": f.get("peakTime"), "region": f.get("activeRegionNum"),
                            "particulas": trajo, "enlace": f.get("link")})
    eventos.sort(key=lambda e: e["pico"])
    datos = {
        "fuente": "NASA CCMC DONKI (Moon to Mars Space Weather Analysis Office)",
        "api": "https://ccmc.gsfc.nasa.gov/DONKI-API",
        "bajado": dt.date.today().isoformat(),
        "desde": desde.isoformat(), "hasta": hoy.isoformat(),
        "total_fulguraciones": len(flr), "total_eventos_particulas": len(sep),
        "nota": "Datos reales guardados (no en vivo). Las dosis del juego son simplificaciones, no datos de DONKI.",
        "eventos": eventos,
    }
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    with open(SALIDA, "w", encoding="utf-8") as fh:
        json.dump(datos, fh, ensure_ascii=False, indent=1)
    x = sum(1 for e in eventos if e["clase"].startswith("X"))
    print(f"guardado {SALIDA}: {len(eventos)} eventos ({x} clase X, "
          f"{sum(e['particulas'] for e in eventos)} con partículas) de {len(flr)} fulguraciones")


if __name__ == "__main__":
    main()
