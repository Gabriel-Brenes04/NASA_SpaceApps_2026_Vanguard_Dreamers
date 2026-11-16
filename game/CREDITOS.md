# Créditos · Credits

## Mission Survival · Base Lunar

Juego hecho por el equipo **Vanguard Dreamers** para el NASA Space Apps Challenge 2026.
Game made by team **Vanguard Dreamers** for the NASA Space Apps Challenge 2026.

## Recursos del reto que usa el juego · Challenge resources used

| Recurso · Resource | Para qué lo usa el juego · What the game does with it |
|---|---|
| **NASA CCMC · DONKI** https://ccmc.gsfc.nasa.gov/tools/DONKI/ (Moon to Mars Space Weather Analysis Office) | Cada tormenta solar del juego se basa en una fulguración real (clase, fecha, región, partículas). Guardadas en `data/donki.json`. Each in-game solar storm is based on a real flare. |
| **NASA OSDR · RadLab** https://visualization.osdr.nasa.gov/radlab/ | Unidades (µGy/h, µSv/h), instrumentos y lugares de medición; la decisión «El dosímetro de la base». Si existe `data/radlab.json` (se baja con `tools/bajar_radlab.py`) usa mediciones reales. Units, instruments and places; real values only if `radlab.json` exists. |
| **NASA Open APIs · APOD** https://api.nasa.gov/ | Los fondos del menú son imágenes astronómicas del día, con su título, fecha y crédito. Menu backgrounds are Astronomy Pictures of the Day, with credit. |
| **CSA · Eating / Physical activity / Relaxing in space; Food production on the Moon** https://www.asc-csa.gc.ca/eng/astronauts/living-in-space/ | Calorías, ejercicio, pérdida de hueso, vueltas a la Tierra, cultivo de comida. Calories, exercise, bone loss, orbits per day, growing food. |

Los parámetros de diseño que no vienen de esa lista (cuánto oxígeno respira una persona, etc.) están en
`DATOS_NASA.md`, sección B. Design parameters outside that list are in `DATOS_NASA.md`, section B.

## Letra · Font

**Press Start 2P**, de/by CodeMan38 (Cody "CodeMan38" Boisclair).
Copyright 2012 The Press Start 2P Project Authors.
Licencia / License: **SIL Open Font License 1.1**. Archivo / File: `game/assets/fuentes/OFL.txt` (si se incluye / if bundled).
Fuente / Source: https://fonts.google.com/specimen/Press+Start+2P — sin modificar / unmodified.

## Sonido e imágenes · Sound and graphics

Los efectos se generan con código (numpy) y los gráficos se dibujan con código (pygame). Las únicas imágenes de
terceros son las de APOD guardadas para el menú, cada una con su crédito en su ficha.
Sound is synthesized in code and graphics are drawn in code; the only third-party images are the saved APOD
pictures, each credited in its metadata.



## Use of Super Intelligence (SI)

Super Intelligence tools were used throughout the development of Mission Survival to support the team in several areas:

Research and Information Gathering: AI tools assisted in exploring scientific concepts, researching relevant information, and identifying resources related to the project's objectives.

Data Analysis and Interpretation: AI assisted in understanding, organizing, interpreting, and explaining scientific data obtained from NASA resources.

Coding, Debugging, and Troubleshooting: AI tools were used to assist with Python programming, code development, debugging, error identification, and technical problem-solving.

Translation: AI-assisted translation was used to improve communication and adapt project documentation and content between languages.

Image Creation: AI tools were used to generate some visual assets incorporated into the project.

Audio Creation: AI tools were used to generate or assist in the creation of audio elements used in the game.

AI tools served as supporting resources throughout development. The team remained responsible for project decisions, implementation, integration, testing, and final validation.

