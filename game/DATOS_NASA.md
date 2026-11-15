# Datos reales del juego · Real data used in the game

Hay dos:

- **A · Recursos del reto** (DONKI, RadLab/OSDR, APOD/NASA Open APIs, CSA). Es lo que el juego presenta como «datos reales»
- **C · Parámetros de diseño**. Números que el simulador necesita; algunos se inspiran en otras páginas de la NASA.

Fecha de lectura de las páginas: 15/11/2026.

## A · Recursos del reto · Challenge resources

| Dato · Data | Valor · Value | En el juego · In the game | Fuente · Source |
|---|---|---|---|
| Fulguraciones solares · Solar flares | 1941 (2024-01 a 2026-11); 243 guardadas (85 clase X, 153 clase M) | Cada tormenta se basa en una real; su clase escala la dosis (`logica/clima.py`) | [DONKI](https://ccmc.gsfc.nasa.gov/tools/DONKI/) · API `/DONKI-API/get/FLR`, `/get/SEP` |
| Tipos de evento DONKI | FLR, SEP, CME, IPS, MPC, GST, RBE, HSS | Explicados en la ayuda «?» | [DONKI](https://ccmc.gsfc.nasa.gov/tools/DONKI/) |
| Unidades de dosis · Dose units | µGy/h (absorbida) y µSv/h (equivalente) | Decisión «El dosímetro de la base» | [RadLab API](https://visualization.osdr.nasa.gov/radlab/gui/data-api/) |
| Instrumentos · Instruments | Liulin-5, ALTEA, Timepix, DosTel, TEPC | Ayuda de la radiación | [RadLab release history](https://visualization.osdr.nasa.gov/radlab/kb/Release_history) |
| Otros lugares de medición | Chang'e 4 (Luna), LRO, Curiosity (Marte) | Contexto | [RadLab release history](https://visualization.osdr.nasa.gov/radlab/kb/Release_history) |
| Base de datos RadLab | Grigorev et al. | Referencia | [NTRS 20240012790](https://ntrs.nasa.gov/citations/20240012790) |
| Imagen del día | APOD | Fondos del menú, con crédito | [NASA Open APIs](https://api.nasa.gov/) |
| Calorías por astronauta | 1 900 a 3 200 al día | Decisión de la ración | [CSA, Eating in space](https://www.asc-csa.gc.ca/eng/astronauts/living-in-space/eating-in-space.asp) |
| Ejercicio y hueso | 2 h/día en la Estación; ~1 % de hueso por mes (12 veces más rápido que un adulto mayor en la Tierra: 1 % por año) | Decisión del ejercicio | [CSA, Physical activity in space](https://www.asc-csa.gc.ca/eng/astronauts/living-in-space/physical-activity-in-space.asp) |
| Vueltas a la Tierra | 16 por día | Ayuda del recreo | [CSA, Relaxing in space](https://www.asc-csa.gc.ca/eng/astronauts/living-in-space/relaxing-in-space.asp) |
| Cultivo de comida | misiones largas a la Luna | Ayuda de la cosecha | [CSA, Food production on the Moon](https://www.asc-csa.gc.ca/eng/youth-educators/toolkits/food-production/) |

## C · Parámetros de diseño · Design parameters

| Parámetro | Valor | Referencia que lo inspira |
|---|---|---|
| O₂, comida y agua por persona | 0,816 · 1,51 · 4,48 | [NASA BVAD Rev1 (2018)](https://ntrs.nasa.gov/citations/20180001338) |
| Reciclaje de agua | 98 % | [NASA, 20/06/2023](https://www.nasa.gov/missions/station/iss-research/nasa-achieves-water-recovery-milestone-on-international-space-station/) |
| Día lunar, 1361 W/m², gravedad, distancia | 14 + 14 días · 1361 · 1,62 · 384 400 km | [NSSDC Moon Fact Sheet](https://nssdc.gsfc.nasa.gov/planetary/factsheet/moonfact.html) |
| Temperaturas | 127 °C / −173 °C | [NASA Science, Moon Facts](https://science.nasa.gov/moon/facts/) |
| Dosis de fondo | 0,5 mSv/día | [NASA OCHMO-TB-020 Rev E](https://www.nasa.gov/wp-content/uploads/2023/03/radiation-protection-technical-brief-ochmo.pdf) |
| Límite de la misión | 250 mSv | [NASA-STD-3001 Vol. 1 Rev B](https://www.nasa.gov/wp-content/uploads/2020/10/2022-01-05_nasa-std-3001_vol.1_rev._b_final_draft_with_signature_010522.pdf) |
| Aviso de partículas | 15 a 30 min | [NASA SDO](https://sdo.gsfc.nasa.gov/mission/spaceweather/spaceweather.php) |
| Regolito y agua como escudo | (el estado de regolito se conserva; la tarea es «barrido de radiación») | [NTRS 20130009378](https://ntrs.nasa.gov/citations/20130009378) |
| Reactor | 10 kW | [NASA Kilopower](https://www.nasa.gov/directorates/stmd/tech-demo-missions-program/kilopower-hmqzw/) |
| Electrólisis | 36 g de agua → 32 g de O₂ (fórmula química) | [NASA ECLSS](https://www.nasa.gov/reference/environmental-control-and-life-support-systems-eclss/) |
| Hielo lunar | LCROSS 2009, M3 2018 | [NASA Science](https://science.nasa.gov/moon/moon-water-and-ices/) |
| Clases de fulguración | X = 10 × M | [NASA Science](https://science.nasa.gov/sun/solar-storms-and-flares/) |
| Lechuga en el espacio (nota del huerto) | Veggie, 2015 | [NASA, blog de la Estación, 10/08/2015](https://www.nasa.gov/blogs/spacestation/2015/08/10/cosmonauts-complete-russian-spacewalk) |


## Por qué DONKI · Why DONKI

El reto pide conectar las decisiones de radiación con el clima espacial real. Por eso las tormentas solares del
juego salen de fulguraciones reales registradas por la oficina Moon to Mars Space Weather Analysis de la NASA, y
la decisión de cubrir el hábitat muestra qué está haciendo el Sol de verdad. Los datos guardados se bajan con
`python tools/bajar_donki.py` y el juego siempre dice si lo que muestra es **en vivo** o **guardado**. Las dosis
de las tormentas en el juego son simplificaciones: DONKI registra los eventos, no la dosis en la Luna.

The challenge asks to link radiation decisions to real space weather, so every in-game solar storm comes from a
real flare recorded by NASA's Moon to Mars Space Weather Analysis Office, and the shielding decision shows the
real Sun. The game always says whether that information is **live** or **saved**.

## Química y física (no son «datos de la NASA») · Chemistry and physics

- 2 H₂O → 2 H₂ + O₂: de 36 g de agua salen 32 g de oxígeno (1,125 kg de agua por kg de O₂).
- La señal de radio viaja a la velocidad de la luz (~300 000 km/s).
- Derretir hielo y moverse en el rover gastan energía: valores aproximados del juego.
