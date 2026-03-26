"""
RapidP2Python - Python-specific Components
PNumPy, PMatPlotLib, PPandas: Focused wrappers for common scientific Python operations.
"""


class PNumPy:
    """Wrapper for NumPy array operations."""

    def __init__(self):
        self._np = None
        self._arr = None
        self.tag = 0

    def _ensure_numpy(self):
        if self._np is None:
            try:
                import numpy
                self._np = numpy
            except ImportError:
                raise ImportError("PNumPy requires numpy. Install with: pip install numpy")

    @property
    def data(self):
        return self._arr

    @data.setter
    def data(self, value):
        self._ensure_numpy()
        if isinstance(value, list):
            self._arr = self._np.array(value)
        else:
            self._arr = value

    @property
    def shape(self):
        if self._arr is not None:
            return list(self._arr.shape)
        return []

    @property
    def size(self):
        if self._arr is not None:
            return self._arr.size
        return 0

    @property
    def dtype(self):
        if self._arr is not None:
            return str(self._arr.dtype)
        return ""

    def zeros(self, *shape):
        self._ensure_numpy()
        self._arr = self._np.zeros(shape)
        return self

    def ones(self, *shape):
        self._ensure_numpy()
        self._arr = self._np.ones(shape)
        return self

    def arange(self, start, stop=None, step=1):
        self._ensure_numpy()
        if stop is None:
            self._arr = self._np.arange(start)
        else:
            self._arr = self._np.arange(start, stop, step)
        return self

    def linspace(self, start, stop, num=50):
        self._ensure_numpy()
        self._arr = self._np.linspace(float(start), float(stop), int(num))
        return self

    def reshape(self, *shape):
        if self._arr is not None:
            self._arr = self._arr.reshape(shape)
        return self

    def sum(self):
        if self._arr is not None:
            return float(self._np.sum(self._arr))
        return 0

    def mean(self):
        if self._arr is not None:
            return float(self._np.mean(self._arr))
        return 0

    def std(self):
        if self._arr is not None:
            return float(self._np.std(self._arr))
        return 0

    def min(self):
        if self._arr is not None:
            return float(self._np.min(self._arr))
        return 0

    def max(self):
        if self._arr is not None:
            return float(self._np.max(self._arr))
        return 0

    def dot(self, other):
        self._ensure_numpy()
        b = other._arr if isinstance(other, PNumPy) else self._np.array(other)
        result = PNumPy()
        result._np = self._np
        result._arr = self._np.dot(self._arr, b)
        return result

    def transpose(self):
        if self._arr is not None:
            self._arr = self._arr.T
        return self

    def tolist(self):
        if self._arr is not None:
            return self._arr.tolist()
        return []

    def sort(self):
        if self._arr is not None:
            self._arr = self._np.sort(self._arr)
        return self

    def savetofile(self, filename):
        if self._arr is not None:
            self._np.save(str(filename), self._arr)

    def loadfromfile(self, filename):
        self._ensure_numpy()
        self._arr = self._np.load(str(filename))

    def __str__(self):
        return str(self._arr) if self._arr is not None else "[]"


class PMatPlotLib:
    """Wrapper for Matplotlib plotting."""

    def __init__(self):
        self._plt = None
        self._fig = None
        self._ax = None
        self.title = ""
        self.xlabel = ""
        self.ylabel = ""
        self.width = 8
        self.height = 6
        self.grid = False
        self.tag = 0

    def _ensure_mpl(self):
        if self._plt is None:
            try:
                import matplotlib
                matplotlib.use('Agg')
                import matplotlib.pyplot as plt
                self._plt = plt
            except ImportError:
                raise ImportError("PMatPlotLib requires matplotlib. Install with: pip install matplotlib")

    def _ensure_fig(self):
        self._ensure_mpl()
        if self._fig is None:
            self._fig, self._ax = self._plt.subplots(figsize=(self.width, self.height))

    def clear(self):
        if self._fig:
            self._plt.close(self._fig)
        self._fig = None
        self._ax = None

    def plot(self, x, y=None, label="", color="", linestyle="-"):
        self._ensure_fig()
        kwargs = {}
        if label:
            kwargs['label'] = label
        if color:
            kwargs['color'] = color
        if linestyle:
            kwargs['linestyle'] = linestyle
        if y is not None:
            xdata = x._arr if hasattr(x, '_arr') and x._arr is not None else x
            ydata = y._arr if hasattr(y, '_arr') and y._arr is not None else y
            self._ax.plot(xdata, ydata, **kwargs)
        else:
            data = x._arr if hasattr(x, '_arr') and x._arr is not None else x
            self._ax.plot(data, **kwargs)

    def scatter(self, x, y, label="", color="", marker="o"):
        self._ensure_fig()
        xdata = x._arr if hasattr(x, '_arr') and x._arr is not None else x
        ydata = y._arr if hasattr(y, '_arr') and y._arr is not None else y
        kwargs = {'marker': marker}
        if label:
            kwargs['label'] = label
        if color:
            kwargs['color'] = color
        self._ax.scatter(xdata, ydata, **kwargs)

    def bar(self, x, y, label="", color=""):
        self._ensure_fig()
        xdata = x._arr if hasattr(x, '_arr') and x._arr is not None else x
        ydata = y._arr if hasattr(y, '_arr') and y._arr is not None else y
        kwargs = {}
        if label:
            kwargs['label'] = label
        if color:
            kwargs['color'] = color
        self._ax.bar(xdata, ydata, **kwargs)

    def hist(self, data, bins=10, label="", color=""):
        self._ensure_fig()
        d = data._arr if hasattr(data, '_arr') and data._arr is not None else data
        kwargs = {'bins': int(bins)}
        if label:
            kwargs['label'] = label
        if color:
            kwargs['color'] = color
        self._ax.hist(d, **kwargs)

    def pie(self, data, labels=None):
        self._ensure_fig()
        d = data._arr if hasattr(data, '_arr') and data._arr is not None else data
        kwargs = {}
        if labels:
            kwargs['labels'] = labels
        self._ax.pie(d, **kwargs)

    def legend(self):
        if self._ax:
            self._ax.legend()

    def _apply_decorations(self):
        if self._ax:
            if self.title:
                self._ax.set_title(self.title)
            if self.xlabel:
                self._ax.set_xlabel(self.xlabel)
            if self.ylabel:
                self._ax.set_ylabel(self.ylabel)
            if self.grid:
                self._ax.grid(True)

    def savetofile(self, filename):
        self._ensure_fig()
        self._apply_decorations()
        self._fig.savefig(str(filename), dpi=100, bbox_inches='tight')

    def saveto_buffer(self):
        """Save plot to in-memory PNG bytes (for PImage integration)."""
        import io
        self._ensure_fig()
        self._apply_decorations()
        buf = io.BytesIO()
        self._fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        return buf

    def show(self):
        self._ensure_fig()
        self._apply_decorations()
        self._plt.show()

    def __str__(self):
        return f"PMatPlotLib(title='{self.title}')"


class PPandas:
    """Wrapper for Pandas DataFrame operations."""

    def __init__(self):
        self._pd = None
        self._df = None
        self.tag = 0

    def _ensure_pandas(self):
        if self._pd is None:
            try:
                import pandas
                self._pd = pandas
            except ImportError:
                raise ImportError("PPandas requires pandas. Install with: pip install pandas")

    @property
    def data(self):
        return self._df

    @data.setter
    def data(self, value):
        self._ensure_pandas()
        if isinstance(value, dict):
            self._df = self._pd.DataFrame(value)
        elif isinstance(value, list):
            self._df = self._pd.DataFrame(value)
        else:
            self._df = value

    @property
    def rowcount(self):
        if self._df is not None:
            return len(self._df)
        return 0

    @property
    def colcount(self):
        if self._df is not None:
            return len(self._df.columns)
        return 0

    @property
    def columns(self):
        if self._df is not None:
            return list(self._df.columns)
        return []

    def loadfromcsv(self, filename, **kwargs):
        self._ensure_pandas()
        self._df = self._pd.read_csv(str(filename), **kwargs)

    def savetocsv(self, filename, index=False):
        if self._df is not None:
            self._df.to_csv(str(filename), index=index)

    def loadfromjson(self, filename):
        self._ensure_pandas()
        self._df = self._pd.read_json(str(filename))

    def savetojson(self, filename):
        if self._df is not None:
            self._df.to_json(str(filename))

    def head(self, n=5):
        if self._df is not None:
            return self._df.head(int(n)).to_string()
        return ""

    def tail(self, n=5):
        if self._df is not None:
            return self._df.tail(int(n)).to_string()
        return ""

    def describe(self):
        if self._df is not None:
            return self._df.describe().to_string()
        return ""

    def sort(self, column, ascending=True):
        if self._df is not None:
            self._df = self._df.sort_values(by=str(column), ascending=bool(ascending))

    def filter(self, column, operator, value):
        if self._df is not None:
            col = self._df[str(column)]
            if operator == "==" or operator == "=":
                self._df = self._df[col == value]
            elif operator == ">":
                self._df = self._df[col > value]
            elif operator == "<":
                self._df = self._df[col < value]
            elif operator == ">=":
                self._df = self._df[col >= value]
            elif operator == "<=":
                self._df = self._df[col <= value]
            elif operator == "!=":
                self._df = self._df[col != value]

    def groupby(self, column, agg="sum"):
        if self._df is not None:
            grouped = self._df.groupby(str(column))
            if agg == "sum":
                self._df = grouped.sum().reset_index()
            elif agg == "mean":
                self._df = grouped.mean().reset_index()
            elif agg == "count":
                self._df = grouped.count().reset_index()
            elif agg == "min":
                self._df = grouped.min().reset_index()
            elif agg == "max":
                self._df = grouped.max().reset_index()

    def addcolumn(self, name, values):
        if self._df is not None:
            self._df[str(name)] = values

    def deletecolumn(self, name):
        if self._df is not None and str(name) in self._df.columns:
            self._df = self._df.drop(columns=[str(name)])

    def cell(self, row, col):
        if self._df is not None:
            return self._df.iloc[int(row), int(col)]
        return ""

    def setcell(self, row, col, value):
        if self._df is not None:
            self._df.iloc[int(row), int(col)] = value

    def query(self, expr):
        self._ensure_pandas()
        if self._df is not None:
            self._df = self._df.query(str(expr))

    def tostring(self):
        if self._df is not None:
            return self._df.to_string()
        return ""

    def tolist(self):
        if self._df is not None:
            return self._df.values.tolist()
        return []

    def __str__(self):
        return self.tostring()
