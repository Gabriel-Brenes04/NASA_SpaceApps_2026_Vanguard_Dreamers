# -*- coding: utf-8 -*-
"""Prueba del balance: juega N misiones con 4 tipos de jugador y cuenta cuántas se ganan.

    python tools/simular_misiones.py            (200 misiones por tipo)
    python tools/simular_misiones.py 500 --json _investigacion/balance.json
    python tools/simular_misiones.py 200 --corta      (la misión corta de 14 días)

Tipos de jugador:
  experto  → siempre la mejor opción y la tarea que más falta hace
  novato   → acierta 6 de cada 10 y escoge la tarea a medias
  azar     → opciones y tareas al azar
  descuidado → siempre una opción equivocada y tareas al azar
Lo que se busca: el experto gana casi siempre, el descuidado casi nunca, y el azar queda en medio.
No usa pygame.
"""
import json
import os
import random
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from game.logica.simulador import Mision  # noqa: E402


def tarea_experta(m):
    ts = m.tareas_disponibles()
    if not ts:
        return None
    e = m.e
    if "estiba" in ts:
        return "estiba"
    if "radiacion" in ts and e.barrido < 0.2 and e.dia <= e.luz and e.energia > 150:
        return "radiacion"
    if "paneles" in ts and e.energia < 250:
        return "paneles"
    if e.animo < 40 and "recreo" in ts:
        return "recreo"
    puntaje = {}
    for r, tid in (("comida", "cosecha"), ("agua", "hielo"), ("o2", "oxigeno")):
        if tid in ts:
            d = e.dias_que_alcanza(r)
            puntaje[tid] = d if d is not None else 999
    if "oxigeno" in puntaje and e.agua < 60:
        puntaje["oxigeno"] += 50
    if not puntaje:
        return "recreo" if "recreo" in ts else ts[0]
    tid = min(puntaje, key=puntaje.get)
    if puntaje[tid] > 60:
        return "recreo" if "recreo" in ts else tid
    return tid


def jugar(semilla, tipo, rng, modo="completa"):
    m = Mision(semilla, modo)
    while not m.fin:
        m.empezar_dia()
        d = m.decision
        if d:
            buenas = [i for i, o in enumerate(d.opciones) if o.correcta]
            malas = [i for i, o in enumerate(d.opciones) if not o.correcta]
            if tipo == "experto" or (tipo == "novato" and rng.random() < 0.6):
                i = buenas[0] if buenas else rng.randrange(len(d.opciones))
            elif tipo == "descuidado" and malas:
                i = rng.choice(malas)
            else:
                i = rng.randrange(len(d.opciones))
            m.elegir(i)
        ts = m.tareas_disponibles()
        if ts:
            if tipo == "experto" or (tipo == "novato" and rng.random() < 0.5):
                tid = tarea_experta(m)
            else:
                tid = rng.choice(ts)
            if tid:
                m.hacer_tarea(tid, 1.0)
        m.cerrar_dia()
    return m


def main():
    args = sys.argv[1:]
    total = int(args[0]) if args and args[0].isdigit() else 200
    salida = args[args.index("--json") + 1] if "--json" in args else None
    modo = "corta" if "--corta" in args else "completa"
    print(f"Misión {modo}:")
    rng = random.Random(2026)
    resultados = {}
    for tipo in ("experto", "novato", "azar", "descuidado"):
        gan = 0
        causas = Counter()
        dias = []
        dosis = []
        finales = Counter()
        curvas = None
        for s in range(total):
            m = jugar(1000 + s, tipo, rng, modo)
            if m.fin == "victoria":
                gan += 1
            else:
                causas[m.causa] += 1
            dias.append(m.e.dia if m.fin == "derrota" else m.total)
            dosis.append(m.e.dosis)
            finales[m.estrellas()] += 1
            if curvas is None:
                curvas = m.historial
        resultados[tipo] = {
            "ganadas": gan, "total": total, "pct": round(100 * gan / total, 1),
            "causas": dict(causas.most_common()), "dia_promedio": round(sum(dias) / total, 1),
            "dosis_promedio": round(sum(dosis) / total, 1), "estrellas": dict(finales),
            "curva_ejemplo": curvas,
        }
        print(f"{tipo:11s} gana {gan:3d}/{total} ({100 * gan / total:5.1f} %)  "
              f"día promedio de fin {sum(dias) / total:4.1f}  dosis {sum(dosis) / total:5.1f} mSv")
        for c, k in causas.most_common(4):
            print(f"              {k:3d} × {c}")
    if salida:
        os.makedirs(os.path.dirname(salida) or ".", exist_ok=True)
        with open(salida, "w", encoding="utf-8") as f:
            json.dump(resultados, f, ensure_ascii=False, indent=1)
        print("guardado:", salida)


if __name__ == "__main__":
    main()
