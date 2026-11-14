# Cómo hacer un microjuego para Base Lunar

Cada tarea del día puede ser un **microjuego** de 5 a 10 segundos que se juega **solo con el ratón**.
Lo bien que te vaya cambia cuánto rinde la tarea: de 0,4 (muy mal) a 1,3 (perfecto).

## Los que faltan

| Archivo | Tarea que reemplaza | Qué da | Idea |
|---|---|---|---|
| `huerto.py` | `cosecha` | comida | Arrastrar la gota de agua a las macetas que se marchitan |
| `paneles.py` | `regolito` o la que se acuerde | energía / blindaje | Girar el panel hasta la zona verde, de frente al Sol |
| `escudo.py` | `regolito` | blindaje | Clic cuando la barra pase por la zona segura |
| `oxigeno.py` | `oxigeno` | oxígeno | Clic en las grietas de la válvula, o seguir la lista de verificación |

`estrellas.py` (el recreo) ya está hecho: es el **ejemplo** para copiar ideas.
Las tareas que todavía no tienen microjuego se hacen solas, sin jugar.

> Ojo con `paneles` y `escudo`: hoy el simulador tiene las tareas `cosecha`, `oxigeno`, `regolito`,
> `hielo`, `recreo` y `estiba`. Si un microjuego necesita una tarea nueva (por ejemplo, «alinear los
> paneles» que dé energía), se agrega en `simulador.py`: avisen y se hace.

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
- **De 5 a 10 segundos** (`duracion`). Se acaba solo; si el jugador ya ganó, `self.terminar()`.
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
