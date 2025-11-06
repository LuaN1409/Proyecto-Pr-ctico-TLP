# -*- coding: utf-8 -*-
"""
analizador de lenguaje .brik - compatible con Python 2.7
"""

import json
import re
import os
import io

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


class Parser(object):
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
                raise SyntaxError("se esperaba identificador, se encontró %s" % clave[1])
            
            # obtener '='
            igual = self.avanzar()
            if igual[1] != '=':
                raise SyntaxError("se esperaba '=', se encontró %s" % igual[1])
            
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
        
        raise SyntaxError("valor inesperado: %s" % valor)

    def parsear_bloque(self):
        self.avanzar()  # consume '{'
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
        print("error: archivo '%s' no encontrado" % ruta)
        return None
    
    with io.open(ruta, 'r', encoding='utf-8') as f:
        return f.read()


def guardar_ast(ast, ruta):
    """Guarda el AST en JSON manejando correctamente Unicode en Python 2.7"""
    # Serializa el AST a texto JSON con indentación y sin escapar caracteres Unicode
    data = json.dumps(ast, indent=2, ensure_ascii=False)
    
    # Si la salida es bytes (str en Python 2), la decodificamos a unicode
    if isinstance(data, str):
        data = data.decode('utf-8')
    
    with io.open(ruta, 'w', encoding='utf-8') as f:
        f.write(data)
    
    print("ast guardado en '%s'" % ruta)


def main():
    print("=== analizador de lenguaje .brik ===\n")
    
    try:
        archivo = raw_input("archivo a analizar (snake.brik / tetris.brik): ").strip()
    except NameError:
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
        print("análisis completado")
        print("juego: %s" % ast.get('juego'))
        print("campos: %d" % len(ast))
        
    except SyntaxError as e:
        print("error de sintaxis: %s" % e)
    except Exception as e:
        print("error: %s" % e)


if __name__ == "__main__":
    main()
