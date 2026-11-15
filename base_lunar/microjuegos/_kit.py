# -*- coding: utf-8 -*-
"""Kit de los microjuegos largos (oxígeno, hielo, recreo y estiba): lo que tienen todos en común.

    from ._kit import Partida

    class MiJuego(Partida):
        tarea = "..."
        duracion = 35.0               # segundos de juego (más la cuenta regresiva y la tarjeta final)
        META = 900                    # puntos para llegar al rendimiento máximo
        def preparar(self): ...       # en vez de iniciar()
        def jugar(self, dt): ...      # la lógica; solo corre mientras se juega (aquí llegan los clics)
        def animar(self, dt): ...     # lo que se mueve siempre (también en la cuenta y al final)
        def escena(self, lienzo): ... # el dibujo del juego

Lo que el kit da hecho:
  · cuenta regresiva 3-2-1-¡YA! con la instrucción grande, y tarjeta final con puntos y 1 a 3 estrellas;
  · NIVEL que se adapta a quien juega: sube con los aciertos y baja con los errores (de 1 a 8). Así un
    niño de 7 años y un adulto juegan cada uno a su medida, y el adulto llega a niveles más difíciles;
  · puntos con COMBO (aciertos seguidos multiplican ×2, ×3…) y una nota musical que sube con cada uno;
  · efectos: chispas con brillo, anillos, textos que flotan, sacudidas, destellos y carteles.
Los microjuegos que heredan directo de `Microjuego` (los del equipo) siguen funcionando igual.
"""
import math

import pygame

from .base import Microjuego, ZONA, COLORES
from ..textos import t, n
from .. import sonido

BLANCO = (255, 255, 255)

# ── dibujitos que se guardan para no rehacerlos cada cuadro ──────────────────────────────────────
_CACHE = {}


def guardado(clave, hacer):
    s = _CACHE.get(clave)
    if s is None:
        if len(_CACHE) > 900:
            _CACHE.clear()
        s = _CACHE[clave] = hacer()
    return s


def brillo(radio, color):
    """Un círculo de luz (negro afuera) para SUMAR encima con BLEND_ADD."""
    r = max(2, int(radio))
    color = tuple(int(max(0, min(255, c))) for c in color)

    def hacer():
        s = pygame.Surface((2 * r, 2 * r))
        s.fill((0, 0, 0))
        for i in range(r, 0, -1):
            k = (1 - i / r) ** 1.8
            pygame.draw.circle(s, tuple(int(c * k) for c in color), (r, r), i)
        return s
    return guardado(("brillo", r, color), hacer)


def luz(lienzo, x, y, radio, color, fuerza=1.0):
    """Suma un brillo redondo en (x, y). fuerza de 0 a 1 (se redondea para no llenar la memoria)."""
    f = round(max(0.0, min(1.0, fuerza)) * 8) / 8
    if f <= 0 or radio < 2:
        return
    s = brillo(int(radio / 2) * 2, tuple(c * f for c in color))
    lienzo.blit(s, (int(x) - s.get_width() // 2, int(y) - s.get_height() // 2), special_flags=pygame.BLEND_ADD)


def degradado(w, h, arriba, abajo):
    def hacer():
        s = pygame.Surface((w, h))
        for y in range(h):
            k = y / max(1, h - 1)
            pygame.draw.line(s, tuple(int(a + (b - a) * k) for a, b in zip(arriba, abajo)), (0, y), (w, y))
        return s
    return guardado(("grad", w, h, tuple(arriba), tuple(abajo)), hacer)


def translucido(w, h, color, alfa, radio=12):
    def hacer():
        s = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(s, (*color, alfa), (0, 0, w, h), border_radius=radio)
        return s
    return guardado(("transl", w, h, tuple(color), alfa, radio), hacer)


def vineta(color, w=ZONA.w, h=ZONA.h):
    """Bordes oscurecidos (o de color) que se desvanecen hacia el centro."""
    def hacer():
        s = pygame.Surface((w, h), pygame.SRCALPHA)
        pasos = 28
        for i in range(pasos):
            k = i / pasos
            a = int(200 * (1 - k) ** 2.2)
            r = pygame.Rect(0, 0, int(w * (1.5 - 0.7 * k)), int(h * (1.5 - 0.7 * k)))
            r.center = (w // 2, h // 2)
            pygame.draw.ellipse(s, (*color, a), r)
        return s
    return guardado(("vineta", tuple(color), w, h), hacer)


def esquinas(radio=16):
    """Tapa las esquinas de la zona de juego para que se vea redondeada."""
    def hacer():
        s = pygame.Surface(ZONA.size, pygame.SRCALPHA)
        s.fill((*COLORES["fondo"], 255))
        pygame.draw.rect(s, (0, 0, 0, 0), (0, 0, *ZONA.size), border_radius=radio)
        pygame.draw.rect(s, (*COLORES["borde"], 255), (0, 0, *ZONA.size), 2, border_radius=radio)
        return s
    return guardado(("esquinas", radio), hacer)


def texto(s, tam, color, negrita=True, sombra=True, pixel_=False):
    """Un texto ya dibujado (con sombra), guardado para no rehacerlo."""
    def hacer():
        from ..texto_mate import fuente, fuente_pixel, pixel
        f = fuente_pixel(tam) if pixel_ else fuente(tam, negrita)
        txt = pixel(s) if pixel_ else s
        img = f.render(txt, not pixel_, color)
        if not sombra:
            return img
        out = pygame.Surface((img.get_width() + 3, img.get_height() + 3), pygame.SRCALPHA)
        sh = f.render(txt, not pixel_, (6, 8, 18))
        out.blit(sh, (3, 3))
        out.blit(img, (0, 0))
        return out
    return guardado(("txt", s, tam, tuple(color), negrita, sombra, pixel_), hacer)


def estrella(lienzo, cx, cy, r, color, borde=None, ancho=0):
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    pygame.draw.polygon(lienzo, color, pts, ancho)
    if borde:
        pygame.draw.polygon(lienzo, borde, pts, 2)


def mezclar(a, b, k):
    k = max(0.0, min(1.0, k))
    return tuple(int(x + (y - x) * k) for x, y in zip(a, b))


# ── efectos ──────────────────────────────────────────────────────────────────────────────────────
class Efectos:
    def __init__(self, rng):
        self.rng = rng
        self.parts = []      # [x, y, vx, vy, vida, vida0, color, tam, grav, roce, con_brillo]
        self.textos = []     # [img, x, y, vida, vida0, sube]
        self.anillos = []    # [x, y, color, r0, r1, vida, vida0, ancho]
        self.carteles = []   # [img, vida, vida0, y]
        self.sac, self.sac0, self.fuerza = 0.0, 1.0, 0.0
        self.flash = None    # [color, vida, vida0]

    def chispas(self, x, y, color, cuantas=16, vel=(80, 280), vida=(0.35, 0.75), grav=0.0, tam=(2, 5),
                con_brillo=True, angulo=None, abre=math.pi, roce=1.5):
        for _ in range(cuantas):
            if angulo is None:
                a = self.rng.uniform(0, 2 * math.pi)
            else:
                a = angulo + self.rng.uniform(-abre, abre)
            v = self.rng.uniform(*vel)
            vi = self.rng.uniform(*vida)
            self.parts.append([x, y, math.cos(a) * v, math.sin(a) * v, vi, vi, color,
                               self.rng.uniform(*tam), grav, roce, con_brillo])

    def anillo(self, x, y, color, r1=70, vida=0.45, ancho=4, r0=8):
        self.anillos.append([x, y, color, r0, r1, vida, vida, ancho])

    def texto(self, x, y, s, color, tam=26, vida=0.95, sube=55):
        self.textos.append([texto(s, tam, color), x, y, vida, vida, sube])

    def cartel(self, s, color, tam=48, vida=1.4, y=None):
        self.carteles.append([texto(s, tam, color, pixel_=True), vida, vida, y or ZONA.centery])

    def sacudir(self, fuerza=6, tiempo=0.25):
        if fuerza >= self.fuerza * (self.sac / max(0.01, self.sac0)):
            self.fuerza, self.sac, self.sac0 = fuerza, tiempo, tiempo

    def destello(self, color, tiempo=0.25):
        self.flash = [color, tiempo, tiempo]

    def desplazamiento(self):
        if self.sac <= 0:
            return 0, 0
        f = self.fuerza * self.sac / self.sac0
        return int(self.rng.uniform(-f, f)), int(self.rng.uniform(-f, f))

    def actualizar(self, dt):
        vivas = []
        for p in self.parts:
            p[4] -= dt
            if p[4] > 0:
                p[0] += p[2] * dt
                p[1] += p[3] * dt
                p[3] += p[8] * dt
                k = max(0.0, 1 - p[9] * dt)
                p[2] *= k
                p[3] *= k
                vivas.append(p)
        self.parts = vivas[-500:]
        self.textos = [x for x in self.textos if self._baja(x, 3, dt)]
        self.anillos = [x for x in self.anillos if self._baja(x, 5, dt)]
        self.carteles = [x for x in self.carteles if self._baja(x, 1, dt)]
        self.sac = max(0.0, self.sac - dt)
        if self.flash:
            self.flash[1] -= dt
            if self.flash[1] <= 0:
                self.flash = None

    @staticmethod
    def _baja(x, i, dt):
        x[i] -= dt
        return x[i] > 0

    def dibujar(self, lienzo):
        for x, y, c, r0, r1, vida, vida0, ancho in self.anillos:
            k = 1 - vida / vida0
            r = r0 + (r1 - r0) * (1 - (1 - k) ** 2)
            col = mezclar(c, (0, 0, 0), k * 0.9)
            pygame.draw.circle(lienzo, col, (int(x), int(y)), int(r), max(1, int(ancho * (1 - k) + 1)))
        for x, y, vx, vy, vida, vida0, c, tam, _g, _r, cb in self.parts:
            k = vida / vida0
            if cb:
                luz(lienzo, x, y, tam * 5 * (0.5 + 0.5 * k), c, k)
                pygame.draw.circle(lienzo, mezclar(c, BLANCO, 0.5 * k), (int(x), int(y)), max(1, int(tam * k)))
            else:
                pygame.draw.circle(lienzo, mezclar(c, (20, 22, 34), 1 - k), (int(x), int(y)),
                                   max(1, int(tam * (0.6 + 0.4 * k))))
        for img, x, y, vida, vida0, sube in self.textos:
            k = 1 - vida / vida0
            yy = y - sube * (1 - (1 - k) ** 2)
            if k < 0.15:                                    # «pop» al aparecer
                esc = 0.6 + 0.6 * (k / 0.15)
                img = pygame.transform.smoothscale_by(img, esc)
            elif k < 0.25:
                esc = 1.2 - 0.2 * ((k - 0.15) / 0.1)
                img = pygame.transform.smoothscale_by(img, esc)
            if vida < 0.3:
                img = img.copy()
                img.set_alpha(int(255 * vida / 0.3))
            lienzo.blit(img, img.get_rect(center=(int(x), int(yy))))
        if self.flash:
            c, vida, vida0 = self.flash
            k = vida / vida0
            lienzo.fill(tuple(int(v * k) for v in c), ZONA, special_flags=pygame.BLEND_ADD)

    def dibujar_carteles(self, lienzo):
        for img, vida, vida0, y in self.carteles:
            k = 1 - vida / vida0
            if k < 0.12:
                img = pygame.transform.smoothscale_by(img, 0.5 + 0.7 * k / 0.12)
            elif k < 0.2:
                img = pygame.transform.smoothscale_by(img, 1.2 - 0.2 * (k - 0.12) / 0.08)
            if vida < 0.35:
                img = img.copy()
                img.set_alpha(int(255 * vida / 0.35))
            r = img.get_rect(center=(ZONA.centerx, int(y)))
            fondo = translucido(min(ZONA.w - 40, r.w + 80), r.h + 30, (6, 8, 20), 150, 16)
            if vida >= 0.35:
                lienzo.blit(fondo, fondo.get_rect(center=r.center))
            lienzo.blit(img, r)


# ── la partida ───────────────────────────────────────────────────────────────────────────────────
class Partida(Microjuego):
    duracion = 35.0
    INTRO = 2.7               # cuenta regresiva (la instrucción se lee mientras tanto)
    OUTRO = 3.4               # tarjeta final (un clic la cierra antes)
    NIVEL_MAX = 8
    DOBLES = 8.0              # los últimos segundos dan puntos dobles
    META = 1000              # puntos para el rendimiento máximo (cada juego pone el suyo)
    CURVA = 1.0               # < 1: los primeros puntos rinden más (ayuda a los más chicos)
    ESTRELLAS = (0.7, 0.95, 1.2)
    COLOR = COLORES["oro"]
    consejos = ()             # 1 a 3 líneas cortas para la tarjeta del inicio
    Y_CARTEL = ZONA.top + 150  # altura de los carteles («¡NIVEL 3!»), para no tapar lo importante

    # ── lo que cambia cada juego ──────────────────────────────────────────────────────
    def preparar(self):
        pass

    def jugar(self, dt):
        pass

    def animar(self, dt):
        pass

    def escena(self, lienzo):
        pass

    def al_final(self):
        pass

    # ── arranque ─────────────────────────────────────────────────────────────────────
    def iniciar(self):
        self.tj = 0.0
        self.tf = 0.0
        self.etapa = "intro"
        self.puntos = 0
        self.mostrados = 0.0
        self.combo = 0
        self.mejor_combo = 0
        self.nivel = 1.0
        self.nivel_tope = 1
        self.aciertos = 0
        self.fallos = 0
        self.errados = 0
        self.eventos = []
        self.dt = 1 / 60
        self._cuenta = 0
        self._dings = 0
        self._vol = {}
        self._dobles_avisado = False
        self.fx = Efectos(self.rng)
        self.preparar()

    def restante(self):
        return max(0.0, self.duracion - self.tj)

    def terminado(self):
        return self._fin or self.t >= self.INTRO + self.duracion + self.OUTRO

    def terminar(self):
        sonido.parar_bucles()
        self._fin = True

    def jugando(self):
        return self.etapa == "juego"

    # ── niveles, puntos y combo ──────────────────────────────────────────────────────
    @property
    def nv(self):
        """El nivel entero (1 a 8)."""
        return int(self.nivel)

    def multiplicador(self):
        return 1 + min(4, self.combo // 4)

    def bono_nivel(self):
        return 1 + 0.15 * (self.nv - 1)

    def subir(self, k=0.2):
        self.nivel = min(self.NIVEL_MAX + 0.999, self.nivel + k)
        if self.nv > self.nivel_tope:
            self.nivel_tope = self.nv
            self.fx.cartel(t("kit.nivel", "¡NIVEL {n}!", n=self.nv), COLORES["cian"], 40, 1.2, self.Y_CARTEL)
            sonido.play("nivel", 0.8)

    def dobles(self):
        """Los últimos segundos valen doble (un cierre emocionante para todos)."""
        return self.etapa == "juego" and self.restante() <= self.DOBLES

    def bajar(self, k=0.5):
        self.nivel = max(1.0, self.nivel - k)

    def ganar(self, base, x, y, texto_=None, color=None, subir=0.2, combo=True, nota=True):
        """Un acierto: suma puntos (con combo y nivel), muestra «+n» y toca la nota que sigue."""
        antes = self.multiplicador()
        if combo:
            self.combo += 1
            self.mejor_combo = max(self.mejor_combo, self.combo)
        mult = self.multiplicador() if combo else 1
        p = max(1, int(round(base * mult * self.bono_nivel())))
        if self.dobles():
            p *= 2
        self.puntos += p
        self.aciertos += 1
        self.subir(subir)
        color = color or COLORES["oro"]
        if texto_:
            self.fx.texto(x, y - 30, texto_, color, 26)
        self.fx.texto(x, y, f"+{p}" + (f"  x{mult}" if mult > 1 else ""), mezclar(color, BLANCO, 0.35), 22)
        if nota:
            sonido.nota(self.combo - 1 if combo else 0, 0.9)
        if combo and self.multiplicador() > antes:
            sonido.play("combo", 0.8)
        return p

    def perder(self, x=None, y=None, texto_=None, castigo=0, bajar=0.6, son="mal"):
        """Un error de verdad: corta el combo, baja el nivel y puede restar puntos."""
        self.combo = 0
        self.fallos += 1
        self.bajar(bajar)
        quita = min(self.puntos, castigo)
        self.puntos -= quita
        if x is not None:
            if texto_:
                self.fx.texto(x, y - 26, texto_, COLORES["rojo"], 24)
            if quita:
                self.fx.texto(x, y + 4, f"−{quita}", COLORES["rojo"], 20)
        if son:
            sonido.play(son, 0.8)

    def errar(self, x, y):
        """Un clic que no le dio a nada: corta el combo (así hacer clic al azar no conviene)."""
        self.errados += 1
        if self.combo >= 4:
            self.fx.texto(x, y - 20, t("kit.combo_perdido", "combo perdido"), COLORES["gris"], 18, 0.7, 30)
        self.combo = 0
        self.bajar(0.12)
        self.fx.anillo(x, y, (110, 116, 140), 22, 0.25, 2)
        sonido.play("fallo", 0.7)

    def bucle(self, nombre, objetivo, rapidez=6.0):
        """Un sonido que se repite, con el volumen suavizado (sin saltos bruscos)."""
        v = self._vol.get(nombre, 0.0)
        v += (objetivo - v) * min(1.0, rapidez * self.dt)
        self._vol[nombre] = v
        sonido.bucle(nombre, v if self.etapa != "final" else 0.0)

    def rendimiento(self):
        frac = math.log1p(max(0, self.puntos) / self.ESCALA) / math.log1p(self.META / self.ESCALA)
        return max(0.4, min(1.3, 0.4 + 0.9 * min(1.0, frac)))

    def estrellas_ganadas(self):
        r = self.rendimiento()
        return sum(1 for e in self.ESTRELLAS if r >= e - 1e-9)

    # ── el bucle ─────────────────────────────────────────────────────────────────────
    def actualizar(self, eventos, dt):
        self.dt = dt
        self.eventos = eventos
        if self.etapa == "intro":
            self.clics = []
            marcas = (0.6, 1.3, 2.0)
            while self._cuenta < 3 and self.t >= marcas[self._cuenta]:
                self._cuenta += 1
                sonido.play("cuenta")
            if self.t >= self.INTRO:
                self.etapa = "juego"
                sonido.play("ya")
                self.fx.cartel(t("kit.ya", "¡YA!"), COLORES["verde"], 56, 0.7)
        elif self.etapa == "juego":
            self.tj += dt
            if not self._dobles_avisado and self.dobles():
                self._dobles_avisado = True
                self.fx.cartel(t("kit.dobles", "¡Puntos dobles hasta el final!"), COLORES["naranja"], 24, 1.6,
                               self.Y_CARTEL)
                sonido.play("nivel")
            self.jugar(dt)
            if self.tj >= self.duracion:
                self.tj = self.duracion
                self.etapa = "final"
                sonido.parar_bucles()
                sonido.play("tiempo")
                self.al_final()
        else:
            self.tf += dt
            self.clics_final = self.clics
            self.clics = []
            gan = self.estrellas_ganadas()
            while self._dings < 3 and self.tf >= 1.1 + 0.3 * self._dings:
                self._dings += 1
                sonido.play(f"estrella{self._dings}" if self._dings <= gan else "estrella0")
            if self.clics_final and self.tf > 1.0:
                self.terminar()
        self.mostrados += (self.puntos - self.mostrados) * min(1.0, 10 * dt)
        if abs(self.puntos - self.mostrados) < 0.5:
            self.mostrados = float(self.puntos)
        self.animar(dt)
        self.fx.actualizar(dt)

    # ── dibujo ───────────────────────────────────────────────────────────────────────
    def dibujar(self, lienzo):
        lienzo.set_clip(ZONA)
        self.escena(lienzo)
        self.fx.dibujar(lienzo)
        dx, dy = self.fx.desplazamiento()
        if dx or dy:
            lienzo.scroll(dx, dy)
        lienzo.set_clip(None)
        lienzo.blit(esquinas(), ZONA.topleft)
        self._hud(lienzo)
        if self.etapa == "intro":
            self._intro(lienzo)
        elif self.etapa == "final":
            self._final(lienzo)
        self.fx.dibujar_carteles(lienzo)

    def _hud(self, lienzo):
        g = COLORES
        x0, y0 = ZONA.left + 14, ZONA.top + 12
        lienzo.blit(translucido(300, 62, (6, 8, 20), 175), (x0, y0))
        lienzo.blit(texto(t("kit.puntos", "PUNTOS"), 8, g["gris"], sombra=False, pixel_=True), (x0 + 14, y0 + 10))
        lienzo.blit(texto(n(int(round(self.mostrados)), 0), 24, g["oro"], pixel_=True), (x0 + 14, y0 + 26))
        m = self.multiplicador()
        if m > 1 and self.etapa == "juego":
            col = (g["amarillo"], g["naranja"], (255, 110, 70), (255, 80, 160))[min(3, m - 2)]
            pulso = 0.6 + 0.4 * math.sin(self.t * 10)
            luz(lienzo, x0 + 256, y0 + 31, 40, col, 0.5 * pulso)
            lienzo.blit(texto(f"x{m}", 24, col, pixel_=True), (x0 + 228, y0 + 26))
            lienzo.blit(texto(t("kit.combo", "COMBO"), 8, col, sombra=False, pixel_=True), (x0 + 228, y0 + 10))
        # nivel, arriba a la derecha
        w = 206
        x1 = ZONA.right - 14 - w
        lienzo.blit(translucido(w, 62, (6, 8, 20), 175), (x1, y0))
        lienzo.blit(texto(t("kit.nivel_hud", "NIVEL {n}", n=self.nv), 16, g["cian"], pixel_=True), (x1 + 14, y0 + 10))
        for i in range(self.NIVEL_MAX):
            r = pygame.Rect(x1 + 14 + i * 23, y0 + 38, 18, 12)
            pygame.draw.rect(lienzo, (34, 40, 66), r, border_radius=3)
            if i < self.nv:
                pygame.draw.rect(lienzo, g["cian"], r, border_radius=3)
            elif i == self.nv:                       # lo que falta para el próximo nivel
                lleno = self.nivel - self.nv
                if lleno > 0.05:
                    pygame.draw.rect(lienzo, (60, 120, 150), (r.x, r.y, int(r.w * lleno), r.h), border_radius=3)

    def _oscurecer(self, lienzo, k):
        v = int(255 - 150 * k)
        lienzo.fill((v, v, min(255, v + 10)), ZONA, special_flags=pygame.BLEND_MULT)

    def _intro(self, lienzo):
        g = COLORES
        self._oscurecer(lienzo, 1.0)
        caja = pygame.Rect(0, 0, 900, 300)
        caja.center = (ZONA.centerx, ZONA.centery - 10)
        lienzo.blit(translucido(caja.w, caja.h, (12, 16, 36), 235, 22), caja)
        pygame.draw.rect(lienzo, self.COLOR, caja, 3, border_radius=22)
        img = texto(self.titulo, 24, self.COLOR, pixel_=True)
        lienzo.blit(img, img.get_rect(midtop=(caja.centerx, caja.top + 26)))
        from ..texto_mate import componer
        img = componer(self.instruccion, 28, g["texto"], caja.w - 80, True, "centro")
        lienzo.blit(img, img.get_rect(midtop=(caja.centerx, caja.top + 70)))
        y = caja.top + 82 + img.get_height() + 14
        for c in self.consejos:
            im = componer("• " + c, 21, g["gris"], caja.w - 120, False, "centro")
            lienzo.blit(im, im.get_rect(midtop=(caja.centerx, y)))
            y += im.get_height() + 4
        if self._cuenta:
            k = (self.t - (0.6, 1.3, 2.0)[self._cuenta - 1]) / 0.7
            esc = 1.5 - 0.5 * min(1.0, k * 3)
            img = texto(str(4 - self._cuenta), 72, g["oro"], pixel_=True)
            img = pygame.transform.smoothscale_by(img, esc)
            centro = (caja.centerx, caja.bottom + 70)
            luz(lienzo, *centro, 90, g["oro"], 0.35 * (1 - min(1, k)))
            lienzo.blit(img, img.get_rect(center=centro))

    def _final(self, lienzo):
        g = COLORES
        k = min(1.0, self.tf / 0.6)
        self._oscurecer(lienzo, k)
        if self.tf < 0.9:
            img = texto(t("kit.tiempo", "¡TIEMPO!"), 56, g["oro"], pixel_=True)
            lienzo.blit(img, img.get_rect(center=(ZONA.centerx, ZONA.centery - 150 * max(0, (self.tf - 0.6) / 0.3))))
            return
        caja = pygame.Rect(0, 0, 640, 330)
        caja.center = ZONA.center
        lienzo.blit(translucido(caja.w, caja.h, (12, 16, 36), 240, 22), caja)
        pygame.draw.rect(lienzo, self.COLOR, caja, 3, border_radius=22)
        img = texto(t("kit.tiempo", "¡TIEMPO!"), 24, g["oro"], pixel_=True)
        lienzo.blit(img, img.get_rect(midtop=(caja.centerx, caja.top + 22)))
        img = texto(n(self.puntos, 0) + " " + t("kit.pts", "puntos"), 40, g["texto"])
        lienzo.blit(img, img.get_rect(midtop=(caja.centerx, caja.top + 62)))
        gan = self.estrellas_ganadas()
        for i in range(3):
            cx, cy = caja.centerx + (i - 1) * 96, caja.top + 168
            if i < self._dings:
                aparece = min(1.0, (self.tf - 1.1 - 0.3 * i) / 0.2)
                if i < gan:
                    luz(lienzo, cx, cy, 80, g["oro"], 0.5)
                    estrella(lienzo, cx, cy, 34 * (0.6 + 0.4 * aparece), g["oro"], (255, 245, 200))
                else:
                    estrella(lienzo, cx, cy, 34, (44, 50, 78), (80, 88, 120))
            else:
                estrella(lienzo, cx, cy, 34, (30, 34, 56))
        lineas = [t("kit.rinde", "La tarea rinde el {p} %", p=n(self.rendimiento() * 100, 0))]
        if self.mejor_combo >= 4:
            lineas.append(t("kit.mejor_combo", "Mejor racha: {n} seguidos · nivel {v}", n=self.mejor_combo,
                            v=self.nivel_tope))
        else:
            lineas.append(t("kit.nivel_max", "Llegaste al nivel {v}", v=self.nivel_tope))
        for j, s in enumerate(lineas):
            img = texto(s, 24 if j == 0 else 19, g["cian"] if j == 0 else g["gris"], negrita=j == 0)
            lienzo.blit(img, img.get_rect(midtop=(caja.centerx, caja.top + 222 + j * 34)))
        if self.tf > 1.0:
            img = texto(t("kit.seguir", "clic para seguir"), 16, (120, 128, 150), negrita=False, sombra=False)
            lienzo.blit(img, img.get_rect(midbottom=(caja.centerx, caja.bottom - 10)))
