# -*- coding: utf-8 -*-
"""El ícono del juego: la base sobre la Luna, con la Tierra al fondo (dibujado con código)."""
import pygame


def dibujar(tam=256):
    s = pygame.Surface((tam, tam), pygame.SRCALPHA)
    k = tam / 256
    pygame.draw.rect(s, (10, 14, 34), (0, 0, tam, tam), border_radius=int(48 * k))
    for x, y in ((40, 40), (90, 26), (200, 60), (150, 90), (30, 110), (220, 120)):
        pygame.draw.circle(s, (220, 225, 240), (int(x * k), int(y * k)), max(1, int(3 * k)))
    pygame.draw.circle(s, (60, 120, 220), (int(196 * k), int(64 * k)), int(30 * k))          # la Tierra
    pygame.draw.circle(s, (80, 180, 110), (int(186 * k), int(56 * k)), int(11 * k))
    pygame.draw.ellipse(s, (150, 152, 162), (int(-40 * k), int(150 * k), int(336 * k), int(200 * k)))  # la Luna
    pygame.draw.ellipse(s, (120, 122, 132), (int(36 * k), int(206 * k), int(50 * k), int(14 * k)))
    pygame.draw.ellipse(s, (124, 104, 82), (int(64 * k), int(118 * k), int(128 * k), int(96 * k)))   # regolito
    pygame.draw.ellipse(s, (232, 234, 240), (int(76 * k), int(128 * k), int(104 * k), int(76 * k)))  # domo
    for i in range(3):
        pygame.draw.circle(s, (232, 186, 60), (int((104 + i * 24) * k), int(166 * k)), int(7 * k))
    pygame.draw.rect(s, (232, 186, 60), (0, 0, tam, tam), max(2, int(8 * k)), border_radius=int(48 * k))
    return s
