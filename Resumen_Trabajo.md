# Proyecto-Practico-TLP

**Autores:** María José Restrepo Osorio · Diego Moncada Gómez

**Asignatura:** Teoría de Lenguajes de Programación

**Profesor:** Fernan Alonso Villa Garzón

---

## Resumen de lo hecho

En la primera parte construimos un analizador para el lenguaje BRIK. Ese analizador lee archivos `.brik` (por ejemplo `tetris.brik` y `snake.brik`), los tokeniza y arma un árbol de sintaxis (AST) que guardamos en `arbol.ast` como JSON. El trabajo fue: leer el texto fuente, reconocer cadenas, números, identificadores, operadores y booleanos, y validar que el archivo contenga los campos mínimos que esperamos para definir un juego (como `juego`, `titulo`, `pantalla`).

Con ese AST definido, diseñamos e implementamos el motor gráfico de la entrega 2. La idea fue construir un motor independiente de la lógica del juego: el analizador aporta los datos estructurados y el motor aporta la capa de ejecución —ventana, bucle, entrada y render— para poder ejecutar cualquier juego descrito con BRIK sin tocar el núcleo del motor.

---

## ¿Qué hace el motor?

El motor ejecuta un bucle clásico: lee entradas, actualiza estado y renderiza la pantalla a ~60 FPS. En la demo actual ese ciclo mueve un ladrillo rojo con las flechas y muestra un texto informativo arriba. Sirve para probar que la comunicación entre los módulos (entrada ↔ lógica ↔ render) funciona correctamente y que el motor puede servir como base para ejecutar juegos a partir de datos (el AST).

---

## Componentes principales

**motor_runtime.py**
Es el punto de entrada y coordina el bucle del juego. Lee las teclas activas, calcula la nueva posición del ladrillo, aplica límites y llama a `render` para dibujar.

**render.py**
Se encarga de crear la ventana (640×480) y de las operaciones de dibujo básicas: limpiar, dibujar ladrillos y texto, y actualizar el lienzo. Está implementado con `tkinter` para mantener compatibilidad con Python 2.7 y Windows XP.

**input.py**
Gestiona las pulsaciones y liberaciones de teclas usando eventos de `tkinter`. Mantiene un conjunto de teclas activas y expone `tecla_activa(tecla)` para consultar el estado en cualquier momento.

**Analizador (Entrega 1)**
Tokenizer + Parser que convierten `.brik` en `arbol.ast` (JSON). Es la pieza que transforma la definición textual del juego en datos estructurados que el motor puede consumir.

---

## Cómo probarlo

Para verificar el funcionamiento del motor existen dos alternativas:

1. **Ejecutable (.exe):**
   Se puede ejecutar directamente desde el archivo `Ejecutable/motor_runtime.exe`.
   Es posible que Windows muestre una advertencia debido a que el archivo no está firmado digitalmente. En caso de duda, se recomienda analizarlo con **VirusTotal** o permitir su ejecución desde la ventana de **Propiedades → Desbloquear**.

2. **Ejecución desde código:**
   Instalar **Python 2.7.18 (32 bits)** y, desde la carpeta raíz del proyecto, ejecutar el siguiente comando en la terminal:

   ```bash
   python motor_runtime.py
   ```

   Al iniciar, se abrirá una ventana de **640×480 píxeles** donde se visualizará un ladrillo rojo que puede moverse utilizando las teclas de dirección.
   El programa finaliza al presionar la tecla **Escape**.

---

## Archivos incluidos

- `motor_runtime.py` - bucle y coordinación.
- `render.py` - render y ventana.
- `input.py` - gestor de teclado.
- `Analizador.py` - tokenizer + parser (Entrega 1).
- `arbol.ast` - ejemplo de salida del analizador (JSON).
- `Ejecutable/` - ejecutable empaquetado.
- `build/` - Carpeta temporal de compilación que guarda los archivos intermedios, scripts y binarios
  necesarios mientras se construyó el ejecutable con PyInstaller.
- `snake.brik` - Define la estructura, reglas y mecánicas de una versión extendida del juego Snake (Entrega 1).
- `tetris.brik` - Define la estructura, reglas y mecánicas de una versión extendida del juego Tetris (Entrega 1).

---

## Requisitos y compatibilidad

- **Python:** 2.7.18 (32 bits) - elegimos esta versión por compatibilidad con Windows XP.
- **Dependencias externas:** ninguna (se usa `tkinter`, que viene con Python).
- **Plataformas:** diseñado para Windows XP; funciona en Windows 7/10 si ejecutas con Python 2.7.
- **Resolución demo:** 640×480.
- **Controles:** flechas para mover, Escape para salir.

---
