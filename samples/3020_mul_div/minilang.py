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
            program.append(self._parse_statement())
        return program

    def _parse_statement(self):
        match self._current_token:
            case "print": return self._parse_print()
            case unexpected: assert False, f"Unexpected token `{unexpected}`."

    def _parse_print(self):
        self._next_token()
        expr = self._parse_expression()
        self._consume_token(";")
        return ["print", expr]

    def _parse_expression(self):
        return self._parse_add_sub()

    def _parse_add_sub(self):
        add_sub = self._parse_mul_div()
        while (op := self._current_token) in ("+", "-"):
            self._next_token()
            add_sub = [op, add_sub, self._parse_mul_div()]
        return add_sub

    def _parse_mul_div(self):
        mul_div = self._parse_primary()
        while (op := self._current_token) in ("*", "/"):
            self._next_token()
            mul_div = [op, mul_div, self._parse_primary()]
        return mul_div

    def _parse_primary(self):
        match self._current_token:
            case int(value):
                self._next_token()
                return value
            case unexpected: assert False, f"Unexpected token `{unexpected}`."

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
        self.output = []

    def eval_program(self, program):
        self.output = []
        match program:
            case ["program", *statements]:
                for statement in statements:
                    self._eval_statement(statement)
            case unexpected: assert False, f"Internal Error at `{unexpected}`."

    def _eval_statement(self, statement):
        match statement:
            case ["print", expr]: self._eval_print(expr)
            case unexpected: assert False, f"Internal Error at `{unexpected}`."

    def _eval_print(self, expr):
        self.output.append(self._eval_expr(expr))

    def _eval_expr(self, expr):
        match expr:
            case int(value): return value
            case ["*", a, b]: return self._eval_expr(a) * self._eval_expr(b)
            case ["/", a, b]: return self._div(self._eval_expr(a), self._eval_expr(b))
            case ["+", a, b]: return self._eval_expr(a) + self._eval_expr(b)
            case ["-", a, b]: return self._eval_expr(a) - self._eval_expr(b)
            case unexpected: assert False, f"Internal Error at `{unexpected}`."

    def _div(self, a, b):
        assert b != 0, f"Division by zero."
        return a // b

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
            print(*evaluator.output, sep="\n")
        except AssertionError as e:
            print("Error:", e)
