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
        block: list = ["block"]
        while self._current_token != "$EOF":
            block.append(self._parse_statement())
        return block

    def _parse_statement(self):
        match self._current_token:
            case "{": return self._parse_block()
            case "var" | "set": return self._parse_var_set()
            case "if": return self._parse_if()
            case "while": return self._parse_while()
            case "print": return self._parse_print()
            case unexpected: assert False, f"Unexpected token `{unexpected}`."

    def _parse_block(self):
        block: list = ["block"]
        self._next_token()
        while self._current_token != "}":
            block.append(self._parse_statement())
        self._next_token()
        return block

    def _parse_if(self):
        self._next_token()
        condtion = self._parse_expression()
        self._check_token("{")
        consequence = self._parse_block()
        alternative = ["block"]
        if self._current_token == "else":
            self._next_token()
            self._check_token("{")
            alternative = self._parse_block()
        return ["if", condtion, consequence, alternative]

    def _parse_while(self):
        self._next_token()
        condtion = self._parse_expression()
        self._check_token("{")
        body = self._parse_block()
        return ["while", condtion, body]

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
        expression = self._parse_expression()
        self._consume_token(";")
        return ["print", expression]

    def _parse_expression(self):
        return self._parse_equality()

    def _parse_equality(self):
        equality = self._parse_add_sub()
        while (op := self._current_token) in ("=", "#"):
            self._next_token()
            equality = [op, equality, self._parse_add_sub()]
        return equality

    def _parse_add_sub(self):
        add_sub = self._parse_mult_div()
        while (op := self._current_token) in ("+", "-"):
            self._next_token()
            add_sub = [op, add_sub, self._parse_mult_div()]
        return add_sub

    def _parse_mult_div(self):
        mult_div = self._parse_power()
        while (op := self._current_token) in ("*", "/"):
            self._next_token()
            mult_div = [op, mult_div, self._parse_power()]
        return mult_div

    def _parse_power(self):
        exp = self._parse_primary()
        if self._current_token != "^": return exp
        self._next_token()
        return ["^", exp, self._parse_power()]

    def _parse_primary(self):
        match self._current_token:
            case "(":
                self._next_token()
                exp = self._parse_expression()
                self._consume_token(")")
                return exp
            case int(value) | str(value):
                self._next_token()
                return value
            case unexpected: assert False, f"Unexpected token `{unexpected}`."

    def _check_token(self, expected_token):
        assert self._current_token == expected_token, \
               f"Expected `{expected_token}`, found `{self._current_token}`."

    def _consume_token(self, expected_token):
        self._check_token(expected_token)
        self._next_token()

    def _next_token(self):
        self._current_token = self.scanner.next_token()
        return self._current_token

class Evaluator:
    def __init__(self):
        self._output = []
        self._env = {}

    def clear_output(self): self._output = []
    def output(self): return self._output

    def eval_statement(self, statement):
        match statement:
            case ["block", *statements]: self._eval_block(statements)
            case ["var", name, value]: self._eval_var(name, value)
            case ["set", name, value]: self._eval_set(name, value)
            case ["if", condition, consequence, alternative]:
                self._eval_if(condition, consequence, alternative)
            case ["while", condition, body]:
                self._eval_while(condition, body)
            case ["print", expression]: self._eval_print(expression)
            case unexpected: assert False, f"Internal Error at `{unexpected}`."

    def _eval_block(self, statements):
        for statement in statements:
            self.eval_statement(statement)

    def _eval_var(self, name, value):
        assert name not in self._env, f"`{name}` already defined."
        self._env[name] = self._eval_exp(value)

    def _eval_set(self, name, value):
        assert name in self._env, f"`{name}` not defined."
        self._env[name] = self._eval_exp(value)

    def _eval_if(self, condition, consequence, alternative):
        if self._eval_exp(condition) != 0:
            self.eval_statement(consequence)
        else:
            self.eval_statement(alternative)

    def _eval_while(self, condition, body):
        while self._eval_exp(condition) != 0:
            self.eval_statement(body)

    def _eval_print(self, expression):
        self._output.append(self._eval_exp(expression))

    def _eval_exp(self, expression):
        match expression:
            case int(value): return value
            case str(name): return self._eval_variable(name)
            case ["=", a, b]: return 1 if self._eval_exp(a) == self._eval_exp(b) else 0
            case ["#", a, b]: return 1 if self._eval_exp(a) != self._eval_exp(b) else 0
            case ["+", a, b]: return self._eval_exp(a) + self._eval_exp(b)
            case ["-", a, b]: return self._eval_exp(a) - self._eval_exp(b)
            case ["*", a, b]: return self._eval_exp(a) * self._eval_exp(b)
            case ["/", a, b]: return self._eval_exp(a) // self._eval_exp(b)
            case ["^", a, b]: return self._eval_exp(a) ** self._eval_exp(b)
            case unexpected: assert False, f"Unexpected expression at `{unexpected}`."

    def _eval_variable(self, name):
        assert name in self._env, f"`{name}` not defined."
        return self._env[name]

if __name__ == "__main__":
    evaluator = Evaluator()
    while source := "\n".join(iter(lambda: input(": "), "")):
        try:
            ast = Parser(source).parse_program()
            print(ast)
            evaluator.clear_output()
            evaluator.eval_statement(ast)
            print(*evaluator.output(), sep="\n")
        except AssertionError as e: print(e)
