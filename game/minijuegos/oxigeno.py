# -*- coding: utf-8 -*-
"""Microjuego «Oxígeno» (tarea: oxigeno → oxígeno).

El generador parte agua con electricidad (electrólisis, como la Estación Espacial): 2 H₂O → 2 H₂ + O₂.
Se VE cómo funciona: el agua sale del tanque, en las celdas suben burbujas (el hidrógeno sale el doble
que el oxígeno), el O₂ viaja hasta su tanque y el hidrógeno sale de la base por arriba.
Cada tanque lleno es el oxígeno de UN astronauta por UN día: 0,816 kg (NASA BVAD, tabla 3-33).

Cómo se juega (40 s):
  · aparecen fugas en las tuberías: clic para sellarlas (más rápido = más puntos);
  · si una fuga se deja mucho tiempo, la tubería se RAJA: hay que soldarla con 3 clics;
  · la PRESIÓN baja según las fugas: con muchas fugas (o una fuga vieja, o un tubo rajado) baja rápido;
    con una sola fuga nueva casi no baja, y sin fugas sube sola. El manómetro dice cuánto por segundo;
  · con poca presión el tanque se llena más despacio, y en 0 el tanque empieza a perder oxígeno;
  · a veces aparece una llave: si se atrapa, repara TODO de una vez.
El nivel sube solo si se juega bien: las fugas salen más seguido y duran menos. Al azar rinde poco.
"""
import math

import pygame

from .base import ZONA, COLORES
from ._kit import Partida, luz, degradado, guardado, texto, mezclar, vineta, translucido
<<<<<<< HEAD:base_lunar/microjuegos/oxigeno.py
from .. import sonido, textos
from ..textos import t, n
=======
from ..assets import sonido, textos
from ..assets.textos import t, n
>>>>>>> datos:game/minijuegos/oxigeno.py

TANQUE_AGUA = pygame.Rect(108, 292, 152, 278)
CELDAS = pygame.Rect(500, 285, 280, 165)
TANQUE_O2 = pygame.Rect(992, 352, 158, 222)
ESTANTE = pygame.Rect(786, 492, 198, 118)
ENERGIA = pygame.Rect(412, 398, 62, 40)
MANOMETRO = (1100, 262)
AGUA = [(262, 470), (380, 470), (380, 368), (500, 368)]
OXIGENO = [(780, 368), (880, 368), (880, 466), (992, 466)]
HIDROGENO = [(640, 285), (640, 232), (930, 232)]
RETORNO = [(262, 540), (760, 540), (760, 450)]
TUBOS = (AGUA, OXIGENO, HIDROGENO, RETORNO)
TINTE = ((80, 145, 225), (150, 215, 245), (225, 170, 110), (80, 145, 225))
HUD = (pygame.Rect(40, 110, 330, 90), pygame.Rect(1000, 110, 240, 90))
KG_TANQUE = 0.816


def _largo(pts):
    return sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))


def _sobre(pts, u):
    d = (u % 1.0) * _largo(pts)
    for a, b in zip(pts, pts[1:]):
        l = math.dist(a, b)
        if d <= l:
            k = d / l if l else 0
            return a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k
        d -= l
    return pts[-1]


def _tubo(s, pts, tinte, ox=0, oy=0):
    p = [(x - ox, y - oy) for x, y in pts]
    pygame.draw.lines(s, (34, 40, 66), False, p, 28)
    for q in p:
        pygame.draw.circle(s, (34, 40, 66), q, 14)
    pygame.draw.lines(s, (104, 116, 152), False, p, 20)
    pygame.draw.lines(s, mezclar(tinte, (104, 116, 152), 0.55), False, p, 10)
    pygame.draw.lines(s, (172, 184, 216), False, [(x - 3, y - 4) for x, y in p], 3)
    for q in p[1:-1]:                                        # codos con brida y tornillos
        pygame.draw.circle(s, (132, 142, 176), q, 15)
        pygame.draw.circle(s, (64, 72, 104), q, 15, 2)
        for k in range(4):
            a = math.pi / 4 + k * math.pi / 2
            pygame.draw.circle(s, (196, 202, 220), (int(q[0] + math.cos(a) * 9), int(q[1] + math.sin(a) * 9)), 2)


def _fondo():
    """Todo lo que no se mueve: pared, piso, tuberías, carcasas y letreros (se dibuja una sola vez)."""
<<<<<<< HEAD:base_lunar/microjuegos/oxigeno.py
    from ..texto_mate import fuente
=======
    from ..assets.texto_mate import fuente
>>>>>>> datos:game/minijuegos/oxigeno.py
    s = pygame.Surface(ZONA.size)
    ox, oy = ZONA.topleft
    s.blit(degradado(ZONA.w, ZONA.h, (30, 37, 62), (13, 16, 30)), (0, 0))
    for x in range(0, ZONA.w, 150):                          # paneles de la pared con remaches
        pygame.draw.line(s, (22, 27, 46), (x, 0), (x, ZONA.h - 90), 3)
        pygame.draw.line(s, (40, 48, 78), (x + 3, 0), (x + 3, ZONA.h - 90), 1)
        for y in range(18, ZONA.h - 100, 60):
            pygame.draw.circle(s, (44, 52, 84), (x + 12, y), 3)
            pygame.draw.circle(s, (44, 52, 84), (x + 138, y), 3)
    piso = pygame.Rect(0, ZONA.h - 88, ZONA.w, 88)
    s.blit(degradado(piso.w, piso.h, (36, 40, 58), (18, 20, 32)), piso)
    for x in range(-90, ZONA.w, 22):                         # rejilla del piso
        pygame.draw.line(s, (26, 29, 44), (x, piso.top), (x + 60, piso.bottom), 2)
    pygame.draw.line(s, (70, 78, 108), (0, piso.top), (ZONA.w, piso.top), 3)
    for pts, tinte in zip(TUBOS, TINTE):
        _tubo(s, pts, tinte, ox, oy)
    # tanque de agua (vidrio)
    r = TANQUE_AGUA.move(-ox, -oy)
    pygame.draw.rect(s, (52, 60, 92), r.inflate(14, 14), border_radius=26)
    pygame.draw.rect(s, (12, 18, 34), r, border_radius=22)
    for y in (r.top + 40, r.bottom - 40):
        pygame.draw.rect(s, (96, 106, 140), (r.left - 9, y, r.w + 18, 10), border_radius=4)
    # carcasa de las celdas
    c = CELDAS.move(-ox, -oy)
    pygame.draw.rect(s, (60, 68, 100), c.inflate(18, 18), border_radius=14)
    pygame.draw.rect(s, (18, 22, 40), c, border_radius=10)
    # cajita de energía y cable a las celdas
    e = ENERGIA.move(-ox, -oy)
    pygame.draw.line(s, (40, 40, 40), (e.right, e.centery), (c.left - 8, e.centery), 6)
    pygame.draw.line(s, (200, 160, 40), (e.right, e.centery), (c.left - 8, e.centery), 2)
    pygame.draw.rect(s, (70, 70, 60), e, border_radius=8)
    pygame.draw.rect(s, (230, 190, 50), e, 2, border_radius=8)
    cx, cy = e.center
    pygame.draw.polygon(s, (250, 210, 60), [(cx + 4, cy - 15), (cx - 8, cy + 2), (cx, cy + 2), (cx - 4, cy + 15),
                                            (cx + 9, cy - 3), (cx + 1, cy - 3)])
    # tanque de O₂
    o = TANQUE_O2.move(-ox, -oy)
    pygame.draw.rect(s, (70, 80, 116), o.inflate(16, 16), border_radius=60)
    pygame.draw.rect(s, (14, 20, 38), o, border_radius=54)
    pygame.draw.rect(s, (120, 130, 166), (o.centerx - 22, o.top - 22, 44, 16), border_radius=5)
    # respiradero del hidrógeno
    pygame.draw.rect(s, (58, 64, 92), (930 - ox, 216 - oy, 46, 32), border_radius=6)
    for k in range(4):
        pygame.draw.line(s, (24, 28, 44), (936 - ox, 222 - oy + k * 7), (970 - ox, 222 - oy + k * 7), 3)
    # estante de tanques llenos
    es = ESTANTE.move(-ox, -oy)
    pygame.draw.rect(s, (20, 26, 46), es, border_radius=12)
    pygame.draw.rect(s, (60, 72, 110), es, 2, border_radius=12)
    # manómetro (la escala de colores)
    mx, my = MANOMETRO[0] - ox, MANOMETRO[1] - oy
    pygame.draw.circle(s, (60, 68, 100), (mx, my), 74)
    pygame.draw.circle(s, (14, 18, 34), (mx, my), 66)
    for i in range(36):
        a = math.pi * (1 - i / 35)
        col = COLORES["rojo"] if i < 11 else COLORES["naranja"] if i < 20 else COLORES["verde"]
        pygame.draw.line(s, col, (mx + math.cos(a) * 50, my - math.sin(a) * 50),
                         (mx + math.cos(a) * 60, my - math.sin(a) * 60), 4)
    # letreros
    for txt, tam, col, pos in (("H₂O", 26, COLORES["texto"], (r.centerx, r.top + 20)),
                               ("2 H₂O → 2 H₂ + O₂", 22, COLORES["oro"], (c.centerx - 20, c.bottom + 44)),
                               ("H₂", 18, (255, 210, 150), (990 - ox, 232 - oy)),
                               ("O₂", 30, COLORES["texto"], (o.centerx, o.top + 30))):
        img = fuente(tam, True).render(txt, True, col)
        s.blit(img, img.get_rect(center=pos))
    img = fuente(15, True).render(t("mj.oxigeno.afuera", "hacia afuera"), True, (200, 170, 130))
    s.blit(img, img.get_rect(center=(990 - ox, 254 - oy)))
    img = fuente(15, True).render(t("mj.oxigeno.presion_tit", "PRESIÓN"), True, COLORES["gris"])
    s.blit(img, img.get_rect(center=(mx, my + 22)))
    return s


class Oxigeno(Partida):
    titulo = "Oxígeno: sellá las fugas"
    instruccion = "Hacé clic en las fugas antes de que se rajen las tuberías"
    tarea = "oxigeno"
    duracion = 40.0
    META = 7000
    ESCALA = 220
    COLOR = (120, 210, 255)

    def preparar(self):
        self.titulo = t("mj.oxigeno.titulo", "Oxígeno: sellá las fugas")
        self.instruccion = t("mj.oxigeno.instr", "Hacé clic en las fugas antes de que se rajen las tuberías")
        self.consejos = (t("mj.oxigeno.c1", "Si una fuga se deja, la tubería se raja: soldala con 3 clics."),
                         t("mj.oxigeno.c4", "Entre más fugas abiertas, más rápido baja la presión. Sin fugas, sube sola."),
                         t("mj.oxigeno.c2", "Atrapá la llave dorada: repara todo de una vez."))
        self.fugas = []           # x, y, edad, estado (abierta, rota, sellada), golpes, normal
        self.parches = []         # [x, y, horizontal, edad]
        self.presion = 1.0
        self.ritmo = 0.0          # cuánto cambia la presión por segundo (suavizado, para mostrarlo)
        self.al_tope = True       # para premiar cuando se vuelve a llevar al 100 %
        self.escape = 0.0         # para el aviso «¡Se escapa el oxígeno!»
        self.llenado = 0.0
        self.tanques = 0
        self.proxima = 0.4
        self.llave = None         # {x, y, vida}
        self.proxima_llave = 9.0
        self.alarma = 0.0
        self.brillo_tanque = 0.0
        self.tramos = [(a, b) for tubo in TUBOS for a, b in zip(tubo, tubo[1:])]
        self.burbujas = [[self.rng.uniform(TANQUE_AGUA.left + 14, TANQUE_AGUA.right - 14),
                          self.rng.uniform(TANQUE_AGUA.top + 60, TANQUE_AGUA.bottom - 10), self.rng.uniform(20, 50)]
                         for _ in range(14)]

    # ── reglas que cambian con el nivel ──────────────────────────────────────────────
    def vida(self):
        return max(1.1, 3.6 - 0.36 * (self.nv - 1))

    def radio(self):
        return max(28, 48 - 2.8 * (self.nv - 1))

    def cada(self):
        base = max(0.36, 1.4 - 0.15 * (self.nv - 1))
        return base * (0.75 if self.restante() <= 8 else 1.0)

    def maximo(self):
        return min(7, 2 + (self.nv + 1) // 2)

    # cuánto sube o baja la presión por segundo (1.0 = 100 %)
    RECUPERA_SIN = 0.08       # sin ninguna fuga: el generador la sube
    RECUPERA_CON = 0.025      # con fugas, el generador sigue empujando un poco

    def perdida(self, f):
        """Lo que bota una fuga por segundo: poco si es nueva, mucho si es vieja, muchísimo si se rajó."""
        if f["estado"] == "rota":
            return 0.15
        return 0.03 + 0.05 * min(1.0, f["edad"] / f["vida"])

    def activas(self):
        return [f for f in self.fugas if f["estado"] in ("abierta", "rota")]

    def _punto_nuevo(self):
        for _ in range(40):
            (x1, y1), (x2, y2) = self.rng.choice(self.tramos)
            u = self.rng.uniform(0.15, 0.85)
            p = (x1 + (x2 - x1) * u, y1 + (y2 - y1) * u)
            if any(h.collidepoint(p) for h in HUD):
                continue
            if all(math.hypot(p[0] - f["x"], p[1] - f["y"]) > 85 for f in self.activas()):
                horiz = abs(y2 - y1) < abs(x2 - x1)
                return p, horiz
        return None, True

    # ── juego ────────────────────────────────────────────────────────────────────────
    def jugar(self, dt):
        self.proxima -= dt
        if self.proxima <= 0:
            self.proxima = self.cada() * self.rng.uniform(0.8, 1.2)
            veces = 2 if self.nv >= 3 and self.rng.random() < 0.25 else 1
            for _ in range(veces):
                if len(self.activas()) < self.maximo():
                    p, horiz = self._punto_nuevo()
                    if p:
                        self.fugas.append({"x": p[0], "y": p[1], "edad": 0.0, "estado": "abierta", "golpes": 0,
                                           "horiz": horiz, "lado": self.rng.choice((-1, 1)),
                                           "vida": self.vida(), "sem": self.rng.uniform(0, 6)})
        # la llave dorada (desde el nivel 2)
        self.proxima_llave -= dt
        if self.llave is None and self.proxima_llave <= 0 and self.nv >= 2:
            self.llave = {"x": self.rng.uniform(380, 900), "y": self.rng.uniform(160, 200), "vida": 3.6}
            self.proxima_llave = self.rng.uniform(8.0, 11.0)
            sonido.play("combo", 0.6)
        if self.llave:
            self.llave["vida"] -= dt
            if self.llave["vida"] <= 0:
                self.llave = None
        for x, y in self.clics:
            self._clic(x, y)
        # la presión: el generador la empuja hacia arriba y cada fuga la baja (más entre más vieja)
        cambio = self.RECUPERA_SIN if not self.activas() else self.RECUPERA_CON
        for f in self.fugas:
            f["edad"] += dt
            if f["estado"] == "abierta":
                cambio -= self.perdida(f)
                if f["edad"] > f["vida"]:
                    f["estado"], f["edad"] = "rota", 0.0
                    self.perder(f["x"], f["y"] - 30, t("mj.oxigeno.rajo", "¡Se rajó!"), bajar=0.6, son="escape")
                    self.fx.sacudir(7, 0.3)
                    self.fx.chispas(f["x"], f["y"], (220, 235, 255), 24, (120, 320), (0.3, 0.7), con_brillo=False,
                                    tam=(3, 7))
            elif f["estado"] == "rota":
                cambio -= self.perdida(f)
        self.presion = max(0.0, min(1.0, self.presion + cambio * dt))
        mostrar = 0.0 if (cambio > 0 and self.presion >= 1.0) else cambio    # en 0 % sigue diciendo que se va
        self.ritmo += (mostrar - self.ritmo) * min(1.0, 6 * dt)
        if self.presion < 0.9:
            self.al_tope = False
        elif not self.al_tope and self.presion >= 0.999:             # la volvió a llevar al máximo
            self.al_tope = True
            mx, my = MANOMETRO
            self.ganar(25, mx - 150, my + 20, t("mj.oxigeno.tope", "¡Presión al 100 %!"), COLORES["verde"],
                       subir=0.1, combo=False, nota=False)
            self.fx.anillo(mx, my, COLORES["verde"], 110, 0.5, 4)
        if self.presion > 0:
            self.llenado += dt * 0.16 * self.presion
        else:                                                       # sin presión, el tanque pierde oxígeno
            self.llenado = max(0.0, self.llenado - 0.06 * dt)
            self.escape -= dt
            if self.escape <= 0 and self.llenado > 0:
                self.escape = 2.0
                self.fx.texto(TANQUE_O2.centerx - 20, TANQUE_O2.bottom + 30, t("mj.oxigeno.escapa", "¡Se escapa el oxígeno!"),
                              COLORES["rojo"], 20, 1.2, 25)
        if self.llenado >= 1.0:
            self.llenado = 0.0
            self.tanques += 1
            self.brillo_tanque = 1.0
            self.ganar(70, TANQUE_O2.centerx, TANQUE_O2.top - 20, t("mj.oxigeno.lleno", "¡Tanque lleno!"),
                       COLORES["cian"], subir=0.2, combo=False, nota=False)
            sonido.play("tanque")
            self.fx.chispas(TANQUE_O2.centerx, TANQUE_O2.centery, (150, 230, 255), 30, (80, 300))
            self.fx.anillo(TANQUE_O2.centerx, TANQUE_O2.centery, (150, 230, 255), 140, 0.6, 5)
        self.fugas = [f for f in self.fugas if f["estado"] != "sellada"]
        # alarma de presión baja
        self.alarma -= dt
        if self.presion < 0.35 and self.alarma <= 0:
            self.alarma = 1.4
            sonido.play("alarma", 0.7)
        abiertas = sum(1 for f in self.fugas if f["estado"] == "abierta")
        rotas = sum(1 for f in self.fugas if f["estado"] == "rota")
        self.bucle("siseo", min(0.9, 0.2 * abiertas + 0.32 * rotas))

    def _clic(self, x, y):
        if self.llave and math.hypot(self.llave["x"] - x, self.llave["y"] - y) < 46:
            lx, ly = self.llave["x"], self.llave["y"]
            self.llave = None
            sonido.play("llave")
            self.fx.destello((90, 80, 20), 0.35)
            self.fx.cartel(t("mj.oxigeno.total", "¡Reparación total!"), COLORES["oro"], 32, 1.2, ZONA.top + 150)
            self.fx.chispas(lx, ly, COLORES["oro"], 30, (100, 360))
            for f in self.activas():
                self._sellar(f, 12, nota=False)
            self.ganar(20, lx, ly + 30, subir=0.3)
            return
        cerca = [f for f in self.activas() if math.hypot(f["x"] - x, f["y"] - y) <= self.radio() + (8 if f["estado"] == "rota" else 0)]
        if not cerca:
            self.errar(x, y)
            return
        f = min(cerca, key=lambda f: math.hypot(f["x"] - x, f["y"] - y))
        if f["estado"] == "abierta":
            rapido = f["edad"] < f["vida"] * 0.4
            self._sellar(f, 10 + (10 if rapido else 0), t("mj.oxigeno.rapido", "¡Rápido!") if rapido else None)
        else:
            f["golpes"] += 1
            sonido.play("soldar")
            self.fx.chispas(f["x"], f["y"], (255, 210, 90), 14, (100, 300), (0.2, 0.5), grav=500)
            if f["golpes"] >= 3:
                self._sellar(f, 18, t("mj.oxigeno.soldada", "¡Soldada!"))

    def _sellar(self, f, puntos, frase=None, nota=True):
        f["estado"] = "sellada"
        self.parches.append([f["x"], f["y"], f["horiz"], 0.0])
        self.parches = self.parches[-24:]
        self.ganar(puntos, f["x"], f["y"] - 34, frase, COLORES["verde"], nota=nota)
        sonido.play("sello", 0.8)
        self.fx.chispas(f["x"], f["y"], COLORES["verde"], 16, (80, 260))
        self.fx.anillo(f["x"], f["y"], COLORES["verde"], 60, 0.35, 3)

    def animar(self, dt):
        self.brillo_tanque = max(0.0, self.brillo_tanque - dt * 1.5)
        for p in self.parches:
            p[3] += dt
        for b in self.burbujas:
            b[1] -= b[2] * dt
            if b[1] < self.nivel_agua() + 6:
                b[1] = TANQUE_AGUA.bottom - 10
                b[0] = self.rng.uniform(TANQUE_AGUA.left + 14, TANQUE_AGUA.right - 14)
        # vapor que sale de cada fuga
        for f in self.fugas:
            if f["estado"] == "sellada":
                continue
            k = min(1.0, f["edad"] / f["vida"]) if f["estado"] == "abierta" else 1.0
            cuantas = 1 + int(k * 3) + (2 if f["estado"] == "rota" else 0)
            if self.rng.random() < 0.85:
                if f["horiz"]:                              # sale para arriba o para abajo del tubo
                    ang = -math.pi / 2 if f["lado"] < 0 else math.pi / 2
                else:                                       # sale para un costado
                    ang = math.pi if f["lado"] < 0 else 0.0
                self.fx.chispas(f["x"], f["y"], (205, 222, 245), cuantas, (90 + 160 * k, 200 + 260 * k), (0.25, 0.55),
                                tam=(3 + 3 * k, 6 + 6 * k), con_brillo=False, angulo=ang, abre=0.35, roce=2.5)
        if self.jugando():
            self.bucle("zumbido", 0.35)
            self.bucle("burbujas", 0.25 + 0.4 * self.presion)

    def nivel_agua(self):
        return TANQUE_AGUA.top + 70 + 6 * math.sin(self.t * 1.3)

    # ── dibujo ───────────────────────────────────────────────────────────────────────
    def escena(self, lienzo):
        g = COLORES
        lienzo.blit(guardado(("oxi_fondo", textos.IDIOMA), _fondo), ZONA.topleft)
        # agua del tanque con olas y burbujas
        r = TANQUE_AGUA
        sup = self.nivel_agua()
        pts = [(r.left + 6, r.bottom - 8)]
        for i in range(13):
            x = r.left + 6 + i * (r.w - 12) / 12
            pts.append((x, sup + 4 * math.sin(self.t * 3 + i * 0.8)))
        pts.append((r.right - 6, r.bottom - 8))
        pygame.draw.polygon(lienzo, (40, 100, 190), pts)
        pygame.draw.lines(lienzo, (130, 190, 250), False, pts[1:-1], 3)
        for x, y, _v in self.burbujas:
            pygame.draw.circle(lienzo, (150, 200, 255), (int(x), int(y)), 3, 1)
        pygame.draw.line(lienzo, (190, 220, 255), (r.left + 16, r.top + 20), (r.left + 16, r.bottom - 30), 3)
        # flujos por dentro de las tuberías (más lentos con poca presión)
        vel = 0.2 + 0.8 * self.presion
        for tubo, col, cant, v in ((AGUA, (150, 205, 255), 7, 0.33), (OXIGENO, (235, 250, 255), 7, 0.42),
                                   (HIDROGENO, (255, 215, 160), 6, 0.5), (RETORNO, (120, 180, 240), 8, 0.25)):
            for k in range(cant):
                x, y = _sobre(tubo, self.t * v * vel + k / cant)
                pygame.draw.circle(lienzo, col, (int(x), int(y)), 4)
        # celdas: el hidrógeno (izquierda) sale el doble que el oxígeno (derecha)
        for i in range(6):
            x0 = CELDAS.left + 14 + i * 44
            celda = pygame.Rect(x0, CELDAS.top + 14, 36, CELDAS.h - 28)
            pygame.draw.rect(lienzo, (24, 60, 110), celda, border_radius=6)
            luz(lienzo, celda.centerx, celda.centery, 46, (30, 70, 140), 0.4 + 0.3 * self.presion)
            pygame.draw.line(lienzo, (150, 160, 190), (x0 + 9, celda.top + 6), (x0 + 9, celda.bottom - 6), 3)
            pygame.draw.line(lienzo, (150, 160, 190), (x0 + 27, celda.top + 6), (x0 + 27, celda.bottom - 6), 3)
            for k in range(6):
                ph = (self.t * (0.7 + 0.08 * i) * (0.3 + 0.7 * self.presion) + k / 6 + i * 0.13) % 1.0
                pygame.draw.circle(lienzo, (255, 230, 190), (x0 + 9 + int(3 * math.sin(k + self.t * 4)),
                                                              int(celda.bottom - 8 - ph * (celda.h - 16))), 3)
            for k in range(3):
                ph = (self.t * (0.6 + 0.07 * i) * (0.3 + 0.7 * self.presion) + k / 3 + i * 0.29) % 1.0
                pygame.draw.circle(lienzo, (220, 245, 255), (x0 + 27, int(celda.bottom - 8 - ph * (celda.h - 16))), 3)
        img = texto("H₂ ×2   O₂ ×1", 15, (200, 210, 230), sombra=False)
        lienzo.blit(img, img.get_rect(midtop=(CELDAS.centerx - 20, CELDAS.bottom + 12)))
        # tanque de O₂ que se va llenando
        o = TANQUE_O2.inflate(-14, -14)
        alto = int((o.h - 8) * self.llenado)
        if alto > 4:
            liq = pygame.Rect(o.left + 4, o.bottom - 4 - alto, o.w - 8, alto)
            lienzo.blit(degradado(liq.w, liq.h, (190, 240, 255), (60, 150, 220)), liq)
            pygame.draw.rect(lienzo, (14, 20, 38), o.inflate(8, 8), 6, border_radius=50)
        luz(lienzo, o.centerx, o.centery, 120, (80, 180, 255), 0.25 + 0.6 * self.brillo_tanque)
        img = texto(f"{n(self.llenado * 100, 0)} %", 22, (20, 30, 60) if self.llenado > 0.55 else g["texto"])
        lienzo.blit(img, img.get_rect(center=(o.centerx, o.centery + 30)))
        # tanques llenos en el estante
        es = ESTANTE
        lienzo.blit(texto(t("mj.oxigeno.estante", "TANQUES LLENOS"), 8, g["cian"], sombra=False, pixel_=True),
                    (es.left + 12, es.top + 10))
        for i in range(min(self.tanques, 7)):
            cap = pygame.Rect(es.left + 12 + i * 25, es.top + 28, 19, 40)
            pygame.draw.rect(lienzo, (150, 220, 255), cap, border_radius=9)
            pygame.draw.rect(lienzo, (240, 250, 255), (cap.x + 4, cap.y + 5, 4, 26), border_radius=2)
        img = texto(t("mj.oxigeno.kg", "{k} kg de O₂", k=n(self.tanques * KG_TANQUE, 3 if self.tanques else 0)), 17,
                    g["texto"], sombra=False)
        lienzo.blit(img, (es.left + 12, es.top + 74))
        img = texto(t("mj.oxigeno.dia", "1 tanque = 1 astronauta, 1 día"), 14, g["gris"], False, sombra=False)
        lienzo.blit(img, (es.left + 12, es.top + 96))
        # parches de las fugas selladas
        for x, y, horiz, edad in self.parches:
            w, h = (34, 24) if horiz else (24, 34)
            pr = pygame.Rect(0, 0, w, h)
            pr.center = (int(x), int(y))
            pygame.draw.rect(lienzo, (90, 150, 110), pr, border_radius=5)
            pygame.draw.rect(lienzo, (40, 80, 56), pr, 2, border_radius=5)
            for dx, dy in ((-1, -1), (1, 1)) if horiz else ((-1, -1), (1, 1)):
                pygame.draw.circle(lienzo, (200, 220, 205), (pr.centerx + dx * (w // 2 - 6), pr.centery + dy * (h // 2 - 6)), 2)
            if edad < 0.5:
                luz(lienzo, x, y, 50, (80, 220, 120), 1 - edad / 0.5)
        # fugas
        for f in self.fugas:
            p = (int(f["x"]), int(f["y"]))
            if f["estado"] == "abierta":
                k = min(1.0, f["edad"] / f["vida"])
                col = mezclar(mezclar(g["texto"], g["naranja"], k * 1.6), g["rojo"], (k - 0.6) * 2.5)
                pulso = 1 + 0.1 * math.sin(f["edad"] * (10 + 10 * k))
                rr = int(self.radio() * pulso)
                pygame.draw.circle(lienzo, col, p, rr, 3)
                if k > 0.02:                                 # lo que le queda, como un reloj
                    pygame.draw.arc(lienzo, col, (p[0] - rr - 7, p[1] - rr - 7, 2 * rr + 14, 2 * rr + 14),
                                    math.pi / 2, math.pi / 2 + 2 * math.pi * (1 - k), 4)
                luz(lienzo, *p, 30, (200, 220, 255), 0.5)
            else:
                pulso = 0.6 + 0.4 * math.sin(self.t * 12 + f["sem"])
                luz(lienzo, *p, 70, (255, 60, 40), 0.5 * pulso)
                for a in (0.5, 2.2, 3.9, 5.1):                  # la grieta
                    pygame.draw.line(lienzo, (255, 120, 80), p, (p[0] + math.cos(a + f["sem"]) * 16,
                                                                 p[1] + math.sin(a + f["sem"]) * 16), 3)
                rr = int(self.radio() + 8)
                for s in range(3):                              # 3 golpes de soldadura
                    col = g["oro"] if s < f["golpes"] else g["rojo"]
                    a0 = math.pi / 2 + s * 2 * math.pi / 3 + 0.08
                    pygame.draw.arc(lienzo, col, (p[0] - rr, p[1] - rr, 2 * rr, 2 * rr), a0, a0 + 2 * math.pi / 3 - 0.16, 5)
                img = texto("×3", 18, g["rojo"])
                lienzo.blit(img, img.get_rect(midleft=(p[0] + rr + 6, p[1])))
        # la llave dorada
        if self.llave:
            lx, ly = self.llave["x"], self.llave["y"] + 6 * math.sin(self.t * 5)
            luz(lienzo, lx, ly, 90, g["oro"], 0.6 + 0.3 * math.sin(self.t * 9))
            self._llave(lienzo, lx, ly)
            pygame.draw.arc(lienzo, g["oro"], (lx - 44, ly - 44, 88, 88), math.pi / 2,
                            math.pi / 2 + 2 * math.pi * self.llave["vida"] / 3.6, 3)
        # manómetro: la aguja
        mx, my = MANOMETRO
        a = math.pi * (1 - self.presion)
        punta = (mx + math.cos(a) * 54, my - math.sin(a) * 54)
        col = g["verde"] if self.presion > 0.55 else g["naranja"] if self.presion > 0.32 else g["rojo"]
        pygame.draw.line(lienzo, g["texto"], (mx, my), punta, 4)
        luz(lienzo, *punta, 26, col, 0.9)
        pygame.draw.circle(lienzo, g["texto"], (mx, my), 7)
        img = texto(f"{int(self.presion * 100)} %", 22, col)
        lienzo.blit(img, img.get_rect(center=(mx, my + 46)))
        self._flechas(lienzo, mx + 92, my)
        # alarma: bordes rojos que laten
        if self.presion < 0.35 and self.etapa == "juego":
            v = vineta((255, 30, 30)).copy()
            v.set_alpha(int(110 + 90 * math.sin(self.t * 8)))
            lienzo.blit(v, ZONA.topleft)
            img = texto(t("mj.oxigeno.baja", "¡PRESIÓN BAJA!"), 26, g["rojo"])
            r = img.get_rect(center=(ZONA.centerx, ZONA.top + 44))
            lienzo.blit(translucido(r.w + 30, r.h + 10, (30, 6, 10), 170, 10), r.inflate(30, 10))
            lienzo.blit(img, r)
        img = texto(t("mj.oxigeno.nota", "La Estación Espacial hace su oxígeno partiendo agua con electricidad "
                                         "(electrólisis, NASA)."), 17, g["gris"], False, sombra=False)
        lienzo.blit(img, (ZONA.left + 20, ZONA.bottom - 28))

    def _flechas(self, lienzo, x, y):
        """Al lado del manómetro: flechas que dicen si la presión sube o baja, y qué tan rápido (1 a 3)."""
        r = self.ritmo
        if self.etapa != "juego" or abs(r) < 0.012:
            pygame.draw.line(lienzo, (110, 118, 140), (x - 9, y), (x + 9, y), 4)        # estable
            return
        baja = r < 0
        cuantas = 1 if abs(r) < 0.06 else 2 if abs(r) < 0.14 else 3
        col = (COLORES["rojo"] if cuantas >= 2 else COLORES["naranja"]) if baja else COLORES["verde"]
        paso = 19
        y0 = y - (cuantas - 1) * paso / 2
        avance = (self.t * (1.5 + cuantas)) % 1.0                                     # se van moviendo
        for i in range(cuantas):
            yy = y0 + i * paso + (avance - 0.5) * 6 * (1 if baja else -1)
            k = 0.55 + 0.45 * (1 - abs(((i / max(1, cuantas)) + avance) % 1.0 - 0.5) * 2)
            c = mezclar((30, 34, 50), col, k)
            d = 7 if baja else -7
            pygame.draw.lines(lienzo, c, False, [(x - 11, yy - d), (x, yy + d), (x + 11, yy - d)], 5)
        if cuantas == 3:
            luz(lienzo, x, y, 34, col, 0.4 + 0.3 * math.sin(self.t * 10))

    @staticmethod
    def _llave(lienzo, x, y):
        s = pygame.Surface((90, 90), pygame.SRCALPHA)
        oro, osc = (250, 205, 70), (150, 110, 20)
        pygame.draw.line(s, osc, (22, 68), (60, 30), 14)
        pygame.draw.line(s, oro, (22, 68), (60, 30), 10)
        pygame.draw.circle(s, oro, (64, 26), 16)
        pygame.draw.circle(s, (0, 0, 0, 0), (70, 20), 8)
        pygame.draw.polygon(s, (0, 0, 0, 0), [(64, 26), (80, 4), (88, 14)])
        pygame.draw.circle(s, oro, (20, 70), 10)
        pygame.draw.circle(s, osc, (20, 70), 4)
        lienzo.blit(s, s.get_rect(center=(int(x), int(y))))
