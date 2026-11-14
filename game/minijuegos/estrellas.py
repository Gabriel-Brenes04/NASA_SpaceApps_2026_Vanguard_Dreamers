# -*- coding: utf-8 -*-
"""EJEMPLO completo de microjuego: «Estrellas fugaces» (tarea: recreo → ánimo).

La tripulación descansa mirando por la ventana. Hay que hacer clic en las estrellas fugaces antes de
que salgan de la pantalla. Sirve de modelo para los microjuegos del equipo: es corto a propósito.
"""
import math

import pygame

from .base import Microjuego, ZONA, COLORES


class Estrellas(Microjuego):
    titulo = "Recreo: estrellas fugaces"
    instruccion = "Hacé clic en las estrellas fugaces antes de que se escapen"
    tarea = "recreo"
    duracion = 8.0
    META = 8                      # con 8 atrapadas se llega al rendimiento máximo

    def iniciar(self):
        self.atrapadas = 0
        self.falladas = 0
        self.estrellas = []
        self.proxima = 0.3        # segundos para que salga la siguiente
        self.fondo = [(self.rng.randint(ZONA.left, ZONA.right), self.rng.randint(ZONA.top, ZONA.bottom),
                       self.rng.randint(60, 200)) for _ in range(140)]
        self.chispas = []

    def actualizar(self, eventos, dt):
        self.proxima -= dt
        if self.proxima <= 0:
            self.proxima = self.rng.uniform(0.35, 0.65)
            y = self.rng.randint(ZONA.top + 40, ZONA.bottom - 140)
            self.estrellas.append({"x": float(ZONA.left - 20), "y": float(y),
                                   "vx": self.rng.uniform(380, 560), "vy": self.rng.uniform(40, 130)})
        for e in self.estrellas:
            e["x"] += e["vx"] * dt
            e["y"] += e["vy"] * dt
        for x, y in self.clics:
            for e in self.estrellas:
                if math.hypot(e["x"] - x, e["y"] - y) < 34:
                    self.atrapadas += 1
                    self.chispas.append([e["x"], e["y"], 0.4])
                    e["x"] = 10_000          # se va de la pantalla
                    break
        quedan = []
        for e in self.estrellas:
            if e["x"] > ZONA.right + 20:
                if e["x"] < 9_000:
                    self.falladas += 1
            else:
                quedan.append(e)
        self.estrellas = quedan
        for c in self.chispas:
            c[2] -= dt
        self.chispas = [c for c in self.chispas if c[2] > 0]

    def dibujar(self, lienzo):
        pygame.draw.rect(lienzo, (3, 4, 14), ZONA, border_radius=16)
        for x, y, b in self.fondo:
            lienzo.set_at((x, y), (b, b, min(255, b + 30)))
        # marco de la ventana del hábitat
        pygame.draw.rect(lienzo, (150, 158, 178), ZONA, 6, border_radius=16)
        lienzo.set_clip(ZONA.inflate(-12, -12))       # que nada se salga de la ventana
        for e in self.estrellas:
            largo = 70
            nx, ny = e["vx"], e["vy"]
            m = math.hypot(nx, ny) or 1
            cola = (e["x"] - nx / m * largo, e["y"] - ny / m * largo)
            pygame.draw.line(lienzo, (120, 140, 220), cola, (e["x"], e["y"]), 3)
            pygame.draw.circle(lienzo, (255, 245, 200), (int(e["x"]), int(e["y"])), 9)
        for x, y, vida in self.chispas:
            r = int(30 * (1 - vida / 0.4)) + 6
            pygame.draw.circle(lienzo, COLORES["oro"], (int(x), int(y)), r, 3)
        lienzo.set_clip(None)
        from ..assets.texto_mate import fuente
        img = fuente(24, True).render(f"Atrapadas: {self.atrapadas}", True, COLORES["oro"])
        lienzo.blit(img, (ZONA.left + 20, ZONA.bottom - 44))

    def rendimiento(self):
        return 0.4 + 0.9 * min(1.0, self.atrapadas / self.META)
