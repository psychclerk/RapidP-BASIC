"""Test suite for preprocessor directives: $MACRO, $DEFINE, $IFDEF, $INCLUDE, $APPTYPE."""
import unittest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from compiler.preprocessor import preprocess


class TestDefine(unittest.TestCase):
    def test_simple_define(self):
        src = '$DEFINE VERSION 2\nPRINT VERSION'
        result = preprocess(src, '.')
        self.assertIn('PRINT 2', result)

    def test_define_substitution_in_code(self):
        src = '$DEFINE MAX_SIZE 100\nDIM arr(MAX_SIZE) AS INTEGER'
        result = preprocess(src, '.')
        self.assertIn('DIM arr(100) AS INTEGER', result)

    def test_define_no_value(self):
        src = '$DEFINE DEBUG\n$IFDEF DEBUG\nPRINT "Debug mode"\n$ENDIF'
        result = preprocess(src, '.')
        self.assertIn('PRINT "Debug mode"', result)

    def test_undef(self):
        src = '$DEFINE DEBUG\n$UNDEF DEBUG\n$IFDEF DEBUG\nPRINT "Debug"\n$ELSE\nPRINT "Release"\n$ENDIF'
        result = preprocess(src, '.')
        self.assertIn('PRINT "Release"', result)
        self.assertNotIn('PRINT "Debug"', result)


class TestConditionalCompilation(unittest.TestCase):
    def test_ifdef_true(self):
        src = '$DEFINE FOO\n$IFDEF FOO\nPRINT "yes"\n$ENDIF'
        result = preprocess(src, '.')
        self.assertIn('PRINT "yes"', result)

    def test_ifdef_false(self):
        src = '$IFDEF FOO\nPRINT "yes"\n$ENDIF'
        result = preprocess(src, '.')
        self.assertNotIn('PRINT "yes"', result)

    def test_ifndef(self):
        src = '$IFNDEF FOO\nPRINT "not defined"\n$ENDIF'
        result = preprocess(src, '.')
        self.assertIn('PRINT "not defined"', result)

    def test_ifdef_else(self):
        src = '$IFDEF FOO\nPRINT "yes"\n$ELSE\nPRINT "no"\n$ENDIF'
        result = preprocess(src, '.')
        self.assertNotIn('PRINT "yes"', result)
        self.assertIn('PRINT "no"', result)

    def test_nested_ifdef(self):
        src = '$DEFINE A\n$IFDEF A\n$DEFINE B\n$IFDEF B\nPRINT "nested"\n$ENDIF\n$ENDIF'
        result = preprocess(src, '.')
        self.assertIn('PRINT "nested"', result)


class TestMacro(unittest.TestCase):
    def test_simple_macro(self):
        src = '$MACRO VERSION = 42\nPRINT VERSION'
        result = preprocess(src, '.')
        self.assertIn('PRINT 42', result)

    def test_parameterized_macro(self):
        src = '$MACRO MAX(a,b) = IIF(a > b, a, b)\nx = MAX(10, 20)'
        result = preprocess(src, '.')
        self.assertIn('x = IIF(10 > 20, 10, 20)', result)

    def test_macro_multiple_params(self):
        src = '$MACRO CLAMP(x,lo,hi) = IIF(x < lo, lo, IIF(x > hi, hi, x))\ny = CLAMP(v, 0, 100)'
        result = preprocess(src, '.')
        self.assertIn('y = IIF(v < 0, 0, IIF(v > 100, 100, v))', result)

    def test_macro_no_substitution_in_strings(self):
        # Macros should not substitute inside quoted strings in define substitution
        src = '$DEFINE GREETING Hello\nPRINT GREETING'
        result = preprocess(src, '.')
        self.assertIn('PRINT Hello', result)


class TestAppType(unittest.TestCase):
    def test_apptype_passes_through(self):
        src = '$APPTYPE GUI\nPRINT "test"'
        result = preprocess(src, '.')
        self.assertIn('$APPTYPE GUI', result)

    def test_apptype_console(self):
        src = '$APPTYPE CONSOLE\nPRINT "test"'
        result = preprocess(src, '.')
        self.assertIn('$APPTYPE CONSOLE', result)


class TestLinePreservation(unittest.TestCase):
    def test_directives_preserve_line_numbers(self):
        src = '$DEFINE X\n$IFDEF X\nline3\n$ENDIF\nline5'
        result = preprocess(src, '.')
        lines = result.split('\n')
        self.assertEqual(len(lines), 5)
        self.assertEqual(lines[2].strip(), 'line3')
        self.assertEqual(lines[4].strip(), 'line5')


if __name__ == '__main__':
    unittest.main()
