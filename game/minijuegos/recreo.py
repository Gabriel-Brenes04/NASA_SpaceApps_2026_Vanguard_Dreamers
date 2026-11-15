# -*- coding: utf-8 -*-
"""Microjuego del recreo (tarea: recreo → ánimo): fotos de la Tierra desde la ventana del hábitat.

(Antes era «estrellas fugaces», en estrellas.py; se cambió porque en la Luna NO hay estrellas fugaces:
no tiene aire donde las piedritas se quemen. Las claves de los textos siguen siendo «mj.estrellas.…».)

La tripulación (con su mono azul de vuelo, parches y audífonos) descansa en la ventana redonda. Afuera
está la Tierra, que gira despacio: de día a la izquierda y de noche a la derecha, con las luces de las
ciudades. Hay que tomarle FOTO a lo que pase:
  · relámpagos en el lado de noche (duran poquito)        · auroras cerca de los polos
  · huracanes en el lado de día                           · un cometa o una nave que cruza el cielo
CÁMARA CON ZOOM: se aprieta el clic para acercar y se SUELTA para tomar la foto. Entre más zoom y más
centrada, más puntos («¡Nítida!»); un clic rapidito también saca la foto, pero de lejos (vale menos).
ENCARGOS: arriba sale una foto pedida («Houston pide: un huracán», «La familia pide: Costa Rica»…).
Cumplirla da un bono grande. Costa Rica solo se puede fotografiar cuando la piden y está de este lado.
Un clic donde no hay nada sale movido y corta el combo. A la mitad hay una tormenta eléctrica.
Dato: la Tierra mide 12 742 km de ancho, casi 4 veces la Luna (3 475 km), y está a 384 400 km (NASA).
En la Luna las estrellas no titilan: no hay aire que las haga temblar.
"""
import math

import pygame

from .base import ZONA, COLORES
from ._kit import Partida, luz, degradado, guardado, texto, mezclar, translucido
from ..assets import sonido
from ..assets.textos import t, n

VENTANA = pygame.Rect(108, 136, 1064, 468)
TIERRA = (790, 372)
R = 150
# continentes: (longitud, latitud, ancho, alto) en grados (dibujados a mano, no es un mapa exacto)
CONTINENTES = ((-100, 48, 56, 34), (-85, 25, 30, 20), (-95, 12, 14, 12), (-60, -12, 34, 40), (-66, -38, 18, 26),
               (12, 50, 40, 22), (35, 55, 50, 20), (18, 8, 44, 40), (28, -18, 30, 30), (90, 50, 80, 30),
               (105, 22, 36, 22), (78, 20, 18, 16), (135, -25, 38, 24), (-40, 72, 30, 14), (45, 25, 26, 16),
               (120, 38, 16, 16), (165, 62, 30, 14), (-84, 10, 6, 5))
NUBES = ((-130, 30, 60, 6), (-20, 10, 70, 5), (60, -30, 80, 6), (150, 40, 60, 5), (-80, -50, 90, 5),
         (110, 5, 50, 4), (0, 55, 60, 5), (-160, -10, 50, 4))
PUNTOS = {"relampago": 15, "aurora": 10, "huracan": 10, "cometa": 40, "nave": 25, "costarica": 45}
COSTA_RICA = (-84.0, 10.0)
GIRO = 9.0                    # grados por segundo que gira la Tierra (acelerado)
ZOOM_T = 0.45                 # segundos de clic sostenido para el zoom completo
BONO_ENCARGO = 40
Y_AVISO = VENTANA.bottom - 50     # los carteles del recreo van abajo, para no tapar la Tierra
CR_COLORES = ((0, 43, 127), (255, 255, 255), (206, 17, 38), (206, 17, 38), (255, 255, 255), (0, 43, 127))


def _pared():
    import random
    rng = random.Random(2)
    s = pygame.Surface(ZONA.size)
    s.blit(degradado(ZONA.w, ZONA.h, (44, 50, 72), (22, 25, 40)), (0, 0))
    for x in range(0, ZONA.w, 120):
        pygame.draw.line(s, (34, 38, 58), (x, 0), (x, ZONA.h), 2)
    v = VENTANA.move(-ZONA.left, -ZONA.top)
    pygame.draw.ellipse(s, (16, 18, 30), v.inflate(70, 70))
    pygame.draw.ellipse(s, (120, 128, 150), v.inflate(46, 46))
    pygame.draw.ellipse(s, (70, 76, 98), v.inflate(46, 46), 6)
    pygame.draw.ellipse(s, (2, 3, 10), v)
    estrellas = pygame.Surface(v.size, pygame.SRCALPHA)
    for _ in range(420):                                          # estrellas nítidas (no titilan)
        x, y = rng.randint(0, v.w - 1), rng.randint(0, v.h - 1)
        b = rng.choice((90, 120, 160, 200, 255))
        col = rng.choice(((b, b, b), (b, b, min(255, b + 40)), (min(255, b + 30), b, b - 20 if b > 20 else b)))
        estrellas.fill((*col, 255), (x, y, 1 if b < 200 else 2, 1 if b < 200 else 2))
    mascara = pygame.Surface(v.size, pygame.SRCALPHA)
    pygame.draw.ellipse(mascara, (255, 255, 255, 255), (0, 0, *v.size))
    estrellas.blit(mascara, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    s.blit(estrellas, v.topleft)
    for k in range(20):                                           # remaches del marco
        a = 2 * math.pi * k / 20
        x = v.centerx + math.cos(a) * (v.w / 2 + 23)
        y = v.centery + math.sin(a) * (v.h / 2 + 23)
        pygame.draw.circle(s, (180, 186, 204), (int(x), int(y)), 5)
        pygame.draw.circle(s, (90, 96, 118), (int(x), int(y)), 5, 1)
    return s


def _noche():
    """La sombra del lado de noche (a la derecha), con un borde suave."""
    s = pygame.Surface((2 * R, 2 * R), pygame.SRCALPHA)
    for i in range(40):
        k = i / 39
        x = int(R * 0.05 + k * R * 0.5)
        pygame.draw.rect(s, (2, 4, 16, int(40 + 175 * k)), (R + x, 0, 2 * R, 2 * R))
    m = pygame.Surface((2 * R, 2 * R), pygame.SRCALPHA)
    pygame.draw.circle(m, (255, 255, 255, 255), (R, R), R)
    s.blit(m, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return s


def _circulo(r):
    m = pygame.Surface((2 * r, 2 * r), pygame.SRCALPHA)
    pygame.draw.circle(m, (255, 255, 255, 255), (r, r), r)
    return m


def bandera_cr(sup, x, y, w, h):
    """La bandera de Costa Rica (franjas 1-1-2-1-1)."""
    alto = h / 6
    for i, c in enumerate(CR_COLORES):
        pygame.draw.rect(sup, c, (x, int(y + i * alto), w, int(alto) + 1))


class Recreo(Partida):
    titulo = "Recreo: fotos de la Tierra"
    instruccion = "Apretá el clic para hacer zoom y soltalo para tomar la foto"
    tarea = "recreo"
    duracion = 40.0
    META = 5700
    ESCALA = 250
    COLOR = (150, 200, 255)
    Y_CARTEL = ZONA.top + 125

    def preparar(self):
        self.titulo = t("mj.estrellas.titulo", "Recreo: fotos de la Tierra")
        self.instruccion = t("mj.estrellas.instr2", "Apretá el clic para hacer zoom y soltalo para tomar la foto")
        self.consejos = (t("mj.estrellas.c4", "Con más zoom y bien centrada, la foto vale más. Un clic rapidito sale de lejos."),
                         t("mj.estrellas.c5", "Cumplí los ENCARGOS de arriba: dan un bono grande (¡hasta Costa Rica!)."),
                         t("mj.estrellas.c3", "Una foto donde no hay nada sale movida y corta el combo."))
        self.cosas = []           # tipo, x, y, vx, vy, vida, vida0, r, sem
        self.fotos = []           # [tipo, k, x0, y0] (k: 0 → 1 mientras vuela al álbum)
        self.album = []           # tipos de las fotos ya guardadas
        self.giro = 0.0
        self.proxima = 0.6
        self.tormenta = None      # segundos que le quedan a la tormenta
        self.tormenta_hecha = False
        self.salto = 0.0
        self.flash_foto = 0.0
        self.luces = [(self.rng.uniform(-180, 180), self.rng.uniform(-55, 60)) for _ in range(70)]
        self.luces.append(COSTA_RICA)
        # la cámara
        self.sosteniendo = False
        self.zoom = 0.0
        self.habia = False        # al apretar había algo cerca (para no castigar si se va)
        # los encargos
        self.encargo = None       # {tipo, quien, vida, vida0}
        self.prox_encargo = 2.0
        self.forzar = 0.0         # para que el cometa o la nave pedidos sí pasen
        self.cumplidos = 0
        self.ultimo_tipo = None

    # ── reglas que cambian con el nivel ──────────────────────────────────────────────
    def radio(self):
        return max(26, 46 - 2.6 * (self.nv - 1))

    def factor(self):
        return max(0.42, 1 - 0.085 * (self.nv - 1))

    def cada(self):
        return max(0.42, 1.25 - 0.11 * (self.nv - 1))

    def proyecta(self, lon, lat):
        """De longitud y latitud a la pantalla: (x, y, z); z > 0 = de este lado de la Tierra."""
        lo = math.radians(lon + self.giro)
        la = math.radians(lat)
        return (TIERRA[0] + R * math.sin(lo) * math.cos(la), TIERRA[1] - R * math.sin(la),
                math.cos(lo) * math.cos(la))

    def cr_falta(self):
        """Segundos de Costa Rica a la vista que quedan (0 si no se ve), y segundos para que aparezca."""
        lo = (COSTA_RICA[0] + self.giro + 180) % 360 - 180
        if -70 < lo < 70:
            return (70 - lo) / GIRO, 0.0
        return 0.0, ((-70 - lo) % 360) / GIRO

    def _en_tierra(self, lado):
        """Un punto al azar sobre la Tierra: «noche» (derecha), «dia» (izquierda) o «polo»."""
        for _ in range(30):
            if lado == "polo":
                ang = self.rng.uniform(-0.2, 0.9)
                sgn = self.rng.choice((-1, 1))
                x = TIERRA[0] + R * 0.55 * math.cos(ang) * self.rng.uniform(0.3, 1.0)
                y = TIERRA[1] + sgn * R * self.rng.uniform(0.72, 0.86)
            else:
                x = TIERRA[0] + (self.rng.uniform(0.18, 0.85) if lado == "noche" else -self.rng.uniform(0.1, 0.8)) * R
                y = TIERRA[1] + self.rng.uniform(-0.75, 0.75) * R
            if math.hypot(x - TIERRA[0], y - TIERRA[1]) < R - 14:
                return x, y
        return TIERRA

    def _nueva(self, tipo=None):
        if tipo is None:
            pesos = {"relampago": 4 + self.nv * 0.5, "aurora": 3, "huracan": 3, "cometa": 0.7 if self.nv >= 2 else 0.3,
                     "nave": 1.2}
            if self.encargo and self.encargo["tipo"] in pesos:             # lo pedido sale más
                pesos[self.encargo["tipo"]] *= 3
            tipo = self.rng.choices(list(pesos), list(pesos.values()))[0]
        f = self.factor()
        c = {"tipo": tipo, "vx": 0.0, "vy": 0.0, "sem": self.rng.uniform(0, 6), "r": self.radio()}
        if tipo == "relampago":
            c["x"], c["y"] = self._en_tierra("noche")
            c["vida"] = self.rng.uniform(0.85, 1.15) * f + 0.15
        elif tipo == "aurora":
            c["x"], c["y"] = self._en_tierra("polo")
            c["vida"] = 2.8 * f + 0.4
        elif tipo == "huracan":
            c["x"], c["y"] = self._en_tierra("dia")
            c["vida"] = 3.0 * f + 0.4
            c["vx"] = 6.0
        elif tipo == "cometa":
            izq = self.rng.random() < 0.5
            c["x"] = VENTANA.left + 40 if izq else VENTANA.right - 40
            c["y"] = self.rng.uniform(VENTANA.top + 60, VENTANA.top + 150)
            vel = 320 / f
            c["vx"], c["vy"] = (vel if izq else -vel), self.rng.uniform(20, 60)
            c["vida"] = (VENTANA.w - 80) / vel
            c["r"] = self.radio() + 6
            sonido.play("cometa", 0.5)
        else:
            izq = self.rng.random() < 0.5
            c["x"] = VENTANA.left + 60 if izq else VENTANA.right - 60
            c["y"] = self.rng.uniform(VENTANA.top + 120, VENTANA.bottom - 120)
            vel = 230 / f
            c["vx"], c["vy"] = (vel if izq else -vel), self.rng.uniform(-25, 25)
            c["vida"] = (VENTANA.w - 120) / vel
        c["vida0"] = c["vida"]
        self.cosas.append(c)

    def _adentro(self, x, y, margen=0):
        rx, ry = VENTANA.w / 2 - margen, VENTANA.h / 2 - margen
        return ((x - VENTANA.centerx) / rx) ** 2 + ((y - VENTANA.centery) / ry) ** 2 <= 1

    # ── encargos ─────────────────────────────────────────────────────────────────────
    def _nuevo_encargo(self):
        opciones = ["relampago", "aurora", "huracan", "nave"] + (["cometa"] if self.nv >= 2 else [])
        quedan, _llega = self.cr_falta()
        if quedan > 9 and self.ultimo_tipo != "costarica" and self.restante() > 8:
            opciones += ["costarica"] * 3                     # se ve un buen rato: la familia la pide
        opciones = [o for o in opciones if o != self.ultimo_tipo] or opciones
        tipo = self.rng.choice(opciones)
        quien = (t("mj.estrellas.familia", "La familia") if tipo == "costarica" else
                 self.rng.choice((t("mj.estrellas.houston", "Houston"), t("mj.estrellas.familia", "La familia"),
                                  t("mj.estrellas.escuela", "Una escuela"), t("mj.estrellas.ciencia", "El equipo de ciencia"))))
        vida = 12.0 if tipo != "costarica" else min(12.0, quedan)
        self.encargo = {"tipo": tipo, "quien": quien, "vida": vida, "vida0": vida}
        self.ultimo_tipo = tipo
        self.forzar = self.rng.uniform(1.5, 3.0)
        sonido.play("radar", 0.4)

    def que_pide(self, tipo):
        return {"relampago": t("mj.estrellas.p_relampago", "un relámpago"), "aurora": t("mj.estrellas.p_aurora", "una aurora"),
                "huracan": t("mj.estrellas.p_huracan", "un huracán"), "cometa": t("mj.estrellas.p_cometa", "un cometa"),
                "nave": t("mj.estrellas.p_nave", "una nave"), "costarica": "Costa Rica"}[tipo]

    def _encargos(self, dt):
        if self.encargo is None:
            self.prox_encargo -= dt
            if self.prox_encargo <= 0 and self.restante() > 4:
                self._nuevo_encargo()
            return
        e = self.encargo
        e["vida"] -= dt
        if e["tipo"] in ("cometa", "nave"):                   # que sí pase uno
            self.forzar -= dt
            if self.forzar <= 0 and not any(c["tipo"] == e["tipo"] for c in self.cosas):
                self._nueva(e["tipo"])
                self.forzar = 5.0
        if e["tipo"] == "costarica":                          # Costa Rica se puede fotografiar mientras se vea
            x, y, z = self.proyecta(*COSTA_RICA)
            cr = next((c for c in self.cosas if c["tipo"] == "costarica"), None)
            if z > 0.3 and cr is None:
                self.cosas.append({"tipo": "costarica", "x": x, "y": y, "vx": 0.0, "vy": 0.0, "vida": 99.0,
                                   "vida0": 99.0, "r": self.radio() + 6, "sem": 0.0})
            elif z <= 0.3 and cr is not None:
                self.cosas.remove(cr)
        if e["vida"] <= 0:
            self.fx.texto(ZONA.centerx + 140, ZONA.top + 100, t("mj.estrellas.vencido", "encargo vencido"),
                          COLORES["gris"], 16, 0.9, 20)
            self._fin_encargo()

    def _fin_encargo(self):
        self.encargo = None
        self.prox_encargo = 1.5
        self.cosas = [c for c in self.cosas if c["tipo"] != "costarica"]

    # ── juego ────────────────────────────────────────────────────────────────────────
    def jugar(self, dt):
        if not self.tormenta_hecha and self.tj >= 17.0:
            self.tormenta_hecha = True
            self.tormenta = 4.5
            self.fx.cartel(t("mj.estrellas.tormenta", "¡Tormenta eléctrica en la Tierra!"), COLORES["amarillo"], 24,
                           1.6, Y_AVISO)
            sonido.play("nivel", 0.7)
        if self.tormenta is not None:
            self.tormenta -= dt
            if self.rng.random() < dt / 0.28:
                self._nueva("relampago")
            if self.tormenta <= 0:
                self.tormenta = None
        self.proxima -= dt
        if self.proxima <= 0:
            self.proxima = self.cada() * self.rng.uniform(0.75, 1.25)
            if sum(1 for c in self.cosas if c["tipo"] != "costarica") < 2 + self.nv // 2:
                self._nueva()
        self._encargos(dt)
        # la cámara: apretar = empezar el zoom; soltar = la foto
        for x, y in self.clics:
            self.sosteniendo = True
            self.zoom = 0.0
            self.habia = any(math.hypot(c["x"] - x, c["y"] - y) <= c["r"] * 1.4 for c in self.cosas)
        if self.sosteniendo:
            if self.apretado:
                self.zoom = min(1.0, self.zoom + dt / ZOOM_T)
            else:
                self.sosteniendo = False
                self._disparar(*self.raton)
        for c in self.cosas:
            if c["tipo"] == "costarica":
                c["x"], c["y"], _z = self.proyecta(*COSTA_RICA)
                continue
            c["x"] += c["vx"] * dt
            c["y"] += c["vy"] * dt
            c["vida"] -= dt
        self.cosas = [c for c in self.cosas if c["vida"] > 0]
        self.bucle("ambiente", 0.55, 2.0)

    def _disparar(self, x, y):
        cerca = [c for c in self.cosas if math.hypot(c["x"] - x, c["y"] - y) <= c["r"]]
        if cerca:
            c = min(cerca, key=lambda c: math.hypot(c["x"] - x, c["y"] - y))
            self._foto(c, math.hypot(c["x"] - x, c["y"] - y) / c["r"])
        elif self.habia:                                     # se fue mientras hacía zoom: no se castiga
            self.fx.texto(x, y + 24, t("mj.estrellas.sefue", "¡Se fue!"), COLORES["gris"], 18, 0.7, 20)
            sonido.play("fallo", 0.4)
        else:
            self.errar(x, y)
            self.fx.texto(x, y + 24, t("mj.estrellas.movida", "foto movida"), COLORES["gris"], 16, 0.6, 20)

    def _foto(self, c, lejos):
        self.cosas.remove(c)
        nombres = {"relampago": t("mj.estrellas.relampago", "¡Relámpago!"), "aurora": t("mj.estrellas.aurora", "¡Aurora!"),
                   "huracan": t("mj.estrellas.huracan", "¡Huracán!"), "cometa": t("mj.estrellas.cometa", "¡Cometa!"),
                   "nave": t("mj.estrellas.nave", "¡Una nave!"), "costarica": t("mj.estrellas.cr", "¡Costa Rica!")}
        col = {"relampago": COLORES["amarillo"], "aurora": COLORES["verde"], "huracan": COLORES["texto"],
               "cometa": COLORES["oro"], "nave": COLORES["cian"], "costarica": (120, 200, 255)}[c["tipo"]]
        calidad = self.zoom * (0.6 + 0.4 * (1 - min(1.0, lejos)))
        nitida = calidad >= 0.8
        base = PUNTOS[c["tipo"]] * (0.5 + 0.7 * calidad)
        frase = nombres[c["tipo"]]
        if nitida:
            frase = t("mj.estrellas.nitida", "¡Nítida!") + " " + frase
        self.ganar(max(1, round(base)), c["x"], c["y"] - 30, frase, col, subir=0.2 if nitida else 0.12)
        if self.zoom < 0.35:
            self.fx.texto(c["x"], c["y"] + 26, t("mj.estrellas.lejos", "de lejos"), COLORES["gris"], 16, 0.7, 15)
        sonido.play("obturador")
        self.flash_foto = 0.12
        self.salto = 0.35
        self.fotos.append([c["tipo"], 0.0, c["x"], c["y"]])
        self.fx.anillo(c["x"], c["y"], (240, 240, 255), c["r"] + 30, 0.3, 3)
        self.fx.chispas(c["x"], c["y"], col, 12 + (10 if nitida else 0), (60, 200), (0.3, 0.6))
        if self.encargo and self.encargo["tipo"] == c["tipo"]:
            self.cumplidos += 1
            self.ganar(BONO_ENCARGO, ZONA.centerx + 140, ZONA.top + 104, None, COLORES["oro"], subir=0.2, combo=False,
                       nota=False)
            self.fx.cartel(t("mj.estrellas.cumplido", "¡Encargo cumplido!"), COLORES["oro"], 28, 1.1, Y_AVISO)
            sonido.play("estrella3", 0.8)
            self._fin_encargo()

    def animar(self, dt):
        self.giro += dt * GIRO                    # la Tierra gira (acelerado)
        self.salto = max(0.0, self.salto - dt)
        self.flash_foto = max(0.0, self.flash_foto - dt)
        if not self.jugando():
            self.sosteniendo = False
        for f in self.fotos:
            f[1] += dt * 1.6
        for f in [f for f in self.fotos if f[1] >= 1]:
            self.album.append(f[0])
            sonido.play("album", 0.5)
        self.fotos = [f for f in self.fotos if f[1] < 1]

    # ── dibujo ───────────────────────────────────────────────────────────────────────
    def _tierra(self, lienzo):
        cx, cy = TIERRA
        luz(lienzo, cx, cy, R + 40, (40, 90, 200), 0.55)            # la atmósfera brilla
        s = guardado("tierra_lienzo", lambda: pygame.Surface((2 * R, 2 * R), pygame.SRCALPHA))
        s.fill((0, 0, 0, 0))
        pygame.draw.circle(s, (26, 82, 170), (R, R), R)
        pygame.draw.circle(s, (40, 110, 205), (R - 20, R - 20), int(R * 0.8))

        def proyecta(lon, lat):
            lo = math.radians(lon + self.giro)
            la = math.radians(lat)
            return R + R * math.sin(lo) * math.cos(la), R - R * math.sin(la), math.cos(lo) * math.cos(la)

        for lon, lat, w, h in CONTINENTES:
            x, y, z = proyecta(lon, lat)
            if z > 0:
                ww = max(2, R * math.radians(w) * z * 0.9)
                hh = R * math.radians(h)
                pygame.draw.ellipse(s, (54, 136, 72), (x - ww / 2, y - hh / 2, ww, hh))
                pygame.draw.ellipse(s, (150, 140, 90), (x - ww / 4, y - hh / 5, ww / 2, hh / 3))
                pygame.draw.ellipse(s, (78, 160, 90), (x - ww / 2.6, y - hh / 2.4, ww / 1.6, hh / 2.2))
        for lat in (78, -80):                                        # hielo de los polos
            pygame.draw.ellipse(s, (230, 240, 250), (R - R * 0.45, R - R * math.sin(math.radians(lat)) - 10, R * 0.9, 20))
        for lon, lat, w, h in NUBES:
            x, y, z = proyecta(lon + self.giro * 0.3, lat)
            if z > 0:
                ww = max(2, R * math.radians(w) * z)
                pygame.draw.ellipse(s, (235, 240, 250), (x - ww / 2, y - h, ww, 2 * h))
                pygame.draw.ellipse(s, (235, 240, 250), (x - ww / 3, y - h * 2, ww / 2, 2 * h))
        s.blit(guardado("tierra_noche", _noche), (0, 0))
        for lon, lat in self.luces:                                  # ciudades del lado de noche
            x, y, z = proyecta(lon, lat)
            if z > 0 and x > R * 1.15:
                s.fill((255, 210, 120, 255), (int(x), int(y), 2, 2))
        m = guardado("tierra_mascara", lambda: _circulo(R))
        s.blit(m, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        lienzo.blit(s, (cx - R, cy - R))
        pygame.draw.circle(lienzo, (120, 170, 255), (cx, cy), R, 2)

    def _cosa(self, lienzo, c):
        k = c["vida"] / c["vida0"]
        entra = min(1.0, (c["vida0"] - c["vida"]) / 0.15)
        alfa = min(entra, min(1.0, c["vida"] / 0.2))
        x, y = c["x"], c["y"]
        tipo = c["tipo"]
        if tipo == "relampago":
            if self.rng.random() < 0.8:
                luz(lienzo, x, y, 60, (255, 250, 200), alfa * self.rng.uniform(0.5, 1.0))
                for _ in range(2):
                    p = (x, y)
                    for _ in range(4):
                        q = (p[0] + self.rng.uniform(-12, 12), p[1] + self.rng.uniform(4, 14))
                        pygame.draw.line(lienzo, (255, 255, 230), p, q, 2)
                        p = q
        elif tipo == "aurora":
            for i in range(7):
                xx = x - 36 + i * 12
                alto = 26 + 12 * math.sin(self.t * 3 + i + c["sem"])
                col = mezclar((60, 255, 140), (170, 90, 255), i / 7)
                luz(lienzo, xx, y, 22, col, 0.55 * alfa)
                pygame.draw.line(lienzo, mezclar((0, 0, 0), col, alfa), (xx, y - alto / 2),
                                 (xx + 3 * math.sin(self.t * 4 + i), y + alto / 2), 2)
        elif tipo == "huracan":
            for i in range(3):
                a0 = -self.t * 3 + i * 2 * math.pi / 3
                pts = [(x + math.cos(a0 + j * 0.35) * (4 + j * 2.4), y + math.sin(a0 + j * 0.35) * (4 + j * 2.4) * 0.8)
                       for j in range(10)]
                pygame.draw.lines(lienzo, mezclar((26, 82, 170), (250, 252, 255), alfa), False, pts, 4)
            pygame.draw.circle(lienzo, mezclar((26, 82, 170), (40, 60, 120), alfa), (int(x), int(y)), 3)
        elif tipo == "cometa":
            m = math.hypot(c["vx"], c["vy"]) or 1
            ux, uy = -c["vx"] / m, -c["vy"] / m
            for j in range(14):
                luz(lienzo, x + ux * j * 9, y + uy * j * 9, 26 - j, (255, 220, 140), alfa * (1 - j / 14))
            pygame.draw.circle(lienzo, (255, 250, 220), (int(x), int(y)), 6)
        elif tipo == "costarica":                                  # un pin con la banderita
            pulso = 0.5 + 0.5 * math.sin(self.t * 6)
            luz(lienzo, x, y, 30, (140, 220, 255), 0.5 + 0.3 * pulso)
            pygame.draw.circle(lienzo, (255, 255, 255), (int(x), int(y)), 4)
            pygame.draw.line(lienzo, (230, 230, 240), (x, y), (x, y - 30), 2)
            bandera_cr(lienzo, int(x) + 1, int(y) - 30, 24, 15)
            img = texto("Costa Rica", 15, (235, 245, 255))
            lienzo.blit(img, img.get_rect(midbottom=(int(x) + 12, int(y) - 33)))
        else:
            pygame.draw.rect(lienzo, (200, 205, 220), (x - 7, y - 5, 14, 10), border_radius=3)
            pygame.draw.line(lienzo, (70, 120, 210), (x - 26, y), (x - 8, y), 6)
            pygame.draw.line(lienzo, (70, 120, 210), (x + 8, y), (x + 26, y), 6)
            if int(self.t * 3) % 2:
                luz(lienzo, x, y - 7, 18, (255, 80, 80), 0.9)
        pedido = self.encargo is not None and self.encargo["tipo"] == tipo
        if self.nv <= 2 or tipo in ("cometa", "nave", "costarica") or pedido:      # ayuda: el blanco se marca
            rr = int(c["r"] * (1 + 0.06 * math.sin(self.t * 8)))
            if pedido:
                col = mezclar((0, 0, 0), COLORES["oro"], alfa * (0.6 + 0.4 * math.sin(self.t * 8)))
                pygame.draw.circle(lienzo, col, (int(x), int(y)), rr, 2)
            else:
                col = mezclar((0, 0, 0), (200, 210, 240), alfa * (0.35 + 0.3 * (1 - k)))
                pygame.draw.circle(lienzo, col, (int(x), int(y)), rr, 1)

    def escena(self, lienzo):
        g = COLORES
        lienzo.blit(guardado("recreo_pared", _pared), ZONA.topleft)
        lienzo.set_clip(VENTANA)
        self._tierra(lienzo)
        for c in self.cosas:
            self._cosa(lienzo, c)
        lienzo.set_clip(ZONA)
        # el zoom de la cámara (una lupa redonda donde está el ratón) y el visor
        if self.etapa == "juego" and self._adentro(*self.raton):
            self._visor(lienzo)
        # la tripulación mirando por la ventana (de espaldas, con el mono azul de vuelo)
        for i, (hx, hy, mono, pelo, cola) in enumerate(((228, 566, (46, 86, 168), (40, 28, 22), True),
                                                        (338, 578, (36, 70, 148), (20, 18, 20), False))):
            brinco = int(12 * math.sin(math.pi * self.salto / 0.35)) if self.salto > 0 and i == len(self.album) % 2 else 0
            self._tripulante(lienzo, hx, hy - brinco, mono, pelo, cola, i)
        # álbum: las fotos que vuelan y la pila
        ax, ay = 1150, 540
        for tipo, k, x0, y0 in self.fotos:
            px = x0 + (ax - x0) * k
            py = y0 + (ay - y0) * k - 90 * math.sin(math.pi * k)
            self._polaroid(lienzo, px, py, tipo, 1.4 - 0.5 * k)
        for i, tipo in enumerate(self.album[-6:]):
            self._polaroid(lienzo, ax + (i % 3 - 1) * 6, ay - i * 4, tipo, 0.9, (i * 37) % 17 - 8)
        img = texto(t("mj.estrellas.fotos", "{n} fotos", n=len(self.album)), 20, g["texto"])
        lienzo.blit(img, img.get_rect(midtop=(ax, ay + 40)))
        self._panel(lienzo)
        if self.flash_foto > 0:                                      # el flash de la cámara (solo en el vidrio)
            nivel = max(1, int(4 * self.flash_foto / 0.12))
            fl = guardado(("flash_ventana", nivel), lambda: self._flash(nivel))
            lienzo.blit(fl, VENTANA.topleft, special_flags=pygame.BLEND_ADD)
        lienzo.blit(translucido(ZONA.w - 4, 34, (6, 8, 20), 170, 0), (ZONA.left + 2, ZONA.bottom - 36))
        img = texto(t("mj.estrellas.nota", "La Tierra mide 12 742 km de ancho, casi 4 veces la Luna, y está a 384 400 km "
                                           "(NASA). Aquí las estrellas no titilan: no hay aire."), 17, g["gris"], False,
                    sombra=False)
        lienzo.blit(img, (ZONA.left + 20, ZONA.bottom - 28))

    def _visor(self, lienzo):
        mx, my = self.raton
        z = self.zoom if self.sosteniendo else 0.0
        if z > 0.02:
            rad = 66
            aumento = 1.0 + 1.6 * z
            lado = int(2 * rad / aumento)
            fuente = pygame.Rect(0, 0, lado, lado)
            fuente.center = (int(mx), int(my))
            fuente.clamp_ip(VENTANA)
            try:
                trozo = lienzo.subsurface(fuente).copy()
            except ValueError:
                trozo = None
            if trozo is not None:
                lupa = pygame.Surface((2 * rad, 2 * rad), pygame.SRCALPHA)
                lupa.blit(pygame.transform.smoothscale(trozo, (2 * rad, 2 * rad)), (0, 0))
                lupa.blit(guardado(("lupa", rad), lambda: _circulo(rad)), (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
                lienzo.blit(lupa, (int(mx) - rad, int(my) - rad))
            listo = z >= 1.0
            col = COLORES["verde"] if listo else (230, 235, 250)
            pygame.draw.circle(lienzo, (20, 24, 40), (int(mx), int(my)), rad + 4, 5)
            pygame.draw.arc(lienzo, col, (mx - rad - 4, my - rad - 4, 2 * rad + 8, 2 * rad + 8),
                            math.pi / 2, math.pi / 2 + 2 * math.pi * z, 5)
            if listo:
                img = texto(t("mj.estrellas.solta", "¡soltá!"), 16, COLORES["verde"])
                lienzo.blit(img, img.get_rect(midtop=(int(mx), int(my) + rad + 8)))
        brazo = 22 - 10 * z
        for sx, sy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
            x0, y0 = mx + sx * brazo, my + sy * brazo
            pygame.draw.line(lienzo, (230, 235, 250), (x0, y0), (x0 - sx * 10, y0), 2)
            pygame.draw.line(lienzo, (230, 235, 250), (x0, y0), (x0, y0 - sy * 10), 2)
        pygame.draw.circle(lienzo, (255, 90, 90), (int(mx), int(my)), 2)

    def _tripulante(self, lienzo, hx, y, mono, pelo, cola, i):
        """Un tripulante de espaldas: mono azul de vuelo con parches, y audífonos con micrófono."""
        osc = mezclar(mono, (0, 0, 0), 0.35)
        piel = (180, 130, 100) if i == 0 else (122, 84, 60)
        for col, d in ((osc, 3), (mono, 0)):                        # hombros y espalda
            pygame.draw.circle(lienzo, col, (hx - 46, y + 58), 28 + d)
            pygame.draw.circle(lienzo, col, (hx + 46, y + 58), 28 + d)
            pygame.draw.rect(lienzo, col, (hx - 50 - d, y + 30 - d, 100 + 2 * d, 110), border_radius=20)
            pygame.draw.rect(lienzo, col, (hx - 74 - d, y + 58, 148 + 2 * d, 80))
        pygame.draw.line(lienzo, osc, (hx, y + 44), (hx, y + 130), 2)                 # costura de la espalda
        pygame.draw.line(lienzo, mezclar(mono, (255, 255, 255), 0.18), (hx - 64, y + 64), (hx - 30, y + 40), 2)
        pygame.draw.rect(lienzo, piel, (hx - 12, y + 16, 24, 20))                   # cuello
        pygame.draw.ellipse(lienzo, osc, (hx - 26, y + 26, 52, 18), 4)               # el cuello del mono
        # parche de la misión (hombro izquierdo): la Luna y una estrella
        px, py = hx - 50, y + 62
        pygame.draw.circle(lienzo, (16, 26, 66), (px, py), 13)
        pygame.draw.circle(lienzo, (230, 232, 240), (px, py), 13, 2)
        pygame.draw.circle(lienzo, (200, 200, 210), (px + 3, py + 2), 5)
        pygame.draw.circle(lienzo, (250, 210, 70), (px - 5, py - 5), 2)
        # bandera de Costa Rica (hombro derecho)
        bandera_cr(lienzo, hx + 34, y + 52, 26, 16)
        pygame.draw.rect(lienzo, osc, (hx + 33, y + 51, 28, 18), 1)
        # cabeza: pelo y orejas
        pygame.draw.circle(lienzo, piel, (hx - 33, y - 2), 8)
        pygame.draw.circle(lienzo, piel, (hx + 33, y - 2), 8)
        pygame.draw.circle(lienzo, pelo, (hx, y - 6), 35)
        if cola:
            pygame.draw.ellipse(lienzo, pelo, (hx - 9, y + 14, 18, 38))
            pygame.draw.circle(lienzo, (220, 80, 120), (hx, y + 16), 5)
        pygame.draw.arc(lienzo, (120, 160, 230), (hx - 35, y - 41, 70, 70), 0.2, 1.4, 3)  # luz de la Tierra
        # audífonos: la diadema, las orejeras y el micrófono
        pygame.draw.arc(lienzo, (78, 82, 98), (hx - 39, y - 47, 78, 78), 0.25, math.pi - 0.25, 6)
        pygame.draw.arc(lienzo, (130, 136, 156), (hx - 38, y - 46, 76, 76), 0.6, math.pi - 0.6, 2)
        for sx in (-1, 1):
            pygame.draw.circle(lienzo, (34, 36, 44), (hx + sx * 36, y - 2), 11)
            pygame.draw.circle(lienzo, (96, 100, 116), (hx + sx * 36, y - 2), 11, 2)
        pygame.draw.line(lienzo, (34, 36, 44), (hx + 40, y + 4), (hx + 30, y + 26), 3)
        pygame.draw.circle(lienzo, (60, 62, 72), (hx + 29, y + 27), 4)

    def _panel(self, lienzo):
        """Arriba al centro: el ánimo de la tripulación y el encargo de turno."""
        g = COLORES
        caja = pygame.Rect(0, 0, 500, 62)
        caja.midtop = (ZONA.centerx + 30, ZONA.top + 12)
        lienzo.blit(translucido(caja.w, caja.h, (6, 8, 20), 180), caja)
        lienzo.blit(texto(t("mj.estrellas.animo", "Ánimo de la tripulación"), 13, (255, 150, 195), sombra=False),
                    (caja.left + 12, caja.top + 6))
        frac = (self.rendimiento() - 0.4) / 0.9
        barra = pygame.Rect(caja.left + 12, caja.top + 30, 150, 18)
        pygame.draw.rect(lienzo, (34, 36, 60), barra, border_radius=9)
        if frac > 0.01:
            pygame.draw.rect(lienzo, mezclar((255, 120, 170), (255, 220, 90), frac),
                             (barra.x, barra.y, int(barra.w * frac), barra.h), border_radius=9)
        cara = (barra.right + 24, caja.top + 38)
        pygame.draw.circle(lienzo, (255, 220, 90), cara, 15)
        pygame.draw.circle(lienzo, (40, 30, 10), (cara[0] - 5, cara[1] - 4), 2)
        pygame.draw.circle(lienzo, (40, 30, 10), (cara[0] + 5, cara[1] - 4), 2)
        sonrisa = -0.6 + 1.6 * frac
        if sonrisa > 0:
            pygame.draw.arc(lienzo, (40, 30, 10), (cara[0] - 8, cara[1] - 6 - 4 * sonrisa, 16, 14 + 4 * sonrisa),
                            math.pi * 1.1, math.pi * 1.9, 2)
        else:
            pygame.draw.line(lienzo, (40, 30, 10), (cara[0] - 6, cara[1] + 5), (cara[0] + 6, cara[1] + 5), 2)
        # el encargo
        x0 = caja.left + 222
        pygame.draw.line(lienzo, (50, 56, 86), (x0 - 12, caja.top + 8), (x0 - 12, caja.bottom - 8), 2)
        lienzo.blit(texto(t("mj.estrellas.encargo", "ENCARGO"), 8, g["oro"], sombra=False, pixel_=True), (x0, caja.top + 8))
        if self.cumplidos:                                      # cuántos encargos van cumplidos
            img = texto(str(self.cumplidos), 15, g["verde"], sombra=False)
            r = img.get_rect(topright=(caja.right - 54, caja.top + 4))
            lienzo.blit(img, r)
            cx, cy = r.left - 12, r.centery
            pygame.draw.lines(lienzo, g["verde"], False, [(cx - 5, cy), (cx - 1, cy + 4), (cx + 6, cy - 4)], 3)
        e = self.encargo
        if e is None:
            img = texto(t("mj.estrellas.espera", "esperando el próximo…"), 16, g["gris"], False, sombra=False)
            lienzo.blit(img, (x0, caja.top + 26))
            return
        frase = t("mj.estrellas.pide", "{q} pide: {c}", q=e["quien"], c=self.que_pide(e["tipo"]))
        img = texto(frase, 17, g["texto"], sombra=False)
        if img.get_width() > caja.right - x0 - 46:
            img = pygame.transform.smoothscale_by(img, (caja.right - x0 - 46) / img.get_width())
        lienzo.blit(img, (x0, caja.top + 22))
        self._polaroid(lienzo, caja.right - 24, caja.top + 34, e["tipo"], 0.75)
        frac = max(0.0, e["vida"] / e["vida0"])
        barra = pygame.Rect(x0, caja.bottom - 13, caja.right - x0 - 46, 6)
        pygame.draw.rect(lienzo, (34, 36, 60), barra, border_radius=3)
        col = g["oro"] if frac > 0.3 else g["naranja"]
        pygame.draw.rect(lienzo, col, (barra.x, barra.y, int(barra.w * frac), barra.h), border_radius=3)

    @staticmethod
    def _flash(nivel):
        s = pygame.Surface(VENTANA.size)
        s.fill((0, 0, 0))
        v = 14 * nivel
        pygame.draw.ellipse(s, (v, v, v + 6), (0, 0, *VENTANA.size))
        return s

    @staticmethod
    def _polaroid(lienzo, x, y, tipo, esc=1.0, giro=0):
        w, h = int(46 * esc), int(52 * esc)
        s = pygame.Surface((w, h), pygame.SRCALPHA)
        s.fill((245, 245, 240))
        foto = pygame.Rect(3, 3, w - 6, h - 14)
        pygame.draw.rect(s, (8, 10, 28), foto)
        c = foto.center
        if tipo == "relampago":
            pygame.draw.lines(s, (255, 250, 180), False, [(c[0] - 4, foto.top + 4), (c[0] + 3, c[1]), (c[0] - 3, c[1]),
                                                          (c[0] + 4, foto.bottom - 4)], 2)
        elif tipo == "aurora":
            for i in range(4):
                pygame.draw.line(s, (80, 255, 150), (foto.left + 6 + i * 8, foto.top + 6), (foto.left + 8 + i * 8, foto.bottom - 6), 2)
        elif tipo == "huracan":
            pygame.draw.circle(s, (230, 235, 250), c, int(9 * esc), 2)
            pygame.draw.circle(s, (230, 235, 250), c, 2)
        elif tipo == "cometa":
            pygame.draw.line(s, (255, 210, 120), (foto.left + 5, foto.top + 5), c, 3)
            pygame.draw.circle(s, (255, 250, 220), c, 3)
        elif tipo == "costarica":
            bandera_cr(s, foto.left + 4, foto.top + 5, foto.w - 8, foto.h - 10)
        else:
            pygame.draw.line(s, (80, 130, 220), (c[0] - 10, c[1]), (c[0] + 10, c[1]), 3)
            pygame.draw.rect(s, (220, 220, 230), (c[0] - 3, c[1] - 3, 6, 6))
        if giro:
            s = pygame.transform.rotate(s, giro)
        lienzo.blit(s, s.get_rect(center=(int(x), int(y))))
