# -*- coding: utf-8 -*-
"""Microjuego «Huerto» (tarea: cosecha → comida).

Seis macetas en el invernadero. Cada planta se va secando a su propio ritmo. Hay que apretar sobre el
tanque de agua, arrastrar la gota hasta una maceta y soltarla para regarla. Rinde según lo sanas que
estuvieron las plantas durante todo el juego.
"""
import math

import pygame

from .base import Microjuego, ZONA, COLORES
from ..textos import t
from ..texto_mate import fuente


def _mezclar(a, b, f):
    """Color intermedio entre a y b (f de 0 a 1)."""
    f = max(0.0, min(1.0, f))
    return tuple(int(a[i] + (b[i] - a[i]) * f) for i in range(3))


class Huerto(Microjuego):
    titulo = "Huerto: regá las plantas"
    instruccion = "Arrastrá el agua del tanque a las macetas que se secan"
    tarea = "cosecha"
    duracion = 8.0
    RIEGO = 0.6                    # cuánta agua devuelve una gota

    def iniciar(self):
        self.titulo = t("mj.huerto.titulo", "Huerto: regá las plantas")
        self.instruccion = t("mj.huerto.instr", "Arrastrá el agua del tanque a las macetas que se secan")
        self.tanque = pygame.Rect(ZONA.left + 30, ZONA.top + 150, 170, 270)
        # 6 macetas (2 filas × 3 columnas) a la derecha del tanque
        self.macetas = []
        for fila in range(2):
            for col in range(3):
                x = ZONA.left + 290 + col * 300
                y = ZONA.top + 40 + fila * 245
                self.macetas.append({"rect": pygame.Rect(x, y, 220, 215),
                                     "agua": self.rng.uniform(0.6, 0.9),
                                     "ritmo": self.rng.uniform(0.09, 0.22)})   # agua que pierde por segundo
        self.arrastrando = False
        self.antes = False                 # estado del botón en el cuadro anterior
        self.suma = 0.0                    # para el promedio de agua de todo el juego
        self.tiempo = 0.0
        self.de_dia = True if self.base is None else self.base.de_dia()

    def _maceta_en(self, p):
        for m in self.macetas:
            if m["rect"].collidepoint(p):
                return m
        return None

    def actualizar(self, eventos, dt):
        for m in self.macetas:
            m["agua"] = max(0.0, m["agua"] - m["ritmo"] * dt)
        # apretar sobre el tanque = tomar una gota; soltar sobre una maceta = regar
        if self.apretado and not self.antes and self.tanque.collidepoint(self.raton):
            self.arrastrando = True
        if not self.apretado and self.antes and self.arrastrando:
            m = self._maceta_en(self.raton)
            if m:
                m["agua"] = min(1.0, m["agua"] + self.RIEGO)
            self.arrastrando = False
        if not self.apretado:
            self.arrastrando = False
        self.antes = self.apretado
        # se muestrea cada cuadro (ponderado por dt)
        self.suma += sum(m["agua"] for m in self.macetas) / len(self.macetas) * dt
        self.tiempo += dt

    def _dibujar_planta(self, lienzo, m):
        r, a = m["rect"], m["agua"]
        base = (r.centerx, r.bottom - 70)
        sano, seco, muerto = (70, 200, 100), (220, 200, 60), (120, 80, 40)
        # verde → amarillo → café a medida que baja el agua
        col = _mezclar(muerto, seco, a / 0.3) if a < 0.3 else _mezclar(seco, sano, (a - 0.3) / 0.4)
        caida = 1.0 - min(1.0, a / 0.35)          # 0 = erguida, 1 = marchita
        largo = 62 + 38 * a
        for k in (-1, 0, 1):
            ang = math.radians(k * 38) + math.radians(70) * caida * (k or 1) * 0.8
            punta = (base[0] + math.sin(ang) * largo, base[1] - math.cos(ang) * largo * (1 - 0.45 * caida))
            pygame.draw.line(lienzo, col, base, punta, 6)
            pygame.draw.ellipse(lienzo, col, pygame.Rect(punta[0] - 17, punta[1] - 11, 34, 22))

    def dibujar(self, lienzo):
        # fondo del invernadero: sol por el techo de día; luces LED moradas de noche
        pygame.draw.rect(lienzo, (14, 22, 34) if self.de_dia else (18, 10, 32), ZONA, border_radius=16)
        if self.de_dia:
            sx, sy = ZONA.right - 46, ZONA.top + 55
            pygame.draw.circle(lienzo, (250, 220, 120), (sx, sy), 26)
            for i in range(8):
                ang = i * math.pi / 4
                pygame.draw.line(lienzo, (250, 220, 120), (sx + math.cos(ang) * 34, sy + math.sin(ang) * 34),
                                 (sx + math.cos(ang) * 46, sy + math.sin(ang) * 46), 3)
        else:
            for x in range(ZONA.left + 400, ZONA.right, 300):
                for yy in (ZONA.top + 28, ZONA.top + 273):
                    pygame.draw.rect(lienzo, (60, 50, 80), (x - 70, yy, 140, 10), border_radius=5)
                    pygame.draw.rect(lienzo, (190, 90, 255), (x - 60, yy + 6, 120, 6), border_radius=3)
        pygame.draw.rect(lienzo, COLORES["borde"], ZONA, 4, border_radius=16)
        # tanque de agua
        k = self.tanque
        pygame.draw.rect(lienzo, (30, 60, 100), k, border_radius=12)
        pygame.draw.rect(lienzo, (70, 150, 230), k.inflate(-16, -60).move(0, 20), border_radius=8)
        pygame.draw.rect(lienzo, COLORES["cian"], k, 4, border_radius=12)
        img = fuente(20, True).render(t("mj.huerto.tanque", "Tanque de agua"), True, COLORES["texto"])
        lienzo.blit(img, (k.centerx - img.get_width() // 2, k.top - 32))
        # macetas, plantas y barritas de agua
        for m in self.macetas:
            r, a = m["rect"], m["agua"]
            resalte = self.arrastrando and r.collidepoint(self.raton)
            pygame.draw.rect(lienzo, (46, 80, 120) if resalte else (34, 44, 70), r, border_radius=12)
            self._dibujar_planta(lienzo, m)
            pygame.draw.polygon(lienzo, (170, 100, 70), [(r.centerx - 55, r.bottom - 70), (r.centerx + 55, r.bottom - 70),
                                                         (r.centerx + 40, r.bottom - 14), (r.centerx - 40, r.bottom - 14)])
            barra = pygame.Rect(r.left + 20, r.top + 12, r.w - 40, 12)
            pygame.draw.rect(lienzo, (36, 42, 72), barra, border_radius=6)
            col = COLORES["cian"] if a > 0.4 else COLORES["naranja"] if a > 0.2 else COLORES["rojo"]
            if a > 0:
                pygame.draw.rect(lienzo, col, (barra.x, barra.y, int(barra.w * a), barra.h), border_radius=6)
        # la gota que se arrastra
        if self.arrastrando:
            x, y = int(self.raton[0]), int(self.raton[1])
            pygame.draw.circle(lienzo, (90, 180, 255), (x, y + 6), 15)
            pygame.draw.polygon(lienzo, (90, 180, 255), [(x - 13, y), (x + 13, y), (x, y - 26)])
            pygame.draw.circle(lienzo, (210, 240, 255), (x - 5, y + 2), 4)
        nota = t("mj.huerto.nota", "Las plantas del invernadero dan comida y también devuelven oxígeno.")
        img = fuente(18, False).render(nota, True, COLORES["gris"])
        lienzo.blit(img, (ZONA.centerx - img.get_width() // 2, ZONA.bottom - 30))

    def rendimiento(self):
        prom = self.suma / self.tiempo if self.tiempo > 0 else 0.0
        return 0.4 + 0.9 * max(0.0, min(1.0, (prom - 0.35) / 0.5))
