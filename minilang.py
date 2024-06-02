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
        self.current_token = ""

    def parse(self):
        command = self._next_token()
        assert command == "print", f"`print` expected, found `{command}`."

        number = self._next_token()
        assert isinstance(number, int), f"Number expected, found `{number}`."

        self._next_token()
        self._consume(";")

        self._consume("$EOF")

        return ["print", number]

    def _consume(self, expected_token):
        assert self.current_token == expected_token, \
               f"Expected `{expected_token}`, found `{self.current_token}`."
        self._next_token()

    def _next_token(self):
        self.current_token = self.scanner.next_token()
        return self.current_token

class Evaluator:
    def __init__(self):
        self._output = []

    def clear_output(self): self._output = []
    def output(self): return self._output

    def evaluate(self, ast):
        match ast:
            case ["print", val]: self._output.append(val)
            case _: assert False, "Internal Error."

if __name__ == "__main__":
    evaluator = Evaluator()
    while source := "\n".join(iter(lambda: input(": "), "")):
        try:
            evaluator.clear_output()
            evaluator.evaluate(Parser(source).parse())
            print(*evaluator.output(), sep="\n")
        except AssertionError as e: print(e)
