class Scanner:
    def __init__(self, source) -> None:
        self._source = source
        self._current_position = 0

    def next_token(self):
        while True:
            match self._current_char():
                case c if c.isspace(): self._current_position += 1
                case "!":
                    while self._current_char() not in ("\r", "\n", "$EOF"):
                        self._current_position += 1
                case _: break

        start = self._current_position
        match self._current_char():
            case "$EOF": return "$EOF"
            case c if c.isalpha():
                while self._current_char().isalnum() or self._current_char() == "_":
                    self._current_position += 1
                token = self._source[start:self._current_position]
                return None if token == "null" else token
            case c if c.isnumeric():
                while self._current_char().isnumeric():
                    self._current_position += 1
                return int(self._source[start:self._current_position])
            case "<" | ">":
                self._current_position += 1
                if self._current_char() == "=":
                    self._current_position += 1
                return self._source[start:self._current_position]
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
            case "{": return self._parse_block()
            case "var" | "set": return self._parse_var_set()
            case "if": return self._parse_if()
            case "while": return self._parse_while()
            case "for": return self._parse_for()
            case "break": return self._parse_break()
            case "continue": return self._parse_continue()
            case "def": return self._parse_def()
            case "return": return self._parse_return()
            case "print": return self._parse_print()
            case _: return self._parse_expression_statement()

    def _parse_block(self):
        block: list = ["block"]
        self._next_token()
        while self._current_token != "}":
            block.append(self._parse_statement())
        self._next_token()
        return block

    def _parse_var_set(self):
        op = self._current_token
        self._next_token()
        name = self._parse_primary()
        assert isinstance(name, str),  f"Expected a name, found `{name}`."
        value = None
        if op == "set" or self._current_token != ";":
            self._consume_token("=")
            value = self._parse_expression()
        self._consume_token(";")
        return [op, name, value]

    def _parse_if(self):
        self._next_token()
        cond = self._parse_expression()
        self._check_token("{")
        conseq = self._parse_block()
        alt = ["block"]
        if self._current_token == "elif":
            alt = self._parse_if()
        elif self._current_token == "else":
            self._next_token()
            self._check_token("{")
            alt = self._parse_block()
        return ["if", cond, conseq, alt]

    def _parse_while(self):
        self._next_token()
        cond = self._parse_expression()
        self._check_token("{")
        body = self._parse_block()
        then = ["block"]
        if self._current_token == "then":
            self._next_token()
            self._check_token("{")
            then = self._parse_block()
        return ["while", cond, body, then]

    def _parse_for(self):
        self._next_token()
        init_name = self._parse_primary()
        assert isinstance(init_name, str),  f"Expected a name, found `{init_name}`."
        self._consume_token("=")
        init_exp = self._parse_expression()
        self._consume_token(";")
        cond = self._parse_expression()
        self._consume_token(";")
        update_name = self._parse_primary()
        assert isinstance(update_name, str),  f"Expected a name, found `{update_name}`."
        self._consume_token("=")
        update_exp = self._parse_expression()
        self._check_token("{")
        body = self._parse_block()
        return ["for", init_name, init_exp, cond, update_name, update_exp, body]

    def _parse_break(self):
        self._next_token()
        self._consume_token(";")
        return ["break"]

    def _parse_continue(self):
        self._next_token()
        self._consume_token(";")
        return ["continue"]

    def _parse_def(self):
        self._next_token()
        name = self._parse_primary()
        assert isinstance(name, str),  f"Expected a name, found `{name}`."
        params = self._parse_parameters()
        body = self._parse_block()
        return ["var", name, ["func", params, body]]

    def _parse_return(self):
        self._next_token()
        value = None
        if self._current_token != ";": value = self._parse_expression()
        self._consume_token(";")
        return ["return", value]

    def _parse_print(self):
        self._next_token()
        expr = self._parse_expression()
        self._consume_token(";")
        return ["print", expr]

    def _parse_expression_statement(self):
        expr = self._parse_expression()
        self._consume_token(";")
        return ["expr", expr]

    def _parse_expression(self): return self._perse_ternary()

    def _perse_ternary(self):
        cond = self._parse_or()
        if self._current_token != "?": return cond
        self._next_token()
        conseq = self._perse_ternary()
        self._consume_token(":")
        alt = self._perse_ternary()
        return ["?", cond, conseq, alt]

    def _parse_or(self): return self._parse_binop_left(("|",), self._parse_and)
    def _parse_and(self): return self._parse_binop_left(("&",), self._parse_equality)
    def _parse_equality(self): return self._parse_binop_left(("=", "#"), self._parse_comparison)
    def _parse_comparison(self): return self._parse_binop_left((">", ">=", "<", "<="), self._parse_add_sub)
    def _parse_add_sub(self): return self._parse_binop_left(("+", "-"), self._parse_mult_div)
    def _parse_mult_div(self): return self._parse_binop_left(("*", "/"), self._parse_power)

    def _parse_binop_left(self, ops, sub_element):
        result = sub_element()
        while (op := self._current_token) in ops:
            self._next_token()
            result = [op, result, sub_element()]
        return result

    def _parse_power(self):
        power = self._parse_unary()
        if self._current_token != "^": return power
        self._next_token()
        return ["^", power, self._parse_power()]

    def _parse_unary(self):
        if self._current_token == "-":
            self._next_token()
            return ["-", self._parse_unary()]
        return self._parse_call()

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
            case None:
                self._next_token()
                return None
            case int(value) | str(value):
                self._next_token()
                return value
            case unexpected: assert False, f"Unexpected token `{unexpected}`."

    def _parse_func(self):
        self._next_token()
        params = self._parse_parameters()
        body = self._parse_block()
        return ["func", params, body]

    def _parse_parameters(self):
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
        return params

    def _check_token(self, expected_token):
        assert self._current_token == expected_token, \
               f"Expected `{expected_token}`, found `{self._current_token}`."

    def _consume_token(self, expected_token):
        self._check_token(expected_token)
        self._next_token()

    def _next_token(self):
        self._current_token = self.scanner.next_token()
        return self._current_token

class Break(Exception): pass
class Continue(Exception): pass
class Return(Exception):
    def __init__(self, value): self.value = value

import inspect , operator as op

class Evaluator:
    def __init__(self):
        self._output = []
        self._env: dict = {
            "less": lambda a, b: self._calc(lambda a, b: 1 if a < b else 0, a, b),
            "print_env": self._print_env
        }

    def clear_output(self): self._output = []
    def output(self): return self._output

    def _print_env(self):
        def _print(env, level):
            print(level, { k: self._to_str(v) for k, v in env.items() if k != "_parent" })
            if "_parent" in env: _print(env["_parent"], level + 1)
        _print(self._env, 0)

    def eval_statement(self, statement):
        match statement:
            case ["program", *statements]: self._eval_program(statements)
            case ["block", *statements]: self._eval_block(statements)
            case ["var", name, value]: self._eval_var(name, value)
            case ["set", name, value]: self._eval_set(name, value)
            case ["if", cond, conseq, alt]: self._eval_if(cond, conseq, alt)
            case ["while", cond, body, then]: self._eval_while(cond, body, then)
            case ["for", init_name, init_exp, cond, update_name, update_exp, body]:
                self._eval_for(init_name, init_exp, cond, update_name, update_exp, body)
            case ["break"]: raise Break()
            case ["continue"]: raise Continue()
            case ["return", value]: raise Return(self._eval_expr(value))
            case ["print", expr]: self._eval_print(expr)
            case ["expr", expr]: self._eval_expr(expr)
            case unexpected: assert False, f"Internal Error at `{unexpected}`."

    def _eval_program(self, statements):
        try:
            for statement in statements: self.eval_statement(statement)
        except Return:
            assert False, "Return from top level."

    def _eval_block(self, statements):
        parent_env = self._env
        self._env = {"_parent": parent_env}
        for statement in statements:
            self.eval_statement(statement)
        self._env = parent_env

    def _eval_var(self, name, value):
        assert name not in self._env, f"`{name}` already defined."
        self._env[name] = self._eval_expr(value)

    def _eval_set(self, name, value):
        def _set(env):
            if name in env: env[name] = self._eval_expr(value)
            elif "_parent" in env: _set(env["_parent"])
            else: assert False, f"`{name}` not defined."
        _set(self._env)

    def _eval_if(self, cond, conseq, alt):
        if self._eval_expr(cond) != 0:
            self.eval_statement(conseq)
        else:
            self.eval_statement(alt)

    def _eval_while(self, cond, body, then):
        while self._eval_expr(cond) != 0:
            try: self.eval_statement(body)
            except Continue: continue
            except Break: break
        else:
            self.eval_statement(then)

    def _eval_for(self, init_name, init_exp, cond, update_name, update_exp, body):
        self._eval_var(init_name, init_exp)
        while self._eval_expr(cond) != 0:
            try:
                self.eval_statement(body)
                self._eval_set(update_name, update_exp)
            except Continue:
                self._eval_set(update_name, update_exp)
                continue
            except Break: break

    def _eval_print(self, expr):
        self._output.append(self._to_str(self._eval_expr(expr)))

    def _to_str(self, value):
        match value:
            case v if callable(v): return "<builtin>"
            case ["func", *_]: return "<func>"
            case None: return "null"
            case _: return value

    def _eval_expr(self, expr):
        match expr:
            case int(value): return value
            case None: return None
            case str(name): return self._eval_variable(name)
            case ["func", param, body]: return ["func", param, body, self._env]
            case ["-", a]: return self._unary_minus(a)
            case ["^", a, b]: return self._apply_calc(op.pow, a, b)
            case ["*", a, b]: return self._apply_calc(op.mul, a, b)
            case ["/", a, b]: return self._apply_calc(self._div, a, b)
            case ["+", a, b]: return self._apply_calc(op.add, a, b)
            case ["-", a, b]: return self._apply_calc(op.sub, a, b)
            case ["<", a, b]: return 1 if self._apply_calc(op.lt, a, b) else 0
            case ["<=", a, b]: return 1 if self._apply_calc(op.le, a, b) else 0
            case [">", a, b]: return 1 if self._apply_calc(op.gt, a, b) else 0
            case [">=", a, b]: return 1 if self._apply_calc(op.ge, a, b) else 0
            case ["=", a, b]: return 1 if self._eval_expr(a) == self._eval_expr(b) else 0
            case ["#", a, b]: return 1 if self._eval_expr(a) != self._eval_expr(b) else 0
            case ["&", a, b]: return self._eval_and(a, b)
            case ["|", a, b]: return self._eval_or(a, b)
            case ["?", cond, conseq, alt]: return self._eval_ternary(cond, conseq, alt)
            case [func, *args]:
                return self._apply(self._eval_expr(func), [self._eval_expr(arg) for arg in args])
            case unexpected: assert False, f"Unexpected expression at `{unexpected}`."


    def _unary_minus(self, a):
        a = self._eval_expr(a)
        assert isinstance(a, int), f"Operand must be integer."
        return -a

    def _div(self, a, b):
        assert b != 0, f"Division by zero."
        return a // b

    def _apply_calc(self, op, a, b):
        a, b = self._eval_expr(a), self._eval_expr(b)
        return self._calc(op, a, b)

    def _calc(self, op, a, b):
        assert isinstance(a, int) and isinstance(b, int), f"Operands must be integers."
        return op(a, b)

    def _apply(self, func, args):
        if callable(func):
            parameters = inspect.signature(func).parameters
            assert len(parameters) == len(args), f"Parameter's count doesn't match."
            return func(*args)

        parent_env = self._env
        [_, parameters, body, env] = func
        assert len(parameters) == len(args), f"Parameter's count doesn't match."
        self._env = dict(zip(func[1], args)) | { "_parent": env }
        value = None
        try: self.eval_statement(body)
        except Return as ret: value = ret.value
        self._env = parent_env
        return value

    def _eval_and(self, a, b):
        a = self._eval_expr(a)
        return self._eval_expr(b) if a != 0 else a

    def _eval_or(self, a, b):
        a = self._eval_expr(a)
        return self._eval_expr(b) if a == 0 else a

    def _eval_ternary(self, cond, conseq, alt):
        cond = self._eval_expr(cond)
        return self._eval_expr(conseq) if cond != 0 else self._eval_expr(alt)

    def _eval_variable(self, name):
        def _get(env):
            if name in env: return env[name]
            if "_parent" in env: return _get(env["_parent"])
            assert False, f"`{name}` not defined."
        return _get(self._env)

if __name__ == "__main__":
    import sys

    def run_from_file(filename):
        evaluator = Evaluator()
        try:
            with open(sys.argv[1], "r") as f:
                evaluator.eval_statement(Parser(f.read()).parse_program())
        except AssertionError as e: print(e, file=sys.stderr)
        print(*evaluator.output(), sep="\n")

    def repl():
        evaluator = Evaluator()
        while source := "\n".join(iter(lambda: input(": "), "")):
            try:
                ast = Parser(source).parse_program()
                print(ast)
                evaluator.clear_output()
                evaluator.eval_statement(ast)
            except AssertionError as e: print(e)
            print(*evaluator.output(), sep="\n")

    if len(sys.argv) > 1:
        run_from_file(sys.argv[1])
    else:
        repl()