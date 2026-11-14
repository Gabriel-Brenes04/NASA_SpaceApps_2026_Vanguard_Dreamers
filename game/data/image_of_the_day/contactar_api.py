"""
    NASA space apps challenge 2026
    Vanguard Dreamers

    contactar_api.py
    Este archivo contacta a la api apod-basic de la nasa para traer imagenes de la pagina image of
    the day. Esto para incorporar imagenes reales del espacio.
"""

import json, sys, datetime, pathlib, requests, os
from dotenv import load_dotenv
load_dotenv()

API = "https://science.nasa.gov/wp-json/wp/v2/apod-basic"
KEY = os.environ.get("NASA_API_KEY", "DEMO_KEY")
OUT = pathlib.Path(__file__).resolve().parents[2] / "assets" / "imagenes_fondo" / "titulo"
if not OUT.is_dir():
    sys.exit(f"No existe la carpeta: {OUT}")

def limpio(html):
    import re
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", html or "")).strip()

#traemos las imagenes de varios dias
def traer(cantidad=5):
    r = requests.get(API, params={"count": cantidad, "api_key": KEY}, timeout=60)
    r.raise_for_status()
    datos = r.json()
    return datos if isinstance(datos, list) else [datos]

#se buscan imagenes con palabras clave que se adaptan a nuestro juego
def buscar(cantidad=5):
    hallados = []
    fechas = set()
    try:
        lote = traer(cantidad)
        for d in lote:
            fecha = d.get("date")
            if (fecha and fecha not in fechas and d.get("media_type") == "image"
                    and (d.get("hdurl") or d.get("url"))):
                fechas.add(fecha)
                hallados.append(d)
    except (requests.RequestException, ValueError) as e:
        print("falló la búsqueda:", e)
    return hallados

#se hacen los requests
def bajar(imagenes):
    guardadas = 0
    for d in imagenes:
        fecha = d["date"]
        existentes = list(OUT.glob(f"{fecha}.jpg")) + list(OUT.glob(f"{fecha}.png"))
        ficha_ruta = OUT / f"{fecha}.json"
        if any(r.exists() and r.stat().st_size > 0 for r in existentes) and ficha_ruta.exists():
            guardadas += 1
            continue
        try:
            imagen_url = d.get("hdurl") or d.get("url")
            respuesta = requests.get(imagen_url, timeout=120)
            respuesta.raise_for_status()
            contenido = respuesta.content
            tipo = respuesta.headers.get("Content-Type", "").lower()
            if "jpeg" in tipo or "jpg" in tipo or contenido.startswith(b"\xff\xd8\xff"):
                extension = ".jpg"
            elif "png" in tipo or contenido.startswith(b"\x89PNG\r\n\x1a\n"):
                extension = ".png"
            else:
                print("formato no compatible:", fecha)
                continue
            ruta = OUT / f"{fecha}{extension}"
            ruta.write_bytes(contenido)
            ficha = {"titulo": d.get("title", ""), "credito": limpio(d.get("credit") or d.get("copyright")), "pagina": d.get("permalink", ""),
                     "fecha_imagen": fecha, "fecha_consulta": datetime.date.today().isoformat(),
                     "fuente": "NASA APOD", "en_vivo": False}
            ficha_ruta.write_text(json.dumps(ficha, ensure_ascii=False, indent=2), encoding="utf-8")
            print("guardada:", ruta)
            guardadas += 1
        except (requests.RequestException, KeyError, OSError, ValueError) as e:
            print("falló", fecha, e)
    return guardadas

def main():
    imagenes = buscar(5)
    if len(imagenes) != 5:
        print(f"La API devolvió {len(imagenes)} imágenes válidas de las 5 solicitadas.")
    if not imagenes:
        print("No se encontraron imágenes disponibles.")
        return
    guardadas = bajar(imagenes)
    print(f"FLUJO COMPLETO: {guardadas}/5 imágenes disponibles.")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        main()
    elif sys.argv[1] == "buscar":
        imagenes = buscar(5)
        print(f"{len(imagenes)} imágenes encontradas.")
    else:
        bajar([{"date": fecha, "hdurl": fecha} for fecha in sys.argv[1:]])
