# -*- coding: utf-8 -*-
"""Textos del juego en dos idiomas.

Cómo funciona: cada texto se pide con una CLAVE y su versión en español al lado:

    t("noche.titulo", "Cae la noche lunar")
    t("o2.enun", "Tenés {o2} kg de oxígeno", o2=n(36.5))

Si el idioma es «en» y la clave está en EN, sale el inglés; si no, sale el español.
Para traducir el juego basta con llenar el diccionario EN de abajo (las mismas llaves {…}).
Python puro: no usa pygame.
"""
IDIOMA = "es"

try:
    from .textos_en import EN          # las traducciones (una por clave)
except ImportError:
    EN = {}


def poner_idioma(idioma):
    global IDIOMA
    IDIOMA = "en" if idioma == "en" else "es"


def t(clave, es, **valores):
    plantilla = EN.get(clave, es) if IDIOMA == "en" else es
    try:
        return plantilla.format(**valores) if valores else plantilla
    except (KeyError, IndexError, ValueError):
        return es.format(**valores) if valores else es


def n(x, dec=1):
    """Número con coma decimal en español y punto en inglés; miles con espacio fino."""
    if isinstance(x, int) or float(x).is_integer() and dec == 0:
        s = f"{int(round(x)):,}"
        return s.replace(",", " ") if IDIOMA == "es" else s
    s = f"{x:,.{dec}f}"
    if IDIOMA == "es":
        s = s.replace(",", " ").replace(".", ",")
    return s
