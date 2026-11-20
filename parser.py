from dataclasses import dataclass
from lexer import Token

@dataclass
class Number:
    value: int


@dataclass
class Name:
    value: str

@dataclass
class StringLiteral:
    value: str

@dataclass
class BinaryOp:
    left: object
    operator: str
    right: object


@dataclass
class Assign:
    name: str
    expression: object


@dataclass
class Print:
    expression: object


@dataclass
class If:
    condition: object
    body: list
    else_body: list


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.position = 0

    @property
    def current(self) -> Token:
        return self.tokens[self.position]

    def advance(self) -> Token:
        token = self.current

        if token.kind != "EOF":
            self.position += 1

        return token

    def check(self, kind: str, value: str | None = None) -> bool:
        token = self.current

        if token.kind != kind:
            return False

        if value is not None and token.value != value:
            return False

        return True

    def expect(self, kind: str, value: str | None = None) -> Token:
        if not self.check(kind, value):
            token = self.current
            expected = value if value is not None else kind
            raise SyntaxError(
                f"Línea {token.line}: se esperaba {expected}, "
                f"pero se encontró {token.value or token.kind}"
            )

        return self.advance()

    def parse_expression(self):
       
        return self.parse_comparison()

    def parse_comparison(self):
        expression = self.parse_addition()

        while self.check("OP") and self.current.value in (
            ">", "<", "==", "!=", ">=", "<="
        ):
            operator = self.advance().value
            right = self.parse_addition()
            expression = BinaryOp(expression, operator, right)

        return expression

    def parse_addition(self):
        expression = self.parse_multiplication()

        while self.check("OP") and self.current.value in ("+", "-"):
            operator = self.advance().value
            right = self.parse_multiplication()
            expression = BinaryOp(expression, operator, right)

        return expression

    def parse_multiplication(self):
        expression = self.parse_atom()

        while self.check("OP") and self.current.value in ("*", "/"):
            operator = self.advance().value
            right = self.parse_atom()
            expression = BinaryOp(expression, operator, right)

        return expression

    def parse_atom(self):
        if self.check("STRING"):
            return StringLiteral(self.advance().value)
        
        if self.check("NUMBER"):
            return Number(int(self.advance().value))

        if self.check("NAME"):
            return Name(self.advance().value)

        if self.check("LPAREN"):
            self.advance()
            expression = self.parse_expression()
            self.expect("RPAREN")
            return expression

        token = self.current
        raise SyntaxError(
            f"Línea {token.line}: se esperaba un número, nombre o paréntesis"
        )

    def parse_statement(self):
        if self.check("IF"):
            return self.parse_if()

        if self.check("PRINT"):
            self.advance()
            self.expect("LPAREN")
            expression = self.parse_expression()
            self.expect("RPAREN")
            return Print(expression)

        if self.check("NAME"):
            name = self.advance().value
            self.expect("OP", "=")
            expression = self.parse_expression()
            return Assign(name, expression)

        token = self.current
        raise SyntaxError(
            f"Línea {token.line}: instrucción no reconocida"
        )

    def parse_program(self):
        statements = []

        while not self.check("EOF"):
            # Ignora líneas vacías.
            if self.check("NEWLINE"):
                self.advance()
                continue

            statements.append(self.parse_statement())

            if self.check("NEWLINE"):
                self.advance()
            elif not self.check("DEDENT") and not self.check("EOF"):
                token = self.current
                raise SyntaxError(
                    f"Línea {token.line}: se esperaba un salto de línea"
                )

        return statements

    def parse_block(self):
        self.expect("NEWLINE")
        self.expect("INDENT")

        statements = []

        while not self.check("DEDENT") and not self.check("EOF"):
            if self.check("NEWLINE"):
                self.advance()
                continue

            statements.append(self.parse_statement())

            if self.check("NEWLINE"):
                self.advance()
            elif not self.check("DEDENT") and not self.check("EOF"):
                token = self.current
                raise SyntaxError(
                    f"Línea {token.line}: se esperaba un salto de línea"
                )

        self.expect("DEDENT")
        return statements

    def parse_if(self):
        self.expect("IF")
        condition = self.parse_expression()
        self.expect("COLON")
        body = self.parse_block()

        else_body = []

        if self.check("ELSE"):
            self.advance()
            self.expect("COLON")
            else_body = self.parse_block()

        return If(condition, body, else_body)