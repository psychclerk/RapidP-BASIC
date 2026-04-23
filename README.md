# RapidP — BASIC-to-Python Transpiler & Runtime 



[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

THIS IS AN UPDATED VERSION - ALBIET AI GENERATED CODE WITH WORKING LISTVIEWS, and OPTION TO CREATE WXPYTHON CODE USING --WX OPTION


**RapidP** is an experiment in building a full-featured BASIC-to-Python transpiler and runtime framework. It reads `.rp` BASIC language like source files and produces modern, executable **Python 3** code.

The project currently provides **49+ GUI components** (P-prefixed: `PForm`, `PButton`, `PStringGrid`, …), **100+ built-in functions**, database access, networking, and a self-hosted **Visual IDE** written in RapidP itself. Needs deeper testing, but most of the core features are implemented and functional.

> **Note:** RapidP is *inspired by* and *aims for basic compatibility with* the original RapidQ BASIC language, but it is **not** a clone or drop-in replacement. RapidP extends the language with Python-native components (NumPy, Matplotlib, Pandas), enhanced networking, and modern tooling while preserving as much backward compatibility as practical.

---

## Table of Contents

- [System Architecture](#system-architecture)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [The Compiler Engine](#the-compiler-engine)
- [Preprocessor Directives](#preprocessor-directives)
- [The Runtime Library](#the-runtime-library)
  - [GUI Components](#gui-components)
  - [Built-in Functions](#built-in-functions)
  - [Database](#database)
  - [Networking](#networking)
  - [Python Extensions](#python-extensions-pnumpy-pmatplotlib-ppandas)
- [The Self-Hosted IDE](#the-self-hosted-ide)
- [RapidP Syntax Reference](#rapidp-syntax-reference)
- [Test Suite](#test-suite)
- [Development Conventions](#development-conventions)
- [Credits](#credits)
- [License](#license)

---

## System Architecture

The project consists of four major pillars:

1. **The Transpiler Backend (`compiler/`)** — Fully parses BASIC syntax through a multi-pass pipeline.
2. **The Python Runtime (`rp_runtime/`)** — P-prefixed component library mapping to Python's Tkinter, plus networking, databases, and Python-native extensions.
3. **The CLI (`compile.py`)** — Command-line interface to transpile and optionally run `.rp` files.
4. **The IDE (`examples/ide.rp`)** — A fully functional visual designer built in RapidP, proving the transpiler's completeness.

---

## Installation

### Prerequisites

- Python 3.10 or later
- Tkinter (included with most Python distributions)

### Steps

```bash
git clone https://github.com/iBobX/RapidP-BASIC.git
cd RapidP-BASIC
pip install -r requirements.txt
```

### Optional Dependencies

The core transpiler requires only `pymysql`, `tkhtmlview`, `pygame`, `pillow`, and `pyinstaller`. For the Python-specific extension components, install the optional packages:

```bash
pip install numpy matplotlib pandas
```

---

## Quick Start

### Hello World

Create `hello.rp`:
```basic
PRINT "Hello, World!"
```

Transpile and run:
```bash
python3 compile.py hello.rp -r
```

### Compile Only

```bash
python3 compile.py hello.rp -o hello.py
```

### Launch the IDE

```bash
python3 compile.py ide.rp -r
```

### CLI Options

```
python3 compile.py <filename.rp> [-o output.py] [-r] [--encoding ENCODING]
```

| Flag | Description |
|------|-------------|
| `<filename.rp>` | Source file to transpile (RapidP-compatible syntax) |
| `-o <output.py>` | Custom output filename (default: same name with `.py` extension) |
| `-r` | Run the transpiled Python file immediately after compilation |
| `--encoding` | Source file encoding (default: `utf-8`; use `latin-1` for legacy files) |

---

## The Compiler Engine

Located in `compiler/`, the transpilation pipeline mirrors a classic multi-pass compiler:

| Stage | File | Description |
|-------|------|-------------|
| Preprocessing | `preprocessor.py` | Handles `$INCLUDE`, `$DEFINE`, `$IFDEF`/`$IFNDEF`, `$MACRO`, `$APPTYPE`, and other directives |
| Lexical Analysis | `lexer.py` | Tokenizes the source into keywords, identifiers, literals, operators, and directives |
| Parsing | `parser.py` | Recursive-descent parser producing an AST; correctly scopes `FOR…NEXT`, `DO…LOOP`, `IF…END IF`, `SELECT CASE`, and `CREATE…END CREATE` blocks |
| AST Nodes | `ast_nodes.py` | Node classes: `ForStatementNode`, `CreateStatementNode`, `AssignmentNode`, `FunctionCallNode`, etc. |
| Code Generation | `codegen.py` | Traverses the AST and emits idiomatic Python 3 code with proper indentation, `global` scoping, and runtime imports |

---

## Preprocessor Directives

| Directive | Description | Example |
|-----------|-------------|---------|
| `$INCLUDE` | Include an external source file | `$INCLUDE "rapidp.inc"` |
| `$DEFINE` | Define a text substitution constant | `$DEFINE MAX_SIZE 100` |
| `$UNDEF` | Undefine a previously defined constant | `$UNDEF MAX_SIZE` |
| `$IFDEF` / `$IFNDEF` | Conditional compilation | `$IFDEF DEBUG` |
| `$ELSE` / `$ENDIF` | Conditional branches | `$ELSE` … `$ENDIF` |
| `$MACRO` | Define a simple or parameterized macro | `$MACRO SQUARE(x) = (x) * (x)` |
| `$APPTYPE` | Set application type (`GUI` or `CONSOLE`) | `$APPTYPE CONSOLE` |
| `$OPTIMIZE` | Optimization hint (pass-through) | `$OPTIMIZE ON` |
| `$ESCAPECHARS` | Enable escape character processing | `$ESCAPECHARS ON` |

---

## The Runtime Library

The transpiler injects `from rp_runtime.<module> import *` into generated Python files. The runtime faithfully emulates the expected behaviors of classic RapidQ BASIC.

### GUI Components

Powered by Python's built-in `tkinter`, the runtime provides **49+ component classes** organized hierarchically from `PObject` → `PWidget` → specific components.

#### Forms & Containers

| Component | Description |
|-----------|-------------|
| `PForm` | Top-level window (maps to `tk.Toplevel`) |
| `PFormMDI` | MDI parent form |
| `PPanel` | Container panel |
| `PGroupBox` | Labeled group container |
| `PTabControl` | Tabbed container |
| `PSplitter` | Resizable split pane |
| `PScrollBox` | Scrollable container |

#### Input Controls

| Component | Description |
|-----------|-------------|
| `PButton` | Push button |
| `PEdit` | Single-line text input |
| `PRichEdit` | Multi-line rich text editor |
| `PCodeEditor` | Code editor with syntax highlighting |
| `PCheckBox` | Checkbox toggle |
| `PRadioButton` | Radio button |
| `PComboBox` | Drop-down combo box |
| `PScrollBar` | Scroll bar |
| `PTrackBar` | Slider / track bar |

#### Display Components

| Component | Description |
|-----------|-------------|
| `PLabel` | Static text label |
| `PCanvas` | Drawing surface |
| `PImage` | Image display (supports `loadfromfile`, `loadfromplot`, `bmpwidth`/`bmpheight`) |
| `PProgressBar` | Progress indicator |
| `PLine` | Horizontal/vertical line |
| `PStatusBar` | Status bar with panels |
| `PHTML` | HTML display widget |

#### List & Grid Components

| Component | Description |
|-----------|-------------|
| `PStringGrid` | Spreadsheet-style grid |
| `PListBox` | List box |
| `PFileListBox` | File listing list box |
| `PListView` | Multi-column list view |
| `PTreeView` | Tree view with nodes |

#### Menu Components

| Component | Description |
|-----------|-------------|
| `PMainMenu` | Menu bar |
| `PMenuItem` | Menu item (supports sub-menus) |
| `PPopupMenu` | Context / popup menu |

#### Dialogs

| Component | Description |
|-----------|-------------|
| `POpenDialog` | File open dialog |
| `PSaveDialog` | File save dialog |
| `PFileDialog` | General file dialog |
| `PColorDialog` | Color picker dialog |
| `PFontDialog` | Font picker dialog |

#### Utility Components

| Component | Description |
|-----------|-------------|
| `PTimer` | Timer with `ontimer` event |
| `PFont` | Font configuration object |
| `PIcon` | Icon resource |
| `PImageList` | Image list collection |
| `PFileStream` | File I/O stream |
| `PMemoryStream` | In-memory byte stream |
| `PStringList` | String collection |
| `PIni` | INI file reader/writer |
| `PPrinter` | Print support |
| `QMidi` | MIDI playback |
| `PDesignSurface` | Visual form designer surface (used by IDE) |

#### Event Handling

Components support event handlers that map directly to Tkinter bindings:

```basic
CREATE Form1 AS PForm
  Caption = "My App"
  CREATE Button1 AS PButton
    Caption = "Click Me"
    OnClick = HandleClick
  END CREATE
END CREATE

SUB HandleClick(Sender AS PButton)
  ShowMessage "Button clicked!"
END SUB
```

---

### Built-in Functions

Over **100 built-in functions** covering string manipulation, math, file I/O, system operations, and more. These functions are implemented in `builtins.py` and are available globally in RapidP code.

#### String Functions

| Function | Description |
|----------|-------------|
| `LEFT$(s, n)` | Left n characters |
| `RIGHT$(s, n)` | Right n characters |
| `MID$(s, start[, len])` | Substring (1-based) |
| `LEN(s)` | String length |
| `INSTR([start,] s, sub)` | Find substring (1-based) |
| `RINSTR(s, sub)` | Reverse find substring |
| `UCASE$(s)` / `LCASE$(s)` | Case conversion |
| `LTRIM$(s)` / `RTRIM$(s)` / `TRIM$(s)` | Whitespace trimming |
| `CHR$(n)` / `ASC(s)` | Character ↔ ASCII code |
| `SPACE$(n)` | n-space string |
| `STRING$(n, c)` | Repeat character |
| `STR$(n)` / `VAL(s)` | Number ↔ string conversion |
| `REPLACE$(s, old, new)` | String replacement |
| `INSERT$(s, pos, sub)` | Insert substring |
| `DELETE$(s, start, count)` | Delete from string |
| `REVERSE$(s)` | Reverse string |
| `FIELD$(s, delim, n)` | Extract delimited field |
| `TALLY(s, sub)` | Count occurrences |
| `FORMAT$(fmt, val)` | Formatted output |
| `CONVBASE$(num, from, to)` | Base conversion |
| `HEX$(n)` / `OCT$(n)` / `BIN$(n)` | Numeric base formatting |
| `HEXTODEC(s)` | Hex to decimal |

#### Math Functions

| Function | Description |
|----------|-------------|
| `ABS(n)` | Absolute value |
| `SGN(n)` | Sign (-1, 0, 1) |
| `SQR(n)` | Square root |
| `SIN(n)` / `COS(n)` / `TAN(n)` | Trigonometric |
| `ATN(n)` / `ASIN(n)` / `ACOS(n)` | Inverse trig |
| `EXP(n)` / `LOG(n)` | Exponential / natural log |
| `CEIL(n)` / `FLOOR(n)` | Rounding |
| `FIX(n)` / `FRAC(n)` | Integer / fractional part |
| `ROUND(n[, dec])` | Round to decimal places |
| `CINT(n)` / `CLNG(n)` | Convert to integer/long |
| `RND[(n)]` | Random — `RND` returns 0.0–1.0; `RND(n)` returns 0 to n-1 |
| `RANDOMIZE [seed]` | Seed random generator |
| `IIF(cond, true, false)` | Inline conditional |
| `RGB(r, g, b)` | Color value |

#### File I/O

| Function | Description |
|----------|-------------|
| `OPEN(file, mode, num)` | Open file for I/O |
| `CLOSE(num)` | Close file handle |
| `PRINT #num, ...` | Write to file |
| `WRITE #num, ...` | Write comma-delimited |
| `LINE INPUT(num)` | Read line from file |
| `EOF(num)` | End-of-file check |
| `LOF(num)` | Length of file (open handle) |
| `SEEK(num, pos)` | Seek in file |
| `FREEFILE` | Next available file number |
| `FILELEN(file)` | File size in bytes |
| `FILEEXISTS(file)` | Check file existence |
| `DIREXISTS(path)` | Check directory existence |
| `DIR$(pattern)` | Directory listing |
| `KILL(file)` | Delete file |
| `MKDIR(path)` / `RMDIR(path)` | Create/remove directory |
| `RENAME(old, new)` | Rename file |
| `CHDIR(path)` / `CURDIR$` | Change/get directory |

#### System & Memory

| Function | Description |
|----------|-------------|
| `SHELL(cmd)` / `SHELLWAIT(cmd)` | Execute system command |
| `ENVIRON$(var)` | Get environment variable |
| `COMMAND$` | Command-line arguments |
| `SLEEP(ms)` | Pause execution |
| `TIMER` | Seconds since midnight |
| `DATE$` / `TIME$` | Current date/time strings |
| `DOEVENTS` | Process pending GUI events |
| `SOUND(freq, dur)` | Play tone (pygame / system fallback) |
| `BEEP` | System beep |
| `PLAYWAV(file)` | Play WAV file |
| `SHOWMESSAGE(msg)` | Message box |
| `MESSAGEBOX(hwnd, text, cap, flags)` | Win-style message box |
| `PEEK(addr)` / `POKE(addr, val)` | Read/write console screen buffer |
| `LOCATE(row, col)` | Set cursor position |
| `COLOR(fg, bg)` | Set console colors |
| `CLS` | Clear screen buffer |
| `CSRLIN` / `POS(0)` | Get cursor row/column |
| `SIZEOF(var)` | Size of variable |
| `MEMCPY` / `MEMSET` / `MEMCMP` | Memory operations |
| `CODEPTR(func)` | Get function reference |

#### Array Functions

| Function | Description |
|----------|-------------|
| `LBOUND(arr)` | Lower bound (always 0) |
| `UBOUND(arr)` | Upper bound |
| `QUICKSORT(arr)` | In-place sort |
| `INITARRAY(arr, ...)` | Initialize with values |

---

### Database

#### PMySQL

Full MySQL/MariaDB client via `pymysql`:

```basic
DIM db AS PMySQL
db.host = "localhost"
db.user = "root"
db.password = "pass"
db.database = "mydb"
db.open
db.sql = "SELECT * FROM users"
db.query
```

#### PSQLite

SQLite database with identical interface:

```basic
DIM db AS PSQLite
db.database = "app.db"
db.open
db.sql = "CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY, name TEXT)"
db.execute
```

---

### Networking

#### PSocket

Full TCP client with SSL support and event-driven I/O:

```basic
DIM sock AS PSocket
sock.host = "example.com"
sock.port = 80
sock.onconnect = OnConnect
sock.ondataready = OnData
sock.open
```

| Property/Method | Description |
|----------------|-------------|
| `host`, `port` | Connection target |
| `open` / `close` | Connect / disconnect |
| `readline` / `writeline` | Line-oriented I/O |
| `usessl` | Enable SSL/TLS |
| `timeout` | Socket timeout (seconds) |
| `bind` / `listen` / `accept` | Server-side operations |
| `onconnect`, `ondisconnect`, `ondataready`, `onerror` | Event handlers |

#### PServerSocket

Threaded TCP server with per-client management:

```basic
DIM server AS PServerSocket
server.port = 9000
server.onclientconnect = OnClient
server.ondatareceived = OnData
server.start
```

| Property/Method | Description |
|----------------|-------------|
| `port` | Listen port |
| `start` / `stop` | Server lifecycle |
| `broadcast(msg)` | Send to all connected clients |
| `onclientconnect`, `ondatareceived`, `onclientdisconnect` | Event handlers |

#### PHTTP

Simple HTTP client with SSL:

```basic
DIM http AS PHTTP
http.url = "https://api.example.com/data"
http.getpage
PRINT http.document
```

| Property/Method | Description |
|----------------|-------------|
| `url` | Target URL |
| `getpage` / `post(data)` | HTTP GET / POST |
| `document` | Response body |
| `responseheaders` | Response headers dict |

---

### Python Extensions: PNumPy, PMatPlotLib, PPandas

These components extend RapidP with access to Python's scientific computing ecosystem. They require `numpy`, `matplotlib`, and `pandas` respectively (optional — the transpiler works without them).

#### PNumPy

```basic
DIM arr AS PNumPy
arr.arange 0, 10, 1
PRINT arr.sum       ' 45.0
PRINT arr.mean      ' 4.5
```

| Method | Description |
|--------|-------------|
| `zeros(n)` / `ones(n)` | Create arrays |
| `arange(start, stop, step)` | Range array |
| `linspace(start, stop, n)` | Linearly spaced |
| `reshape(rows, cols)` | Reshape array |
| `sum` / `mean` / `std` / `min` / `max` | Statistics |
| `dot(other)` | Matrix multiplication |
| `transpose` | Transpose matrix |
| `sort` | Sort in place |
| `save(file)` / `load(file)` | NumPy `.npy` file I/O |

#### PMatPlotLib

```basic
DIM plt AS PMatPlotLib
plt.plot x_array, y_array, "b-", "Series 1"
plt.title = "My Plot"
plt.savetofile "plot.png"
```

| Method | Description |
|--------|-------------|
| `plot(x, y, fmt, label)` | Line plot |
| `scatter(x, y, label)` | Scatter plot |
| `bar(x, heights, label)` | Bar chart |
| `hist(data, bins)` | Histogram |
| `pie(sizes, labels)` | Pie chart |
| `legend` | Show legend |
| `savetofile(path)` | Save to PNG/PDF/SVG |
| `saveto_buffer` | Save to BytesIO (for `PImage.loadfromplot`) |
| `show` / `clear` | Display / reset |

#### PPandas

```basic
DIM df AS PPandas
df.loadfromcsv "data.csv"
PRINT df.describe
df.sort "age", 0     ' ascending
```

| Method | Description |
|--------|-------------|
| `loadfromcsv(file)` / `savetocsv(file)` | CSV I/O |
| `loadfromjson(file)` / `savetojson(file)` | JSON I/O |
| `head(n)` / `tail(n)` | Preview rows |
| `describe` | Statistical summary |
| `sort(col, asc)` | Sort by column |
| `filter(col, op, val)` | Filter rows |
| `groupby(col, agg)` | Group and aggregate |
| `addcolumn(name, vals)` / `deletecolumn(name)` | Column operations |
| `cell(row, col)` / `setcell(row, col, val)` | Cell access |
| `query(expr)` | Pandas query expression |

#### PImage + Matplotlib Integration

`PImage` can display Matplotlib plots directly:

```basic
DIM plt AS PMatPlotLib
DIM img AS PImage
plt.plot x, y, "r-", "Data"
img.loadfromplot plt
```

---

## The Self-Hosted IDE

The project ships with its own robust **Visual Form Designer & Code Editor** (`ide.rp`).

- **Self-hosting**: Written purely in RapidP BASIC, serving as the ultimate benchmark of the transpiler's completeness.
- **Component Palette**: Drag-and-drop components onto a visual `PCanvas` design surface.
- **8-Handle Resize**: Full directional drag-and-resize with hit-testing mathematics.
- **Property Grid**: Double-editable spreadsheet for properties like `Caption`, `Color` (with popup pickers), and `Font`.
- **Event Grid**: Browse and bind event handlers; double-clicking auto-generates SUB stubs.
- **Code Editor**: Integrated `PCodeEditor` with syntax highlighting for writing RapidP code.
- **Code Generation**: VB-style auto-stub generation — the IDE transpiles your visual design into `.rp` source code.

```bash
python3 compile.py ide.rp -r
```

---

## Demo Examples

Three demo applications showcase the Python-specific components with full GUI integration:

| Demo | Components | Description |
|------|-----------|-------------|
| `demo_matplotlib.rp` | `PMatPlotLib` + `PImage` | Generates sine/cosine plots and bar charts, displays them inside a `PImage` on a form |
| `demo_numpy.rp` | `PNumPy` + `PStringGrid` | Array math operations (element-wise, statistics, linspace, dot product) shown in a grid |
| `demo_pandas.rp` | `PPandas` + `PStringGrid` | Loads CSV data, supports sort, filter, group-by, and summary statistics in a grid |

Run any of them:
```bash
python3 compile.py examples/demo_matplotlib.rp -r
python3 compile.py examples/demo_numpy.rp -r
python3 compile.py examples/demo_pandas.rp -r
```

> **Note:** The pandas demo expects `examples/demo_pandas_data.csv` (included) for sample employee data.

---

## RapidP Syntax Reference

### Variables & Types

```basic
DIM x AS INTEGER
DIM name AS STRING
DIM values(100) AS DOUBLE
DIM flag AS LONG
```

### TYPE (User-Defined Types)

```basic
TYPE PersonType
  Name AS STRING
  Age AS INTEGER
END TYPE

DIM person AS PersonType
person.Name = "Alice"
person.Age = 30
```

### SUB & FUNCTION

```basic
SUB Greet(name AS STRING)
  PRINT "Hello, " + name
END SUB

FUNCTION Add(a AS INTEGER, b AS INTEGER) AS INTEGER
  Add = a + b
END FUNCTION
```

### Control Flow

```basic
' IF...THEN...ELSE
IF x > 10 THEN
  PRINT "Large"
ELSEIF x > 5 THEN
  PRINT "Medium"
ELSE
  PRINT "Small"
END IF

' FOR...NEXT
FOR i = 1 TO 10
  PRINT STR$(i)
NEXT i

' WHILE...WEND
WHILE x < 100
  x = x * 2
WEND

' DO...LOOP
DO
  x = x + 1
LOOP UNTIL x >= 50

' SELECT CASE
SELECT CASE grade
  CASE "A"
    PRINT "Excellent"
  CASE "B", "C"
    PRINT "Good"
  CASE ELSE
    PRINT "Try harder"
END SELECT
```

### CREATE Blocks

```basic
CREATE Form1 AS PForm
  Caption = "My Application"
  Width = 640
  Height = 480
  Center
  CREATE Panel1 AS PPanel
    Align = 5
    CREATE Button1 AS PButton
      Caption = "OK"
      Left = 10
      Top = 10
      OnClick = HandleOK
    END CREATE
  END CREATE
END CREATE

Form1.ShowModal
```

---

## Test Suite

The project includes a comprehensive test suite with **170+ tests** covering all subsystems:

```bash
# Run all tests
python3 -m pytest tests/ -q

# Run specific test modules
python3 -m pytest tests/test_builtins.py -v
python3 -m pytest tests/test_codegen.py -v
python3 -m pytest tests/test_network.py -v
python3 -m pytest tests/test_pycomponents.py -v
```

| Test Module | Coverage |
|-------------|----------|
| `test_lexer.py` | Tokenization of all RapidP token types |
| `test_parser.py` | AST generation for all language constructs |
| `test_codegen.py` / `test_codegen_extended.py` | Python code generation, component registry, `$APPTYPE` |
| `test_builtins.py` / `test_builtins_extended.py` | All 100+ built-in functions |
| `test_directives.py` | `$DEFINE`, `$IFDEF`, `$MACRO`, `$APPTYPE`, line preservation |
| `test_gui.py` | GUI component creation and event handling |
| `test_network.py` | PSocket, PServerSocket, PHTTP |
| `test_pycomponents.py` | PNumPy, PMatPlotLib, PPandas |

---

## Development Conventions

- Transpiler expects strict block encapsulation for multi-line `IF…THEN` (must have `END IF`).
- Runtime component classes must have lowercase aliases in `gui.py` to match the `gui_types` lowercasing rule (e.g., `pform = PForm`).
- Global dependencies are resolved at the start of `SUB` blocks during code generation. Avoid deep nesting that obscures global modification scope.
- New GUI components should inherit from `PWidget` (or `PObject` for non-visual) and be added to the `COMPONENT_REGISTRY` in `codegen.py`.
- The `codegen.py` file has two `gui_types` maps (around lines 764 and 1266) — both must be updated when adding components.

---

## Credits

- **Roberto Berrospe** ([@iBobX](https://github.com/iBobX)) — Creator, architect, and lead developer
- **VS Code Copilot with Claude Opus 4.6** — AI pair-programming assistant for feature implementation, testing, and documentation

---

## License

This project is licensed under the [MIT License](LICENSE).
