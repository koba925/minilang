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
        self.assertEqual(get_error("prin 1;"), "`print` expected, found `prin`.")
        self.assertEqual(get_error("print a;"), "Number expected, found `a`.")
        self.assertEqual(get_error("print 1:"), "Expected `;`, found `:`.")
        self.assertEqual(get_error("print 1"), "Expected `;`, found `$EOF`.")
        self.assertEqual(get_error("print 1;a"), "Expected `$EOF`, found `a`.")

if __name__ == '__main__':
    unittest.main()
