# -*- coding: utf-8 -*-
"""El simulador de la base lunar: reglas

Uso (lo mismo hacen la pantalla del juego y las pruebas):

    m = Mision(semilla=7)
    while not m.fin:
        reporte = m.empezar_dia()          # qué pasó ayer y qué trae hoy
        if m.decision:                     # la decisión del día (puede no haber)
            resultado = m.elegir(0)        # índice de la opción
        m.hacer_tarea("cosecha", 1.0)      # tarea del día; 1.0 = rendimiento normal
        resumen = m.cerrar_dia()           # consumo, producción y revisión de fin

Los datos reales (los recursos del reto: DONKI, RadLab/OSDR, APOD y la CSA) viven en `datos_nasa.py`
y `clima.py`. Los números de abajo son «parámetros del juego»: decisiones de diseño (tamaño de la
batería, potencia de cada aparato, cuánto gasta una persona...). No se presentan como datos del reto.

Las 7 tareas del día, siempre visibles: cosecha, oxigeno, radiacion, hielo, recreo, estiba, paneles.
"""
import random

from ..data import datos_nasa as N
from ..assets.textos import t, n

# ══ Parámetros del juego (diseño, NO datos de la NASA) ════════════════════════════════════
PANEL_M2 = 40                    # m² de paneles solares
PANEL_EFICIENCIA = 0.20          # fracción de la luz que se vuelve electricidad
PANEL_KW = PANEL_M2 * N.IRRADIANCIA_W_M2 * PANEL_EFICIENCIA / 1000   # = 10,9 kW
REACTOR_KW = N.REACTOR_KW        # 10 kW, se enciende al caer la noche (idea del equipo)
BATERIA_MAX = 500                # kWh
CARGAS_KW = {                    # lo que gasta cada aparato encendido
    "base_dia": 4.0,             # aire, CO₂, computadoras, luces
    "base_noche": 6.0,           # lo mismo + calefacción a −173 °C
    "generador": 2.5,            # generador de oxígeno (electrólisis)
    "reciclador": 1.0,           # reciclador de agua
    "invernadero": 3.0,          # luces LED del invernadero
}
GEN_O2_KG = 4.0                  # kg de O₂ por día del generador
GEN_AGUA_L = GEN_O2_KG * N.AGUA_POR_KG_O2   # 4,5 L de agua que parte por día (química real)
INV_COMIDA_KG = 1.6              # kg de comida por día del invernadero
INV_O2_KG = 0.25                 # kg de O₂ por día que devuelven las plantas
INV_AGUA_L = 1.0                 # L por día que pierde el invernadero
MAXIMOS = {"o2": 60, "agua": 160, "comida": 160, "energia": BATERIA_MAX}
INICIO = {"o2": 32.0, "agua": 110.0, "comida": 115.0, "energia": 470.0,
          "dosis": 0.0, "animo": 80.0}
DIAS_MISION = N.DIAS_DE_LUZ + N.DIAS_DE_NOCHE   # 28 (misión completa)

# Dos misiones. La corta NO inventa un día lunar de 7 días: empieza a mitad del día lunar (le quedan
# 7 días de sol) y termina a mitad de la noche (7 días de oscuridad). Lleva menos reservas y un cohete
# de carga más chico, para que siga siendo difícil (ver tools/simular_misiones.py --corta).
INICIO_CORTA = {"o2": 26.0, "agua": 58.0, "comida": 62.0, "energia": 300.0,
                "dosis": 0.0, "animo": 70.0}
MODOS = {
    "completa": {"luz": N.DIAS_DE_LUZ, "total": DIAS_MISION, "inicio": INICIO, "carga": 1.0},
    "corta": {"luz": 7, "total": 14, "inicio": INICIO_CORTA, "carga": 0.5},
}
TORMENTA_MSV = {"moderada": 80, "fuerte": 200}   # dosis base afuera, sin protección; se escala con la clase
                                                 # de la fulguración REAL de DONKI (clima.escala)
LIMITE_DOSIS = N.LIMITE_MISION_MSV              # 250 mSv: límite de la misión (parámetro del juego)
BARRIDO_PASO = 0.10              # cada barrido de radiación baja 10 % la dosis...
BARRIDO_MAX = 0.30               # ...hasta un 30 % (tres barridos). Reemplaza al viejo blindaje de regolito.
PANELES_KWH = 60                 # energía que suma limpiar y alinear los paneles (solo de día)

RECURSOS = ("o2", "agua", "comida", "energia", "dosis", "animo")


class Opcion:
    def __init__(self, texto, efecto, correcta=False):
        self.texto = texto          # lo que dice el botón
        self.efecto = efecto        # función(estado) -> lista de frases de consecuencia
        self.correcta = correcta


class Decision:
    def __init__(self, ident, titulo, enunciado, opciones, explicacion, datos=None, evento=False):
        self.ident = ident
        self.titulo = titulo
        self.enunciado = enunciado      # puede llevar {{a|b}} y ^ (el juego los dibuja)
        self.opciones = opciones
        self.explicacion = explicacion  # por qué la mejor opción es la mejor, con números
        self.datos = datos or []        # renglones cortos con los números del problema
        self.evento = evento


class Estado:
    def __init__(self, modo="completa"):
        cfg = MODOS[modo]
        self.modo = modo
        self.luz = cfg["luz"]           # días de sol que vive la misión
        self.total = cfg["total"]       # días que dura la misión
        self.carga_factor = cfg["carga"]
        self.inicio = dict(cfg["inicio"])
        for k, v in self.inicio.items():
            setattr(self, k, v)
        self.dia = 1
        self.sistemas = {"generador": True, "reciclador": True, "invernadero": True}
        self.reciclador_roto = 0        # días que faltan para que llegue el repuesto
        self.panel_factor = 1.0         # 1 = panel sano y de frente al Sol
        self.regolito = 0.0             # metros de regolito sobre el hábitat (0 a 3); hoy solo lo sube la mancha
        self.barrido = 0.0              # fracción de dosis que bajaron los barridos de radiación (0 a 0,3)
        self.refugio = 1.0              # cuánto deja pasar el refugio (1 = no protege)
        self.refugio_elegido = False    # ya se decidió qué rodea al dormitorio
        self.racion = 1.0               # 1 = comida normal, 0.75 = racionada
        self.tripulantes = N.TRIPULANTES
        self.enfermo = 0                # días que le quedan de fiebre al tripulante enfermo
        self.tuberias_sin_aislar = False
        self.sin_tarea = False          # hoy la tarea se gastó en una reparación
        self.carga_hoy = None           # reabastecimiento que llegó hoy
        self.aciertos = 0
        self.errores = 0

    # ── consumos y producciones por día ───────────────────────────────────────────────
    def de_dia(self, dia=None):
        return (dia or self.dia) <= self.luz

    def dias_de_noche(self):
        return self.total - self.luz

    def consumo_o2(self):
        return N.O2_PERSONA_DIA * self.tripulantes

    def consumo_comida(self):
        return N.COMIDA_PERSONA_DIA * self.tripulantes * self.racion

    def agua_bruta(self):
        return N.AGUA_TOTAL_PERSONA_DIA * self.tripulantes

    def reciclando(self):
        return self.sistemas["reciclador"] and not self.reciclador_roto

    def consumo_agua(self):
        c = self.agua_bruta() * ((1 - N.RECICLAJE_AGUA) if self.reciclando() else 1.0)
        if self.sistemas["generador"]:
            c += GEN_AGUA_L
        if self.sistemas["invernadero"]:
            c += INV_AGUA_L
        return c

    def eficiencia(self):
        """Tripulación desanimada o con un enfermo rinde menos."""
        e = 0.8 if self.animo < 30 else 1.0
        return e * (0.9 if self.enfermo else 1.0)

    def kw_carga(self, dia=None, sistemas=None):
        s = sistemas or self.sistemas
        kw = CARGAS_KW["base_dia"] if self.de_dia(dia) else CARGAS_KW["base_noche"]
        for k in ("generador", "reciclador", "invernadero"):
            if s[k]:
                kw += CARGAS_KW[k]
        return kw

    def kw_fuente(self, dia=None):
        return PANEL_KW * self.panel_factor if self.de_dia(dia) else REACTOR_KW

    def factor_habitat(self):
        """Cuánto de una tormenta solar entra al hábitat (el regolito y los barridos la frenan)."""
        return max(0.25, 1 - 0.25 * self.regolito) * (1 - self.barrido)

    def dosis_diaria(self):
        return N.DOSIS_DIA_MSV * (1 - 0.15 * self.regolito) * (1 - self.barrido)

    def dias_que_alcanza(self, recurso):
        """Cuántos días dura un recurso al ritmo de hoy (None = no baja)."""
        neto = {"o2": (GEN_O2_KG * self.eficiencia() if self.sistemas["generador"] else 0)
                      + (INV_O2_KG if self.sistemas["invernadero"] else 0) - self.consumo_o2(),
                "agua": -self.consumo_agua(),
                "comida": (INV_COMIDA_KG * self.eficiencia() if self.sistemas["invernadero"] else 0)
                          - self.consumo_comida()}[recurso]
        if neto >= 0:
            return None
        return getattr(self, recurso) / -neto

    def foto(self):
        return {k: round(getattr(self, k), 2) for k in RECURSOS} | {
            "dia": self.dia, "regolito": self.regolito, "barrido": self.barrido,
            "generador": self.sistemas["generador"], "reciclador": self.reciclando(),
            "invernadero": self.sistemas["invernadero"]}


<<<<<<< HEAD:base_lunar/simulador.py
# ══ Tareas del día (cada una se volverá un minijuego; `r` = rendimiento 0,4 a 1,3) ═══════
TAREAS = ("cosecha", "oxigeno", "regolito", "hielo", "recreo", "estiba", "paneles")
PANELES_KWH = 60                 # kWh extra por limpiar y alinear los paneles (parámetro del juego)
=======
# ══ Tareas del día (cada una puede ser un minijuego; `r` = rendimiento 0,4 a 1,3) ════════════
# Siempre se muestran las 7. Las que hoy no se pueden hacer salen apagadas, con el motivo.
TAREAS = ("cosecha", "oxigeno", "radiacion", "hielo", "recreo", "estiba", "paneles")
>>>>>>> datos:game/logica/simulador.py


def tarea_titulo(tid):
    return {
        "cosecha": t("tarea.cosecha", "Cosecha en el invernadero"),
        "oxigeno": t("tarea.oxigeno", "Lista de verificación del generador de O₂"),
        "radiacion": t("tarea.radiacion", "Barrido de radiación"),
        "hielo": t("tarea.hielo", "Traer hielo del cráter"),
        "recreo": t("tarea.recreo", "Recreo de la tripulación"),
        "estiba": t("tarea.estiba", "Estiba del cohete de carga"),
        "paneles": t("tarea.paneles", "Limpiar y alinear los paneles solares"),
    }[tid]


def tarea_detalle(tid):
    return {
        "cosecha": t("tarea.cosecha.d", "+5 kg de comida · necesita el invernadero encendido"),
        "oxigeno": t("tarea.oxigeno.d", "+4 kg de O₂ · parte 4,5 L de agua"),
        "radiacion": t("tarea.radiacion.d", "−10 % de dosis en cada barrido, hasta −30 %"),
        "hielo": t("tarea.hielo.d", "+15 L de agua · gasta 5 kWh para derretirlo"),
        "recreo": t("tarea.recreo.d", "+12 de ánimo"),
        "estiba": t("tarea.estiba.d", "+15 % de la carga que llegó hoy"),
        "paneles": t("tarea.paneles.d", "+60 kWh de energía · solo de día"),
    }[tid]


# ══ La misión ═════════════════════════════════════════════════════════════════════════════
class Mision:
    def __init__(self, semilla=None, modo="completa"):
        from . import decisiones
        self._decisiones = decisiones
        self.semilla = semilla if semilla is not None else random.randrange(1_000_000)
        self.rng = random.Random(self.semilla)
        self.e = Estado(modo)
        self.total = self.e.total
        self.plan = decisiones.armar_calendario(self.rng, self.e)   # {día: id de decisión}
        self.usadas = set()
        self.decision = None
        self.fin = None          # None, "victoria" o "derrota"
        self.causa = ""
        self.historial = [self.e.foto()]
        self.bitacora = []       # frases del día, para el reporte de la mañana
        self.pronostico = decisiones.pronostico(self.plan, 2, self.e)

    # ── ① mañana ─────────────────────────────────────────────────────────────────────
    def empezar_dia(self):
        e = self.e
        e.sin_tarea = False
        e.carga_hoy = None
        reporte = list(self.bitacora)
        self.bitacora = []
        if e.dia == e.luz + 1:
            reporte.insert(0, t("rep.noche", "Cayó la noche lunar: −173 °C afuera y la misión sigue {n} días en "
                                             "la oscuridad. El reactor ya está encendido.", n=e.dias_de_noche()))
        ident = self.plan.get(e.dia) or self._decisiones.elegir_rutina(self)
        self.decision = self._decisiones.construir(ident, self) if ident else None
        if self.decision:
            self.usadas.add(self.decision.ident)
        self.pronostico = self._decisiones.pronostico(self.plan, e.dia + 1, e)
        return reporte

    # ── ② decisión ───────────────────────────────────────────────────────────────────
    def elegir(self, idx):
        d = self.decision
        op = d.opciones[idx]
        frases = op.efecto(self.e) or []
        if op.correcta:
            self.e.aciertos += 1
            self.e.animo = min(100, self.e.animo + 3)
        else:
            self.e.errores += 1
            self.e.animo = max(0, self.e.animo - 4)
        mejores = [o.texto for o in d.opciones if o.correcta]
        return {"correcta": op.correcta, "frases": frases, "explicacion": d.explicacion,
                "mejores": mejores}

    # ── ③ tarea ──────────────────────────────────────────────────────────────────────
    def tareas_estado(self):
        """Las 7 tareas, siempre: [(id, se_puede, motivo_si_no)]."""
        e = self.e
<<<<<<< HEAD:base_lunar/simulador.py
        if e.sin_tarea:
            return []
        ts = ["oxigeno", "hielo", "recreo"]
        if e.sistemas["invernadero"]:
            ts.insert(0, "cosecha")
        if e.regolito < 3:
            ts.append("regolito")
        if e.de_dia():
            ts.append("paneles")
        if e.carga_hoy:
            ts.append("estiba")
        return ts
=======
        res = []
        for tid in TAREAS:
            motivo = ""
            if e.sin_tarea:
                motivo = t("nod.rep", "hoy la tripulación está en una reparación")
            elif tid == "cosecha" and not e.sistemas["invernadero"]:
                motivo = t("nod.inv", "el invernadero está apagado")
            elif tid == "estiba" and not e.carga_hoy:
                motivo = t("nod.carga", "hoy no llegó ningún cohete de carga")
            elif tid == "paneles" and not e.de_dia():
                motivo = t("nod.noche", "de noche no hay Sol")
            elif tid == "radiacion" and e.barrido >= BARRIDO_MAX - 1e-9:
                motivo = t("nod.rad", "ya mapearon toda la radiación")
            res.append((tid, not motivo, motivo))
        return res

    def tareas_disponibles(self):
        return [tid for tid, ok, _ in self.tareas_estado() if ok]
>>>>>>> datos:game/logica/simulador.py

    def hacer_tarea(self, tid, r=1.0):
        """Aplica la tarea con rendimiento r (1 = normal; el minijuego lo sube o lo baja)."""
        e = self.e
        r = max(0.0, min(1.3, r)) * e.eficiencia()
        if tid not in self.tareas_disponibles():
            return []
        if tid == "cosecha":
            e.comida += 5 * r
            e.animo = min(100, e.animo + 2)
            return [t("tar.cosecha", "Cosecharon {kg} kg de comida.", kg=n(5 * r))]
        if tid == "oxigeno":
            o2 = 4 * r
            agua = o2 * N.AGUA_POR_KG_O2
            e.o2 += o2
            e.agua -= agua
            return [t("tar.oxigeno", "El generador hizo {o2} kg extra de O₂ con {agua} L de agua.",
                      o2=n(o2), agua=n(agua))]
        if tid == "radiacion":
            paso = BARRIDO_PASO if r >= 0.6 else BARRIDO_PASO / 2
            e.barrido = min(BARRIDO_MAX, e.barrido + paso)
            return [t("tar.radiacion", "Los detectores mostraron dónde hay menos radiación y la tripulación se "
                                       "mudó allí: la dosis baja {p} % en total.", p=n(e.barrido * 100, 0))]
        if tid == "hielo":
            litros = 15 * r
            e.agua += litros
            e.energia -= 5
            e.dosis += 0.1
            return [t("tar.hielo", "Trajeron hielo: {l} L de agua.", l=n(litros))]
        if tid == "recreo":
            e.animo = min(100, e.animo + 12 * r)
            return [t("tar.recreo", "La tripulación descansó: el ánimo subió.")]
        if tid == "paneles":
            kwh = PANELES_KWH * r
            e.energia += kwh
            return [t("tar.paneles", "Con los paneles limpios y de frente al Sol entraron {k} kWh más.",
                      k=n(kwh, 0))]
        if tid == "estiba":
            c = e.carga_hoy
            extra = 0.15 * min(r, 1.0)
            for k, v in c.items():
                setattr(e, k, getattr(e, k) + v * extra)
            return [t("tar.estiba", "Con la estiba bien hecha cupo un {p} % más de carga.",
                      p=n(extra * 100, 0))]
        if tid == "paneles":
            kwh = PANELES_KWH * r
            e.energia = min(MAXIMOS["energia"], e.energia + kwh)
            return [t("tar.paneles", "Con los paneles limpios y de frente al Sol entraron {k} kWh más.",
                      k=n(kwh, 0))]
        return []

    # ── ④ cierre del día ─────────────────────────────────────────────────────────────
    def cerrar_dia(self):
        e = self.e
        antes = e.foto()
        frases = []
        # Energía: lo que entra menos lo que sale. Si no alcanza, se apaga solo lo que se pueda.
        entra = e.kw_fuente() * 24
        sale = e.kw_carga() * 24
        if e.energia + entra - sale < 0:
            for k in ("invernadero", "generador"):
                if e.sistemas[k] and e.energia + entra - sale < 0:
                    e.sistemas[k] = False
                    sale = e.kw_carga() * 24
                    frases.append(t("cie.apagon." + k, "¡Apagón! Se apagó solo el {s} para salvar la batería.",
                                    s=t("sis." + k, {"invernadero": "invernadero", "generador": "generador de O₂"}[k])))
        e.energia += entra - sale
        if e.energia < 0:
            e.energia = 0
            e.animo -= 12
            e.o2 -= 1.0
            frases.append(t("cie.frio", "La batería se vació: la base pasó frío y el aire se renovó mal."))
        ef = e.eficiencia()
        # Oxígeno
        e.o2 += (GEN_O2_KG * ef if e.sistemas["generador"] else 0) \
            + (INV_O2_KG if e.sistemas["invernadero"] else 0) - e.consumo_o2()
        # Agua
        e.agua -= e.consumo_agua()
        if e.reciclador_roto:
            e.reciclador_roto -= 1
            if not e.reciclador_roto:
                frases.append(t("cie.repuesto", "Llegó el repuesto: el reciclador de agua funciona otra vez."))
        if e.tuberias_sin_aislar and not e.de_dia():
            e.tuberias_sin_aislar = False
            e.agua -= 20
            frases.append(t("cie.tuberia", "Con el frío de la noche se reventó una tubería sin aislar: "
                                           "se perdieron 20 L de agua."))
        # Comida
        e.comida += (INV_COMIDA_KG * ef if e.sistemas["invernadero"] else 0) - e.consumo_comida()
        # Radiación de fondo
        e.dosis += e.dosis_diaria()
        # Ánimo
        e.animo -= 1.5 + (0 if e.de_dia() else 1.0) + (3 if e.racion < 1 else 0) + (2 if e.enfermo else 0)
        if e.enfermo:
            e.enfermo -= 1
        # Topes
        for k, mx in MAXIMOS.items():
            if getattr(e, k) > mx:
                setattr(e, k, float(mx))
        e.animo = max(0.0, min(100.0, e.animo))
        # ¿Se acabó?
        for k, causa in (("o2", t("fin.o2", "Se acabó el oxígeno.")),
                         ("agua", t("fin.agua", "Se acabó el agua.")),
                         ("comida", t("fin.comida", "Se acabó la comida."))):
            if getattr(e, k) <= 0:
                setattr(e, k, 0.0)
                self.fin, self.causa = "derrota", causa
        if not self.fin and e.dosis >= LIMITE_DOSIS:
            self.fin = "derrota"
            self.causa = t("fin.dosis_limite", "La tripulación pasó el límite de radiación de la misión ({l} mSv).",
                           l=LIMITE_DOSIS)
        if not self.fin and e.animo <= 0:
            self.fin = "derrota"
            self.causa = t("fin.animo", "La tripulación, agotada, pidió abortar la misión.")
        self.historial.append(e.foto())
        cambios = {k: round(getattr(e, k) - antes[k], 2) for k in RECURSOS}
        if not self.fin:
            e.dia += 1
            if e.dia > e.total:
                self.fin = "victoria"
                self.causa = (t("fin.victoria", "¡La tripulación sobrevivió los 28 días: un día lunar completo!")
                              if e.modo == "completa" else
                              t("fin.victoria_corta", "¡La tripulación sobrevivió los 14 días: 7 de sol y 7 de "
                                                      "noche lunar!"))
        self.bitacora = frases
        return {"cambios": cambios, "frases": frases, "fin": self.fin, "causa": self.causa}

    # ── puntaje ──────────────────────────────────────────────────────────────────────
    def puntaje(self):
        e = self.e
        p = e.aciertos * 100 + e.animo * 5 + max(0, LIMITE_DOSIS - e.dosis) * 2
        p += sum(getattr(e, k) / e.inicio[k] for k in ("o2", "agua", "comida")) * 100
        if self.fin == "victoria":
            p += 1000
        return int(round(p))

    def estrellas(self):
        if self.fin != "victoria":
            return 0
        p = self.puntaje()
        k = 0.5 + 0.5 * self.e.total / DIAS_MISION      # la corta tiene la mitad de decisiones
        return 3 if p >= 3200 * k else 2 if p >= 2400 * k else 1
