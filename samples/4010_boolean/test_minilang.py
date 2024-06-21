import unittest

from minilang import Parser, Evaluator

def get_ast(source): return Parser(source).parse_program()

def get_output(source):
    evaluator = Evaluator()
    evaluator.eval_program(Parser(source).parse_program())
    return evaluator.output

def get_error(source):
    try: output = get_output(source)
    except AssertionError as e: return str(e)
    else: return f"Error not occurred. out={output}"

class TestMinilang(unittest.TestCase):
    def test_print(self):
        self.assertEqual(get_ast(""), ["program"])
        self.assertEqual(get_output(""), [])

        self.assertEqual(get_ast(" \t\n"), ["program"])
        self.assertEqual(get_output(" \t\n"), [])

        self.assertEqual(get_ast("print 123;"), ["program", ["print", 123]])
        self.assertEqual(get_output("print 123;"), [123])

        self.assertEqual(get_ast("print 5; print 6; print 7;"), \
                         ["program", ["print", 5], ["print", 6], ["print", 7]])
        self.assertEqual(get_output("print 5; print 6; print 7;"), [5, 6, 7])
        self.assertEqual(get_output("  print  5  ;\n\tprint  6  ;  \n  print\n7\n\n ; \n"), [5, 6, 7])

        self.assertEqual(get_error("prin 5;"), "Unexpected token `prin`.")
        self.assertEqual(get_error("print a;"), "Unexpected token `a`.")
        self.assertEqual(get_error("print 5:"), "Expected `;`, found `:`.")
        self.assertEqual(get_error("print 5"), "Expected `;`, found `$EOF`.")
        self.assertEqual(get_error("print 5; prin 6;"), "Unexpected token `prin`.")

    def test_add_sum(self):
        self.assertEqual(get_output("print 5 + 6;"), [11])
        self.assertEqual(get_ast("print 5 + 6 + 7;"), ["program", ["print", ["+", ["+", 5, 6], 7]]])
        self.assertEqual(get_output("print 5 + 6 + 7;"), [18])

        self.assertEqual(get_output("print 18 - 7;"), [11])
        self.assertEqual(get_ast("print 18 - 7 - 6;"), ["program", ["print", ["-", ["-", 18, 7], 6]]])
        self.assertEqual(get_output("print 18 - 7 - 6;"), [5])

    def test_mul_div(self):
        self.assertEqual(get_output("print 5 * 6;"), [30])
        self.assertEqual(get_ast("print 5 * 6 * 7;"), ["program", ["print", ["*", ["*", 5, 6], 7]]])
        self.assertEqual(get_output("print 5 * 6 * 7;"), [210])

        self.assertEqual(get_output("print 210 / 7;"), [30])
        self.assertEqual(get_ast("print 210 / 7 / 6;"), ["program", ["print", ["/", ["/", 210, 7], 6]]])
        self.assertEqual(get_output("print 210 / 7 / 6;"), [5])
        self.assertEqual(get_error("print 5 / 0;"), "Division by zero.")

    def test_parens(self):
        self.assertEqual(get_ast("print (5 + 6) * 7;"), ["program", ["print", ["*", ["+", 5, 6], 7]]])
        self.assertEqual(get_output("print (5 + 6) * 7;"), [77])
        self.assertEqual(get_ast("print 5 * (6 + 7);"), ["program", ["print", ["*", 5, ["+", 6, 7]]]])
        self.assertEqual(get_output("print 5 * (6 + 7);"), [65])

    def test_power(self):
        self.assertEqual(get_output("print 2 ^ 3;"), [8])
        self.assertEqual(get_ast("print 2 ^ 2 ^ 3;"), ["program", ["print", ["^", 2, ["^", 2, 3]]]])
        self.assertEqual(get_output("print 2 ^ 2 ^ 3;"), [256])
        self.assertEqual(get_output("print 5 * 2 ^ 3;"), [40])

    def test_boolean(self):
        self.assertEqual(get_output("print true; print false;"), ["true", "false"])

if __name__ == "__main__":
    unittest.main()
