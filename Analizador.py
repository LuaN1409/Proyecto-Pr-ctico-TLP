import re
import json
import sys

# ---------------------------
# Lexer
# ---------------------------
TOKENS = [
    ("STRING", r'"[^"]*"'),
    ("NUMBER", r'\d+(\.\d+)?'),
    ("IDENT", r'[a-zA-Z_][a-zA-Z0-9_]*'),
    ("EQUALS", r'='),
    ("LBRACKET", r'\['),
    ("RBRACKET", r'\]'),
    ("LBRACE", r'\{'),
    ("RBRACE", r'\}'),
    ("COMMA", r','),
    ("COLON", r':'),
    ("TRUE", r'true'),
    ("FALSE", r'false'),
    ("NEWLINE", r'\n'),
    ("WHITESPACE", r'[ \t]+'),
    ("COMMENT", r'#.*')
]

token_regex = "|".join(f"(?P<{name}>{pattern})" for name, pattern in TOKENS)
token_re = re.compile(token_regex)

def lexer(text):
    tokens = []
    for match in token_re.finditer(text):
        kind = match.lastgroup
        value = match.group()
        if kind in ("WHITESPACE", "COMMENT"):
            continue
        if kind == "STRING":
            value = value.strip('"')
        if kind == "NUMBER":
            value = float(value) if "." in value else int(value)
        if kind == "TRUE":
            value = True
        if kind == "FALSE":
            value = False
        tokens.append((kind, value))
    return tokens

# ---------------------------
# Parser (muy sencillo)
# ---------------------------
def parse(tokens):
    ast = {}
    i = 0
    while i < len(tokens):
        if tokens[i][0] == "IDENT":
            key = tokens[i][1]
            if tokens[i+1][0] != "EQUALS":
                raise SyntaxError(f"Se esperaba '=' después de {key}")
            value, jump = parse_value(tokens, i+2)
            ast[key] = value
            i = jump
        else:
            i += 1
    return ast

def parse_value(tokens, i):
    """Devuelve (valor, nuevo_indice)"""
    t, v = tokens[i]

    if t in ("STRING", "NUMBER", "TRUE", "FALSE"):
        return v, i+1

    elif t == "LBRACKET":  # lista
        arr = []
        i += 1
        while tokens[i][0] != "RBRACKET":
            val, i = parse_value(tokens, i)
            arr.append(val)
            if tokens[i][0] == "COMMA":
                i += 1
        return arr, i+1

    elif t == "LBRACE":  # diccionario
        obj = {}
        i += 1
        while tokens[i][0] != "RBRACE":
            if tokens[i][0] != "STRING" and tokens[i][0] != "IDENT":
                raise SyntaxError("Clave inválida en objeto")
            key = tokens[i][1]
            if tokens[i+1][0] != "COLON":
                raise SyntaxError("Se esperaba ':' en objeto")
            val, i = parse_value(tokens, i+2)
            obj[key] = val
            if tokens[i][0] == "COMMA":
                i += 1
        return obj, i+1

    else:
        raise SyntaxError(f"Valor inesperado {t}")

# ---------------------------
# Main
# ---------------------------
def main():
    if len(sys.argv) < 2:
        print("Uso: python analizador.py archivo.brik")
        return

    filename = sys.argv[1]
    with open(filename, "r", encoding="utf-8") as f:
        text = f.read()

    tokens = lexer(text)
    ast = parse(tokens)

    with open("arbol.ast", "w", encoding="utf-8") as f:
        json.dump(ast, f, indent=2, ensure_ascii=False)

    print("✅ Análisis completado. AST guardado en arbol.ast")


# -------------------------------
# Zona de ejecución
# -------------------------------
if __name__ == "__main__":
    main()
