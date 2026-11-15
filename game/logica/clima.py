# -*- coding: utf-8 -*-
"""Clima espacial REAL de la NASA (DONKI) dentro del juego.

Dos fuentes, y el juego siempre dice cuál está usando:
  · GUARDADOS: base_lunar/datos/donki.json, fulguraciones reales ya pasadas (tools/bajar_donki.py).
    Cada tormenta solar del juego se basa en una de ellas (su clase y su fecha).
  · EN VIVO: si hay internet, al abrir el juego se piden a DONKI las fulguraciones de los últimos
    30 días (en otro hilo, sin frenar el juego). Si no hay internet, se dice que son datos guardados.
La consulta no lleva ningún dato del jugador. Las dosis del juego son simplificaciones, no de DONKI.
"""
import datetime as dt
import json
import os
import threading
import urllib.request

from ..assets.textos import t, IDIOMA  # noqa: F401  (IDIOMA se lee de textos en cada llamada)
from ..assets import textos

_RUTA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "datos", "donki.json")
_API = "https://ccmc.gsfc.nasa.gov/DONKI-API/get/FLR?startDate={ini}&endDate={fin}"
_DATOS = None
VIVO = {"estado": "sin_pedir"}          # sin_pedir · pidiendo · listo · sin_internet

_MESES_ES = ("enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre",
             "octubre", "noviembre", "diciembre")
_MESES_EN = ("January", "February", "March", "April", "May", "June", "July", "August", "September",
             "October", "November", "December")


def datos():
    global _DATOS
    if _DATOS is None:
        try:
            with open(_RUTA, encoding="utf-8") as f:
                _DATOS = json.load(f)
        except (OSError, ValueError):
            _DATOS = {"eventos": [], "hasta": "", "total_fulguraciones": 0}
    return _DATOS


def potencia(clase):
    try:
        return {"A": 0.01, "B": 0.1, "C": 1, "M": 10, "X": 100}[clase[0]] * float(clase[1:])
    except (KeyError, ValueError, IndexError):
        return 0.0


def fecha(iso):
    """'2024-05-14T16:51Z' → '14 de mayo de 2024' (o 'May 14, 2024' en inglés)."""
    try:
        d = dt.date.fromisoformat(iso[:10])
    except (TypeError, ValueError):
        return iso or ""
    if textos.IDIOMA == "en":
        return f"{_MESES_EN[d.month - 1]} {d.day}, {d.year}"
    return f"{d.day} de {_MESES_ES[d.month - 1]} de {d.year}"


def evento_real(rng, nivel):
    """Una fulguración real para la tormenta del juego: clase X si es fuerte, M si es moderada.
    Se prefieren las que de verdad lanzaron partículas (eventos SEP de DONKI)."""
    ev = datos().get("eventos", [])
    letra = "X" if nivel == "fuerte" else "M"
    cand = [e for e in ev if e.get("clase", "").startswith(letra) and e.get("particulas")]
    cand = cand or [e for e in ev if e.get("clase", "").startswith(letra)]
    return rng.choice(cand) if cand else None


def pedir_en_vivo():
    """Pide los últimos 30 días a DONKI en otro hilo. No frena el juego; si falla, queda sin_internet."""
    if VIVO["estado"] != "sin_pedir":
        return

    def _hilo():
        try:
            fin = dt.date.today()
            ini = fin - dt.timedelta(days=30)
            req = urllib.request.Request(_API.format(ini=ini.isoformat(), fin=fin.isoformat()),
                                         headers={"User-Agent": "base-lunar-game"})
            with urllib.request.urlopen(req, timeout=6) as r:
                texto = r.read().decode("utf-8")
            lista = json.loads(texto) if texto.strip() else []
            fuerte = max(lista, key=lambda f: potencia(f.get("classType") or ""), default=None)
            VIVO.update(estado="listo", n=len(lista), dias=30,
                        clase=(fuerte or {}).get("classType", ""), pico=(fuerte or {}).get("peakTime", ""))
        except Exception:          # sin internet, servidor caído, respuesta rara: se usan los guardados
            VIVO.update(estado="sin_internet")

    VIVO["estado"] = "pidiendo"
    threading.Thread(target=_hilo, daemon=True).start()


def resumen():
    """Una frase sobre el Sol real, diciendo si es EN VIVO o GUARDADO."""
    if VIVO.get("estado") == "listo":
        if VIVO["n"] == 0:
            return t("clima.vivo0", "En vivo, NASA DONKI: en los últimos 30 días no hubo fulguraciones registradas.")
        return t("clima.vivo", "En vivo, NASA DONKI: en los últimos 30 días hubo {n} fulguraciones; la más fuerte "
                               "fue {c} el {f}.", n=VIVO["n"], c=VIVO["clase"], f=fecha(VIVO["pico"]))
    d = datos()
    ev = d.get("eventos", [])
    if not ev:
        return t("clima.nada", "No hay datos de clima espacial disponibles.")
    fuerte = max(ev, key=lambda e: e.get("potencia", 0))
    return t("clima.guardado", "Datos guardados de NASA DONKI (hasta el {h}, no en vivo): desde 2024 hubo {n} "
                               "fulguraciones; la más fuerte fue {c} el {f}.",
             h=fecha(d.get("hasta", "")), n=f"{d.get('total_fulguraciones', 0):,}".replace(",", " "),
             c=fuerte["clase"], f=fecha(fuerte["pico"]))
