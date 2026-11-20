from dataclasses import dataclass
import re


@dataclass
class Token:
    kind: str
    value: str
    line: int
    indentation: int = 0


TOKEN_PATTERN = re.compile(
    r'''(?P<STRING>"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*')'''
    r"|(?P<NUMBER>\d+(?:\.\d+)?)"
    r"|(?P<NAME>[A-Za-z_][A-Za-z0-9_]*)"
    r"|(?P<OP>\*\*|//|==|!=|<=|>=|[+\-*/%<>=])"
    r"|(?P<LPAREN>\()"
    r"|(?P<RPAREN>\))"
    r"|(?P<COMMA>,)"
    r"|(?P<COLON>:)"
    r"|(?P<DOT>\.)"
    r"|(?P<COMMENT>\#.*)"
    r"|(?P<SKIP>[ \t]+)"
    r"|(?P<MISMATCH>.)"
)

KEYWORDS = {
    "if": "IF",
    "else": "ELSE",
    "while": "WHILE",
    "for": "FOR",
    "in": "IN",
    "def": "DEF",
    "class": "CLASS",
    "return": "RETURN",
}


def tokenize(source: str) -> list[Token]:
    tokens = []
    indentation_stack = [0]
    source_lines = source.splitlines()

    for line_number, line in enumerate(source_lines, start=1):
        leading_whitespace = line[:len(line) - len(line.lstrip(" \t"))]
        content = line[len(leading_whitespace):]

        # Empty lines and comment-only lines do not change block indentation.
        if not content or content.startswith("#"):
            continue

        if "\t" in leading_whitespace:
            raise SyntaxError(f"Línea {line_number}: usa espacios para indentar")

        indentation = len(leading_whitespace)

        if indentation > indentation_stack[-1]:
            indentation_stack.append(indentation)
            tokens.append(Token("INDENT", "", line_number, indentation))
        elif indentation < indentation_stack[-1]:
            while indentation < indentation_stack[-1]:
                indentation_stack.pop()
                tokens.append(Token("DEDENT", "", line_number, indentation))

            if indentation != indentation_stack[-1]:
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

            if kind == "COMMENT":
                break

            if kind != "SKIP":
                if kind == "NAME" and value in KEYWORDS:
                    kind = KEYWORDS[value]
                tokens.append(Token(kind, value, line_number, indentation))

            position = match.end()

        tokens.append(Token("NEWLINE", "", line_number, indentation))

    end_line = len(source_lines) or 1
    while len(indentation_stack) > 1:
        indentation_stack.pop()
        tokens.append(Token("DEDENT", "", end_line))

    tokens.append(Token("EOF", "", end_line))
    return tokens
