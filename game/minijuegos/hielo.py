# -*- coding: utf-8 -*-
"""Microjuego «Hielo» (tarea: hielo → agua).

Corte del suelo de un cráter del polo sur que nunca ve el sol: arriba el vehículo con su taladro, abajo
regolito con BOLSAS DE HIELO y rocas. La NASA confirmó ese hielo con la misión LCROSS (2009).
El suelo NO es plano: tiene lomitas y cráteres chiquitos (cambian en cada partida). El vehículo sube,
baja y se inclina con el terreno, y la profundidad se cuenta desde donde está parado. En el fondo de los
cráteres, que nunca reciben sol, el hielo suele quedar más cerca de la superficie (y se ve escarcha).

Cómo se juega (38 s):
  · el vehículo sigue al ratón por la superficie; mantener el clic perfora, soltar lo detiene;
  · hay que soltar con la punta DENTRO de una bolsa de hielo (en el centro: «¡Perfecto!», más puntos);
  · si la punta toca una roca, el taladro se atasca;
  · se oye cuando la punta entra al hielo (el ruido cambia a un chirrido agudo).
Al subir de nivel el taladro baja más rápido, las bolsas son más delgadas y, desde el nivel 3, el suelo
deja de verse: un RADAR las muestra cada pocos segundos (se quedan a la vista un rato y después se
apagan despacio: hay que acordarse dónde estaban).
"""
import math
import random

import pygame

from .base import ZONA, COLORES
from ._kit import Partida, luz, degradado, guardado, texto, mezclar, translucido
from ..assets import sonido
from ..assets.textos import t, n

SUP = 318                     # altura media de la superficie (las lomitas suben y los cráteres bajan)
ARRIBA, ABAJO = SUP - 42, SUP + 50   # lo más alto y lo más hondo que llega el suelo
FONDO = 612                   # y donde empieza la roca firme
X_MIN, X_MAX = ZONA.left + 80, ZONA.right - 80
HIELO, HIELO_C = (150, 210, 245), (215, 242, 255)
RADAR_CADA = 4.0              # segundos entre una pasada del radar y la otra
EJE = 34                      # media distancia entre las ruedas del vehículo


def _perfil(rng):
    """La altura del suelo en cada x de la zona: ondulación suave, 3 lomitas y 2 cráteres."""
    w = ZONA.w
    f1, f2 = rng.uniform(0, 6), rng.uniform(0, 6)
    ys = [SUP + 7 * math.sin(i / 97 + f1) + 4 * math.sin(i / 41 + f2) for i in range(w)]
    crateres = []
    for _ in range(80):
        if len(crateres) == 2:
            break
        r = rng.uniform(80, 112)
        c = rng.uniform(130 + r, w - 130 - r)
        if all(abs(c - c2) > r + r2 + 70 for c2, r2, _d in crateres):
            crateres.append((c, r, rng.uniform(36, 48)))
    lomas = []
    for _ in range(120):
        if len(lomas) == 3:
            break
        a, h = rng.uniform(42, 70), rng.uniform(24, 40)
        c = rng.uniform(90, w - 90)
        if (all(abs(c - c2) > r2 + a + 24 for c2, r2, _d in crateres)
                and all(abs(c - c3) > a + a3 for c3, a3, _h in lomas)):
            lomas.append((c, a, h))
    for i in range(w):
        y = ys[i]
        for c, a, h in lomas:
            y -= h * math.exp(-((i - c) / a) ** 2)
        for c, r, d in crateres:
            dx = abs(i - c)
            if dx < r:
                y += d * (1 - (dx / r) ** 2)
            y -= 11 * math.exp(-((dx - r) / 16) ** 2)             # el borde levantado del cráter
        ys[i] = max(ARRIBA, min(ABAJO, y))
    # a coordenadas del lienzo
    return ys, [(ZONA.left + c, r, d) for c, r, d in crateres]


def _cielo():
    rng = random.Random(9)
    alto = ABAJO + 10 - ZONA.top
    s = pygame.Surface((ZONA.w, alto))
    s.blit(degradado(ZONA.w, alto, (2, 3, 12), (12, 14, 30)), (0, 0))
    for _ in range(170):
        b = rng.randint(70, 230)
        s.set_at((rng.randint(0, ZONA.w - 1), rng.randint(0, alto - 1)), (b, b, min(255, b + 25)))
    # el borde del cráter grande, a lo lejos: sus cumbres sí reciben sol
    base = SUP - ZONA.top + 6
    pts = [(0, alto)]
    for x in range(0, ZONA.w + 30, 30):
        pts.append((x, base - 66 - 30 * abs(math.sin(x / 210)) - 12 * math.sin(x / 47)))
    pts.append((ZONA.w, alto))
    pygame.draw.polygon(s, (36, 34, 42), pts)
    for (x1, y1), (x2, y2) in zip(pts[1:-2], pts[2:-1]):
        if y2 < base - 90 or y1 < base - 90:
            pygame.draw.line(s, (210, 180, 110), (x1, y1), (x2, y2), 3)
    # la Tierra, bajita en el horizonte
    pygame.draw.circle(s, (40, 100, 200), (880, 52), 20)
    pygame.draw.circle(s, (80, 160, 100), (874, 46), 8)
    pygame.draw.circle(s, (230, 238, 250), (887, 58), 5)
    return s


def _fondo(ys, crateres, rng):
    """Cielo + el corte del suelo siguiendo el relieve (se arma una vez por partida)."""
    s = pygame.Surface(ZONA.size)
    s.blit(guardado("hielo_cielo", _cielo), (0, 0))
    w, h = ZONA.w, ZONA.h
    oy = ZONA.top
    tierra = pygame.Surface((w, h), pygame.SRCALPHA)
    techo = int(min(ys)) - oy
    tierra.blit(degradado(w, FONDO - oy - techo, (124, 114, 104), (74, 67, 62)), (0, techo))
    fondo_rel = FONDO - oy
    for _ in range(10):                                            # capas que siguen el relieve
        o = rng.randint(16, FONDO - SUP - 12)
        k = o / (FONDO - SUP)                                      # las hondas son más planas
        fase, onda = rng.random() * 6, rng.uniform(60, 140)
        pts = [(i, (ys[min(w - 1, i)] * (1 - k) + SUP * k) - oy + o + 5 * math.sin(i / onda + fase))
               for i in range(0, w + 20, 20)]
        pygame.draw.lines(tierra, (98, 90, 83) if rng.random() < 0.5 else (134, 124, 114), False, pts, 2)
    for _ in range(2800):                                          # granitos
        x, y = rng.randint(0, w - 1), rng.randint(techo, fondo_rel - 1)
        c = rng.choice(((140, 130, 120), (90, 83, 77), (110, 102, 94), (160, 150, 140)))
        tierra.fill(c, (x, y, rng.choice((1, 2, 2, 3)), 2))
    # la roca firme
    roca = pygame.Rect(0, fondo_rel, w, h - fondo_rel)
    tierra.blit(degradado(roca.w, roca.h, (60, 55, 62), (34, 31, 38)), roca)
    pts = [(x, fondo_rel + 5 * math.sin(x / 37) + 3 * math.sin(x / 11)) for x in range(0, w + 20, 10)]
    pygame.draw.polygon(tierra, (60, 55, 62), [(0, h)] + pts + [(w, h)])
    pygame.draw.lines(tierra, (90, 84, 92), False, pts, 2)
    for _ in range(500):
        tierra.fill((44, 40, 48), (rng.randint(0, w - 1), rng.randint(fondo_rel + 6, h - 1), 2, 2))
    # el fondo de los cráteres es más oscuro (nunca le da el sol)
    for c, r, _d in crateres:
        for i in range(int(c - r * 0.85) - ZONA.left, int(c + r * 0.85) - ZONA.left):
            k = max(0.0, min(1.0, 1 - abs(i + ZONA.left - c) / (r * 0.85)))
            if not 0 <= i < w:
                continue
            y0 = int(ys[i]) - oy
            sombra = pygame.Surface((1, 46), pygame.SRCALPHA)
            sombra.fill((20, 22, 40, int(90 * k)))
            tierra.blit(sombra, (i, y0))
    # recortar con la forma del suelo
    mascara = pygame.Surface((w, h), pygame.SRCALPHA)
    borde = [(i, ys[i] - oy) for i in range(0, w, 4)] + [(w - 1, ys[w - 1] - oy)]
    pygame.draw.polygon(mascara, (255, 255, 255, 255), [(0, h)] + borde + [(w, h)])
    tierra.blit(mascara, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    s.blit(tierra, (0, 0))
    pygame.draw.lines(s, (172, 162, 150), False, borde, 3)
    # escarcha en el fondo de los cráteres y piedritas sueltas sobre la superficie
    for c, r, _d in crateres:
        for _ in range(26):
            i = int(c + rng.uniform(-0.6, 0.6) * r) - ZONA.left
            s.fill(rng.choice((HIELO_C, HIELO, (190, 230, 250))), (i, int(ys[i]) - oy - 1, 2, 2))
    for _ in range(26):
        i = rng.randint(10, w - 10)
        rr = rng.uniform(2.5, 6)
        y = ys[i] - oy - rr * 0.6
        pygame.draw.ellipse(s, (112, 104, 98), (i - rr, y - rr * 0.7, 2 * rr, rr * 1.4))
        pygame.draw.ellipse(s, (150, 142, 132), (i - rr * 0.6, y - rr * 0.6, rr, rr * 0.5))
    return s


class Hielo(Partida):
    titulo = "Hielo: perforá el cráter"
    instruccion = "Mantené el clic para perforar y soltá dentro de una bolsa de hielo"
    tarea = "hielo"
    duracion = 38.0
    META = 5800
    ESCALA = 24
    COLOR = HIELO
    Y_CARTEL = ZONA.bottom - 96

    def preparar(self):
        self.titulo = t("mj.hielo.titulo", "Hielo: perforá el cráter")
        self.instruccion = t("mj.hielo.instr", "Mantené el clic para perforar y soltá dentro de una bolsa de hielo")
        self.consejos = (t("mj.hielo.c4", "Mové el ratón para llevar el vehículo. En los cráteres el hielo queda más cerca."),
                         t("mj.hielo.c2", "Soltá en el centro de la bolsa: «¡Perfecto!» vale el doble."),
                         t("mj.hielo.c3", "Escuchá: cuando la punta entra al hielo, el taladro chirría."))
        terreno = random.Random(self.rng.random())
        self.perfil, self.crateres = _perfil(terreno)
        self.fondo = _fondo(self.perfil, self.crateres, terreno)
        self.x = float(ZONA.centerx)
        self.vx = 0.0
        self.rueda = 0.0
        self.angulo = 0.0
        self.prof = 0.0
        self.estado = "libre"          # libre · bajando · subiendo · atascado
        self.atasco = 0.0
        self.carga = None              # «perfecto» o «bien» si sube con núcleo
        self.previo = False
        self.nucleos = 0
        self.volando = []              # núcleos que viajan al contador: [x, y, k]
        self.hoyos = []                # (x, arriba, profundidad, bien)
        self.bolsas = []
        self.rocas = []
        self.radar = 1.6
        self.onda = None               # radio de la onda del radar
        self.onda_de = (0, 0)          # desde dónde salió
        for _ in range(5):
            self._bolsa_nueva()
        for _ in range(5):
            self._roca_nueva()

    # ── el suelo ─────────────────────────────────────────────────────────────────────
    def sup(self, x):
        """La altura de la superficie en x."""
        i = int(x) - ZONA.left
        return self.perfil[max(0, min(len(self.perfil) - 1, i))]

    def grosor(self):
        return max(30, 86 - 8 * (self.nv - 1))

    def baja(self):
        return 130 + 26 * (self.nv - 1)

    def visible_min(self):
        """Qué tanto se ven las bolsas entre radar y radar (1 = siempre; 0 = nada)."""
        return 1.0 if self.nv <= 2 else max(0.0, 0.62 - 0.14 * (self.nv - 3))

    def ver_radar(self):
        """Segundos que una bolsa queda bien a la vista después de que el radar la toca."""
        return max(1.1, 2.1 - 0.15 * (self.nv - 3))

    def _bolsa_nueva(self, lejos_de=None):
        for _ in range(80):
            w = self.rng.uniform(110, 190) - 6 * (self.nv - 1)
            h = self.grosor() * self.rng.uniform(0.9, 1.15)
            if self.crateres and self.rng.random() < 0.5:              # debajo de un cráter: más cerca
                c, r, _d = self.rng.choice(self.crateres)
                cx = self.rng.uniform(c - r * 0.55, c + r * 0.55)
                hondo = 58
            else:
                cx = self.rng.uniform(X_MIN + w / 2, X_MAX - w / 2)
                hondo = 88
            cx = max(X_MIN + w / 2, min(X_MAX - w / 2, cx))
            techo = max(self.sup(x) for x in range(int(cx - w / 2), int(cx + w / 2) + 1, 8))
            lo, hi = techo + hondo + h / 2, FONDO - 30 - h / 2
            if lo > hi:
                continue
            cy = lo + (hi - lo) * self.rng.random() ** (1.6 if hondo < 80 else 1.0)
            if lejos_de is not None and abs(cx - lejos_de) < 60:
                continue
            if all(abs(cx - b["cx"]) > (w + b["w"]) / 2 + 26 for b in self.bolsas if b["cargas"] > 0):
                cargas = 3 if w > 165 else 2 if w > 130 else 1
                self.bolsas.append({"cx": cx, "cy": cy, "w": w, "h": h, "cargas": cargas, "vis": 1.0, "ver": 0.0,
                                    "sem": self.rng.uniform(0, 6), "vacia": 0.0, "img": self._dibujo_bolsa(w, h)})
                return

    def _dibujo_bolsa(self, w, h):
        s = pygame.Surface((int(w) + 8, int(h) + 8), pygame.SRCALPHA)
        r = pygame.Rect(4, 4, int(w), int(h))
        pygame.draw.ellipse(s, (*HIELO, 255), r)
        pygame.draw.ellipse(s, (*mezclar(HIELO, (40, 90, 140), 0.35), 255), r.inflate(-int(w * 0.18), -int(h * 0.3)))
        pygame.draw.ellipse(s, (*HIELO, 255), r.inflate(-int(w * 0.4), -int(h * 0.55)))
        for i in range(5):
            x = r.left + r.w * (0.2 + 0.15 * i)
            y = r.top + r.h * (0.3 + 0.1 * (i % 3))
            pygame.draw.line(s, (*HIELO_C, 255), (x, y), (x + 12, y - 5), 2)
        pygame.draw.ellipse(s, (*HIELO_C, 255), r, 2)
        return s

    def _roca_nueva(self):
        for _ in range(60):
            r = self.rng.uniform(17, 30)
            x = self.rng.uniform(X_MIN, X_MAX)
            arriba = self.sup(x) + 40
            if arriba > FONDO - 40:
                continue
            y = self.rng.uniform(arriba, FONDO - 40)
            if any(self._dentro(b, x, y, margen=r + 14) for b in self.bolsas if b["cargas"] > 0):
                continue
            if all(math.hypot(x - q["x"], y - q["y"]) > r + q["r"] + 30 for q in self.rocas):
                pts = [(math.cos(a) * r * self.rng.uniform(0.8, 1.15), math.sin(a) * r * self.rng.uniform(0.8, 1.15))
                       for a in [k * 2 * math.pi / 9 for k in range(9)]]
                self.rocas.append({"x": x, "y": y, "r": r, "pts": pts})
                return

    @staticmethod
    def _dentro(b, x, y, margen=0.0):
        rx, ry = b["w"] / 2 + margen, b["h"] / 2 + margen
        return ((x - b["cx"]) / rx) ** 2 + ((y - b["cy"]) / ry) ** 2 <= 1

    def bolsa_en(self, x, y):
        for b in self.bolsas:
            if b["cargas"] > 0 and self._dentro(b, x, y):
                return b
        return None

    def roca_en(self, x, y):
        for q in self.rocas:
            if math.hypot(x - q["x"], y - q["y"]) <= q["r"]:
                return q
        return None

    @property
    def punta(self):
        return self.sup(self.x) + self.prof

    # ── juego ────────────────────────────────────────────────────────────────────────
    def jugar(self, dt):
        suelto = self.previo and not self.apretado
        apreto = self.apretado and not self.previo
        self.previo = self.apretado
        # el vehículo sigue al ratón (si no está perforando); en las cuestas va un poco más lento
        if self.estado == "libre":
            meta = max(X_MIN, min(X_MAX, self.raton[0]))
            cuesta = abs(self.sup(self.x + EJE) - self.sup(self.x - EJE)) / (2 * EJE)
            tope = 900.0 * (1 - min(0.45, cuesta * 1.3))
            v = max(-tope, min(tope, (meta - self.x) * 9))
            self.vx = v
            self.x += v * dt
            self.rueda += v * dt / 11
            if apreto or (self.apretado and abs(v) < 40):
                self.estado = "bajando"
        else:
            self.vx = 0.0
        if self.estado == "bajando":
            if suelto or not self.apretado:
                self._soltar()
            else:
                self.prof += self.baja() * dt
                y = self.punta
                b = self.bolsa_en(self.x, y)
                self.fx.chispas(self.x, self.sup(self.x) - 2, HIELO_C if b else (150, 138, 124), 1, (60, 180),
                                (0.3, 0.6), grav=420, tam=(2, 4), con_brillo=bool(b), angulo=-math.pi / 2, abre=0.9)
                if self.roca_en(self.x, y) or y >= FONDO:
                    self.estado, self.atasco = "atascado", 0.9
                    self.hoyos.append((self.x, self.sup(self.x), self.prof, False))
                    self.perder(self.x + 70, y, t("mj.hielo.roca", "¡Roca!"), bajar=0.6, son="atasco")
                    self.fx.sacudir(8, 0.35)
                    self.fx.chispas(self.x, y, (255, 170, 80), 18, (100, 300), (0.2, 0.5), grav=600)
        elif self.estado == "atascado":
            self.atasco -= self.dt
            if self.atasco <= 0:
                self.estado = "subiendo"
        elif self.estado == "subiendo":
            self.prof -= 640 * dt
            if self.prof <= 0:
                self.prof, self.estado = 0.0, "libre"
                if self.carga:
                    self.volando.append([self.x, self.sup(self.x) - 40, 0.0])
                    self.carga = None
        # el radar (desde el nivel 3)
        if self.nv >= 3:
            self.radar -= dt
            if self.radar <= 0:
                self.radar = RADAR_CADA
                self.onda = 0.0
                self.onda_de = (self.x, self.sup(self.x))
                sonido.play("radar", 0.7)
        # bolsas vacías que se van y nuevas que aparecen
        for b in self.bolsas:
            if b["cargas"] <= 0:
                b["vacia"] += dt
        if any(b["cargas"] <= 0 and b["vacia"] > 1.4 for b in self.bolsas):
            self.bolsas = [b for b in self.bolsas if not (b["cargas"] <= 0 and b["vacia"] > 1.4)]
        while sum(1 for b in self.bolsas if b["cargas"] > 0) < 5:
            antes = len(self.bolsas)
            self._bolsa_nueva(lejos_de=self.x)
            if len(self.bolsas) == antes:
                break
        while len(self.rocas) < 4 + self.nv // 2:
            antes = len(self.rocas)
            self._roca_nueva()
            if len(self.rocas) == antes:
                break
        # sonido: motor, tierra o hielo
        en_hielo = self.estado == "bajando" and self.bolsa_en(self.x, self.punta) is not None
        self.bucle("motor", 0.55 if self.estado in ("bajando", "subiendo") else min(0.3, abs(self.vx) / 900 * 0.6 + 0.08))
        self.bucle("tierra", 0.7 if self.estado == "bajando" and not en_hielo else 0.0, 14)
        self.bucle("hielo", 0.8 if en_hielo else 0.0, 14)

    def _soltar(self):
        y = self.punta
        b = self.bolsa_en(self.x, y)
        arriba = self.sup(self.x)
        if b:
            # qué tan al centro (en vertical) quedó la punta, según el grosor de la bolsa en esa x
            mitad = (b["h"] / 2) * math.sqrt(max(0.0, 1 - ((self.x - b["cx"]) / (b["w"] / 2)) ** 2))
            perfecto = abs(y - b["cy"]) <= max(6.0, mitad * 0.4)
            b["cargas"] -= 1
            self.carga = "perfecto" if perfecto else "bien"
            self.nucleos += 1
            self.hoyos.append((self.x, arriba, self.prof, True))
            if perfecto:
                self.ganar(40, self.x + 80, y, t("mj.hielo.perfecto", "¡Perfecto!"), HIELO_C, subir=0.45)
                sonido.play("perfecto", 0.8)
                self.fx.anillo(self.x, y, HIELO_C, 70, 0.5, 4)
            else:
                self.ganar(20, self.x + 80, y, t("mj.hielo.bien", "¡Hielo!"), HIELO, subir=0.3)
            sonido.play("nucleo")
            self.fx.chispas(self.x, y, HIELO_C, 22, (60, 220))
            if b["cargas"] <= 0:
                self.fx.texto(b["cx"], b["cy"] - b["h"] / 2 - 14, t("mj.hielo.agotada", "bolsa agotada"),
                              COLORES["gris"], 16, 1.0, 20)
        else:
            self.hoyos.append((self.x, arriba, self.prof, False))
            hay_abajo = any(self._dentro(bb, self.x, yy) for bb in self.bolsas if bb["cargas"] > 0
                            for yy in range(int(y), FONDO, 8))
            frase = t("mj.hielo.arriba", "Muy arriba") if hay_abajo else t("mj.hielo.nada", "Sin hielo")
            self.perder(self.x + 80, y, frase, bajar=0.3, son="fallo")
        self.hoyos = self.hoyos[-18:]
        self.estado = "subiendo"

    def animar(self, dt):
        # el vehículo se inclina con el terreno
        izq, der = self.sup(self.x - EJE), self.sup(self.x + EJE)
        meta = math.atan2(der - izq, 2 * EJE)
        self.angulo += (meta - self.angulo) * min(1.0, 14 * dt)
        if self.onda is not None:
            self.onda += 900 * dt
            ox, oy = self.onda_de
            for b in self.bolsas:
                if abs(math.hypot(b["cx"] - ox, b["cy"] - oy) - self.onda) < 40:
                    b["vis"], b["ver"] = 1.0, self.ver_radar()
            if self.onda > 1500:
                self.onda = None
        piso = self.visible_min()
        for b in self.bolsas:
            if b["ver"] > 0:                                    # recién vista por el radar: se queda
                b["ver"] -= dt
            else:
                b["vis"] = max(piso, b["vis"] - dt / 1.5)        # y después se apaga despacio
        cx, cy = ZONA.centerx, ZONA.top + 44
        for v in self.volando:
            v[2] += dt * 1.8
        llegaron = [v for v in self.volando if v[2] >= 1]
        if llegaron:
            sonido.play("album", 0.6)
            self.fx.chispas(cx + 120, cy, HIELO_C, 12, (60, 160))
        self.volando = [v for v in self.volando if v[2] < 1]

    # ── dibujo ───────────────────────────────────────────────────────────────────────
    def escena(self, lienzo):
        g = COLORES
        lienzo.blit(self.fondo, ZONA.topleft)
        # rocas
        for q in self.rocas:
            pts = [(q["x"] + x, q["y"] + y) for x, y in q["pts"]]
            pygame.draw.polygon(lienzo, (64, 60, 66), pts)
            pygame.draw.polygon(lienzo, (40, 37, 44), pts, 3)
            pygame.draw.line(lienzo, (96, 90, 98), (q["x"] - q["r"] * 0.5, q["y"] - q["r"] * 0.4),
                             (q["x"] + q["r"] * 0.1, q["y"] - q["r"] * 0.6), 3)
        # bolsas de hielo (se ven menos entre radar y radar)
        for b in self.bolsas:
            if b["cargas"] <= 0:
                k = min(1.0, b["vacia"] / 1.4)
                img = b["img"].copy()
                img.fill((120, 120, 130, int(255 * (1 - k))), special_flags=pygame.BLEND_RGBA_MULT)
                lienzo.blit(img, img.get_rect(center=(int(b["cx"]), int(b["cy"]))))
                continue
            if b["vis"] > 0.03:
                b["img"].set_alpha(int(255 * b["vis"]))
                lienzo.blit(b["img"], b["img"].get_rect(center=(int(b["cx"]), int(b["cy"]))))
                if b["vis"] > 0.6:
                    luz(lienzo, b["cx"], b["cy"], b["w"] * 0.5, (40, 90, 130), (b["vis"] - 0.6) * 1.5)
                    s = (self.t * 0.7 + b["sem"]) % 1.0           # destello que recorre la bolsa
                    luz(lienzo, b["cx"] - b["w"] * 0.4 + b["w"] * 0.8 * s, b["cy"] - b["h"] * 0.15, 16, HIELO_C,
                        b["vis"] * 0.8)
                for i in range(b["cargas"]):                       # cuántos núcleos le quedan
                    pygame.draw.circle(lienzo, mezclar((20, 30, 50), HIELO_C, b["vis"]),
                                       (int(b["cx"] - (b["cargas"] - 1) * 8 + i * 16), int(b["cy"])), 4)
        # la onda del radar
        if self.onda is not None:
            ox, oy = int(self.onda_de[0]), int(self.onda_de[1])
            pygame.draw.circle(lienzo, (90, 220, 160), (ox, oy), int(self.onda), 2)
            if self.onda > 30:
                pygame.draw.circle(lienzo, (40, 110, 80), (ox, oy), int(self.onda - 24), 1)
        # hoyos anteriores
        for x, arriba, prof, bien in self.hoyos:
            pygame.draw.line(lienzo, (34, 30, 30), (x, arriba), (x, arriba + prof), 5)
            pygame.draw.circle(lienzo, g["verde"] if bien else g["rojo"], (int(x), int(arriba) + 8), 4)
        # el taladro (siempre baja derecho)
        x, y = int(self.x), int(self.punta)
        s0 = int(self.sup(self.x))
        sacude = 3 if self.estado == "atascado" and int(self.t * 40) % 2 else 0
        if self.prof > 0:
            pygame.draw.line(lienzo, (20, 16, 18), (x, s0), (x, y), 12)
            pygame.draw.rect(lienzo, (150, 158, 178), (x - 4 + sacude, s0 - 14, 8, max(0, y - s0 - 16)))
            for k in range(0, int(self.prof), 18):                   # estrías que giran
                yy = s0 + ((k + int(self.t * 240)) % max(18, int(self.prof)))
                if yy < y - 30:
                    pygame.draw.line(lienzo, (96, 102, 122), (x - 4 + sacude, yy), (x + 4 + sacude, yy - 4), 2)
            pygame.draw.polygon(lienzo, (200, 205, 220), [(x - 11 + sacude, y - 30), (x + 11 + sacude, y - 30),
                                                         (x + sacude, y)])
            if self.carga:
                pygame.draw.rect(lienzo, HIELO_C, (x - 8, y - 4, 16, 36), border_radius=5)
                luz(lienzo, x, y + 14, 30, HIELO, 0.8)
            if self.estado == "bajando" and self.bolsa_en(self.x, self.punta):
                luz(lienzo, x, y, 46, (120, 200, 255), 0.7 + 0.3 * math.sin(self.t * 30))
                if self.nv <= 2:
                    img = texto(t("mj.hielo.ahora", "¡Soltá!"), 26, HIELO_C)
                    lienzo.blit(img, img.get_rect(midleft=(x + 26, y)))
        self._vehiculo(lienzo)
        for vx, vy, k in self.volando:                                 # núcleos que vuelan al contador
            tx, ty = ZONA.centerx + 120, ZONA.top + 44
            px = vx + (tx - vx) * k
            py = vy + (ty - vy) * k - 120 * math.sin(math.pi * k)
            pygame.draw.rect(lienzo, HIELO_C, (px - 6, py - 14, 12, 28), border_radius=4)
            luz(lienzo, px, py, 26, HIELO, 0.7)
        # contador de núcleos (arriba al centro)
        caja = pygame.Rect(0, 0, 330, 62)
        caja.midtop = (ZONA.centerx + 20, ZONA.top + 12)
        lienzo.blit(translucido(caja.w, caja.h, (6, 8, 20), 175), caja)
        lienzo.blit(texto(t("mj.hielo.contador", "Núcleos de hielo"), 8, HIELO, sombra=False, pixel_=True),
                    (caja.left + 14, caja.top + 10))
        lienzo.blit(texto(str(self.nucleos), 24, HIELO_C, pixel_=True), (caja.left + 14, caja.top + 26))
        for i in range(min(self.nucleos, 10)):
            pygame.draw.rect(lienzo, HIELO_C, (caja.left + 76 + i * 24, caja.top + 22, 14, 30), border_radius=4)
            pygame.draw.rect(lienzo, (255, 255, 255), (caja.left + 79 + i * 24, caja.top + 26, 3, 20), border_radius=2)
        if self.nv >= 3 and self.etapa == "juego":
            img = texto(t("mj.hielo.radar", "RADAR"), 8, (90, 220, 160), sombra=False, pixel_=True)
            lienzo.blit(img, (caja.right - 66, caja.top + 10))
            pygame.draw.rect(lienzo, (30, 60, 50), (caja.right - 66, caja.top + 24, 52, 6), border_radius=3)
            pygame.draw.rect(lienzo, (90, 220, 160),
                             (caja.right - 66, caja.top + 24, int(52 * (1 - self.radar / RADAR_CADA)), 6), border_radius=3)
        img = texto(t("mj.hielo.nota", "En los cráteres que nunca ven el sol hay hielo de agua: la NASA lo confirmó "
                                      "con la misión LCROSS en 2009."), 17, (210, 205, 215), False)
        lienzo.blit(img, (ZONA.left + 20, ZONA.bottom - 30))

    def _vehiculo(self, lienzo):
        """El vehículo, inclinado según el suelo debajo de sus ruedas."""
        x = self.x
        izq, der = self.sup(x - EJE), self.sup(x + EJE)
        piso = (izq + der) / 2                       # el suelo bajo el centro del eje
        a = self.angulo
        ca, sa = math.cos(a), math.sin(a)

        def pos(dx, dy):                             # de «coordenadas del vehículo» al lienzo
            return x + dx * ca - dy * sa, piso + dx * sa + dy * ca

        luz(lienzo, *pos(40, -8), 70, (120, 110, 70), 0.6)                    # luz del foco en el suelo
        s = pygame.Surface((200, 200), pygame.SRCALPHA)
        P = 100                                      # el centro de la superficie = el piso bajo el eje
        y0 = P - 30
        pygame.draw.polygon(s, (90, 96, 120), [(P - 50, y0 - 4), (P + 50, y0 - 4), (P + 44, y0 + 18), (P - 44, y0 + 18)])
        pygame.draw.rect(s, (210, 214, 226), (P - 46, y0 - 14, 92, 14), border_radius=5)
        pygame.draw.line(s, (60, 120, 200), (P - 40, y0 - 22), (P + 10, y0 - 34), 6)     # panel solar
        pygame.draw.line(s, (160, 170, 190), (P - 14, y0 - 14), (P - 14, y0 - 28), 2)
        pygame.draw.line(s, (180, 186, 204), (P + 30, y0 - 14), (P + 30, y0 - 44), 2)    # antena
        pygame.draw.circle(s, COLORES["rojo"] if int(self.t * 2) % 2 else (120, 40, 40), (P + 30, y0 - 46), 3)
        pygame.draw.rect(s, (230, 190, 60), (P - 9, y0 - 58, 18, 62), border_radius=3)   # torre del taladro
        pygame.draw.rect(s, (150, 120, 30), (P - 9, y0 - 58, 18, 62), 2, border_radius=3)
        pygame.draw.circle(s, (255, 240, 180), (P + 46, y0 + 4), 5)
        for dx in (-EJE, EJE):
            c = (P + dx, P - 11)
            pygame.draw.circle(s, (40, 42, 52), c, 12)
            pygame.draw.circle(s, (120, 126, 146), c, 12, 3)
            for k in range(3):
                r = self.rueda + k * math.pi / 3
                pygame.draw.line(s, (120, 126, 146), (c[0] - math.cos(r) * 9, c[1] - math.sin(r) * 9),
                                 (c[0] + math.cos(r) * 9, c[1] + math.sin(r) * 9), 2)
        if abs(a) > 0.004:
            s = pygame.transform.rotozoom(s, -math.degrees(a), 1.0)
        lienzo.blit(s, s.get_rect(center=(int(x), int(piso))))
        luz(lienzo, *pos(46, -26), 26, (255, 230, 150), 0.9)
