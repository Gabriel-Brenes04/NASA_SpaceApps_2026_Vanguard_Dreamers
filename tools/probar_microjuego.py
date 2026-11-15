# -*- coding: utf-8 -*-
"""Probá UN microjuego solo, sin jugar la misión entera.

    python tools/probar_microjuego.py recreo
    python tools/probar_microjuego.py huerto
    python tools/probar_microjuego.py huerto --auto _capturas/micro    (se juega solo y guarda una foto)

Al terminar escribe en la consola el rendimiento (0,4 a 1,3). ESC cierra. ENTER vuelve a empezar.
"""
import importlib
import os
import random
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)

import pygame  # noqa: E402

from base_lunar import simulador as S  # noqa: E402
from base_lunar.microjuegos import Microjuego  # noqa: E402
from base_lunar.texto_mate import fuente  # noqa: E402


def cargar(nombre):
    mod = importlib.import_module(f"base_lunar.microjuegos.{nombre}")
    clases = [v for v in vars(mod).values() if isinstance(v, type) and issubclass(v, Microjuego) and v is not Microjuego]
    propias = [v for v in clases if getattr(v, "tarea", None) and v.__module__ == mod.__name__]
    for v in propias or clases:          # la del archivo, no una clase base importada (como Partida)
        return v
    raise SystemExit(f"En {nombre}.py no hay ninguna clase que herede de Microjuego.")


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    nombre = sys.argv[1].removesuffix(".py")
    auto = sys.argv[sys.argv.index("--auto") + 1] if "--auto" in sys.argv else None
    clase = cargar(nombre)
    pygame.init()
    from base_lunar import sonido
    sonido.iniciar()
    pygame.display.set_caption(f"Probando: {clase.titulo}")
    ventana = pygame.display.set_mode((1280, 720))
    lienzo = pygame.Surface((1280, 720))
    reloj = pygame.time.Clock()
    base = S.Estado()
    rng = random.Random(1)
    mj = clase(base, rng)
    cuadro = 0
    resultado = None
    while True:
        eventos = pygame.event.get()
        for ev in eventos:
            if ev.type == pygame.QUIT or (ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE):
                sonido.parar_bucles(0)
                pygame.quit()
                return
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_RETURN and resultado is not None:
                mj, resultado = clase(base, rng), None
        if auto and resultado is None and cuadro % 9 == 0:
            # se juega solo: clics al azar DENTRO de su propia ventana (nunca en otras)
            pos = (rng.randint(60, 1220), rng.randint(130, 660))
            pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=pos))
        if resultado is None:
            if mj.paso(eventos, 1 / 60, pygame.mouse.get_pos(), pygame.mouse.get_pressed()[0]):
                sonido.parar_bucles()
                resultado = mj.rendimiento_seguro()
                print(f"{clase.titulo}: rendimiento {resultado:.2f}  (0,4 = muy mal · 1,0 = normal · 1,3 = perfecto)")
            mj.dibujar_todo(lienzo, fuente)
            if auto and cuadro == 600:
                os.makedirs(auto, exist_ok=True)
                pygame.image.save(lienzo, os.path.join(auto, f"{nombre}.png"))
        else:
            img = fuente(36, True).render(f"Rendimiento: {resultado * 100:.0f} %", True, (232, 186, 60))
            lienzo.blit(img, img.get_rect(center=(640, 360)))
            img = fuente(20).render("ENTER para repetir · ESC para salir", True, (236, 239, 246))
            lienzo.blit(img, img.get_rect(center=(640, 410)))
            if auto:
                pygame.quit()
                return
        ventana.blit(lienzo, (0, 0))
        pygame.display.flip()
        reloj.tick(60)
        cuadro += 1


if __name__ == "__main__":
    main()
