# -*- coding: utf-8 -*-
"""
Analizador de Lenguaje .brik
"""

import json
import re
import os

# -------------------------------
# Tokenizador (Lexer)
# -------------------------------
class Tokenizer:
    def __init__(self, source_code):
        self.source = source_code
        self.tokens = []

    def tokenize(self):
        lines = self.source.splitlines()
        for line_num, line in enumerate(lines, start=1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            # Captura strings, números, operadores, identificadores
            regex_tokens = re.findall(r'"([^"]*)"|(\d+\.?\d*)|({|}|\[|\]|=|,)|(\w+)', line)

            for group in regex_tokens:
                if group[0]:  # Cadena de texto
                    self.tokens.append(('STRING', group[0]))
                elif group[1]:  # Número
                    if '.' in group[1]:
                        self.tokens.append(('NUMBER', float(group[1])))
                    else:
                        self.tokens.append(('NUMBER', int(group[1])))
                elif group[2]:  # Operador o delimitador
                    self.tokens.append(('OPERATOR', group[2]))
                elif group[3]:  # Identificador
                    value = group[3]
                    if value.lower() in ['true', 'false']:
                        self.tokens.append(('BOOLEAN', value.lower() == 'true'))
                    else:
                        self.tokens.append(('IDENTIFIER', value))
        return self.tokens


# -------------------------------
# Parser (Análisis Sintáctico)
# -------------------------------
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token_index = 0
        self.symbol_table = {}

    def parse(self):
        while self.current_token_index < len(self.tokens):
            if self.peek_token() is None:
                break

            key_token = self.get_token()
            if key_token[0] != 'IDENTIFIER':
                raise SyntaxError(f"Error de sintaxis: Se esperaba un identificador, se encontró {key_token[1]}")

            eq_token = self.get_token()
            if eq_token[1] != '=':
                raise SyntaxError(f"Error de sintaxis: Se esperaba '=', se encontró {eq_token[1]}")

            value = self.parse_value()
            self.symbol_table[key_token[1]] = value

        return self.symbol_table

    def get_token(self):
        if self.current_token_index < len(self.tokens):
            token = self.tokens[self.current_token_index]
            self.current_token_index += 1
            return token
        return None

    def peek_token(self):
        if self.current_token_index < len(self.tokens):
            return self.tokens[self.current_token_index]
        return None

    def parse_value(self):
        token = self.peek_token()
        if token is None:
            raise SyntaxError("Error de sintaxis: Se esperaba un valor después de '='")

        token_type, token_value = token

        if token_type in ('STRING', 'NUMBER', 'BOOLEAN'):
            self.current_token_index += 1
            return token_value
        elif token_type == 'OPERATOR' and token_value == '{':
            return self.parse_block()
        elif token_type == 'OPERATOR' and token_value == '[':
            return self.parse_list()

        raise SyntaxError(f"Error de sintaxis: Valor inesperado '{token_value}'")

    def parse_block(self):
        self.get_token()  # Consume '{'
        block_content = {}

        while self.peek_token() and self.peek_token()[1] != '}':
            key_token = self.get_token()
            if key_token[0] != 'IDENTIFIER':
                raise SyntaxError(f"Error en bloque: Se esperaba un identificador, se encontró {key_token[1]}")

            eq_token = self.get_token()
            if eq_token[1] != '=':
                raise SyntaxError(f"Error en bloque: Se esperaba '=', se encontró {eq_token[1]}")

            value = self.parse_value()
            block_content[key_token[1]] = value

            # Permitir coma opcional entre elementos del bloque
            if self.peek_token() and self.peek_token()[1] == ',':
                self.get_token()

        if not self.peek_token() or self.peek_token()[1] != '}':
            raise SyntaxError("Error de sintaxis: Se esperaba '}' para cerrar un bloque")

        self.get_token()  # Consume '}'
        return block_content

    def parse_list(self):
        self.get_token()  # Consume '['
        list_content = []

        while self.peek_token() and self.peek_token()[1] != ']':
            item = self.parse_value()
            list_content.append(item)

            if self.peek_token() and self.peek_token()[1] == ',':
                self.get_token()  # Consume ','

        if not self.peek_token() or self.peek_token()[1] != ']':
            raise SyntaxError("Error de sintaxis: Se esperaba ']' para cerrar una lista")

        self.get_token()  # Consume ']'
        return list_content


# -------------------------------
# Funciones auxiliares
# -------------------------------
def load_file_content(filepath):
    if not os.path.exists(filepath):
        print(f"❌ Error: El archivo '{filepath}' no se encontró.")
        return None
    with open(filepath, 'r', encoding='utf-8') as file:
        return file.read()

def save_ast_to_file(ast, filepath):
    try:
        with open(filepath, 'w', encoding='utf-8') as file:
            json.dump(ast, file, indent=4, ensure_ascii=False)
        print(f"✅ AST guardado exitosamente en '{filepath}'")
    except Exception as e:
        print(f"Error al guardar el archivo: {e}")


# -------------------------------
# Zona de ejecución
# -------------------------------
if __name__ == "__main__":
    print("=== Analizador de Lenguaje .brik ===\n")
    file_path = input("Ingrese el nombre del archivo a analizar (Snake.brik / Tetris.brik): ").strip()

    if not file_path:
        file_path = "Tetris.brik"  # valor por defecto

    ast_file_path = "arbol.ast"

    source_code = load_file_content(file_path)

    if source_code:
        print("\n--- Análisis Léxico (Lexer) ---")
        tokenizer = Tokenizer(source_code)
        tokens = tokenizer.tokenize()
        print(f"Total de tokens reconocidos: {len(tokens)}")

        print("\n--- Análisis Sintáctico (Parser) ---")
        parser = Parser(tokens)
        try:
            ast = parser.parse()
            print("✅ Sintaxis correcta. Se ha construido el Árbol de Sintaxis Abstracta (AST).")
            save_ast_to_file(ast, ast_file_path)
        except (SyntaxError, NameError) as e:
            print(f"❌ Error en la sintaxis: {e}")
