# -*- coding: utf-8 -*-
"""Texto con matemática: dibuja fracciones apiladas dentro de un párrafo.

    {{36|32}}   →   36
                    ──
                    32

Uso:  sup = componer("Cada kg necesita {{36|32}} = 1,125 kg de agua", 24, (255,255,255), 900)
      pantalla.blit(sup, (x, y))
Parte las líneas por palabras y respeta los saltos \\n. Guarda lo ya compuesto (caché).
"""
import os
import re

import pygame

_RX_FRAC = re.compile(r"\{\{([^|{}]+)\|([^|{}]+)\}\}")
_FUENTES = {}
_CACHE = {}

# Press Start 2P (CodeMan38, SIL Open Font License 1.1): títulos, botones y números grandes.
# Se usa en tamaños múltiplos de 8 (8, 16, 24, 32, 40, 48) para que los píxeles queden parejos.
_RUTA_PIXEL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fuentes", "PressStart2P-Regular.ttf")
_PIXEL = {}
# Lo que esa letra no trae: se cambia por algo parecido (comprobado el 14/11 dibujando cada símbolo).
_SIN_GLIFO = {"−": "-", "₂": "2", "✓": "OK"}


def fuente_pixel(tam):
    tam = int(tam)
    f = _PIXEL.get(tam)
    if f is None:
        try:
            f = pygame.font.Font(_RUTA_PIXEL, tam)
        except Exception:
            f = fuente(tam, True)          # si falta el archivo, la letra normal en negrita
        _PIXEL[tam] = f
    return f


def pixel(texto):
    for a, b in _SIN_GLIFO.items():
        texto = texto.replace(a, b)
    return texto


def fuente(tam, negrita=False):
    clave = (int(tam), bool(negrita))
    f = _FUENTES.get(clave)
    if f is None:
        for nombre in ("Segoe UI", "Arial", "DejaVu Sans", "Liberation Sans"):
            try:
                f = pygame.font.SysFont(nombre, int(tam), bold=negrita)
                if f:
                    break
            except Exception:
                f = None
        if f is None:
            f = pygame.font.Font(None, int(tam * 1.3))
        _FUENTES[clave] = f
    return f


def _fichas(texto):
    """[(tipo, contenido, espacio_antes)] — tipo: 'pal', 'frac' o 'nl'."""
    out = []
    for i, parrafo in enumerate(texto.split("\n")):
        if i:
            out.append(("nl", None, False))
        espacio = False
        pos = 0
        trozos = []
        for mt in _RX_FRAC.finditer(parrafo):
            trozos.append(("txt", parrafo[pos:mt.start()]))
            trozos.append(("frac", (mt.group(1).strip(), mt.group(2).strip())))
            pos = mt.end()
        trozos.append(("txt", parrafo[pos:]))
        for tipo, cont in trozos:
            if tipo == "frac":
                out.append(("frac", cont, espacio))
                espacio = False
                continue
            for pieza in re.findall(r"[^ 	]+|[ 	]+", cont):   # el espacio duro no parte
                if pieza.strip(" 	") == "":
                    espacio = True
                else:
                    out.append(("pal", pieza, espacio))
                    espacio = False
    return out


def _surf_frac(num, den, tam, color, negrita):
    f = fuente(max(10, int(tam * 0.78)), negrita)
    sn = f.render(num, True, color)
    sd = f.render(den, True, color)
    w = max(sn.get_width(), sd.get_width()) + 8
    h = sn.get_height() + sd.get_height() + 4
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    s.blit(sn, ((w - sn.get_width()) // 2, 0))
    y = sn.get_height() + 1
    pygame.draw.line(s, color, (2, y), (w - 3, y), max(1, tam // 14))
    s.blit(sd, ((w - sd.get_width()) // 2, y + 3))
    return s


def componer(texto, tam, color, ancho_max, negrita=False, alinear="izq", interlinea=1.12):
    clave = (texto, tam, tuple(color), ancho_max, negrita, alinear)
    s = _CACHE.get(clave)
    if s is not None:
        return s
    f = fuente(tam, negrita)
    esp = f.size(" ")[0]
    lineas = [[]]      # cada línea: [(surf, espacio_antes)]
    ancho = 0
    for tipo, cont, espacio in _fichas(texto):
        if tipo == "nl":
            lineas.append([])
            ancho = 0
            continue
        surf = (_surf_frac(cont[0], cont[1], tam, color, negrita) if tipo == "frac"
                else f.render(cont, True, color))
        sep = esp if (espacio and lineas[-1]) else 0
        if lineas[-1] and ancho + sep + surf.get_width() > ancho_max:
            lineas.append([])
            ancho = 0
            sep = 0
        lineas[-1].append((surf, sep))
        ancho += sep + surf.get_width()
    alto_base = int(f.get_linesize() * interlinea)
    medidas = []
    total_h = 0
    total_w = 0
    for ln in lineas:
        w = sum(s.get_width() + sep for s, sep in ln)
        h = max([alto_base] + [s.get_height() + 4 for s, _ in ln])
        medidas.append((w, h))
        total_h += h
        total_w = max(total_w, w)
    total_w = min(max(total_w, 1), ancho_max) if alinear == "izq" else ancho_max
    out = pygame.Surface((max(1, total_w), max(1, total_h)), pygame.SRCALPHA)
    y = 0
    for ln, (w, h) in zip(lineas, medidas):
        x = 0 if alinear == "izq" else (ancho_max - w) // 2
        for s, sep in ln:
            x += sep
            out.blit(s, (x, y + (h - s.get_height()) // 2))
            x += s.get_width()
        y += h
    if len(_CACHE) > 400:
        _CACHE.clear()
    _CACHE[clave] = out
    return out


def plano(texto):
    """El mismo texto sin marcas (para lectores o registros): {{a|b}} → a/b."""
    return _RX_FRAC.sub(lambda mt: f"{mt.group(1).strip()}/{mt.group(2).strip()}", texto)
