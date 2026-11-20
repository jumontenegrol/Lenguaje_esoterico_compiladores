from parser import (
    Assign,
    Attribute,
    BinaryOp,
    BooleanLiteral,
    Call,
    ClassDef,
    ExpressionStatement,
    For,
    FunctionDef,
    If,
    Name,
    Number,
    Return,
    StringLiteral,
    UnaryOp,
    While,
)


def generate_expression(expression) -> str:
    if isinstance(expression, Number):
        return str(expression.value)
    if isinstance(expression, StringLiteral):
        return repr(expression.value)
    if isinstance(expression, BooleanLiteral):
        return "verdadero" if expression.value else "falso"
    if isinstance(expression, Name):
        return expression.value
    if isinstance(expression, Attribute):
        return f"{generate_expression(expression.object)}.{expression.name}"
    if isinstance(expression, Call):
        if isinstance(expression.function, Name) and expression.function.value == "print":
            function = "gritar"
        elif isinstance(expression.function, Name) and expression.function.value == "range":
            function = "rango"
        else:
            function = generate_expression(expression.function)
        arguments = ", ".join(generate_expression(arg) for arg in expression.arguments)
        return f"{function}({arguments})"
    if isinstance(expression, UnaryOp):
        operator = "no" if expression.operator == "not" else expression.operator
        return f"{operator} {generate_expression(expression.operand)}"
    if isinstance(expression, BinaryOp):
        operator = {"and": "y", "or": "o", "in": "en"}.get(
            expression.operator, expression.operator
        )
        left = generate_expression(expression.left)
        right = generate_expression(expression.right)
        return f"{left} {operator} {right}"
    raise TypeError(f"Expresión no soportada: {type(expression).__name__}")


def generate_statement(statement, level: int = 0) -> list[str]:
    indentation = "    " * level

    if isinstance(statement, Assign):
        value = generate_expression(statement.expression)
        target = generate_expression(statement.target)
        return [f"{indentation}neymar {target} = {value}"]

    if isinstance(statement, ExpressionStatement):
        return [f"{indentation}{generate_expression(statement.expression)}"]

    if isinstance(statement, Return):
        value = "" if statement.expression is None else " " + generate_expression(statement.expression)
        return [f"{indentation}modric{value}"]

    if isinstance(statement, If):
        condition = generate_expression(statement.condition)
        lines = [f"{indentation}ronaldo {condition} messi"]
        for child in statement.body:
            lines.extend(generate_statement(child, level + 1))
        if statement.else_body:
            lines.append(f"{indentation}sino")
            for child in statement.else_body:
                lines.extend(generate_statement(child, level + 1))
        lines.append(f"{indentation}fin")
        return lines

    if isinstance(statement, While):
        condition = generate_expression(statement.condition)
        lines = [f"{indentation}maradona {condition} pele"]
        for child in statement.body:
            lines.extend(generate_statement(child, level + 1))
        lines.append(f"{indentation}fin")
        return lines

    if isinstance(statement, For):
        iterable = generate_expression(statement.iterable)
        lines = [f"{indentation}iniesta {statement.variable} en {iterable} xavi"]
        for child in statement.body:
            lines.extend(generate_statement(child, level + 1))
        lines.append(f"{indentation}fin")
        return lines

    if isinstance(statement, FunctionDef):
        parameters = ", ".join(statement.parameters)
        lines = [f"{indentation}James {statement.name}({parameters})"]
        for child in statement.body:
            lines.extend(generate_statement(child, level + 1))
        lines.append(f"{indentation}fin")
        return lines

    if isinstance(statement, ClassDef):
        lines = [f"{indentation}madrid {statement.name}"]
        for child in statement.body:
            lines.extend(generate_statement(child, level + 1))
        lines.append(f"{indentation}fin")
        return lines

    raise TypeError(f"Instrucción no soportada: {type(statement).__name__}")


def generate(program) -> str:
    lines = []
    for statement in program:
        lines.extend(generate_statement(statement))
    return "\n".join(lines)
