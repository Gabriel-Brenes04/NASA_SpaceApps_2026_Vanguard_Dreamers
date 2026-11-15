# -*- coding: utf-8 -*-
"""La clase base de todos los microjuegos. Cada microjuego hereda de `Microjuego`.

Lo que TIENE que poner cada microjuego (ver _plantilla.py):
    titulo       lo que se lee arriba                       "Huerto"
    instruccion  qué hacer, en una línea                    "Arrastrá el agua a las macetas secas"
    tarea        qué tarea del día reemplaza                "cosecha", "oxigeno", "regolito",
                                                            "hielo", "recreo" o "estiba"
    duracion     segundos que dura (5 a 45)                 8
    iniciar()    arma el juego (en vez de __init__)
    actualizar(eventos, dt)   mueve el juego; dt = segundos desde el cuadro anterior
    dibujar(lienzo)           dibuja en un lienzo de 1280 × 720 (el marco lo pone la base)
    rendimiento()             qué tan bien salió: 0,4 (muy mal) a 1,3 (perfecto)

Lo que la base YA da hecho:
    self.base     el estado de la base lunar (solo LEER: oxígeno, agua, día, etc.)
    self.rng      números al azar (usar este, no `random`, para poder repetir partidas)
    self.raton    (x, y) del ratón en el lienzo        self.apretado  True mientras se aprieta
    self.t        segundos que lleva el juego          self.restante() segundos que faltan
    self.clics    lista de los clics de ESTE cuadro, ya en coordenadas del lienzo
    self.terminar()   para acabar antes de tiempo (si ya se ganó)
El juego se acaba solo al cumplirse `duracion`.
"""
import pygame

ANCHO, ALTO = 1280, 720
ZONA = pygame.Rect(40, 110, 1200, 570)        # donde se juega (debajo del título y el reloj)

COLORES = {
    "fondo": (8, 11, 26), "panel": (20, 26, 50), "borde": (64, 84, 136), "oro": (232, 186, 60),
    "texto": (236, 239, 246), "gris": (150, 158, 178), "cian": (90, 205, 255), "azul": (96, 150, 255),
    "verde": (80, 214, 120), "rojo": (236, 84, 84), "naranja": (245, 160, 52), "amarillo": (250, 220, 70),
}


class Microjuego:
    titulo = "Microjuego"
    instruccion = "Instrucción en una línea"
    tarea = None
    duracion = 8.0

    def __init__(self, base=None, rng=None):
        import random
        self.base = base
        self.rng = rng or random.Random()
        self.t = 0.0
        self.raton = (0, 0)
        self.apretado = False
        self.clics = []
        self._fin = False
        self.iniciar()

    # ── lo que cada microjuego cambia ────────────────────────────────────────────────
    def iniciar(self):
        pass

    def actualizar(self, eventos, dt):
        pass

    def dibujar(self, lienzo):
        pass

    def rendimiento(self):
        return 1.0

    # ── lo que ya viene hecho ────────────────────────────────────────────────────────
    def restante(self):
        return max(0.0, self.duracion - self.t)

    def terminar(self):
        self._fin = True

    def terminado(self):
        return self._fin or self.t >= self.duracion

    def paso(self, eventos, dt, raton, apretado):
        """Lo llama el juego cada cuadro. NO hace falta tocarlo."""
        if self.terminado():
            return True
        self.raton, self.apretado = raton, apretado
        self.clics = [ev.pos for ev in eventos if ev.type == pygame.MOUSEBUTTONDOWN and getattr(ev, "button", 1) == 1]
        self.t += dt
        self.actualizar(eventos, dt)
        return self.terminado()

    def rendimiento_seguro(self):
        """El rendimiento, siempre entre 0,4 y 1,3 aunque el microjuego se equivoque."""
        try:
            r = float(self.rendimiento())
        except Exception:
            r = 1.0
        return max(0.4, min(1.3, r))

    def dibujar_todo(self, lienzo, fuente):
        """Fondo + el microjuego + el marco (título, instrucción y reloj). NO hace falta tocarlo."""
        lienzo.fill(COLORES["fondo"])
        self.dibujar(lienzo)
        pygame.draw.rect(lienzo, COLORES["panel"], (0, 0, ANCHO, 96))
        pygame.draw.line(lienzo, COLORES["borde"], (0, 96), (ANCHO, 96), 2)
        from ..assets.texto_mate import fuente_pixel, pixel
        img = fuente_pixel(24).render(pixel(self.titulo), False, COLORES["oro"])
        lienzo.blit(img, (40, 18))
        img = fuente(20, False).render(self.instruccion, True, COLORES["texto"])
        lienzo.blit(img, (40, 56))
        frac = self.restante() / self.duracion if self.duracion else 0
        barra = pygame.Rect(ANCHO - 400, 30, 260, 18)
        pygame.draw.rect(lienzo, (36, 42, 72), barra, border_radius=9)
        col = COLORES["verde"] if frac > 0.4 else COLORES["naranja"] if frac > 0.2 else COLORES["rojo"]
        if frac > 0:
            pygame.draw.rect(lienzo, col, (barra.x, barra.y, int(barra.w * frac), barra.h), border_radius=9)
<<<<<<< HEAD:base_lunar/microjuegos/base.py
        from ..textos import n
=======
        from ..assets.textos import n
>>>>>>> datos:game/minijuegos/base.py
        img = fuente_pixel(16).render(f"{n(self.restante(), 1)} s", False, COLORES["texto"])
        lienzo.blit(img, (barra.right + 10, barra.y + 1))
