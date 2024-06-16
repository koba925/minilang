import sys, re

def interpret(source):
    statement_pattern = re.compile(r"\s*print\s*(\d+)\s*;\s*")

    current_position = 0
    while current_position < len(source):
        statement = statement_pattern.match(source, current_position)
        assert statement is not None, "Does not match."
        print(int(statement.group(1)))
        current_position = statement.end()

while True:
    print("Input source and enter Ctrl+D:")
    if (source := sys.stdin.read()) == "": break

    print("Output:")
    try: interpret(source)
    except AssertionError as e: print("Error: ", e)
