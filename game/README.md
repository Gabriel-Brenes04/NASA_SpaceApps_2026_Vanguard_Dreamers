# NASA_SpaceApps_2026_Vanguard_Dreamers
Proyecto para presentar el dia domingo 15 de noviembre.

# Base Lunar

**Junior astronaut mission simulator · Simulador de misión para astronautas junior**
NASA Space Apps Challenge 2026 · Team Vanguard Dreamers

![Base Lunar](docs/capturas/titulo.png)

---

## English

Kids aged 7 to 12 run a lunar outpost with 4 crew members for 14 or 28 days. They balance **oxygen, water,
energy, food, radiation dose and crew morale**. Every day brings a decision that is a **real math problem with
real NASA numbers**, and every choice has consequences.

- **Two missions.** The full one lasts 28 days: one whole lunar day, 14 of sunlight and 14 of night. The short
  one lasts 14 days: the last 7 of sunlight and the first 7 of night.
- **19 different decisions.** Their numbers come from the state of the base at that moment. Examples: will
  the crew reach the shelter before the solar particles (distance ÷ speed against a 15–30 minute warning)?
  What should be switched off when night falls and the 10 kW reactor can't power everything?
- **Explained afterwards.** After each decision the game shows the math, so the player sees why the best
  option is the best.
- **Seven daily tasks, always shown** (mouse only, with sound): harvest, oxygen leaks, radiation sweep, ice drilling,
  crew break, cargo stowing and solar panels. A task that can't be done today stays visible, greyed out, with the reason. Your score changes how much the task yields. The longer ones
  (35 to 45 s) adapt to the player: the level rises with good play, so a 7-year-old and an adult are both
  challenged.
- **English and Spanish.** Switch the language on the title screen.
- **Challenge resources.** DONKI (space weather), RadLab/OSDR (dose units), APOD (menu backgrounds) and CSA pages (food, exercise). Round **?** buttons open fun facts in the menu, the central panel and under each task.
- **Real space weather from NASA DONKI.** Every solar storm in the game is based on a real flare recorded by
  NASA (its class and date), and the shielding decision shows the real Sun: **live** (last 30 days) when
  there is internet, or clearly labelled **saved data** when there isn't.
- **Real data, with sources.** Every real number is listed with its link in [DATOS_NASA.md](DATOS_NASA.md),
  and on the in-game "NASA data" screen.

### How to run it

Requires Python 3.10+ (tested with 3.13).

```
pip install -r game/requirements.txt
python -m game.main
```

(run from the project root, the folder that contains `game/`). On Windows you can also double-click `JUGAR.bat`. Keys: **F11** fullscreen · **ESC** back or quit ·
**F12** saves a screenshot to `~/.mision_lunar/capturas`.

### How to check it

```
python game/tools/verificar.py
```

It checks every decision, every minigame and the balance, and must end with **TODO OK**. A quick balance
test where the computer plays 200 missions in a few seconds:
`python game/tools/simular_misiones.py 200` (add `--corta` for the short mission).

**Not affiliated with or endorsed by NASA.** No NASA logos or branding are used.

---

## Español

Chicos de 7 a 12 años administran una base en la Luna con 4 tripulantes durante 14 o 28 días. Equilibran
**oxígeno, agua, energía, comida, radiación recibida y ánimo de la tripulación**. Cada día llega una decisión
que es un **problema de matemática con números reales de la NASA**, y cada decisión tiene consecuencias.

![Tablero de la base](docs/capturas/tablero.png)

### Cómo se juega un día

1. **Mañana:** mirar los 6 indicadores y el reporte. Los sistemas se encienden y apagan con un clic.
2. **Decisión:** un problema con números reales. Después el juego explica las cuentas.
3. **Tarea:** las 7 tareas aparecen siempre: cosecha, fugas de oxígeno, barrido de radiación, perforar hielo, recreo (fotos a la Tierra), estiba de la carga y paneles solares. Si una no se puede hoy, se ve apagada con el motivo. El botón **?** de cada una explica la tarea.
   Cada una es un microjuego con sonido (se pueden apagar). Los largos (de 35 a 45 s) se adaptan a quien juega: el
   nivel sube si se juega bien, así un niño de 7 años y un adulto tienen cada uno su reto.
4. **Cierre:** la base consume y produce; se ve qué subió y qué bajó.

Se pierde si se acaba el oxígeno, el agua o la comida, si la radiación pasa el límite de la misión (250 mSv) o
si el ánimo llega a cero.

![Una decisión](docs/capturas/decision.png)

### Cómo abrirlo

Hace falta Python 3.10 o más nuevo (probado con 3.13).

```
pip install -r game/requirements.txt
python -m game.main
```

(desde la carpeta que contiene `game/`). En Windows también se puede dar doble clic a `JUGAR.bat`.

### Para el equipo: cómo hacer o mejorar un microjuego

Aquí están los cuatro nuestros: `oxigeno`, `hielo`, `recreo` y `estiba`. Los demás los hace el resto del equipo; mientras no estén aquí, esas tareas se hacen solas. Cada quien trabaja en
**su propio archivo** y el juego lo encuentra solo. La guía completa está en
[game/minijuegos/LEEME.md](game/minijuegos/LEEME.md).

1. Para uno nuevo, copiar `game/minijuegos/_plantilla.py` con otro nombre (por ejemplo `mi_juego.py`).
2. Llenar las 4 partes marcadas con **HACER**.
3. Probarlo solo: `python game/tools/probar_microjuego.py huerto`
4. Antes de subirlo: `python game/tools/verificar.py` tiene que decir **TODO OK**.

Los nuestros (`oxigeno`, `hielo`, `recreo`
y `estiba`) usan el kit `game/minijuegos/_kit.py`: cuenta regresiva, niveles que se adaptan, combo,
efectos y la tarjeta final con estrellas.

### Qué hay en cada carpeta

| Carpeta o archivo | Qué es |
|---|---|
| `main.py` · `JUGAR.bat` | Para abrir el juego |
| `game/logica/simulador.py` | Las reglas de la base (sin pantalla) |
| `game/logica/decisiones.py` | Las 19 decisiones con su matemática |
| `game/data/datos_nasa.py` · `curiosidades.py` | Los datos reales con su fuente |
| `game/logica/juego.py` · `game/escenas/` | Las pantallas |
| `game/minijuegos/` | La plantilla, el ejemplo y los microjuegos del equipo |
| `game/assets/textos.py` · `textos_en.py` | Los textos: español y su traducción al inglés |
| `game/tools/` | Bajar DONKI y RadLab, verificador, simulador del balance y probador de microjuegos |

**No está afiliado a la NASA ni respaldado por ella.** No usa sus logos ni su marca. Créditos en
[CREDITOS.md](CREDITOS.md).
