class Interpreter:
    def __init__(self, source) -> None:
        self._source = source
        self._current_position = 0

    def interpret(self):
        while self._current_char() != "$EOF":
            while self._current_char().isspace(): self._current_position += 1

            start = self._current_position
            while  self._current_char().isalpha(): self._current_position += 1
            command = self._source[start:self._current_position]
            assert command == "print", f"`print` expected."

            while self._current_char().isspace(): self._current_position += 1

            start = self._current_position
            while  self._current_char().isnumeric():
                self._current_position += 1
            assert self._source[start:self._current_position].isnumeric(), f"Number expected."
            number = int(self._source[start:self._current_position])

            while self._current_char().isspace(): self._current_position += 1

            start = self._current_position
            self._current_position += 1
            assert self._source[start:self._current_position] == ";", f"Semicolon expected."

            while self._current_char().isspace(): self._current_position += 1

            print(number)

    def _current_char(self):
        if self._current_position < len(self._source):
            return self._source[self._current_position]
        else:
            return "$EOF"

import sys

while True:
    print("Input source and enter Ctrl+D:")
    if (source := sys.stdin.read()) == "": break

    print("Output:")
    try: Interpreter(source).interpret()
    except AssertionError as e: print("Error: ", e)
