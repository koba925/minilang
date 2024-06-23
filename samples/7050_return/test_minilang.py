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

        self.assertEqual(get_error("prin 5;"), "Expected `;`, found `5`.")
        self.assertEqual(get_error("print 5:"), "Expected `;`, found `:`.")
        self.assertEqual(get_error("print 5"), "Expected `;`, found `$EOF`.")
        self.assertEqual(get_error("print 5; prin 6;"), "Expected `;`, found `6`.")

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
        self.assertEqual(get_error("{ print 1;"), "Expected `;`, found `$EOF`.")

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

    def test_builtin_function(self):
        self.assertEqual(get_ast("print less(5 + 6, 5 * 6);"),
                         ["program", ["print", ["less", ["+", 5, 6], ["*", 5, 6]]]])
        self.assertEqual(get_output("print less(5 + 6, 5 * 6);"), ["true"])
        self.assertEqual(get_output("print less(5 * 6, 5 + 6);"), ["false"])
        self.assertEqual(get_output("print less;"), ["<builtin>"])
        self.assertEqual(get_error("print less(5 * 6 7);"), "Expected `,`, found `7`.")

    def test_gcd(self):
        self.assertEqual(get_output("""
                                    var a = 36; var b = 24; var tmp = 0;
                                    while b # 0 {
                                        if less(a, b) {
                                            set tmp = a; set a = b; set b = tmp;
                                        }
                                        set a = a - b;
                                    }
                                    print a;
                                    """), [12])

    def test_expression_statement(self):
        self.assertEqual(get_ast("5 + 6;"), ["program", ["expr", ["+", 5, 6]]])
        self.assertEqual(get_output("5 + 6;"), [])

    def test_user_function_type(self):
        self.assertEqual(get_ast("func() {};"), \
                         ["program", ["expr", ["func", [], ["block"]]]])
        self.assertEqual(get_output("print func() {};"), ["<func>"])

        self.assertEqual(get_ast("func(a, b) { a + b; };"), \
                         ["program", ["expr", ["func", ["a", "b"], ["block", ["expr", ["+", "a", "b"]]]]]])
        self.assertEqual(get_output("print func(a, b) { a + b; };"), ["<func>"])

    def test_user_function_call(self):
        self.assertEqual(get_output("print func() {}();"), [0])
        self.assertEqual(get_output("func() { print 5; }();"), [5])
        self.assertEqual(get_output("func(a, b) { print a + b; }(5, 6);"), [11])
        self.assertEqual(get_output("""
                                    var sum = func(a, b) {
                                        print a + b;
                                    };
                                    sum(5, 6); sum(7, 8);
                                    """), [11, 15])

    def test_fib2(self):
        self.assertEqual(get_output("""
                                    var fib = func(n) {
                                        var i = 0; var a = 1; var b = 0; var tmp = 0;
                                        while i # n {
                                            print a;
                                            set tmp = a; set a = a + b; set b = tmp;
                                            set i = i + 1;
                                        }
                                    };
                                    fib(3); fib(5);
                                    """), [1, 1, 2, 1, 1, 2, 3, 5])

    def test_return(self):
        self.assertEqual(get_output("print func() { return; }();"), [0])
        self.assertEqual(get_output("print func() { return 5; }();"), [5])
        self.assertEqual(get_output("print func(a, b) { return a + b; }(5, 6);"), [11])
        self.assertEqual(get_output("func() { print 5; return; print 6; }();"), [5])
        self.assertEqual(get_output("""
                                    var sum = func(a, b) {
                                        return a + b;
                                    };
                                    print sum(5, 6);
                                    print sum(7, 8);
                                    """), [11, 15])
        self.assertEqual(get_output("""
                                    var nums_to_n = func(n) {
                                        var k = 1;
                                        while true {
                                            print k;
                                            if k = n { return; }
                                            set k = k + 1;
                                        }
                                    };
                                    nums_to_n(5);
                                    """), [1, 2, 3, 4, 5])
        self.assertEqual(get_output("print func() { return less; }();"), ["<builtin>"])
        self.assertEqual(get_output("print func() { return less; }()(5, 6);"), ["true"])
        self.assertEqual(get_output("print func() { return func(a) { return a + 5; }; }()(6);"), [11])

    def test_gcd2(self):
        self.assertEqual(get_output("""
                                    var gcd = func(a, b) {
                                        var tmp = 0;
                                        while b # 0 {
                                            if less(a, b) {
                                                set tmp = a; set a = b; set b = tmp;
                                            }
                                            set a = a - b;
                                        }
                                        return a;
                                    };
                                    print gcd(36, 12);
                                    """), [12])

    def test_fib3(self):
        self.assertEqual(get_output("""
                                    var fib = func(n) {
                                        if n = 1 { return 1; }
                                        if n = 2 { return 1; }
                                        return fib(n - 1) + fib(n - 2);
                                    };
                                    print fib(6);
                                    """), [8])

    def test_even_odd(self):
        self.assertEqual(get_output("""
                                    var is_even = func(a) { if a = 0 { return true; } else { return is_odd(a - 1); } };
                                    var is_odd = func(a) { if a = 0 { return false; } else { return is_even(a - 1); } };
                                    print is_even(5);
                                    print is_odd(5);
                                    print is_even(6);
                                    print is_odd(6);
                                    """), ["false", "true", "true", "false"])

if __name__ == "__main__":
    unittest.main()
