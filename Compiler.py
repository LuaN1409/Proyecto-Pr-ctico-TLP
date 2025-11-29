# -*- coding: utf-8 -*-
import json
import re
import os
import io
import sys

class Tokenizer(object):
    """Convierte código .brik en tokens"""
    
    def __init__(self, codigo):
        self.codigo = codigo
        self.tokens = []
        self.linea_actual = 0

    def tokenizar(self):
        """Genera lista de tokens del código"""
        lineas = self.codigo.splitlines()
        
        for num_linea, linea in enumerate(lineas, 1):
            self.linea_actual = num_linea
            linea = linea.strip()
            
            # Ignorar vacías y comentarios
            if not linea or linea.startswith('#'):
                continue

            # Patrón mejorado: captura strings, números, operadores, identificadores
            patron = r'"([^"]*)"|(\d+\.?\d*)|([{}\[\]=:,])|([a-zA-Z_]\w*)'
            matches = re.finditer(patron, linea)

            for match in matches:
                if match.group(1) is not None:  # String
                    self.tokens.append(('STRING', match.group(1), num_linea))
                
                elif match.group(2):  # Número
                    num = match.group(2)
                    if '.' in num:
                        self.tokens.append(('NUMBER', float(num), num_linea))
                    else:
                        self.tokens.append(('NUMBER', int(num), num_linea))
                
                elif match.group(3):  # Operador
                    self.tokens.append(('OPERATOR', match.group(3), num_linea))
                
                elif match.group(4):  # Identificador o booleano
                    valor = match.group(4)
                    if valor.lower() in ['true', 'false']:
                        self.tokens.append(('BOOLEAN', valor.lower() == 'true', num_linea))
                    else:
                        self.tokens.append(('IDENTIFIER', valor, num_linea))

        return self.tokens

class Parser(object):
    """Construye el AST a partir de tokens"""
    
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.ast = {}

    def error(self, mensaje):
        """Lanza error con información de línea"""
        if self.pos < len(self.tokens):
            token = self.tokens[self.pos]
            linea = token[2] if len(token) > 2 else "?"
            raise SyntaxError("Linea %s: %s (cerca de '%s')" % (linea, mensaje, token[1]))
        raise SyntaxError(mensaje)

    def parsear(self):
        """Genera el AST completo"""
        while self.pos < len(self.tokens):
            if self.peek() is None:
                break

            # Leer asignación: clave = valor
            token_clave = self.avanzar()
            if token_clave[0] != 'IDENTIFIER':
                self.error("Se esperaba identificador")

            clave = token_clave[1]

            token_igual = self.avanzar()
            if token_igual[1] != '=':
                self.error("Se esperaba '=' despues de '%s'" % clave)

            valor = self.parsear_valor()
            self.ast[clave] = valor

        self.validar_ast()
        return self.ast

    def validar_ast(self):
        """Valida campos obligatorios según tipo de juego"""
        if 'juego' not in self.ast:
            self.error("Falta campo obligatorio: 'juego'")
        
        tipo_juego = self.ast['juego'].lower()
        
        if tipo_juego not in ['snake', 'tetris']:
            self.error("Tipo de juego invalido: '%s' (debe ser 'snake' o 'tetris')" % 
                      self.ast['juego'])
        
        if 'pantalla' not in self.ast:
            self.error("Falta campo obligatorio: 'pantalla'")
        
        # Validaciones por tipo
        if tipo_juego == 'snake':
            if 'serpiente' not in self.ast:
                self.error("Juego Snake requiere campo 'serpiente'")
        
        elif tipo_juego == 'tetris':
            if 'piezas' not in self.ast:
                self.error("Juego Tetris requiere campo 'piezas'")

    def avanzar(self):
        """Consume y retorna el siguiente token"""
        if self.pos < len(self.tokens):
            token = self.tokens[self.pos]
            self.pos += 1
            return token
        return None

    def peek(self):
        """Observa el siguiente token sin consumir"""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def parsear_valor(self):
        """Parsea un valor (string, número, booleano, bloque o lista)"""
        token = self.peek()
        if token is None:
            self.error("Se esperaba un valor")

        tipo = token[0]
        valor = token[1]

        # Valores primitivos
        if tipo in ('STRING', 'NUMBER', 'BOOLEAN'):
            self.pos += 1
            return valor
        
        # Bloque { ... }
        elif tipo == 'OPERATOR' and valor == '{':
            return self.parsear_bloque()
        
        # Lista [ ... ]
        elif tipo == 'OPERATOR' and valor == '[':
            return self.parsear_lista()

        self.error("Valor inesperado: '%s'" % valor)

    def parsear_bloque(self):
        """Parsea un bloque: { clave = valor, ... }"""
        self.avanzar()  # Consume '{'
        bloque = {}

        while self.peek() and self.peek()[1] != '}':
            token_clave = self.avanzar()
            if token_clave[0] != 'IDENTIFIER':
                self.error("Se esperaba identificador en bloque")

            clave = token_clave[1]

            # Acepta = o :
            token_sep = self.avanzar()
            if token_sep[1] not in ['=', ':']:
                self.error("Se esperaba '=' o ':' despues de '%s'" % clave)

            valor = self.parsear_valor()
            bloque[clave] = valor

            # Coma opcional
            if self.peek() and self.peek()[1] == ',':
                self.avanzar()

        if not self.peek() or self.peek()[1] != '}':
            self.error("Se esperaba '}' para cerrar bloque")

        self.avanzar()  # Consume '}'
        return bloque

    def parsear_lista(self):
        """Parsea una lista: [ valor, valor, ... ]"""
        self.avanzar()  # Consume '['
        lista = []

        while self.peek() and self.peek()[1] != ']':
            item = self.parsear_valor()
            lista.append(item)

            # Coma opcional
            if self.peek() and self.peek()[1] == ',':
                self.avanzar()

        if not self.peek() or self.peek()[1] != ']':
            self.error("Se esperaba ']' para cerrar lista")

        self.avanzar()  # Consume ']'
        return lista

def cargar_archivo(ruta):
    """Carga archivo con encoding UTF-8"""
    if not os.path.exists(ruta):
        print("ERROR: Archivo '%s' no encontrado" % ruta)
        return None

    try:
        with io.open(ruta, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print("ERROR al leer archivo: %s" % str(e))
        return None

def guardar_ast(ast, ruta):
    """Guarda AST como JSON con encoding UTF-8"""
    try:
        # Serializar con formato legible
        data = json.dumps(ast, indent=2, ensure_ascii=False, sort_keys=False)
        
        # Escribir archivo
        with io.open(ruta, 'w', encoding='utf-8') as f:
            f.write(data if isinstance(data, unicode) else data.decode('utf-8'))
        
        print("[OK] JSON generado: %s" % ruta)
        print("     Tamanio: %d bytes" % os.path.getsize(ruta))
        return True
    
    except Exception as e:
        print("ERROR al guardar JSON: %s" % str(e))
        return False

def compilar(nombre_archivo):
    print("COMPILADOR")
    # Construir ruta
    ruta = os.path.join("games", nombre_archivo)
    
    print("\n[1/4] Cargando archivo: %s" % ruta)
    codigo = cargar_archivo(ruta)
    if not codigo:
        return False

    print("[2/4] Analisis lexico (Tokenizando)...")
    try:
        tokenizer = Tokenizer(codigo)
        tokens = tokenizer.tokenizar()
        print("     -> %d tokens generados" % len(tokens))
    except Exception as e:
        print("ERROR en tokenizacion: %s" % str(e))
        return False

    print("[3/4] Analisis sintactico (Parseando)...")
    try:
        parser = Parser(tokens)
        ast = parser.parsear()
        print("     -> AST construido (%d campos principales)" % len(ast))
    except SyntaxError as e:
        print("ERROR de sintaxis: %s" % str(e))
        return False
    except Exception as e:
        print("ERROR en parseo: %s" % str(e))
        return False

    print("[4/4] Generando JSON...")
    salida = os.path.join("games", nombre_archivo.replace(".brik", ".json"))
    
    if guardar_ast(ast, salida):
        print("COMPILACION EXITOSA")
        return True
    
    return False

def main():
    """Función principal"""
    print("\n")
    print("  ___  ___  ___ _  __")
    print(" | _ )| _ \|_ _| |/ /")
    print(" | _ \|   / | || ' < ")
    print(" |___/|_|_\|___|_|\_\\")
    print("\n COMPILADOR\n")
    
    # Leer nombre de archivo
    if len(sys.argv) > 1:
        archivo = sys.argv[1]
    else:
        print("Juegos disponibles:")
        print("  - snake.brik")
        print("  - tetris.brik\n")
        archivo = raw_input("Archivo a compilar: ").strip()

    if not archivo:
        print("\nERROR: Debes ingresar un nombre de archivo")
        return

    # Agregar extensión si falta
    if not archivo.endswith(".brik"):
        archivo += ".brik"
        print("(Extension .brik agregada automaticamente)")

    # Compilar
    exito = compilar(archivo)
    
    if not exito:
        print("\n[X] Compilacion fallida. Revisa los errores.")
        sys.exit(1)
    else:
        print("\n[✓] Listo para jugar")
        print("    Ejecuta: python runtime.py")
        print("    O usa:   jugar.bat\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[!] Cancelado por el usuario")
        sys.exit(0)
    except Exception as e:
        print("\n[!] Error inesperado: %s" % str(e))
        sys.exit(1)