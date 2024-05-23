import unittest

class TestRun(unittest.TestCase):
    def test_print(self):
        self.assertEqual(interpret("print 12;"), 12)


if __name__ == '__main__':
    unittest.main()
