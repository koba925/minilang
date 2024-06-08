import unittest

from minilang import Parser, Evaluator

def get_ast(source): return Parser(source).parse_program()

def get_output(source):
    evaluator = Evaluator()
    evaluator.eval_statement(Parser(source).parse_program())
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
        self.assertEqual(get_error("print 1:"), "Expected `;`, found `:`.")
        self.assertEqual(get_error("print 1"), "Expected `;`, found `$EOF`.")

    def test_statements(self):
        self.assertEqual(get_output(""), [])
        self.assertEqual(get_output("print 1; print 2;"), [1, 2])
        self.assertEqual(get_error("print 1; prin"), "Unexpected token `prin`.")

    def test_block(self):
        self.assertEqual(get_ast("print 1; { print 2; print 3; } print 4;"),
                         ["block", ["print", 1], ["block", ["print", 2], ["print", 3]], ["print", 4]])
        self.assertEqual(get_output("print 1; { print 2; print 3; } print 4;"), [1, 2, 3, 4])

    def test_power(self):
        self.assertEqual(get_output("print 2 ^ 3;"), [8])
        self.assertEqual(get_ast("print 2 ^ 2 ^ 3;"), ["block", ["print", ["^", 2, ["^", 2, 3]]]])
        self.assertEqual(get_output("print 2 ^ 2 ^ 3;"), [256])

    def test_factor(self):
        self.assertEqual(get_output("print 2 * 3;"), [6])
        self.assertEqual(get_ast("print 2 * 3 * 4;"), ["block", ["print", ["*", ["*", 2, 3], 4]]])
        self.assertEqual(get_output("print 2 * 3 * 4;"), [24])
        self.assertEqual(get_output("print 24 / 2;"), [12])
        self.assertEqual(get_ast("print 24 / 4 / 2;"), ["block", ["print", ["/", ["/", 24, 4], 2]]])
        self.assertEqual(get_output("print 24 / 4 / 2;"), [3])
        self.assertEqual(get_output("print 2 ^ 3 * 2;"), [16])
        self.assertEqual(get_output("print 2 * 2 ^ 3;"), [16])

    def test_term(self):
        self.assertEqual(get_output("print 2 + 3;"), [5])
        self.assertEqual(get_ast("print 2 + 3 + 4;"), ["block", ["print", ["+", ["+", 2, 3], 4]]])
        self.assertEqual(get_output("print 2 + 3 + 4;"), [9])
        self.assertEqual(get_output("print 9 - 3;"), [6])
        self.assertEqual(get_ast("print 9 - 4 - 2;"), ["block", ["print", ["-", ["-", 9, 4], 2]]])
        self.assertEqual(get_output("print 9 - 4 - 2;"), [3])
        self.assertEqual(get_ast("print 2 + 3 * 4;"), ["block", ["print", ["+", 2, ["*", 3, 4]]]])
        self.assertEqual(get_output("print 2 + 3 * 4;"), [14])
        self.assertEqual(get_ast("print 2 * 3 + 4;"), ["block", ["print", ["+", ["*", 2, 3], 4]]])
        self.assertEqual(get_output("print 2 * 3 + 4;"), [10])

    def test_equality(self):
        self.assertEqual(get_output("print 2 = 2;"), [1])
        self.assertEqual(get_output("print 2 = 3;"), [0])
        self.assertEqual(get_output("print 2 # 2;"), [0])
        self.assertEqual(get_output("print 2 # 3;"), [1])
        self.assertEqual(get_ast("print 1 = 2 = 2;"), ["block", ["print", ["=", ["=", 1, 2], 2]]])
        self.assertEqual(get_output("print 1 = 2 = 2;"), [0])
        self.assertEqual(get_output("print 1 + 2 = 6 - 3;"), [1])

    def test_grouping(self):
        self.assertEqual(get_ast("print (2 + 3) * 4;"), ["block", ["print", ["*", ["+", 2, 3], 4]]])
        self.assertEqual(get_output("print (2 + 3) * 4;"), [20])
        self.assertEqual(get_ast("print 2 * (3 + 4);"), ["block", ["print", ["*", 2, ["+", 3, 4]]]])
        self.assertEqual(get_output("print 2 * (3 + 4);"), [14])

    def test_if(self):
        self.assertEqual(get_ast("if 1 { print 2; }"), ["block", ["if", 1, ["block", ["print", 2]], ["block"]]])
        self.assertEqual(get_output("if 1 { print 2; }"), [2])
        self.assertEqual(get_output("if 0 { print 2; }"), [])
        self.assertEqual(get_output("if 1 + 2 = 4 - 1 { print 1; }"), [1])
        self.assertEqual(get_output("if 1 + 2 # 4 - 1 { print 1; }"), [])
        self.assertEqual(get_output("if 1 { if 1 { print 2; } }"), [2])
        self.assertEqual(get_output("if 1 { if 0 { print 2; } }"), [])
        self.assertEqual(get_error("if 1 print 2;"), "Expected `{`, found `print`.")

    def test_else(self):
        self.assertEqual(get_ast("if 1 { print 2; } else { print 3; }"),
                         ["block", ["if", 1, ["block", ["print", 2]], ["block", ["print", 3]]]])
        self.assertEqual(get_output("if 1 { print 2; } else { print 3; }"), [2])
        self.assertEqual(get_output("if 0 { print 2; } else { print 3; }"), [3])
        self.assertEqual(get_output("if 1 + 2 = 4 - 1 { print 1; } else { print 2; }"), [1])
        self.assertEqual(get_output("if 1 + 2 # 4 - 1 { print 1; } else { print 2; }"), [2])
        self.assertEqual(get_error("if 1 { print 2; } else print 3;"), "Expected `{`, found `print`.")

    def test_var(self):
        self.assertEqual(get_output("var a = 1 + 2; print a; set a = a + 3; print a;"), [3, 6])
        self.assertEqual(get_output("var a = 1; var b = 2; print a; print b;"), [1, 2])
        self.assertEqual(get_error("var a;"), "Expected `=`, found `;`.")
        self.assertEqual(get_error("var a = 1; var a = 1;"), "`a` already defined.")
        self.assertEqual(get_error("set a;"), "Expected `=`, found `;`.")
        self.assertEqual(get_error("set a = 1;"), "`a` not defined.")
        self.assertEqual(get_error("print a;"), "`a` not defined.")

if __name__ == "__main__":
    unittest.main()
