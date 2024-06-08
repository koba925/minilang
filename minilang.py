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
            case _: return self._expression_statement()

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

    def _expression_statement(self):
        expression = self._parse_expression()
        self._consume_token(";")
        return ["expression", expression]

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
        power = self._parse_call()
        if self._current_token != "^": return power
        self._next_token()
        return ["^", power, self._parse_power()]

    def _parse_call(self):
        call = self._parse_primary()
        while self._current_token == "(":
            self._next_token()
            args = []
            while self._current_token != ")":
                args.append(self._parse_expression())
                if self._current_token != ")":
                    self._consume_token(",")
            call = [call] + args
            self._consume_token(")")
        return call

    def _parse_primary(self):
        match self._current_token:
            case "(":
                self._next_token()
                exp = self._parse_expression()
                self._consume_token(")")
                return exp
            case "func": return self._parse_func()
            case int(value) | str(value):
                self._next_token()
                return value
            case unexpected: assert False, f"Unexpected token `{unexpected}`."

    def _parse_func(self):
        self._next_token()
        self._consume_token("(")
        params = []
        while self._current_token != ")":
            param = self._current_token
            assert isinstance(param, str), f"Name expected, found `{param}`."
            self._next_token()
            params.append(param)
            if self._current_token != ")":
                self._consume_token(",")
        self._consume_token(")")
        body = self._parse_block()
        return ["func", params, body]

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
        self._env: dict = {
            "less": lambda a, b: 1 if a < b else 0,
            "print_env": self._print_env
        }

    def clear_output(self): self._output = []
    def output(self): return self._output

    def _print_env(self):
        def _print(env, level):
            print(level, { k:"<builtin>" if callable(v) else v for k, v in env.items() if k != "_parent" })
            if "_parent" in env: _print(env["_parent"], level + 1)
        _print(self._env, 0)

    def eval_statement(self, statement):
        match statement:
            case ["block", *statements]: self._eval_block(statements)
            case ["var", name, value]: self._eval_var(name, value)
            case ["set", name, value]: self._eval_set(name, value)
            case ["if", condition, consequence, alternative]:
                self._eval_if(condition, consequence, alternative)
            case ["while", condition, body]:
                self._eval_while(condition, body)
            case ["expression", expression]: self._eval_expression(expression)
            case ["print", expression]: self._eval_print(expression)
            case unexpected: assert False, f"Internal Error at `{unexpected}`."

    def _eval_block(self, statements):
        parent_env = self._env
        self._env = {"_parent": parent_env}
        for statement in statements:
            self.eval_statement(statement)
        self._env = parent_env

    def _eval_var(self, name, value):
        assert name not in self._env, f"`{name}` already defined."
        self._env[name] = self._eval_exp(value)

    def _eval_set(self, name, value):
        def _set(env):
            if name in env: env[name] = self._eval_exp(value)
            elif "_parent" in env: _set(env["_parent"])
            else: assert False, f"`{name}` not defined."
        _set(self._env)

    def _eval_if(self, condition, consequence, alternative):
        if self._eval_exp(condition) != 0:
            self.eval_statement(consequence)
        else:
            self.eval_statement(alternative)

    def _eval_while(self, condition, body):
        while self._eval_exp(condition) != 0:
            self.eval_statement(body)

    def _eval_expression(self, expression):
        self._eval_exp(expression)

    def _eval_print(self, expression):
        self._output.append(self._eval_exp(expression))

    def _eval_exp(self, expression):
        match expression:
            case int(value): return value
            case str(name): return self._eval_variable(name)
            case ["func", param, body]: return ["func", param, body]
            case ["=", a, b]: return 1 if self._eval_exp(a) == self._eval_exp(b) else 0
            case ["#", a, b]: return 1 if self._eval_exp(a) != self._eval_exp(b) else 0
            case ["+", a, b]: return self._eval_exp(a) + self._eval_exp(b)
            case ["-", a, b]: return self._eval_exp(a) - self._eval_exp(b)
            case ["*", a, b]: return self._eval_exp(a) * self._eval_exp(b)
            case ["/", a, b]: return self._eval_exp(a) // self._eval_exp(b)
            case ["^", a, b]: return self._eval_exp(a) ** self._eval_exp(b)
            case [op, *args]:
                op, args = self._eval_exp(op), [self._eval_exp(arg) for arg in args]
                return op(*args) if callable(op) else self._apply(op, args)
            case unexpected: assert False, f"Unexpected expression at `{unexpected}`."

    def _apply(self, op, args):
        parent_env = self._env
        self._env = dict(zip(op[1], args)) | { "_parent": parent_env }
        self.eval_statement(op[2])
        self.env = parent_env
        return 0

    def _eval_variable(self, name):
        def _get(env):
            if name in env: return env[name]
            if "_parent" in env: return _get(env["_parent"])
            assert False, f"`{name}` not defined."
        return _get(self._env)

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
