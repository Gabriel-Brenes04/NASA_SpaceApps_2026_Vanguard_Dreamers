# NASA_SpaceApps_2026_Vanguard_Dreamers
Proyecto para presentar el día domingo 15 de noviembre.

# Mission Survival

**Junior astronaut mission simulator · Simulador de misión para astronautas junior**
NASA Space Apps Challenge 2026 · Team Vanguard Dreamers


---

## English

Kids aged 7 to 12 run a lunar outpost with 4 crew members for 14 or 28 days. They balance **oxygen, water,
energy, food, radiation dose and crew morale**. Every day brings a decision, and every choice has consequences.

- **Two missions.** The full one lasts 28 days: one whole lunar day, 14 of sunlight and 14 of night. The short
  one lasts 14 days: the last 7 of sunlight and the first 7 of night.
- **19 different decisions.** Their numbers come from the state of the base at that moment.
- **Explained afterwards.** After each decision the game shows the math, so the player sees why the best  option is the best.
- **Eight daily tasks**: harvest, oxygen leaks, radiation sweep, ice drilling, crew break, cargo stowing and solar panels.
- **English and Spanish.** Switch the language on the title screen.
- **Challenge resources.** DONKI (space weather), RadLab/OSDR (dose units), APOD (menu backgrounds) and CSA pages (food, exercise). Round **?** buttons open fun facts in the menu, the central panel and under each task.
- **Real space weather from NASA DONKI.** Every solar storm in the game is inspired on a real flare recorded by NASA.
- **Real data, with sources.** Every real source is listed with its link in [DATOS_NASA.md](DATOS_NASA.md),
  and on the in-game "NASA data" screen.

### How to run it

Requires Python 3.10+

```
pip install -r game/requirements.txt
python -m game.main
```

(run from the project root, the folder that contains `game/`). On Windows you can also double-click `JUGAR.bat`. Keys: **F11** fullscreen · **ESC** back or quit ·

### How to check it

```
python game/tools/verificar.py
```

It checks every decision, every minigame and the balance, and must end with **TODO OK**. A quick balance test where the computer plays 200 missions in a few seconds:
`python game/tools/simular_misiones.py 200` (add `--corta` for the short mission).


---

## Español

Niños de 7 a 12 años administran una base en la Luna con 4 tripulantes durante 14 o 28 días. Equilibran
**oxígeno, agua, energía, comida, radiación recibida y ánimo de la tripulación**. Cada día llega una decisión, y cada decisión tiene consecuencias.

### Cómo se juega un día

1. **Mañana:** mirar los 6 indicadores y el reporte. Los sistemas se encienden y apagan con un clic.
2. **Decisión:** un problema de decisión y manejo de recursos.
3. **Tarea:** las 7 tareas: cosecha, fugas de oxígeno, barrido de radiación, perforar hielo, recreo (fotos a la Tierra), estiba de la carga y paneles solares. Cada una es un microjuego. 
4. **Cierre:** la base consume y produce; se ve qué subió y qué bajó.

Se pierde si se acaba el oxígeno, el agua o la comida, si la radiación pasa el límite de la misión (250 mSv) o si el ánimo llega a cero.


### Cómo abrirlo

Hace falta Python 3.10+

```
pip install -r game/requirements.txt
python -m game.main
```

(desde la carpeta que contiene `game/`). En Windows también se puede dar doble clic a `JUGAR.bat`.

### Qué hay en cada carpeta

| Carpeta o archivo | Qué es |
|---|---|
| `main.py` · `JUGAR.bat` | Para abrir el juego |
| `game/logica/simulador.py` | Las reglas de la base (sin pantalla) |
| `game/logica/decisiones.py` | Las 19 decisiones con su matemática |
| `game/data/datos_nasa.py` · `curiosidades.py` | Los datos reales con su fuente |
| `game/logica/juego.py` · `game/escenas/` | Las pantallas |
| `game/minijuegos/` | La plantilla, el ejemplo y los microjuegos |
| `game/assets/textos.py` · `textos_en.py` | Los textos: español y su traducción al inglés |
| `game/tools/` | Bajar DONKI y RadLab, verificador, simulador del balance y probador de microjuegos |

Créditos en [CREDITOS.md](CREDITOS.md).