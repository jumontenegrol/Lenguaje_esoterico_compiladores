from pathlib import Path
import sys

from codegen import generate
from lexer import tokenize
from parser import Parser


def main() -> int:
    if len(sys.argv) != 2:
        print("Uso: python main.py archivo.py")
        return 2

    input_path = Path(sys.argv[1])

    try:
        source = input_path.read_text(encoding="utf-8")
        tokens = tokenize(source)
        program = Parser(tokens).parse_program()
        output = generate(program)
    except (OSError, SyntaxError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
