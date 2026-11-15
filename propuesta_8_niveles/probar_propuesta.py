# -*- coding: utf-8 -*-
"""Prueba la propuesta de 8 tareas SIN tocar el juego del repositorio.

Copia la carpeta game/ a una carpeta temporal, le pone encima los archivos de la propuesta (archivos/game/...)
y abre esa copia. El juego del repositorio queda igual.

    python propuesta_8_niveles/probar_propuesta.py      (o doble clic en JUGAR_propuesta.bat)
"""
import os
import shutil
import subprocess
import sys
import tempfile

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
ARCHIVOS = os.path.join(AQUI, "archivos")
DESTINO = os.path.join(tempfile.gettempdir(), "mission_survival_propuesta_8")

if os.path.exists(DESTINO):
    shutil.rmtree(DESTINO)
shutil.copytree(os.path.join(RAIZ, "game"), os.path.join(DESTINO, "game"),
                ignore=shutil.ignore_patterns("__pycache__", "_capturas"))
for carpeta, _sub, nombres in os.walk(ARCHIVOS):
    for nombre in nombres:
        origen = os.path.join(carpeta, nombre)
        destino = os.path.join(DESTINO, os.path.relpath(origen, ARCHIVOS))
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        shutil.copyfile(origen, destino)
print("Copia de prueba armada en:", DESTINO)
sys.exit(subprocess.call([sys.executable, "-m", "game.main"], cwd=DESTINO))
