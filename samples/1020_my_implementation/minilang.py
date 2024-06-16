def interpret(source):
    current_position = 0

    while current_position < len(source):
        while current_position < len(source) and source[current_position].isspace():
            current_position += 1

        start = current_position
        while  current_position < len(source) and source[current_position].isalpha():
            current_position += 1
        command = source[start:current_position]
        assert command == "print", f"Expected `print`."

        while current_position < len(source) and source[current_position].isspace():
            current_position += 1

        start = current_position
        while  current_position < len(source) and source[current_position].isnumeric():
            current_position += 1
        assert source[start:current_position].isnumeric(), f"Expected number."
        number = int(source[start:current_position])

        while current_position < len(source) and source[current_position].isspace():
            current_position += 1

        start = current_position
        if current_position < len(source): current_position += 1
        assert source[start:current_position] == ";", f"Expected semicolon."

        while current_position < len(source) and source[current_position].isspace():
            current_position += 1

        print(number)

import sys

while True:
    print("Input source and enter Ctrl+D:")
    if (source := sys.stdin.read()) == "": break

    print("Output:")
    try: interpret(source)
    except AssertionError as e: print("Error: ", e)
