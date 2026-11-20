from pathlib import Path
import sys

from lexer import tokenize
from parser import Parser
from codegen import generate


def main():
    if len(sys.argv) != 2:
        print("Uso: python main.py archivo.py")
        return 2

    input_path = Path(sys.argv[1])
    source = input_path.read_text(encoding="utf-8")

    try:
        tokens = tokenize(source)
        program = Parser(tokens).parse_program()
        output = generate(program)
    except SyntaxError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())