import unittest
from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.codegen import CodeGenerator

class TestCodegen(unittest.TestCase):
    def generate(self, code):
        tokens = Lexer(code).tokenize()
        ast = Parser(tokens).parse()
        return CodeGenerator().generate(ast)

    def test_dim(self):
        rq_code = "DIM x AS INTEGER\nDIM y AS STRING"
        py_code = self.generate(rq_code)
        self.assertIn("x = 0", py_code)
        self.assertIn("y = \"\"", py_code)
        
    def test_print(self):
        rq_code = "PRINT \"Hello\", x"
        py_code = self.generate(rq_code)
        self.assertIn("rp_print(\"Hello\", x)", py_code)
        
    def test_if_statement(self):
        rq_code = "IF x = 5 THEN\ny = 10\nEND IF"
        py_code = self.generate(rq_code)
        self.assertIn("if (x == 5):", py_code)
        self.assertIn("    y = 10", py_code)
        
    def test_for_loop(self):
        rq_code = "FOR i = 1 TO 10 STEP 1\nPRINT i\nNEXT"
        py_code = self.generate(rq_code)
        self.assertIn("i = 1", py_code)
        self.assertIn("while i <= 10:", py_code)
        self.assertIn("    rp_print(i)", py_code)
        self.assertIn("    i += 1", py_code)

    def test_sub(self):
         rq_code = "SUB MySub(val AS INTEGER)\nPRINT val\nEND SUB\nCALL MySub(10)"
         py_code = self.generate(rq_code)
         self.assertIn("def mysub(val):", py_code)
         self.assertIn("    rp_print(val)", py_code)
         self.assertIn("mysub(10)", py_code)

    def test_function(self):
         rq_code = "FUNCTION MyFunc() AS INTEGER\nMyFunc = 100\nEND FUNCTION"
         py_code = self.generate(rq_code)
         self.assertIn("def myfunc():", py_code)
         self.assertIn("    myfunc = None", py_code)
         self.assertIn("    myfunc = 100", py_code)
         self.assertIn("    return myfunc", py_code)

    def test_import(self):
         rq_code = "IMPORT \"numpy\" AS np"
         py_code = self.generate(rq_code)
         self.assertIn("import numpy as np", py_code)

if __name__ == '__main__':
    unittest.main()
