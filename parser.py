import ast as python_ast
from dataclasses import dataclass

from lexer import Token


# Nodos de expresiones
@dataclass
class Number:
    value: int | float


@dataclass
class StringLiteral:
    value: str


@dataclass
class BooleanLiteral:
    value: bool


@dataclass
class Name:
    value: str


@dataclass
class Attribute:
    object: object
    name: str


@dataclass
class Call:
    function: object
    arguments: list


@dataclass
class UnaryOp:
    operator: str
    operand: object


@dataclass
class BinaryOp:
    left: object
    operator: str
    right: object


# Nodos de instrucciones
@dataclass
class Assign:
    target: object
    expression: object


@dataclass
class ExpressionStatement:
    expression: object


@dataclass
class If:
    condition: object
    body: list
    else_body: list


@dataclass
class While:
    condition: object
    body: list


@dataclass
class For:
    variable: str
    iterable: object
    body: list


@dataclass
class FunctionDef:
    name: str
    parameters: list[str]
    body: list


@dataclass
class ClassDef:
    name: str
    body: list


@dataclass
class Return:
    expression: object | None


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.position = 0

    @property
    def current(self) -> Token:
        return self.tokens[self.position]

    def peek(self, distance: int = 1) -> Token:
        position = min(self.position + distance, len(self.tokens) - 1)
        return self.tokens[position]

    def advance(self) -> Token:
        token = self.current
        if token.kind != "EOF":
            self.position += 1
        return token

    def check(self, kind: str, value: str | None = None) -> bool:
        return (
            self.current.kind == kind
            and (value is None or self.current.value == value)
        )

    def expect(self, kind: str, value: str | None = None) -> Token:
        if not self.check(kind, value):
            token = self.current
            expected = value if value is not None else kind
            found = token.value or token.kind
            raise SyntaxError(
                f"Línea {token.line}: se esperaba {expected}, pero se encontró {found}"
            )
        return self.advance()

    def parse_program(self) -> list:
        statements = []
        while not self.check("EOF"):
            if self.check("NEWLINE"):
                self.advance()
                continue
            statement_line = self.current.line
            statements.append(self.parse_statement())
            self.consume_statement_end(statement_line)
        return statements

    def consume_statement_end(self, statement_line: int) -> None:
        if self.check("NEWLINE"):
            self.advance()
        elif (
            not self.check("DEDENT")
            and not self.check("EOF")
            and self.current.line <= statement_line
        ):
            token = self.current
            raise SyntaxError(f"Línea {token.line}: se esperaba un salto de línea")

    def parse_block(self) -> list:
        self.expect("NEWLINE")
        self.expect("INDENT")
        statements = []

        while not self.check("DEDENT") and not self.check("EOF"):
            if self.check("NEWLINE"):
                self.advance()
                continue
            statement_line = self.current.line
            statements.append(self.parse_statement())
            self.consume_statement_end(statement_line)

        self.expect("DEDENT")
        return statements

    def parse_statement(self):
        if self.check("IF"):
            return self.parse_if()
        if self.check("WHILE"):
            return self.parse_while()
        if self.check("FOR"):
            return self.parse_for()
        if self.check("DEF"):
            return self.parse_function()
        if self.check("CLASS"):
            return self.parse_class()
        if self.check("RETURN"):
            self.advance()
            expression = None if self.check("NEWLINE") else self.parse_expression()
            return Return(expression)

        expression = self.parse_expression()
        if self.check("OP", "="):
            self.advance()
            if not isinstance(expression, (Name, Attribute)):
                token = self.current
                raise SyntaxError(
                    f"Línea {token.line}: destino de asignación inválido"
                )
            return Assign(expression, self.parse_expression())

        return ExpressionStatement(expression)

    def parse_if(self):
        if_indentation = self.current.indentation
        self.expect("IF")
        condition = self.parse_expression()
        self.expect("COLON")
        body = self.parse_block()
        else_body = []

        if self.check("ELSE") and self.current.indentation == if_indentation:
            self.advance()
            self.expect("COLON")
            else_body = self.parse_block()

        return If(condition, body, else_body)

    def parse_while(self):
        self.expect("WHILE")
        condition = self.parse_expression()
        self.expect("COLON")
        return While(condition, self.parse_block())

    def parse_for(self):
        self.expect("FOR")
        variable = self.expect("NAME").value
        self.expect("IN")
        iterable = self.parse_expression()
        self.expect("COLON")
        return For(variable, iterable, self.parse_block())

    def parse_function(self):
        self.expect("DEF")
        name = self.expect("NAME").value
        self.expect("LPAREN")
        parameters = []
        if not self.check("RPAREN"):
            parameters.append(self.expect("NAME").value)
            while self.check("COMMA"):
                self.advance()
                parameters.append(self.expect("NAME").value)
        self.expect("RPAREN")
        self.expect("COLON")
        return FunctionDef(name, parameters, self.parse_block())

    def parse_class(self):
        self.expect("CLASS")
        name = self.expect("NAME").value
        self.expect("COLON")
        return ClassDef(name, self.parse_block())

    # Expresiones: or < and < not < comparaciones < suma < producto < potencia.
    def parse_expression(self):
        return self.parse_or()

    def parse_or(self):
        expression = self.parse_and()
        while self.check("NAME", "or"):
            self.advance()
            expression = BinaryOp(expression, "or", self.parse_and())
        return expression

    def parse_and(self):
        expression = self.parse_not()
        while self.check("NAME", "and"):
            self.advance()
            expression = BinaryOp(expression, "and", self.parse_not())
        return expression

    def parse_not(self):
        if self.check("NAME", "not"):
            self.advance()
            return UnaryOp("not", self.parse_not())
        return self.parse_comparison()

    def parse_comparison(self):
        expression = self.parse_addition()
        comparisons = ("==", "!=", "<", ">", "<=", ">=", "in")
        while (
            (self.check("OP") and self.current.value in comparisons)
            or self.check("IN")
        ):
            operator = self.advance().value
            expression = BinaryOp(expression, operator, self.parse_addition())
        return expression

    def parse_addition(self):
        expression = self.parse_product()
        while self.check("OP") and self.current.value in ("+", "-"):
            operator = self.advance().value
            expression = BinaryOp(expression, operator, self.parse_product())
        return expression

    def parse_product(self):
        expression = self.parse_unary()
        while self.check("OP") and self.current.value in ("*", "/", "//", "%"):
            operator = self.advance().value
            expression = BinaryOp(expression, operator, self.parse_unary())
        return expression

    def parse_unary(self):
        if self.check("OP") and self.current.value in ("+", "-"):
            operator = self.advance().value
            return UnaryOp(operator, self.parse_unary())
        return self.parse_power()

    def parse_power(self):
        expression = self.parse_postfix()
        if self.check("OP", "**"):
            self.advance()
            expression = BinaryOp(expression, "**", self.parse_unary())
        return expression

    def parse_postfix(self):
        expression = self.parse_atom()
        while True:
            if self.check("LPAREN"):
                self.advance()
                arguments = []
                if not self.check("RPAREN"):
                    arguments.append(self.parse_expression())
                    while self.check("COMMA"):
                        self.advance()
                        arguments.append(self.parse_expression())
                self.expect("RPAREN")
                expression = Call(expression, arguments)
            elif self.check("DOT"):
                self.advance()
                expression = Attribute(expression, self.expect("NAME").value)
            else:
                return expression

    def parse_atom(self):
        if self.check("NUMBER"):
            value = self.advance().value
            return Number(float(value) if "." in value else int(value))
        if self.check("STRING"):
            return StringLiteral(python_ast.literal_eval(self.advance().value))
        if self.check("NAME", "True"):
            self.advance()
            return BooleanLiteral(True)
        if self.check("NAME", "False"):
            self.advance()
            return BooleanLiteral(False)
        if self.check("NAME"):
            return Name(self.advance().value)
        if self.check("LPAREN"):
            self.advance()
            expression = self.parse_expression()
            self.expect("RPAREN")
            return expression

        token = self.current
        raise SyntaxError(
            f"Línea {token.line}: se esperaba un literal, nombre o paréntesis"
        )
