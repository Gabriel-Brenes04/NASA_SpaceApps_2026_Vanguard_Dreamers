# -*- coding: utf-8 -*-
"""Microjuego «Estiba» (tarea: estiba → más carga del cohete que llegó hoy).

Llegó el cohete de carga y hay que guardar las bolsas en la bodega del hábitat. La bodega tiene una
SECCIÓN POR TIPO (agua, comida, O₂ y repuestos), como los lugares fijos de una estación espacial; cada
tipo tiene su color y su dibujo (gota, manzana, O₂, engranaje), así se distingue aunque no se vean bien
los colores. Cada sección tiene 3 columnas y 6 filas.

Cómo se juega (45 s):
  · la bolsa cuelga de la grúa, que sigue al ratón; clic en la bodega = soltarla (cae a lo más alto que
    haya debajo);
  · clic EN LA BOLSA (o clic derecho, o la rueda del ratón) = girarla (acostada ↔ parada);
  · CAMBIAR: un clic en una bolsa de la cinta la cambia por la que cuelga de la grúa (sirve cuando la de
    turno no cabe, o cuando otra encaja mejor);
  · si la de turno no cabe en su sección, ni girada, la grúa la devuelve sola a la cinta a los pocos
    segundos (sin castigo);
  · en la sección equivocada cae igual y OCUPA LUGAR, pero resta puntos y 2 segundos del reloj (y al
    sellar esa sección, el premio baja);
  · si una bolsa queda montada y abajo queda un HUECO, se pierden puntos;
  · fila completa en una sección = puntos extra; sección llena = se SELLA y la carga va a la despensa;
  · desde el nivel 2 viene a veces el KIT PERSONAL (morado, con estrella): cabe en cualquier sección.
Al subir de nivel aparecen bolsas triples paradas y la grúa da poco tiempo para soltar.

Dato real (NASA): en la Estación Espacial la carga viaja en bolsas de tela de tamaños fijos (media,
sencilla, doble y triple); una sencilla mide unos 50 × 42 × 25 cm. Fuente: Baccus, Broyan y Borrego
(2016), «Multipurpose Cargo Transfer Bags for Reducing Exploration Mission Logistics», NASA JSC,
pág. 2 — https://ntrs.nasa.gov/citations/20160002631
"""
import math

import pygame

from .base import ZONA, COLORES
from ._kit import Partida, luz, degradado, guardado, texto, mezclar, translucido, estrella
<<<<<<< HEAD:base_lunar/microjuegos/estiba.py
from .. import sonido
from ..textos import t, n
=======
from ..assets import sonido
from ..assets.textos import t, n
>>>>>>> datos:game/minijuegos/estiba.py

CELDA, ANCHO_SEC, FILAS = 50, 3, 6
ORDEN = ("agua", "comida", "o2", "repuestos")
COLS = ANCHO_SEC * len(ORDEN)
BODEGA = pygame.Rect(400, 620 - FILAS * CELDA, COLS * CELDA, FILAS * CELDA)    # x 400-1000, y 320-620
RIEL_Y = 226
TIPOS = {"agua": (66, 128, 230), "comida": (64, 172, 92), "o2": (56, 180, 200), "repuestos": (226, 136, 46),
         "personal": (170, 110, 225)}
DESPENSA = pygame.Rect(1024, 320, 202, 300)
PUERTA = pygame.Rect(62, 200, 236, 236)
CINTA = pygame.Rect(ZONA.left + 12, 588, BODEGA.left - ZONA.left - 46, 26)
ESC_COLA = 30                 # píxeles por celda en las bolsas de la cinta
EN_COLA = 3                   # cuántas bolsas se ven (y se pueden escoger) en la cinta
DEVUELVE = 4.0                # segundos que la grúa espera con una bolsa que no cabe
CASTIGO_CELDA = 6             # puntos que resta cada celda de carga puesta en la sección equivocada
CASTIGO_TIEMPO = 2.0          # y los segundos que le quita al reloj


def seccion(c):
    return ORDEN[c // ANCHO_SEC]


def _icono(sup, tipo, cx, cy, color, fondo, esc=1.0):
    if tipo == "agua":                                         # gota
        pygame.draw.circle(sup, color, (cx, int(cy + 5 * esc)), int(10 * esc))
        pygame.draw.polygon(sup, color, [(cx - 9 * esc, cy + 1 * esc), (cx + 9 * esc, cy + 1 * esc), (cx, cy - 16 * esc)])
    elif tipo == "comida":                                     # manzana
        pygame.draw.circle(sup, color, (cx, int(cy + 3 * esc)), int(12 * esc))
        pygame.draw.line(sup, color, (cx, cy - 8 * esc), (cx + 2 * esc, cy - 15 * esc), max(1, int(3 * esc)))
        pygame.draw.ellipse(sup, color, (cx + 3 * esc, cy - 17 * esc, 10 * esc, 6 * esc))
    elif tipo == "o2":
<<<<<<< HEAD:base_lunar/microjuegos/estiba.py
        from ..texto_mate import fuente
=======
        from ..assets.texto_mate import fuente
>>>>>>> datos:game/minijuegos/estiba.py
        img = fuente(max(10, int(22 * esc)), True).render("O₂", True, color[:3])
        if len(color) > 3:
            img.set_alpha(color[3])
        sup.blit(img, img.get_rect(center=(cx, cy)))
    elif tipo == "personal":                                   # estrella
        estrella(sup, cx, cy, 14 * esc, color)
    else:                                                      # engranaje
        for k in range(8):
            a = k * math.pi / 4
            pygame.draw.circle(sup, color, (int(cx + math.cos(a) * 12 * esc), int(cy + math.sin(a) * 12 * esc)),
                               max(1, int(4 * esc)))
        pygame.draw.circle(sup, color, (cx, cy), int(11 * esc))
        pygame.draw.circle(sup, fondo, (cx, cy), max(1, int(5 * esc)))


def _bolsa(w, h, tipo, alfa=255):
    """Una bolsa de tela (en píxeles w × h), con su correa y su etiqueta blanca con el dibujo."""
    def hacer():
        col = TIPOS[tipo]
        s = pygame.Surface((w, h), pygame.SRCALPHA)
        r = s.get_rect().inflate(-4, -4)
        rad = max(4, min(12, min(r.w, r.h) // 4))
        pygame.draw.rect(s, (*mezclar(col, (0, 0, 0), 0.35), alfa), r.move(0, 2), border_radius=rad)
        pygame.draw.rect(s, (*col, alfa), r, border_radius=rad)
        pygame.draw.rect(s, (*mezclar(col, (255, 255, 255), 0.25), alfa), (r.x + 3, r.y + 3, r.w - 6, r.h // 3),
                         border_radius=rad)
        if r.h >= 30:
            for x in range(r.left + 7, r.right - 7, 8):                # costura
                pygame.draw.line(s, (*mezclar(col, (0, 0, 0), 0.45), alfa), (x, r.bottom - 5), (x + 3, r.bottom - 5), 2)
            pygame.draw.line(s, (*mezclar(col, (0, 0, 0), 0.5), alfa), (r.centerx - 12, r.top + 2), (r.centerx + 12, r.top + 2), 4)
        lado = min(r.w, r.h)
        esc = 1.0 if lado >= 60 else 0.62 if lado >= 40 else 0.36
        et = pygame.Rect(0, 0, int(40 * esc), int(40 * esc))
        et.center = r.center
        pygame.draw.rect(s, (245, 245, 238, alfa), et, border_radius=max(2, int(6 * esc)))
        _icono(s, tipo, et.centerx, et.centery + int(2 * esc), (*col, alfa), (245, 245, 238, alfa), esc * 0.85)
        pygame.draw.rect(s, (*mezclar(col, (255, 255, 255), 0.5), alfa), r, 2, border_radius=rad)
        return s
    return guardado(("bolsa", w, h, tipo, alfa), hacer)


def _fondo():
    import random
    rng = random.Random(6)
    s = pygame.Surface(ZONA.size)
    s.blit(degradado(ZONA.w, ZONA.h, (34, 40, 64), (16, 19, 34)), (0, 0))
    for x in range(0, ZONA.w, 110):                                    # costillas del hangar
        pygame.draw.rect(s, (26, 31, 52), (x, 0, 14, ZONA.h))
        pygame.draw.line(s, (48, 56, 88), (x + 14, 0), (x + 14, ZONA.h), 1)
    # la puerta del hangar con el cohete afuera
    p = PUERTA.move(-ZONA.left, -ZONA.top)
    pygame.draw.rect(s, (4, 5, 14), p)
    for _ in range(60):
        b = rng.randint(80, 220)
        s.set_at((rng.randint(p.left, p.right - 1), rng.randint(p.top, p.top + 130)), (b, b, b))
    suelo = [(p.left, p.bottom)] + [(x, p.top + 178 + 6 * math.sin(x / 30)) for x in range(p.left, p.right + 1, 10)] + [(p.right, p.bottom)]
    pygame.draw.polygon(s, (88, 84, 80), suelo)
    cx = p.centerx + 30
    pygame.draw.polygon(s, (214, 218, 228), [(cx - 28, p.top + 92), (cx, p.top + 26), (cx + 28, p.top + 92)])
    pygame.draw.rect(s, (196, 202, 216), (cx - 28, p.top + 92, 56, 88))
    pygame.draw.rect(s, (60, 66, 90), (cx - 12, p.top + 116, 24, 34), border_radius=4)
    pygame.draw.circle(s, (120, 180, 255), (cx, p.top + 80), 8)
    for dx in (-1, 1):
        pygame.draw.line(s, (150, 156, 170), (cx + dx * 26, p.top + 168), (cx + dx * 44, p.top + 194), 5)
    pygame.draw.rect(s, (110, 118, 150), p.inflate(16, 16), 8, border_radius=6)
    for y in range(p.top, p.bottom, 26):                               # rayas de la puerta
        pygame.draw.line(s, (230, 190, 40) if (y // 26) % 2 else (30, 30, 30), (p.left - 8, y), (p.left - 8, y + 13), 6)
    # piso
    piso = pygame.Rect(0, 512, ZONA.w, ZONA.h - 512)
    s.blit(degradado(piso.w, piso.h, (44, 46, 62), (22, 24, 36)), piso)
    pygame.draw.line(s, (80, 86, 112), (0, piso.top), (ZONA.w, piso.top), 3)
    # el riel de la grúa
    y = RIEL_Y - ZONA.top
    pygame.draw.rect(s, (90, 98, 128), (BODEGA.left - ZONA.left - 40, y - 8, BODEGA.w + 80, 16), border_radius=4)
    pygame.draw.line(s, (150, 160, 190), (BODEGA.left - ZONA.left - 40, y - 7), (BODEGA.right - ZONA.left + 40, y - 7), 2)
    for x in (BODEGA.left - ZONA.left - 30, BODEGA.right - ZONA.left + 30):
        pygame.draw.rect(s, (70, 76, 104), (x - 8, y, 16, BODEGA.top - RIEL_Y))
    # la bodega: marco y secciones
    b = BODEGA.move(-ZONA.left, -ZONA.top)
    pygame.draw.rect(s, (24, 28, 48), b)
    for k, tipo in enumerate(ORDEN):
        col = TIPOS[tipo]
        sec = pygame.Rect(b.left + ANCHO_SEC * k * CELDA, b.top, ANCHO_SEC * CELDA, b.h)
        s.blit(degradado(sec.w, sec.h, tuple(14 + v // 6 for v in col), tuple(22 + v // 3 for v in col)), sec)
        icono = pygame.Surface(sec.size, pygame.SRCALPHA)
        _icono(icono, tipo, sec.w // 2, sec.h // 2, (*col, 70), (*tuple(18 + v // 4 for v in col), 255), 2.4)
        s.blit(icono, sec.topleft)
        pygame.draw.rect(s, col, (sec.x + 4, b.bottom - 6, sec.w - 8, 6))
    for i in range(COLS + 1):
        grueso = i % ANCHO_SEC == 0
        pygame.draw.line(s, (96, 106, 140) if grueso else (44, 52, 84), (b.left + i * CELDA, b.top),
                         (b.left + i * CELDA, b.bottom), 4 if grueso else 1)
    for j in range(1, FILAS):
        pygame.draw.line(s, (44, 52, 84), (b.left, b.top + j * CELDA), (b.right, b.top + j * CELDA))
    pygame.draw.rect(s, (150, 158, 184), b.inflate(14, 14), 7, border_radius=6)
    # la despensa
    d = DESPENSA.move(-ZONA.left, -ZONA.top)
    pygame.draw.rect(s, (18, 22, 40), d, border_radius=14)
    pygame.draw.rect(s, (64, 76, 116), d, 2, border_radius=14)
    return s


class Estiba(Partida):
    titulo = "Estiba: guardá la carga"
    instruccion = "Soltá cada bolsa en la sección de su tipo, sin dejar huecos"
    tarea = "estiba"
    duracion = 45.0
    META = 5000
    ESCALA = 25
    COLOR = (230, 160, 70)

    def preparar(self):
        self.titulo = t("mj.estiba.titulo", "Estiba: guardá la carga")
        self.instruccion = t("mj.estiba.instr", "Soltá cada bolsa en la sección de su tipo, sin dejar huecos")
        self.consejos = (t("mj.estiba.c5", "Clic en la bolsa = girarla · clic en la bodega = soltarla."),
                         t("mj.estiba.c4", "¿No cabe o hay otra mejor? Hacé clic en una bolsa de la cinta para cambiarla."),
                         t("mj.estiba.c6", "En la sección equivocada cae igual, pero ocupa lugar y resta puntos y 2 segundos."))
        self.alto = [0] * COLS
        self.lleno = [[False] * FILAS for _ in range(COLS)]
        self.huecos = []                 # (columna, fila)
        self.bolsas = []                 # c, fila, w, h, tipo, caida, vel, sale
        self.guardadas = 0
        self.cambios = 0
        self.malas = 0                   # bolsas puestas en la sección equivocada
        self.girada_veces = 0
        self.despensa = {k: 0 for k in ORDEN}
        self.espera = 0.0                # la grúa está devolviendo o cambiando una bolsa
        self.reloj_grua = None           # tiempo que queda para soltar (desde el nivel 3)
        self.atorada = 0.0               # segundos que lleva colgando una bolsa que no cabe
        self.cola = [self._nueva() for _ in range(EN_COLA + 1)]
        self.actual = self.cola.pop(0)
        self.grua_x = float(BODEGA.centerx)
        self.grua_v = 0.0
        self.giro = 0.0                  # balanceo de la bolsa (radianes)
        self.giro_v = 0.0
        self.cinta = 0.0
        self.sello = {}                  # sección -> brillo al sellarse
        self.salto_cola = {}             # índice de la cinta -> brinquito al cambiar

    # ── las bolsas ───────────────────────────────────────────────────────────────────
    def _formas(self):
        formas = [((1, 1), 3), ((2, 1), 3), ((1, 2), 3), ((2, 2), 2)]
        if self.nv >= 2:
            formas.append(((3, 1), 2))
        if self.nv >= 3:
            formas.append(((1, 3), 2))
        return formas

    def _nueva(self):
        if self.nv >= 2 and self.rng.random() < 0.08:           # el kit personal: cabe en cualquier sección
            return {"w": 1, "h": 1, "tipo": "personal", "id": self.rng.random()}
        tipos = list(ORDEN)
        if self.rng.random() < 0.6:                            # un poco más de lo que más falta acomodar
            tipos.sort(key=lambda k: sum(self.alto[self._cols(k)[0]:self._cols(k)[-1] + 1]))
            tipo = self.rng.choice(tipos[:2])
        else:
            tipo = self.rng.choice(tipos)
        formas = self._formas()
        if self.rng.random() < 0.7:                            # casi siempre, una que encaje sin huecos
            buenas = [(f, p) for f, p in formas if self._encaja(tipo, *f)]
            if buenas:
                formas = buenas
        w, h = self.rng.choices([f for f, _ in formas], [p for _, p in formas])[0]
        return {"w": w, "h": h, "tipo": tipo, "id": self.rng.random()}

    @staticmethod
    def _cols(tipo):
        s = ORDEN.index(tipo)
        return list(range(ANCHO_SEC * s, ANCHO_SEC * s + ANCHO_SEC))

    def _encaja(self, tipo, w, h):
        b = {"w": w, "h": h, "tipo": tipo}
        for o in [b] + ([self.girada(b)] if self.girada(b) else []):
            if any(self.cabe(o, c) and not self.huecos_si(o, c) for c in self.columnas(o)):
                return True
        return False

    def girada(self, b):
        if b["w"] == b["h"]:
            return None                                   # las cuadradas no cambian
        return {**b, "w": b["h"], "h": b["w"]}

    def x_col(self, c, w):
        return BODEGA.left + (c + w / 2) * CELDA

    def columna(self, x, w):
        """La columna más cercana a x donde la bolsa queda entera dentro de una sección."""
        validas = [c for c in range(0, COLS - w + 1) if c // ANCHO_SEC == (c + w - 1) // ANCHO_SEC]
        return min(validas, key=lambda c: abs(self.x_col(c, w) - x))

    def entra(self, b, c):
        """¿Entra físicamente ahí (sea o no su sección)?"""
        return c + b["w"] <= COLS and self._apoyo(c, b["w"]) + b["h"] <= FILAS

    def rect_colgada(self):
        """Dónde está la bolsa que cuelga de la grúa (un poco más grande, para atinarle con el clic)."""
        b = self.actual
        w, h = b["w"] * CELDA, b["h"] * CELDA
        largo = 26 - int(70 * min(1.0, self.espera / 0.8))
        cx = self.grua_x - math.sin(self.giro) * (largo + h / 2)
        cy = RIEL_Y + 6 + math.cos(self.giro) * (largo + h / 2)
        r = pygame.Rect(0, 0, w + 16, h + 16)
        r.center = (int(cx), int(cy))
        return r

    def _apoyo(self, c, w):
        return max(self.alto[c:c + w])

    def en_su_seccion(self, b, c):
        if b["tipo"] == "personal":
            return c // ANCHO_SEC == (c + b["w"] - 1) // ANCHO_SEC
        return all(seccion(cc) == b["tipo"] for cc in range(c, c + b["w"]))

    def cabe(self, b, c):
        return c + b["w"] <= COLS and self.en_su_seccion(b, c) and self._apoyo(c, b["w"]) + b["h"] <= FILAS

    def columnas(self, b):
        """Las columnas donde puede empezar la bolsa (sin salirse de una sección)."""
        return [c for c in range(0, COLS - b["w"] + 1) if c // ANCHO_SEC == (c + b["w"] - 1) // ANCHO_SEC]

    def huecos_si(self, b, c):
        f = self._apoyo(c, b["w"])
        return sum(f - self.alto[cc] for cc in range(c, c + b["w"]))

    def cabe_algo(self, b):
        """¿Cabe en alguna parte (como viene o girada)?"""
        opciones = [b] + ([self.girada(b)] if self.girada(b) else [])
        return any(self.cabe(o, c) for o in opciones for c in self.columnas(o))

    def rects_cola(self):
        """Dónde está dibujada cada bolsa de la cinta (para escogerla con un clic)."""
        out = []
        x = CINTA.right - 12
        for i, b in enumerate(self.cola[:EN_COLA]):
            w, h = b["w"] * ESC_COLA, b["h"] * ESC_COLA
            x -= w
            out.append(pygame.Rect(x, CINTA.top + 4 - h, w, h))
            x -= 12
        return out

    # ── juego ────────────────────────────────────────────────────────────────────────
    def jugar(self, dt):
        self.espera = max(0.0, self.espera - dt)
        for ev in self.eventos:                          # girar también con clic derecho o la rueda
            if (ev.type == pygame.MOUSEBUTTONDOWN and getattr(ev, "button", 1) == 3) or ev.type == pygame.MOUSEWHEEL:
                self._girar()
        cabe = self.cabe_algo(self.actual)
        if self.nv >= 3 and self.espera <= 0 and cabe:
            if self.reloj_grua is None:
                self.reloj_grua = self.tiempo_grua()
            self.reloj_grua -= dt
            if self.reloj_grua <= 0:
                self.perder(self.grua_x, BODEGA.top - 40, t("mj.estiba.tarde", "¡Se acabó el tiempo!"), bajar=0.5,
                            son="noentra")
                self.cola.insert(EN_COLA - 1, self.actual)
                self._siguiente()
        # si no cabe en ningún lado, la grúa la devuelve sola a la cinta (sin castigo)
        self.atorada = self.atorada + dt if (not cabe and self.espera <= 0) else 0.0
        if self.atorada >= DEVUELVE:
            self.fx.texto(self.grua_x, BODEGA.top - 50, t("mj.estiba.devuelve", "La grúa la devuelve"), COLORES["gris"],
                          18, 1.0, 25)
            sonido.play("clac", 0.5)
            self.cola.insert(EN_COLA - 1, self.actual)
            self._siguiente()
            self.espera = 0.4
        for x, y in self.clics:
            i = next((k for k, r in enumerate(self.rects_cola()) if r.inflate(14, 14).collidepoint(x, y)), None)
            if i is not None:                            # clic en la cinta: cambiarla
                self._cambiar(i)
                break
            colgada = self.rect_colgada()
            if colgada.collidepoint(x, y):               # clic en la bolsa misma: girarla
                self._girar()
                break
            if (self.espera <= 0 and BODEGA.left - 50 <= x <= BODEGA.right + 50 and colgada.top <= y <= ZONA.bottom):
                self._soltar(self.columna(self.grua_x, self.actual["w"]))    # clic en la bodega: soltarla
                break

    def _girar(self):
        g = self.girada(self.actual)
        if g and self.espera <= 0:
            self.actual = g
            self.girada_veces += 1
            sonido.play("clac", 0.6)
            self.giro_v += 2.5

    def tiempo_grua(self):
        return max(2.6, 7.5 - 0.75 * (self.nv - 3))

    def _siguiente(self):
        self.actual = self.cola.pop(0)
        while len(self.cola) < EN_COLA + 1:
            self.cola.append(self._nueva())
        self.reloj_grua = None
        self.atorada = 0.0

    def _cambiar(self, i):
        """Cambia la bolsa de la grúa por la i-ésima de la cinta."""
        self.actual, self.cola[i] = self.cola[i], self.actual
        self.cambios += 1
        self.espera = 0.3
        self.atorada = 0.0
        self.salto_cola[i] = 0.3
        self.giro_v += 3.0
        sonido.play("clac", 0.7)

    def _soltar(self, c):
        b = self.actual
        x = self.x_col(c, b["w"])
        if not self.entra(b, c):                         # no hay lugar: la columna está llena
            self.espera = 0.8
            self.perder(x, BODEGA.top - 30, t("mj.estiba.nocabe", "¡No cabe ahí!"), bajar=0.3, son="noentra")
            return
        mala = not self.en_su_seccion(b, c)              # la sección equivocada: cae igual, pero cuesta
        fila = self._apoyo(c, b["w"])
        nuevos = []
        for cc in range(c, c + b["w"]):
            for ff in range(self.alto[cc], fila):
                nuevos.append((cc, ff))
            for ff in range(fila, fila + b["h"]):
                self.lleno[cc][ff] = True
            self.alto[cc] = fila + b["h"]
        self.huecos += nuevos
        caida = RIEL_Y + 34 - self._y(fila, b["h"])
        self.bolsas.append({"c": c, "fila": fila, "w": b["w"], "h": b["h"], "tipo": b["tipo"], "caida": caida,
                            "vel": 0.0, "sale": None, "aplasta": 0.0, "mala": mala})
        self.guardadas += 1
        sonido.play("soltar", 0.8)
        cx, cy = x, self._y(fila, b["h"])
        s = c // ANCHO_SEC
        cols = list(range(ANCHO_SEC * s, ANCHO_SEC * s + ANCHO_SEC))
        if mala:
            celdas = b["w"] * b["h"]
            self.malas += 1
            self.perder(cx, cy - 10, t("mj.estiba.equivocada", "¡Sección equivocada!"),
                        castigo=CASTIGO_CELDA * celdas + 8 * len(nuevos), bajar=0.5, son="noentra")
            self.tj = min(self.duracion, self.tj + CASTIGO_TIEMPO)                  # y le quita tiempo
            self.fx.texto(cx, cy + 30, t("mj.estiba.menos_s", "−{s} s", s=n(CASTIGO_TIEMPO, 0)), COLORES["rojo"], 22)
            self.fx.sacudir(5, 0.25)
        elif nuevos:
            self.perder(cx, cy - 10, t("mj.estiba.hueco", "¡Hueco!"), castigo=8 * len(nuevos), bajar=0.3, son="hueco")
        else:
            extra = 6 if b["tipo"] == "personal" else 0
            self.ganar(4 * b["w"] * b["h"] + extra, cx, cy - 10, subir=0.25)
            for ff in range(fila, fila + b["h"]):            # esta bolsa completó una fila de la sección
                if all(self.lleno[cc][ff] for cc in cols):
                    self.ganar(10, BODEGA.left + (cols[0] + 1.5) * CELDA, self._y(ff, 1) + CELDA // 2,
                               t("mj.estiba.fila", "¡Fila!"), COLORES["amarillo"], subir=0.05, combo=False, nota=False)
                    break
        self._siguiente()
        if all(self.alto[cc] >= FILAS for cc in cols):
            self._sellar(s)

    def _sellar(self, s):
        tipo = ORDEN[s]
        cols = list(range(ANCHO_SEC * s, ANCHO_SEC * s + ANCHO_SEC))
        huecos = [h for h in self.huecos if h[0] in cols]
        malas = sum(b["w"] * b["h"] for b in self.bolsas if b.get("mala") and b["sale"] is None and b["c"] // ANCHO_SEC == s)
        x, y = BODEGA.left + (cols[0] + 1.5) * CELDA, BODEGA.top + 40
        pts = max(0, 90 - 20 * len(huecos) - 15 * malas)
        if malas:
            frase = t("mj.estiba.sellada_m", "Sellada (con carga equivocada)")
        elif huecos:
            frase = t("mj.estiba.sellada_h", "Sellada (con huecos)")
        else:
            frase = t("mj.estiba.sellada", "¡Sección llena!")
        if pts > 0:
            self.ganar(pts, x, y, frase, TIPOS[tipo], subir=0.3 if not (huecos or malas) else 0.0, combo=False, nota=False)
        else:
            self.fx.texto(x, y, frase, COLORES["gris"], 24)
        sonido.play("sellar", 0.9)
        self.fx.chispas(x, BODEGA.bottom - 30, TIPOS[tipo], 30, (80, 260))
        self.fx.sacudir(4, 0.2)
        self.sello[s] = 1.0
        self.despensa[tipo] += 1
        for b in self.bolsas:
            if b["c"] // ANCHO_SEC == s and b["sale"] is None:
                b["sale"] = 0.0
        for cc in cols:
            self.alto[cc] = 0
            self.lleno[cc] = [False] * FILAS
        self.huecos = [h for h in self.huecos if h[0] not in cols]

    def animar(self, dt):
        # la grúa sigue al ratón como un resorte; la bolsa se balancea
        if self.etapa == "juego":
            w = self.actual["w"]
            meta = max(BODEGA.left + w * CELDA / 2, min(BODEGA.right - w * CELDA / 2, self.raton[0]))
            acel = (meta - self.grua_x) * 160 - self.grua_v * 22
            self.grua_v += acel * dt
            self.grua_x += self.grua_v * dt
            self.giro_v += (-self.giro * 40 - self.giro_v * 3.5 - acel * 0.0006) * dt
            self.giro += self.giro_v * dt
            self.giro = max(-0.5, min(0.5, self.giro))
            self.bucle("grua", min(0.6, abs(self.grua_v) / 1500))
        self.cinta += dt * 40
        for s in list(self.sello):
            self.sello[s] -= dt * 1.5
            if self.sello[s] <= 0:
                del self.sello[s]
        for i in list(self.salto_cola):
            self.salto_cola[i] -= dt
            if self.salto_cola[i] <= 0:
                del self.salto_cola[i]
        vivas = []
        for b in self.bolsas:
            if b["sale"] is not None:
                b["sale"] += dt
                if b["sale"] < 0.6:
                    vivas.append(b)
                continue
            if b["caida"] < 0:
                b["vel"] += 2600 * dt
                b["caida"] = min(0.0, b["caida"] + b["vel"] * dt)
                if b["caida"] >= 0:
                    b["aplasta"] = 1.0
                    sonido.play("golpe", 0.5 + 0.1 * b["w"] * b["h"])
                    x = BODEGA.left + (b["c"] + b["w"] / 2) * CELDA
                    self.fx.chispas(x, self._y(b["fila"], 0), (170, 160, 150), 10, (40, 140), (0.3, 0.5),
                                    con_brillo=False, angulo=-math.pi / 2, abre=1.4, tam=(2, 4))
            b["aplasta"] = max(0.0, b["aplasta"] - dt * 5)
            vivas.append(b)
        self.bolsas = vivas

    def _y(self, fila, h):
        return BODEGA.bottom - (fila + h) * CELDA

    # ── dibujo ───────────────────────────────────────────────────────────────────────
    def escena(self, lienzo):
        g = COLORES
        lienzo.blit(guardado("estiba_fondo", _fondo), ZONA.topleft)
        self._cinta(lienzo)
        # bolsas guardadas (las recién soltadas todavía caen; las de una sección sellada se van)
        lienzo.set_clip(pygame.Rect(BODEGA.left, ZONA.top, BODEGA.w, BODEGA.bottom - ZONA.top))
        for b in self.bolsas:
            w, h = b["w"] * CELDA, b["h"] * CELDA
            img = _bolsa(w, h, b["tipo"])
            y = self._y(b["fila"], b["h"]) + b["caida"]
            x = BODEGA.left + b["c"] * CELDA
            if b["sale"] is not None:
                y += 900 * b["sale"] ** 2
            if b["aplasta"] > 0:                                     # se aplasta un poquito al caer
                a = b["aplasta"]
                img = pygame.transform.smoothscale(img, (int(w * (1 + 0.08 * a)), int(h * (1 - 0.08 * a))))
                x -= int(w * 0.04 * a)
                y += int(h * 0.08 * a)
            lienzo.blit(img, (x, y))
            if b.get("mala"):                                        # carga en la sección equivocada
                r = pygame.Rect(x, y, img.get_width(), img.get_height())
                pygame.draw.rect(lienzo, g["rojo"], r.inflate(-3, -3), 3, border_radius=10)
                bx, by = r.right - 13, r.top + 13
                pygame.draw.circle(lienzo, g["rojo"], (bx, by), 9)
                pygame.draw.line(lienzo, (255, 255, 255), (bx - 4, by - 4), (bx + 4, by + 4), 3)
                pygame.draw.line(lienzo, (255, 255, 255), (bx - 4, by + 4), (bx + 4, by - 4), 3)
        lienzo.set_clip(ZONA)
        for cc, ff in self.huecos:                                   # huecos rayados
            x, y = BODEGA.left + cc * CELDA, BODEGA.bottom - (ff + 1) * CELDA
            pygame.draw.rect(lienzo, (64, 24, 30), (x + 2, y + 2, CELDA - 4, CELDA - 4))
            for k in range(-CELDA, CELDA, 12):
                pygame.draw.line(lienzo, (140, 50, 50), (x + max(0, k), y + max(0, -k)),
                                 (x + min(CELDA, CELDA + k), y + min(CELDA, CELDA - k)), 2)
        for s, k in self.sello.items():                              # brillo al sellar
            sec = pygame.Rect(BODEGA.left + ANCHO_SEC * s * CELDA, BODEGA.top, ANCHO_SEC * CELDA, BODEGA.h)
            lienzo.fill(tuple(int(v * 0.5 * k) for v in TIPOS[ORDEN[s]]), sec, special_flags=pygame.BLEND_ADD)
        # la grúa y la bolsa de turno
        if self.etapa != "final":
            self._grua(lienzo)
        # nombres de las secciones
        for k, tipo in enumerate(ORDEN):
            nombre = {"agua": t("mj.estiba.agua", "AGUA"), "comida": t("mj.estiba.comida", "COMIDA"), "o2": "O2",
                      "repuestos": t("mj.estiba.repuestos", "REPUESTOS")}[tipo]
            img = texto(nombre, 8, TIPOS[tipo], pixel_=True)
            lienzo.blit(img, img.get_rect(midtop=(BODEGA.left + (ANCHO_SEC * k + 1.5) * CELDA, BODEGA.bottom + 10)))
        # la despensa
        d = DESPENSA
        lienzo.blit(texto(t("mj.estiba.despensa", "DESPENSA"), 8, g["oro"], pixel_=True), (d.left + 16, d.top + 14))
        for i, tipo in enumerate(ORDEN):
            y = d.top + 42 + i * 62
            caja = pygame.Rect(d.left + 16, y, 50, 50)
            pygame.draw.rect(lienzo, TIPOS[tipo], caja, border_radius=10)
            _icono(lienzo, tipo, caja.centerx, caja.centery + 2, (250, 250, 250), TIPOS[tipo], 0.9)
            img = texto(f"× {self.despensa[tipo]}", 24, g["texto"])
            lienzo.blit(img, (caja.right + 14, y + 10))
        img = texto(t("mj.estiba.nota", "En la Estación Espacial la carga viaja en bolsas de tela de tamaños fijos "
                                        "(media, sencilla, doble y triple), que encajan como bloques (NASA)."), 17,
                    g["gris"], False, sombra=False)
        lienzo.blit(img, (ZONA.left + 20, ZONA.bottom - 28))

    def _cinta(self, lienzo):
        """La cinta con las bolsas que siguen: un clic en una la cambia por la de la grúa."""
        g = COLORES
        pygame.draw.rect(lienzo, (40, 42, 56), CINTA, border_radius=12)
        for k in range(CINTA.left - 30, CINTA.right, 24):
            x = k + int(self.cinta) % 24
            if CINTA.left < x < CINTA.right:
                pygame.draw.line(lienzo, (70, 74, 96), (x, CINTA.top + 4), (x - 8, CINTA.bottom - 4), 3)
        for i in range(3):
            pygame.draw.circle(lienzo, (90, 96, 120), (CINTA.left + 20 + i * (CINTA.w - 40) // 2, CINTA.bottom + 6), 7)
        atorada = self.etapa == "juego" and not self.cabe_algo(self.actual)
        for i, (r, b) in enumerate(zip(self.rects_cola(), self.cola)):
            brinco = int(14 * math.sin(math.pi * self.salto_cola.get(i, 0) / 0.3))
            encima = r.inflate(14, 14).collidepoint(self.raton) and self.etapa == "juego"
            if encima or atorada:
                k = 0.6 + 0.4 * math.sin(self.t * 8) if atorada and not encima else 1.0
                pygame.draw.rect(lienzo, mezclar((0, 0, 0), g["oro"], k), r.inflate(10, 10).move(0, -brinco), 2,
                                 border_radius=8)
            lienzo.blit(_bolsa(r.w, r.h, b["tipo"]), r.move(0, -brinco))
        y = CINTA.bottom + 16
        lienzo.blit(texto(t("mj.estiba.siguen", "SIGUEN"), 8, g["texto"], pixel_=True), (CINTA.left + 4, y + 3))
        img = texto(t("mj.estiba.cambiar", "clic en una = cambiarla"), 17, g["oro"] if atorada else (200, 206, 224))
        lienzo.blit(img, img.get_rect(topright=(CINTA.right, y - 2)))
        if atorada:                                               # la de turno no cabe: hay que cambiarla
            img = texto(t("mj.estiba.nocabe_sec", "¡No cabe en su sección! Cambiala"), 20, g["oro"])
            r = img.get_rect(midbottom=(CINTA.centerx, CINTA.top - 104))
            lienzo.blit(translucido(r.w + 20, r.h + 8, (6, 8, 20), 190, 8), r.inflate(20, 8))
            lienzo.blit(img, r)
            flecha_y = CINTA.top - 100 + 6 * math.sin(self.t * 8)
            pygame.draw.polygon(lienzo, g["oro"], [(CINTA.centerx - 10, flecha_y), (CINTA.centerx + 10, flecha_y),
                                                   (CINTA.centerx, flecha_y + 14)])

    def _grua(self, lienzo):
        g = COLORES
        b = self.actual
        c = self.columna(self.grua_x, b["w"])
        cx = int(self.grua_x)
        devuelve = int(70 * min(1.0, self.espera / 0.8))
        # carrito en el riel
        pygame.draw.rect(lienzo, (220, 180, 50), (cx - 30, RIEL_Y - 16, 60, 22), border_radius=5)
        pygame.draw.rect(lienzo, (120, 90, 20), (cx - 30, RIEL_Y - 16, 60, 22), 2, border_radius=5)
        for dx in (-18, 18):
            pygame.draw.circle(lienzo, (60, 60, 70), (cx + dx, RIEL_Y - 16), 6)
        luz(lienzo, cx, RIEL_Y + 8, 22, (255, 180, 60), 0.6 if int(self.t * 3) % 2 else 0.2)
        w, h = b["w"] * CELDA, b["h"] * CELDA
        gancho = (cx, RIEL_Y + 6)
        largo = 26 - devuelve
        # la sombra de dónde va a caer
        if self.espera <= 0 and self.etapa == "juego":
            if self.entra(b, c):
                destino = pygame.Rect(BODEGA.left + c * CELDA, self._y(self._apoyo(c, b["w"]), b["h"]), w, h)
                lienzo.blit(_bolsa(w, h, b["tipo"], 85), destino)
                if self.en_su_seccion(b, c):
                    pygame.draw.rect(lienzo, (255, 255, 255), destino.inflate(-4, -4), 2, border_radius=10)
                    aviso = t("mj.estiba.ojo", "¡dejaría hueco!") if self.huecos_si(b, c) else None
                    col = g["naranja"]
                else:                                  # sección equivocada: se puede, pero cuesta
                    pygame.draw.rect(lienzo, g["rojo"], destino.inflate(-4, -4), 3, border_radius=10)
                    aviso, col = t("mj.estiba.ojo_sec", "¡sección equivocada!"), g["rojo"]
                if aviso:
                    img = texto(aviso, 16, col)
                    lienzo.blit(img, img.get_rect(midbottom=(destino.centerx, destino.top - 4)))
            else:
                x0 = BODEGA.left + c * CELDA
                pygame.draw.rect(lienzo, g["rojo"], (x0 + 2, BODEGA.top + 2, w - 4, BODEGA.h - 4), 3, border_radius=8)
        # la bolsa colgando (se balancea)
        img = _bolsa(w, h, b["tipo"], 225)            # un poquito transparente: deja ver la carga de abajo
        ang = math.degrees(self.giro)
        rot = pygame.transform.rotate(img, ang)
        centro = (gancho[0] - math.sin(self.giro) * (largo + h / 2), gancho[1] + math.cos(self.giro) * (largo + h / 2))
        arriba = (gancho[0] - math.sin(self.giro) * largo, gancho[1] + math.cos(self.giro) * largo)
        pygame.draw.line(lienzo, (170, 176, 196), gancho, arriba, 3)
        lienzo.blit(rot, rot.get_rect(center=(int(centro[0]), int(centro[1]))))
        encima = self.etapa == "juego" and self.rect_colgada().collidepoint(self.raton)
        if self.girada(b) and self.etapa == "juego" and (encima or 1 <= self.guardadas < 7):
            if encima:                                                      # el clic aquí la gira
                pygame.draw.rect(lienzo, g["oro"], self.rect_colgada(), 2, border_radius=12)
            img = texto(t("mj.estiba.girar2", "clic en la bolsa = girarla"), 15, g["oro"] if encima else g["gris"], False)
            lienzo.blit(img, img.get_rect(midleft=(cx + w // 2 + 16, RIEL_Y + 34 + h // 2)))
        if self.reloj_grua is not None and self.espera <= 0:                 # el tiempo para soltar
            frac = max(0.0, self.reloj_grua / self.tiempo_grua())
            col = g["verde"] if frac > 0.5 else g["naranja"] if frac > 0.25 else g["rojo"]
            pygame.draw.arc(lienzo, col, (cx - 22, RIEL_Y - 38, 44, 44), math.pi / 2, math.pi / 2 + 2 * math.pi * frac, 4)
        if self.atorada > 0:                                                 # cuánto falta para que la devuelva
            frac = min(1.0, self.atorada / DEVUELVE)
            pygame.draw.arc(lienzo, g["gris"], (cx - 22, RIEL_Y - 38, 44, 44), math.pi / 2, math.pi / 2 + 2 * math.pi * frac, 3)
        if self.guardadas == 0 and self.tj < 4 and self.etapa == "juego":
            img = texto(t("mj.estiba.ayuda", "Llevala a su sección y hacé clic"), 22, g["oro"])
            lienzo.blit(img, img.get_rect(midleft=(cx + w // 2 + 20, RIEL_Y + 60)) if cx < 760
                        else img.get_rect(midright=(cx - w // 2 - 20, RIEL_Y + 60)))
