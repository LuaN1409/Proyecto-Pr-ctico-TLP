# Documentación Técnica

**Proyecto Práctico TLP — Entrega 2: Motor de Juego y Renderizado**

---

## 1. Introducción

El presente documento describe el diseño, arquitectura y funcionamiento del **motor de juego** desarrollado en Python 2.7, correspondiente a la **segunda entrega** del Proyecto Práctico de la asignatura **Teoría de Lenguajes de Programación**.

Este motor constituye la base sobre la cual se ejecutarán los juegos definidos mediante el lenguaje **BRIK**, analizado en la Entrega 1.
Su propósito es proveer un entorno **independiente de la lógica de los juegos** (como _Snake_ y _Tetris_) capaz de manejar:

- **Inicialización del entorno gráfico.**
- **Bucle principal (Game Loop).**
- **Renderizado de elementos visuales.**
- **Gestión de entradas del usuario.**

La implementación se diseñó bajo un enfoque modular, garantizando compatibilidad con **Windows XP y Python 2.7**, sin dependencias externas, utilizando únicamente la biblioteca estándar `tkinter`.

---

## 2. Arquitectura General del Motor

El motor sigue una **estructura modular** dividida en tres componentes principales:

| Módulo             | Función Principal                                                                                 |
| ------------------ | ------------------------------------------------------------------------------------------------- |
| `motor_runtime.py` | Núcleo del sistema. Implementa el bucle de juego y la integración de módulos.                     |
| `render.py`        | Encargado del manejo gráfico: creación de la ventana, dibujo de elementos y actualización visual. |
| `input.py`         | Responsable de la gestión de entradas del usuario mediante teclado.                               |

El siguiente diagrama resume la relación entre los módulos:

```
         +-------------------+
         |  motor_runtime.py |
         +-------------------+
                   |
     +-------------+-------------+
     |                           |
+------------+             +-------------+
|  render.py |             |  input.py   |
+------------+             +-------------+
     |                           |
     |---> Dibujar objetos        |---> Detectar teclas
```

---

## 3. Ciclo de Ejecución (Game Loop)

El **bucle principal del juego** se implementa en `motor_runtime.py` y sigue la estructura clásica de tres fases:

1. **Entrada (Input):**

   - Lee las teclas presionadas mediante el módulo `input.py`.
   - Interpreta acciones del usuario (por ejemplo, mover hacia arriba, abajo, izquierda o derecha).

2. **Lógica (Update):**

   - Actualiza el estado interno del juego según las entradas recibidas.
   - En esta versión de demostración, modifica la posición del ladrillo.

3. **Renderizado (Render):**

   - Limpia la pantalla anterior.
   - Dibuja los elementos actualizados mediante `render.py`.
   - Refresca la ventana a ~60 FPS.

El ciclo se repite continuamente hasta que el usuario presiona la tecla **Escape**, que detiene el motor y cierra la ventana.

---

## 4. Módulo `render.py` — Renderizado Gráfico

### Descripción

Este módulo utiliza **Tkinter** para crear y controlar la ventana gráfica del motor.
Su objetivo es proveer una capa de abstracción visual que permita dibujar objetos básicos (como bloques, textos o elementos de HUD).

### Funciones Principales

| Función                                  | Descripción                                                   |
| ---------------------------------------- | ------------------------------------------------------------- |
| `__init__(self, titulo)`                 | Crea una ventana de 640×480 píxeles con título personalizado. |
| `limpiar()`                              | Borra todos los elementos dibujados del frame anterior.       |
| `dibujar_ladrillo(x, y, color, tam)`     | Dibuja un bloque rectangular (representa sprites o piezas).   |
| `dibujar_texto(x, y, texto, color, tam)` | Muestra texto informativo (puntuaciones, mensajes, etc.).     |
| `actualizar()`                           | Refresca el lienzo y mantiene la ventana activa.              |
| `cerrar()`                               | Cierra la ventana y libera recursos.                          |

### Ejemplo Interno

```python
motor.dibujar_ladrillo(200, 100, "red", 40)
motor.dibujar_texto(320, 30, "Presiona flechas para mover", "yellow")
```

---

## 5. Módulo `input.py` — Control de Entradas

### Descripción

Gestiona la interacción del usuario mediante las teclas del teclado.
Asocia eventos de **KeyPress** y **KeyRelease** del sistema `tkinter` a un conjunto interno de teclas activas.

### Funciones Principales

| Función               | Descripción                                                                |
| --------------------- | -------------------------------------------------------------------------- |
| `__init__(root)`      | Inicializa el sistema de escucha de teclas dentro de la ventana del motor. |
| `_presionar(evento)`  | Registra la pulsación de una tecla.                                        |
| `_soltar(evento)`     | Elimina la tecla del conjunto activo cuando se libera.                     |
| `tecla_activa(tecla)` | Devuelve `True` si la tecla indicada está presionada.                      |

### Ejemplo Interno

```python
if entrada.tecla_activa("Left"):
    x -= velocidad
if entrada.tecla_activa("Right"):
    x += velocidad
```

El sistema permite controlar cualquier elemento en pantalla, como piezas o personajes, de acuerdo con los comandos definidos en los archivos `.brik` de cada juego.

---

## 6. Módulo `motor_runtime.py` — Núcleo del Motor

### Descripción

Define el **bucle de ejecución del motor** y la lógica mínima necesaria para mantener la interacción continua entre los módulos `input` y `render`.

### Flujo de Ejecución

```python
while corriendo:
    # 1. Lectura de entrada
    dx = dy = 0
    if entrada.tecla_activa("Left"): dx = -VELOCIDAD
    if entrada.tecla_activa("Right"): dx = VELOCIDAD
    if entrada.tecla_activa("Up"): dy = -VELOCIDAD
    if entrada.tecla_activa("Down"): dy = VELOCIDAD

    # 2. Actualización de posición
    POS_X += dx
    POS_Y += dy

    # 3. Renderizado
    motor.limpiar()
    motor.dibujar_ladrillo(POS_X, POS_Y, "red", 40)
    motor.actualizar()
```

El bucle incluye una pequeña pausa (`time.sleep(0.016)`) para estabilizar la velocidad de actualización (~60 FPS).

---

## 7. Relación con los Juegos Definidos en `.brik`

Los archivos `snake.brik` y `tetris.brik` definen la **estructura lógica y los parámetros configurables** de cada juego (niveles, colores, objetos, controles, etc.), mientras que el motor implementa la **capa de ejecución universal**.

| Capa                       | Responsable                                 | Función                                                           |
| -------------------------- | ------------------------------------------- | ----------------------------------------------------------------- |
| **BRIK (.brik)**           | Lenguaje de definición de juegos            | Describe la configuración: pantalla, controles, niveles, colores. |
| **Analizador (Entrega 1)** | `analizador.py`                             | Convierte el archivo `.brik` en un AST (JSON estructurado).       |
| **Motor (Entrega 2)**      | `motor_runtime.py`, `render.py`, `input.py` | Ejecuta la representación visual e interacción con el jugador.    |

Este diseño modular permitirá que, en la **Entrega 3**, el motor cargue dinámicamente los datos del AST generado por el analizador para construir los mundos de _Tetris_ y _Snake_ en tiempo de ejecución.

---

## 8. Diseño Modular y Extensibilidad

El motor está pensado para ser **ampliado fácilmente**:

- El módulo `render` puede incorporar nuevas funciones como `dibujar_pieza()`, `dibujar_serpiente()`, o soporte para sprites.
- `input` puede extenderse con mapeos personalizados de teclas, tal como se define en los archivos `.brik`.
- `motor_runtime` podrá leer los archivos AST generados y convertirlos en objetos visuales configurados automáticamente.

Gracias a esta estructura, el motor puede adaptarse a cualquier juego descrito con BRIK sin necesidad de modificar su núcleo.

---

## 9. Requisitos Técnicos

| Recurso                         | Especificación                                           |
| ------------------------------- | -------------------------------------------------------- |
| **Lenguaje**                    | Python 2.7.18 (32 bits)                                  |
| **Librerías externas**          | Ninguna (usa `tkinter`, parte de la biblioteca estándar) |
| **Compatibilidad**              | Windows XP, 7, 10                                        |
| **Resolución gráfica**          | 640 × 480 píxeles                                        |
| **Control de entrada**          | Teclado (flechas y tecla Escape)                         |
| **Frecuencia de actualización** | ~60 FPS                                                  |

---

**Autores:**
María José Restrepo Osorio
Diego Moncada Gómez

**Asignatura:** Teoría de Lenguajes de Programación
**Profesor:** Fernan Alonso Villa Garzón
**Entrega 2 — Motor de Juego y Renderizado**
