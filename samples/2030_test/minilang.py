class Scanner:
    def __init__(self, source) -> None:
        self._source = source
        self._current_position = 0

    def next_token(self):
        while self._current_char().isspace(): self._current_position += 1

        start = self._current_position
        match self._current_char():
            case "$EOF": return "$EOF"
            case c if c.isalpha():
                while self._current_char().isalnum() or self._current_char() == "_":
                    self._current_position += 1
                return self._source[start:self._current_position]
            case c if c.isnumeric():
                while self._current_char().isnumeric():
                    self._current_position += 1
                return int(self._source[start:self._current_position])
            case _:
                self._current_position += 1
                return self._source[start:self._current_position]

    def _current_char(self):
        if self._current_position < len(self._source):
            return self._source[self._current_position]
        else:
            return "$EOF"

class Parser:
    def __init__(self, source):
        self.scanner = Scanner(source)
        self._current_token = ""
        self._next_token()

    def parse_program(self):
        program: list = ["program"]
        while self._current_token != "$EOF":
            self._check_token("print")
            number = self._next_token()
            assert isinstance(number, int), f"Expected number , found `{number}`."
            self._next_token()
            self._consume_token(";")
            program.append(["print", number])
        return program

    def _consume_token(self, expected_token):
        self._check_token(expected_token)
        return self._next_token()

    def _check_token(self, expected_token):
        assert self._current_token == expected_token, \
               f"Expected `{expected_token}`, found `{self._current_token}`."

    def _next_token(self):
        self._current_token = self.scanner.next_token()
        return self._current_token

class Evaluator:
    def __init__(self):
        self._output = []

    def clear_output(self): self._output = []
    def output(self): return self._output

    def eval_program(self, program):
        match program:
            case ["program", *statements]:
                for statement in statements:
                    self._eval_statement(statement)
            case unexpected: assert False, f"Internal Error at `{unexpected}`."

    def _eval_statement(self, statement):
        match statement:
            case ["print", val]: self._output.append(val)
            case unexpected: assert False, f"Internal Error at `{unexpected}`."

if __name__ == "__main__":
    import sys

    evaluator = Evaluator()
    while True:
        print("Input source and enter Ctrl+D:")
        if (source := sys.stdin.read()) == "": break

        print("Output:")
        try:
            ast = Parser(source).parse_program()
            print(ast)
            evaluator.eval_program(ast)
            print(*evaluator.output(), sep="\n")
        except AssertionError as e:
            print("Error:", e)
