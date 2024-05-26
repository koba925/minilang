class Interpreter:
    def __init__(self, source):
        self._source = source
        self._current_position = 0

    def interpret(self):
        while self._current_char().isspace(): self._current_position += 1
        start = self._current_position
        while  self._current_char().isalpha(): self._current_position += 1
        command = self._source[start:self._current_position]
        assert command == "print"

        while self._current_char().isspace(): self._current_position += 1
        start = self._current_position
        while  self._current_char().isnumeric():
            self._current_position += 1
        assert self._source[start:self._current_position].isnumeric()
        number = int(self._source[start:self._current_position])

        while self._current_char().isspace(): self._current_position += 1
        start = self._current_position
        self._current_position += 1
        assert self._source[start:self._current_position] == ";"

        while self._current_char().isspace(): self._current_position += 1
        assert self._current_char() == "$EOF"

        print(number)

    def _current_char(self):
        if self._current_position < len(self._source):
            return self._source[self._current_position]
        else:
            return "$EOF"

if __name__ == "__main__":
    while src := "\n".join(iter(lambda: input(": "), "")):
        Interpreter(src).interpret()

