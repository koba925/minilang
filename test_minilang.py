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
        # self.assertEqual(get_error("prin 1;"), "Unexpected token `prin`.")
        self.assertEqual(get_error("prin 1;"), "Expected `;`, found `1`.")
        self.assertEqual(get_error("print 1:"), "Expected `;`, found `:`.")
        self.assertEqual(get_error("print 1"), "Expected `;`, found `$EOF`.")

    def test_statements(self):
        self.assertEqual(get_output(""), [])
        self.assertEqual(get_output("print 1; print 2;"), [1, 2])
        # self.assertEqual(get_error("print 1; prin"), "Unexpected token `prin`.")
        self.assertEqual(get_error("print 1; prin"), "Expected `;`, found `$EOF`.")

    def test_block(self):
        self.assertEqual(get_ast("print 1; { print 2; print 3; } print 4;"),
                         ["program", ["print", 1], ["block", ["print", 2], ["print", 3]], ["print", 4]])
        self.assertEqual(get_output("print 1; { print 2; print 3; } print 4;"), [1, 2, 3, 4])

    def test_power(self):
        self.assertEqual(get_output("print 2 ^ 3;"), [8])
        self.assertEqual(get_ast("print 2 ^ 2 ^ 3;"), ["program", ["print", ["^", 2, ["^", 2, 3]]]])
        self.assertEqual(get_output("print 2 ^ 2 ^ 3;"), [256])

    def test_factor(self):
        self.assertEqual(get_output("print 2 * 3;"), [6])
        self.assertEqual(get_ast("print 2 * 3 * 4;"), ["program", ["print", ["*", ["*", 2, 3], 4]]])
        self.assertEqual(get_output("print 2 * 3 * 4;"), [24])
        self.assertEqual(get_output("print 24 / 2;"), [12])
        self.assertEqual(get_ast("print 24 / 4 / 2;"), ["program", ["print", ["/", ["/", 24, 4], 2]]])
        self.assertEqual(get_output("print 24 / 4 / 2;"), [3])
        self.assertEqual(get_output("print 2 ^ 3 * 2;"), [16])
        self.assertEqual(get_output("print 2 * 2 ^ 3;"), [16])

    def test_term(self):
        self.assertEqual(get_output("print 2 + 3;"), [5])
        self.assertEqual(get_ast("print 2 + 3 + 4;"), ["program", ["print", ["+", ["+", 2, 3], 4]]])
        self.assertEqual(get_output("print 2 + 3 + 4;"), [9])
        self.assertEqual(get_output("print 9 - 3;"), [6])
        self.assertEqual(get_ast("print 9 - 4 - 2;"), ["program", ["print", ["-", ["-", 9, 4], 2]]])
        self.assertEqual(get_output("print 9 - 4 - 2;"), [3])
        self.assertEqual(get_ast("print 2 + 3 * 4;"), ["program", ["print", ["+", 2, ["*", 3, 4]]]])
        self.assertEqual(get_output("print 2 + 3 * 4;"), [14])
        self.assertEqual(get_ast("print 2 * 3 + 4;"), ["program", ["print", ["+", ["*", 2, 3], 4]]])
        self.assertEqual(get_output("print 2 * 3 + 4;"), [10])

    def test_equality(self):
        self.assertEqual(get_output("print 2 = 2;"), [1])
        self.assertEqual(get_output("print 2 = 3;"), [0])
        self.assertEqual(get_output("print 2 # 2;"), [0])
        self.assertEqual(get_output("print 2 # 3;"), [1])
        self.assertEqual(get_ast("print 1 = 2 = 2;"), ["program", ["print", ["=", ["=", 1, 2], 2]]])
        self.assertEqual(get_output("print 1 = 2 = 2;"), [0])
        self.assertEqual(get_output("print 1 + 2 = 6 - 3;"), [1])

    def test_grouping(self):
        self.assertEqual(get_ast("print (2 + 3) * 4;"), ["program", ["print", ["*", ["+", 2, 3], 4]]])
        self.assertEqual(get_output("print (2 + 3) * 4;"), [20])
        self.assertEqual(get_ast("print 2 * (3 + 4);"), ["program", ["print", ["*", 2, ["+", 3, 4]]]])
        self.assertEqual(get_output("print 2 * (3 + 4);"), [14])

    def test_var(self):
        self.assertEqual(get_output("var a = 1 + 2; print a; set a = a + 3; print a;"), [3, 6])
        self.assertEqual(get_output("var a = 1; var b = 2; print a; print b;"), [1, 2])
        self.assertEqual(get_error("var a;"), "Expected `=`, found `;`.")
        self.assertEqual(get_error("var 1 = 1;"), "Expected a name, found `1`.")
        self.assertEqual(get_error("var a = 1; var a = 1;"), "`a` already defined.")
        self.assertEqual(get_error("set a;"), "Expected `=`, found `;`.")
        self.assertEqual(get_error("set 1 = 1;"), "Expected a name, found `1`.")
        self.assertEqual(get_error("set a = 1;"), "`a` not defined.")
        self.assertEqual(get_error("print a;"), "`a` not defined.")

    def test_scope(self):
        self.assertEqual(get_output("var a = 2; { var a = 4; print a; } print a;"), [4, 2])
        self.assertEqual(get_output("var a = 2; { set a = 4; print a; } print a;"), [4, 4])
        self.assertEqual(get_error("var a = 2; { var b = 4; print b; } print b;"), "`b` not defined.")

    def test_if(self):
        self.assertEqual(get_ast("if 1 { print 2; }"), ["program", ["if", 1, ["block", ["print", 2]], ["block"]]])
        self.assertEqual(get_output("if 1 { print 2; }"), [2])
        self.assertEqual(get_output("if 0 { print 2; }"), [])
        self.assertEqual(get_output("if 1 + 2 = 4 - 1 { print 1; }"), [1])
        self.assertEqual(get_output("if 1 + 2 # 4 - 1 { print 1; }"), [])
        self.assertEqual(get_output("if 1 { if 1 { print 2; } }"), [2])
        self.assertEqual(get_output("if 1 { if 0 { print 2; } }"), [])
        self.assertEqual(get_error("if 1 print 2;"), "Expected `{`, found `print`.")

    def test_else(self):
        self.assertEqual(get_ast("if 1 { print 2; } else { print 3; }"),
                         ["program", ["if", 1, ["block", ["print", 2]], ["block", ["print", 3]]]])
        self.assertEqual(get_output("if 1 { print 2; } else { print 3; }"), [2])
        self.assertEqual(get_output("if 0 { print 2; } else { print 3; }"), [3])
        self.assertEqual(get_output("if 1 + 2 = 4 - 1 { print 1; } else { print 2; }"), [1])
        self.assertEqual(get_output("if 1 + 2 # 4 - 1 { print 1; } else { print 2; }"), [2])
        self.assertEqual(get_error("if 1 { print 2; } else print 3;"), "Expected `{`, found `print`.")

    def test_while(self):
        self.assertEqual(get_output("""
                                    var i = 0;
                                    while i # 3 {
                                        print i;
                                        set i = i + 1;
                                    }
                                    """), [0, 1, 2])
        self.assertEqual(get_error("while 1 print 2;"), "Expected `{`, found `print`.")

    def test_builtin_function(self):
        self.assertEqual(get_ast("print less(2 + 3, 2 * 3);"),
                         ["program", ["print", ["less", ["+", 2, 3], ["*", 2, 3]]]])
        self.assertEqual(get_output("print less(2 + 3, 2 * 3);"), [1])
        self.assertEqual(get_output("print less(2 * 3, 2 + 3);"), [0])
        self.assertEqual(get_error("print less(2 * 3 2);"), "Expected `,`, found `2`.")

    def test_expression_statement(self):
        self.assertEqual(get_ast("2 + 3;"), ["program", ["expr", ["+", 2, 3]]])
        self.assertEqual(get_output("2 + 3;"), [])

    def test_user_function(self):
        self.assertEqual(get_output("func() { print 2; }();"), [2])
        self.assertEqual(get_output("func(a, b) { print a + b; }(2, 3);"), [5])
        self.assertEqual(get_output("""
                                    var sum = func(a, b) {
                                        print a + b;
                                    };
                                    sum(2, 3); sum(4, 5);
                                    """), [5, 9])

    def test_return(self):
        self.assertEqual(get_output("func() { print 1; return; print 2; }();"), [1])
        self.assertEqual(get_output("print func() {}();"), [0])
        self.assertEqual(get_output("print func() { return; }();"), [0])
        self.assertEqual(get_output("print func() { return 2; }();"), [2])
        self.assertEqual(get_output("print func(a, b) { return a + b; }(2, 3);"), [5])
        self.assertEqual(get_output("""
                                    var sum = func(a, b) {
                                        return a + b;
                                    };
                                    print sum(2, 3);
                                    print sum(4, 5);
                                    """), [5, 9])
        self.assertEqual(get_output("print func(b) { return func(a) { return a + b; }; }(2)(3);"), [5])

    def test_closure(self):
        self.assertEqual(get_output("""
                                    var make_adder = func(a) {
                                        return func(b) { return a + b; };
                                    };
                                    var a = 1;
                                    var add_2 = make_adder(2);
                                    print add_2(3);
                                    """), [5])

if __name__ == "__main__":
    unittest.main()
