# -*- coding: utf-8 -*-
"""Juega misiones completas SIN ventana, dibujando TODAS las pantallas de cada día.

Sirve para dos cosas:
  1) prueba: si alguna pantalla revienta con algún estado de la base, aquí se ve;
  2) capturas: guarda PNG de cada tipo de pantalla para la propuesta y la entrega.

    python tools/capturas.py                 (prueba 30 misiones + capturas en _capturas/)
    python tools/capturas.py --salida ENTREGA/capturas
"""
import os
import random
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
sys.path.insert(0, os.path.join(RAIZ, "tools"))

import pygame  # noqa: E402
from base_lunar.juego import Juego  # noqa: E402
import simular_misiones as SM  # noqa: E402


def guardar(j, carpeta, nombre, hechas):
    if carpeta and nombre not in hechas:
        j.dibujar()
        pygame.image.save(j.lienzo, os.path.join(carpeta, nombre + ".png"))
        hechas.add(nombre)


def jugar(j, semilla, tipo, rng, carpeta=None, hechas=None, modo="completa"):
    hechas = hechas if hechas is not None else set()
    j.fase = "titulo"
    j.dibujar()
    guardar(j, carpeta, "01_titulo", hechas)
    j.nueva_mision(semilla, modo)
    while True:
        m = j.m
        j.dibujar()
        dia = m.e.dia
        if dia == 1:
            guardar(j, carpeta, "02_tablero_dia", hechas)
        if dia == m.e.luz + 2:
            guardar(j, carpeta, "07_tablero_noche" + ("_corta" if modo == "corta" else ""), hechas)
        if modo == "corta" and dia == 1:
            guardar(j, carpeta, "02b_tablero_corta", hechas)
        j.ir_decision()
        j.dibujar()
        d = m.decision
        if d:
            if d.ident == "tormenta":
                guardar(j, carpeta, "04_evento_tormenta", hechas)
            elif d.ident == "noche":
                guardar(j, carpeta, "05_decision_noche", hechas)
            elif d.ident == "electrolisis":
                guardar(j, carpeta, "03_decision_fraccion", hechas)
            buenas = [i for i, o in enumerate(d.opciones) if o.correcta]
            malas = [i for i, o in enumerate(d.opciones) if not o.correcta]
            if tipo == "experto":
                i = buenas[0] if buenas else 0
            elif tipo == "descuidado" and malas:
                i = rng.choice(malas)
            else:
                i = rng.randrange(len(d.opciones))
            j.elegir(i)
            j.dibujar()
            if d.ident == "noche":
                guardar(j, carpeta, "06_resultado_noche", hechas)
            if not j.res["correcta"]:
                guardar(j, carpeta, "06b_resultado_error", hechas)
            j.fase = "tarea"
            j.dibujar()
            guardar(j, carpeta, "08_tarea", hechas)
        ts = m.tareas_disponibles()
        if ts:
            tid = SM.tarea_experta(m) if tipo == "experto" else rng.choice(ts)
            j.elegir_tarea(tid or ts[0])
            cuadros = 0
            while j.fase == "micro":           # el microjuego se juega con clics al azar
                ev = []
                if cuadros % 12 == 0:
                    ev = [pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1,
                                             pos=(rng.randint(60, 1220), rng.randint(130, 660)))]
                j._dt = 1 / 60
                j.paso_micro(ev)
                if cuadros % 20 == 0 or cuadros == 600:     # dibujar cada cuadro tardaría demasiado
                    j.dibujar()
                if cuadros == 600:
                    guardar(j, carpeta, "08b_microjuego", hechas)
                cuadros += 1
            j.dibujar()
        j.cerrar()
        j.dibujar()
        guardar(j, carpeta, "09_cierre", hechas)
        j.siguiente()
        j.dibujar()
        if j.fase == "fin":
            guardar(j, carpeta, "10_fin_" + m.fin + ("_corta" if modo == "corta" else ""), hechas)
            return m


def main():
    args = sys.argv[1:]
    carpeta = args[args.index("--salida") + 1] if "--salida" in args else os.path.join(RAIZ, "_capturas")
    if "--en" in args:
        from base_lunar import textos
        textos.poner_idioma("en")
        if "--salida" not in args:
            carpeta = os.path.join(RAIZ, "_capturas", "en")
    os.makedirs(carpeta, exist_ok=True)
    j = Juego(ventana=False)
    rng = random.Random(7)
    hechas = set()
    resultados = []
    for s in range(30):
        tipo = ("experto", "azar", "descuidado")[s % 3]
        modo = "corta" if s % 2 else "completa"
        m = jugar(j, 300 + s, tipo, rng, carpeta, hechas, modo)
        resultados.append((tipo, m.fin))
    j.fase = "datos"
    guardar(j, carpeta, "11_datos_nasa", hechas)
    j.fase = "como"
    guardar(j, carpeta, "12_como_se_juega", hechas)
    print("30 misiones (15 completas y 15 cortas) jugadas pantalla por pantalla sin errores.")
    for tipo in ("experto", "azar", "descuidado"):
        g = sum(1 for tp, f in resultados if tp == tipo and f == "victoria")
        print(f"  {tipo}: {g} de 10 ganadas")
    print("capturas:", ", ".join(sorted(hechas)))


if __name__ == "__main__":
    main()
