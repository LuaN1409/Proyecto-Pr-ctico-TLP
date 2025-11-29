# -*- coding: utf-8 -*-
"""
compiler.py – Compilador del lenguaje .brik
Entrega 3 – Proyecto TLP

Este archivo toma un programa .brik ubicado en /games/, lo tokeniza,
lo parsea y genera su representación en formato JSON (AST) dentro de /games/.
"""

import json
import re
import os
import io

# =========================================
#               TOKENIZER
# =========================================

class Tokenizer(object):
    def __init__(self, codigo):
        self.codigo = codigo
        self.tokens = []

    def tokenizar(self):
        lineas = self.codigo.splitlines()
        for linea in lineas:
            linea = linea.strip()
            if not linea or linea.startswith('#'):
                continue

            patron = r'"([^"]*)"|(\d+\.?\d*)|({|}|\[|\]|=|:|,)|(\w+)'
            matches = re.findall(patron, linea)

            for match in matches:
                if match[0]:
                    self.tokens.append(('STRING', match[0]))
                elif match[1]:
                    if '.' in match[1]:
                        self.tokens.append(('NUMBER', float(match[1])))
                    else:
                        self.tokens.append(('NUMBER', int(match[1])))
                elif match[2]:
                    self.tokens.append(('OPERATOR', match[2]))
                elif match[3]:
                    valor = match[3]
                    if valor.lower() in ['true', 'false']:
                        self.tokens.append(('BOOLEAN', valor.lower() == 'true'))
                    else:
                        self.tokens.append(('IDENTIFIER', valor))

        return self.tokens


# =========================================
#                 PARSER
# =========================================

class Parser(object):
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.ast = {}

    def parsear(self):
        while self.pos < len(self.tokens):
            if self.peek() is None:
                break

            clave = self.avanzar()
            if clave[0] != 'IDENTIFIER':
                raise SyntaxError("se esperaba identificador, se encontró %s" % clave[1])

            igual = self.avanzar()
            if igual[1] != '=':
                raise SyntaxError("se esperaba '=', se encontró %s" % igual[1])

            valor = self.parsear_valor()
            self.ast[clave[1]] = valor

        self.validar()
        return self.ast

    def validar(self):
        if 'juego' not in self.ast:
            raise SyntaxError("falta campo obligatorio: 'juego'")
        if 'titulo' not in self.ast:
            raise SyntaxError("falta campo obligatorio: 'titulo'")
        if 'pantalla' not in self.ast:
            raise SyntaxError("falta campo obligatorio: 'pantalla'")

    def avanzar(self):
        if self.pos < len(self.tokens):
            token = self.tokens[self.pos]
            self.pos += 1
            return token
        return None

    def peek(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def parsear_valor(self):
        token = self.peek()
        if token is None:
            raise SyntaxError("se esperaba un valor")

        tipo, valor = token

        if tipo in ('STRING', 'NUMBER', 'BOOLEAN'):
            self.pos += 1
            return valor
        elif tipo == 'OPERATOR' and valor == '{':
            return self.parsear_bloque()
        elif tipo == 'OPERATOR' and valor == '[':
            return self.parsear_lista()

        raise SyntaxError("valor inesperado: %s" % valor)

    def parsear_bloque(self):
        self.avanzar()
        bloque = {}

        while self.peek() and self.peek()[1] != '}':
            clave = self.avanzar()
            if clave[0] != 'IDENTIFIER':
                raise SyntaxError("se esperaba identificador en bloque")

            separador = self.avanzar()
            if separador[1] not in ['=', ':']:
                raise SyntaxError("se esperaba '=' o ':'")

            valor = self.parsear_valor()
            bloque[clave[1]] = valor

            if self.peek() and self.peek()[1] == ',':
                self.avanzar()

        if not self.peek() or self.peek()[1] != '}':
            raise SyntaxError("se esperaba '}' para cerrar bloque")

        self.avanzar()
        return bloque

    def parsear_lista(self):
        self.avanzar()
        lista = []

        while self.peek() and self.peek()[1] != ']':
            item = self.parsear_valor()
            lista.append(item)

            if self.peek() and self.peek()[1] == ',':
                self.avanzar()

        if not self.peek() or self.peek()[1] != ']':
            raise SyntaxError("se esperaba ']' para cerrar lista")

        self.avanzar()
        return lista


# =========================================
#        FUNCIONES DE ARCHIVOS
# =========================================

def cargar_archivo(ruta):
    if not os.path.exists(ruta):
        print("ERROR: archivo '%s' no encontrado" % ruta)
        return None

    with io.open(ruta, 'r', encoding='utf-8') as f:
        return f.read()


def guardar_ast(ast, ruta):
    data = json.dumps(ast, indent=2, ensure_ascii=False)

    if isinstance(data, str):
        data = data.decode('utf-8')

    with io.open(ruta, 'w', encoding='utf-8') as f:
        f.write(data)

    print("✔ AST generado en '%s'" % ruta)


# =========================================
#             FUNCIÓN COMPILAR
# =========================================

def compilar(nombre_archivo):
    # Siempre compilar desde la carpeta /games/
    ruta = os.path.join("games", nombre_archivo)

    print("Compilando:", ruta)

    codigo = cargar_archivo(ruta)
    if not codigo:
        return

    tokenizer = Tokenizer(codigo)
    tokens = tokenizer.tokenizar()

    parser = Parser(tokens)
    ast = parser.parsear()

    salida = os.path.join("games", nombre_archivo.replace(".brik", ".json"))
    guardar_ast(ast, salida)


# =========================================
#                  MAIN
# =========================================

if __name__ == "__main__":
    print("=== Compilador BRIK ===")
    archivo = raw_input("Nombre del archivo (snake.brik / tetris.brik): ").strip()

    if not archivo.endswith(".brik"):
        print("Debes ingresar un archivo con extensión .brik")
    else:
        compilar(archivo)
