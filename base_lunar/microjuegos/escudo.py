# -*- coding: utf-8 -*-
"""Microjuego «Escudo» (tarea: regolito → blindaje).

Corte del hábitat enterrado en el suelo lunar. Una pala excavadora pasa por encima mientras un marcador
va y viene por una barra. Si se hace clic con el marcador en la zona verde, la pala está justo encima del
hábitat y la carga de regolito cae sobre él (suma una capa). Si no, la carga se derrama al lado.
Dato: unos 3 m de regolito sobre el hábitat protegen de la radiación (estudios de la NASA).
"""
import pygame

from .base import Microjuego, ZONA, COLORES
from ..textos import t

REGOLITO = [(128, 116, 104), (108, 98, 88)]       # dos tonos gris pardo para ver cada capa


class Escudo(Microjuego):
    titulo = "Escudo: cubrí el hábitat"
    instruccion = "Hacé clic cuando la pala esté encima del hábitat (zona verde)"
    tarea = "regolito"
    duracion = 8.0
    META = 6                      # capas buenas para el rendimiento máximo
    BARRA = pygame.Rect(290, 132, 700, 26)
    ZONA_W = 130                  # ancho de la zona verde (px de barra)
    ENFRIAR = 0.35                # segundos entre un clic y el siguiente
    DOMO_X, SUELO, RX, RY = 640, 625, 70, 60
    PALA_Y = 275                  # altura de la pala

    def iniciar(self):
        self.titulo = t("mj.escudo.titulo", "Escudo: cubrí el hábitat")
        self.instruccion = t("mj.escudo.instr", "Hacé clic cuando la pala esté encima del hábitat (zona verde)")
        self.aciertos = 0
        self.fallos = 0
        self.marca = self.rng.uniform(0, self.BARRA.w)    # posición del marcador en la barra
        self.sentido = 1
        self.vel = 380.0                                  # px de barra por segundo
        self.centro = self._zona_nueva()
        self.espera = 0.0
        self.cargas = []          # cargas cayendo: [x, y, vy, vx, buena]
        self.capas_dib = 0        # capas que ya cayeron sobre el hábitat
        self.derrames = []        # montoncitos al lado: x
        self.mal = 0.0            # parpadeo rojo tras un fallo

    def _zona_nueva(self):
        """Centro de la zona verde en un lugar nuevo, lejos del marcador."""
        m = self.ZONA_W // 2 + 10
        c = self.rng.uniform(m, self.BARRA.w - m)
        for _ in range(20):
            c = self.rng.uniform(m, self.BARRA.w - m)
            if abs(c - getattr(self, "marca", 0)) > 160:
                break
        return c

    def _pala_x(self):
        """La pala está sobre el hábitat justo cuando el marcador está en el centro de la zona."""
        x = self.DOMO_X + (self.marca - self.centro)
        return max(ZONA.left + 50, min(ZONA.right - 50, x))

    def actualizar(self, eventos, dt):
        self.marca += self.sentido * self.vel * dt
        if self.marca >= self.BARRA.w:
            self.marca, self.sentido = self.BARRA.w, -1
        elif self.marca <= 0:
            self.marca, self.sentido = 0, 1
        self.espera = max(0.0, self.espera - dt)
        self.mal = max(0.0, self.mal - dt)
        for _ in self.clics:
            if self.espera > 0:
                continue                      # todavía enfriando: el clic no cuenta
            self.espera = self.ENFRIAR
            buena = abs(self.marca - self.centro) <= self.ZONA_W / 2
            px = self._pala_x()
            lado = 1 if px >= self.DOMO_X else -1
            self.cargas.append([px, self.PALA_Y + 30.0, 0.0, 0.0 if buena else 220.0 * lado, buena])
            if buena:
                self.aciertos += 1
                self.vel += 55.0              # cada acierto acelera el marcador
                self.centro = self._zona_nueva()
            else:
                self.fallos += 1
                self.mal = 0.3
        resto = []
        for c in self.cargas:
            c[2] += 1500 * dt
            c[1] += c[2] * dt
            c[0] += c[3] * dt
            tope = self.SUELO - self.RY - 12 * self.capas_dib if c[4] else self.SUELO
            if c[1] >= tope:
                if c[4]:
                    self.capas_dib += 1
                else:
                    self.derrames.append(c[0])
            else:
                resto.append(c)
        self.cargas = resto

    def dibujar(self, lienzo):
        from ..texto_mate import fuente
        pygame.draw.rect(lienzo, (3, 4, 14), ZONA, border_radius=16)
        lienzo.set_clip(ZONA)
        px, g = self._pala_x(), COLORES
        cx, s = self.DOMO_X, self.SUELO
        # excavadora: cabina a la izquierda y brazo hasta la pala
        pygame.draw.rect(lienzo, (200, 150, 40), (ZONA.left + 40, s - 70, 130, 60), border_radius=8)
        pygame.draw.rect(lienzo, (70, 80, 110), (ZONA.left + 120, s - 66, 40, 30))
        pygame.draw.rect(lienzo, (40, 40, 50), (ZONA.left + 30, s - 18, 150, 18), border_radius=9)
        pygame.draw.line(lienzo, (200, 150, 40), (ZONA.left + 80, s - 60), (px, self.PALA_Y), 12)
        # pala (balde) con su carga si ya está lista
        pygame.draw.polygon(lienzo, (170, 175, 190), [(px - 38, self.PALA_Y), (px + 38, self.PALA_Y),
                                                      (px + 26, self.PALA_Y + 38), (px - 26, self.PALA_Y + 38)])
        if self.espera <= 0:
            pygame.draw.ellipse(lienzo, REGOLITO[0], (px - 28, self.PALA_Y + 8, 56, 26))
        # hábitat (media cúpula) y capas de regolito: cada capa es un anillo más grueso
        pygame.draw.ellipse(lienzo, (190, 200, 225), (cx - self.RX, s - self.RY, 2 * self.RX, 2 * self.RY))
        pygame.draw.ellipse(lienzo, (90, 140, 200), (cx - 30, s - self.RY + 14, 60, 26))
        for i in range(1, self.capas_dib + 1):
            r = pygame.Rect(0, 0, 2 * (self.RX + 12 * i), 2 * (self.RY + 12 * i))
            r.center = (cx, s)
            pygame.draw.ellipse(lienzo, REGOLITO[i % 2], r, 14)
        # suelo y montoncitos derramados
        pygame.draw.rect(lienzo, (74, 66, 60), (ZONA.left, s, ZONA.w, ZONA.bottom - s))
        pygame.draw.line(lienzo, (110, 100, 92), (ZONA.left, s), (ZONA.right, s), 3)
        for x in self.derrames:
            pygame.draw.polygon(lienzo, REGOLITO[0], [(x - 26, s), (x, s - 16), (x + 26, s)])
        for x, y, _, _, buena in self.cargas:
            pygame.draw.circle(lienzo, REGOLITO[0] if buena else (150, 110, 90), (int(x), int(y)), 14)
        # barra de tiempos con la zona verde y el marcador
        b = self.BARRA
        pygame.draw.rect(lienzo, (36, 42, 72), b, border_radius=13)
        zx = b.x + self.centro - self.ZONA_W / 2
        pygame.draw.rect(lienzo, g["verde"], (zx, b.y, self.ZONA_W, b.h), border_radius=13)
        col = g["rojo"] if self.mal > 0 else g["oro"]
        pygame.draw.rect(lienzo, col, (b.x + self.marca - 5, b.y - 8, 10, b.h + 16), border_radius=4)
        lienzo.set_clip(None)
        img = fuente(26, True).render(t("mj.escudo.capas", "Capas: {n}", n=self.aciertos), True, g["oro"])
        lienzo.blit(img, (ZONA.left + 20, ZONA.bottom - 70))
        img = fuente(17, False).render(t("mj.escudo.nota", "Unos 3 m de regolito sobre el hábitat protegen a la "
                                         "tripulación de la radiación (estudios de la NASA)."), True, g["gris"])
        lienzo.blit(img, (ZONA.left + 20, ZONA.bottom - 30))

    def rendimiento(self):
        r = 0.4 + 0.9 * min(1.0, self.aciertos / self.META) - 0.05 * self.fallos
        return max(0.4, min(1.3, r))
