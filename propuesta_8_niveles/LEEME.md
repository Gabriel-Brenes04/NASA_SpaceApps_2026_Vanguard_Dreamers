# Propuesta: 8 tareas (las dos huertas) + el mapa chiquito en el tablero

**Es una propuesta para revisar. No cambia nada del juego actual.** Todo está en esta carpeta. Si el equipo
la aprueba, se aplica con un solo comando (ver abajo).

## Qué propone

1. **Las dos huertas en el juego.** La huerta de Juan David sigue siendo la tarea «cosecha», sin cambios. La
   otra huerta (la de la regadera y la cosecha de lo que brilla) vuelve como una **tarea nueva, la octava**:
   **«Huerto Veggie» / «Veggie garden»**. El nombre viene del sistema Veggie de la NASA, con el que los
   astronautas cultivaron en la Estación la lechuga que se comieron en 2015.
2. **El mapa de la misión en chiquito, arriba en el tablero** (el menú de los indicadores), en lugar de la fila
   de bolitas. Con un clic, o con «Ver mapa», se abre el grande.

## Cómo probarla sin tocar nada

Doble clic en `JUGAR_propuesta.bat`, o desde la raíz del repositorio:

    python propuesta_8_niveles/probar_propuesta.py

Copia `game/` a una carpeta temporal, le pone encima los archivos de `archivos/` y abre esa copia. El juego
del repositorio no cambia.

## Qué cambia, archivo por archivo

| Archivo | Cambio |
|---|---|
| `game/minijuegos/veggie.py` | NUEVO (950 líneas). La otra huerta tal cual: solo cambian la tarea (`veggie`) y el título. |
| `game/logica/simulador.py` | +12 −5: la tarea en `TAREAS`, su título, su detalle, que necesite el invernadero y su efecto. |
| `game/logica/juego.py` | +5 −21: el color de la tarea nueva y el mapa chiquito en lugar de la fila de bolitas. |
| `game/data/curiosidades.py` | +12 −1: el «?» de la tarea nueva, con el dato de la lechuga de 2015 y su fuente. |
| `game/assets/textos_en.py` | +8: el inglés de todo lo nuevo. |
| `game/minijuegos/__init__.py` | +1 −1: «veggie» en `CONOCIDOS`, para el .exe. |

La tarea nueva da **+3 kg de comida y +5 de ánimo**, según cómo se juegue el minijuego, y necesita el
invernadero encendido, igual que la cosecha. Son números del juego, no datos de la NASA. Va de última, la 8,
así las teclas 1 a 7 de las otras tareas no cambian.

## Cómo aplicarla si se aprueba

Desde la raíz del repositorio (el parche está hecho sobre el commit 3a0021d):

    git apply propuesta_8_niveles/propuesta.patch

Después se puede borrar esta carpeta.

## Probado

- Verificador (`python game/tools/verificar.py`): todo bien, menos los textos en inglés que ya faltan hoy en
  el juego (ayudas «?», textos de la huerta…). Lo nuevo no suma ninguno.
- 30 misiones jugadas pantalla por pantalla, sin errores.
- El minijuego Veggie, jugado en ventana real.
- Fotos en `fotos/`: la pantalla de tareas con las 8, el tablero con el mapa chiquito y el resultado de la
  tarea Veggie, en español y en inglés.
