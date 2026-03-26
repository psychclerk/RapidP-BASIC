# RapidP Compiler & Language Manual

> **Purpose:** This is a comprehensive reference for AI assistants (and humans) working on the RapidP codebase. It documents the full language syntax, compiler internals, runtime architecture, known limitations, and coding patterns — eliminating the need to re-analyze the source each time.
> **Instructions for AI:** Always read this manual first when working on RapidP. Refer to specific sections as needed. When adding new features or fixing bugs, update this manual with relevant details and examples to ensure the knowledge is retained for future reference.
>
> **Last Updated:** March 26, 2026

---

## Table of Contents

- [1. Project Overview](#1-project-overview)
- [2. Architecture & Pipeline](#2-architecture--pipeline)
- [3. Language Syntax Reference](#3-language-syntax-reference)
  - [3.1 Comments](#31-comments)
  - [3.2 Variables & Types](#32-variables--types)
  - [3.3 Constants](#33-constants)
  - [3.4 Arrays](#34-arrays)
  - [3.5 User-Defined Types (TYPE)](#35-user-defined-types-type)
  - [3.6 Control Flow](#36-control-flow)
  - [3.7 Subroutines & Functions](#37-subroutines--functions)
  - [3.8 CREATE Blocks (GUI)](#38-create-blocks-gui)
  - [3.9 WITH Blocks](#39-with-blocks)
  - [3.10 IMPORT Statement](#310-import-statement)
  - [3.11 DECLARE Statement (DLL/FFI)](#311-declare-statement-dllffi)
  - [3.12 BIND Statement](#312-bind-statement)
  - [3.13 PRINT Statement](#313-print-statement)
  - [3.14 Operators](#314-operators)
  - [3.15 String Suffixes](#315-string-suffixes)
- [4. Preprocessor Directives](#4-preprocessor-directives)
- [5. Compiler Internals](#5-compiler-internals)
  - [5.1 Lexer (compiler/lexer.py)](#51-lexer-compilerlexerpy)
  - [5.2 Parser (compiler/parser.py)](#52-parser-compilerparserpy)
  - [5.3 AST Nodes (compiler/ast_nodes.py)](#53-ast-nodes-compilerast_nodespy)
  - [5.4 Code Generator (compiler/codegen.py)](#54-code-generator-compilercodgenpy)
  - [5.5 Preprocessor (compiler/preprocessor.py)](#55-preprocessor-compilerpreprocessorpy)
  - [5.6 Error System (compiler/errors.py)](#56-error-system-compilererrorspy)
  - [5.7 Symbol Table](#57-symbol-table)
  - [5.8 Component Registry](#58-component-registry)
- [6. Runtime Library](#6-runtime-library)
  - [6.1 Builtins (rp_runtime/builtins.py)](#61-builtins-rp_runtimebuiltinspy)
  - [6.2 GUI (rp_runtime/gui.py)](#62-gui-rp_runtimeguipy)
  - [6.3 Database (rp_runtime/database.py)](#63-database-rp_runtimedatabasepy)
  - [6.4 Network (rp_runtime/network.py)](#64-network-rp_runtimenetworkpy)
  - [6.5 PyComponents (rp_runtime/pycomponents.py)](#65-pycomponents-rp_runtimepycomponentspy)
- [7. Code Generation Patterns](#7-code-generation-patterns)
- [8. Known Limitations & Gotchas](#8-known-limitations--gotchas)
- [9. How to Add New Features](#9-how-to-add-new-features)
- [10. Test Suite](#10-test-suite)

---

## 1. Project Overview

**RapidP** is a BASIC-to-Python transpiler that reads `.rp` source files (BASIC-like syntax inspired by RapidQ) and produces executable Python 3 code. The project lives at the root directory and consists of:

```
compile.py              — CLI entry point (transpile & optionally run)
compiler/               — Transpiler backend (lexer, parser, AST, codegen, preprocessor, errors)
rp_runtime/             — Python runtime library (builtins, GUI, database, network, pycomponents)
examples/               — Demo and test .rp programs
tests/                  — pytest test suite (170+ tests)
```

### CLI Usage

```bash
python3 compile.py <file.rp> [-o output.py] [-r] [--encoding ENCODING] [--json-errors] [-b] [-s]
```

| Flag | Description |
|------|-------------|
| `-o` | Output filename (default: same base name `.py`) |
| `-r` | Run after compilation |
| `-b` | Compile to bytecode (`.pyc`) |
| `-s` | Build standalone executable via PyInstaller |
| `--encoding` | Source encoding (default `utf-8`, use `latin-1` for legacy) |
| `--json-errors` | Output errors as JSON array (for IDE integration) |

---

## 2. Architecture & Pipeline

The compilation pipeline (in `compile.py`'s `compile_code()`) is:

```
Source (.rp)
    ↓
Preprocessor (preprocessor.py)  — $INCLUDE, $DEFINE, $IFDEF, $MACRO expansion
    ↓
Lexer (lexer.py)                — Tokenization into Token stream
    ↓
Parser (parser.py)              — Recursive-descent → AST (ProgramNode)
    ↓
CodeGenerator (codegen.py)      — AST traversal → Python 3 source string
    ↓
Output (.py)
```

**Key design decisions:**
- The parser is a **single-pass recursive-descent** parser — no separate semantic analysis pass.
- The code generator does **three pre-passes** before generating code:
  1. Collect UDT type names (`TypeStatementNode`)
  2. Collect global variables, arrays, constants, and CREATE components (`collect_globals`)
  3. Collect SUB/FUNCTION signatures, DECLARE, IMPORT modules
- Then processes directives ($TYPECHECK, $APPTYPE, etc.)
- Then generates Python code by visiting AST nodes.

---

## 3. Language Syntax Reference

### 3.1 Comments

```basic
' This is a comment (single quote)
REM This is also a comment
```

Comments are stripped by the lexer. Everything after `'` or `REM` on a line is ignored.

### 3.2 Variables & Types

```basic
DIM x AS INTEGER
DIM name AS STRING
DIM value AS DOUBLE
DIM flag AS LONG
DIM anything AS VARIANT      ' Default type when unspecified
```

**Supported types:**
| Type | Python Equivalent | Default Value |
|------|-------------------|---------------|
| `INTEGER` | `int` | `0` |
| `LONG` | `int` | `0` |
| `INT64` | `int` | `0` |
| `BYTE` | `int` | `0` |
| `WORD` | `int` | `0` |
| `DWORD` | `int` | `0` |
| `SINGLE` | `float` | `0` |
| `DOUBLE` | `float` | `0` |
| `CURRENCY` | `float` | `0` |
| `STRING` | `str` | `""` |
| `VARIANT` | any | `None` |
| `POBJECT` | any | `None` |
| Any P-component | class instance | constructor call |
| Any UDT name | dataclass instance | constructor call |

**Multiple declarations:**
```basic
DIM a, b, c AS INTEGER     ' All three are INTEGER
```

**Implicit declaration:** When `$TYPECHECK OFF` (default), assigning to an undeclared variable auto-declares it as `DOUBLE` (or whatever `$OPTION DIM` specifies).

**Case insensitivity:** RapidP identifiers are case-insensitive. The codegen lowercases all identifiers (e.g., `MyVar` → `myvar`).

**Suffix conventions (legacy BASIC):** The lexer accepts `$`, `%`, `#`, `&`, `!` suffixes on identifiers (e.g., `name$`, `count%`). These are stripped during code generation.

### 3.3 Constants

```basic
CONST PI = 3.14159
CONST MAX_SIZE AS LONG = 100    ' Optional type annotation (ignored)
CONST GREETING = "Hello"
```

Constants are compiled as regular Python variable assignments. They are tracked in `SymbolTable.const_names` for validation purposes.

### 3.4 Arrays

```basic
DIM values(100) AS DOUBLE       ' Array of 101 elements (0-100)
DIM grid(10, 20) AS INTEGER     ' 2D array (currently stored as nested list)
DIM names(1 TO 50) AS STRING    ' 1-based range (allocates 51 elements, 0 unused)
```

**Important:** In RapidP, `DIM A(10)` creates 11 elements (indices 0-10), matching classic BASIC semantics. The codegen emits `a = [0] * (10 + 1)`.

**Array access uses parentheses** (not square brackets):
```basic
values(5) = 42.0
x = values(i)
```

**The array/function ambiguity:** Both array access and function calls use `()` — e.g., `foo(5)` could be either. The parser always creates `FunctionCallNode` at parse time. The codegen resolves this:
1. If the name is in `self.arrays` set → emit `name[idx]`
2. If the name is in the symbol table as `variable`/`array`/`component` → emit `name[idx]`
3. Otherwise → emit `name(idx)` (function call)

### 3.5 User-Defined Types (TYPE)

```basic
TYPE PersonType
    Name AS STRING
    Age AS INTEGER
    Scores(10) AS DOUBLE
END TYPE

TYPE Employee EXTENDS PersonType
    Department AS STRING
    
    CONSTRUCTOR
        .Department = "Unknown"
    END CONSTRUCTOR
    
    SUB Display()
        PRINT .Name + " - " + .Department
    END SUB
END TYPE

DIM p AS PersonType
p.Name = "Alice"
p.Age = 30
p.Scores(1) = 95.5
```

**Generated as Python `@dataclass` classes.**

Supports:
- Fields with optional array dimensions
- `EXTENDS` for inheritance
- `CONSTRUCTOR` block (mapped to `__post_init__`)
- Embedded `SUB`/`FUNCTION` methods (gets `self` parameter injected)
- `PRIVATE`/`PUBLIC` visibility markers (parsed but ignored in codegen)
- `PROPERTY SET` attribute (parsed but not fully implemented)

### 3.6 Control Flow

#### IF...THEN...END IF (Block)
```basic
IF x > 10 THEN
    PRINT "Large"
ELSEIF x > 5 THEN
    PRINT "Medium"
ELSE
    PRINT "Small"
END IF
```

#### IF...THEN (Single-line)
```basic
IF x > 10 THEN PRINT "Large"
IF x > 10 THEN PRINT "A" : PRINT "B" ELSE PRINT "C"
```
Single-line IF handles `:` as additional THEN-branch statements until ELSE or newline.

#### FOR...NEXT
```basic
FOR i = 1 TO 10
    PRINT STR$(i)
NEXT i           ' Variable name after NEXT is optional

FOR j = 10 TO 0 STEP -1
    PRINT STR$(j)
NEXT j
```

**Generated as `while` loop** (not Python `for/range`):
```python
i = 1
while i <= 10:
    rp_print(str_func(i))
    i += 1
```
This correctly handles both positive and negative STEP values, including floating-point steps.

#### WHILE...WEND
```basic
WHILE x < 100
    x = x * 2
WEND
```

#### DO...LOOP
```basic
' Pre-condition forms:
DO WHILE x < 100
    x = x + 1
LOOP

DO UNTIL x >= 50
    x = x + 1
LOOP

' Post-condition forms:
DO
    x = x + 1
LOOP WHILE x < 100

DO
    x = x + 1
LOOP UNTIL x >= 50
```

#### SELECT CASE
```basic
SELECT CASE grade
    CASE "A"
        PRINT "Excellent"
    CASE "B", "C"
        PRINT "Good"
    CASE ELSE
        PRINT "Try harder"
END SELECT
```
**Generated as if/elif/else chain** with a temporary variable `_select_val_{line}`.

#### EXIT Statement
```basic
EXIT FOR       ' → break
EXIT WHILE     ' → break
EXIT DO        ' → break
EXIT SUB       ' → return
EXIT FUNCTION  ' → return <function_name>
```

### 3.7 Subroutines & Functions

#### SUB (no return value)
```basic
SUB Greet(name AS STRING)
    PRINT "Hello, " + name
END SUB

' Calling:
CALL Greet("World")
Greet "World"           ' CALL keyword is optional
Greet("World")          ' Parentheses also work
```

#### FUNCTION (returns a value)
```basic
FUNCTION Add(a AS INTEGER, b AS INTEGER) AS INTEGER
    Add = a + b          ' Return by assigning to function name
END FUNCTION

' Or with RETURN:
FUNCTION Add2(a AS INTEGER, b AS INTEGER) AS INTEGER
    RETURN a + b
END FUNCTION

DIM result AS INTEGER
result = Add(3, 4)
```

**Function return mechanism:** The codegen creates a local variable with the function's name, initialized to `None`. Assigning to the function name sets this variable. A `return <name>` is appended at the end.

**Parameter passing:** `BYVAL` and `BYREF` keywords are accepted by the parser but ignored (Python semantics apply — mutable objects are effectively BYREF).

**Global variable scoping:** Every SUB/FUNCTION gets a `global` declaration for all top-level variables (excluding parameters and the function name itself).

### 3.8 CREATE Blocks (GUI)

```basic
CREATE Form1 AS PForm
    Caption = "My App"
    Width = 640
    Height = 480
    
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
```

**Semantics:**
- `CREATE X AS PType` generates `x = PType(parent=<enclosing_object>)` (or without parent for top-level)
- Property assignments inside CREATE become `x.prop = value`
- Method calls inside CREATE become `x.method(args)`
- Nested CREATEs pass the parent automatically
- Builtin function calls inside CREATE blocks are NOT prefixed (they're detected via a known-builtins list)
- The `create_obj_stack` tracks nesting, `_create_type_stack` tracks component types for validation

**Q-prefix backward compatibility:** Types prefixed with `Q` (from RapidQ) are automatically normalized to `P` prefix by `_normalize_comp_type()`.

### 3.9 WITH Blocks

```basic
DIM form AS PForm

WITH form
    .Caption = "My Form"
    .Width = 800
    .Height = 600
END WITH
```

The parser maintains a `with_stack`. When a `.` is encountered at the start of an expression or statement, it's resolved to `with_stack[-1].member`.

### 3.10 IMPORT Statement

```basic
IMPORT "numpy" AS np
IMPORT "math" AS math
IMPORT os
```

Generated as `import <module> as <alias>` in Python. The alias is registered in the symbol table as a `MODULE` kind, preventing the codegen from treating it as an undeclared variable.

### 3.11 DECLARE Statement (DLL/FFI)

```basic
DECLARE SUB Sleep LIB "kernel32" ALIAS "Sleep" (ms AS LONG)
DECLARE FUNCTION GetTickCount LIB "kernel32" ALIAS "GetTickCount" () AS LONG
```

Translated to `from <lib> import <alias> as <name>`. The `.dll`/`.so` extension is stripped. Empty LIB defaults to `builtins`.

### 3.12 BIND Statement

```basic
BIND Button1.OnClick TO HandleClick
```

Generated as `button1.onclick = handleclick`.

### 3.13 PRINT Statement

```basic
PRINT "Hello"                    ' With newline
PRINT "A", "B", "C"             ' Comma-separated (space-separated in output)
PRINT "No newline";             ' Semicolon suppresses newline
PRINT                           ' Empty line
PRINT #1, "To file"             ' File I/O (handled by builtins)
```

Generated as `rp_print(...)` calls, which wraps Python's `print()`.

### 3.14 Operators

| Operator | RapidP | Python Equivalent |
|----------|--------|-------------------|
| Addition | `+` | `+` |
| Subtraction | `-` | `-` |
| Multiplication | `*` | `*` |
| Division | `/` | `/` |
| Integer Division | `\` | `//` |
| Modulo | `MOD` | `%` |
| Exponentiation | `^` | `**` |
| String Concatenation | `&` or `+` | `+` |
| Equal | `=` | `==` |
| Not Equal | `<>` | `!=` |
| Less Than | `<` | `<` |
| Greater Than | `>` | `>` |
| Less/Equal | `<=` | `<=` |
| Greater/Equal | `>=` | `>=` |
| Logical AND | `AND` | `and` |
| Logical OR | `OR` | `or` |
| Logical NOT | `NOT` | `not` |
| Logical XOR | `XOR` | `^` |

**Operator precedence (highest to lowest):**
1. Unary (`NOT`, `-`, `+`)
2. Exponentiation (`^`)
3. Multiplication/Division (`*`, `/`, `\`, `MOD`)
4. Addition/Subtraction (`+`, `-`, `&`)
5. Comparison (`<`, `>`, `<=`, `>=`)
6. Equality (`=`, `<>`)
7. Logical AND
8. Logical OR, XOR

### 3.15 String Suffixes

BASIC-style identifier suffixes are accepted by the lexer:
- `$` — String (e.g., `LEFT$`, `MID$`, `name$`)
- `%` — Integer
- `#` — Double
- `&` — Long
- `!` — Single

These are **stripped during code generation** — they don't affect typing.

---

## 4. Preprocessor Directives

Handled in `compiler/preprocessor.py` before lexing.

| Directive | Description | Behavior |
|-----------|-------------|----------|
| `$INCLUDE "file"` | Include external source file | Recursively preprocesses and inlines; detects circular includes |
| `$DEFINE SYMBOL [value]` | Define text substitution | Whole-word replacement in non-string segments; default value = `"1"` |
| `$UNDEF SYMBOL` | Remove a define | |
| `$IFDEF SYMBOL` | Conditional: skip if not defined | Supports nesting |
| `$IFNDEF SYMBOL` | Conditional: skip if defined | |
| `$ELSE` | Toggle conditional branch | |
| `$ENDIF` | End conditional block | |
| `$MACRO NAME[(params)] = body` | Define parameterized macro | Expanded before $DEFINE substitution |
| `$APPTYPE GUI\|CONSOLE\|CGI` | Set application type | Passed through to codegen as DirectiveNode |
| `$OPTIMIZE ON\|OFF` | Optimization hint | Pass-through (no effect) |
| `$ESCAPECHARS ON\|OFF` | Escape character mode | Pass-through (no effect) |
| `$TYPECHECK ON\|OFF` | Enable/disable strict type checking | Enables undeclared variable/function errors |
| `$OPTION EXPLICIT` | Same as `$TYPECHECK ON` | |
| `$OPTION DIM <TYPE>` | Default DIM type | Changes default from `DOUBLE` |

**Line preservation:** The preprocessor replaces consumed directive lines with empty strings to preserve line numbers for error reporting.

**$DEFINE substitution rules:**
- Only replaces whole words (uses `\b` word boundaries)
- Skips content inside quoted strings (splits by `"`, only substitutes in even-indexed segments)
- Sorted by length (longest first) to avoid partial replacements
- Inline comments in `$DEFINE` lines are stripped via `split("'")`

---

## 5. Compiler Internals

### 5.1 Lexer (`compiler/lexer.py`)

**307 lines.** Tokenizes source into `Token(type, value, line, column)` tuples.

**Token types (enum `TokenType`):**
- **Keywords (40+):** `DIM`, `AS`, `IF`, `THEN`, `ELSE`, `ELSEIF`, `END`, `FOR`, `TO`, `STEP`, `NEXT`, `WHILE`, `WEND`, `DO`, `LOOP`, `UNTIL`, `SELECT`, `CASE`, `SUB`, `FUNCTION`, `CALL`, `RETURN`, `EXIT`, `PRINT`, `INPUT`, `GOTO`, `GOSUB`, `IMPORT`, `CREATE`, `CONST`, `TYPE`, `DECLARE`, `LIB`, `ALIAS`, `WITH`, `EXTENDS`, `PROPERTY`, `SET`, `BYVAL`, `BYREF`, `BIND`, `CONSTRUCTOR`, `AND`, `OR`, `NOT`, `XOR`, `MOD`, `DEFSTR`, `DEFINT`, etc.
- **Type keywords:** `INTEGER`, `STRING`, `DOUBLE`, `SINGLE`, `BYTE`, `WORD`, `DWORD`, `LONG`, `INT64`, `CURRENCY`, `POBJECT`
- **Operators:** `PLUS`, `MINUS`, `STAR`, `SLASH`, `BACKSLASH`, `CARET`, `AMPERSAND`, `EQ`, `NEQ`, `LT`, `LTE`, `GT`, `GTE`
- **Symbols:** `LPAREN`, `RPAREN`, `COMMA`, `COLON`, `SEMI`, `DOT`
- **Literals:** `NUMBER`, `STRING_LIT`, `IDENTIFIER`
- **Special:** `NEWLINE`, `EOF`, `DIRECTIVE`

**Tokenization method:** Single compiled regex with named groups, applied via `finditer()`. Rules are ordered by priority (comments first, then directives, numbers, strings, identifiers, operators).

**Number formats:**
- Decimal: `123`, `3.14`, `1.5e10`
- Hex: `&H1F` or `&hFF` → converted to `0x1f`
- Octal: `&O77` → converted to `0o77`
- Binary: `&B1010` → converted to `0b1010`

**Line continuation:** `_` at end of line (before newline) is swallowed as whitespace.

**CRITICAL LIMITATION:** The lexer does NOT support `[`, `]`, `{`, or `}` characters. Any use of Python-style list literals `[1, 2, 3]` or dict literals `{"key": "value"}` will cause a "Unexpected character" error. Workarounds: use component methods (PNumPy.arange, PPandas.loadfromcsv) or IMPORT a Python module.

### 5.2 Parser (`compiler/parser.py`)

**847 lines.** Recursive-descent parser producing AST from token stream.

**Key methods:**
- `parse()` → `ProgramNode` (top-level)
- `parse_statement()` — dispatches to specific statement parsers based on current token
- `parse_expression()` → starts precedence climbing
- `parse_assignment_or_call()` — handles the ambiguous `IDENTIFIER [.member]* [= expr | args]` pattern

**Expression precedence (method call chain):**
```
parse_expression → parse_logical_or → parse_logical_and → parse_equality
    → parse_comparison → parse_term → parse_factor → parse_power
    → parse_unary → parse_primary
```

**Statement terminators:** `NEWLINE` or `COLON` (`:` allows multiple statements per line).

**Block parsing:** `parse_block(end_tokens)` — consumes statements until one of the `end_tokens` is found at the current position. Used by IF, FOR, WHILE, DO, SELECT, SUB, FUNCTION, TYPE, WITH, CREATE.

**The assignment-or-call ambiguity:** When the parser sees an `IDENTIFIER`:
1. If followed by `(` → parse as `ArrayAccessNode` (statement level)
2. If followed by `.` → chain into `MemberAccessNode`
3. If followed by `=` → it's an `AssignmentNode`
4. Otherwise → it's a `CallStatementNode` with space-separated arguments

**The array/function ambiguity in expressions:** In `parse_primary()`, `IDENTIFIER(args)` is always parsed as `FunctionCallNode`. The codegen resolves whether it's actually array indexing.

### 5.3 AST Nodes (`compiler/ast_nodes.py`)

**192 lines.** All nodes are `@dataclass` classes inheriting from `ASTNode(line, column)`.

**Expression nodes** (inherit `ExpressionNode`):
- `IdentifierNode(name)` — variable or function name
- `LiteralNode(value, type_name)` — string, number literal
- `BinaryOpNode(left, op, right)` — binary operation
- `UnaryOpNode(op, operand)` — unary operation
- `ArrayAccessNode(array, index)` — explicit array access (from statement-level parsing)
- `MemberAccessNode(obj, member)` — dot access
- `FunctionCallNode(name, args)` — function call OR array access (ambiguous)
- `MethodCallNode(obj, method, args)` — method call

**Statement nodes** (inherit `StatementNode`):
- `DimStatementNode(variables: List[tuple], var_type)` — variable is `(name, array_dims_or_None)`
- `AssignmentNode(target, value)`
- `IfStatementNode(condition, then_branch, elseif_branches, else_branch)`
- `ForStatementNode(variable, start, end, step, body)`
- `WhileStatementNode(condition, body)`
- `DoLoopStatementNode(condition, pre_condition, is_until, body)`
- `SelectCaseStatementNode(expression, cases, case_else)`
- `PrintStatementNode(items, append_newline)`
- `SubroutineDefNode(name, params, body)`
- `FunctionDefNode(name, params, return_type, body)`
- `CallStatementNode(name, args)`
- `MethodCallStatementNode(method_call: MethodCallNode)`
- `ImportStatementNode(module_name, alias)`
- `WithStatementNode(obj, body)`
- `CreateStatementNode(name, obj_type, body)`
- `ReturnStatementNode(value)`
- `ExitStatementNode(exit_type)`
- `DirectiveNode(name, value)`
- `ConstStatementNode(name, value)`
- `DeclareStatementNode(name, lib, alias, params, return_type)`
- `TypeStatementNode(name, fields, methods, constructor, extends)`
- `BindStatementNode(target, function)`

### 5.4 Code Generator (`compiler/codegen.py`)

**1464 lines.** The largest and most complex file. Visits AST nodes and emits Python 3 code.

**Key class: `CodeGenerator`**

**State tracking:**
- `output` — collected code lines
- `indent_level` — current Python indentation depth
- `imported_modules` — set of import statements to add to preamble
- `create_obj_stack` — stack of current CREATE block object names (for implicit property prefixing)
- `_create_type_stack` — parallel stack of component type names (for validation)
- `global_vars` — set of all top-level variable names
- `arrays` — set of all explicitly DIM'd array names
- `udts` — dict of `UPPER_NAME → original_name` for TYPE definitions
- `udt_array_fields` — set of field names that are arrays inside TYPEs
- `symbols` — `SymbolTable` instance
- `typecheck` — bool, whether `$TYPECHECK ON` is active
- `apptype` — string: `'GUI'`, `'CONSOLE'`, or `'CGI'`
- `_current_function_name` — tracks current FUNCTION name for `EXIT FUNCTION` → `return <name>`

**Generated Python preamble:**
```python
from rp_runtime.builtins import *
from rp_runtime.gui import *          # Omitted if $APPTYPE CONSOLE
from rp_runtime.database import *
from rp_runtime.network import *
from rp_runtime.pycomponents import *
# + any user IMPORT statements
```

**Name intercepts:** Many BASIC function names conflict with Python builtins. The codegen maps them:
```
str → str_func, dir → dir_func, format → format_func, input → input_func,
delete → delete_func, sleep → sleep_func, hex → hex_func, bin → bin_func,
oct → oct_func, round → round_func, insert → insert_func, replace → replace_func,
reverse → reverse_func, field → field_func, mkdir → mkdir_func, rmdir → rmdir_func,
kill → kill_func, rename → rename_func, messagebox → messagebox_func,
run → run_func, end → end_func, floor → floor_func, command → command_func,
date → date_func,  varptr$ → varptr_str
```

**Special identifier mappings:**
- `TRUE` → `True`, `FALSE` → `False`
- `DATE$` → `date_func()`, `TIME$` → `time_func()`, `TIMER` → `timer()`
- `COMMAND$` → `command_func()`, `DIR$` → `dir_func()`

**Zero-argument method auto-call:** Some method names are detected and `()` is appended if accessed without parentheses: `fetchrow`, `fetchfield`, `close`, `showmodal`, `clear`, `show`, `center`, `cls`, `paint`, `update`, `refresh`.

**FOR loop generation:** Uses `while` loop pattern instead of Python `for/range` to correctly handle:
- Inclusive end bounds (BASIC: `FOR I=1 TO 10` includes 10)
- Negative STEP values
- Float STEPs

**GUI component type maps:** There are TWO `gui_types` dictionaries (one in `visit_DimStatementNode` around line 764, one in `visit_CreateStatementNode` around line 1266). **Both must be updated** when adding new component types.

**The `visit_FunctionCallNode` array-indexing fix (critical):**
```python
# 1. Check explicit arrays set
if name in self.arrays:
    return f"{name}[{idx}]"

# 2. Check symbol table for known variables being indexed
sym = self.symbols.lookup(name)
if sym and sym.get('kind') in ('variable', 'array', 'component') and node.args:
    return f"{name}[{idx}]"

# 3. Otherwise, emit as function call
return f"{target}({args})"
```

### 5.5 Preprocessor (`compiler/preprocessor.py`)

**190 lines.** Pure text-based preprocessing before lexing.

Key features:
- Recursive `$INCLUDE` with circular-include detection (via `include_stack`)
- Nested `$IFDEF`/`$IFNDEF` with skip stack
- `$MACRO` with optional parameters — expanded before `$DEFINE` substitution
- Line-number preservation (consumed directives → empty lines)

### 5.6 Error System (`compiler/errors.py`)

**104 lines.** Three classes:
- `RapidPSyntaxError(RapidPError)` — raised immediately by lexer/parser
- `RapidPCompileError(RapidPError)` — collected by `ErrorCollector`
- `RapidPWarning` — non-fatal, collected

`ErrorCollector` accumulates errors/warnings and can output as text or JSON (for IDE).

### 5.7 Symbol Table

Located in `codegen.py`. Scoped stack of dictionaries.

```python
class SymbolTable:
    _scopes = [{}]           # Stack; index 0 = global
    sub_signatures = {}       # name → param_count
    func_signatures = {}      # name → param_count
    const_names = set()
```

Each symbol entry: `{'type': str, 'kind': str, 'component_type': str|None}`

`kind` values: `'variable'`, `'array'`, `'component'`, `'constant'`, `'parameter'`, `'function'`, `'sub'`, `'module'`, `'function_result'`

### 5.8 Component Registry

`COMPONENT_REGISTRY` in `codegen.py` — dict mapping component type (uppercase) → `{props, methods, events}` sets. Used for semantic validation (warnings for unknown properties, not errors).

Covers 40+ component types including: `PFORM`, `PBUTTON`, `PLABEL`, `PEDIT`, `PCANVAS`, `PPANEL`, `PTIMER`, `PSTRINGGRID`, `PIMAGE`, `PCODEEDITOR`, `PMYSQL`, `PSQLITE`, `PSOCKET`, `PSERVERSOCKET`, `PHTTP`, `PNUMPY`, `PMATPLOTLIB`, `PPANDAS`, `PDESIGNSURFACE`, etc.

---

## 6. Runtime Library

All runtime modules are in `rp_runtime/` and are imported via `from rp_runtime.<module> import *`.

### 6.1 Builtins (`rp_runtime/builtins.py`)

**825 lines.** 100+ functions implementing BASIC string, math, file I/O, and system operations.

**CRITICAL: `len()` function:** `def len(var): return builtins.len(str(var))` — converts to string first! This means `len(python_list)` returns the string length of the list representation, NOT the list length. Use `.size` for PNumPy arrays or Python's `builtins.len()` for real list length.

**File I/O system:** Uses a global `_file_handles` dict mapping file numbers to file objects. Functions: `open_func()`, `close_func()`, `print_hash()`, `line_input()`, `eof()`, `lof()`, `seek()`, `freefile()`.

**Console emulation:** `PEEK`/`POKE` work on a 80×25 `_screen_buffer` array. `LOCATE`, `COLOR`, `CLS` manipulate console state. `CSRLIN`/`POS` return cursor position.

### 6.2 GUI (`rp_runtime/gui.py`)

**3235 lines.** The largest runtime file. Implements 49+ Tkinter-based GUI components.

**Class hierarchy:**
```
PObject → PWidget → PForm, PButton, PLabel, PEdit, PPanel, ...
PObject → PTimer, PFont, PIcon, PMainMenu, PMenuItem, ...
PObject → PCanvas, PImage (special drawing surfaces)
PObject → PStringGrid, PListView, PTreeView (data displays)
```

**Event binding pattern:**
```python
@property
def onclick(self): return self._onclick
@onclick.setter
def onclick(self, handler):
    self._onclick = handler
    if self._widget:
        self._widget.bind("<Button-1>", lambda e: handler())
```

**Parent-child relationship:** Components accept `parent=` in constructor. Visual components create their Tkinter widget in `_build_widget()`, called from constructor or when parent is set.

### 6.3 Database (`rp_runtime/database.py`)

**361 lines.** `PMySQL` (pymysql) and `PSQLite` (sqlite3) with identical-ish interfaces.

Both support: `connect`/`open`/`close`, `query`, `fetchrow`/`fetchfield`, `rowcount`/`colcount`, `sql` property (sets query text), event callbacks.

### 6.4 Network (`rp_runtime/network.py`)

**323 lines.** `PSocket`, `PServerSocket`, `PHTTP`.

- `PSocket` — TCP client with optional SSL, event-driven I/O
- `PServerSocket` — threaded TCP server, per-client management, `broadcast()`
- `PHTTP` — HTTP GET/POST via urllib

### 6.5 PyComponents (`rp_runtime/pycomponents.py`)

**419 lines.** `PNumPy`, `PMatPlotLib`, `PPandas`.

- **PNumPy:** Wraps numpy arrays. Key: `.data` property (get/set raw array), `.size`, `.tolist()`, `.arange()`, `.linspace()`, `.sum()`, `.mean()`, `.std()`, `.dot()`, `.save()`/`.load()`.
  - **Class methods:** `PNumPy.sin()`, `PNumPy.cos()`, `PNumPy.array()`, `PNumPy.random.*` — these are accessed as static-like calls from RapidP code.
- **PMatPlotLib:** Wraps matplotlib. `.plot()`, `.bar()`, `.scatter()`, `.hist()`, `.pie()`, `.saveto_buffer()`, `.savetofile()`. The `.saveto_buffer()` returns a `BytesIO` for `PImage.loadfromplot()`.
- **PPandas:** Wraps pandas DataFrames. `.loadfromcsv()`, `.savetocsv()`, `.sort()`, `.filter()`, `.groupby()`, `.describe`, `.cell()`, `.setcell()`, `.columns`, `.rowcount`, `.colcount`.

---

## 7. Code Generation Patterns

### How a DIM becomes Python
```basic
DIM x AS INTEGER        →  x = 0
DIM s AS STRING         →  s = ""
DIM f AS PForm          →  f = PForm()         (or f = None if later CREATE'd)
DIM a(10) AS DOUBLE     →  a = [0] * (10 + 1)
DIM p AS PersonType     →  p = PersonType()
```

### How a CREATE block becomes Python
```basic
CREATE Form1 AS PForm           →  form1 = PForm()
    Caption = "Test"            →  form1.caption = "Test"
    CREATE Btn AS PButton       →  btn = PButton(parent=form1)
        Caption = "OK"          →  btn.caption = "OK"
    END CREATE
END CREATE
```

### How a SUB becomes Python
```basic
SUB Foo(x AS INTEGER)           →  def foo(x):
    DIM local AS STRING         →      global <all_globals_except_x>
    local = "hello"             →      local = ""
    PRINT local                 →      local = "hello"
END SUB                         →      rp_print(local)
```

### How a FUNCTION becomes Python
```basic
FUNCTION Add(a AS INTEGER, b AS INTEGER) AS INTEGER
    Add = a + b
END FUNCTION
→
def add(a, b):
    global <globals_except_a_b_add>
    add = None
    add = (a + b)
    return add
```

### How FOR loops work
```basic
FOR i = 1 TO 10 STEP 2         →  i = 1
    PRINT i                     →  while i <= 10:
NEXT i                          →      rp_print(i)
                                →      i += 2
```

---

## 8. Known Limitations & Gotchas

### Language Limitations
1. **No `[`, `]`, `{`, `}` in source code.** The lexer rejects these characters. Cannot use Python list/dict literals directly. Workaround: use component methods or `IMPORT`.
2. **`len()` converts to string first.** `LEN(myList)` returns `builtins.len(str(myList))`, not the list length. Use `.size` for PNumPy or access Python's `builtins.len()` via IMPORT.
3. **Array/function ambiguity.** `foo(i)` in expressions is always parsed as `FunctionCallNode`. The codegen resolves it via symbol table lookup. If a variable isn't in the symbol table (e.g., returned from a method, stored in VARIANT), it may be incorrectly emitted as a function call.
4. **All identifiers are lowercased.** `MyVar` and `MYVAR` are the same variable. Case-sensitive Python code may break if relying on case differences.
5. **No multi-line string literals.** Strings must be on a single line.
6. **No lambda/anonymous functions.** Use `CODEPTR(SubName)` for function references.
7. **GOTO/GOSUB recognized but not implemented** in codegen.
8. **Single `=` for both assignment and comparison.** Context determines meaning (statement = assignment, expression = comparison).

### Compiler Gotchas
1. **Two `gui_types` dictionaries** in codegen.py (~line 764 and ~line 1266). Both must be updated when adding components.
2. **Known builtins list appears THREE times** in codegen.py: `_all_known_builtins` frozenset, and inline lists in `visit_CallStatementNode` and `visit_FunctionCallNode`. All three must be updated when adding builtins.
3. **Pre-pass ordering matters.** UDTs are collected first, then globals/arrays/consts, then SUB/FUNCTION signatures, then directives. Changing this order can break symbol resolution.
4. **VARIANT type default is `None`**, but `DIM x AS VARIANT` then `x = some_list` makes `x` a Python list. The `len()` issue above then applies.
5. **String suffix stripping** — `LEFT$()` becomes `left()`, `STR$()` becomes `str_func()`.

### Runtime Gotchas
1. **Tkinter root window.** `builtins.py` creates a hidden `tk.Tk()` root on first `showmessage()` call. GUI components in `gui.py` may also create one. Multiple roots can cause issues.
2. **Global statement in SUBs/FUNCTIONs.** Every global variable is declared `global` in every SUB/FUNCTION. This can be verbose but is correct for RapidP's flat scoping model.
3. **PImage.loadfromplot(plt)** — expects a `PMatPlotLib` instance; calls `plt.saveto_buffer()` internally.
4. **PStringGrid.AddRow** — takes variable positional string args. Column count must be set first.

---

## 9. How to Add New Features

### Adding a New GUI Component
1. **`rp_runtime/gui.py`** — Create class inheriting `PWidget` (visual) or `PObject` (non-visual)
2. **`compiler/codegen.py`** — Add to BOTH `gui_types` dicts (~line 764 and ~line 1266)
3. **`compiler/codegen.py`** — Add to `COMPONENT_REGISTRY` with props, methods, events
4. **Add lowercase alias** at bottom of `gui.py`: `pnewcomp = PNewComp`
5. **Add tests** in `tests/test_gui.py`

### Adding a New Builtin Function
1. **`rp_runtime/builtins.py`** — Implement the function
2. **`compiler/codegen.py`** — If name conflicts with Python builtin, add to `intercepts` dict in BOTH `visit_CallStatementNode` and `visit_FunctionCallNode`
3. **`compiler/codegen.py`** — Add to `_all_known_builtins` frozenset AND the inline `known_builtins` lists in BOTH call/function visit methods
4. **Add tests** in `tests/test_builtins.py` or `tests/test_builtins_extended.py`

### Adding a New Keyword
1. **`compiler/lexer.py`** — Add to `TokenType` enum AND `KEYWORDS` dict
2. **`compiler/parser.py`** — Add parsing logic in `parse_statement()` or relevant method
3. **`compiler/ast_nodes.py`** — Create new `*Node` dataclass if needed
4. **`compiler/codegen.py`** — Add `visit_*Node` method

### Adding a New Preprocessor Directive
1. **`compiler/preprocessor.py`** — Add handling in the main loop
2. If it needs codegen awareness, pass it through as `DirectiveNode` and handle in `_process_directive()`

---

## 10. Test Suite

**170+ tests** in `tests/` directory, run via:
```bash
python3 -m pytest tests/ -q
```

| File | Covers |
|------|--------|
| `test_lexer.py` | Token types, keywords, operators, directives, literals |
| `test_parser.py` | AST generation for all constructs |
| `test_codegen.py` | Code generation, component types, $APPTYPE |
| `test_codegen_extended.py` | Extended codegen: UDTs, FUNCTION, EXIT, SELECT |
| `test_builtins.py` | Core builtin functions |
| `test_builtins_extended.py` | Phase 2-3 builtins |
| `test_directives.py` | $DEFINE, $IFDEF, $MACRO, line preservation |
| `test_gui.py` | GUI component creation, properties, events |
| `test_gui_integration.py` | Full GUI integration tests |
| `test_network.py` | PSocket, PServerSocket, PHTTP |
| `test_pycomponents.py` | PNumPy, PMatPlotLib, PPandas |

**Known failure:** `test_lexer.py::TestLexer::test_directives` — assertion expects specific directive value parsing that doesn't match current implementation. Pre-existing, not a regression.

---

*End of manual. Keep this file updated as the compiler evolves.*
