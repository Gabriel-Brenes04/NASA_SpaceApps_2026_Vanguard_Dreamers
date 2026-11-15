# -*- coding: utf-8 -*-
"""PLANTILLA para hacer un microjuego nuevo.

1. Copiá este archivo con el nombre de tu microjuego, SIN el guion bajo:
       huerto.py · paneles.py · escudo.py · oxigeno.py
2. Cambiá el nombre de la clase y llená las 4 partes marcadas con «HACER».
3. Probalo solo:            python tools/probar_microjuego.py huerto
4. Revisá que pase:         python tools/verificar.py
No hace falta tocar ningún otro archivo: el juego lo encuentra solo.

Reglas para que todo encaje:
  · Solo pygame-ce (nada de otras librerías). Solo el RATÓN.
  · Dura entre 5 y 45 segundos (`duracion`).
  · Se dibuja dentro de ZONA (x 40 a 1240, y 110 a 680). Arriba va el título y el reloj.
  · Nada de imágenes, sonidos ni letras bajadas de internet, salvo que tengan licencia libre y se
    anote en CREDITOS.md. Lo más seguro: dibujar con pygame.draw (rect, circle, line, polygon).
  · Números al azar con self.rng, no con random.
  · El estado de la base (self.base) se puede LEER para cambiar la dificultad, pero NO modificar.
"""
import pygame

from .base import Microjuego, ZONA, COLORES


class MiMicrojuego(Microjuego):
    titulo = "Nombre del microjuego"                  # HACER: título corto
    instruccion = "Qué hay que hacer, en una línea"   # HACER
    tarea = None                                      # HACER: "cosecha", "oxigeno", "regolito" o "hielo"
    duracion = 8.0

    def iniciar(self):
        # HACER: preparar el juego (posiciones, puntos...)
        self.puntos = 0

    def actualizar(self, eventos, dt):
        # HACER: mover cosas y revisar los clics.
        #   self.clics   → lista de (x, y) de los clics de este cuadro
        #   self.raton   → (x, y) del ratón ahora mismo
        #   self.apretado → True mientras el botón está apretado (para arrastrar)
        #   dt           → segundos desde el cuadro anterior (multiplicar las velocidades por dt)
        for x, y in self.clics:
            self.puntos += 1

    def dibujar(self, lienzo):
        # HACER: dibujar dentro de ZONA
        pygame.draw.rect(lienzo, COLORES["panel"], ZONA, border_radius=16)

    def rendimiento(self):
        # HACER: 0,4 si salió muy mal · 1,0 normal · 1,3 perfecto
        return 0.4 + 0.9 * min(1.0, self.puntos / 10)
