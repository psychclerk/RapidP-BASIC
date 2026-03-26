"""GUI integration tests for Python extensions: PPandas+PStringGrid, PNumPy+PMatPlotLib+PImage."""
import unittest
import sys
import os
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Check for optional dependencies
try:
    import numpy
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

try:
    import matplotlib
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

try:
    import pandas
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

try:
    import tkinter as tk
    from rp_runtime.gui import get_root
    _root = get_root()  # Use the runtime's root to avoid multi-root conflicts
    HAS_TK = True
except Exception:
    HAS_TK = False

from rp_runtime.pycomponents import PNumPy, PMatPlotLib, PPandas


# ---------------------------------------------------------------------------
# PPandas -> PStringGrid integration
# ---------------------------------------------------------------------------
@unittest.skipUnless(HAS_PANDAS, "pandas not installed")
@unittest.skipUnless(HAS_TK, "tkinter not available")
class TestPandasToStringGrid(unittest.TestCase):
    """Test populating a PStringGrid from PPandas data."""

    def setUp(self):
        from rp_runtime.gui import PStringGrid
        self.grid = PStringGrid()
        self.df = PPandas()
        self.df.data = {
            "Name": ["Alice", "Bob", "Charlie"],
            "Age": [30, 25, 35],
            "City": ["New York", "London", "Tokyo"],
        }

    def test_pandas_to_grid_basic(self):
        """Load PPandas DataFrame rows into PStringGrid."""
        grid = self.grid
        df = self.df
        grid.cols = df.colcount

        # Add header row
        grid.addrow(*df.columns)
        # Add data rows
        for row_data in df.tolist():
            grid.addrow(*[str(v) for v in row_data])

        # Verify header
        self.assertEqual(grid.cell(0, 0), "Name")
        self.assertEqual(grid.cell(0, 1), "Age")
        self.assertEqual(grid.cell(0, 2), "City")

        # Verify data
        self.assertEqual(grid.cell(1, 0), "Alice")
        self.assertEqual(grid.cell(1, 1), "30")
        self.assertEqual(grid.cell(2, 0), "Bob")
        self.assertEqual(grid.cell(3, 2), "Tokyo")

        # Verify dimensions
        self.assertEqual(grid.rows, 4)  # 1 header + 3 data rows

    def test_pandas_filter_then_grid(self):
        """Filter PPandas data then load filtered results into grid."""
        df = self.df
        grid = self.grid
        grid.cols = df.colcount

        # Filter: Age > 28
        df.filter("Age", ">", 28)

        for row_data in df.tolist():
            grid.addrow(*[str(v) for v in row_data])

        # Should have Alice (30) and Charlie (35), not Bob (25)
        self.assertEqual(grid.rows, 2)
        self.assertEqual(grid.cell(0, 0), "Alice")
        self.assertEqual(grid.cell(1, 0), "Charlie")

    def test_pandas_sort_then_grid(self):
        """Sort PPandas data by column then load into grid."""
        df = self.df
        grid = self.grid
        grid.cols = df.colcount

        df.sort("Age", True)  # ascending

        for row_data in df.tolist():
            grid.addrow(*[str(v) for v in row_data])

        # Sorted by age: Bob(25), Alice(30), Charlie(35)
        self.assertEqual(grid.cell(0, 0), "Bob")
        self.assertEqual(grid.cell(1, 0), "Alice")
        self.assertEqual(grid.cell(2, 0), "Charlie")

    def test_grid_edit_back_to_pandas(self):
        """Edit grid cells then read values usable by PPandas."""
        grid = self.grid
        df = self.df
        grid.cols = df.colcount

        for row_data in df.tolist():
            grid.addrow(*[str(v) for v in row_data])

        # Edit a cell in the grid
        grid.setcell(0, 1, "31")

        # Read grid data back into a new PPandas
        new_data = {}
        col_names = df.columns
        for c_idx, col_name in enumerate(col_names):
            col_values = []
            for r_idx in range(grid.rows):
                col_values.append(grid.cell(r_idx, c_idx))
            new_data[col_name] = col_values

        df2 = PPandas()
        df2.data = new_data
        self.assertEqual(df2.cell(0, 1), "31")  # Age updated
        self.assertEqual(df2.rowcount, 3)

    def test_pandas_csv_roundtrip_to_grid(self):
        """Save PPandas to CSV, reload, and populate grid."""
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
            csv_path = f.name

        try:
            self.df.savetocsv(csv_path)

            df2 = PPandas()
            df2.loadfromcsv(csv_path)

            grid = self.grid
            grid.cols = df2.colcount

            grid.addrow(*df2.columns)
            for row_data in df2.tolist():
                grid.addrow(*[str(v) for v in row_data])

            self.assertEqual(grid.rows, 4)  # header + 3 rows
            self.assertEqual(grid.cell(0, 0), "Name")
            self.assertEqual(grid.cell(1, 0), "Alice")
        finally:
            os.unlink(csv_path)


# ---------------------------------------------------------------------------
# PNumPy + PMatPlotLib -> PImage integration
# ---------------------------------------------------------------------------
@unittest.skipUnless(HAS_NUMPY, "numpy not installed")
@unittest.skipUnless(HAS_MATPLOTLIB, "matplotlib not installed")
class TestNumPyMatPlotLibPlotGeneration(unittest.TestCase):
    """Test generating plots from PNumPy data via PMatPlotLib."""

    def test_line_plot_to_buffer(self):
        """Generate a line plot from PNumPy arrays and save to buffer."""
        x = PNumPy()
        x.arange(0, 100)

        y = PNumPy()
        y.data = [v ** 2 for v in x.tolist()]

        plt = PMatPlotLib()
        plt.title = "Quadratic"
        plt.xlabel = "x"
        plt.ylabel = "y"
        plt.plot(x, y, label="x^2")

        buf = plt.saveto_buffer()
        self.assertIsNotNone(buf)
        png_header = buf.read(4)
        self.assertEqual(png_header, b'\x89PNG')
        plt.clear()

    def test_scatter_plot_to_file(self):
        """Generate a scatter plot and save to a PNG file."""
        x = PNumPy()
        x.arange(0, 50)

        y = PNumPy()
        y.data = [v * 0.5 + 2 for v in x.tolist()]

        plt = PMatPlotLib()
        plt.title = "Scatter Test"
        plt.scatter(x, y, label="data")

        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            png_path = f.name

        try:
            plt.savetofile(png_path)
            self.assertTrue(os.path.exists(png_path))
            self.assertGreater(os.path.getsize(png_path), 100)

            # Verify it's a valid PNG
            with open(png_path, 'rb') as f:
                self.assertEqual(f.read(4), b'\x89PNG')
        finally:
            os.unlink(png_path)
            plt.clear()

    def test_bar_chart(self):
        """Generate a bar chart from PNumPy arrays."""
        categories = PNumPy()
        categories.arange(1, 6)

        values = PNumPy()
        values.data = [10, 25, 15, 30, 20]

        plt = PMatPlotLib()
        plt.title = "Sales"
        plt.bar(categories, values, label="revenue")

        buf = plt.saveto_buffer()
        buf.seek(0)
        self.assertEqual(buf.read(4), b'\x89PNG')
        plt.clear()

    def test_multiple_series(self):
        """Plot multiple data series and verify output."""
        x = PNumPy()
        x.linspace(0, 6.28, 100)

        sin_y = PNumPy()
        sin_y.data = [numpy.sin(v) for v in x.tolist()]

        cos_y = PNumPy()
        cos_y.data = [numpy.cos(v) for v in x.tolist()]

        plt = PMatPlotLib()
        plt.title = "Trig Functions"
        plt.plot(x, sin_y, label="sin(x)")
        plt.plot(x, cos_y, label="cos(x)")
        plt.legend()

        buf = plt.saveto_buffer()
        buf.seek(0)
        png_data = buf.read()
        self.assertGreater(len(png_data), 1000)  # real plot should be > 1KB
        plt.clear()


@unittest.skipUnless(HAS_NUMPY, "numpy not installed")
@unittest.skipUnless(HAS_MATPLOTLIB, "matplotlib not installed")
@unittest.skipUnless(HAS_TK, "tkinter not available")
class TestMatPlotLibToImage(unittest.TestCase):
    """Test loading PMatPlotLib plots into PImage component."""

    def test_loadfromplot(self):
        """Generate a plot and load it into PImage via loadfromplot."""
        from rp_runtime.gui import PImage

        x = PNumPy()
        x.arange(0, 10)
        y = PNumPy()
        y.data = [v ** 2 for v in x.tolist()]

        plt = PMatPlotLib()
        plt.title = "Test Plot"
        plt.plot(x, y, label="quadratic")

        img = PImage()
        img.autosize = 1
        img.loadfromplot(plt)

        self.assertGreater(img.bmpwidth, 0)
        self.assertGreater(img.bmpheight, 0)
        self.assertIsNotNone(img.image)
        plt.clear()

    def test_plot_save_then_load_in_image(self):
        """Save plot to file, then load into PImage from file."""
        from rp_runtime.gui import PImage

        x = PNumPy()
        x.linspace(0, 10, 50)
        y = PNumPy()
        y.data = [v * 2 for v in x.tolist()]

        plt = PMatPlotLib()
        plt.plot(x, y)

        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            png_path = f.name

        try:
            plt.savetofile(png_path)

            img = PImage()
            img.autosize = 1
            img.loadfromfile(png_path)

            self.assertGreater(img.bmpwidth, 0)
            self.assertGreater(img.bmpheight, 0)
        finally:
            os.unlink(png_path)
            plt.clear()

    def test_image_dimensions_from_plot(self):
        """Verify PImage dimensions are reasonable for PMatPlotLib figure size."""
        from rp_runtime.gui import PImage

        plt = PMatPlotLib()
        plt.width = 4
        plt.height = 3

        x = PNumPy()
        x.arange(0, 5)
        plt.plot(x)

        img = PImage()
        img.autosize = 1
        img.loadfromplot(plt)

        # bbox_inches='tight' trims whitespace, so exact match is not guaranteed
        # but dimensions should be close to 4*100=400 x 3*100=300
        self.assertGreater(img.bmpwidth, 200)
        self.assertGreater(img.bmpheight, 150)
        self.assertLess(img.bmpwidth, 600)
        self.assertLess(img.bmpheight, 450)
        plt.clear()


# ---------------------------------------------------------------------------
# PNumPy + PPandas integration
# ---------------------------------------------------------------------------
@unittest.skipUnless(HAS_NUMPY, "numpy not installed")
@unittest.skipUnless(HAS_PANDAS, "pandas not installed")
class TestNumPyPandasIntegration(unittest.TestCase):
    """Test data flow between PNumPy and PPandas."""

    def test_numpy_array_to_pandas_column(self):
        """Create PNumPy array and use it as a PPandas column."""
        arr = PNumPy()
        arr.arange(1, 11)

        df = PPandas()
        df.data = {"values": arr.tolist()}
        self.assertEqual(df.rowcount, 10)
        self.assertEqual(df.cell(0, 0), 1)
        self.assertEqual(df.cell(9, 0), 10)

    def test_pandas_column_to_numpy_stats(self):
        """Load PPandas column into PNumPy for statistical analysis."""
        df = PPandas()
        df.data = {"score": [85, 92, 78, 95, 88, 76, 91, 83, 97, 80]}

        scores = PNumPy()
        scores.data = [df.cell(i, 0) for i in range(df.rowcount)]

        self.assertAlmostEqual(scores.mean(), 86.5)
        self.assertEqual(scores.min(), 76)
        self.assertEqual(scores.max(), 97)

    def test_numpy_computation_to_pandas(self):
        """Compute in PNumPy, store result in PPandas DataFrame."""
        x = PNumPy()
        x.arange(0, 5)

        squared = PNumPy()
        squared.data = [v ** 2 for v in x.tolist()]

        df = PPandas()
        df.data = {"x": x.tolist(), "x_squared": squared.tolist()}

        self.assertEqual(df.colcount, 2)
        self.assertEqual(df.cell(3, 0), 3)
        self.assertEqual(df.cell(3, 1), 9)


# ---------------------------------------------------------------------------
# Full pipeline: PNumPy -> PMatPlotLib -> PImage + PPandas -> PStringGrid
# ---------------------------------------------------------------------------
@unittest.skipUnless(HAS_NUMPY and HAS_MATPLOTLIB and HAS_PANDAS, "requires numpy+matplotlib+pandas")
@unittest.skipUnless(HAS_TK, "tkinter not available")
class TestFullPipeline(unittest.TestCase):
    """End-to-end integration: data generation, visualization, and grid display."""

    def test_full_data_pipeline(self):
        """Generate data -> compute stats -> plot -> display in grid and image."""
        from rp_runtime.gui import PStringGrid, PImage

        # 1. Generate data with PNumPy
        x = PNumPy()
        x.arange(1, 11)
        y = PNumPy()
        y.data = [v ** 2 for v in x.tolist()]

        # 2. Store in PPandas
        df = PPandas()
        df.data = {"X": x.tolist(), "Y": y.tolist()}
        self.assertEqual(df.rowcount, 10)

        # 3. Populate PStringGrid
        grid = PStringGrid()
        grid.cols = df.colcount
        grid.addrow(*df.columns)
        for row_data in df.tolist():
            grid.addrow(*[str(int(v)) for v in row_data])

        self.assertEqual(grid.rows, 11)  # header + 10 data rows
        self.assertEqual(grid.cell(0, 0), "X")
        self.assertEqual(grid.cell(0, 1), "Y")
        self.assertEqual(grid.cell(5, 1), "25")  # 5^2

        # 4. Generate plot
        plt = PMatPlotLib()
        plt.title = "X vs X^2"
        plt.plot(x, y, label="quadratic")

        # 5. Load into PImage
        img = PImage()
        img.autosize = 1
        img.loadfromplot(plt)

        self.assertGreater(img.bmpwidth, 0)
        self.assertGreater(img.bmpheight, 0)
        plt.clear()


if __name__ == '__main__':
    unittest.main()
