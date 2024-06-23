import unittest

from minilang import Parser, Evaluator

def get_ast(source): return Parser(source).parse_program()

def get_output(source):
    evaluator = Evaluator()
    evaluator.eval_program(Parser(source).parse_program())
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
        self.assertEqual(get_error("print 2 ^ func() {};"), "Operands must be integers.")
        self.assertEqual(get_error("print func() {} ^ 2;"), "Operands must be integers.")

    def test_factor(self):
        self.assertEqual(get_output("print 2 * 3;"), [6])
        self.assertEqual(get_ast("print 2 * 3 * 4;"), ["program", ["print", ["*", ["*", 2, 3], 4]]])
        self.assertEqual(get_output("print 2 * 3 * 4;"), [24])
        self.assertEqual(get_output("print 24 / 2;"), [12])
        self.assertEqual(get_ast("print 24 / 4 / 2;"), ["program", ["print", ["/", ["/", 24, 4], 2]]])
        self.assertEqual(get_output("print 24 / 4 / 2;"), [3])
        self.assertEqual(get_output("print 2 ^ 3 * 2;"), [16])
        self.assertEqual(get_output("print 2 * 2 ^ 3;"), [16])
        self.assertEqual(get_error("print 2 / 0;"), "Division by zero.")
        self.assertEqual(get_error("print 2 * func() {};"), "Operands must be integers.")
        self.assertEqual(get_error("print func() {} / 2;"), "Operands must be integers.")

    def test_add_sum(self):
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
        self.assertEqual(get_error("print 2 + func() {};"), "Operands must be integers.")
        self.assertEqual(get_error("print func() {} - 2;"), "Operands must be integers.")

    def test_equality(self):
        self.assertEqual(get_output("print 2 = 2;"), ["true"])
        self.assertEqual(get_output("print 2 = 3;"), ["false"])
        self.assertEqual(get_output("print 2 # 2;"), ["false"])
        self.assertEqual(get_output("print 2 # 3;"), ["true"])
        self.assertEqual(get_ast("print 1 = 2 = 2;"), ["program", ["print", ["=", ["=", 1, 2], 2]]])
        self.assertEqual(get_output("print 1 = 2 = 2;"), ["false"])
        self.assertEqual(get_output("print 1 + 2 = 6 - 3;"), ["true"])
        self.assertEqual(get_output("print func() {} = 0;"), ["false"])
        self.assertEqual(get_output("print func() {} # 0;"), ["true"])
        self.assertEqual(get_output("print func(a) { return a; } = func(a) { return a; };"), ["true"])
        self.assertEqual(get_output("print func(a) { return a; } = func(b) { return b; };"), ["false"])
        self.assertEqual(get_output("print func(a) { return a; } # func(a) { return a; };"), ["false"])
        self.assertEqual(get_output("print func(a) { return a; } # func(b) { return b; };"), ["true"])

    def test_grouping(self):
        self.assertEqual(get_ast("print (2 + 3) * 4;"), ["program", ["print", ["*", ["+", 2, 3], 4]]])
        self.assertEqual(get_output("print (2 + 3) * 4;"), [20])
        self.assertEqual(get_ast("print 2 * (3 + 4);"), ["program", ["print", ["*", 2, ["+", 3, 4]]]])
        self.assertEqual(get_output("print 2 * (3 + 4);"), [14])

    def test_var(self):
        self.assertEqual(get_output("var a = 1 + 2; print a; set a = a + 3; print a;"), [3, 6])
        self.assertEqual(get_output("var a = 1; var b = 2; print a; print b;"), [1, 2])
        self.assertEqual(get_output("var a; print a;"), ["null"])
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
        self.assertEqual(get_ast("if true { print 2; }"), ["program", ["if", True, ["block", ["print", 2]], ["block"]]])
        self.assertEqual(get_output("if true { print 2; }"), [2])
        self.assertEqual(get_output("if false { print 2; }"), [])
        self.assertEqual(get_output("if 1 + 2 = 4 - 1 { print 1; }"), [1])
        self.assertEqual(get_output("if 1 + 2 # 4 - 1 { print 1; }"), [])
        self.assertEqual(get_output("if true { if true { print 2; } }"), [2])
        self.assertEqual(get_output("if true { if false { print 2; } }"), [])
        self.assertEqual(get_error("if true print 2;"), "Expected `{`, found `print`.")

    def test_else(self):
        self.assertEqual(get_ast("if true { print 2; } else { print 3; }"),
                         ["program", ["if", True, ["block", ["print", 2]], ["block", ["print", 3]]]])
        self.assertEqual(get_output("if true { print 2; } else { print 3; }"), [2])
        self.assertEqual(get_output("if false { print 2; } else { print 3; }"), [3])
        self.assertEqual(get_output("if 1 + 2 = 4 - 1 { print 1; } else { print 2; }"), [1])
        self.assertEqual(get_output("if 1 + 2 # 4 - 1 { print 1; } else { print 2; }"), [2])
        self.assertEqual(get_error("if true { print 2; } else print 3;"), "Expected `{`, found `print`.")

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
                                    print a;
                                    """), [1, 1, 2, 3, 5, 8])

    def test_builtin_function(self):
        self.assertEqual(get_ast("print less(2 + 3, 2 * 3);"),
                         ["program", ["print", ["less", ["+", 2, 3], ["*", 2, 3]]]])
        self.assertEqual(get_output("print less(2 + 3, 2 * 3);"), ["true"])
        self.assertEqual(get_output("print less(2 * 3, 2 + 3);"), ["false"])
        self.assertEqual(get_output("print less;"), ["<builtin>"])
        self.assertEqual(get_error("print less(2 * 3 2);"), "Expected `,`, found `2`.")
        self.assertEqual(get_error("less(1);"), "Parameter's count doesn't match.")
        self.assertEqual(get_error("less(1, 2, 3);"), "Parameter's count doesn't match.")

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
        self.assertEqual(get_ast("2 + 3;"), ["program", ["expr", ["+", 2, 3]]])
        self.assertEqual(get_output("2 + 3;"), [])

    def test_user_function(self):
        self.assertEqual(get_output("print func() {};"), ["<func>"])
        self.assertEqual(get_output("print func() {}();"), ["null"])
        self.assertEqual(get_output("func() { print 2; }();"), [2])
        self.assertEqual(get_output("func(a, b) { print a + b; }(2, 3);"), [5])
        self.assertEqual(get_output("""
                                    var sum = func(a, b) {
                                        print a + b;
                                    };
                                    sum(2, 3); sum(4, 5);
                                    print sum;
                                    """), [5, 9, "<func>"])
        self.assertEqual(get_error("func() {}(1);"), "Parameter's count doesn't match.")
        self.assertEqual(get_error("func(a, b) {}(1);"), "Parameter's count doesn't match.")

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
                                    fib(3); fib(6);
                                    """), [1, 1, 2, 1, 1, 2, 3, 5, 8])

    def test_return(self):
        self.assertEqual(get_output("print func() { return; }();"), ["null"])
        self.assertEqual(get_output("print func() { return 2; }();"), [2])
        self.assertEqual(get_output("print func(a, b) { return a + b; }(2, 3);"), [5])
        self.assertEqual(get_output("func() { print 1; return; print 2; }();"), [1])
        self.assertEqual(get_output("""
                                    var sum = func(a, b) {
                                        return a + b;
                                    };
                                    print sum(2, 3);
                                    print sum(4, 5);
                                    """), [5, 9])
        self.assertEqual(get_output("print func(b) { return func(a) { return a + b; }; }(2)(3);"), [5])
        self.assertEqual(get_error("return;"), "Return from top level.")
        self.assertEqual(get_error("if 1 = 1 { return; }"), "Return from top level.")

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
                                    print is_even(3);
                                    print is_odd(3);
                                    print is_even(4);
                                    print is_odd(4);
                                    """), ["false", "true", "true", "false"])

    def test_closure(self):
        self.assertEqual(get_output("""
                                    var make_adder = func(a) {
                                        return func(b) { return a + b; };
                                    };
                                    var a = 1;
                                    var add_2 = make_adder(2);
                                    print add_2(3);
                                    """), [5])

    def test_comments(self):
        self.assertEqual(get_output("! This is a comment"), [])
        self.assertEqual(get_output("""
                                    !!! Test of comments !!!
                                    print 1; ! This is a comment!
                                    ! print 2; This will not be excecuted.
                                    """), [1])

    def test_unary_minus(self):
        self.assertEqual(get_output("print -1;"), [-1])
        self.assertEqual(get_output("print --1;"), [1])
        self.assertEqual(get_output("print 1--1;"), [2])
        self.assertEqual(get_output("var a = 1; print -a;"), [-1])

    def test_and_or(self):
        self.assertEqual(get_output("print 1 = 1 & 2 = 2;"), ["true"])
        self.assertEqual(get_output("print 1 = 1 & 2 # 2;"), ["false"])
        self.assertEqual(get_output("print 1 # 1 & 1 / 0;"), ["false"])
        self.assertEqual(get_output("print 1 # 1 | 2 = 2;"), ["true"])
        self.assertEqual(get_output("print 1 # 1 | 2 # 2;"), ["false"])
        self.assertEqual(get_output("print 1 = 1 | 1 / 0;"), ["true"])

        self.assertEqual(get_output("print true & false;"), ["false"])
        self.assertEqual(get_output("print true & 2;"), [2])
        self.assertEqual(get_output("print 2 | 1;"), [2])
        self.assertEqual(get_output("print false | 2;"), [2])

        self.assertEqual(get_ast("print true & true & false;"), ["program", ["print", ["&", ["&", True, True], False]]])
        self.assertEqual(get_output("print true & true & false;"), ["false"])
        self.assertEqual(get_output("print true & false & 1 / 0;"), ["false"])

        self.assertEqual(get_ast("print false | false | true;"), ["program", ["print", ["|", ["|", False, False], True]]])
        self.assertEqual(get_output("print false | false | true;"), ["true"])
        self.assertEqual(get_output("print false | true | 1 / 0;"), ["true"])

        self.assertEqual(get_ast("print true | true & false;"), ["program", ["print", ["|", True, ["&", True, False]]]])
        self.assertEqual(get_ast("print true & true | false;"), ["program", ["print", ["|", ["&", True, True], False]]])
        self.assertEqual(get_output("print true | true & false;"), ["true"])
        self.assertEqual(get_output("print true & true | false;"), ["true"])

    def test_break(self):
        self.assertEqual(get_output("""
                                    var n = 0;
                                    while true {
                                        if n = 3 { break; }
                                        print n;
                                        set n = n + 1;
                                    }
                                    print 10;
                                    """), [0, 1, 2, 10])
        self.assertEqual(get_error("break;"), "Break at top level.")

    def test_continue(self):
        self.assertEqual(get_output("""
                                    var n = 0;
                                    while n # 4 {
                                        set n = n + 1;
                                        if n = 2 { continue; }
                                        print n;
                                    }
                                    print 10;
                                    """), [1, 3, 4, 10])
        self.assertEqual(get_error("continue;"), "Continue at top level.")

    def test_def(self):
        self.assertEqual(get_output("""
                                    def sum(a, b) {
                                        return a + b;
                                    }
                                    print sum(2, 3);
                                    print sum(4, 5);
                                    """), [5, 9])

    def test_elif(self):
        self.assertEqual(get_output("if true { print 0; } elif true {print 1; } elif true { print 2; } else { print 3; }"), [0])
        self.assertEqual(get_output("if false { print 0; } elif true {print 1; } elif true { print 2; } else { print 3; }"), [1])
        self.assertEqual(get_output("if false { print 0; } elif false {print 1; } elif true { print 2; } else { print 3; }"), [2])
        self.assertEqual(get_output("if false { print 0; } elif false {print 1; } elif false { print 2; } else { print 3; }"), [3])

    def test_for(self):
        self.assertEqual(get_output("for i = 0; i # 5; i = i + 1 { print i; }"), [0, 1, 2, 3, 4])
        self.assertEqual(get_output("for i = 0; i # 5; i = i + 1 { if i = 3 { break; } print i; }"), [0, 1, 2])
        self.assertEqual(get_output("for i = 0; i # 5; i = i + 1 { if i = 2 { continue; } print i; }"), [0, 1, 3, 4])

    def test_comparison(self):
        self.assertEqual(get_output("print 2 + 3 < 2 * 3;"), ["true"])
        self.assertEqual(get_output("print 2 * 3 < 2 * 3;"), ["false"])
        self.assertEqual(get_output("print 2 * 3 < 2 + 3;"), ["false"])
        self.assertEqual(get_output("print 2 + 3 <= 2 * 3;"), ["true"])
        self.assertEqual(get_output("print 2 * 3 <= 2 * 3;"), ["true"])
        self.assertEqual(get_output("print 2 * 3 <= 2 + 3;"), ["false"])
        self.assertEqual(get_output("print 2 * 3 > 2 + 3;"), ["true"])
        self.assertEqual(get_output("print 2 * 3 > 2 * 3;"), ["false"])
        self.assertEqual(get_output("print 2 + 3 > 2 * 3;"), ["false"])
        self.assertEqual(get_output("print 2 * 3 >= 2 + 3;"), ["true"])
        self.assertEqual(get_output("print 2 * 3 >= 2 * 3;"), ["true"])
        self.assertEqual(get_output("print 2 + 3 >= 2 * 3;"), ["false"])

    def test_while_then(self):
        self.assertEqual(get_output("while false {} then { print 2; }"), [2])
        self.assertEqual(get_output("while true { break; } then { print 2; }"), [])

    def test_null(self):
        self.assertEqual(get_output("print null;"), ["null"])
        self.assertEqual(get_output("var a = null; print a;"), ["null"])
        self.assertEqual(get_error("print -null;"), "Operand must be integer.")
        self.assertEqual(get_error("print null + 1;"), "Operands must be integers.")
        self.assertEqual(get_error("print 1 - null;"), "Operands must be integers.")

    def test_ternary(self):
        self.assertEqual(get_output("print 1 = 1 ? 1 + 2 : 1 / 0;"), [3])
        self.assertEqual(get_output("print 1 # 1 ? 1 / 0  : 1 + 2;"), [3])

        self.assertEqual(get_output("print true ? 2 : true ? 3 : 4;"), [2])

        self.assertEqual(get_output("print true ? true ? 2 : 1 / 0 : 1 / 0 ? 0 : 0;"), [2])
        self.assertEqual(get_output("print true ? 0 ? 1 / 0 : 2 : 1 / 0 ? 0 : 0;"), [2])
        self.assertEqual(get_output("print 0 ? 1 / 0 ? 0 : 0 : true ? 2 : 1 / 0;"), [2])
        self.assertEqual(get_output("print 0 ? 1 / 0 ? 0 : 0 : 0 ? 1 / 0 : 2;"), [2])

        self.assertEqual(get_error("print 1 # 1 ? 1 + 2;"), "Expected `:`, found `;`.")

if __name__ == "__main__":
    unittest.main()
