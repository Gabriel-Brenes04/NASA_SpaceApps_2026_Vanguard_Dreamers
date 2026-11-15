# -*- coding: utf-8 -*-
"""Los datos curiosos de los botones «?» del juego.

Python puro (sin pygame). Cada ayuda tiene un título y una lista de renglones de dos tipos:
  · "juego": cómo funciona esa parte del juego (no es un dato real, es una regla nuestra);
  · "dato" : un dato real, con el nombre de su fuente. Las fuentes son los recursos del reto
             (NASA APOD, DONKI, RadLab/OSDR, CSA); si alguna vez se usa otra, se dice en `fuente`.

    ayuda("radiacion")  →  {"titulo": ..., "items": [{"tipo", "texto", "fuente", "url"}, ...]}
Claves: "apod" (menú), "recursos" (panel central) y una por cada tarea del día.
Todo se pide con t(clave, español) para que salga en los dos idiomas.
"""
from ..assets.textos import t

_CSA_COMER = "https://www.asc-csa.gc.ca/eng/astronauts/living-in-space/eating-in-space.asp"
_CSA_RELAJAR = "https://www.asc-csa.gc.ca/eng/astronauts/living-in-space/relaxing-in-space.asp"
_CSA_EJERCICIO = "https://www.asc-csa.gc.ca/eng/astronauts/living-in-space/physical-activity-in-space.asp"
_CSA_COMIDA_LUNA = "https://www.asc-csa.gc.ca/eng/youth-educators/toolkits/food-production/"
_RADLAB_API = "https://visualization.osdr.nasa.gov/radlab/gui/data-api/"
_RADLAB_VERSIONES = "https://visualization.osdr.nasa.gov/radlab/kb/Release_history"
_DONKI = "https://ccmc.gsfc.nasa.gov/tools/DONKI/"
_APOD = "https://apod.nasa.gov/"


def _j(texto):
    return {"tipo": "juego", "texto": texto, "fuente": "", "url": ""}


def _d(texto, fuente, url=""):
    return {"tipo": "dato", "texto": texto, "fuente": fuente, "url": url}


def ayuda(clave, extra=None):
    """Devuelve la ayuda de `clave` en el idioma actual. `extra` = renglones de dato ya armados
    (por ejemplo, la imagen del día que se está viendo) que se ponen primero."""
    f = _AYUDAS.get(clave)
    if f is None:
        return {"titulo": "", "items": []}
    titulo, items = f()
    return {"titulo": titulo, "items": list(extra or []) + items}


def _apod():
    return t("ayu.apod.tit", "La imagen del día de la NASA"), [
        _d(t("ayu.apod.1", "Cada día la NASA publica una imagen distinta del universo con una explicación escrita "
                           "por un astrónomo profesional. Se llama APOD, por Astronomy Picture of the Day. Las "
                           "fotos que cambian de fondo en este menú vienen de ahí."),
           "NASA APOD", _APOD),
        _d(t("ayu.apod.2", "La primera APOD salió el 16 de junio de 1995. La publican la NASA y la Universidad "
                           "Tecnológica de Michigan."), "NASA APOD", _APOD),
        _d(t("ayu.apod.3", "Una APOD no siempre es una foto normal: puede ser una imagen en falso color de luz "
                           "que nuestros ojos no ven, un video, una animación o un dibujo hecho por un artista."),
           "NASA APOD", _APOD),
    ]


def _recursos():
    return t("ayu.rec.tit", "Manejar los recursos en el espacio"), [
        _d(t("ayu.rec.1", "Un astronauta come entre 1 900 y 3 200 calorías al día, según su peso y lo que necesite "
                          "su cuerpo. Los nutricionistas revisan lo que come cada uno y recomiendan cambios."),
           "CSA · Eating in space", _CSA_COMER),
        _d(t("ayu.rec.2", "La Estación Espacial recicla su agua: la recupera de la orina, del sudor, del vapor del "
                          "aliento y del agua de lavado. Aquí el reciclador hace lo mismo."),
           "CSA · Eating in space", _CSA_COMER),
        _d(t("ayu.rec.3", "Para las misiones largas a la Luna del programa Artemis, los astronautas tendrán que "
                          "cultivar comida, porque no pueden llevar toda la que necesitan."),
           "CSA · Eating in space", _CSA_COMER),
        _d(t("ayu.rec.4", "A la Estación llegan de vez en cuando naves de carga con comida fresca, y los equipos en "
                          "la Tierra a veces agregan unas frutas y verduras frescas."),
           "CSA · Eating in space", _CSA_COMER),
        _d(t("ayu.rec.5", "Los estudios de psicología relacionan la variedad, la calidad y la cantidad de la comida "
                          "con el rendimiento y el bienestar de la tripulación. Por eso, en el juego, racionar "
                          "baja el ánimo."),
           "CSA · Eating in space", _CSA_COMER),
    ]


def _cosecha():
    return t("ayu.cosecha.tit", "Cosecha en el invernadero"), [
        _j(t("ayu.cosecha.j", "Cosechás lo que creció en el invernadero: +5 kg de comida. Solo se puede si el "
                              "invernadero está encendido (gasta 3 kW). Las plantas también devuelven un poco "
                              "de oxígeno.")),
        _d(t("ayu.cosecha.1", "El astronauta canadiense David Saint-Jacques revisó plantas que crecían en la "
                              "Estación para un experimento de botánica espacial llamado Veg-04A."),
           "CSA · Food production", _CSA_COMIDA_LUNA),
    ]


def _oxigeno():
    return t("ayu.oxigeno.tit", "Generador de oxígeno"), [
        _j(t("ayu.oxigeno.j", "Revisás el generador: hace 4 kg extra de oxígeno y gasta 4,5 L de agua. Si el agua "
                              "está justa, no conviene.")),
        _j(t("ayu.oxigeno.1", "El generador parte el agua con electricidad: 2 H₂O → 2 H₂ + O₂. De 36 g de agua "
                              "salen 32 g de oxígeno, así que cada kg de O₂ cuesta 1,125 kg de agua.")),
        _d(t("ayu.oxigeno.2", "La Estación recicla el agua de la orina, el sudor y el aliento para volver a "
                              "usarla. Aquí pasa igual: el generador gasta agua, así que cuidarla es cuidar "
                              "el aire."),
           "CSA · Eating in space", _CSA_COMER),
    ]


def _radiacion():
    return t("ayu.rad.tit", "Barrido de radiación"), [
        _d(t("ayu.rad.1", "RadLab, la base de datos de radiación del OSDR de la NASA, guarda lo que miden "
                          "instrumentos reales. Su medida principal es la dosis absorbida por hora (µGy/h) y, "
                          "cuando se puede, el equivalente de dosis por hora (µSv/h)."),
           "NASA OSDR · RadLab", _RADLAB_API),
        _d(t("ayu.rad.2", "Liulin-5, ALTEA y Timepix son instrumentos reales. El Liulin-5 anota una medición cada "
                          "20 segundos cerca de la Anomalía del Atlántico Sur y cada 90 segundos en el resto de "
                          "la órbita."),
           "NASA OSDR · RadLab", _RADLAB_VERSIONES),
        _d(t("ayu.rad.3", "RadLab no tiene solo la Estación: guarda mediciones del módulo Chang'e 4 sobre la Luna, "
                          "de la sonda LRO en órbita lunar y del rover Curiosity en Marte."),
           "NASA OSDR · RadLab", _RADLAB_VERSIONES),
    ]


def _hielo():
    return t("ayu.hielo.tit", "Traer hielo del cráter"), [
        _j(t("ayu.hielo.j", "Salís con el rover a un cráter y traés hielo: +15 L de agua. Derretirlo gasta 5 kWh "
                            "y la salida suma un poquito de radiación.")),
        _d(t("ayu.hielo.1", "En 2018 el instrumento M3 de la NASA confirmó hielo de agua en la superficie de varias "
                            "zonas de la Luna que están siempre en sombra."),
           t("ayu.hielo.f", "NASA Science · Moon Water and Ices"),
           "https://science.nasa.gov/moon/moon-water-and-ices/"),
        _d(t("ayu.hielo.2", "En 2009 la misión LCROSS de la NASA confirmó hielo de agua en los polos de la Luna."),
           t("ayu.hielo.f2", "NASA Ames · LCROSS"),
           "https://www.nasa.gov/centers/ames/news/releases/2010/10-89AR.html"),
    ]


def _recreo():
    return t("ayu.recreo.tit", "Recreo de la tripulación"), [
        _j(t("ayu.recreo.j", "La tripulación descansa: +12 de ánimo. Con el ánimo por debajo de 30, la tripulación "
                             "rinde menos en todo.")),
        _d(t("ayu.recreo.1", "Muchos astronautas dicen que su actividad favorita es mirar la Tierra por la ventana. "
                             "La Estación le da 16 vueltas al planeta cada día, así que la vista cambia todo "
                             "el tiempo."), "CSA · Relaxing in space", _CSA_RELAJAR),
        _d(t("ayu.recreo.2", "El internet de la Estación es muy lento y solo se usa unas pocas veces al día. Las "
                             "familias mandan paquetes con dulces, libros, fotos y cartas."),
           "CSA · Relaxing in space", _CSA_RELAJAR),
        _d(t("ayu.recreo.3", "En misiones largas los astronautas hacen unas 2 horas de ejercicio al día. En el "
                             "espacio se pierde en promedio un 1 % de la densidad de los huesos por mes."),
           "CSA · Physical activity in space", _CSA_EJERCICIO),
    ]


def _estiba():
    return t("ayu.estiba.tit", "Estiba del cohete de carga"), [
        _j(t("ayu.estiba.j", "Cuando llega un cohete de carga podés acomodarlo bien: con una buena estiba caben "
                             "hasta un 15 % más de lo que llegó. Solo hay estiba el día que llega la carga.")),
        _d(t("ayu.estiba.1", "En la Estación todo flota, así que cada paquete de comida lleva un punto de velcro "
                             "para pegarlo a las superficies."), "CSA · Eating in space", _CSA_COMER),
        _d(t("ayu.estiba.2", "Los envases usados no se tiran al espacio: vuelven a la Tierra con los astronautas o "
                             "se queman en la atmósfera dentro de una nave de carga."),
           "CSA · Eating in space", _CSA_COMER),
        _d(t("ayu.estiba.3", "El equipo de ejercicio de la Estación pesa más de 1 800 kg y ocupa casi 80 m². El "
                             "volante de ejercicio de la cápsula Orion pesa solo 14 kg: en un viaje largo, cada "
                             "kilo cuenta."), "CSA · Physical activity in space", _CSA_EJERCICIO),
    ]


def _paneles():
    return t("ayu.paneles.tit", "Alinear los paneles"), [
        _j(t("ayu.paneles.j", "Alineás los paneles con el Sol: +60 kWh de energía. Solo se puede "
                              "de día. Cuenta del juego: 40 m² × 1 361 W por m² × 20 % ≈ 10,9 kW.")),
        _d(t("ayu.paneles.1", "El Sol también molesta a las naves. DONKI anota fulguraciones, partículas solares, "
                              "eyecciones de masa coronal, tormentas geomagnéticas y aumentos en los cinturones "
                              "de radiación."), "NASA CCMC DONKI", _DONKI),
    ]


_AYUDAS = {"apod": _apod, "recursos": _recursos, "cosecha": _cosecha, "oxigeno": _oxigeno,
           "radiacion": _radiacion, "hielo": _hielo, "recreo": _recreo, "estiba": _estiba, "paneles": _paneles}
