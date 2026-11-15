# -*- coding: utf-8 -*-
"""El mapa de la misión, en pixel art: una constelación con un nodo por día.

Hay dos tamaños, con la MISMA forma:
  · el chiquito, arriba en el tablero (en lugar de la fila de bolitas);
  · el grande, que se abre con el botón «Ver mapa» o con un clic en el chiquito.

Cada día la tripulación avanza un nodo:
  · los días vividos quedan encendidos (dorados los de sol, celestes los de noche);
  · los que faltan quedan apagados;
  · una flecha que rebota marca el día de hoy.
Al empezar un día nuevo, la marca viaja por la línea hasta el nodo siguiente.

En el grande, además, los días vividos muestran lo que pasó (tormenta, cohete...), mañana muestra el
aviso si lo hay, y al pasar el ratón por un nodo sale un cartelito con el resumen de ese día.

Se dibuja en chiquito y se agranda SIN suavizar (3 veces el chiquito, 4 veces el grande), igual que la
vista de la base (escena_pixel.py).

CÓMO CONECTARLO (se subió aparte, sin tocar lo que ya estaba; son 5 cambios en game/logica/juego.py):
  1. Arriba, con los otros imports de escenas:
         from ..escenas.mapa import MapaMixin, dibujar_mini
  2. La clase suma MapaMixin:
         class Juego(MenuInicial, PantallasInformacion, AyudaMixin, MapaMixin):
  3. En dibujar(), junto a «fin»:
         elif f == "mapa":
             self._mapa()
  4. En la tecla ESC, «mapa» vuelve como «datos» y «como»:
         elif self.fase in ("datos", "como", "mapa"):
  5. En _tablero(), la fila de bolitas (desde «x0, x1, yy = ...» hasta el texto «noche») se cambia por
         dibujar_mini(self, pygame.Rect(MAP_X + ARR_X - 40, 7 + ARR_Y, MAP_W + 140, ARR_H - 14), interactivo)
     y el botón «Ver mapa» pasa de  lambda: None  a  self.abrir_mapa
Con eso, el mapa chiquito queda arriba en el tablero y «Ver mapa» abre el grande (ESC o «Volver» para salir).
"""
import math
import random

import pygame

from ..assets import textos as _textos
from ..assets.textos import n
from ..assets.texto_mate import fuente_pixel, pixel
from ..assets.constantes import C, W as ANCHO, H as ALTO

DURA = 54            # cuadros que tarda la marca en pasar al día siguiente (~0,9 s)
DESTELLO = 30        # cuadros del destello al llegar

ESPACIO = (18, 8, 48)
ESPACIO2 = (34, 16, 80)
ESTRELLA = (64, 42, 132)
ESTRELLA2 = (128, 104, 210)
LINEA = (72, 76, 255)
LINEA_FUT = (60, 46, 138)
CORTE = (92, 72, 176)                 # la raya donde empieza la noche
PALETA = {"sol": ((232, 186, 60), (255, 244, 196)),
          "noche": ((0, 190, 226), (214, 250, 255)),
          "falta": ((86, 72, 160), (42, 30, 96))}
OSCURO = (34, 10, 28)                 # contorno de la flecha y de los dibujitos

# Los dibujitos: cada letra es un color (b = borde, c = centro); el punto no se pinta.
CUADRO = ("bbb", "bcb", "bbb")
ROMBO = ("..b..", ".bcb.", "bcccb", ".bcb.", "..b..")
GRANDE = ("...b...", "..bcb..", ".bcccb.", "bcccccb", ".bcccb.", "..bcb..", "...b...")
FLECHA_CHICA = (".oos.", ".oos.", "oooss", ".oos.", "..s..")
FLECHA = ("..oos..", "..oos..", "oooosss", ".oooss.", "..oss..", "...s...")
COLORES_FLECHA = {"o": (252, 206, 84), "s": (214, 128, 30)}

RAYO = ("...oo", "..oo.", ".oooo", "..oo.", ".oo..", "oo...")
COHETE = ("..w..", ".www.", ".wcw.", ".www.", "rwwwr", "r.f.r")
PIEDRA = ("l....", ".l...", "..gg.", ".gggg", "..gg.")
CRUZ = ("..r..", "..r..", "rrrrr", "..r..", "..r..")
GOTA = ("..b..", ".bbb.", "bbbbb", "bbwbb", ".bbb.")
ANTENA = ("o...o", ".o.o.", "..o..", "..o..", ".ooo.")
LUNA = (".mm..", "mm...", "mm...", "mm...", ".mm..")
MANCHA = (".yyy.", "yyyyy", "yykyy", "yyyyy", ".yyy.")
AVISO = ("o", "o", "o", ".", "o")
BANDERA = ("pfff", "pfff", "p...", "p...", "p...")
COLORES_ICONO = {"o": (250, 170, 60), "w": (232, 234, 244), "c": (90, 205, 255), "r": (236, 84, 84),
                 "f": (250, 190, 60), "l": (200, 190, 255), "g": (150, 140, 156), "b": (96, 150, 255),
                 "m": (222, 228, 255), "y": (250, 210, 70), "k": (130, 76, 24), "p": (200, 200, 214)}
ICONOS = {"tormenta": RAYO, "mancha": MANCHA, "reabastecimiento": COHETE, "micrometeorito": PIEDRA,
          "enfermo": CRUZ, "reciclador": GOTA, "llamada": ANTENA, "noche": LUNA}


# Los textos en inglés del mapa van aquí mismo (así no hay que tocar assets/textos_en.py).
_EN = {
    "map.ev.cohete": "A cargo rocket arrived",
    "map.ev.enfermo": "A sick crew member",
    "map.ev.llamada": "Call to Earth",
    "map.ev.mancha": "Sunspot",
    "map.ev.micro": "A micrometeorite",
    "map.ev.noche": "The lunar night falls",
    "map.ev.reciclador": "The recycler broke down",
    "map.ev.tormenta": "Solar storm",
    "map.hoy": "TODAY",
    "map.l_aviso": "warning for tomorrow",
    "map.l_cohete": "cargo rocket",
    "map.l_falta": "still to come",
    "map.l_noche": "night day",
    "map.l_sol": "day with sun",
    "map.l_tormenta": "storm",
    "map.m_noche": "NIGHT",
    "map.m_sol": "SUN",
    "map.noche": "Lunar night",
    "map.noche_en": "The lunar night starts on day {n}.",
    "map.noche_ya": "It's night now: the base runs on the reactor.",
    "map.raton": "Move the mouse over a day to see what happened.",
    "map.sol": "Days with sun",
    "map.sub": "Day {d} of {t} · {f} days to go",
    "map.sub1": "Day {d} of {t} · last day!",
    "map.tip_dia": "Day {d}",
    "map.tip_falta": "They haven't reached this day yet.",
    "map.tip_fin": "At the end: O₂ {o} kg · water {a} L · food {c} kg",
    "map.tip_hoy": "The crew is here today.",
    "map.tip_noche": "at night",
    "map.tip_sol": "with sun",
    "map.tit": "Mission map",
    "map.volver": "Back",
}


def _t(clave, es, **valores):
    """Como t() del juego, pero con el inglés de _EN."""
    plantilla = _EN.get(clave, es) if _textos.IDIOMA == "en" else es
    try:
        return plantilla.format(**valores) if valores else plantilla
    except (KeyError, IndexError, ValueError):
        return es.format(**valores) if valores else es


def _evento(juego, dia):
    """Qué evento del calendario tocó ese día ("tormenta", "cohete"...), o None."""
    ident = (juego.m.plan.get(dia) or "").partition(":")[0]
    return ident if ident in ICONOS else None


def _nombre_evento(ident):
    return {"tormenta": _t("map.ev.tormenta", "Tormenta solar"), "mancha": _t("map.ev.mancha", "Mancha solar"),
            "reabastecimiento": _t("map.ev.cohete", "Llegó un cohete de carga"),
            "micrometeorito": _t("map.ev.micro", "Un micrometeorito"),
            "enfermo": _t("map.ev.enfermo", "Un tripulante enfermo"),
            "reciclador": _t("map.ev.reciclador", "Se averió el reciclador"),
            "llamada": _t("map.ev.llamada", "Llamada a la Tierra"),
            "noche": _t("map.ev.noche", "Cae la noche lunar")}.get(ident)


# ── herramientas de pixeles ──────────────────────────────────────────────────────────────────
def _mezcla(a, b, f):
    return tuple(int(x + (y - x) * f) for x, y in zip(a, b))


def _punto(s, x, y, col):
    if 0 <= x < s.get_width() and 0 <= y < s.get_height():
        s.set_at((x, y), col)


def _sprite(s, filas, x, y, colores, contorno=None):
    """Pinta un dibujito de letras con la esquina de arriba a la izquierda en (x, y)."""
    llenas = {(i, j) for j, fila in enumerate(filas) for i, ch in enumerate(fila) if ch not in ". "}
    if contorno:
        for i, j in llenas:
            for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                if (i + di, j + dj) not in llenas:
                    _punto(s, x + i + di, y + j + dj, contorno)
    for i, j in llenas:
        _punto(s, x + i, y + j, colores[filas[j][i]])


def _centrado(s, filas, cx, cy, colores, contorno=None):
    _sprite(s, filas, cx - len(filas[0]) // 2, cy - len(filas) // 2, colores, contorno)


def _linea(a, b):
    """Los cuadritos de una línea recta de a hasta b (sin suavizar)."""
    (x0, y0), (x1, y1) = a, b
    dx, dy = abs(x1 - x0), -abs(y1 - y0)
    sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
    err, pts = dx + dy, []
    while True:
        pts.append((x0, y0))
        if (x0, y0) == (x1, y1):
            return pts
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def _ruta(total, x0, x1, ybaj, yalt, amp):
    """Dónde va cada día: sube de izquierda a derecha en zigzag, como una constelación."""
    pts = []
    for i in range(total):
        f = i / (total - 1)
        x = x0 + f * (x1 - x0)
        y = ybaj + (yalt - ybaj) * f
        if 0 < i < total - 1:
            x += (x1 - x0) / (total - 1) * 0.16 * math.sin(i * 2.7 + 1)
            y += amp * (0.62 * math.sin(i * 1.85 + 0.6) + 0.38 * math.sin(i * 0.77 + 2.1))
        pts.append((round(x), round(y)))
    return pts


# ── el tamaño de cada mapa ───────────────────────────────────────────────────────────────────
class _Medidas:
    def __init__(self, grande, w, h, total, luz):
        self.grande, self.w, self.h = grande, w, h
        self.esc = 4 if grande else 3
        if grande:
            self.pts = _ruta(total, 30, w - 28, 132, 46, 10)
        else:
            self.pts = _ruta(total, 8, w - 9, 26, 14, 3)
        a, b = self.pts[luz - 1][0], self.pts[min(luz, total - 1)][0]
        self.corte = (a + b) // 2                 # entre el último día de sol y el primero de noche
        self.forma_hoy = GRANDE if grande else ROMBO
        self.flecha = FLECHA if grande else FLECHA_CHICA


def _dia_es_noche(e, d):
    return d > e.luz


def _forma(i, total):
    return ROMBO if (i % 3 == 1 or i == total - 1) else CUADRO


# ── fondos (se dibujan una sola vez) ─────────────────────────────────────────────────────────
_FONDOS = {}


def _cielo(s, rng, cuantas):
    for _ in range(cuantas):
        _punto(s, rng.randrange(s.get_width()), rng.randrange(s.get_height()),
               ESTRELLA if rng.random() < 0.8 else ESTRELLA2)


def _sol(s, cx, cy, r):
    for y in range(cy - r - 3, cy + r + 4):
        for x in range(cx - r - 3, cx + r + 4):
            d = math.hypot(x - cx, y - cy)
            if r < d <= r + 3 and (x + y) % 2 == 0:
                _punto(s, x, y, (96, 64, 60) if d > r + 1.5 else (170, 120, 70))
    pygame.draw.circle(s, (250, 214, 84), (cx, cy), r)
    pygame.draw.circle(s, (255, 244, 190), (cx - r // 3, cy - r // 3), max(1, r // 2))


def _tierra(s, cx, cy, r):
    pygame.draw.circle(s, (40, 96, 204), (cx, cy), r)
    for dx, dy, rr in ((-2, -2, 2), (2, 1, 2), (-1, 3, 1)):
        pygame.draw.circle(s, (72, 164, 92), (cx + dx, cy + dy), rr)
    for dx, dy in ((1, -4), (2, -4), (-4, 1), (3, 4)):
        _punto(s, cx + dx, cy + dy, (232, 238, 248))
    for y in range(cy - r, cy + r + 1):           # la mitad de atrás, en sombra
        for x in range(cx + 1, cx + r + 1):
            if math.hypot(x - cx, y - cy) <= r and (x + y) % 2 == 0:
                _punto(s, x, y, (16, 30, 80))


def _fondo(med, total, luz):
    clave = (med.grande, med.w, med.h, total, luz)
    s = _FONDOS.get(clave)
    if s is not None:
        return s
    s = pygame.Surface((med.w, med.h))
    rng = random.Random(total * 31 + luz)
    if med.grande:
        for y in range(med.h):
            s.fill(_mezcla(ESPACIO, ESPACIO2, y / med.h), (0, y, med.w, 1))
        _cielo(s, rng, 260)
        xs = [p[0] for p in med.pts[:luz]]
        _sol(s, (min(xs) + max(xs)) // 2 + 30, 30, 6)
        xs = [p[0] for p in med.pts[luz:]] or [med.w - 40]
        _tierra(s, (min(xs) + max(xs)) // 2 - 10, 26, 7)
        for y in range(8, 148, 3):               # la raya donde cae la noche
            _punto(s, med.corte, y, CORTE)
        for x in range(med.w):                   # el suelo de la Luna: con sol a la izquierda
            alto = 150 + round(2 * math.sin(x * 0.07) + 1.5 * math.sin(x * 0.19 + 1))
            luz_aqui = x < med.corte - 3 or (abs(x - med.corte) <= 3 and (x + alto) % 2 == 0 and x < med.corte)
            claro, base = ((156, 152, 166), (118, 114, 130)) if luz_aqui else ((62, 62, 86), (44, 44, 62))
            s.fill(claro, (x, alto, 1, 1))
            s.fill(base, (x, alto + 1, 1, med.h - alto))
        for cx, cy, rr in ((40, 158, 6), (118, 164, 4), (210, 160, 5), (270, 166, 3)):
            pygame.draw.ellipse(s, (96, 94, 108) if cx < med.corte else (34, 34, 50), (cx - rr, cy - rr // 3, 2 * rr, rr))
    else:
        s.fill(ESPACIO)
        _cielo(s, rng, 70)
        for y in range(1, med.h - 1, 2):
            _punto(s, med.corte, y, CORTE)
        _sol(s, 5, 6, 2)
        _sprite(s, LUNA, med.corte + 4, 3, COLORES_ICONO)
    _FONDOS[clave] = s
    return s


# ── en qué va la marca (para moverla de un día al otro) ──────────────────────────────────────
def _animar():
    try:
        return pygame.display.get_driver() != "dummy"
    except pygame.error:
        return False


def _momento(juego, interactivo):
    """(día que se muestra, avance de 0 a 1+ desde el día anterior, o None si está quieta)."""
    m, e = juego.m, juego.m.e
    dia = max(1, min(e.dia, e.total))
    if getattr(juego, "_mapa_mision", None) is not m:          # misión nueva
        juego._mapa_mision, juego._mapa_visto, juego._mapa_desde, juego._mapa_dias = m, dia, None, {}
    visto = juego._mapa_visto
    if dia == visto + 1 and _animar():
        if not interactivo:
            return visto, None             # todavía en el cierre del día: la marca sigue en ayer
        juego._mapa_visto, juego._mapa_desde = dia, juego.cuadro
    elif dia != visto:
        juego._mapa_visto, juego._mapa_desde = dia, None
    if juego._mapa_desde is None:
        return dia, None
    f = (juego.cuadro - juego._mapa_desde) / DURA
    if f >= 1 + DESTELLO / DURA:
        juego._mapa_desde = None
        return dia, None
    return dia, f


def _suave(f):
    f = max(0.0, min(1.0, f))
    return f * f * (3 - 2 * f)


# ── la constelación (lo mismo para el chiquito y el grande) ──────────────────────────────────
def _constelacion(juego, med, dia, f, interactivo):
    m, e = juego.m, juego.m.e
    cuadro = juego.cuadro
    s = _fondo(med, e.total, e.luz).copy()
    if med.grande:
        rng = random.Random(5)
        for k in range(14):                       # estrellas en cruz que titilan
            x, y = rng.randrange(med.w), rng.randrange(140)
            if math.sin(cuadro * 0.05 + k * 1.7) > 0.55:
                _sprite(s, (".a.", "aaa", ".a."), x - 1, y - 1, {"a": ESTRELLA2})
    viajando = f is not None and f < 1
    hoy = dia - 1
    pts = med.pts
    # la línea: lo recorrido, fuerte; lo que falta, punteado
    for i in range(len(pts) - 1):
        cuadritos = _linea(pts[i], pts[i + 1])
        if i < hoy - 1 or (i == hoy - 1 and not viajando):
            for p in cuadritos:
                _punto(s, *p, LINEA)
        elif i == hoy - 1:
            corte = int(len(cuadritos) * _suave(f))
            for k, p in enumerate(cuadritos):
                _punto(s, *p, LINEA if k <= corte else (LINEA_FUT if k % 3 else ESPACIO))
        else:
            for k, p in enumerate(cuadritos):
                if k % 3:
                    _punto(s, *p, LINEA_FUT)
    # los nodos
    for i, (x, y) in enumerate(pts):
        d = i + 1
        if d < dia or (d == dia and not viajando):
            clase = "noche" if _dia_es_noche(e, d) else "sol"
        else:
            clase = "falta"
        if d == dia and not viajando:
            continue                              # el de hoy va al final, encima de todo
        b, c = PALETA[clase]
        _centrado(s, _forma(i, len(pts)), x, y, {"b": b, "c": c})
        if med.grande and d < dia and _evento(juego, d):
            filas = ICONOS[_evento(juego, d)]
            _sprite(s, filas, x - len(filas[0]) // 2, y - 5 - len(filas), COLORES_ICONO, OSCURO)
    # la meta
    xm, ym = pts[-1]
    _sprite(s, BANDERA, xm + 2, ym - 7 if med.grande else ym - 6, COLORES_ICONO, OSCURO)
    # el aviso de mañana
    if m.pronostico and dia < e.total and (interactivo or med.grande) and (cuadro // 20) % 3:
        x, y = pts[dia]
        if med.grande:
            _sprite(s, AVISO, x, y - 10, COLORES_ICONO, OSCURO)
        pygame.draw.circle(s, C["naranja"], (x, y), 4 if med.grande else 3, 1)
    # la marca de hoy: viaja desde ayer y al llegar echa un destello
    x, y = pts[hoy]
    if viajando:
        xa, ya = pts[hoy - 1]
        g = _suave(f)
        x, y = round(xa + (x - xa) * g), round(ya + (y - ya) * g)
    clase = "noche" if _dia_es_noche(e, dia) else "sol"
    borde = PALETA[clase][0]
    r = len(med.forma_hoy) // 2
    paso = 1 if (cuadro // 18) % 2 else 0
    for yy in range(y - r - 3 - paso, y + r + 4 + paso):        # halo de cuadritos
        for xx in range(x - r - 3 - paso, x + r + 4 + paso):
            dd = abs(xx - x) + abs(yy - y)
            if r < dd <= r + 2 + paso and (xx + yy) % 2 == 0:
                _punto(s, xx, yy, _mezcla(borde, ESPACIO, 0.55))
    _centrado(s, med.forma_hoy, x, y, {"b": borde, "c": (255, 255, 255)})
    if (cuadro // 14) % 2:                                       # chispitas
        for dx, dy in ((r + 2, 0), (-r - 2, 0), (0, r + 2), (0, -r - 2)):
            _punto(s, x + dx, y + dy, PALETA[clase][1])
    if f is not None and f >= 1:
        b = (f - 1) * DURA / DESTELLO
        pygame.draw.circle(s, _mezcla((255, 255, 255), ESPACIO, b), (x, y), round(r + 2 + b * (10 if med.grande else 6)), 1)
    bote = round(math.sin(cuadro * 0.13) * (2 if med.grande else 1))
    fl = med.flecha
    _sprite(s, fl, x - len(fl[0]) // 2, y - r - 2 - len(fl) + bote, COLORES_FLECHA, OSCURO)
    return s, (x, y)


# ── el chiquito, en la barra del tablero ─────────────────────────────────────────────────────
class _Zona:
    """Un botón invisible (el mapa chiquito se abre con un clic)."""
    def __init__(self, rect, accion):
        self.rect, self.accion = pygame.Rect(rect), accion
        self.texto, self.activo, self.tecla, self.color, self.tam, self.negrita = "", True, None, "panel", 16, True


def dibujar_mini(juego, rect, interactivo):
    m, e = juego.m, juego.m.e
    dia, f = _momento(juego, interactivo)
    if interactivo and m.decision is not None:
        juego._mapa_dias[e.dia] = m.decision.titulo          # para el cartelito del mapa grande
    rect = pygame.Rect(rect)
    med = _Medidas(False, rect.w // 3, rect.h // 3, e.total, e.luz)
    s, _ = _constelacion(juego, med, dia, f, interactivo)
    encima = interactivo and rect.collidepoint(juego.mouse)
    marco = C["oro"] if encima else (82, 64, 168)
    for x in range(1, med.w - 1):                 # marco de cuadritos con las esquinas cortadas
        _punto(s, x, 0, marco)
        _punto(s, x, med.h - 1, marco)
    for y in range(1, med.h - 1):
        _punto(s, 0, y, marco)
        _punto(s, med.w - 1, y, marco)
    for x, y in ((0, 0), (med.w - 1, 0), (0, med.h - 1), (med.w - 1, med.h - 1)):
        s.set_at((x, y), C["panel"])
    juego.lienzo.blit(pygame.transform.scale(s, (med.w * 3, med.h * 3)), rect.topleft)
    letra = fuente_pixel(8)
    juego.lienzo.blit(letra.render(pixel(_t("map.m_sol", "SOL")), False, (226, 196, 110)), (rect.x + 30, rect.y + 13))
    juego.lienzo.blit(letra.render(pixel(_t("map.m_noche", "NOCHE")), False, (150, 190, 236)),
                      (rect.x + (med.corte + 11) * 3, rect.y + 13))
    if interactivo:
        juego.botones.append(_Zona(rect, juego.abrir_mapa))


# ── el grande, en su propia pantalla ─────────────────────────────────────────────────────────
LEYENDA = (("sol", None), ("noche", None), ("falta", None), ("tormenta", RAYO), ("cohete", COHETE),
           ("aviso", AVISO))


class MapaMixin:
    def abrir_mapa(self):
        self._abrir("mapa")

    def cerrar_mapa(self):
        self.fase = self.volver_a

    def _mapa(self):
        m, e = self.m, self.m.e
        dia, f = _momento(self, True)
        med = _Medidas(True, ANCHO // 4, ALTO // 4, e.total, e.luz)
        s, _ = _constelacion(self, med, dia, f, True)
        self.lienzo.blit(pygame.transform.scale(s, (ANCHO, ALTO)), (0, 0))
        # título y en qué va la misión
        self.pix(_t("map.tit", "Mapa de la misión"), 24, "oro", 40, 28)
        falta = e.total - dia
        self.txt(_t("map.sub", "Día {d} de {t} · faltan {f} días", d=dia, t=e.total, f=falta) if falta else
                 _t("map.sub1", "Día {d} de {t} · ¡último día!", d=dia, t=e.total), 22, "texto", 40, 66, True)
        self.txt(_t("map.noche_en", "La noche lunar empieza el día {n}.", n=e.luz + 1) if dia <= e.luz else
                 _t("map.noche_ya", "Ya es de noche: la base vive del reactor."), 18, "gris", 40, 98)
        if m.pronostico and dia < e.total:
            self.txt(m.pronostico, 18, "naranja", 40, 124)
        # los nombres de las dos mitades
        xs = [p[0] for p in med.pts[:e.luz]]
        self.pix(_t("map.sol", "Días con sol"), 10, (230, 200, 120), ((min(xs) + max(xs)) // 2 + 30) * 4, 44 * 4,
                 centro=True)
        xs = [p[0] for p in med.pts[e.luz:]] or [med.w - 40]
        self.pix(_t("map.noche", "Noche lunar"), 10, (150, 190, 236), ((min(xs) + max(xs)) // 2 - 10) * 4, 39 * 4,
                 centro=True)
        # el número de cada día, debajo del nodo
        letra = fuente_pixel(8)
        for i, (x, y) in enumerate(med.pts):
            d = i + 1
            col = C["oro"] if d == dia else (C["gris"] if d < dia else (110, 98, 170))
            img = letra.render(str(d), False, col)
            abajo = 6 if _forma(i, e.total) is ROMBO or d == dia else 5
            self.lienzo.blit(img, img.get_rect(midtop=(x * 4 + 2, (y + abajo) * 4)))
        # «HOY» encima de la flecha
        x, y = med.pts[dia - 1]
        if f is None or f >= 1:
            self.pix(_t("map.hoy", "HOY"), 10, "oro", x * 4 + 2, (y - 14) * 4, centro=True)
        # la leyenda y el botón de volver
        caja = self.caja((24, 640, ANCHO - 48, 64), "panel")
        xx = caja.x + 22
        for clave, icono in LEYENDA:
            g = pygame.Surface((7, 7), pygame.SRCALPHA)
            if icono is None:
                b, c = PALETA[clave]
                _centrado(g, ROMBO, 3, 3, {"b": b, "c": c})
            else:
                _sprite(g, icono, (7 - len(icono[0])) // 2, (7 - len(icono)) // 2,
                        COLORES_ICONO, OSCURO)
            self.lienzo.blit(pygame.transform.scale(g, (28, 28)), (xx, caja.centery - 14))
            r = self.txt({"sol": _t("map.l_sol", "día con sol"), "noche": _t("map.l_noche", "día de noche"),
                          "falta": _t("map.l_falta", "lo que falta"), "tormenta": _t("map.l_tormenta", "tormenta"),
                          "cohete": _t("map.l_cohete", "cohete de carga"),
                          "aviso": _t("map.l_aviso", "aviso de mañana")}[clave], 16, "texto", xx + 34,
                         caja.centery - 11)
            xx = r.right + 26
        self.boton((ANCHO - 230, caja.y + 10, 190, 44), _t("map.volver", "Volver"), self.cerrar_mapa, tam=18,
                   tecla=pygame.K_RETURN)
        self.txt(_t("map.raton", "Pasá el ratón por un día para ver qué pasó."), 15, "gris2", 40, 150)
        # el cartelito del día que está debajo del ratón
        for i, (x, y) in enumerate(med.pts):
            cx, cy = x * 4 + 2, y * 4 + 2
            if abs(self.mouse[0] - cx) <= 14 and abs(self.mouse[1] - cy) <= 14:
                self._cartel_dia(i + 1, dia, cx, cy)
                break

    def _cartel_dia(self, d, dia, cx, cy):
        m, e = self.m, self.m.e
        noche = _dia_es_noche(e, d)
        renglones = [(_t("map.tip_dia", "Día {d}", d=d) + " · " +
                      (_t("map.tip_noche", "de noche") if noche else _t("map.tip_sol", "con sol")), "oro")]
        if d < dia or d == dia:
            titulo = getattr(self, "_mapa_dias", {}).get(d) or _nombre_evento(_evento(self, d))
            if titulo:
                renglones.append((titulo, "texto"))
            if d == dia:
                renglones.append((_t("map.tip_hoy", "Están aquí hoy."), "cian"))
            elif len(m.historial) > d:
                h = m.historial[d]
                renglones.append((_t("map.tip_fin", "Al terminar: O₂ {o} kg · agua {a} L · comida {c} kg",
                                    o=n(h["o2"]), a=n(h["agua"]), c=n(h["comida"])), "gris"))
        elif d == dia + 1 and m.pronostico:
            renglones.append((m.pronostico, "naranja"))
        else:
            renglones.append((_t("map.tip_falta", "Todavía no llegan a este día."), "gris"))
        from ..assets.texto_mate import fuente
        imgs = [fuente(17, k == 0).render(txt, True, C[col]) for k, (txt, col) in enumerate(renglones)]
        w = max(i.get_width() for i in imgs) + 28
        h = sum(i.get_height() + 4 for i in imgs) + 20
        x = min(max(16, cx - w // 2), ANCHO - w - 16)
        y = cy - h - 34 if cy - h - 34 > 170 else cy + 36
        self.caja((x, y, w, h), "panel", "oro", radio=10)
        yy = y + 12
        for img in imgs:
            self.lienzo.blit(img, (x + 14, yy))
            yy += img.get_height() + 4
