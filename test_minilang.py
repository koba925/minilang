import unittest

from minilang import Parser, Evaluator

def get_output(source):
    evaluator = Evaluator()
    evaluator.evaluate(Parser(source).parse())
    return evaluator.output()

def get_error(source):
    try: output = get_output(source)
    except AssertionError as e: return str(e)
    else: return f"Error not occurred. out={output}"

class TestMinilang(unittest.TestCase):
    def test_print(self):
        self.assertEqual(get_output("print 1;"), [1])
        self.assertEqual(get_output("  print\n  12  ;\n  "), [12])
        self.assertEqual(get_error("prin 1;"), "Unexpected token `prin`.")
        self.assertEqual(get_error("print a;"), "Number expected, found `a`.")
        self.assertEqual(get_error("print 1:"), "Expected `;`, found `:`.")
        self.assertEqual(get_error("print 1"), "Expected `;`, found `$EOF`.")

    def test_statements(self):
        self.assertEqual(get_output(""), [])
        self.assertEqual(get_output("print 1; print 2;"), [1, 2])
        self.assertEqual(get_error("print 1; prin"), "Unexpected token `prin`.")

    def test_block(self):
        self.assertEqual(Parser("print 1; { print 2; print 3; } print 4;").parse(),
                         ["block", ["print", 1], ["block", ["print", 2], ["print", 3]], ["print", 4]])
        self.assertEqual(get_output("print 1; { print 2; print 3; } print 4;"), [1, 2, 3, 4])

    def test_if(self):
        self.assertEqual(get_output("if 1 { print 2; }"), [2])
        self.assertEqual(get_output("if 0 { print 2; }"), [])
        self.assertEqual(get_output("if 1 { if 1 { print 2; } }"), [2])
        self.assertEqual(get_output("if 1 { if 0 { print 2; } }"), [])
        self.assertEqual(get_error("if a { print 2; }"), "Number expected, found `a`.")
        self.assertEqual(get_error("if 1 print 2;"), "Expected `{`, found `print`.")

    def test_else(self):
        self.assertEqual(get_output("if 1 { print 2; } else { print 3; }"), [2])
        self.assertEqual(get_output("if 0 { print 2; } else { print 3; }"), [3])
        self.assertEqual(get_error("if 1 { print 2; } else print 3;"), "Expected `{`, found `print`.")

if __name__ == "__main__":
    unittest.main()
