# -*- coding: utf-8 -*-
"""Datos reales que usa el simulador.

Hay dos partes:

  A · RECURSOS DEL RETO (NASA Space Apps 2026). Lo que el reto nos dio: NASA Open APIs (APOD),
      DONKI, RadLab / OSDR y los recursos de la Agencia Espacial Canadiense (CSA). Cada número de esta
      capa se leyó en la página de la fuente el 15/11/2026.

  B · PARÁMETROS DEL JUEGO. Números de diseño que el simulador necesita para funcionar (cuánto
      oxígeno gasta una persona, qué tan grande es la batería...). 
"""

#  A · RECURSOS DEL RETO 
# A1 · DONKI (clima espacial)
# https://ccmc.gsfc.nasa.gov/tools/DONKI/ · la mantiene la Moon-to-Mars Space Weather Analysis
# Office (M2M-SWAO) del Goddard, desde junio de 2020.
DONKI_TIPOS = ("FLR", "SEP", "CME", "IPS", "MPC", "GST", "RBE", "HSS")

# A2 · RadLab (OSDR): dosis de radiación medidas por instrumentos reales
# https://visualization.osdr.nasa.gov/radlab/gui/data-api/
RADLAB_UNIDAD_ABSORBIDA = "µGy/h"        # dosis absorbida por hora (absorbed_dose_rate)
RADLAB_UNIDAD_EQUIVALENTE = "µSv/h"      # equivalente de dosis por hora (dose_equivalent_rate)
RADLAB_MODULOS_ISS = ("US Lab", "Cupola", "JPM", "SM")        # lugares dentro de la Estación
RADLAB_INSTRUMENTOS = ("Liulin-5", "ALTEA", "Timepix", "DosTel", "TEPC")
RADLAB_LIULIN5_SEG_SAA = 20              # una medición cada 20 s cerca de la Anomalía del Atlántico Sur
RADLAB_LIULIN5_SEG = 90                  # y cada 90 s en el resto de la órbita (RadLab, release 1.0.0)
RADLAB_ALTEA_SEG = 60                    # ALTEA-Survey: cada 60 s (mediana, release 1.1.0)
RADLAB_OTROS_LUGARES = ("Chang'e 4 (superficie de la Luna)", "LRO (órbita de la Luna)",
                        "Curiosity (superficie de Marte)")

# A3 · CSA (Agencia Espacial Canadiense): vivir y comer en el espacio
CSA_KCAL_DIA = (1900, 3200)              # calorías por astronauta por día, según peso, sexo y necesidades
CSA_EJERCICIO_H_DIA = 2                  # horas de ejercicio al día en la Estación (misiones largas)
CSA_EJERCICIO_ORION_MIN = 30             # minutos casi todos los días en Orion (camino a la Luna)
CSA_HUESO_PCT_MES = 1                    # % de densidad ósea que se pierde por mes en el espacio (promedio)
CSA_HUESO_PCT_ANIO_MAYOR = 1             # % que pierde por AÑO un adulto mayor en la Tierra
CSA_VUELTAS_ISS_DIA = 16                 # vueltas a la Tierra de la Estación en un día
CSA_EQUIPO_ISS_KG = 1800                 # el equipo de ejercicio de la Estación pesa más de 1800 kg
CSA_EQUIPO_ISS_M2 = 80                   # y ocupa casi 80 m²
CSA_VOLANTE_ORION_KG = 14                # el volante de ejercicio de Orion pesa solo 14 kg
HUESO_VECES_MAS_RAPIDO = 12              # 1 % por mes contra 1 % por año: 12 veces más rápido (cuenta)

# B · PARÁMETROS DEL JUEGO (diseño simplificado inspirado en los datos reales)
TRIPULANTES = 4
O2_PERSONA_DIA = 0.816        # kg de oxígeno por persona por día
COMIDA_PERSONA_DIA = 1.51     # kg de comida por persona por día
AGUA_TOTAL_PERSONA_DIA = 4.48  # L por persona por día (con higiene)
RECICLAJE_AGUA = 0.98         # fracción de agua que recupera el reciclador
DIAS_DE_LUZ = 14              # días de sol y de noche de la misión completa
DIAS_DE_NOCHE = 14
IRRADIANCIA_W_M2 = 1361       # potencia del Sol por m²
T_SOL_C = 127                 # °C al sol
T_SOMBRA_C = -173             # °C en la oscuridad
DOSIS_DIA_MSV = 0.5           # mSv de radiación de fondo por día en la superficie
LIMITE_MISION_MSV = 250       # mSv: si la tripulación lo pasa, se pierde la misión
REACTOR_KW = 10               # kW del reactor que se enciende de noche
# Química (no es un dato de la NASA: es la fórmula del agua).
AGUA_POR_KG_O2 = 36 / 32      # 1,125 kg de agua por cada kg de oxígeno

REFERENCIAS_OTRAS = [
    ("O₂, comida y agua por persona (0,816 · 1,51 · 4,48)", "NASA BVAD Rev1 (2018), tablas 3-33 y 4-20",
     "https://ntrs.nasa.gov/citations/20180001338"),
    ("Reciclaje del 98 % del agua", "NASA, 20 de junio de 2023",
     "https://www.nasa.gov/missions/station/iss-research/nasa-achieves-water-recovery-milestone-on-international-space-station/"),
    ("Día lunar, 1361 W/m², gravedad, distancia a la Tierra", "NSSDC Moon Fact Sheet",
     "https://nssdc.gsfc.nasa.gov/planetary/factsheet/moonfact.html"),
    ("Día y noche de unas dos semanas", "NASA Science, Moonlight", "https://science.nasa.gov/moon/moonlight/"),
    ("127 °C al sol y −173 °C en la oscuridad", "NASA Science, Moon Facts", "https://science.nasa.gov/moon/facts/"),
    ("0,5 mSv por día en la superficie", "NASA OCHMO-TB-020 Rev E (2022)",
     "https://www.nasa.gov/wp-content/uploads/2023/03/radiation-protection-technical-brief-ochmo.pdf"),
    ("250 mSv de límite por tormenta", "NASA-STD-3001 Vol. 1 Rev B (2022)",
     "https://www.nasa.gov/wp-content/uploads/2020/10/2022-01-05_nasa-std-3001_vol.1_rev._b_final_draft_with_signature_010522.pdf"),
    ("Partículas solares llegan en 15 a 30 minutos", "NASA Solar Dynamics Observatory",
     "https://sdo.gsfc.nasa.gov/mission/spaceweather/spaceweather.php"),
    ("Regolito y agua como escudo contra la radiación", "NASA NTRS 20130009378 y 20150001237",
     "https://ntrs.nasa.gov/citations/20130009378"),
    ("Reactor de 10 kW (Kilopower)", "NASA Kilopower",
     "https://www.nasa.gov/directorates/stmd/tech-demo-missions-program/kilopower-hmqzw/"),
    ("Electrólisis del agua para hacer oxígeno", "NASA ECLSS",
     "https://www.nasa.gov/reference/environmental-control-and-life-support-systems-eclss/"),
    ("Hielo de agua en la Luna (LCROSS 2009; M3 2018)", "NASA Ames y NASA Science",
     "https://science.nasa.gov/moon/moon-water-and-ices/"),
    ("Una fulguración X es 10 veces una M y 100 veces una C", "NASA Science, Solar Storms and Flares",
     "https://science.nasa.gov/sun/solar-storms-and-flares/"),
]

# ══ Fuentes que se muestran en la pantalla «Los datos reales del juego» ═══════════════════════
# (dato, fuente, enlace, origen)   origen: "NASA" (recurso del reto) o "CSA" (socio del reto)
FUENTES = [
    ("Fulguraciones solares y partículas reales (2024 a hoy)", "NASA CCMC DONKI · Moon to Mars Space Weather Office",
     "https://ccmc.gsfc.nasa.gov/tools/DONKI/", "NASA"),
    ("DONKI también anota eyecciones de masa, tormentas geomagnéticas y cinturones de radiación",
     "NASA CCMC DONKI", "https://ccmc.gsfc.nasa.gov/tools/DONKI/", "NASA"),
    ("Dosis de radiación medidas en la Estación Espacial (µGy/h y µSv/h)", "NASA OSDR · RadLab, API de datos",
     "https://visualization.osdr.nasa.gov/radlab/gui/data-api/", "NASA"),
    ("Instrumentos reales: Liulin-5, ALTEA y Timepix", "NASA OSDR · RadLab, historial de versiones",
     "https://visualization.osdr.nasa.gov/radlab/kb/Release_history", "NASA"),
    ("Mediciones también en la Luna (Chang'e 4), en órbita lunar (LRO) y en Marte (Curiosity)",
     "NASA OSDR · RadLab, historial de versiones",
     "https://visualization.osdr.nasa.gov/radlab/kb/Release_history", "NASA"),
    ("RadLab: base de datos de radiación del OSDR", "Grigorev et al., NASA NTRS 20240012790",
     "https://ntrs.nasa.gov/citations/20240012790", "NASA"),
    ("Estudios de cómo el vuelo espacial afecta huesos, músculos, defensas y sueño",
     "NASA OSDR · Open Science Data Repository", "https://osdr.nasa.gov/bio/repo/", "NASA"),
    ("Imagen astronómica del día (los fondos del menú)", "NASA APOD · NASA Open APIs",
     "https://api.nasa.gov/", "NASA"),
    ("Astronautas: de 1 900 a 3 200 calorías al día", "CSA · Eating in space",
     "https://www.asc-csa.gc.ca/eng/astronauts/living-in-space/eating-in-space.asp", "CSA"),
    ("La Estación recicla el agua de la orina, el sudor, el aliento y el lavado", "CSA · Eating in space",
     "https://www.asc-csa.gc.ca/eng/astronauts/living-in-space/eating-in-space.asp", "CSA"),
    ("2 horas de ejercicio al día y 1 % de hueso perdido por mes", "CSA · Physical activity in space",
     "https://www.asc-csa.gc.ca/eng/astronauts/living-in-space/physical-activity-in-space.asp", "CSA"),
    ("16 vueltas a la Tierra por día; internet lento; tiempo libre", "CSA · Relaxing in space",
     "https://www.asc-csa.gc.ca/eng/astronauts/living-in-space/relaxing-in-space.asp", "CSA"),
    ("Cultivar comida para las misiones largas a la Luna", "CSA · Food production on the Moon",
     "https://www.asc-csa.gc.ca/eng/youth-educators/toolkits/food-production/", "CSA"),
]
