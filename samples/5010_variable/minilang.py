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
                token = self._source[start:self._current_position]
                match token:
                    case "true": return True
                    case "false": return False
                    case _: return token
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
            case "var" | "set": return self._parse_var_set()
            case "print": return self._parse_print()
            case unexpected: assert False, f"Unexpected token `{unexpected}`."

    def _parse_var_set(self):
        op = self._current_token
        self._next_token()
        name = self._parse_primary()
        assert isinstance(name, str),  f"Expected a name, found `{name}`."
        self._consume_token("=")
        value = self._parse_expression()
        self._consume_token(";")
        return [op, name, value]

    def _parse_print(self):
        self._next_token()
        expr = self._parse_expression()
        self._consume_token(";")
        return ["print", expr]

    def _parse_expression(self):
        return self._parse_equality()

    def _parse_equality(self): return self._parse_binop_left(("=", "#"), self._parse_add_sub)
    def _parse_add_sub(self): return self._parse_binop_left(("+", "-"), self._parse_mult_div)
    def _parse_mult_div(self): return self._parse_binop_left(("*", "/"), self._parse_power)

    def _parse_binop_left(self, ops, sub_element):
        result = sub_element()
        while (op := self._current_token) in ops:
            self._next_token()
            result = [op, result, sub_element()]
        return result

    def _parse_power(self):
        power = self._parse_primary()
        if self._current_token != "^": return power
        self._next_token()
        return ["^", power, self._parse_power()]

    def _parse_primary(self):
        match self._current_token:
            case "(":
                self._next_token()
                exp = self._parse_expression()
                self._consume_token(")")
                return exp
            case int(value) | bool(value) | str(value):
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


class Environment:
    def __init__(self):
        self._values = {}

    def define(self, name, value):
        assert name not in self._values, f"`{name}` already defined."
        self._values[name] = value

    def assign(self, name, value):
        if name in self._values: self._values[name] = value
        else: assert False, f"`{name}` not defined."

    def get(self, name):
        if name in self._values: return self._values[name]
        assert False, f"`{name}` not defined."

class Evaluator:
    def __init__(self):
        self.output = []
        self._env = Environment()

    def eval_program(self, program):
        self.output = []
        match program:
            case ["program", *statements]:
                for statement in statements:
                    self._eval_statement(statement)
            case unexpected: assert False, f"Internal Error at `{unexpected}`."

    def _eval_statement(self, statement):
        match statement:
            case ["var", name, value]: self._eval_var(name, value)
            case ["set", name, value]: self._eval_set(name, value)
            case ["print", expr]: self._eval_print(expr)
            case unexpected: assert False, f"Internal Error at `{unexpected}`."

    def _eval_var(self, name, value):
        self._env.define(name, self._eval_expr(value))

    def _eval_set(self, name, value):
        self._env.assign(name, self._eval_expr(value))

    def _eval_print(self, expr):
        self.output.append(self._to_print(self._eval_expr(expr)))

    def _to_print(self, value):
        match value:
            case bool(b): return "true" if b else "false"
            case _: return value

    def _eval_expr(self, expr):
        match expr:
            case int(value) | bool(value): return value
            case str(name): return self._eval_variable(name)
            case ["^", a, b]: return self._eval_expr(a) ** self._eval_expr(b)
            case ["*", a, b]: return self._eval_expr(a) * self._eval_expr(b)
            case ["/", a, b]: return self._div(self._eval_expr(a), self._eval_expr(b))
            case ["+", a, b]: return self._eval_expr(a) + self._eval_expr(b)
            case ["-", a, b]: return self._eval_expr(a) - self._eval_expr(b)
            case ["=", a, b]: return self._eval_expr(a) == self._eval_expr(b)
            case ["#", a, b]: return self._eval_expr(a) != self._eval_expr(b)
            case unexpected: assert False, f"Internal Error at `{unexpected}`."

    def _div(self, a, b):
        assert b != 0, f"Division by zero."
        return a // b

    def _eval_variable(self, name):
        return self._env.get(name)

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
