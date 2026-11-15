import pygame
import json

from .data.image_of_the_day.contactar_api import main as cargar_imagenes_nasa
from .escenas.titulo import MenuInicial
from .assets.texto_mate import fuente, fuente_pixel, pixel
from .assets.constantes import W, H, C

cargar_imagenes_nasa()

pygame.init()

pantalla = pygame.display.set_mode((W, H))
pygame.display.set_caption("Prueba visual - Mission Survival")

reloj = pygame.time.Clock()


class Prueba(MenuInicial):

    def __init__(self):
        self.lienzo = pantalla
        self.cuadro = 0
        self.m = None

    
    def cielo(self):
        self.lienzo.fill(C["fondo"])

    def txt(self, s, size, color, x, y, centro=False):
        c = C.get(color, color) if isinstance(color, str) else color
        f = fuente(size)
        img = f.render(str(s), True, c)
        r = img.get_rect(center=(x, y)) if centro else img.get_rect(topleft=(x, y))
        self.lienzo.blit(img, r)

    def pix(self, s, size, color, x, y, centro=False):
        c = C.get(color, color) if isinstance(color, str) else color
        img = fuente_pixel(size).render(pixel(str(s)), True, c)
        r = img.get_rect(center=(x, y)) if centro else img.get_rect(topleft=(x, y))
        self.lienzo.blit(img, r)

    def boton(self, r, texto, accion, color="panel", tecla=None):
        r = pygame.Rect(r)
        c = C.get(color, C["panel"])
        pygame.draw.rect(self.lienzo, c, r, border_radius=8)
        pygame.draw.rect(self.lienzo, C["borde"], r, 2, border_radius=8)
        if texto:
            self.txt(texto, 20, "texto", r.centerx, r.centery, True)



escena = Prueba()
corriendo = True

while corriendo:

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            corriendo = False

        elif e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                corriendo = False

            elif e.key == pygame.K_SPACE:
                # Adelantar al momento del fundido
                escena.cuadro = (escena.cuadro // 360 + 1) * 360 - 90

    pantalla.fill((0, 0, 0))

    escena._titulo()

    escena.cuadro += 1

    pygame.display.flip()
    reloj.tick(60)

pygame.quit()