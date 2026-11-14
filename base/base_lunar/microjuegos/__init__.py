# -*- coding: utf-8 -*-
"""Microjuegos: las tareas del día que se juegan (5 a 10 segundos, solo con el ratón).

Para AGREGAR uno no hay que tocar este archivo: basta con crear `mi_juego.py` en esta carpeta con una
clase que herede de `Microjuego` y diga qué `tarea` reemplaza. Este archivo los encuentra solo.
Los archivos que empiezan con «_» (como _plantilla.py) no se cargan.

    from base_lunar.microjuegos import REGISTRO, para_tarea
    clase = para_tarea("cosecha")      # None si nadie hizo todavía el de esa tarea
"""
import importlib
import pkgutil

from .base import Microjuego, ANCHO, ALTO, ZONA, COLORES  # noqa: F401

REGISTRO = {}       # tarea -> clase
ERRORES = {}        # módulo -> error (un microjuego roto no tumba el juego)

# Si el .exe no deja listar la carpeta, se usan estos nombres (agregar aquí los nuevos también).
CONOCIDOS = ["estrellas", "huerto", "paneles", "escudo", "oxigeno"]


def _cargar(nombre):
    try:
        mod = importlib.import_module(f"{__name__}.{nombre}")
    except ModuleNotFoundError as e:
        if e.name and e.name.endswith(nombre):
            return            # todavía no existe: no es un error
        ERRORES[nombre] = repr(e)
        return
    except Exception as e:     # noqa: BLE001
        ERRORES[nombre] = repr(e)
        return
    for valor in vars(mod).values():
        if (isinstance(valor, type) and issubclass(valor, Microjuego) and valor is not Microjuego
                and getattr(valor, "tarea", None)):
            REGISTRO.setdefault(valor.tarea, valor)


nombres = [m.name for m in pkgutil.iter_modules(__path__) if not m.name.startswith("_") and m.name != "base"]
for _n in sorted(set(nombres) | set(CONOCIDOS)):
    _cargar(_n)


def para_tarea(tarea):
    return REGISTRO.get(tarea)
