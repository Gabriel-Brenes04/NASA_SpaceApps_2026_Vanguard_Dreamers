# -*- coding: utf-8 -*-
"""Datos reales que usa el simulador, cada uno con su fuente.

Python puro (sin pygame): se puede leer y probar sin el motor del juego.
Verificados el 14/11/2026 abriendo cada página (ver _investigacion/datos_verificados.md).

Regla del proyecto: si un dato no se pudo verificar, NO está aquí. Los números que son
decisiones de diseño del juego (tamaño de la batería, potencia de cada aparato, etc.) van
aparte, en `simulador.py`, marcados como «parámetro del juego».
"""

# ── Tripulación y soporte vital (NASA BVAD, NASA/TP-2015-218570 Rev1, enero 2018) ──────────
TRIPULANTES = 4
O2_PERSONA_DIA = 0.816        # kg de oxígeno por persona por día        (BVAD tabla 3-33)
CO2_PERSONA_DIA = 1.04        # kg de CO₂ que exhala una persona por día  (BVAD tabla 3-33)
COMIDA_PERSONA_DIA = 1.51     # kg de comida por persona por día, tal como se envía (BVAD 3-33)
AGUA_TOMAR_PERSONA_DIA = 2.5  # kg (= litros) para tomar y preparar comida (BVAD 3-33 y 4-20)
AGUA_TOTAL_PERSONA_DIA = 4.48  # kg (= litros) con higiene, «base planetaria temprana» (BVAD 4-20)
RECICLAJE_AGUA = 0.98         # la Estación Espacial recupera el 98 % del agua (NASA, junio 2023)

# ── La Luna ──────────────────────────────────────────────────────────────────────────────
DIA_LUNAR_DIAS = 29.53        # días terrestres entre un amanecer y el siguiente (NSSDC)
DIAS_DE_LUZ = 14              # «el día y la noche lunar duran cada uno unas dos semanas» (NASA)
DIAS_DE_NOCHE = 14
IRRADIANCIA_W_M2 = 1361       # potencia del Sol por m² a la distancia de la Luna (NSSDC)
T_SOL_C = 127                 # °C al sol (NASA, Moon facts)
T_SOMBRA_C = -173             # °C en la oscuridad (NASA, Moon facts)

# ── Radiación ────────────────────────────────────────────────────────────────────────────
DOSIS_DIA_MSV = 0.5           # mSv por día en la superficie: cifra de planificación de la NASA
                              # (OCHMO-TB-020 Rev E, 2022, p. 6)
DOSIS_MEDIDA_MSV = 1.37       # mSv por día medidos por la sonda Chang'e-4 (Zhang et al., Science
                              # Advances, 2020). NO es de la NASA: solo se menciona como contexto.
LIMITE_TORMENTA_MSV = 250     # límite de la NASA por evento de partículas solares (NASA-STD-3001)
LIMITE_CARRERA_MSV = 600      # límite de la NASA para toda la carrera de un astronauta (2022)
AVISO_TORMENTA_MIN = (15, 30)  # las partículas más rápidas llegan en 15 a 30 minutos (NASA SDO)
REGOLITO_PROTECTOR_M = 3      # ~3 m de regolito protegen un hábitat (estudios NASA en NTRS)

# ── Energía ──────────────────────────────────────────────────────────────────────────────
REACTOR_KILOPOWER_KW = 10     # demostración lunar de fisión «clase 10 kilovatios» (NASA Kilopower)
REACTOR_FSP_KW = 40           # meta de la NASA: reactor de 40 kW en la Luna a inicios de los 2030
PANELES_ISS_KW = (75, 90)     # los 8 paneles de la Estación Espacial dan 75 a 90 kW (NASA)

# ── Química (no es un «dato de la NASA»: es la fórmula del agua) ─────────────────────────
# 2 H₂O → 2 H₂ + O₂ : 36 g de agua dan 32 g de oxígeno. La Estación Espacial hace su oxígeno
# así, partiendo agua con electricidad (electrólisis, NASA ECLSS).
AGUA_POR_KG_O2 = 36 / 32      # 1,125 kg de agua por cada kg de oxígeno

# ── Fuentes (lo que se cita en la pantalla de créditos y en DATOS_NASA.md) ──────────────
FUENTES = [
    ("Oxígeno, comida y agua por persona", "NASA BVAD Rev1 (2018), tablas 3-33 y 4-20",
     "https://ntrs.nasa.gov/citations/20180001338", True),
    ("Reciclaje del 98 % del agua", "NASA, 20 de junio de 2023",
     "https://www.nasa.gov/missions/station/iss-research/nasa-achieves-water-recovery-milestone-on-international-space-station/", True),
    ("Día lunar de 29,53 días, luz del Sol 1361 W/m²", "NSSDC Moon Fact Sheet",
     "https://nssdc.gsfc.nasa.gov/planetary/factsheet/moonfact.html", True),
    ("Día y noche de unas dos semanas", "NASA Science, Moonlight",
     "https://science.nasa.gov/moon/moonlight/", True),
    ("127 °C al sol y −173 °C en la oscuridad", "NASA Science, Moon Facts",
     "https://science.nasa.gov/moon/facts/", True),
    ("0,5 mSv por día en la superficie", "NASA OCHMO-TB-020 Rev E (2022)",
     "https://www.nasa.gov/wp-content/uploads/2023/03/radiation-protection-technical-brief-ochmo.pdf", True),
    ("Límites: 250 mSv por tormenta, 600 mSv en la carrera", "NASA-STD-3001 Vol. 1 Rev B (2022)",
     "https://www.nasa.gov/wp-content/uploads/2020/10/2022-01-05_nasa-std-3001_vol.1_rev._b_final_draft_with_signature_010522.pdf", True),
    ("Las partículas llegan en 15 a 30 minutos", "NASA Solar Dynamics Observatory",
     "https://sdo.gsfc.nasa.gov/mission/spaceweather/spaceweather.php", True),
    ("~3 m de regolito protegen el hábitat", "NASA NTRS 20210022066 y 20130009378",
     "https://ntrs.nasa.gov/citations/20130009378", True),
    ("Reactor de fisión clase 10 kW (Kilopower)", "NASA Kilopower",
     "https://www.nasa.gov/directorates/stmd/tech-demo-missions-program/kilopower-hmqzw/", True),
    ("Reactor de 40 kW para la Luna", "NASA Fission Surface Power",
     "https://www.nasa.gov/exploration-systems-development-mission-directorate/fission-surface-power/", True),
    ("El oxígeno se hace partiendo agua (electrólisis)", "NASA ECLSS",
     "https://www.nasa.gov/reference/environmental-control-and-life-support-systems-eclss/", True),
    ("Hielo de agua en los polos de la Luna (LCROSS, 2009)", "NASA Ames",
     "https://www.nasa.gov/centers/ames/news/releases/2010/10-89AR.html", True),
    ("1,37 mSv por día medidos en la superficie", "Zhang et al., Science Advances 6, eaaz1334 (2020)",
     "https://www.science.org/doi/10.1126/sciadv.aaz1334", False),
]
