import unittest
from rp_runtime.builtins import *

class TestBuiltins(unittest.TestCase):
    def test_string_functions(self):
        self.assertEqual(chr(65), 'A')
        self.assertEqual(asc('A'), 65)
        self.assertEqual(left('Hello', 2), 'He')
        self.assertEqual(right('Hello', 2), 'lo')
        
        # 1-indexed RapidP behavior
        self.assertEqual(mid('Hello', 2, 3), 'ell')
        self.assertEqual(mid('Hello', 2), 'ello')
        
        self.assertEqual(len('Hello'), 5)
        self.assertEqual(instr('Hello', 'l'), 3)
        self.assertEqual(instr(4, 'Hello', 'l'), 4)
        
        self.assertEqual(ucase('hello'), 'HELLO')
        self.assertEqual(lcase('HELLO'), 'hello')

    def test_type_conversion(self):
        self.assertEqual(val("123"), 123)
        self.assertEqual(val("123.45"), 123.45)
        self.assertEqual(val("abc"), 0)
        self.assertEqual(str_func(123), "123")
        
    def test_math(self):
         self.assertEqual(abs(-10), 10)
         self.assertEqual(sqr(16), 4.0)

if __name__ == '__main__':
    unittest.main()
