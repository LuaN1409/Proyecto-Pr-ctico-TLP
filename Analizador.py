# -*- coding: utf-8 -*-
"""
analizador de lenguaje .brik
"""

import json
import re
import os

class Tokenizer:
    def __init__(self, codigo):
        self.codigo = codigo
        self.tokens = []

    def tokenizar(self):
        lineas = self.codigo.splitlines()
        for linea in lineas:
            linea = linea.strip()
            if not linea or linea.startswith('#'):
                continue
            
            # buscar strings, números, operadores e identificadores
            patron = r'"([^"]*)"|(\d+\.?\d*)|({|}|\[|\]|=|:|,)|(\w+)'
            matches = re.findall(patron, linea)
            
            for match in matches:
                if match[0]:  # string
                    self.tokens.append(('STRING', match[0]))
                elif match[1]:  # número
                    if '.' in match[1]:
                        self.tokens.append(('NUMBER', float(match[1])))
                    else:
                        self.tokens.append(('NUMBER', int(match[1])))
                elif match[2]:  # operador
                    self.tokens.append(('OPERATOR', match[2]))
                elif match[3]:  # identificador o booleano
                    valor = match[3]
                    if valor.lower() in ['true', 'false']:
                        self.tokens.append(('BOOLEAN', valor.lower() == 'true'))
                    else:
                        self.tokens.append(('IDENTIFIER', valor))
        
        return self.tokens

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.ast = {}

    def parsear(self):
        while self.pos < len(self.tokens):
            if self.peek() is None:
                break
            
            # obtener clave
            clave = self.avanzar()
            if clave[0] != 'IDENTIFIER':
                raise SyntaxError(f"se esperaba identificador, se encontró {clave[1]}")
            
            # obtener '='
            igual = self.avanzar()
            if igual[1] != '=':
                raise SyntaxError(f"se esperaba '=', se encontró {igual[1]}")
            
            # obtener valor
            valor = self.parsear_valor()
            self.ast[clave[1]] = valor
        
        # validación básica
        self.validar()
        return self.ast

    def validar(self):
        """validación mínima del ast"""
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
        
        raise SyntaxError(f"valor inesperado: {valor}")

    def parsear_bloque(self):
        self.avanzar()  # consume '{'
        bloque = {}
        
        while self.peek() and self.peek()[1] != '}':
            clave = self.avanzar()
            if clave[0] != 'IDENTIFIER':
                raise SyntaxError(f"se esperaba identificador en bloque")
            
            separador = self.avanzar()
            if separador[1] not in ['=', ':']:
                raise SyntaxError(f"se esperaba '=' o ':'")
            
            valor = self.parsear_valor()
            bloque[clave[1]] = valor
            
            if self.peek() and self.peek()[1] == ',':
                self.avanzar()
        
        if not self.peek() or self.peek()[1] != '}':
            raise SyntaxError("se esperaba '}' para cerrar bloque")
        
        self.avanzar()  # consume '}'
        return bloque

    def parsear_lista(self):
        self.avanzar()  # consume '['
        lista = []
        
        while self.peek() and self.peek()[1] != ']':
            item = self.parsear_valor()
            lista.append(item)
            
            if self.peek() and self.peek()[1] == ',':
                self.avanzar()
        
        if not self.peek() or self.peek()[1] != ']':
            raise SyntaxError("se esperaba ']' para cerrar lista")
        
        self.avanzar()  # consume ']'
        return lista

def cargar_archivo(ruta):
    if not os.path.exists(ruta):
        print(f"error: archivo '{ruta}' no encontrado")
        return None
    
    with open(ruta, 'r', encoding='utf-8') as f:
        return f.read()

def guardar_ast(ast, ruta):
    with open(ruta, 'w', encoding='utf-8') as f:
        json.dump(ast, f, indent=2, ensure_ascii=False)
    print(f"ast guardado en '{ruta}'")

def main():
    print("=== analizador de lenguaje .brik ===\n")
    
    archivo = input("archivo a analizar (snake.brik / tetris.brik): ").strip()
    if not archivo:
        archivo = "tetris.brik"
    
    codigo = cargar_archivo(archivo)
    if not codigo:
        return
    
    try:
        print("analizando...")
        tokenizer = Tokenizer(codigo)
        tokens = tokenizer.tokenizar()
        
        parser = Parser(tokens)
        ast = parser.parsear()
        
        guardar_ast(ast, "arbol.ast")
        print(f"análisis completado")
        print(f"juego: {ast.get('juego')}")
        print(f"campos: {len(ast)}")
        
    except SyntaxError as e:
        print(f"error de sintaxis: {e}")
    except Exception as e:
        print(f"error: {e}")

if __name__ == "__main__":
    main()