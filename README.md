# Proyecto-Practico-TLP

Autores:

María José Restrepo Osorio
Diego Moncada Gómez

Asignatura: Teoría de Lenguajes de Programación
Profesor: Fernan Alonso Villa Garzon

Sobre el Proyecto

Este proyecto implementa un analizador léxico y sintáctico para BRIK, lenguaje diseñado para definir las reglas y configuraciones de los siguientes juegos:

Tetris.brik — Una versión dimensional con piezas especiales y niveles progresivos.

Snake.brik — Una versión extendida con frutas especiales, portales y obstáculos.

Respecto analizador y sus componentes:

1. Tokenizer (Lexer)

Separa el código fuente en tokens (identificadores, números, cadenas, operadores y booleanos).

Usa expresiones regulares para reconocer patrones.

Ignora comentarios (#) y líneas vacías.

2. Parser (Análisis Sintáctico)

Construye una estructura jerárquica (AST) a partir de los tokens.

Reconoce bloques {}, listas [] y asignaciones = o :.

Valida la estructura básica del juego (juego, titulo, pantalla).

3. Generador de AST

El AST se guarda automáticamente como arbol.ast en formato JSON.

Básicamente, el analizador lee uno el juego.brik que quieras, realiza el proceso de tokenización (lexer), genera un árbol de sintaxis abstracta (AST) y lo guarda en un archivo arbol.ast en formato JSON.
