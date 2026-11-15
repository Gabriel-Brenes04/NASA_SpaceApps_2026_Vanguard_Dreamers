# -*- coding: utf-8 -*-
"""Dibuja el ícono del juego (la base sobre la Luna, con la Tierra) y lo guarda como .png y .ico.

    python tools/hacer_icono.py <carpeta_de_salida>

El .ico lleva el PNG adentro (formato que Windows entiende desde Vista): no hace falta ninguna librería.
"""
import os
import struct
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
import pygame  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from game.assets.icono import dibujar  # noqa: E402


def main():
    salida = sys.argv[1] if len(sys.argv) > 1 else "."
    os.makedirs(salida, exist_ok=True)
    pygame.init()
    png = os.path.join(salida, "base_lunar.png")
    pygame.image.save(dibujar(256), png)
    datos = open(png, "rb").read()
    # ICONDIR (6 bytes) + 1 ICONDIRENTRY (16 bytes) + el PNG
    ico = struct.pack("<HHH", 0, 1, 1) + struct.pack("<BBBBHHII", 0, 0, 0, 0, 1, 32, len(datos), 22) + datos
    open(os.path.join(salida, "base_lunar.ico"), "wb").write(ico)
    print("ícono:", os.path.join(salida, "base_lunar.ico"))


if __name__ == "__main__":
    main()
