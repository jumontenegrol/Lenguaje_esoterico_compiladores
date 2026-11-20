from parser import Assign, BinaryOp, If, Name, Number, Print, StringLiteral

def generate_expression(expression):
    if isinstance(expression, StringLiteral):
        return expression.value

    if isinstance(expression, Number):
        return str(expression.value)

    if isinstance(expression, Name):
        return expression.value

    if isinstance(expression, BinaryOp):
        left = generate_expression(expression.left)
        right = generate_expression(expression.right)
        return f"{left} {expression.operator} {right}"

    raise TypeError(f"Expresión no soportada: {type(expression).__name__}")


def generate_statement(statement, level=0):
    indentation = "    " * level

    if isinstance(statement, Assign):
        expression = generate_expression(statement.expression)
        return [f"{indentation}neymar {statement.name} = {expression}"]

    if isinstance(statement, Print):
        expression = generate_expression(statement.expression)
        return [f"{indentation}gritar({expression})"]

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

    raise TypeError(f"Instrucción no soportada: {type(statement).__name__}")

def generate(program):
    lines = []

    for statement in program:
        lines.extend(generate_statement(statement))

    return "\n".join(lines)