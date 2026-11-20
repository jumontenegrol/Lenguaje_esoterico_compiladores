from dataclasses import dataclass
import re


@dataclass
class Token:
    kind: str
    value: str
    line: int


TOKEN_PATTERN = re.compile(
    r'''(?P<STRING>"[^"\n]*"|'[^'\n]*')'''
    r"|(?P<NUMBER>\d+)"
    r"|(?P<NAME>[A-Za-z_][A-Za-z0-9_]*)"
    r"|(?P<OP>==|!=|<=|>=|[+\-*/<>=])"
    r"|(?P<LPAREN>\()"
    r"|(?P<RPAREN>\))"
    r"|(?P<COLON>:)"
    r"|(?P<SKIP>[ \t]+)"
    r"|(?P<MISMATCH>.)"
)

KEYWORDS = {
    "if": "IF",
    "else": "ELSE",
    "print": "PRINT",
}

def tokenize(source: str) -> list[Token]:
    tokens = []
    indents = [0]

    for line_number, line in enumerate(source.splitlines(), start=1):
        # Ignora las líneas vacías.
        if not line.strip():
            continue

        # Cuenta los espacios al inicio de la línea.
        leading_whitespace = line[:len(line) - len(line.lstrip(" \t"))]

        if "\t" in leading_whitespace:
            raise SyntaxError(f"Línea {line_number}: usa espacios para indentar")

        indentation = len(leading_whitespace)

        content = line[indentation:]

        # Una indentación mayor abre un bloque.
        if indentation > indents[-1]:
            indents.append(indentation)
            tokens.append(Token("INDENT", "", line_number))

        # Una indentación menor cierra uno o más bloques.
        elif indentation < indents[-1]:
            while indentation < indents[-1]:
                indents.pop()
                tokens.append(Token("DEDENT", "", line_number))

            # La nueva indentación debe coincidir con un nivel anterior.
            if indentation != indents[-1]:
                raise SyntaxError(
                    f"Línea {line_number}: nivel de indentación inconsistente"
                )

        position = 0

        while position < len(content):
            match = TOKEN_PATTERN.match(content, position)
            kind = match.lastgroup
            value = match.group()

            if kind == "MISMATCH":
                raise SyntaxError(
                    f"Línea {line_number}: carácter inesperado {value!r}"
                )

            if kind != "SKIP":
                if kind == "NAME" and value in KEYWORDS:
                    kind = KEYWORDS[value]

                tokens.append(Token(kind, value, line_number))

            position = match.end()

        tokens.append(Token("NEWLINE", "", line_number))

    # Cierra cualquier bloque que haya quedado abierto.
    while len(indents) > 1:
        indents.pop()
        tokens.append(Token("DEDENT", "", len(source.splitlines())))

    tokens.append(Token("EOF", "", len(source.splitlines())))
    return tokens