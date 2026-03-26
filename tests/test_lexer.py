import unittest
from compiler.lexer import Lexer, TokenType, RapidPSyntaxError

class TestLexer(unittest.TestCase):
    def test_keywords(self):
        code = "DIM x AS INTEGER\nIf y = 5 tHeN Print y"
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        
        expected_types = [
            TokenType.DIM, TokenType.IDENTIFIER, TokenType.AS, TokenType.INTEGER, TokenType.NEWLINE,
            TokenType.IF, TokenType.IDENTIFIER, TokenType.EQ, TokenType.NUMBER, TokenType.THEN, TokenType.PRINT, TokenType.IDENTIFIER, TokenType.EOF
        ]
        
        self.assertEqual([t.type for t in tokens], expected_types)
        
    def test_strings_and_numbers(self):
        code = 'val = "Hello World!"\nnum = 123.45e-2'
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        
        self.assertEqual(tokens[0].type, TokenType.IDENTIFIER)
        self.assertEqual(tokens[2].type, TokenType.STRING_LIT)
        self.assertEqual(tokens[2].value, "Hello World!")
        
        self.assertEqual(tokens[6].type, TokenType.NUMBER)
        self.assertEqual(tokens[6].value, "123.45e-2")

    def test_comments(self):
        code = "DIM ' This is a comment\nREM this is also a comment"
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        
        expected_types = [
            TokenType.DIM, TokenType.NEWLINE, TokenType.EOF
        ]
        
        self.assertEqual([t.type for t in tokens], expected_types)

    def test_operators(self):
        code = "a + b - c * d / e \\ f ^ g < > <= >= = <> AND OR NOT"
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        
        op_types = [
            TokenType.IDENTIFIER, TokenType.PLUS, TokenType.IDENTIFIER, TokenType.MINUS,
            TokenType.IDENTIFIER, TokenType.STAR, TokenType.IDENTIFIER, TokenType.SLASH,
            TokenType.IDENTIFIER, TokenType.BACKSLASH, TokenType.IDENTIFIER, TokenType.CARET,
            TokenType.IDENTIFIER, TokenType.LT, TokenType.GT, TokenType.LTE, TokenType.GTE, TokenType.EQ, TokenType.NEQ,
            TokenType.AND, TokenType.OR, TokenType.NOT, TokenType.EOF
        ]
        self.assertEqual([t.type for t in tokens], op_types)

    def test_suffixes(self):
        code = "name$ value% x# ptr&"
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        
        self.assertEqual(tokens[0].value, "name$")
        self.assertEqual(tokens[1].value, "value%")
        self.assertEqual(tokens[2].value, "x#")
        self.assertEqual(tokens[3].value, "ptr&")

    def test_directives(self):
        code = "$TYPECHECK ON\n$INCLUDE <PForms.inc>"
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        
        self.assertEqual(tokens[0].type, TokenType.DIRECTIVE)
        self.assertEqual(tokens[0].value, "$TYPECHECK")
        self.assertEqual(tokens[3].type, TokenType.DIRECTIVE)
        self.assertEqual(tokens[3].value, "$INCLUDE")

if __name__ == '__main__':
    unittest.main()
