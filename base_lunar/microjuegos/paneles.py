# -*- coding: utf-8 -*-
"""Microjuego «Paneles» (tarea: paneles → energía).

El Sol cruza el cielo negro de la Luna. El panel solar da más potencia mientras más de frente
mire al Sol: eficiencia = cos(ángulo entre la normal del panel y la dirección al Sol).
El ángulo del panel se maneja moviendo el ratón de izquierda a derecha.
"""
import math

import pygame

from .base import Microjuego, ZONA, COLORES
from ..textos import t, n
from ..texto_mate import fuente, fuente_pixel, pixel

P_MAX = 10.9          # potencia a pleno sol de un panel en este juego (kW)


class Paneles(Microjuego):
    titulo = "Paneles: seguí al Sol"
    instruccion = "Mové el ratón para que el panel mire de frente al Sol"
    tarea = "paneles"
    duracion = 8.0

    def iniciar(self):
        self.titulo = t("mj.paneles.titulo", "Paneles: seguí al Sol")
        self.instruccion = t("mj.paneles.instr", "Mové el ratón para que el panel mire de frente al Sol")
        self.sol = -62.0                     # ángulo del Sol desde la vertical (grados; + = derecha)
        self.vel = 17.0                      # grados por segundo
        self.cambio = 2.5                    # segundos para el próximo cambio de velocidad
        self.panel = 0.0                     # ángulo actual del panel
        self.eficiencia = 0.0
        self.suma = 0.0
        self.tiempo = 0.0
        self.cx = ZONA.centerx
        self.horizonte = ZONA.bottom - 110
        self.estrellas = [(self.rng.randint(ZONA.left + 8, ZONA.right - 8), self.rng.randint(ZONA.top + 8, self.horizonte - 10),
                           self.rng.randint(80, 220)) for _ in range(110)]

    def actualizar(self, eventos, dt):
        # el Sol se mueve despacio y cada ~2,5 s cambia un poco de velocidad
        self.cambio -= dt
        if self.cambio <= 0:
            self.cambio = 2.5
            self.vel = self.rng.uniform(11.0, 23.0)
        self.sol = max(-80.0, min(80.0, self.sol + self.vel * dt))
        # el ratón fija el ángulo deseado (−90° a +90° a lo ancho de ZONA); el panel lo sigue suavemente
        meta = (self.raton[0] - ZONA.centerx) / (ZONA.w / 2) * 90.0
        meta = max(-90.0, min(90.0, meta))
        self.panel += (meta - self.panel) * min(1.0, 9.0 * dt)
        self.eficiencia = max(0.0, math.cos(math.radians(self.panel - self.sol)))
        self.suma += self.eficiencia * dt
        self.tiempo += dt

    def dibujar(self, lienzo):
        pygame.draw.rect(lienzo, (3, 4, 14), ZONA, border_radius=16)      # cielo negro, incluso de día
        for x, y, b in self.estrellas:
            lienzo.set_at((x, y), (b, b, min(255, b + 30)))
        lienzo.set_clip(ZONA.inflate(-8, -8))
        # horizonte lunar
        pygame.draw.rect(lienzo, (96, 96, 104), (ZONA.left, self.horizonte, ZONA.w, ZONA.bottom - self.horizonte))
        pygame.draw.line(lienzo, (150, 150, 160), (ZONA.left, self.horizonte), (ZONA.right, self.horizonte), 3)
        for dx in (-380, -190, 230, 420):
            pygame.draw.ellipse(lienzo, (78, 78, 86), (self.cx + dx - 45, self.horizonte + 40, 90, 22))
        # arco del Sol y el Sol
        radio = 340
        pygame.draw.arc(lienzo, (50, 56, 90), (self.cx - radio, self.horizonte - radio, 2 * radio, 2 * radio), 0.0, math.pi, 2)
        s = math.radians(self.sol)
        sol = (self.cx + radio * math.sin(s), self.horizonte - radio * math.cos(s))
        pygame.draw.circle(lienzo, (255, 236, 150), sol, 34)
        pygame.draw.circle(lienzo, (255, 250, 210), sol, 22)
        # poste y panel (gira sobre el pivote)
        pivote = (self.cx, self.horizonte - 110)
        pygame.draw.line(lienzo, (170, 176, 190), (self.cx, self.horizonte), pivote, 10)
        a = math.radians(self.panel)
        normal = (math.sin(a), -math.cos(a))
        lado = (math.cos(a), math.sin(a))
        L, E = 110, 9
        pts = [(pivote[0] + lado[0] * sx * L + normal[0] * sy * E, pivote[1] + lado[1] * sx * L + normal[1] * sy * E)
               for sx, sy in ((-1, 1), (1, 1), (1, -1), (-1, -1))]
        pygame.draw.polygon(lienzo, (40, 90, 170), pts)
        pygame.draw.polygon(lienzo, (170, 200, 240), pts, 3)
        # rayos del Sol hacia el panel: más brillantes mientras más alineado
        ef = self.eficiencia
        col = (int(60 + 195 * ef), int(60 + 170 * ef), int(40 + 60 * ef))
        for k in (-0.7, -0.35, 0.0, 0.35, 0.7):
            dest = (pivote[0] + lado[0] * k * L, pivote[1] + lado[1] * k * L)
            pygame.draw.line(lienzo, col, (sol[0] + lado[0] * k * 25, sol[1] + lado[1] * k * 25), dest, 2 + int(2 * ef))
        lienzo.set_clip(None)
        pygame.draw.rect(lienzo, COLORES["borde"], ZONA, 4, border_radius=16)
        # medidor de potencia (zona verde: eficiencia de 0,97 en adelante, unos 15°)
        med = pygame.Rect(ZONA.left + 30, ZONA.top + 52, 520, 26)
        pygame.draw.rect(lienzo, (36, 42, 72), med, border_radius=8)
        verde = ef >= 0.97
        pygame.draw.rect(lienzo, COLORES["verde"] if verde else COLORES["cian"], (med.x, med.y, int(med.w * ef), med.h), border_radius=8)
        x0 = med.x + int(med.w * 0.97)
        pygame.draw.rect(lienzo, COLORES["verde"], (x0, med.y - 6, med.right - x0, med.h + 12), 3, border_radius=4)
        pygame.draw.rect(lienzo, COLORES["borde"], med, 2, border_radius=8)
        txt = t("mj.paneles.potencia", "Potencia: {pmax} × cos θ = {kw} kW", pmax=n(P_MAX, 1), kw=n(P_MAX * ef, 1))
        lienzo.blit(fuente(24, True).render(txt, True, COLORES["texto"]), (ZONA.left + 30, ZONA.top + 14))
        img = fuente_pixel(16).render(pixel(f"{int(round(ef * 100))} %"), False, COLORES["verde"] if verde else COLORES["oro"])
        lienzo.blit(img, (med.right + 24, med.y + 5))
        nota = t("mj.paneles.nota", "La NASA explica que un panel da menos mientras más se inclina: la potencia baja con el coseno del ángulo.")
        img = fuente(18, True).render(nota, True, (22, 26, 44))     # oscuro: va sobre el suelo gris
        lienzo.blit(img, (ZONA.centerx - img.get_width() // 2, ZONA.bottom - 30))

    def rendimiento(self):
        prom = self.suma / self.tiempo if self.tiempo > 0 else 0.0
        return 0.4 + 0.9 * max(0.0, min(1.0, (prom - 0.55) / 0.4))
