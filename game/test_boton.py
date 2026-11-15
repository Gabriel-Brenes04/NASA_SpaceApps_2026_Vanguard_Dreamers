import os
import pygame

from game.logica.juego import Boton

pygame.init()

ANCHO, ALTO = 500, 500
VENTANA = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Prueba de tarjeta")
RELOJ = pygame.time.Clock()

C = {
    "panel2": (27, 36, 62),
    "oro": (255, 190, 75),
    "borde": (75, 91, 125),
    "texto": (240, 240, 245),
    "gris": (180, 190, 210),
}

ruta = os.path.join(os.path.dirname(__file__), ".", "assets", "imagenes_fondo", "titulo", "2026-10-21.png")
img_tarea = pygame.image.load(os.path.abspath(ruta)).convert_alpha()
img_tarea = pygame.transform.smoothscale(img_tarea, (260, 110))

fuente_titulo = pygame.font.SysFont("Arial", 22, bold=True)
fuente_desc = pygame.font.SysFont("Arial", 17)

tarjeta = pygame.Rect(100, 100, 296, 280)
mouse = (0, 0)

ejecutando = True
while ejecutando:
    RELOJ.tick(60)
    mouse = pygame.mouse.get_pos()

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False
        elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
            ejecutando = False

    encima = tarjeta.collidepoint(mouse)

    VENTANA.fill((12, 17, 35))

    pygame.draw.rect(VENTANA, (34, 44, 80) if encima else C["panel2"], tarjeta, border_radius=12)
    pygame.draw.rect(VENTANA, C["oro"] if encima else C["borde"], tarjeta, 2, border_radius=12)

    img_rect = img_tarea.get_rect(midtop=(tarjeta.centerx, tarjeta.y + 8))
    VENTANA.blit(img_tarea, img_rect)

    titulo = fuente_titulo.render("EJEMPLO DE TAREA", True, C["texto"])
    VENTANA.blit(titulo, (tarjeta.x + 14, tarjeta.y + 128))

    descripcion = fuente_desc.render("Descripción de prueba de la tarjeta.", True, C["gris"])
    VENTANA.blit(descripcion, (tarjeta.x + 14, tarjeta.y + 160))

    pygame.display.flip()

pygame.quit()
