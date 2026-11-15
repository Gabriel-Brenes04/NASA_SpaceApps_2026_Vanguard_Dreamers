# -*- coding: utf-8 -*-
"""Los textos del juego: sacarlos para traducir y revisar las traducciones.

    python tools/textos.py sacar  _traduccion/textos_es.json   (todas las claves con su español)
    python tools/textos.py revisar                               (¿falta alguna en inglés? ¿llaves iguales?)

Busca en game/ cada llamada t("clave", "texto en español", ...). Las claves armadas con «+»
(por ejemplo t("cie.apagon." + k, ...)) se listan aparte con sus valores posibles.
"""
import ast
import json
import os
import re
import string
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))          # la carpeta del paquete «game»
sys.path.insert(0, os.path.dirname(RAIZ))


def _cadena(nodo):
    if isinstance(nodo, ast.Constant) and isinstance(nodo.value, str):
        return nodo.value
    return None


def sacar():
    claves, dinamicas = {}, []
    for raiz, _d, archivos in os.walk(RAIZ):
        if "__pycache__" in raiz:
            continue
        for a in sorted(archivos):
            if not a.endswith(".py") or a == "textos_en.py":
                continue
            ruta = os.path.join(raiz, a)
            arbol = ast.parse(open(ruta, encoding="utf-8").read())
            for nodo in ast.walk(arbol):
                if (isinstance(nodo, ast.Call) and isinstance(nodo.func, ast.Name) and nodo.func.id == "t"
                        and len(nodo.args) >= 2):
                    clave, es = _cadena(nodo.args[0]), _cadena(nodo.args[1])
                    lugar = f"{os.path.relpath(ruta, RAIZ)}:{nodo.lineno}"
                    if clave is not None and es is not None:
                        claves.setdefault(clave, {"es": es, "donde": lugar})
                    else:
                        dinamicas.append(lugar)
    # claves armadas a mano (las que el código arma con «+» o con un número)
    from game.data import datos_nasa as N
    for i, (dato, fuente, _url, _origen) in enumerate(N.FUENTES):
        claves.setdefault(f"fuente.{i}", {"es": dato, "donde": "datos_nasa.FUENTES"})
        claves.setdefault(f"fuente.{i}.f", {"es": fuente, "donde": "datos_nasa.FUENTES"})
    for k, es in (("cie.apagon.invernadero", "¡Apagón! Se apagó solo el {s} para salvar la batería."),
                  ("cie.apagon.generador", "¡Apagón! Se apagó solo el {s} para salvar la batería."),
                  ("sis.invernadero", "invernadero"), ("sis.generador", "generador de O₂"),
                  ("tor.moderada", "moderada"), ("tor.fuerte", "fuerte"),
                  ("car.dur.comida", "comida {d} d"), ("car.dur.agua", "agua {d} d"), ("car.dur.o2", "O₂ {d} d")):
        claves.setdefault(k, {"es": es, "donde": "clave armada"})
    return claves, dinamicas


def llaves(texto):
    """Los {nombre} que se llenan con valores (sin contar las fracciones {{a|b}})."""
    return sorted(n for _l, n, _f, _c in string.Formatter().parse(texto) if n)


def revisar():
    from game.assets.textos_en import EN
    claves, _ = sacar()
    faltan = [k for k in claves if k not in EN]
    malas = []
    for k, v in claves.items():
        if k in EN:
            try:
                if llaves(v["es"]) != llaves(EN[k]):
                    malas.append(f"{k}: llaves {llaves(v['es'])} en español y {llaves(EN[k])} en inglés")
                if v["es"].count("{{") != EN[k].count("{{"):
                    malas.append(f"{k}: distinto número de fracciones {{{{a|b}}}}")
            except ValueError as e:
                malas.append(f"{k}: plantilla rota ({e})")
    sobran = [k for k in EN if k not in claves]
    return claves, faltan, malas, sobran


if __name__ == "__main__":
    accion = sys.argv[1] if len(sys.argv) > 1 else "revisar"
    if accion == "sacar":
        salida = sys.argv[2] if len(sys.argv) > 2 else os.path.join(RAIZ, "_traduccion", "textos_es.json")
        claves, dinamicas = sacar()
        os.makedirs(os.path.dirname(salida), exist_ok=True)
        json.dump(claves, open(salida, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"{len(claves)} textos guardados en {salida}")
        if dinamicas:
            print("claves armadas en el código (revisar que estén en la lista de arriba):", ", ".join(dinamicas))
    else:
        claves, faltan, malas, sobran = revisar()
        print(f"{len(claves)} textos · faltan en inglés: {len(faltan)} · con llaves distintas: {len(malas)} · "
              f"sobran: {len(sobran)}")
        for x in faltan[:30]:
            print("  falta:", x)
        for x in malas:
            print("  mal:", x)
        sys.exit(1 if faltan or malas else 0)
