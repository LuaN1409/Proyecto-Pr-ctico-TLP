# Proyecto-Practico-TLP

Autores:
María José Restrepo Osorio
Diego Moncada Gómez

Asignatura: **Teoría de Lenguajes de Programación**
Profesor: **Fernan Alonso Villa Garzón**

---

## Sobre la Entrega 1

Este proyecto implementa un analizador léxico y sintáctico para **BRIK**, lenguaje diseñado para definir las reglas y configuraciones de los siguientes juegos:

- **Tetris.brik** — Una versión dimensional con piezas especiales y niveles progresivos.
- **Snake.brik** — Una versión extendida con frutas especiales, portales y obstáculos.

Respecto al analizador y sus componentes:

1. **Tokenizer (Lexer)**

   - Separa el código fuente en tokens (identificadores, números, cadenas, operadores y booleanos).
   - Usa expresiones regulares para reconocer patrones.
   - Ignora comentarios (`#`) y líneas vacías.

2. **Parser (Análisis Sintáctico)**

   - Construye una estructura jerárquica (AST) a partir de los tokens.
   - Reconoce bloques `{}`, listas `[]` y asignaciones `=` o `:`.
   - Valida la estructura básica del juego (`juego`, `titulo`, `pantalla`).

3. **Generador de AST**

   - El AST se guarda automáticamente como **arbol.ast** en formato JSON.
   - El analizador permite leer cualquier archivo `.brik`, procesarlo y generar su representación estructurada.

---

## Sobre la Entrega 2 — El Motor de Juego y Renderizado

La segunda entrega se centra en la implementación del **motor gráfico y de juego**.
El objetivo fue desarrollar un entorno capaz de mostrar elementos visuales, procesar entradas del usuario y mantener un bucle principal de ejecución — todo de forma **independiente de la lógica de los juegos específicos (Snake o Tetris)**.

### Componentes del motor

#### 1. `motor_runtime.py` — Bucle principal del juego

Implementa el **ciclo base del motor**, responsable de tres fases en cada frame:

1. **Gestión de eventos (Entrada):**

   - Detecta pulsaciones de teclas (flechas y tecla Escape).

2. **Actualización lógica:**

   - Modifica la posición del objeto en pantalla según la entrada del usuario.

3. **Renderizado:**

   - Dibuja los elementos (ladrillo y texto) en una ventana de 640×480 píxeles.

El bucle se ejecuta continuamente hasta que el usuario presiona la tecla _Escape_, garantizando una tasa aproximada de 60 FPS.

---

#### 2. `render.py` — Módulo de Renderizado

Maneja la **creación y actualización de la ventana** gráfica utilizando la librería estándar `tkinter` (inclusa en Python 2.7).
Proporciona funciones clave para la abstracción gráfica:

- `dibujar_ladrillo(x, y, color, tamaño)` — Dibuja un bloque en las coordenadas indicadas.
- `dibujar_texto(x, y, texto, color, tamaño)` — Muestra texto en pantalla (mensajes o puntuación).
- `limpiar()` — Borra el contenido previo antes de redibujar.
- `actualizar()` — Refresca el lienzo en cada ciclo.

Este módulo garantiza compatibilidad total con **Windows XP y Python 2.7**, sin dependencias externas.

---

#### 3. `input.py` — Control de Entradas

Administra la interacción del usuario mediante las teclas.
Usa los eventos de `tkinter` para registrar las pulsaciones y liberaciones en tiempo real.
Permite detectar si una tecla específica está activa mediante:

```python
entrada.tecla_activa("Left")
```

Las teclas soportadas en la demostración incluyen:

- **Flechas de dirección:** Mueven el ladrillo rojo.
- **Escape:** Finaliza la ejecución del motor.

---

### Diseño del Motor

El motor mantiene una estructura modular, dividida en tres capas:

1. **Entrada:** Captura las acciones del usuario.
2. **Lógica:** Interpreta la entrada y actualiza el estado interno.
3. **Render:** Dibuja el resultado visual.

Esta arquitectura se inspira en los principios de **Game Loop** y **abstracción por capas**, permitiendo en futuras entregas reemplazar o extender los módulos sin alterar la base.

---

### Ejecución

Para probar el motor:

```bash
python motor_runtime.py
```

Se abrirá una ventana de 640×480 con un ladrillo rojo que se puede mover con las flechas.
El sistema renderiza texto en la parte superior y se cierra con la tecla **Escape**.

---

### Compatibilidad

- Lenguaje: **Python 2.7.18 (32 bits)**
- Librerías externas: **Ninguna (usa solo `tkinter`)**
- Sistemas compatibles: **Windows XP, Windows 7, Windows 10**

---

### Entregables de la Fase 2

- `motor_runtime.py` — Bucle del juego y lógica básica.
- `render.py` — Sistema de renderizado.
- `input.py` — Control de entradas del usuario.
- `README.md` — Documentación técnica y de ejecución.

---

### Próximos pasos (para la Entrega 3)

En la siguiente fase, se integrará este motor con los juegos definidos en los archivos `.brik`, de modo que el motor pueda cargar dinámicamente las configuraciones (pantalla, objetos, niveles) y renderizarlas de manera automática.

---
