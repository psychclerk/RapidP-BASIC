"""Test suite for Python-specific components: PNumPy, PMatPlotLib, PPandas."""
import unittest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import numpy
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

try:
    import matplotlib
    HAS_MPL = True
except ImportError:
    HAS_MPL = False

try:
    import pandas
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

from rp_runtime.pycomponents import PNumPy, PMatPlotLib, PPandas


class TestPNumPyConstruction(unittest.TestCase):
    def test_constructor_no_crash(self):
        n = PNumPy()
        self.assertIsNone(n._arr)
        self.assertEqual(n.size, 0)


@unittest.skipUnless(HAS_NUMPY, "numpy not installed")
class TestPNumPy(unittest.TestCase):
    def test_arange(self):
        n = PNumPy()
        n.arange(0, 10)
        self.assertEqual(n.size, 10)

    def test_zeros(self):
        n = PNumPy()
        n.zeros(3, 4)
        self.assertEqual(n.shape, [3, 4])
        self.assertEqual(n.size, 12)

    def test_ones(self):
        n = PNumPy()
        n.ones(5)
        self.assertEqual(n.size, 5)
        self.assertAlmostEqual(n.sum(), 5.0)

    def test_linspace(self):
        n = PNumPy()
        n.linspace(0, 1, 11)
        self.assertEqual(n.size, 11)
        self.assertAlmostEqual(n.min(), 0.0)
        self.assertAlmostEqual(n.max(), 1.0)

    def test_sum_mean_std(self):
        n = PNumPy()
        n.data = [1, 2, 3, 4, 5]
        self.assertAlmostEqual(n.sum(), 15.0)
        self.assertAlmostEqual(n.mean(), 3.0)
        self.assertGreater(n.std(), 0)

    def test_reshape(self):
        n = PNumPy()
        n.arange(0, 12)
        n.reshape(3, 4)
        self.assertEqual(n.shape, [3, 4])

    def test_dot(self):
        a = PNumPy()
        a.data = [1, 2, 3]
        b = PNumPy()
        b.data = [4, 5, 6]
        result = a.dot(b)
        self.assertAlmostEqual(result.sum(), 32.0)  # 1*4 + 2*5 + 3*6

    def test_transpose(self):
        n = PNumPy()
        n.data = [[1, 2], [3, 4]]
        n.transpose()
        self.assertEqual(n.shape, [2, 2])

    def test_tolist(self):
        n = PNumPy()
        n.data = [1, 2, 3]
        self.assertEqual(n.tolist(), [1, 2, 3])

    def test_sort(self):
        n = PNumPy()
        n.data = [3, 1, 2]
        n.sort()
        self.assertEqual(n.tolist(), [1, 2, 3])

    def test_dtype(self):
        n = PNumPy()
        n.data = [1.0, 2.0]
        self.assertIn('float', n.dtype)

    def test_save_load(self):
        import tempfile
        n = PNumPy()
        n.data = [1, 2, 3]
        with tempfile.NamedTemporaryFile(suffix='.npy', delete=False) as f:
            path = f.name
        try:
            n.savetofile(path)
            n2 = PNumPy()
            n2.loadfromfile(path)
            self.assertEqual(n2.tolist(), [1, 2, 3])
        finally:
            os.unlink(path)


class TestPMatPlotLibConstruction(unittest.TestCase):
    def test_constructor_no_crash(self):
        m = PMatPlotLib()
        self.assertEqual(m.title, "")


@unittest.skipUnless(HAS_MPL and HAS_NUMPY, "matplotlib/numpy not installed")
class TestPMatPlotLib(unittest.TestCase):
    def test_plot_and_save(self):
        import tempfile
        m = PMatPlotLib()
        m.title = "Test"
        m.plot([1, 2, 3], [4, 5, 6])
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            path = f.name
        try:
            m.savetofile(path)
            self.assertTrue(os.path.exists(path))
            self.assertGreater(os.path.getsize(path), 0)
        finally:
            os.unlink(path)

    def test_scatter(self):
        m = PMatPlotLib()
        m.scatter([1, 2, 3], [4, 5, 6])
        # Just verify no crash
        self.assertIsNotNone(m._ax)

    def test_bar(self):
        m = PMatPlotLib()
        m.bar([1, 2, 3], [4, 5, 6])
        self.assertIsNotNone(m._ax)

    def test_hist(self):
        m = PMatPlotLib()
        m.hist([1, 2, 2, 3, 3, 3])
        self.assertIsNotNone(m._ax)

    def test_saveto_buffer(self):
        m = PMatPlotLib()
        m.plot([1, 2, 3])
        buf = m.saveto_buffer()
        data = buf.read()
        self.assertTrue(data.startswith(b'\x89PNG'))

    def test_clear(self):
        m = PMatPlotLib()
        m.plot([1, 2, 3])
        m.clear()
        self.assertIsNone(m._fig)

    def test_with_qnumpy(self):
        n = PNumPy()
        n.linspace(0, 6.28, 50)
        import numpy as np
        y = PNumPy()
        y.data = np.sin(n.data)
        m = PMatPlotLib()
        m.plot(n, y, label="sin")
        m.legend()
        # Verify no crash
        self.assertIsNotNone(m._ax)


class TestPPandasConstruction(unittest.TestCase):
    def test_constructor_no_crash(self):
        p = PPandas()
        self.assertEqual(p.rowcount, 0)
        self.assertEqual(p.colcount, 0)


@unittest.skipUnless(HAS_PANDAS, "pandas not installed")
class TestPPandas(unittest.TestCase):
    def test_data_from_dict(self):
        p = PPandas()
        p.data = {'A': [1, 2, 3], 'B': [4, 5, 6]}
        self.assertEqual(p.rowcount, 3)
        self.assertEqual(p.colcount, 2)
        self.assertEqual(p.columns, ['A', 'B'])

    def test_cell_access(self):
        p = PPandas()
        p.data = {'A': [10, 20], 'B': [30, 40]}
        self.assertEqual(p.cell(0, 0), 10)
        self.assertEqual(p.cell(1, 1), 40)

    def test_setcell(self):
        p = PPandas()
        p.data = {'A': [1, 2]}
        p.setcell(0, 0, 99)
        self.assertEqual(p.cell(0, 0), 99)

    def test_head_tail(self):
        p = PPandas()
        p.data = {'X': list(range(20))}
        head = p.head(3)
        self.assertIn('0', head)

    def test_describe(self):
        p = PPandas()
        p.data = {'A': [1, 2, 3, 4, 5]}
        desc = p.describe()
        self.assertIn('mean', desc)

    def test_sort(self):
        p = PPandas()
        p.data = {'A': [3, 1, 2]}
        p.sort('A')
        self.assertEqual(p.cell(0, 0), 1)

    def test_addcolumn(self):
        p = PPandas()
        p.data = {'A': [1, 2, 3]}
        p.addcolumn('B', [4, 5, 6])
        self.assertEqual(p.colcount, 2)
        self.assertIn('B', p.columns)

    def test_deletecolumn(self):
        p = PPandas()
        p.data = {'A': [1], 'B': [2]}
        p.deletecolumn('B')
        self.assertEqual(p.colcount, 1)
        self.assertNotIn('B', p.columns)

    def test_tostring(self):
        p = PPandas()
        p.data = {'A': [1]}
        s = p.tostring()
        self.assertIn('A', s)

    def test_tolist(self):
        p = PPandas()
        p.data = {'A': [1, 2], 'B': [3, 4]}
        result = p.tolist()
        self.assertEqual(len(result), 2)

    def test_csv_roundtrip(self):
        import tempfile
        p = PPandas()
        p.data = {'Name': ['Alice', 'Bob'], 'Age': [25, 30]}
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False, mode='w') as f:
            path = f.name
        try:
            p.savetocsv(path)
            p2 = PPandas()
            p2.loadfromcsv(path)
            self.assertEqual(p2.rowcount, 2)
            self.assertEqual(p2.cell(0, 0), 'Alice')
        finally:
            os.unlink(path)


if __name__ == '__main__':
    unittest.main()
