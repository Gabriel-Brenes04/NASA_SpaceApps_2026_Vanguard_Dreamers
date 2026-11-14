# -*- coding: utf-8 -*-
"""Las decisiones de la misión: problemas de matemática reales con consecuencias.

Cada decisión se ARMA con el estado de la base en ese momento (los números cambian de una
partida a otra) y trae: enunciado, 2 a 4 opciones con su efecto, cuál es la mejor según los
números, y la explicación con la cuenta. Python puro (sin pygame).

Ideas del equipo integradas: el muro de agua alrededor del dormitorio (arquitecto), el
reactor que se enciende al caer la noche, y el ángulo del panel solar.
"""
from ..data import datos_nasa as N
from . import simulador as S
from ..assets.textos import t, n

# ══ Calendario: qué decisión toca cada día ════════════════════════════════════════════════
UNICAS = ("temperatura", "llamada", "angulo")
REPETIBLES = {"racion": 3, "electrolisis": 2, "hielo": 3, "gravedad": 2, "oxigeno": 3}


def armar_calendario(rng, e):
    L, T = e.luz, e.total          # días de sol y días de la misión
    plan = {1: "arquitecto", 2: "panel", L: "noche"}
    if L >= 10:                    # misión completa: 14 de sol y 14 de noche
        t1 = rng.randint(4, 8)
        t2 = rng.randint(10, L - 1)
        rangos = (("micrometeorito", (3, L - 2)), ("reabastecimiento", (L + 2, L + 5)),
                  ("reciclador", (L + 3, T - 4)), ("enfermo", (L + 4, T - 2)))
    else:                          # misión corta: 7 de sol y 7 de noche (todo más seguido)
        t2 = rng.randint(5, L - 1)
        t1 = rng.randint(3, t2 - 2)
        rangos = (("micrometeorito", (3, L - 1)), ("reabastecimiento", (L + 1, L + 3)),
                  ("reciclador", (L + 2, T - 2)), ("enfermo", (L + 3, T - 1)))
    plan[t1] = "tormenta:moderada"
    plan[t2] = "tormenta:fuerte"
    plan[t2 - 1] = "mancha"

    def libre(desde, hasta):
        dias = [d for d in range(desde, hasta + 1) if d not in plan]
        return rng.choice(dias) if dias else None

    for ident, (a, b) in rangos:
        d = libre(a, b) or libre(3, T - 1)
        if d:
            plan[d] = ident
    return plan


def pronostico(plan, dia, e):
    """Lo que se sabe de mañana (idea del equipo: ver venir el evento para prepararse)."""
    p = plan.get(dia, "")
    if p == "noche" or dia == e.luz + 1:
        return t("pro.noche", "Mañana cae la noche lunar: sin sol y a −173 °C.")
    if p == "reabastecimiento":
        return t("pro.carga", "Mañana llega un cohete de carga.")
    if p.startswith("tormenta") and plan.get(dia - 1) == "mancha":
        return t("pro.tormenta", "Alerta del Sol: posible fulguración mañana.")
    return None


def elegir_rutina(m):
    """Día sin evento: una decisión de rutina que tenga sentido hoy (o ninguna)."""
    e = m.e
    conteo = getattr(m, "conteo", None)
    if conteo is None:
        conteo = m.conteo = {}
    if m.rng.random() < 0.15:
        return None                       # día tranquilo
    quedan = e.total - e.dia + 1
    cand = []
    for ident in list(UNICAS) + list(REPETIBLES):
        usos = conteo.get(ident, 0)
        if ident in UNICAS and usos:
            continue
        if ident in REPETIBLES and usos >= REPETIBLES[ident]:
            continue
        if ident == "temperatura" and not (3 <= e.dia <= e.luz - 1):
            continue
        if ident in ("angulo", "electrolisis") and not e.de_dia():
            continue
        if ident == "angulo" and e.dia > e.luz - 2:
            continue
        if ident == "oxigeno" and e.de_dia():
            continue
        if ident == "racion":
            d = e.dias_que_alcanza("comida")
            if e.dia < max(3, e.total // 5) or (e.racion == 1 and (d is None or d > quedan + 4)):
                continue
        if ident == "electrolisis" and e.o2 > 50:
            continue
        cand.append(ident)
    if not cand:
        return None
    m.rng.shuffle(cand)
    cand.sort(key=lambda i: conteo.get(i, 0))
    ident = cand[0]
    conteo[ident] = conteo.get(ident, 0) + 1
    return ident


def construir(ident, m):
    nombre, _, arg = ident.partition(":")
    f = globals()["_d_" + nombre]
    return f(m, arg) if arg else f(m)


def _quedan(e):
    return e.total - e.dia + 1


# ══ 1 · Arquitecto del hábitat (idea del equipo: el muro de agua) ═════════════════════════
def _d_arquitecto(m):
    def ef(f, animo=0):
        def _(e):
            e.refugio = f
            e.refugio_elegido = True
            e.animo = min(100, e.animo + animo)
            return [t("arq.ok", "El refugio deja pasar {p} % de una tormenta.", p=n(f * 100, 0))]
        return _
    return S.Decision(
        "arquitecto",
        t("arq.tit", "Arquitecto del hábitat"),
        t("arq.enun", "Alrededor del dormitorio caben 4 módulos. Si llega una tormenta solar, la "
                      "tripulación se encierra ahí. El agua y las plantas tienen mucho hidrógeno, y el "
                      "hidrógeno frena las partículas del Sol (NASA). En el juego, detrás del agua pasa "
                      "{{3|10}} de la radiación, detrás de las plantas {{6|10}} y detrás de las "
                      "baterías pasa toda. ¿Qué ponés alrededor del dormitorio?"),
        [S.Opcion(t("arq.a", "Los tanques de agua"), ef(0.3), True),
         S.Opcion(t("arq.b", "El invernadero"), ef(0.6, 5)),
         S.Opcion(t("arq.c", "Las baterías"), ef(1.0))],
        t("arq.exp", "Una tormenta fuerte da 200 mSv. Detrás del agua: 200 × {{3|10}} = 60 mSv. Detrás "
                     "de las plantas: 200 × {{6|10}} = 120 mSv. Detrás de las baterías: 200 mSv. El límite "
                     "de la NASA es 250 mSv: solo el agua deja margen para una segunda tormenta. La NASA "
                     "estudió una «pared de agua» de unos 10 cm alrededor del cuarto de la tripulación."),
        datos=[t("arq.d1", "Tormenta fuerte: 200 mSv"), t("arq.d2", "Límite de la NASA: 250 mSv")])


# ══ 2 · Cuánto da el panel solar ══════════════════════════════════════════════════════════
def _d_panel(m):
    kw = S.PANEL_KW

    def a(e):
        e.sistemas.update(generador=True, reciclador=True, invernadero=True)
        return [t("pan.a", "Todo funciona y sobra un poquito para la batería.")]

    def b(e):
        perdida = (S.CARGAS_KW["base_dia"] + 6.5 + 2 - kw) * 24
        e.energia -= perdida * 2
        e.animo = min(100, e.animo + 2)
        return [t("pan.b", "El taller quedó tibio, pero la batería perdió {k} kWh en dos días.",
                  k=n(perdida * 2, 0))]

    def c(e):
        e.o2 -= S.GEN_O2_KG
        e.comida -= S.INV_COMIDA_KG
        return [t("pan.c", "Hoy no se hizo oxígeno ni comida, y la batería ya estaba casi llena: "
                           "la energía que sobró se perdió.")]
    return S.Decision(
        "panel",
        t("pan.tit", "¿Cuánta energía da el panel?"),
        t("pan.enun", "El panel solar mide 40 m². El Sol da 1361 W por cada m² (NASA) y el panel "
                      "convierte el 20 % en electricidad. El soporte vital ya usa 4 kW. ¿Qué más encendés?"),
        [S.Opcion(t("pan.oa", "Generador de O₂, reciclador e invernadero"), a, True),
         S.Opcion(t("pan.ob", "Todo eso y también el calentador del taller"), b),
         S.Opcion(t("pan.oc", "Solo el reciclador, para ahorrar"), c)],
        t("pan.exp", "40 × 1361 × 0,20 = 10 888 W ≈ 10,9 kW. Soporte vital + generador + reciclador + "
                     "invernadero = 4 + 2,5 + 1 + 3 = 10,5 kW: cabe. Con el calentador (2 kW) serían "
                     "12,5 kW: no cabe. Apagar cosas no sirve si la batería ya está llena."),
        datos=[t("pan.d1", "Generador de O₂: 2,5 kW · Reciclador: 1 kW"),
               t("pan.d2", "Invernadero: 3 kW · Calentador del taller: 2 kW")])


# ══ 3 · Cae la noche: el reactor da 10 kW (idea del equipo) ═══════════════════════════════
def _d_noche(m):
    e = m.e
    noche = e.dias_de_noche()
    necesita_comida = noche * e.consumo_comida()
    necesita_o2 = noche * (e.consumo_o2() - S.INV_O2_KG)
    perdida_agua = e.agua_bruta() * (1 - N.RECICLAJE_AGUA)
    agua_b = noche * (perdida_agua + S.GEN_AGUA_L)      # sin invernadero: el generador parte agua
    agua_c = noche * (perdida_agua + S.INV_AGUA_L)      # sin generador: solo el invernadero gasta
    razon_b = min(e.comida / necesita_comida, e.agua / agua_b)
    razon_c = min(e.o2 / necesita_o2, e.agua / agua_c)
    ok_b = razon_b >= 1
    ok_c = razon_c >= 1
    if not ok_b and not ok_c:
        ok_b = razon_b >= razon_c
        ok_c = not ok_b
    dias_bat = e.energia / 60
    ok_a = dias_bat >= noche          # (con la batería de este juego nunca alcanza, pero se calcula)

    def pon(**s):
        def _(e):
            e.sistemas.update(s)
            return []
        return _
    return S.Decision(
        "noche",
        t("noc.tit", "Mañana cae la noche lunar"),
        t("noc.enun", "La noche lunar dura unas dos semanas y afuera baja a −173 °C (NASA). A la misión le "
                      "quedan {n} días de oscuridad. El reactor da 10 kW, como el Kilopower de la NASA. De "
                      "noche el soporte vital con calefacción usa 6 kW. Con todo encendido serían "
                      "6 + 2,5 + 1 + 3 = 12,5 kW. ¿Qué hacés?", n=noche),
        [S.Opcion(t("noc.a", "Dejar todo encendido"), pon(generador=True, reciclador=True, invernadero=True), ok_a),
         S.Opcion(t("noc.b", "Apagar el invernadero (3 kW)"), pon(invernadero=False, generador=True), ok_b),
         S.Opcion(t("noc.c", "Apagar el generador de O₂ (2,5 kW)"), pon(generador=False, invernadero=True), ok_c),
         S.Opcion(t("noc.d", "Apagar el reciclador de agua (1 kW)"), pon(reciclador=False))],
        t("noc.exp", "Todo encendido: 12,5 kW y el reactor da 10. La batería ({b} kWh) perdería 2,5 × 24 = "
                     "60 kWh por día: dura {d} días, y faltan {n}. Sin el reciclador: 11,5 kW, no cabe, y se "
                     "perderían 17,9 L de agua por día. Sin el invernadero (9,5 kW) hay que tener "
                     "{n} × {c} = {nc} kg de comida (tenés {tc}) y, como el generador parte agua, "
                     "{ab} L de agua. Sin el generador (10 kW) hay que tener {n} × ({o} − 0,25) = {no} kg de "
                     "O₂ (tenés {to}) y solo {ac} L de agua. Tenés {ta} L.",
          n=noche, b=n(e.energia, 0), d=n(dias_bat), c=n(e.consumo_comida(), 2), nc=n(necesita_comida),
          tc=n(e.comida), ab=n(agua_b, 0), o=n(e.consumo_o2(), 2), no=n(necesita_o2), to=n(e.o2),
          ac=n(agua_c, 0), ta=n(e.agua)),
        datos=[t("noc.d1", "Batería: {b} kWh", b=n(e.energia, 0)),
               t("noc.d2", "Comida: {c} kg · Agua: {a} L · O₂: {o} kg", c=n(e.comida), a=n(e.agua), o=n(e.o2))])


# ══ 4 · Tormenta solar: ¿llegan al refugio? ══════════════════════════════════════════════
def _d_tormenta(m, nivel):
    e = m.e
    msv = S.TORMENTA_MSV[nivel]
    d = m.rng.choice((600, 900, 1200, 1500, 1800, 2100))
    v = m.rng.choice((1.0, 1.2, 1.5))
    aviso = m.rng.choice((15, 20, 25, 30))
    seg = d / v
    minutos = seg / 60
    llegan = minutos <= aviso
    adentro = msv * e.factor_habitat() * e.refugio

    def recibir(afuera, animo=0):
        def _(e):
            dosis = max(afuera, adentro)
            e.dosis += dosis
            e.animo = max(0, e.animo + animo)
            return [t("tor.dosis", "La tripulación recibió {d} mSv. Lleva {tot} de 250.",
                      d=n(dosis), tot=n(e.dosis))]
        return _
    volver = adentro if llegan else 0.5 * msv + 0.5 * adentro
    return S.Decision(
        "tormenta",
        t("tor.tit", "¡Fulguración solar!"),
        t("tor.enun", "Una tormenta {niv}: afuera, sin protección, daría {msv} mSv. Las partículas llegan "
                      "en {a} minutos (la NASA dice que las más rápidas tardan de 15 a 30). Dos tripulantes "
                      "están a {d} m del hábitat y caminan a {v} m/s con el traje. ¿Qué hacen?",
          niv=t("tor." + nivel, nivel), msv=msv, a=aviso, d=n(d, 0), v=n(v)),
        [S.Opcion(t("tor.a", "Volver corriendo al refugio del hábitat"), recibir(volver), llegan),
         S.Opcion(t("tor.b", "Meterse al rover presurizado, que está ahí cerca"), recibir(0.6 * msv, -3),
                  not llegan),
         S.Opcion(t("tor.c", "Seguir trabajando: hay que terminar"), recibir(msv, -8))],
        t("tor.exp", "Tiempo para volver: {{{{{d}|{v}}}}} = {s} s, y {s} ÷ 60 = {mi} min. Las partículas "
                     "llegan en {a} min: {si}. En el hábitat la tormenta da {msv} × {fh} (regolito) × "
                     "{fr} (refugio) = {ad} mSv; en el rover pasa {{{{6|10}}}}: {ro} mSv.",
          d=n(d, 0), v=n(v), s=n(seg, 0), mi=n(minutos), a=aviso,
          si=(t("tor.si", "sí alcanzan") if llegan else t("tor.no", "NO alcanzan")),
          msv=msv, fh=n(e.factor_habitat(), 2), fr=n(e.refugio, 1), ad=n(adentro), ro=n(0.6 * msv, 0)),
        datos=[t("tor.d1", "Límite de la NASA: 250 mSv · Llevan {d}", d=n(e.dosis))], evento=True)


# ══ 5 · Mancha solar: ¿más regolito? ══════════════════════════════════════════════════════
def _d_mancha(m):
    e = m.e
    if e.regolito >= 3:
        return None
    f1, f2 = e.factor_habitat(), max(0.25, 1 - 0.25 * (e.regolito + 1))
    d1, d2 = 200 * f1 * e.refugio, 200 * f2 * e.refugio
    alcanza = e.energia >= 90

    def cubrir(e):
        e.regolito = min(3.0, e.regolito + 1)
        e.energia -= 40
        e.sin_tarea = True
        return [t("man.a", "Ya hay {m} m de regolito sobre el hábitat.", m=n(e.regolito))]
    return S.Decision(
        "mancha",
        t("man.tit", "Una mancha solar muy activa"),
        t("man.enun", "Los observatorios ven una mancha solar muy activa: puede venir una tormenta fuerte. "
                      "Hoy podés cubrir el hábitat con 1 m más de regolito. Cuesta 40 kWh de la excavadora y "
                      "el trabajo de todo el día. Ahora tiene {m} m. ¿Lo cubren?", m=n(e.regolito)),
        [S.Opcion(t("man.oa", "Sí, cubrir con 1 m más"), cubrir, alcanza),
         S.Opcion(t("man.ob", "No, seguir con el trabajo normal"), lambda e: [], not alcanza)],
        t("man.exp", "En el refugio, una tormenta fuerte daría 200 × {f1} × {r} = {d1} mSv. Con un metro "
                     "más: 200 × {f2} × {r} = {d2} mSv. Llevan {dos} mSv de 250. Los 40 kWh son lo que "
                     "gasta la base en unas 4 horas: {vale}.",
          f1=n(f1, 2), f2=n(f2, 2), r=n(e.refugio, 1), d1=n(d1), d2=n(d2), dos=n(e.dosis),
          vale=(t("man.vale", "vale la pena") if alcanza else t("man.novale", "hoy la batería no alcanza")))
    )


# ══ 6 · Se avería el reciclador de agua ═══════════════════════════════════════════════════
def _d_reciclador(m):
    e = m.e
    bruta = e.agua_bruta()
    neta = bruta * (1 - N.RECICLAJE_AGUA)

    def reparar(e):
        e.energia -= 30
        e.sin_tarea = True
        return [t("rec.a", "Reparado: el reciclador vuelve a recuperar el 98 % del agua.")]

    def esperar(e):
        e.reciclador_roto = 3
        return [t("rec.b", "Durante 3 días se pierde casi toda el agua que se usa.")]

    def toallitas(e):
        e.reciclador_roto = 3
        e.agua += 3 * 1.08 * e.tripulantes
        e.animo = max(0, e.animo - 6)
        return [t("rec.c", "Sin ducha se ahorra un poco de agua, pero la tripulación está de mal humor.")]
    return S.Decision(
        "reciclador",
        t("rec.tit", "¡Se averió el reciclador de agua!"),
        t("rec.enun", "Sin el reciclador, la tripulación gasta 4 × 4,48 = {b} L de agua por día (NASA). Con "
                      "él, la base recupera el 98 % como la Estación Espacial y solo se pierden {nt} L. "
                      "El repuesto llega en 3 días. Tenés {a} L.", b=n(bruta, 2), nt=n(neta, 2), a=n(e.agua)),
        [S.Opcion(t("rec.oa", "Repararlo hoy: 30 kWh y el trabajo del día"), reparar, True),
         S.Opcion(t("rec.ob", "Esperar el repuesto"), esperar),
         S.Opcion(t("rec.oc", "Esperar el repuesto y bañarse con toallitas"), toallitas)],
        t("rec.exp", "Esperar 3 días cuesta 3 × ({b} − {nt}) = {p} L de agua. Sin ducha se ahorran "
                     "3 × 4 × 1,08 = 13 L, y aun así se pierden {p2} L. Repararlo cuesta 30 kWh, y la "
                     "energía vuelve con el reactor; el agua aquí no se fabrica.",
          b=n(bruta, 2), nt=n(neta, 2), p=n(3 * (bruta - neta)), p2=n(3 * (bruta - neta) - 13)),
        evento=True)


# ══ 7 · Micrometeorito en el panel ════════════════════════════════════════════════════════
def _d_micrometeorito(m):
    e = m.e
    k = max(0, e.luz + 1 - e.dia)
    vale = k >= 2
    perdida_kw = S.PANEL_KW * 0.25

    def reparar(e):
        e.sin_tarea = True
        e.dosis += 0.1
        return [t("mic.a", "El panel quedó como nuevo.")]

    def dejar(e):
        e.panel_factor *= 0.75
        return [t("mic.b", "El panel sigue dando el 75 %.")]
    return S.Decision(
        "micrometeorito",
        t("mic.tit", "Un micrometeorito perforó el panel"),
        t("mic.enun", "Ahora el panel da solo {{{{3|4}}}} de lo normal. Repararlo es una salida corta, pero se "
                      "pierde el trabajo del día. Quedan {k} días de sol.", k=k),
        [S.Opcion(t("mic.oa", "Repararlo hoy"), reparar, vale),
         S.Opcion(t("mic.ob", "Dejarlo así"), dejar, not vale)],
        t("mic.exp", "Se pierde {{{{1|4}}}} de 10,9 kW ≈ {p} kW. En {k} días de sol: {p} × 24 × {k} = {kwh} kWh. "
                     "{vale}",
          p=n(perdida_kw), k=k, kwh=n(perdida_kw * 24 * k, 0),
          vale=(t("mic.vale", "Es mucho más de lo que rinde un día de trabajo: hay que repararlo.") if vale
                else t("mic.novale", "Ya casi es de noche y el panel no va a servir: mejor no salir."))),
        evento=True)


# ══ 8 · Un tripulante enfermo ═════════════════════════════════════════════════════════════
def _d_enfermo(m):
    e = m.e
    horas = m.rng.choice((8, 6))
    tomas = 24 // horas
    necesita = tomas * 2 * 3
    hay = 20
    alcanza = necesita <= hay

    def tratar(e):
        e.enfermo = 3 if alcanza else 6
        return [t("enf.a1", "Se curó en 3 días.") if alcanza else
                t("enf.a2", "Las tabletas se acabaron antes: tardó 6 días en curarse.")]

    def media(e):
        e.enfermo = 7
        e.animo = max(0, e.animo - 6)
        return [t("enf.b", "Con media dosis la fiebre no bajó: tardó una semana.")]

    def rover(e):
        e.enfermo = 3
        e.energia -= 10
        return [t("enf.c", "El médico de vuelo aprobó usar también el botiquín del rover.")]
    return S.Decision(
        "enfermo",
        t("enf.tit", "Un tripulante tiene fiebre"),
        t("enf.enun", "El médico de vuelo, desde la Tierra, indica 2 tabletas cada {h} horas durante 3 días. "
                      "El botiquín tiene {hay} tabletas. ¿Qué hacen?", h=horas, hay=hay),
        [S.Opcion(t("enf.oa", "Tratarlo con el botiquín"), tratar, alcanza),
         S.Opcion(t("enf.ob", "Darle media dosis para que alcance"), media),
         S.Opcion(t("enf.oc", "Pedir permiso al médico y usar también el botiquín del rover (12 más)"),
                  rover, not alcanza)],
        t("enf.exp", "En un día hay 24 ÷ {h} = {to} tomas. Cada toma son 2 tabletas: {to} × 2 = {pd} por día. "
                     "En 3 días: {pd} × 3 = {ne} tabletas. Hay {hay}: {res} La dosis del médico nunca se "
                     "cambia por cuenta propia.",
          h=horas, to=tomas, pd=tomas * 2, ne=necesita, hay=hay,
          res=(t("enf.si", "alcanzan.") if alcanza else t("enf.no", "no alcanzan."))),
        evento=True)


# ══ 9 · Llega el cohete de carga ══════════════════════════════════════════════════════════
def _d_reabastecimiento(m):
    e = m.e
    gasto = {}
    for r in ("comida", "agua", "o2"):
        d = e.dias_que_alcanza(r)
        gasto[r] = 0.0 if d is None else getattr(e, r) / d      # lo que baja por día, neto
    g, c = round(100 * e.carga_factor), round(50 * e.carga_factor)     # cantidad grande y chica
    combos = [
        (t("car.a", "{g} kg de comida + {c} L de agua", g=g, c=c), {"comida": g, "agua": c, "o2": 0}),
        (t("car.b", "{c} kg de comida + {g} L de agua", g=g, c=c), {"comida": c, "agua": g, "o2": 0}),
        (t("car.c", "{c} kg de comida + {c} L de agua + {c} kg de O₂", c=c), {"comida": c, "agua": c, "o2": c}),
    ]

    def cabe(r, cant):
        return max(0.0, min(cant, S.MAXIMOS[r] - getattr(e, r)))

    def dias(c, r):
        return 999 if gasto[r] <= 0 else (getattr(e, r) + cabe(r, c[r])) / gasto[r]

    def descubierto(c):
        # «lo que primero se acaba manda»: se compara el recurso que dura MENOS; si empatan,
        # el que le sigue. Solo cuenta hasta el fin de la misión; más ya no importa.
        tope = _quedan(e) + 2
        ds = sorted(min(dias(c, r), tope) for r in gasto)
        return tuple(-d for d in ds)
    mejor = min(descubierto(c) for _, c in combos)

    def es_mejor(c):
        return all(abs(a - b) < 0.5 for a, b in zip(descubierto(c), mejor))

    def linea(c):
        return " · ".join(t("car.dur." + r, nom + " {d} d", d=n(dias(c, r), 0))
                          for r, nom in (("comida", "comida"), ("agua", "agua"), ("o2", "O₂"))
                          if gasto[r] > 0)

    def recibir(c):
        def _(e):
            llego = {r: max(0.0, min(v, S.MAXIMOS[r] - getattr(e, r))) for r, v in c.items()}
            for r, v in llego.items():
                setattr(e, r, getattr(e, r) + v)
            e.carga_hoy = llego
            e.animo = min(100, e.animo + 8)
            perdido = sum(c.values()) - sum(llego.values())
            fr = [t("car.ok", "Llegó la carga. La tripulación está feliz.")]
            if perdido > 0.5:
                fr.append(t("car.perdido", "{k} kg no cupieron en los tanques y se perdieron.", k=n(perdido, 0)))
            return fr
        return _
    return S.Decision(
        "reabastecimiento",
        t("car.tit", "Llega un cohete de carga"),
        t("car.enun", "El cohete trae {kg} kg. Al ritmo de hoy, cada día se gastan {gc} kg de comida y {ga} L "
                      "de agua{go}. Ojo: los tanques tienen tope (agua {ta} L, comida {tc} kg, O₂ {to} kg) y "
                      "lo que no cabe se pierde. ¿Qué pedís?",
          kg=g + c, ta=S.MAXIMOS["agua"], tc=S.MAXIMOS["comida"], to=S.MAXIMOS["o2"],
          gc=n(gasto["comida"]), ga=n(gasto["agua"]),
          go=(t("car.go", " y {g} kg de O₂", g=n(gasto["o2"])) if gasto["o2"] > 0 else "")),
        [S.Opcion(txt, recibir(c), es_mejor(c)) for txt, c in combos],
        t("car.exp", "Cuántos días alcanzaría cada cosa después del pedido (contando solo lo que cabe): "
                     "A → {a}. B → {b}. C → {c}. Manda lo que primero se acaba: la mejor opción es la "
                     "que hace durar más al recurso más escaso.",
          a=linea(combos[0][1]), b=linea(combos[1][1]), c=linea(combos[2][1])),
        datos=[t("car.d1", "Tenés: comida {c} kg · agua {a} L · O₂ {o} kg", c=n(e.comida), a=n(e.agua), o=n(e.o2))],
        evento=True)


# ══ 10 · ¿Alcanza el oxígeno sin el generador? (de noche) ═════════════════════════════════
def _d_oxigeno(m):
    e = m.e
    q = _quedan(e)
    neto = e.consumo_o2() - (S.INV_O2_KG if e.sistemas["invernadero"] else 0)
    dias = e.o2 / neto
    alcanza = dias >= q + 1
    encendido = e.sistemas["generador"]

    def pon(v):
        def _(e):
            e.sistemas["generador"] = v
            return []
        return _
    if encendido:
        ops = [S.Opcion(t("oxi.a", "Apagar el generador para ahorrar 2,5 kW"), pon(False), alcanza),
               S.Opcion(t("oxi.b", "Dejarlo encendido"), pon(True), not alcanza)]
        preg = t("oxi.p1", "¿Apagás el generador de O₂?")
    else:
        ops = [S.Opcion(t("oxi.c", "Encenderlo otra vez"), pon(True), not alcanza),
               S.Opcion(t("oxi.d", "Seguir con el generador apagado"), pon(False), alcanza)]
        preg = t("oxi.p2", "El generador de O₂ está apagado. ¿Lo encendés?")
    return S.Decision(
        "oxigeno",
        t("oxi.tit", "Las cuentas del oxígeno"),
        t("oxi.enun", "Tenés {o} kg de O₂. Cada tripulante usa 0,816 kg por día (NASA): 4 × 0,816 = {c} kg, "
                      "y las plantas devuelven {p} kg. Faltan {q} días. {preg}",
          o=n(e.o2), c=n(e.consumo_o2(), 3), p=n(S.INV_O2_KG if e.sistemas["invernadero"] else 0, 2),
          q=q, preg=preg),
        ops,
        t("oxi.exp", "{{{{{o}|{ne}}}}} ≈ {d} días de oxígeno sin el generador, y faltan {q}. {res}",
          o=n(e.o2), ne=n(neto, 2), d=n(dias), q=q,
          res=(t("oxi.si", "Alcanza con margen: se puede apagar.") if alcanza
               else t("oxi.no", "No alcanza: el generador tiene que estar encendido."))))


# ══ 11 · ¿Racionar la comida? ════════════════════════════════════════════════════════════
def _d_racion(m):
    e = m.e
    q = _quedan(e)
    normal = N.COMIDA_PERSONA_DIA * e.tripulantes
    prod = S.INV_COMIDA_KG * e.eficiencia() if e.sistemas["invernadero"] else 0
    necesita = q * (normal - prod)
    alcanza = e.comida >= necesita
    racionando = e.racion < 1

    def pon(v):
        def _(e):
            e.racion = v
            return []
        return _
    if racionando:
        ops = [S.Opcion(t("rac.a", "Volver a comer normal"), pon(1.0), alcanza),
               S.Opcion(t("rac.b", "Seguir racionando al 75 %"), pon(0.75), not alcanza)]
    else:
        ops = [S.Opcion(t("rac.c", "Racionar al 75 % (baja el ánimo)"), pon(0.75), not alcanza),
               S.Opcion(t("rac.d", "Comer normal"), pon(1.0), alcanza)]
    return S.Decision(
        "racion",
        t("rac.tit", "¿Alcanza la comida?"),
        t("rac.enun", "Tenés {c} kg de comida y faltan {q} días. La tripulación come 4 × 1,51 = {no} kg por día "
                      "(NASA) y el invernadero da {p} kg por día.",
          c=n(e.comida), q=q, no=n(normal, 2), p=n(prod)),
        ops,
        t("rac.exp", "Hacen falta {q} × ({no} − {p}) = {ne} kg y tenés {c} kg. {res}",
          q=q, no=n(normal, 2), p=n(prod), ne=n(necesita), c=n(e.comida),
          res=(t("rac.si", "Alcanza: no hace falta racionar.") if alcanza
               else t("rac.no", "No alcanza: hay que racionar o conseguir más comida."))))


# ══ 12 · Electrólisis: oxígeno a cambio de agua ═══════════════════════════════════════════
def _d_electrolisis(m):
    e = m.e
    noche_o2 = e.dias_de_noche() * (e.consumo_o2() - S.INV_O2_KG)   # O₂ para la noche sin generador
    falta_o2 = e.o2 < noche_o2
    sobra_agua = e.agua - 9 > 45
    conviene = falta_o2 and sobra_agua and e.energia >= 60

    def hacer(e):
        e.o2 += 8
        e.agua -= 9
        e.energia -= 20
        return [t("ele.a", "Listo: 8 kg más de O₂ guardados para la noche.")]
    return S.Decision(
        "electrolisis",
        t("ele.tit", "Oxígeno a cambio de agua"),
        t("ele.enun", "La base hace oxígeno partiendo agua con electricidad, como la Estación Espacial: "
                      "2 H₂O → 2 H₂ + O₂. De 36 g de agua salen 32 g de oxígeno. ¿Hacés 8 kg extra de O₂ para "
                      "la noche? Gasta 20 kWh. Tenés {a} L de agua y {o} kg de O₂.", a=n(e.agua), o=n(e.o2)),
        [S.Opcion(t("ele.oa", "Sí, hacer 8 kg de O₂"), hacer, conviene),
         S.Opcion(t("ele.ob", "No, guardar el agua"), lambda e: [], not conviene)],
        t("ele.exp", "Cada kg de O₂ necesita {{{{36|32}}}} = 1,125 kg de agua: 8 × 1,125 = 9 L. Para pasar la "
                     "noche con el generador apagado hacen falta unos {nn} kg de O₂ (tenés {o}). {res}",
          nn=n(noche_o2, 0), o=n(e.o2),
          res=(t("ele.si", "Conviene: falta oxígeno y sobra agua.") if conviene
               else t("ele.no", "No conviene hoy: o ya hay oxígeno o el agua está justa."))))


# ══ 13 · Hielo del cráter: ¿alcanza la batería del rover? ═════════════════════════════════
def _d_hielo(m):
    e = m.e
    cerca = m.rng.choice((4, 5, 6))
    lejos = m.rng.choice((7, 8, 9))
    lleno = e.agua >= 180

    def ir_cerca(e):
        e.agua += 20
        e.energia -= 5
        e.dosis += 0.2
        return [t("hie.a", "Trajeron 20 L de agua del hielo.")]

    def ir_lejos(e):
        e.energia -= 25
        e.animo = max(0, e.animo - 8)
        e.dosis += 0.5
        return [t("hie.b", "El rover se quedó sin batería a mitad de camino. Hubo que rescatarlo y "
                           "el hielo se quedó allá.")]
    ops = [S.Opcion(t("hie.oa", "Al cráter A, a {d} km: 20 L de hielo", d=cerca), ir_cerca, not lleno),
           S.Opcion(t("hie.ob", "Al cráter B, a {d} km: 35 L de hielo", d=lejos), ir_lejos),
           S.Opcion(t("hie.oc", "No ir hoy"), lambda e: [], lleno)]
    return S.Decision(
        "hielo",
        t("hie.tit", "Hielo en los cráteres"),
        t("hie.enun", "En los cráteres que nunca ven el sol hay hielo de agua: la NASA lo confirmó con la misión "
                      "LCROSS en 2009. El rover gasta 1,5 kWh por km y su batería tiene 20 kWh. ¿A dónde van?"),
        ops,
        t("hie.exp", "Ida y vuelta al A: 2 × {a} × 1,5 = {ka} kWh. Al B: 2 × {b} × 1,5 = {kb} kWh. La batería del "
                     "rover tiene 20 kWh: al B no se llega y se vuelve. Más hielo no sirve si no se puede traer.",
          a=cerca, ka=n(3 * cerca, 0), b=lejos, kb=n(3 * lejos, 0)))


# ══ 14 · Gravedad: ¿se puede cargar la caja? ══════════════════════════════════════════════
def _d_gravedad(m):
    e = m.e
    masa = m.rng.choice((90, 120, 150, 180, 210))
    siente = masa * 1.62 / 9.80
    puede = siente <= 25

    def mano(e):
        if puede:
            return [t("gra.a1", "La cargaron sin problema.")]
        e.enfermo = 2
        e.animo = max(0, e.animo - 6)
        return [t("gra.a2", "¡Era demasiado! Un tripulante se lastimó la espalda.")]

    def grua(e):
        e.energia -= 15
        return [t("gra.b", "La grúa la movió con 15 kWh.")]
    return S.Decision(
        "gravedad",
        t("gra.tit", "Una caja de {m} kg", m=masa),
        t("gra.enun", "Llegó una caja de repuestos de {m} kg. La gravedad de la Luna es 1,62 m/s² y la de la "
                      "Tierra 9,80 m/s² (NASA). Un tripulante puede levantar sin peligro lo que en la Tierra "
                      "pesaría 25 kg. La grúa gasta 15 kWh. ¿Cómo la mueven?", m=masa),
        [S.Opcion(t("gra.oa", "Cargarla a mano"), mano, puede),
         S.Opcion(t("gra.ob", "Usar la grúa"), grua, not puede)],
        t("gra.exp", "{{{{1,62|9,80}}}} ≈ 0,165: en la Luna todo pesa como {{{{1|6}}}}. La caja se siente como "
                     "{m} × 0,165 ≈ {s} kg. {res} Ojo: pesa menos, pero cuesta lo mismo frenarla: su masa "
                     "sigue siendo {m} kg.",
          m=masa, s=n(siente),
          res=(t("gra.si", "Es menos de 25: se puede a mano.") if puede
               else t("gra.no", "Es más de 25: hace falta la grúa."))))


# ══ 15 · Temperatura: ¿aislar las tuberías? ═══════════════════════════════════════════════
def _d_temperatura(m):
    e = m.e
    aguanta = m.rng.choice((250, 280, 320))
    cambio = N.T_SOL_C - N.T_SOMBRA_C
    hace_falta = cambio > aguanta

    def aislar(e):
        e.energia -= 25
        e.tuberias_sin_aislar = False
        return [t("tem.a", "Tuberías aisladas antes de la noche.")]

    def no(e):
        e.tuberias_sin_aislar = hace_falta
        return []
    return S.Decision(
        "temperatura",
        t("tem.tit", "Las tuberías de afuera"),
        t("tem.enun", "Al sol la superficie llega a 127 °C y en la oscuridad baja a −173 °C (NASA). Las tuberías "
                      "de afuera aguantan un cambio de hasta {ag} °C. Aislarlas cuesta 25 kWh. ¿Las aíslan?",
          ag=aguanta),
        [S.Opcion(t("tem.oa", "Sí, aislarlas"), aislar, hace_falta),
         S.Opcion(t("tem.ob", "No hace falta"), no, not hace_falta)],
        t("tem.exp", "127 − (−173) = 127 + 173 = 300 °C de cambio. Aguantan {ag} °C: {res}",
          ag=aguanta,
          res=(t("tem.si", "300 > {ag}, sin aislar se revientan.", ag=aguanta) if hace_falta
               else t("tem.no", "300 < {ag}, aguantan solas.", ag=aguanta))))


# ══ 16 · Llamada a la Tierra ══════════════════════════════════════════════════════════════
def _d_llamada(m):
    def ef(bien):
        def _(e):
            e.animo = min(100, e.animo + (10 if bien else 4))
            return [t("lla.si", "Esperaron su turno y la llamada salió muy bien.") if bien
                    else t("lla.no", "Se pisaban al hablar, pero igual fue lindo oír a la familia.")]
        return _
    ops = [S.Opcion(t("lla.a", "Unos 1,3 segundos"), ef(False)),
           S.Opcion(t("lla.b", "Unos 2,6 segundos"), ef(True), True),
           S.Opcion(t("lla.c", "Unos 26 segundos"), ef(False))]
    m.rng.shuffle(ops)
    return S.Decision(
        "llamada",
        t("lla.tit", "Videollamada con las familias"),
        t("lla.enun", "La señal viaja a la velocidad de la luz: unos 300 000 km por segundo. La Luna está a "
                      "384 400 km de la Tierra (NASA). Si un astronauta pregunta algo, ¿cuánto tarda en oír "
                      "la respuesta?"),
        ops,
        t("lla.exp", "Ida: {{384 400|300 000}} ≈ 1,3 s. La respuesta también tiene que volver: 1,3 × 2 ≈ 2,6 s. "
                     "Por eso en la Luna se habla por turnos."))


# ══ 17 · El ángulo del panel (idea del equipo) ════════════════════════════════════════════
def _d_angulo(m):
    e = m.e
    k = max(0, e.luz + 1 - e.dia)
    vale = k >= 2

    def alinear(e):
        e.sin_tarea = True
        return [t("ang.a", "El panel vuelve a mirar de frente al Sol.")]

    def dejar(e):
        e.panel_factor *= 0.5
        return [t("ang.b", "El panel sigue torcido: da la mitad.")]
    return S.Decision(
        "angulo",
        t("ang.tit", "El panel se torció"),
        t("ang.enun", "El polvo que levantó el rover movió el panel y ahora el Sol le llega de lado. La NASA "
                      "explica que un panel da menos mientras más se inclina: a 60° recibe solo {{{{1|2}}}} de la "
                      "luz. Alinearlo es una salida que ocupa el trabajo del día. Quedan {k} días de sol.", k=k),
        [S.Opcion(t("ang.oa", "Salir a alinearlo"), alinear, vale),
         S.Opcion(t("ang.ob", "Dejarlo así"), dejar, not vale)],
        t("ang.exp", "Torcido da 10,9 × {{{{1|2}}}} ≈ 5,4 kW: se pierden 5,4 × 24 ≈ 131 kWh por cada día de sol. "
                     "En {k} días: {kwh} kWh. {res}",
          k=k, kwh=n(131 * k, 0),
          res=(t("ang.si", "Vale mucho más que un día de trabajo.") if vale
               else t("ang.no", "Ya casi es de noche: no vale la pena salir."))))
