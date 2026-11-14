# -*- coding: utf-8 -*-
"""Verificador del proyecto: correr ANTES de subir cualquier cambio.

    python tools/verificar.py

Revisa, sin abrir ventana:
  1. que todo el paquete importe;
  2. que los datos de la NASA tengan su fuente;
  3. que las 17 decisiones se armen sin errores y siempre tengan al menos una opción correcta;
  4. que cada microjuego cumpla las reglas (termina solo, dura 5-10 s, rendimiento 0,4-1,3, no rompe
     con clics al azar ni sin ningún clic, dibuja dentro de la pantalla);
  5. que las misiones completas (28 días) y cortas (14) corran enteras, y el balance (el experto gana
     casi siempre y el descuidado casi nunca);
  6. que no se haya colado nada que no debe ir al repositorio.
Termina con «TODO OK» o con la lista de fallas.
"""
import os
import random
import re
import sys

from base.base_lunar import datos_nasa, decisiones, juego, simulador, texto_mate, textos

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
sys.path.insert(0, os.path.join(RAIZ, "tools"))

FALLAS = []


def falla(msg):
    FALLAS.append(msg)
    print("  ✗", msg)


def ok(msg):
    print("  ✓", msg)


def main():
    import pygame
    pygame.init()
    pygame.display.set_mode((1, 1))

    print("1. Paquete")
    from base.base_lunar import microjuegos  # noqa: F401
    ok("base_lunar importa completo")

    print("2. Datos de la NASA")
    sin_url = [f for f in datos_nasa.FUENTES if not f[2].startswith("https://")]
    falla(f"{len(sin_url)} datos sin enlace") if sin_url else ok(f"{len(datos_nasa.FUENTES)} fuentes con enlace")

    print("3. Decisiones")
    m = simulador.Mision(11)
    ids = ["arquitecto", "panel", "noche", "tormenta:moderada", "tormenta:fuerte", "mancha", "reciclador",
           "micrometeorito", "enfermo", "reabastecimiento", "oxigeno", "racion", "electrolisis", "hielo",
           "gravedad", "temperatura", "llamada", "angulo"]
    distintas = set()
    for semilla in range(60):
        modo = ("completa", "corta")[semilla % 2]
        m = simulador.Mision(semilla, modo)
        m.e.dia = 1 + semilla % m.total
        for ident in ids:
            try:
                d = decisiones.construir(ident, m)
            except Exception as ex:  # noqa: BLE001
                falla(f"la decisión {ident} revienta: {ex!r}")
                continue
            if d is None:
                continue
            distintas.add(d.ident)
            if not any(o.correcta for o in d.opciones):
                falla(f"la decisión {ident} (semilla {semilla}) no tiene opción correcta")
            for txt in (d.enunciado, d.explicacion):
                if re.search(r"(?<!\{)\{[a-z_]+\}", txt):
                    falla(f"la decisión {ident} tiene una llave sin llenar: {txt[:60]}")
    ok(f"{len(distintas)} decisiones distintas, todas con al menos una opción correcta")
    if len(distintas) < 12:
        falla("hay menos de 12 decisiones distintas (el reto pide un juego rico)")

    print("4. Microjuegos")
    if microjuegos.ERRORES:
        for mod, err in microjuegos.ERRORES.items():
            falla(f"el microjuego {mod}.py no carga: {err}")
    lienzo = pygame.Surface((1280, 720))
    for tarea, clase in sorted(microjuegos.REGISTRO.items()):
        nombre = f"{clase.__module__.split('.')[-1]}.py ({tarea})"
        if tarea not in simulador.TAREAS:
            falla(f"{nombre}: la tarea «{tarea}» no existe; son {simulador.TAREAS}")
        if not 5 <= clase.duracion <= 10:
            falla(f"{nombre}: dura {clase.duracion} s; tiene que ser de 5 a 10")
        for modo in ("sin clics", "clics al azar"):
            rng = random.Random(3)
            try:
                mj = clase(simulador.Estado(), random.Random(5))
                cuadros = 0
                while True:
                    eventos = []
                    if modo == "clics al azar" and cuadros % 6 == 0:
                        eventos = [pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1,
                                                      pos=(rng.randint(40, 1240), rng.randint(110, 680)))]
                    pos = (rng.randint(40, 1240), rng.randint(110, 680))
                    if mj.paso(eventos, 1 / 60, pos, cuadros % 30 < 15):
                        break
                    mj.dibujar_todo(lienzo, texto_mate.fuente)
                    cuadros += 1
                    if cuadros > 60 * 15:
                        falla(f"{nombre}: no termina solo ({modo})")
                        break
                r = mj.rendimiento()
                if not 0.4 <= float(r) <= 1.3:
                    falla(f"{nombre}: rendimiento {r} fuera de 0,4–1,3 ({modo})")
            except Exception as ex:  # noqa: BLE001
                falla(f"{nombre}: revienta ({modo}): {ex!r}")
                break
        else:
            ok(f"{nombre}: termina solo, rendimiento en rango, aguanta clics al azar")
    faltan = [t for t in ("cosecha", "oxigeno", "regolito", "hielo") if t not in microjuegos.REGISTRO]
    if faltan:
        print(f"  · todavía sin microjuego (se hacen automáticas): {', '.join(faltan)}")

    print("5. Misiones completas y balance")
    import base.tools.simular_misiones as SM
    rng = random.Random(9)
    for modo in ("completa", "corta"):
        for tipo, minimo, maximo in (("experto", 95, 100), ("descuidado", 0, 15)):
            ganadas = sum(SM.jugar(500 + s, tipo, rng, modo).fin == "victoria" for s in range(60))
            pct = 100 * ganadas / 60
            (ok if minimo <= pct <= maximo else falla)(
                f"misión {modo}, {tipo}: gana {pct:.0f} % (se espera {minimo}–{maximo} %)")

    print("5b. Letras incluidas con su licencia")
    carpeta_f = os.path.join(RAIZ, "base_lunar", "fuentes")
    ttfs = [a for a in os.listdir(carpeta_f) if a.lower().endswith((".ttf", ".otf"))] if os.path.isdir(carpeta_f) else []
    if ttfs and not os.path.exists(os.path.join(carpeta_f, "OFL.txt")):
        falla("hay letras en base_lunar/fuentes/ sin su archivo de licencia OFL.txt")
    elif ttfs and "Press Start 2P" not in open(os.path.join(RAIZ, "CREDITOS.md"), encoding="utf-8").read():
        falla("la letra Press Start 2P no está anotada en CREDITOS.md")
    else:
        ok(f"{len(ttfs)} letra(s) con licencia y en los créditos")

    print("6. Nada que no deba ir al repositorio")
    patrones = [r"\.jks", r"\.keystore", r"\.pem", r"config\.php", r"conexion\.php", r"\.env\b",
                r"(?<!wp-content/)uploads/", r"gho_[A-Za-z0-9]{10,}", r"ghp_[A-Za-z0-9]{10,}"]
    # Palabras que NO deben aparecer y que no se escriben aquí porque este archivo es público:
    # se leen de _prohibidos_local.txt (una por renglón), que está en .gitignore y no se sube.
    local = os.path.join(RAIZ, "_prohibidos_local.txt")
    if os.path.exists(local):
        patrones += [re.escape(p.strip()) for p in open(local, encoding="utf-8") if p.strip()]
    prohibidos = re.compile("|".join(patrones), re.I)
    for carpeta in ("base_lunar", "tools"):
        for raiz, _dirs, archivos in os.walk(os.path.join(RAIZ, carpeta)):
            if "__pycache__" in raiz:
                continue
            for a in archivos:
                if not a.endswith((".py", ".md", ".txt", ".json")):
                    continue
                ruta = os.path.join(raiz, a)
                texto = open(ruta, encoding="utf-8", errors="ignore").read()
                if a != "verificar.py" and prohibidos.search(texto):
                    falla(f"{os.path.relpath(ruta, RAIZ)} menciona algo que no va: «{prohibidos.search(texto).group(0)}»")
    ok("revisadas base_lunar/ y tools/")

    print()
    if FALLAS:
        print(f"HAY {len(FALLAS)} FALLAS")
        sys.exit(1)
    print("TODO OK")


if __name__ == "__main__":
    main()
