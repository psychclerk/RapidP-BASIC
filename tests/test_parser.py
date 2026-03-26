import unittest
from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.ast_nodes import *

class TestParser(unittest.TestCase):
    def parse(self, code):
        tokens = Lexer(code).tokenize()
        return Parser(tokens).parse()

    def test_dim_statement(self):
        ast = self.parse("DIM x, y AS INTEGER\n")
        self.assertEqual(len(ast.statements), 1)
        stmt = ast.statements[0]
        self.assertTrue(isinstance(stmt, DimStatementNode))
        self.assertEqual(stmt.variables, [('x', None), ('y', None)])
        self.assertEqual(stmt.var_type, 'INTEGER')

    def test_assignment(self):
        ast = self.parse("x = 10 + 5\n")
        stmt = ast.statements[0]
        self.assertTrue(isinstance(stmt, AssignmentNode))
        self.assertEqual(stmt.target.name, 'x')
        self.assertTrue(isinstance(stmt.value, BinaryOpNode))
        self.assertEqual(stmt.value.op, '+')

    def test_if_statement(self):
        code = '''
        IF x > 5 THEN
            PRINT "Big"
        ELSEIF x = 5 THEN
            PRINT "Equal"
        ELSE
            PRINT "Small"
        END IF
        '''
        ast = self.parse(code)
        stmt = ast.statements[0]
        self.assertTrue(isinstance(stmt, IfStatementNode))
        self.assertEqual(len(stmt.then_branch), 1)
        self.assertEqual(len(stmt.elseif_branches), 1)
        self.assertEqual(len(stmt.else_branch), 1)

    def test_for_loop(self):
        code = "FOR i = 1 TO 10 STEP 2\nPRINT i\nNEXT i\n"
        ast = self.parse(code)
        stmt = ast.statements[0]
        self.assertTrue(isinstance(stmt, ForStatementNode))
        self.assertEqual(stmt.variable, 'i')
        self.assertTrue(isinstance(stmt.start, LiteralNode))
        self.assertEqual(stmt.start.value, 1)

    def test_sub_definition(self):
        code = '''
        SUB MyPrint(msg AS STRING)
            PRINT msg
        END SUB
        '''
        ast = self.parse(code)
        stmt = ast.statements[0]
        self.assertTrue(isinstance(stmt, SubroutineDefNode))
        self.assertEqual(stmt.name, 'MyPrint')
        self.assertEqual(stmt.params[0], ('msg', 'STRING'))

    def test_select_case(self):
        code = '''
        SELECT CASE x
            CASE 1, 2
                PRINT "1 or 2"
            CASE ELSE
                PRINT "Other"
        END SELECT
        '''
        ast = self.parse(code)
        stmt = ast.statements[0]
        self.assertTrue(isinstance(stmt, SelectCaseStatementNode))
        self.assertEqual(stmt.expression.name, 'x')
        self.assertEqual(len(stmt.cases), 1)
        self.assertEqual(len(stmt.case_else), 1)
        
    def test_member_access_and_method(self):
        code = "form.caption = \"Title\"\nform.ShowModal()"
        ast = self.parse(code)
        self.assertTrue(isinstance(ast.statements[0], AssignmentNode))
        self.assertTrue(isinstance(ast.statements[0].target, MemberAccessNode))
        
        self.assertTrue(isinstance(ast.statements[1], MethodCallStatementNode))
        self.assertEqual(ast.statements[1].method_call.method, "ShowModal")

if __name__ == '__main__':
    unittest.main()
