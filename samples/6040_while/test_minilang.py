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

    def test_equality(self):
        self.assertEqual(get_output("print 5 + 7 = 3 * 4;"), ["true"])
        self.assertEqual(get_output("print 5 + 6 = 3 * 4;"), ["false"])
        self.assertEqual(get_output("print 5 + 7 # 3 * 4;"), ["false"])
        self.assertEqual(get_output("print 5 + 6 # 3 * 4;"), ["true"])
        self.assertEqual(get_output("print true = true;"), ["true"])
        self.assertEqual(get_output("print true = false;"), ["false"])
        self.assertEqual(get_output("print true # true;"), ["false"])
        self.assertEqual(get_output("print true # false;"), ["true"])
        self.assertEqual(get_ast("print 5 = 6 = true;"), ["program", ["print", ["=", ["=", 5, 6], True]]])
        self.assertEqual(get_output("print 5 = 6 = true;"), ["false"])

    def test_variable(self):
        self.assertEqual(get_output("var aa = 5 + 6; var bb = 7 * 8; print aa + bb;"), [67])
        self.assertEqual(get_output("var a = 5; print a; set a = a + 6; print a;"), [5, 11])
        self.assertEqual(get_output("var a = true; print a; set a = false; print a;"), ["true", "false"])
        self.assertEqual(get_error("var 1 = 1;"), "Expected a name, found `1`.")
        self.assertEqual(get_error("var a = 1; var a = 1;"), "`a` already defined.")
        self.assertEqual(get_error("set a;"), "Expected `=`, found `;`.")
        self.assertEqual(get_error("set 1 = 1;"), "Expected a name, found `1`.")
        self.assertEqual(get_error("set a = 1;"), "`a` not defined.")
        self.assertEqual(get_error("print a;"), "`a` not defined.")

    def test_scope(self):
        self.assertEqual(get_output("var a = 5 + 6; { var a = 7; print a; } print a;"), [7, 11])
        self.assertEqual(get_output("var a = 5 + 6; { set a = 7; print a; } print a;"), [7, 7])
        self.assertEqual(get_error("var a = 5 + 6; { var b = 7; print b; } print b;"), "`b` not defined.")
        self.assertEqual(get_error("{ print 1;"), "Unexpected token `$EOF`.")

    def test_if(self):
        self.assertEqual(get_ast("if 5 = 5 { print 6; }"), \
                         ["program", ["if", ["=", 5, 5], ["block", ["print", 6]], ["block"]]])
        self.assertEqual(get_output("if 5 = 5 { print 6; }"), [6])
        self.assertEqual(get_output("if 5 # 5 { print 6; }"), [])

        self.assertEqual(get_output("if true { if true { print 6; } }"), [6])
        self.assertEqual(get_output("if true { if false { print 6; } }"), [])

        self.assertEqual(get_error("if true print 5;"), "Expected `{`, found `print`.")

    def test_else(self):
        self.assertEqual(get_ast("if 5 = 5 { print 6; } else { print 7; }"), \
                         ["program", ["if", ["=", 5, 5], ["block", ["print", 6]], ["block", ["print", 7]]]])
        self.assertEqual(get_output("if 5 = 5 { print 6; } else { print 7; }"), [6])
        self.assertEqual(get_output("if 5 # 5 { print 6; } else { print 7; }"), [7])

        self.assertEqual(get_output("if true { print 6; } else { if true { print 7; } else {print 8;} }"), [6])
        self.assertEqual(get_output("if false { print 6; } else { if true { print 7; } else {print 8;} }"), [7])
        self.assertEqual(get_output("if false { print 6; } else { if false { print 7; } else {print 8;} }"), [8])

        self.assertEqual(get_error("if true { print 5; } else print 6;"), "Expected `{`, found `print`.")

    def test_elif(self):
        self.assertEqual(get_ast("if 5 # 5 { print 5; } elif 5 = 5 { print 6; } else { print 7; }"), \
                         ["program", ["if", ["#", 5, 5], ["block", ["print", 5]], ["if", ["=", 5, 5], ["block", ["print", 6]], ["block", ["print", 7]]]]])
        self.assertEqual(get_output("if 5 # 5 { print 5; } elif 5 = 5 { print 6; } else { print 7; }"), [6])

        self.assertEqual(get_output("if true { print 5; } elif true { print 6; } elif true { print 7; } else { print 8; }"), [5])
        self.assertEqual(get_output("if false { print 5; } elif true { print 6; } elif true { print 7; } else { print 8; }"), [6])
        self.assertEqual(get_output("if false { print 5; } elif false { print 6; } elif true { print 7; } else { print 8; }"), [7])
        self.assertEqual(get_output("if false { print 5; } elif false { print 6; } elif false { print 7; } else { print 8; }"), [8])
        self.assertEqual(get_output("if false { print 5; } elif false { print 6; } elif false { print 7; }"), [])

    def test_while(self):
        self.assertEqual(get_output("""
                                    var i = 0;
                                    while i # 3 {
                                        print i;
                                        set i = i + 1;
                                    }
                                    """), [0, 1, 2])
        self.assertEqual(get_error("while true print 2;"), "Expected `{`, found `print`.")

    def test_fib(self):
        self.assertEqual(get_output("""
                                    var i = 0; var a = 1; var b = 0; var tmp = 0;
                                    while i # 5 {
                                        print a;
                                        set tmp = a; set a = a + b; set b = tmp;
                                        set i = i + 1;
                                    }
                                    """), [1, 1, 2, 3, 5])

if __name__ == "__main__":
    unittest.main()
