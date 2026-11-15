# Cómo hacer un microjuego para Base Lunar

Cada tarea del día puede ser un **microjuego** de 5 a 45 segundos que se juega **solo con el ratón**.
Lo bien que te vaya cambia cuánto rinde la tarea: de 0,4 (muy mal) a 1,3 (perfecto).

## Los que hay

| Archivo | Tarea que reemplaza | Qué da | Idea |
|---|---|---|---|
| `oxigeno.py` | `oxigeno` | oxígeno | Sellar fugas antes de que se rajen las tuberías; la presión baja más rápido entre más fugas haya (y sube sola sin fugas); cada tanque lleno = 1 astronauta, 1 día (40 s) |
| `hielo.py` | `hielo` | agua | Llevar el vehículo por un suelo con lomitas y cráteres, perforar y soltar dentro de las bolsas de hielo; desde el nivel 3, radar (38 s) |
| `recreo.py` | `recreo` | ánimo | Tomarle fotos a la Tierra con zoom (apretar y soltar): relámpagos, auroras, huracanes, cometas, naves y encargos (hasta Costa Rica) (40 s) |
| `estiba.py` | `estiba` | más carga del cohete | Soltar las bolsas en su sección (3 × 6) sin dejar huecos; se pueden cambiar por las de la cinta; las secciones llenas se sellan (solo el día que llega el cohete) (45 s) |
| `huerto.py` | `cosecha` | comida | Regar con la regadera (clic apretado) y llenarla en la llave del agua reciclada; cosechar las plantas que brillan antes de que se pasen; calor en el domo, plantas doradas y más macetas al subir de nivel (40 s) |

Los paneles (`solaris/`) y el barrido de radiación (`barrido_orbital/`) los hizo el resto del equipo.

### Los largos usan el kit (`_kit.py`)

`oxigeno`, `hielo`, `recreo`, `estiba` y `huerto` duran de 35 a 45 s y heredan de `Partida` (en `_kit.py`) en vez de
`Microjuego`. El kit trae hecho:

- la cuenta regresiva 3-2-1-¡YA! con la instrucción grande, y la tarjeta final con puntos y 1 a 3 estrellas;
- un **nivel que se adapta** (1 a 8): sube con los aciertos y baja con los errores. Así un niño de 7 años y un
  adulto juegan cada uno a su medida;
- puntos con **combo** (aciertos seguidos multiplican ×2, ×3…), una nota musical que sube con cada acierto y
  los últimos 8 segundos con puntos dobles;
- efectos: chispas con brillo, anillos, textos que flotan, sacudidas y carteles;
- sonidos sintetizados (`sonido.play`, `sonido.bucle` para los que se repiten).

En vez de `iniciar/actualizar/dibujar` se llenan `preparar`, `jugar` (la lógica), `animar` (lo que se mueve
siempre) y `escena` (el dibujo); se gana con `self.ganar(...)`, se pierde con `self.perder(...)` y un clic al
aire se marca con `self.errar(x, y)`. El rendimiento sale solo de los puntos (`META`, en escala logarítmica).

> Las tareas del simulador son `cosecha`, `oxigeno`, `regolito`, `hielo`, `recreo`, `estiba` y `paneles`
> (esta última solo de día). Si un microjuego necesita una tarea nueva, se agrega en `simulador.py`.

## Paso a paso

1. Instalar lo necesario (una sola vez):
   ```
   pip install pygame-ce numpy
   ```
2. Copiar `_plantilla.py` con el nombre de tu microjuego, **sin el guion bajo**: `huerto.py`.
3. Llenar las 4 partes marcadas con **HACER**: `iniciar`, `actualizar`, `dibujar` y `rendimiento`.
4. Probarlo solo, sin jugar la misión entera:
   ```
   python tools/probar_microjuego.py huerto
   ```
5. Antes de subirlo, correr el verificador. Tiene que decir **TODO OK**:
   ```
   python tools/verificar.py
   ```
6. Jugarlo dentro del juego: `python main.py` → la tarea va a decir **«se juega»**.

No hay que tocar ningún otro archivo: el juego encuentra tu microjuego solo. Así cada quien trabaja en
su archivo y nadie le pisa el trabajo a nadie.

## Reglas

- **Solo `pygame-ce`.** Nada de otras librerías.
- **Solo el ratón:** `self.clics` (los clics de este cuadro), `self.raton` (dónde está) y `self.apretado`
  (si el botón está apretado, para arrastrar).
- **De 5 a 45 segundos** (`duracion`). Se acaba solo; si el jugador ya ganó, `self.terminar()`.
- **Velocidades por `dt`:** `x += velocidad * dt`. Así corre igual en cualquier computadora.
- **Dibujar dentro de `ZONA`** (x 40 a 1240, y 110 a 680). Arriba van el título y el reloj.
- **Números al azar con `self.rng`**, no con `random`.
- **El estado de la base (`self.base`) solo se lee.** Por ejemplo, de noche (`self.base.de_dia()` es
  `False`) el huerto puede verse más oscuro.
- **Nada bajado de internet** (imágenes, sonidos, letras) salvo que tenga licencia libre y se anote en
  `CREDITOS.md`. Lo más seguro: dibujar con `pygame.draw` (rect, circle, line, polygon).
- **Nada copiado de otros juegos ni de otros proyectos:** todo es nuevo y basado en la NASA.
- **Si usás un dato real** (por ejemplo, cuánta agua necesita una planta), anotá la fuente en un
  comentario. Si no se puede verificar, no se presenta como dato de la NASA.

## Cómo calcular el rendimiento

Una regla simple que funciona: contá aciertos y compará con una meta.

```python
def rendimiento(self):
    return 0.4 + 0.9 * min(1.0, self.aciertos / self.META)
```

Con 0 aciertos da 0,4; con la meta o más, 1,3. El verificador revisa que siempre quede entre 0,4 y 1,3.
