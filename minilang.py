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

    def parse(self):
        block: list = ["block"]
        while self._current_token != "$EOF":
            block.append(self._statement())
        return block

    def _statement(self):
        match self._current_token:
            case "{": return self._block()
            case "if": return self._if()
            case "print": return self._print()
            case unexpected: assert False, f"Unexpected token `{unexpected}`."

    def _block(self):
        block: list = ["block"]
        self._next_token()
        while self._current_token != "}":
            block.append(self._statement())
        self._next_token()
        return block

    def _if(self):
        self._next_token()
        condtion = self._expression()
        self._check("{")
        consequence = self._block()
        alternative = ["block"]
        if self._current_token == "else":
            self._next_token()
            self._check("{")
            alternative = self._block()
        return ["if", condtion, consequence, alternative]

    def _print(self):
        self._next_token()
        expression = self._expression()
        self._consume(";")
        return ["print", expression]

    def _expression(self):
        return self._add_sub()

    def _add_sub(self):
        term = self._mult_div()
        while (op := self._current_token) in ("+", "-"):
            self._next_token()
            term = [op, term, self._mult_div()]
        return term

    def _mult_div(self):
        term = self._primary()
        while (op := self._current_token) in ("*", "/"):
            self._next_token()
            term = [op, term, self._primary()]
        return term

    def _primary(self):
        match self._current_token:
            case int(value):
                self._next_token()
                return value
            case unexpected: assert False, f"Unexpected token `{unexpected}`."

    def _check(self, expected_token):
        assert self._current_token == expected_token, \
               f"Expected `{expected_token}`, found `{self._current_token}`."

    def _consume(self, expected_token):
        self._check(expected_token)
        self._next_token()

    def _next_token(self):
        self._current_token = self.scanner.next_token()
        return self._current_token

class Evaluator:
    def __init__(self):
        self._output = []

    def clear_output(self): self._output = []
    def output(self): return self._output

    def evaluate(self, ast):
        match ast:
            case ["block", *statements]: self._block(statements)
            case ["if", condition, consequence, alternative]:
                self._if(condition, consequence, alternative)
            case ["print", expression]: self._print(expression)
            case unexpected: assert False, f"Internal Error at `{unexpected}`"

    def _block(self, statements):
        for statement in statements:
            self.evaluate(statement)

    def _if(self, condition, consequence, alternative):
        if condition != 0:
            self.evaluate(consequence)
        else:
            self.evaluate(alternative)

    def _print(self, expression):
        self._output.append(self._expression(expression))

    def _expression(self, expression):
        match expression:
            case int(value): return value
            case ["+", a, b]: return self._expression(a) + self._expression(b)
            case ["-", a, b]: return self._expression(a) - self._expression(b)
            case ["*", a, b]: return self._expression(a) * self._expression(b)
            case ["/", a, b]: return self._expression(a) // self._expression(b)
            case unexpected: assert False, f"Unexpected expression at `{unexpected}`."

if __name__ == "__main__":
    evaluator = Evaluator()
    while source := "\n".join(iter(lambda: input(": "), "")):
        try:
            evaluator.clear_output()
            evaluator.evaluate(Parser(source).parse())
            print(*evaluator.output(), sep="\n")
        except AssertionError as e: print(e)
