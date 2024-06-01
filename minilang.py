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

class Interpreter:
    def __init__(self, source):
        self.scanner = Scanner(source)

    def interpret(self):
        command = self.scanner.next_token()
        assert command == "print", f"`print` expected, found `{command}`."

        number = self.scanner.next_token()
        assert isinstance(number, int), f"Number expected, found `{number}`."

        semicolon = self.scanner.next_token()
        assert semicolon == ";", f"Semicolon expected, found `{semicolon}`."

        eof = self.scanner.next_token()
        assert eof == "$EOF", f"EOF expected, found `{eof}`."


        print(number)

if __name__ == "__main__":
    while source := "\n".join(iter(lambda: input(": "), "")):
        try: Interpreter(source).interpret()
        except AssertionError as e: print(e)
