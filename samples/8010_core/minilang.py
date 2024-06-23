class Return(Exception):
    def __init__(self, value): self.value = value

class Environment:
    def __init__(self, parent:"Environment | None"=None):
        self._values = {}
        self._parent = parent

    def define(self, name, value):
        assert name not in self._values, f"`{name}` already defined."
        self._values[name] = value

    def assign(self, name, value):
        if name in self._values: self._values[name] = value
        elif self._parent is not None: self._parent.assign(name, value)
        else: assert False, f"`{name}` not defined."

    def get(self, name):
        if name in self._values: return self._values[name]
        if self._parent is not None: return self._parent.get(name)
        assert False, f"`{name}` not defined."

    def list(self):
        if self._parent is None: return [self._values]
        return self._parent.list() + [self._values]

class Evaluator:
    def __init__(self):
        self.output = []
        self._env = Environment()
        self._env.define("less", lambda a, b: a < b)
        self._env.define("print_env", self._print_env)

    def _print_env(self):
        for values in self._env.list():
            print({ k: self._to_print(v) for k, v in values.items() })

    def eval_program(self, program):
        self.output = []
        match program:
            case ["program", *statements]:
                for statement in statements:
                    self._eval_statement(statement)
            case unexpected: assert False, f"Internal Error at `{unexpected}`."

    def _eval_statement(self, statement):
        match statement:
            case ["block", *statements]: self._eval_block(statements)
            case ["var", name, value]: self._eval_var(name, value)
            case ["set", name, value]: self._eval_set(name, value)
            case ["if", cond, conseq, alt]: self._eval_if(cond, conseq, alt)
            case ["while", cond, body]: self._eval_while(cond, body)
            case ["return", value]: raise Return(self._eval_expr(value))
            case ["print", expr]: self._eval_print(expr)
            case ["expr", expr]: self._eval_expr(expr)
            case unexpected: assert False, f"Internal Error at `{unexpected}`."

    def _eval_block(self, statements):
        parent_env = self._env
        self._env = Environment(parent_env)
        for statement in statements:
            self._eval_statement(statement)
        self._env = parent_env

    def _eval_var(self, name, value):
        self._env.define(name, self._eval_expr(value))

    def _eval_set(self, name, value):
        self._env.assign(name, self._eval_expr(value))

    def _eval_if(self, cond, conseq, alt):
        if self._eval_expr(cond):
            self._eval_statement(conseq)
        else:
            self._eval_statement(alt)

    def _eval_while(self, cond, body):
        while self._eval_expr(cond):
            self._eval_statement(body)

    def _eval_print(self, expr):
        self.output.append(self._to_print(self._eval_expr(expr)))

    def _to_print(self, value):
        match value:
            case bool(b): return "true" if b else "false"
            case v if callable(v): return "<builtin>"
            case ["func", *_]: return "<func>"
            case _: return value

    def _eval_expr(self, expr):
        match expr:
            case int(value) | bool(value): return value
            case str(name): return self._eval_variable(name)
            case ["func", param, body]: return ["func", param, body, self._env]
            case ["^", a, b]: return self._eval_expr(a) ** self._eval_expr(b)
            case ["*", a, b]: return self._eval_expr(a) * self._eval_expr(b)
            case ["/", a, b]: return self._div(self._eval_expr(a), self._eval_expr(b))
            case ["+", a, b]: return self._eval_expr(a) + self._eval_expr(b)
            case ["-", a, b]: return self._eval_expr(a) - self._eval_expr(b)
            case ["=", a, b]: return self._eval_expr(a) == self._eval_expr(b)
            case ["#", a, b]: return self._eval_expr(a) != self._eval_expr(b)
            case [func, *args]:
                return self._apply(self._eval_expr(func),
                                   [self._eval_expr(arg) for arg in args])
            case unexpected: assert False, f"Internal Error at `{unexpected}`."

    def _div(self, a, b):
        assert b != 0, f"Division by zero."
        return a // b

    def _apply(self, func, args):
        if callable(func): return func(*args)

        [_, parameters, body, env] = func
        parent_env = self._env
        self._env = Environment(env)
        for param, arg in zip(parameters, args): self._env.define(param, arg)
        value = 0
        try:
            self._eval_statement(body)
        except Return as ret:
            value = ret.value
        self._env = parent_env
        return value

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
            evaluator.eval_program(eval(source))
            print(*evaluator.output, sep="\n")
        except AssertionError as e:
            print("Error:", e)
