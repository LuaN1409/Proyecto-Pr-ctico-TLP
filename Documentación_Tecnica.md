# Documentación Técnica

**Proyecto Práctico TLP - Entrega 2: Motor de Juego y Renderizado**

**Autores:** María José Restrepo Osorio · Diego Moncada Gómez

---

## 1. Propósito del proyecto

El propósito del proyecto es separar la definición de un juego (datos) de su ejecución (motor).
Para eso se hicieron dos cosas:

- Un **analizador** que toma archivos `.brik` (texto donde se describen pantallas, objetos, controles) y produce un **AST** en formato JSON (`arbol.ast`), es decir: una representación estructurada y legible por programas.
- Un **motor** que lee esos datos y ejecuta la escena en pantalla: crea la ventana, procesa entradas del teclado, actualiza posiciones y dibuja objetos.

Hay una ventaja práctica ya que para cambiar un juego basta editar el `.brik` (o su AST). No hay que modificar el núcleo del motor.

---

## 2. Avance y qué hay hasta ahora

Estado actual del proyecto:

- **Analizador** (Entrega 1): completo. Lee `.brik`, tokeniza, parsea, valida campos básicos y guarda `arbol.ast`.
- **Motor** (Entrega 2): funcional. Contiene las piezas mínimas para ejecutar una demo:

  - Ventana 640×480.
  - Bucle principal (entrada → actualización → render).
  - Render de un ladrillo (bloque) y texto.
  - Gestión de entrada por teclado (flechas y Escape).

- **Empaquetado**: disponible un ejecutable en `Ejecutable/` para correr la demo sin instalar Python.

Carpetas/archivos clave del repositorio:

- `Analizador.py` → (Tokenizer + Parser) → produce `arbol.ast`

* `arbol.ast` → ejemplo de salida del analizador (JSON).
* `motor_runtime.py` → bucle y coordinación
* `render.py` → dibujo y ventana (tkinter)
* `input.py` → gestor de teclas
* `Ejecutable/motor_runtime.exe` → ejecutable empaquetado.
* `build/` → Carpeta temporal de compilación que guarda los archivos intermedios, scripts y binarios
  necesarios mientras se construyó el ejecutable con PyInstaller.
* `snake.brik` → Define la estructura, reglas y mecánicas de una versión extendida del juego Snake.
* `tetris.brik` → Define la estructura, reglas y mecánicas de una versión extendida del juego Tetris.

---

## 3. Idea clave y teoría esencial

### 3.1 Idea fundamental

Separar **datos** y **máquina de ejecución**:

- **Datos**: describen el juego (qué objetos, colores, controles, tamaño de pantalla). Se escriben en `.brik`.
- **Máquina**: el motor lee esos datos y se encarga de ejecutar el juego (mostrar y actualizar).

### 3.2 Por qué esto funciona

- Facilita reutilizar el motor para distintos juegos: El mismo motor puede ejecutar `snake.brik` o `tetris.brik` si recibe datos distintos.
- Simplifica pruebas: Se puede trabajar en el analizador por un lado y en el render/entrada por otro.
- Mejora mantenimiento: Cambios en un juego no requieren tocar el motor.

### 3.3 Conceptos que conviene entender

- **Token**: la unidad mínima que sale del texto; por ejemplo, una palabra, un número, una cadena entre comillas.
- **AST (árbol de sintaxis abstracta)**: estructura de datos (diccionario anidado en Python / JSON) que representa la información del `.brik`.
- **Game Loop**: el ciclo repetitivo que procesa entrada, actualiza estado y renderiza. Es la “batería” del motor.

---

## 4. El analizador

### Objetivo

Convertir un archivo de texto `.brik` en un archivo `arbol.ast` (JSON) que el motor pueda leer sin ambigüedades.

### Flujo interno del analizador

1. **Leer archivo**

   - `cargar_archivo(ruta)` abre el `.brik` y devuelve su contenido como texto (UTF-8).

2. **Tokenizar (Tokenizer / Lexer)**

   - Procesa el texto línea por línea.
   - Ignora líneas vacías y comentarios que comienzan con `#`.
   - Busca y clasifica:

     - cadenas entre comillas → `STRING`
     - números con o sin punto → `NUMBER`
     - símbolos `{ } [ ] = : ,` → `OPERATOR`
     - palabras → `IDENTIFIER` o `BOOLEAN` (true/false)

   - Resultado: una lista ordenada de tokens: por ejemplo `[('IDENTIFIER','juego'), ('OPERATOR','=') , ('STRING','snake'), ...]`.

3. **Parsear (Parser)**

   - Consume la lista de tokens y construye un diccionario anidado (AST).
   - Reconoce estructuras:

     - `clave = valor` (asignación simple)
     - `{ ... }` → bloque/diccionario
     - `[ ... ]` → lista
     - valores primitivos: cadena, número, booleano

   - Valida que existan campos esenciales: `juego`, `titulo`, `pantalla` (si faltan, lanza error con mensaje claro).

4. **Guardar AST**

   - Serializa el AST a JSON con `ensure_ascii=False` (preserva acentos/ñ).
   - Guarda el JSON en `arbol.ast` (UTF-8).

## 5. `motor_runtime.py`

### Propósito

Coordinar entrada, estado, render para ejecutar la demo y servir como base para juegos completos.

### Inicio del motor

- Crea el **Renderizador** (ventana y canvas).
- Crea el **Gestor de Entrada** y lo vincula a la ventana.
- Inicializa variables de estado (ej.: `POS_X`, `POS_Y`, `VELOCIDAD`).
- Muestra texto informativo en pantalla (ej.: "Usa las flechas...").

### El bucle principal

Cada iteración hace:

1. **Entrada**

   - Consulta el gestor: ¿qué teclas están presionadas?
   - Si `Escape` está presionada: salir.

2. **Cálculo/Actualización**

   - Calcula `dx` y `dy` según flechas.
   - `POS_X += dx`, `POS_Y += dy`.
   - Aplica límites: `POS_X = max(0, min(POS_X, ancho - tam))` (evita que salga de la ventana).

3. **Render**

   - `motor.limpiar()` borra el canvas.
   - `motor.dibujar_texto(...)` dibuja mensajes.
   - `motor.dibujar_ladrillo(POS_X, POS_Y, ...)` dibuja el bloque.
   - `motor.actualizar()` refresca la interfaz.

4. **Pausa**

   - `time.sleep(0.016)` para aproximar 60 FPS.

---

## 6. `input.py`

### Qué hace

Detecta qué teclas están presionadas en cada momento y permite consultarlo desde el motor.

### Cómo funciona

- Al crear el gestor, se hace `root.bind("<KeyPress>", _presionar)` y `root.bind("<KeyRelease>", _soltar)`.
- `_presionar(evento)` añade `evento.keysym` a un `set` llamado `teclas_presionadas`.
- `_soltar(evento)` elimina la tecla del `set` cuando se suelta.
- `tecla_activa(tecla)` devuelve si `tecla` está en el `set`.

### Ventajas de este enfoque

- **No bloqueante**: el motor no espera por eventos; simplemente pregunta el estado actual.
- **Sencillo** de mapear a controles definidos en el `.brik`.
- Funciona bien para controles por teclado en demos simples.

---

## 7. `render.py`

### Propósito

Encapsular toda la lógica de ventana y dibujo en un módulo simple y reutilizable.

### Elementos y cómo se usan

- **Creación de ventana**

  - Al instanciar `Renderizador`, se crea `tk.Tk()` y un `Canvas` con tamaño fijo (640×480).
  - `root.resizable(False, False)` bloquea el redimensionado para facilitar cálculos.

- **Primitivas de dibujo**

  - `limpiar()`: borra todo el contenido del canvas (`delete("all")`). Usar siempre antes de volver a dibujar un frame.
  - `dibujar_ladrillo(x, y, color, tam)`: dibuja un rectángulo; el motor usa esta primitiva para representar sprites o piezas.
  - `dibujar_texto(x, y, texto, color, tam)`: muestra información (instrucciones, puntaje).
  - `actualizar()`: llama a `update_idletasks()` y `update()` para que la ventana refresque inmediatamente.
  - `cerrar()`: destruye la ventana (`destroy()`), usado al terminar.

### Coordenadas y referencias

- Origen `(0,0)` está en la esquina superior izquierda.
- Al dibujar rectángulos se suele usar `(x,y)` como esquina superior izquierda y sumar `tam` para la esquina opuesta.

### Por qué `tkinter`

- Está incluida en Python 2.7 por defecto.
- No exige instalar librerías adicionales, lo que hace el proyecto más portable y compatible con máquinas antiguas.

---

## 8. Requisitos técnicos y compatibilidad

### Requisitos mínimos

- **Python:** 2.7.18 (32 bits) — la versión elegida por compatibilidad con Windows XP.
- **Librerías:** ninguna externa; se usa `tkinter` que viene con Python 2.7.
- **Sistema objetivo:** Windows XP; también funciona en Windows 7/10 si se usa Python 2.7.

### Recursos y rendimiento

- **Resolución inicial:** 640 × 480 (fija en la demo).
- **Control de entrada:** teclado (flechas para mover; Escape para salir).
- **Frecuencia de actualización:** aproximada a 60 FPS mediante `time.sleep(0.016)` — suficiente para demos simples sin requerimientos de alta performance.

### Ejecutable

- El ejecutable en `Ejecutable/` fue creado con PyInstaller. Windows puede advertir porque el `.exe` no está firmado. Si se prefiere evitar advertencias, ejecutar el script con Python en modo desarrollo.

- Si quiere ejecutar el juego desde la consola del proyecto directamente, debe tener Python 2.7.18 y abrir la consola del proyecto (ctrl + ñ) y luego escribir el comando:

ejecutar el siguiente comando en la terminal:

```bash
python motor_runtime.py
```
