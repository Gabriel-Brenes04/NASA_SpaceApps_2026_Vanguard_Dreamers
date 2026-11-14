# -*- coding: utf-8 -*-
"""Efectos de sonido sintetizados con numpy (obra propia, sin archivos ni licencias).

Si no hay numpy o no hay tarjeta de sonido, el juego sigue mudo sin avisar.
"""
import pygame

_SONIDOS = {}
ACTIVO = False


def iniciar():
    global ACTIVO
    try:
        import numpy as np
        if not pygame.mixer.get_init():
            pygame.mixer.init(44100, -16, 2, 1024)
        sr = 44100

        def tono(notas, dur, vol=0.35, forma="seno"):
            partes = []
            for fr in notas:
                tt = np.linspace(0, dur, int(sr * dur), False)
                if forma == "cuadrada":
                    w = np.sign(np.sin(2 * np.pi * fr * tt)) * 0.5
                else:
                    w = np.sin(2 * np.pi * fr * tt) + 0.3 * np.sin(4 * np.pi * fr * tt)
                env = np.exp(-4 * tt / dur)
                a = max(1, int(0.008 * sr))
                env[:a] *= np.linspace(0, 1, a)
                partes.append(w * env)
            onda = np.concatenate(partes)
            onda = (onda / max(1e-6, np.abs(onda).max()) * vol * 32767).astype(np.int16)
            return pygame.sndarray.make_sound(np.column_stack([onda, onda]).copy())
        _SONIDOS["click"] = tono([880], 0.05, 0.25)
        _SONIDOS["bien"] = tono([660, 880, 1320], 0.11)
        _SONIDOS["mal"] = tono([392, 330, 247], 0.14)
        _SONIDOS["alerta"] = tono([988, 740, 988, 740], 0.12, 0.3, "cuadrada")
        _SONIDOS["dia"] = tono([523, 659, 784], 0.16, 0.3)
        _SONIDOS["victoria"] = tono([523, 659, 784, 1047, 1319], 0.16)
        _SONIDOS["derrota"] = tono([440, 392, 349, 262], 0.28)
        ACTIVO = True
    except Exception:
        ACTIVO = False


def play(nombre):
    s = _SONIDOS.get(nombre)
    if s is not None:
        try:
            s.play()
        except Exception:
            pass
