# -*- coding: utf-8 -*-
"""Efectos de sonido sintetizados con numpy (obra propia, sin archivos ni licencias).

    sonido.play("bien")              un efecto
    sonido.play("sello", 0.7)        con volumen (0 a 1)
    sonido.nota(k)                   la nota k de una escala: los aciertos seguidos suenan como una melodía
    sonido.bucle("siseo", 0.5)       un sonido que se repite solo; se llama cada cuadro con el volumen
    sonido.parar_bucles()            apaga los que se repiten (al terminar un microjuego)

Si no hay numpy o no hay tarjeta de sonido, el juego sigue mudo sin avisar.
"""
import pygame

_SONIDOS = {}
_BUCLES = {}          # nombre -> canal reservado
ACTIVO = False
NOTAS = 15            # notas de la escala (pentatónica: siempre suenan bien juntas)
RESERVADOS = 8        # canales apartados para los bucles


def iniciar():
    global ACTIVO
    try:
        import numpy as np
        if not pygame.mixer.get_init():
            pygame.mixer.init(44100, -16, 2, 512)
        sr, _fmt, canales = pygame.mixer.get_init()
        pygame.mixer.set_num_channels(32)
        pygame.mixer.set_reserved(RESERVADOS)
        rng = np.random.default_rng(11)

        # ── herramientas ─────────────────────────────────────────────────────────────
        def tt(d):
            return np.arange(int(sr * d)) / sr

        def seno(f, d):
            """Onda seno; f puede ser un número o un arreglo del mismo largo (un barrido)."""
            if np.isscalar(f):
                return np.sin(2 * np.pi * f * tt(d))
            return np.sin(2 * np.pi * np.cumsum(f) / sr)

        def barrido(f0, f1, d):
            return seno(np.linspace(f0, f1, int(sr * d)), d)

        def env(d, ataque=0.003, k=5.0):
            """Envolvente: sube rápido y se apaga (k grande = se apaga más rápido)."""
            n = int(sr * d)
            e = np.exp(-k * np.arange(n) / max(1, n))
            a = max(1, min(n, int(ataque * sr)))
            e[:a] *= np.linspace(0, 1, a)
            r = max(1, min(n, int(0.006 * sr)))
            e[-r:] *= np.linspace(1, 0, r)
            return e

        def campana(d):
            return np.sin(np.pi * np.clip(tt(d) / d, 0, 1))

        def ruido(d):
            return rng.standard_normal(int(sr * d))

        def banda(x, lo, hi):
            """Deja pasar solo las frecuencias entre lo y hi (con FFT: en un bucle no deja costura)."""
            X = np.fft.rfft(x)
            f = np.fft.rfftfreq(len(x), 1 / sr)
            m = np.clip((f - lo * 0.8) / (lo * 0.2 + 1), 0, 1) * np.clip((hi * 1.25 - f) / (hi * 0.25), 0, 1)
            return np.fft.irfft(X * m, len(x))

        def junta(*partes):
            return np.concatenate(partes)

        def mezcla(*ondas):
            largo = max(len(o) for o in ondas)
            out = np.zeros(largo)
            for o in ondas:
                out[:len(o)] += o
            return out

        def corrida(x, seg):
            out = np.zeros(len(x) + int(seg * sr))
            out[int(seg * sr):] = x
            return out

        def bell(f, d=0.45, k=6.0, parciales=((1, 1), (2, .45), (3, .18), (4.2, .08))):
            return sum(a * seno(f * m, d) for m, a in parciales) * env(d, 0.002, k)

        def destellos(d, n=10, lo=2600, hi=5200):
            x = np.zeros(int(sr * d))
            for _ in range(n):
                f = rng.uniform(lo, hi)
                b = bell(f, 0.09, 7.0, ((1, 1), (2.1, .3)))
                i0 = int(rng.integers(0, max(1, len(x) - len(b))))
                x[i0:i0 + len(b)] += b * rng.uniform(0.3, 1.0)
            return x

        def hacer(onda, vol=0.5):
            pico = float(np.abs(onda).max()) or 1.0
            a = (onda / pico * vol * 30000).astype(np.int16)
            arr = a if canales == 1 else np.ascontiguousarray(np.repeat(a[:, None], canales, axis=1))
            return pygame.sndarray.make_sound(arr)

        def tono(notas, dur, vol=0.35, forma="seno"):
            partes = []
            for fr in notas:
                x = tt(dur)
                if forma == "cuadrada":
                    w = np.sign(np.sin(2 * np.pi * fr * x)) * 0.5
                else:
                    w = np.sin(2 * np.pi * fr * x) + 0.3 * np.sin(4 * np.pi * fr * x)
                e = np.exp(-4 * x / dur)
                a = max(1, int(0.008 * sr))
                e[:a] *= np.linspace(0, 1, a)
                partes.append(w * e)
            return hacer(np.concatenate(partes), vol)

        S = _SONIDOS
        # ── los de siempre (los usa el juego) ────────────────────────────────────────
        S["click"] = tono([880], 0.05, 0.25)
        S["bien"] = tono([660, 880, 1320], 0.11)
        S["mal"] = tono([392, 330, 247], 0.14)
        S["alerta"] = tono([988, 740, 988, 740], 0.12, 0.3, "cuadrada")
        S["dia"] = tono([523, 659, 784], 0.16, 0.3)
        S["victoria"] = tono([523, 659, 784, 1047, 1319], 0.16)
        S["derrota"] = tono([440, 392, 349, 262], 0.28)

        # ── comunes a los microjuegos ────────────────────────────────────────────────
        S["cuenta"] = hacer(bell(660, 0.2, 8), 0.3)
        S["ya"] = hacer(mezcla(bell(880, 0.55), bell(1320, 0.5) * 0.8, bell(1760, 0.45) * 0.5), 0.36)
        S["tiempo"] = hacer(junta(bell(1047, 0.16, 2), bell(784, 0.16, 2), bell(523, 0.5, 4)), 0.34)
        for i, f in enumerate((1047, 1319, 1568)):
            S[f"estrella{i + 1}"] = hacer(mezcla(bell(f, 0.6), bell(f * 1.5, 0.5) * 0.4, destellos(0.4, 4) * 0.3), 0.36)
        S["estrella0"] = hacer(bell(330, 0.25, 9), 0.18)          # estrella que no se ganó
        S["nivel"] = hacer(junta(*[bell(f, 0.075, 2) for f in (523, 659, 784)],
                                 mezcla(bell(1047, 0.5), destellos(0.45, 6) * 0.35)), 0.34)
        S["combo"] = hacer(mezcla(barrido(700, 1500, 0.12) * env(0.12, 0.003, 2), destellos(0.25, 5) * 0.4), 0.26)
        escala = (0, 2, 4, 7, 9)
        for k in range(NOTAS):
            f = 392 * 2 ** ((escala[k % 5] + 12 * (k // 5)) / 12)
            S[f"n{k}"] = hacer(bell(f, 0.42, 7, ((1, 1), (2, .35), (3, .12), (5.4, .05))), 0.3)
        S["fallo"] = hacer(barrido(230, 130, 0.13) * env(0.13, 0.003, 6), 0.2)

        # ── oxígeno ──────────────────────────────────────────────────────────────────
        S["siseo"] = hacer(banda(ruido(1.0), 2200, 9000) * (1 + 0.18 * np.sin(2 * np.pi * 7 * tt(1.0))), 0.45)
        d = 0.4
        clanc = sum(a * seno(440 * m, d) for m, a in ((1, 1), (2.76, .6), (5.4, .35), (8.93, .2))) * env(d, 0.001, 12)
        S["sello"] = hacer(clanc + banda(ruido(d), 3000, 9000) * env(d, 0.001, 16) * 0.7, 0.4)
        d = 0.16
        S["soldar"] = hacer(banda(ruido(d), 1500, 7000) * (np.sign(np.sin(2 * np.pi * 90 * tt(d))) * 0.5 + 0.5)
                            * env(d, 0.001, 4), 0.3)
        d = 0.6
        e = campana(d) ** 1.5
        S["escape"] = hacer(banda(ruido(d), 500, 5000) * e + 0.35 * barrido(380, 140, d) * e, 0.36)
        x = np.zeros(int(sr * 2.0))
        for _ in range(16):
            f0, d = rng.uniform(320, 760), 0.05
            b = barrido(f0, f0 * 1.7, d) * env(d, 0.002, 5)
            i0 = int(rng.integers(0, len(x) - len(b)))
            x[i0:i0 + len(b)] += b * rng.uniform(0.4, 1.0)
        S["burbujas"] = hacer(x, 0.2)
        x = seno(60, 1.0) * 0.6 + seno(120, 1.0) * 0.5 + seno(180, 1.0) * 0.25 + banda(ruido(1.0), 60, 500) * 2.5
        S["zumbido"] = hacer(x, 0.22)
        d = 0.35
        S["tanque"] = hacer(junta(barrido(300, 900, d) * env(d, 0.01, 2) * 0.5,
                                  mezcla(bell(1047, 0.6), bell(1319, 0.6), bell(1568, 0.6))), 0.4)
        S["llave"] = hacer(junta(barrido(400, 1800, 0.3) * env(0.3, 0.01, 1.5), destellos(0.5, 12)), 0.36)
        S["alarma"] = hacer(junta(seno(880, 0.16) * env(0.16, 0.005, 2), seno(660, 0.16) * env(0.16, 0.005, 2)), 0.2)

        # ── hielo ────────────────────────────────────────────────────────────────────
        x1 = tt(1.0)
        sierra = sum(np.sin(2 * np.pi * 90 * k * x1) / k for k in range(1, 9))
        S["motor"] = hacer(sierra * (1 + 0.3 * np.sin(2 * np.pi * 15 * x1)) + banda(ruido(1.0), 30, 350) * 4, 0.32)
        x = np.zeros(len(x1))
        idx = rng.integers(0, len(x), 420)
        x[idx] = rng.uniform(-1, 1, len(idx))
        S["tierra"] = hacer(banda(x, 700, 4500) + banda(ruido(1.0), 200, 1200) * 0.02, 0.3)
        x = np.zeros(len(x1))
        idx = rng.integers(0, len(x), 160)
        x[idx] = rng.uniform(-1, 1, len(idx))
        canto = (seno(1760, 1.0) + 0.5 * seno(2640, 1.0)) * (0.6 + 0.4 * np.sin(2 * np.pi * 6 * x1))
        S["hielo"] = hacer(canto * 0.05 + banda(x, 4500, 11000), 0.3)
        d = 0.5
        S["atasco"] = hacer(barrido(110, 45, d) * env(d, 0.001, 7) + banda(ruido(d), 150, 1800) * env(d, 0.001, 5) * 0.8
                            + sum(a * seno(310 * m, d) for m, a in ((1, 1), (2.3, .5), (3.9, .3))) * env(d, 0.001, 10) * 0.5,
                            0.45)
        d = 0.7
        S["nucleo"] = hacer(sum(a * seno(2093 * m, d) for m, a in ((1, 1), (2.4, .4), (1.5, .5))) * env(d, 0.001, 6)
                            + banda(ruido(d), 1200, 6000) * campana(d) * 0.3, 0.34)
        S["perfecto"] = hacer(junta(*[bell(f, 0.06, 2) for f in (1047, 1319, 1568)],
                                    mezcla(bell(2093, 0.6), destellos(0.6, 10) * 0.6)), 0.36)
        d = 0.9
        ping = seno(1250, d) * env(d, 0.002, 9)
        S["radar"] = hacer(mezcla(ping, corrida(ping * 0.35, 0.2)), 0.24)

        # ── recreo (cámara) ──────────────────────────────────────────────────────────
        x = np.zeros(int(sr * 0.12))
        for i0, a in ((0, 1.0), (int(0.045 * sr), 0.7)):
            b = banda(ruido(0.014), 1500, 7000) * env(0.014, 0.0005, 6)
            x[i0:i0 + len(b)] += b * a
        S["obturador"] = hacer(x, 0.4)
        x8 = tt(8.0)
        pad = np.zeros(len(x8))
        for f, a in ((130.75, 1), (196.0, .8), (246.875, .55), (329.625, .45), (392.0, .25)):
            pad += a * (np.sin(2 * np.pi * f * x8) + 0.6 * np.sin(2 * np.pi * (f + 0.25) * x8)
                        + 0.12 * np.sin(2 * np.pi * 2 * f * x8))
        S["ambiente"] = hacer(pad * (0.75 + 0.25 * np.sin(2 * np.pi * 0.25 * x8)), 0.18)
        S["cometa"] = hacer(mezcla(junta(*[bell(f, 0.06, 2) for f in (2637, 2349, 2093, 1760)], bell(1568, 0.6)),
                                   destellos(0.8, 14) * 0.5), 0.34)
        d = 0.2
        S["borrosa"] = hacer(sum(np.sin(2 * np.pi * 150 * k * tt(d)) / k for k in range(1, 6)) * env(d, 0.004, 3), 0.18)
        S["album"] = hacer(banda(ruido(0.16), 800, 5000) * campana(0.16), 0.16)

        # ── estiba ───────────────────────────────────────────────────────────────────
        S["grua"] = hacer(sum(np.sin(2 * np.pi * 120 * k * x1) / k ** 1.3 for k in range(1, 7))
                          * (1 + 0.25 * np.sin(2 * np.pi * 20 * x1)) + banda(ruido(1.0), 200, 2500) * 1.5, 0.24)
        S["soltar"] = hacer(mezcla(banda(ruido(0.14), 1200, 5000) * env(0.14, 0.001, 5), bell(2400, 0.03, 10) * 0.5), 0.3)
        d = 0.3
        golpe = barrido(95, 48, d) * env(d, 0.002, 7) + banda(ruido(d), 40, 400) * env(d, 0.001, 12) * 3
        S["golpe"] = hacer(golpe, 0.5)
        clac = mezcla(bell(2600, 0.05, 12), corrida(bell(1900, 0.05, 12), 0.04))
        S["clac"] = hacer(clac, 0.3)
        S["sellar"] = hacer(junta(mezcla(golpe, clac * 0.6), *[bell(f, 0.07, 2) for f in (523, 659, 784)],
                                  bell(1047, 0.5)), 0.42)
        d = 0.32
        S["noentra"] = hacer(sum(np.sin(2 * np.pi * 110 * k * tt(d)) / k for k in range(1, 10))
                             * (0.7 + 0.3 * np.sin(2 * np.pi * 25 * tt(d))) * env(d, 0.004, 2), 0.26)
        d = 0.2
        S["hueco"] = hacer(barrido(320, 220, d) * env(d, 0.002, 9) + banda(ruido(d), 300, 1500) * env(d, 0.001, 15) * 0.4,
                           0.32)
        ACTIVO = True
    except Exception:
        ACTIVO = False


def play(nombre, vol=1.0):
    s = _SONIDOS.get(nombre)
    if s is not None:
        try:
            canal = s.play()
            if canal is not None and vol < 1.0:
                canal.set_volume(max(0.0, vol))
        except Exception:
            pass


def nota(k, vol=1.0):
    """La nota k de la escala; pasando la última, se queda dando vueltas en la octava de arriba."""
    k = max(0, int(k))
    if k >= NOTAS:
        k = NOTAS - 5 + (k - NOTAS) % 5
    play(f"n{k}", vol)


def bucle(nombre, vol):
    """Un sonido que se repite solo. Se llama cada cuadro con el volumen que se quiere (0 = calladito)."""
    s = _SONIDOS.get(nombre)
    if s is None:
        return
    try:
        i = _BUCLES.get(nombre)
        if i is None:
            if len(_BUCLES) >= RESERVADOS:            # se liberan los de otros microjuegos que ya callaron
                for k in [k for k, j in _BUCLES.items() if not pygame.mixer.Channel(j).get_busy()]:
                    del _BUCLES[k]
            libres = [j for j in range(RESERVADOS) if j not in _BUCLES.values()]
            if not libres:
                return
            i = _BUCLES[nombre] = libres[0]
        canal = pygame.mixer.Channel(i)
        vol = max(0.0, min(1.0, float(vol)))
        if not canal.get_busy() or canal.get_sound() is not s:
            if vol < 0.01:
                return
            canal.play(s, loops=-1, fade_ms=120)
        canal.set_volume(vol)
    except Exception:
        pass


def parar_bucles(ms=250):
    for i in _BUCLES.values():
        try:
            pygame.mixer.Channel(i).fadeout(ms)
        except Exception:
            pass
