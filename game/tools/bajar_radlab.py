# -*- coding: utf-8 -*-
"""Baja de RadLab (NASA OSDR) mediciones REALES de radiación y guarda un resumen dentro del juego:
game/data/radlab.json. La decisión «El dosímetro de la base» usa ese número real si el archivo existe;
si no existe, usa un número de ejemplo y lo dice.

    python tools/bajar_radlab.py                       (las dos consultas de abajo)
    python tools/bajar_radlab.py --consulta "ISS · DosTel|spacecraft=ISS&instrument=DosTel&timestamp>=2022-04-01T00:00&timestamp<2022-04-08T00:00"

Fuente: NASA OSDR · RadLab. Documentación de la API: https://visualization.osdr.nasa.gov/radlab/gui/data-api/
Se pide en CSV: https://visualization.osdr.nasa.gov/radlab/api/?<consulta>&format=csv
Campos que usa: absorbed_dose_rate (µGy/h) y dose_equivalent_rate (µSv/h).

OJO: este archivo se escribió leyendo la documentación de RadLab, pero quien lo escribió NO pudo conectarse a la API
para probarlo con datos de verdad. Si RadLab devuelve las columnas con otros nombres, el programa lo dice (imprime las
columnas que recibió) y NO guarda nada, para no meter datos falsos al juego. Solo usa la biblioteca estándar.
"""
import csv
import datetime as dt
import io
import json
import os
import sys
import urllib.error
import urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://visualization.osdr.nasa.gov/radlab/api/?{consulta}&absorbed_dose_rate&dose_equivalent_rate&format=csv"
SALIDA = os.path.join(RAIZ, "data", "radlab.json")
MAX_BYTES = 20_000_000          # no leer más de 20 MB por consulta
# nombre|consulta. La primera es el ejemplo de la documentación de RadLab (DosTel en la Estación, abril de 2022);
# la segunda pide el instrumento LND del módulo Chang'e 4, en la superficie de la Luna.
CONSULTAS = [
    "ISS · DosTel|spacecraft=ISS&instrument=DosTel&timestamp>=2022-04-01T00:00&timestamp<2022-04-08T00:00",
    "Luna (superficie) · LND de Chang'e 4|celestial_body=Moon&instrument=LND",
]


def _num(x):
    try:
        v = float(x)
        return v if v == v else None          # descarta NaN
    except (TypeError, ValueError):
        return None


def resumir(nombre, consulta, texto_csv):
    """De un CSV de RadLab saca el promedio de cada tasa de dosis. Devuelve None si faltan las columnas."""
    lector = csv.DictReader(io.StringIO(texto_csv))
    cols = {(c or "").strip().lower(): c for c in (lector.fieldnames or [])}
    c_abs, c_eq, c_t = cols.get("absorbed_dose_rate"), cols.get("dose_equivalent_rate"), cols.get("timestamp")
    if not (c_abs or c_eq):
        print(f"  ✗ {nombre}: RadLab no trajo absorbed_dose_rate ni dose_equivalent_rate. Columnas recibidas: "
              f"{list(cols)}")
        return None
    abs_v, eq_v, tiempos = [], [], []
    for fila in lector:
        a = _num(fila.get(c_abs)) if c_abs else None
        e = _num(fila.get(c_eq)) if c_eq else None
        if a is not None and a >= 0:
            abs_v.append(a)
        if e is not None and e >= 0:
            eq_v.append(e)
        if c_t and fila.get(c_t):
            tiempos.append(fila[c_t])
    if not eq_v:
        print(f"  ✗ {nombre}: no hay valores de dose_equivalent_rate (µSv/h) en esta consulta")
        return None
    return {"nombre": nombre, "consulta": consulta, "n": len(eq_v),
            "equivalente_usv_h": round(sum(eq_v) / len(eq_v), 2),
            "absorbida_ugy_h": round(sum(abs_v) / len(abs_v), 3) if abs_v else None,
            "desde": min(tiempos) if tiempos else None, "hasta": max(tiempos) if tiempos else None}


def pedir(consulta):
    req = urllib.request.Request(BASE.format(consulta=consulta), headers={"User-Agent": "base-lunar-data-fetch"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read(MAX_BYTES).decode("utf-8", errors="replace")


def main():
    args = sys.argv[1:]
    consultas = [args[i + 1] for i, a in enumerate(args) if a == "--consulta"] or CONSULTAS
    medidas = []
    for c in consultas:
        nombre, _, consulta = c.partition("|")
        print("pidiendo:", nombre)
        try:
            m = resumir(nombre, consulta, pedir(consulta))
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            print(f"  ✗ {nombre}: no se pudo conectar ({e})")
            continue
        if m:
            medidas.append(m)
            print(f"  ✓ {m['n']} mediciones · {m['equivalente_usv_h']} µSv/h · {m['absorbida_ugy_h']} µGy/h")
    if not medidas:
        print("No se guardó nada: el juego seguirá usando el número de ejemplo.")
        sys.exit(1)
    datos = {"fuente": "NASA OSDR · RadLab", "api": "https://visualization.osdr.nasa.gov/radlab/api/",
             "bajado": dt.date.today().isoformat(), "mediciones": medidas,
             "nota": "Promedios de mediciones reales ya hechas (datos guardados, no en vivo)."}
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    with open(SALIDA, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=1)
    print("guardado:", SALIDA)


if __name__ == "__main__":
    main()
