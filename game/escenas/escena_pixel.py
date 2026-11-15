# -*- coding: utf-8 -*-
"""La vista de la base en el tablero, dibujada como pixel art (como los juegos viejos de consola).

Se dibuja en chiquito (110 × 83 cuadritos) y se agranda 4 veces SIN suavizar: así cada píxel se ve como
un cuadrito. Los nombres van encima con la letra de píxeles. Lo que se ve depende del estado de la base:
de día o de noche, el panel inclinado o rajado, el regolito encima del hábitat, el refugio del
dormitorio y el invernadero encendido o apagado. Hay cosas que se mueven: estrellas que titilan, la luz
de la antena, una astronauta que camina, las plantas y el reactor de noche.
"""
import math
import random

import pygame

from ..assets.textos import t, n
from ..assets.texto_mate import fuente_pixel, pixel

ESC = 4                       # cada cuadrito mide 4 × 4 píxeles de pantalla
W, H = 110, 83
HAB = 50                      # dónde está cada cosa (en cuadritos)
INV = 87
REA = 101
PAN = 14
SUELO = 54                    # la línea del horizonte


def _paleta(de_dia):
    if de_dia:
        return {"cielo": (6, 7, 16), "cielo2": (12, 13, 28), "monte": (112, 110, 122), "monte_luz": (160, 158, 168),
                "monte_sombra": (82, 80, 94), "suelo": (150, 148, 156), "suelo2": (128, 126, 136),
                "suelo3": (100, 98, 110), "piedra": (182, 180, 188), "estrella": 0.55, "hab": (214, 218, 226),
                "hab_sombra": (168, 172, 186), "hab_luz": (244, 246, 250), "panel": (46, 92, 196)}
    return {"cielo": (3, 4, 12), "cielo2": (8, 10, 24), "monte": (40, 42, 58), "monte_luz": (62, 64, 84),
            "monte_sombra": (28, 30, 44), "suelo": (54, 56, 72), "suelo2": (44, 46, 62), "suelo3": (34, 36, 50),
            "piedra": (76, 78, 96), "estrella": 1.0, "hab": (150, 156, 172), "hab_sombra": (110, 116, 134),
            "hab_luz": (186, 190, 204), "panel": (22, 34, 76)}


_RNG = random.Random(9)
ESTRELLAS = [(_RNG.randrange(W), _RNG.randrange(SUELO - 8), _RNG.choice((90, 140, 200, 255)), _RNG.random())
             for _ in range(55)]
PIEDRAS = [(_RNG.randrange(W), _RNG.randrange(SUELO + 4, H), _RNG.choice((0, 1))) for _ in range(40)]
CRATERES = ((8, 72, 12), (34, 76, 8), (70, 74, 14), (96, 78, 9), (58, 67, 6))


def _monte(x):
    return int(SUELO - 4 - 3 * math.sin(x * 0.15) - 2 * math.sin(x * 0.37 + 1) - 4 * max(0.0, math.sin(x * 0.06 + 2)))


def _fondo(de_dia):
    """Lo que no se mueve: cielo con degradado tramado, montañas, suelo con cráteres y piedras."""
    c = _paleta(de_dia)
    s = pygame.Surface((W, H))
    s.fill(c["cielo"])
    for y in range(SUELO - 14, SUELO):                         # el cielo se aclara un poquito abajo (tramado)
        for x in range(W):
            if (x + y) % 2 == 0 or y > SUELO - 6:
                s.set_at((x, y), c["cielo2"])
    for x in range(W):                                          # montañas lejanas, con luz del lado del Sol
        y0 = _monte(x)
        sube = _monte(x + 1) < y0
        pygame.draw.line(s, c["monte"], (x, y0), (x, SUELO + 2))
        s.set_at((x, y0), c["monte_luz"] if not sube else c["monte_sombra"])
        if not sube:
            s.set_at((x, y0 + 1), c["monte_luz"] if x % 2 else c["monte"])
    for x in range(W):                                          # el suelo, con lomitas
        y0 = SUELO + (1 if math.sin(x * 0.3) > 0.6 else 0)
        pygame.draw.line(s, c["suelo"], (x, y0), (x, H))
        s.set_at((x, y0), c["piedra"])
    for y in range(SUELO + 12, H):                              # más oscuro hacia abajo (tramado)
        for x in range(W):
            if (x + y) % 2 == 0 and (y > SUELO + 20 or (x * 7 + y * 3) % 5 == 0):
                s.set_at((x, y), c["suelo2"])
    for cx, cy, w in CRATERES:
        pygame.draw.ellipse(s, c["suelo3"], (cx - w // 2, cy - w // 6, w, max(2, w // 3)))
        pygame.draw.line(s, c["piedra"], (cx - w // 2 + 2, cy - w // 6 + max(2, w // 3)), (cx + w // 2 - 2, cy - w // 6 + max(2, w // 3)))
    for x, y, k in PIEDRAS:
        s.set_at((x, y), c["suelo3"] if k else c["piedra"])
        if k:
            s.set_at((x + 1, y), c["suelo3"])
            s.set_at((x, y - 1), c["piedra"])
    return s


_FONDOS = {}
_TXT = {}


def _rotulo(texto, color=(226, 232, 246)):
    """Un nombre con la letra de píxeles y un borde oscuro (se lee sobre cualquier cosa)."""
    k = (texto, color)
    img = _TXT.get(k)
    if img is None:
        f = fuente_pixel(8)
        s = pixel(texto)
        a = f.render(s, False, color)
        b = f.render(s, False, (6, 8, 16))
        img = pygame.Surface((a.get_width() + 2, a.get_height() + 2), pygame.SRCALPHA)
        for dx, dy in ((0, 1), (2, 1), (1, 0), (1, 2), (2, 2)):
            img.blit(b, (dx, dy))
        img.blit(a, (1, 1))
        if len(_TXT) > 60:
            _TXT.clear()
        _TXT[k] = img
    return img


def _sol(s):
    cx, cy = 15, 11
    for y in range(cy - 8, cy + 9):
        for x in range(cx - 8, cx + 9):
            d = math.hypot(x - cx, y - cy)
            if 5.5 < d <= 7.5 and (x + y) % 2 == 0:
                s.set_at((x, y), (110, 96, 52))
            elif 4.5 < d <= 5.5:
                s.set_at((x, y), (255, 214, 110))
    pygame.draw.circle(s, (255, 246, 206), (cx, cy), 4)
    s.set_at((cx - 1, cy - 2), (255, 255, 255))


def _tierra(s, cuadro):
    cx, cy, r = 94, 12, 6
    pygame.draw.circle(s, (36, 94, 196), (cx, cy), r)
    giro = (cuadro // 40) % 12                                 # los continentes pasan despacito
    for x, y in ((-3, -2), (-2, -2), (-3, -1), (-2, -1), (-1, -1), (-2, 0), (2, 1), (3, 1), (2, 2), (1, -3), (2, -3)):
        xx = cx + ((x + giro + 6) % 12) - 6
        if math.hypot(xx - cx, y) <= r - 0.5:
            s.set_at((xx, cy + y), (70, 166, 82))
    for x, y in ((-4, 2), (-3, 3), (0, -5), (1, -5), (3, -3), (-1, 4)):
        if math.hypot(x, y) <= r:
            s.set_at((cx + x, cy + y), (236, 242, 250))
    for y in range(-r, r + 1):                                 # la noche de la Tierra (tramado)
        for x in range(2, r + 1):
            if math.hypot(x, y) <= r and ((x + y) % 2 == 0 or x >= 4):
                s.set_at((cx + x, cy + y), (14, 30, 72))


def _panel(s, e, c):
    x0, y0 = PAN, SUELO + 7
    pygame.draw.line(s, (176, 178, 190), (x0, y0), (x0, y0 - 12))
    s.set_at((x0 + 1, y0), (90, 92, 104))
    ang = math.radians(35 if e.panel_factor <= 0.5 else 0)
    cx, cy = x0, y0 - 16
    w, h = 9.5, 3.5
    esq = [(-w, -h), (w, -h), (w, h), (-w, h)]
    pts = [(cx + x * math.cos(ang) - y * math.sin(ang), cy + x * math.sin(ang) + y * math.cos(ang)) for x, y in esq]
    pygame.draw.polygon(s, c["panel"], pts)
    for k in (1 / 3, 2 / 3):                                    # las celdas
        a = (pts[0][0] + (pts[1][0] - pts[0][0]) * k, pts[0][1] + (pts[1][1] - pts[0][1]) * k)
        b = (pts[3][0] + (pts[2][0] - pts[3][0]) * k, pts[3][1] + (pts[2][1] - pts[3][1]) * k)
        pygame.draw.line(s, (20, 40, 110), a, b)
    m0 = ((pts[0][0] + pts[3][0]) / 2, (pts[0][1] + pts[3][1]) / 2)
    m1 = ((pts[1][0] + pts[2][0]) / 2, (pts[1][1] + pts[2][1]) / 2)
    pygame.draw.line(s, (20, 40, 110), m0, m1)
    pygame.draw.polygon(s, (176, 194, 236), pts, 1)
    if e.de_dia():
        s.set_at((int(pts[0][0]) + 2, int(pts[0][1]) + 1), (255, 255, 255))
    if e.panel_factor < 1 and e.panel_factor != 0.5:            # rajado
        pygame.draw.line(s, (255, 255, 255), (cx - 3, cy - 2), (cx + 2, cy + 2))


def _habitat(s, e, c, cuadro, noche):
    hx, base = HAB, SUELO + 8
    # sombra en el suelo
    for x in range(hx - 16, hx + 22):
        if x % 2 == 0:
            s.set_at((x, base + 1), c["suelo3"])
    s.set_clip((0, 0, W, base))                                 # de los óvalos solo se ve la mitad de arriba
    if e.regolito > 0:                                          # el regolito encima (más grueso = más metros)
        g = 1 + min(3, int(round(e.regolito)))
        cap = pygame.Rect(hx - 17 - g, base - 17 - g, 34 + 2 * g, 2 * (17 + g))
        pygame.draw.ellipse(s, (124, 102, 78), cap)
        for y in range(cap.top, base):
            for x in range(cap.left, cap.right):
                if (x * 3 + y * 5) % 7 == 0 and s.get_at((x, y))[:3] == (124, 102, 78):
                    s.set_at((x, y), (96, 78, 60))
    domo = pygame.Rect(hx - 17, base - 17, 34, 34)
    pygame.draw.ellipse(s, c["hab"], domo)
    for y in range(domo.top, domo.centery + 1):                 # sombra del lado contrario al Sol
        for x in range(hx + 6, domo.right):
            if s.get_at((x, y))[:3] == c["hab"] and (x > hx + 10 or (x + y) % 2 == 0):
                s.set_at((x, y), c["hab_sombra"])
    pygame.draw.arc(s, c["hab_luz"], domo.inflate(-6, -6), 1.9, 2.9)
    pygame.draw.ellipse(s, (96, 100, 116), domo, 1)
    s.set_clip(None)
    pygame.draw.rect(s, c["hab_sombra"], (hx - 18, base - 4, 36, 5))   # el anillo de abajo
    pygame.draw.line(s, (90, 94, 110), (hx - 18, base), (hx + 17, base))
    pygame.draw.rect(s, (60, 64, 80), (hx - 2, base - 6, 4, 6))       # la puerta
    s.set_at((hx + 1, base - 3), (255, 214, 110) if noche else (200, 204, 214))
    for x in (hx - 11, hx - 6, hx + 5, hx + 10):                       # ventanas
        if noche:
            pygame.draw.rect(s, (255, 216, 112), (x - 1, base - 11, 3, 2))
            for dx, dy in ((-2, 0), (2, 0), (0, -1)):
                if (cuadro // 20 + x) % 3:
                    s.set_at((x + dx, base - 11 + dy), (120, 100, 60))
        else:
            pygame.draw.rect(s, (54, 74, 116), (x - 1, base - 11, 3, 2))
            s.set_at((x - 1, base - 11), (220, 232, 250))
    # antena con lucecita que parpadea
    pygame.draw.line(s, (180, 184, 196), (hx + 6, base - 16), (hx + 9, base - 22))
    s.set_at((hx + 8, base - 21), (200, 204, 214))
    s.set_at((hx + 10, base - 22), (200, 204, 214))
    if (cuadro // 30) % 2:
        s.set_at((hx + 9, base - 23), (255, 70, 70))
    # el refugio del dormitorio (bloques del color de lo que se escogió)
    cols = {0.3: (80, 150, 255), 0.6: (80, 200, 110), 1.0: (230, 200, 70)}
    col = cols.get(e.refugio)
    if col and e.refugio_elegido:
        for dx in (-15, -10, 7, 12):
            pygame.draw.rect(s, col, (hx + dx, base - 3, 4, 4))
            s.set_at((hx + dx, base - 3), tuple(min(255, v + 60) for v in col))


def _invernadero(s, e, cuadro):
    gx, base = INV, SUELO + 9
    on = e.sistemas["invernadero"]
    caja = pygame.Rect(gx - 10, base - 12, 20, 24)
    if on:                                                      # el resplandor verde (tramado)
        for y in range(caja.top - 3, base):
            for x in range(caja.left - 3, caja.right + 3):
                d = math.hypot((x - gx) / 13, (y - base) / 15)
                if 0.8 < d < 1.0 and (x + y + cuadro // 15) % 2 == 0:
                    s.set_at((x, y), (40, 110, 60))
    vidrio = (52, 104, 80) if on else (56, 62, 76)
    s.set_clip((0, 0, W, base))
    pygame.draw.ellipse(s, vidrio, caja)
    if on:
        for i in range(5):                                      # las plantas adentro, que se mecen
            x = gx - 6 + 3 * i
            alto = 3 + (i % 2) * 2 + (1 if math.sin(cuadro * 0.05 + i) > 0.3 else 0)
            pygame.draw.line(s, (70, 200, 90), (x, base - 1), (x, base - alto))
            s.set_at((x, base - alto - 1), (150, 240, 140))
            if i % 2 == 0:
                s.set_at((x + 1, base - alto + 1), (70, 200, 90))
    else:
        for i in range(5):
            s.set_at((gx - 6 + 3 * i, base - 2), (120, 96, 60))
    marco = (150, 226, 172) if on else (104, 112, 126)
    pygame.draw.ellipse(s, marco, caja, 1)
    s.set_clip(None)
    pygame.draw.line(s, marco, (gx, caja.top), (gx, base))
    pygame.draw.line(s, marco, (caja.left + 3, base - 6), (caja.right - 4, base - 6))
    s.set_at((gx - 5, base - 9), (230, 255, 236))
    pygame.draw.line(s, (90, 96, 112), (caja.left, base), (caja.right - 1, base))


def _reactor(s, cuadro, noche):
    """Un reactor de fisión chiquito (como los que estudia la NASA para la Luna): caja, mástil y radiadores."""
    rx, base = REA, SUELO + 8
    if noche:                                                   # brilla de noche (anillo tramado que late)
        r = 5 + (cuadro // 10) % 2
        for y in range(base - 10, base + 2):
            for x in range(rx - 8, rx + 9):
                if r - 0.8 < math.hypot(x - rx, y - (base - 3)) <= r + 0.2 and (x + y) % 2 == 0:
                    s.set_at((x, y), (255, 140, 40))
    pygame.draw.rect(s, (40, 42, 54), (rx - 4, base - 6, 9, 7))          # la caja (con borde oscuro)
    pygame.draw.rect(s, (150, 152, 166), (rx - 3, base - 5, 7, 5))
    pygame.draw.line(s, (206, 208, 220), (rx - 3, base - 5), (rx + 3, base - 5))
    s.set_at((rx, base - 3), (255, 180, 80) if noche else (90, 92, 104))
    pygame.draw.line(s, (40, 42, 54), (rx + 1, base - 7), (rx + 1, base - 19))   # el mástil
    pygame.draw.line(s, (176, 178, 192), (rx, base - 7), (rx, base - 19))
    for k, w in enumerate((3, 4, 5)):                           # los radiadores (más anchos abajo)
        y = base - 18 + k * 4
        pygame.draw.line(s, (40, 42, 54), (rx - w, y + 1), (rx + w, y + 1))
        pygame.draw.line(s, (214, 216, 228), (rx - w, y), (rx + w, y))


def _rover(s, de_dia):
    x, y = 28, SUELO + 15
    if de_dia:
        pygame.draw.line(s, (100, 98, 110), (x, y + 3), (x + 8, y + 3))
    pygame.draw.rect(s, (206, 206, 216), (x, y - 1, 8, 3))
    pygame.draw.line(s, (240, 240, 246), (x, y - 1), (x + 7, y - 1))
    pygame.draw.line(s, (90, 140, 220), (x + 1, y - 2), (x + 3, y - 2))       # su panelcito
    for wx in (x + 1, x + 6):
        s.set_at((wx, y + 2), (40, 42, 52))
        s.set_at((wx + 1, y + 2), (40, 42, 52))
    pygame.draw.line(s, (180, 182, 194), (x + 7, y - 1), (x + 8, y - 4))
    s.set_at((x + 8, y - 5), (255, 214, 110))


# la astronauta (5 × 8 cuadritos): . vacío, o borde, b traje, v visor, m mochila; dos pasos
_ASTRO = ([".ooo.", "obbbo", "ovvbo", "obbbo", "mbbbo", "obbbo", "ob.bo", "oo.oo"],
          [".ooo.", "obbbo", "ovvbo", "obbbo", "mbbbo", "obbbo", ".obo.", ".ooo."])
_COLOR_ASTRO = {"o": (24, 26, 38), "b": (238, 240, 246), "v": (255, 196, 70), "m": (140, 146, 164)}


def _astronauta(s, cuadro):
    """Una astronauta que camina entre el hábitat y el invernadero (2 cuadros de animación)."""
    u = (cuadro % 600) / 600
    ida = u < 0.5
    k = u * 2 if ida else 2 - u * 2
    x0 = int(65 + 7 * k)
    y0 = SUELO + 5
    filas = _ASTRO[(cuadro // 12) % 2]
    for j, fila in enumerate(filas):
        for i, ch in enumerate(fila if not ida else fila[::-1]):
            if ch != ".":
                s.set_at((x0 + i, y0 + j), _COLOR_ASTRO[ch])


def _esquinas(r, fondo):
    k = ("esq", r.size, fondo)
    img = _FONDOS.get(k)
    if img is None:
        img = pygame.Surface(r.size, pygame.SRCALPHA)
        img.fill((*fondo, 255))
        pygame.draw.rect(img, (0, 0, 0, 0), (0, 0, *r.size), border_radius=12)
        _FONDOS[k] = img
    return img


def dibujar(juego, r):
    """Dibuja la vista de la base dentro del rectángulo r del tablero."""
    e = juego.m.e
    cuadro = juego.cuadro
    de_dia = e.de_dia()
    noche = not de_dia
    c = _paleta(de_dia)
    fondo = _FONDOS.get(de_dia)
    if fondo is None:
        fondo = _FONDOS[de_dia] = _fondo(de_dia)
    s = fondo.copy()
    for x, y, b, fase in ESTRELLAS:                              # estrellas que titilan
        tw = 0.6 + 0.4 * math.sin(cuadro * 0.04 + fase * 40)
        v = int(b * tw * c["estrella"])
        if v > 40:
            s.set_at((x, y), (v, v, min(255, v + 20)))
            if b == 255 and tw > 0.9 and noche:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    s.set_at((x + dx, y + dy), (v // 3, v // 3, v // 2))
    if de_dia:
        _sol(s)
    _tierra(s, cuadro)
    _panel(s, e, c)
    _rover(s, de_dia)
    _habitat(s, e, c, cuadro, noche)
    _invernadero(s, e, cuadro)
    _reactor(s, cuadro, noche)
    _astronauta(s, cuadro)
    grande = pygame.transform.scale(s, (W * ESC, H * ESC))       # sin suavizar: se ven los cuadritos
    lienzo = juego.lienzo
    color_fuera = tuple(lienzo.get_at(r.topleft))[:3]           # lo que hay afuera de las esquinas redondeadas
    lienzo.set_clip(r)
    lienzo.blit(grande, r.topleft)
    # los nombres (con la letra de píxeles)
    x0, y0 = r.topleft

    def poner(texto, x, y, centro=True, derecha=False):
        img = _rotulo(texto)
        rr = img.get_rect()
        if derecha:
            rr.topright = (x, y)
        else:
            rr.midtop = (x, y)
        rr.clamp_ip(r.inflate(-8, -8))
        lienzo.blit(img, rr)

    poner(t("esc.tierra", "la Tierra"), x0 + 94 * ESC, y0 + 20 * ESC)
    poner(t("esc.panel", "panel solar"), x0 + PAN * ESC + 2, y0 + (SUELO + 9) * ESC)
    poner(t("esc.habitat", "hábitat ({m} m de regolito)", m=n(e.regolito)), x0 + HAB * ESC, y0 + (SUELO + 19) * ESC)
    poner(t("esc.inv", "invernadero"), x0 + INV * ESC, y0 + (SUELO + 11) * ESC)
    poner(t("esc.reactor", "reactor"), r.right - 6, y0 + (SUELO - 15) * ESC, derecha=True)
    lienzo.set_clip(None)
    lienzo.blit(_esquinas(r, color_fuera), r.topleft)
