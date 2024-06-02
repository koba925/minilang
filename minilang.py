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
            case token: assert False, f"Unexpected token `{token}`."

    def _block(self):
        block: list = ["block"]
        self._next_token()
        while self._current_token != "}":
            block.append(self._statement())
        self._next_token()
        return block

    def _if(self):
        condtion = self._next_token()
        assert isinstance(condtion, int), f"Number expected, found `{condtion}`."
        self._next_token()
        self._check("{")
        consequence = self._block()
        alternative = ["block"]
        if self._current_token == "else":
            self._next_token()
            self._check("{")
            alternative = self._block()
        return ["if", condtion, consequence, alternative]

    def _print(self):
        number = self._next_token()
        assert isinstance(number, int), f"Number expected, found `{number}`."
        self._next_token()
        self._consume(";")
        return ["print", number]

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
            case ["print", val]: self._output.append(val)
            case _: assert False, "Internal Error."

    def _block(self, statements):
        for statement in statements:
            self.evaluate(statement)

    def _if(self, condition, consequence, alternative):
        if condition != 0:
            self.evaluate(consequence)
        else:
            self.evaluate(alternative)

if __name__ == "__main__":
    evaluator = Evaluator()
    while source := "\n".join(iter(lambda: input(": "), "")):
        try:
            evaluator.clear_output()
            evaluator.evaluate(Parser(source).parse())
            print(*evaluator.output(), sep="\n")
        except AssertionError as e: print(e)
