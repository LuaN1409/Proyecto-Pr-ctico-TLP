
MOTOR BRIK v3.0
Proyecto Práctico Entrega 3
                    
DESCRIPCIÓN GENERAL

El Motor BRIK es un sistema completo de desarrollo de juegos que permite
definir juegos de ladrillos (Snake y Tetris) usando un lenguaje propio
llamado BRIK. El proyecto cumple con las restricciones técnicas de caber
en un disquete de 1.44 MB y ejecutarse en hardware limitado (AMD Athlon XP
con Windows XP).

El sistema consta de tres componentes principales:

  • LENGUAJE BRIK: Lenguaje de alto nivel para definir juegos
  • COMPILADOR: Traduce archivos .brik a JSON ejecutable
  • RUNTIME: Motor que ejecuta los juegos compilados


2. CARACTERÍSTICAS DEL PROYECTO

Características técnicas:
  Lenguaje propio con sintaxis declarativa
  Compilador con análisis léxico y sintáctico completo
  Tabla de símbolos implícita en formato JSON
  Motor de renderizado con Tkinter
  Sistema de niveles dinámico
  Detección de colisiones precisa
  Manejo de eventos de teclado en tiempo real


Requisitos cumplidos:
  Tamaño total < 1.44 MB
  Compatible con Python 2.7
  Funciona en Windows XP
  Hardware: AMD Athlon XP o superior


ARQUITECTURA DEL SISTEMA

El sistema sigue el modelo de compilación e interpretación clásico:


Componentes del sistema:

compiler.py:                                                 
 Tokenizer: Análisis léxico                                
 Parser: Análisis sintáctico                               
 Validador: Verifica estructura del juego                  
 Generador: Produce JSON ejecutable                        


runtime.py                                                  

 MenuInicio: Selector de juegos                            
 Juego: Clase base del motor                               
 SnakeEngine: Lógica específica de Snake                   
 TetrisEngine: Lógica específica de Tetris                 
 Renderer: Sistema de dibujado (Tkinter)                   
 InputHandler: Manejo de teclado                          

LENGUAJE BRIK

BRIK es un lenguaje declarativo diseñado específicamente para definir
juegos de ladrillos. Su sintaxis es simple e intuitiva.

Características del lenguaje:
  Sintaxis tipo clave = valor
  Soporta: strings, números, booleanos, bloques y listas
  Comentarios con #
  Estructuras anidadas con { } y [ ]
  Separadores flexibles: = o : para asignaciones

Tipos de datos:
  
  STRING:     "texto"
  NUMBER:     42, 3.14
  BOOLEAN:    true, false
  BLOQUE:     { clave = valor, ... }
  LISTA:      [ valor1, valor2, ... ]

Ejemplo de código BRIK:

  # Comentario
  juego = "snake"
  titulo = "Snake Dimensional"
  
  pantalla = {
      ancho = 30,
      alto = 20,
      color_fondo = "negro"
  }
  
  serpiente = {
      color_cabeza = "verde_claro",
      longitud_inicial = 3,
      posicion_inicial = [15, 10]
  }
  
  frutas = {
      manzana = {
          color = "rojo",
          puntos = 10
      }
  }


USO DEL COMPILADOR

El compilador traduce archivos .brik a JSON ejecutable por el runtime.

Sintaxis:
  python compiler.py <archivo.brik>

Ejemplos:
  python compiler.py snake.brik
  python compiler.py tetris.brik

Salida exitosa:

  COMPILACION EXITOSA

  [OK] JSON generado: games/snake.json
       Tamaño: 2847 bytes

Mensajes de error comunes:

  • "Archivo no encontrado"
    → Verificar que el archivo exista en games/
    
  • "Se esperaba '=' después de 'campo'"
    → Falta operador de asignación
    
  • "Tipo de juego inválido"
    → El campo 'juego' debe ser "snake" o "tetris"
    
  • "Falta campo obligatorio: 'pantalla'"
    → Agregar la sección pantalla = { ... }


USO DEL RUNTIME

El runtime es el motor que ejecuta los juegos compilados.

Ejecución:
  
  Windows:
    • Doble clic en: jugar.bat
    • O desde CMD: python runtime.py
  
  Linux/macOS:
    $ python2 runtime.py

Flujo de ejecución:

  1. Se muestra un menú con los juegos disponibles
  2. Usuario selecciona Snake o Tetris
  3. El runtime carga el JSON correspondiente
  4. Se inicializa el motor de juego
  5. Comienza el loop principal (50ms por frame)
  6. El juego responde a inputs del usuario
  7. Al terminar, muestra puntuación y cierra

Controles generales:
  
  P           → Pausar/Reanudar
  ESC         → Salir del juego

Controles de Snake:
  
  ↑ ↓ ← →    → Mover serpiente

Controles de Tetris:
  
  ↑           → Rotar pieza
  ↓           → Acelerar caída
  ← →         → Mover horizontalmente
  ESPACIO     → Caída instantánea (hard drop)


GRAMÁTICAS BNF

Las gramáticas formales del lenguaje BRIK están definidas en formato BNF
(Backus-Naur Form) en la carpeta gramaticas_bnf/.

Archivos:
  • snake.bnf   → Gramática para juegos Snake
  • tetris.bnf  → Gramática para juegos Tetris

Reglas principales:

  <programa> ::= <lista_de_asignaciones>
  
  <asignacion> ::= <identificador> "=" <valor>
  
  <valor> ::= <string>
            | <numero>
            | <booleano>
            | <bloque>
            | <lista>
  
  <bloque> ::= "{" <contenido_bloque> "}"
  
  <lista> ::= "[" <contenido_lista> "]"

Las gramáticas completas incluyen todas las producciones necesarias para
reconocer la sintaxis del lenguaje BRIK.

JUEGOS INCLUIDOS

SNAKE DIMENSIONAL

Descripción:
  Versión mejorada del clásico Snake con mecánicas especiales.

Características:
  • 3 niveles de dificultad creciente
  • Sistema de frutas con diferentes valores
  • Frutas especiales con tiempo límite
  • Velocidad incrementa por nivel
  • Paredes sólidas por defecto

Tipos de frutas:
  
    MANZANA (rojo)
     • Puntos: 10
     • Disponibilidad: Siempre
     • Crece: 1 segmento
  
    BANANA (amarillo)
     • Puntos: 50
     • Tiempo de vida: 5 segundos
     • Probabilidad: 15%
     • Bonus de puntos extra
  
    FRESA (rosa)
     • Puntos: 20
     • Tiempo de vida: 6 segundos
     • Probabilidad: 10%
     • Efecto: ralentiza temporalmente

Sistema de niveles:
  
  Nivel 1 - Inicio:
    • Velocidad: 200ms
    • Frutas requeridas: 10
    
  Nivel 2 - Portal:
    • Velocidad: 150ms
    • Frutas requeridas: 15
    
  Nivel 3 - Caos:
    • Velocidad: 100ms
    • Frutas requeridas: 20

Puntuación:
  • Fruta normal: 10 pts
  • Fruta especial: 20-50 pts
  • Bonus por nivel completado

TETRIS DIMENSIONAL

Descripción:
  Implementación clásica de Tetris con 7 piezas estándar.

Características:
  • 7 tetrominos clásicos (I, O, T, S, Z, J, L)
  • Sistema de rotación completo
  • Hard drop (caída instantánea)
  • Puntuación por cantidad de líneas
  • 3 niveles con velocidad creciente

Piezas:
  
  I (cyan)      - Línea vertical/horizontal
  O (amarillo)  - Cuadrado 2x2
  T (magenta)   - Forma de T
  S (verde)     - Forma de S
  Z (rojo)      - Forma de Z
  J (azul)      - Forma de J
  L (naranja)   - Forma de L

Sistema de puntuación:
  
  1 línea   →  100 puntos
  2 líneas  →  300 puntos
  3 líneas  →  500 puntos
  4 líneas  →  800 puntos (TETRIS!)

Niveles:
  
  Nivel 1 - Inicio:
    • Velocidad: 1000ms
    • Líneas requeridas: 10
    
  Nivel 2 - Intermedio:
    • Velocidad: 700ms
    • Líneas requeridas: 15
    
  Nivel 3 - Avanzado:
    • Velocidad: 400ms
    • Líneas requeridas: 20

Restricciones de diseño:
  
  Máximo 1.44 MB
  Compatible con Python 2.7
  Funciona en Windows XP
  Hardware mínimo: AMD Athlon XP

Compatibilidad:
  
  Windows XP / 7 / 8 / 10 / 11
  Linux (cualquier distribución moderna)
  macOS 10.8+

================================================================================

Proyecto Práctico - Entrega 3
Teoría de Lenguajes de Programación (TLP)
Universidad Nacional de Colombia
Sede Medellín 

Tecnologías utilizadas:
  • Lenguaje: Python 2.7
  • GUI: Tkinter
  • Formato de datos: JSON
  • Control de versiones: Git