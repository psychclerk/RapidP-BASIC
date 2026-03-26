"""Test suite for compiler: $APPTYPE codegen, new component types in registry."""
import unittest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.codegen import CodeGenerator, COMPONENT_REGISTRY


class TestComponentRegistry(unittest.TestCase):
    """Verify all expected component types are in the registry."""

    def test_core_components(self):
        expected = [
            'PFORM', 'PBUTTON', 'PLABEL', 'PEDIT', 'PPANEL', 'PCANVAS',
            'PTIMER', 'PMAINMENU', 'PMENUITEM', 'PCHECKBOX', 'PRADIOBUTTON',
            'PCOMBOBOX', 'PLISTBOX', 'PGROUPBOX', 'PRICHEDIT', 'PSTRINGGRID',
            'PPROGRESSBAR', 'PTABCONTROL', 'PSCROLLBAR', 'PCODEEDITOR',
        ]
        for comp in expected:
            self.assertIn(comp, COMPONENT_REGISTRY, f"{comp} missing from registry")

    def test_file_dialog_components(self):
        for comp in ['POPENDIALOG', 'PSAVEDIALOG', 'PFILEDIALOG', 'PCOLORDIALOG', 'PFONTDIALOG']:
            self.assertIn(comp, COMPONENT_REGISTRY)

    def test_data_components(self):
        for comp in ['PMYSQL', 'PSQLITE', 'PFILESTREAM', 'PSTRINGLIST', 'PMEMORYSTREAM', 'PINI']:
            self.assertIn(comp, COMPONENT_REGISTRY)

    def test_networking_components(self):
        for comp in ['PSOCKET', 'PSERVERSOCKET', 'PHTTP']:
            self.assertIn(comp, COMPONENT_REGISTRY)

    def test_python_components(self):
        for comp in ['PNUMPY', 'PMATPLOTLIB', 'PPANDAS']:
            self.assertIn(comp, COMPONENT_REGISTRY)

    def test_qimage_properties(self):
        props = COMPONENT_REGISTRY['PIMAGE']['props']
        self.assertIn('image', props)
        self.assertIn('bmpwidth', props)
        self.assertIn('bmpheight', props)

    def test_qsocket_events(self):
        events = COMPONENT_REGISTRY['PSOCKET']['events']
        self.assertIn('onconnect', events)
        self.assertIn('onerror', events)

    def test_qserversocket_events(self):
        events = COMPONENT_REGISTRY['PSERVERSOCKET']['events']
        self.assertIn('onclientconnect', events)
        self.assertIn('ondatareceived', events)


class TestAppTypeCodegen(unittest.TestCase):
    def _compile(self, src):
        lexer = Lexer(src)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        codegen = CodeGenerator()
        return codegen.generate(ast)

    def test_default_includes_gui(self):
        code = self._compile('DIM x AS INTEGER')
        self.assertIn('from rp_runtime.gui import *', code)

    def test_console_apptype_no_gui(self):
        code = self._compile('$APPTYPE CONSOLE\nDIM x AS INTEGER')
        self.assertNotIn('from rp_runtime.gui import *', code)
        self.assertIn('from rp_runtime.builtins import *', code)

    def test_gui_apptype_includes_gui(self):
        code = self._compile('$APPTYPE GUI\nDIM x AS INTEGER')
        self.assertIn('from rp_runtime.gui import *', code)

    def test_pycomponents_import(self):
        code = self._compile('DIM x AS INTEGER')
        self.assertIn('from rp_runtime.pycomponents import *', code)

    def test_network_import(self):
        code = self._compile('DIM x AS INTEGER')
        self.assertIn('from rp_runtime.network import *', code)


class TestNewComponentCodegen(unittest.TestCase):
    def _compile(self, src):
        lexer = Lexer(src)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        codegen = CodeGenerator()
        return codegen.generate(ast)

    def test_dim_qnumpy(self):
        code = self._compile('DIM n AS PNumPy')
        self.assertIn('PNumPy()', code)

    def test_dim_qmatplotlib(self):
        code = self._compile('DIM m AS PMatPlotLib')
        self.assertIn('PMatPlotLib()', code)

    def test_dim_qpandas(self):
        code = self._compile('DIM p AS PPandas')
        self.assertIn('PPandas()', code)

    def test_dim_qserversocket(self):
        code = self._compile('DIM srv AS PServerSocket')
        self.assertIn('PServerSocket()', code)

    def test_dim_qhttp(self):
        code = self._compile('DIM h AS PHTTP')
        self.assertIn('PHTTP()', code)


if __name__ == '__main__':
    unittest.main()
