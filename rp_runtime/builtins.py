import sys
import os
import glob
import math
import random
import builtins
import tkinter as tk
from tkinter import messagebox
import platform
import array
import time
import datetime
import re

try:
    import pygame
except ImportError:
    pygame = None

try:
    import winsound
except ImportError:
    winsound = None

_tk_root = None

def get_tk_root():
    global _tk_root
    if _tk_root is None:
         _tk_root = tk.Tk()
         _tk_root.withdraw()
    return _tk_root

def showmessage(msg: str):
    get_tk_root()
    messagebox.showinfo("Message", str(msg))

def msgbox(prompt, title="Message", flags=0):
    """Display a message box.
    
    Args:
        prompt: Message text
        title: Window title
        flags: 0=OK only, 1=Yes/No, 2=Retry/Cancel
        
    Returns:
        1 for OK/Yes/Retry, 0 for No/Cancel
    """
    if flags == 1:
        result = messagebox.askyesno(title, prompt)
        return 1 if result else 0
    elif flags == 2:
        result = messagebox.askretrycancel(title, prompt)
        return 1 if result else 0
    else:
        messagebox.showinfo(title, prompt)
        return 1

def rp_print(*args, **kwargs):
    """Replacement for RapidP PRINT statement."""
    print(*args, **kwargs)

# String functions
def chr(ascii_val):
    """CHR$ in RapidP"""
    return builtins.chr(int(ascii_val))

def asc(string_val):
    """ASC in RapidP"""
    if not string_val:
        return 0
    return ord(str(string_val)[0])

def left(string_val, n):
    """LEFT$ in RapidP"""
    return str(string_val)[:int(n)]

def right(string_val, n):
    """RIGHT$ in RapidP"""
    s = str(string_val)
    n = int(n)
    if n <= 0: return ""
    return s[-n:]

def mid(string_val, start, length=None):
    """MID$ in RapidP. Note: RapidP strings are 1-indexed!"""
    s = str(string_val)
    start = int(start) - 1 # 1-based to 0-based
    if start < 0: start = 0
    
    if length is None:
        return s[start:]
    else:
        return s[start:start + int(length)]

def len(var):
    """LEN in RapidP"""
    return builtins.len(str(var))

def instr(start, string_val, substring=None):
    """INSTR in RapidP. Can be INSTR(string, substring) or INSTR(start, string, substring)"""
    if substring is None:
         substring = string_val
         string_val = start
         start = 1
         
    s = str(string_val)
    sub = str(substring)
    start = int(start) - 1
    
    pos = s.find(sub, start)
    if pos == -1: return 0
    return pos + 1 # 1-based index

def ucase(string_val):
    return str(string_val).upper()

def lcase(string_val):
    return str(string_val).lower()

def val(string_val):
    """VAL in RapidP: converts string to number."""
    s = str(string_val).strip()
    if not s: return 0
    try:
        if '.' in s or 'e' in s.lower():
            return float(s)
        return int(s)
    except ValueError:
        return 0

def str_func(number_val):
    """STR$ in RapidP: converts number to string."""
    return str(number_val)

# Math functions
def abs(number_val):
    return builtins.abs(number_val)

def atn(number_val):
    return math.atan(number_val)

def cos(number_val):
    return math.cos(number_val)

def sin(number_val):
    return math.sin(number_val)

def exp(number_val):
    return math.exp(number_val)

def log(number_val):
    """LOG in Basic is usually Natural Logarithm ln()"""
    return math.log(number_val)

def sqr(number_val):
    return math.sqrt(number_val)

def rnd(upper_bound=None):
    if upper_bound is not None:
        return random.randint(0, int(upper_bound) - 1)
    return random.random()

def timer():
    import time
    return time.time()

# Console Input
def input_func(prompt=""):
    """INPUT in RapidP"""
    return input(prompt)

# Extra String Functions
def space(n):
    return " " * int(n)

def string(n, char):
    c = char if isinstance(char, str) else builtins.chr(int(char))
    return c[0] * int(n)

def ltrim(s):
    return str(s).lstrip()

def rtrim(s):
    return str(s).rstrip()

def trim(s):
    return str(s).strip()

def hex_func(n):
    return builtins.hex(int(n))[2:].upper()

def oct_func(n):
    return builtins.oct(int(n))[2:]

def bin_func(n):
    return builtins.bin(int(n))[2:]

# File I/O (simplistic simulated RapidP globals for #1, #2 handles)
_file_handles = {}

def open_func(filename, mode, file_num):
    # E.g OPEN "file.txt" FOR INPUT AS #1
    py_mode = 'r'
    if 'output' in mode.lower(): py_mode = 'w'
    elif 'append' in mode.lower(): py_mode = 'a'
    elif 'binary' in mode.lower(): py_mode = 'rb'
    
    _file_handles[file_num] = builtins.open(filename, py_mode)

def close_func(file_num):
    if file_num in _file_handles:
        _file_handles[file_num].close()
        del _file_handles[file_num]

def print_hash(file_num, *args):
    if file_num in _file_handles:
        print(*args, file=_file_handles[file_num])

# Constants (clred, true, false, etc)
true = True
false = False
true_val = True
false_val = False
vttrue = True
vtfalse = False

clblack = 0x000000
clmaroon = 0x000080
clgreen = 0x008000
clolive = 0x008080
clnavy = 0x800000
clpurple = 0x800080
clteal = 0x808000
clgray = 0x808080
clsilver = 0xC0C0C0
clred = 0x0000FF
cllime = 0x00FF00
clyellow = 0x00FFFF
clblue = 0xFF0000
clfuchsia = 0xFF00FF
claqua = 0xFFFF00
clwhite = 0xFFFFFF

def environ(var_name):
    import os
    return os.environ.get(str(var_name), "")

def command_func():
    import sys
    return " ".join(sys.argv[1:])

def curdir():
    import os
    return os.getcwd()

# Advanced Builtins Added from Docs Phase 17
def chdir(path):
    try:
        os.chdir(path)
    except:
        pass

def direxists(path):
    return 1 if os.path.exists(path) and os.path.isdir(path) else 0

_dir_iterator = None

def dir_func(pattern="*.*", attrib=0):
    global _dir_iterator
    if pattern != "":
        # Initial call
        if pattern == "*.*": pattern = "*"
        try:
             files = glob.glob(pattern)
             _dir_iterator = iter(files)
        except:
             return ""
    
    if _dir_iterator is not None:
         try:
             return next(_dir_iterator)
         except StopIteration:
             _dir_iterator = None
             return ""
    return ""

def ceil(n):
    return math.ceil(float(n))

def acos(n):
    return math.acos(float(n))

def asin(n):
    return math.asin(float(n))

# Phase 18 System and String Additions
def date_func():
    import datetime
    return datetime.date.today().strftime('%m-%d-%Y')

def time_func():
    import datetime
    return datetime.datetime.now().strftime('%H:%M:%S')

def delete_func(s, start, count):
    # RapidP DELETE$ removing characters. 1-indexed.
    s = str(s)
    start = int(start) - 1
    if start < 0: start = 0
    count = int(count)
    return s[:start] + s[start+count:]

def format_func(s, val):
    # Basic standard Python format as fallback
    try:
         # RapidP uses FORMAT$("#.##", val). We simplify.
         if isinstance(val, float):
              return f"{val:.2f}"
         return str(val)
    except:
         return str(val)

def hextodec(h):
    h = str(h).upper()
    if h.startswith('&H'): h = h[2:]
    if h.startswith('0X'): h = h[2:]
    try:
         return int(h, 16)
    except:
         return 0

def callback(ptr):
    return ptr

def callfunc(ptr, *args):
    if callable(ptr):
         return ptr(*args)
    return 0

def varptr(var):
    return id(var)

def varptr_str(var):
    return builtins.hex(id(var))[2:].upper()

def vartype(var):
    if isinstance(var, int): return 2
    if isinstance(var, float): return 5
    if isinstance(var, str): return 8
    return 0

def sound(freq, duration=1000):
    freq = int(freq)
    duration = int(duration)
    try:
        if pygame:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=1024)
            sample_rate = 44100
            duration_sec = duration / 1000.0
            n_samples = int(duration_sec * sample_rate)
            buf = array.array('h')
            factor = float(freq) * 2.0 * math.pi / sample_rate
            for i in range(n_samples):
                buf.append(int(math.sin(i * factor) * 32767))
            snd = pygame.mixer.Sound(buffer=buf)
            snd.play()
            pygame.time.wait(duration)
            return
    except Exception:
        pass
    # Fallback paths
    if platform.system() == "Windows" and winsound:
        winsound.Beep(freq, duration)
    elif platform.system() == "Darwin":
        import subprocess as _sp
        # Generate tone with sox (brew install sox) or use say as last resort
        try:
            _sp.run(["play", "-nq", "-t", "alsa", "synth", str(duration / 1000.0), "sine", str(freq)],
                    capture_output=True, timeout=duration / 1000.0 + 2)
        except (FileNotFoundError, _sp.TimeoutExpired):
            os.system("printf '\a'")
    else:
        print("\a")

def beep(freq=800, duration=200):
    """BEEP: play a short beep tone."""
    sound(freq, duration)

def sleep_func(ms):
    time.sleep(float(ms) / 1000.0)

def shell(command):
    """Execute a shell command (RapidP SHELL equivalent)."""
    import subprocess
    subprocess.Popen(str(command), shell=True)

def shellwait(command):
    """Execute a shell command and wait for completion. Returns exit code."""
    import subprocess
    result = subprocess.run(str(command), shell=True)
    return result.returncode

def fileexists(filename):
    """Check if a file exists (RapidP FILEEXISTS equivalent)."""
    return os.path.isfile(str(filename))

# ── Phase 3: Missing Built-in Functions ──

# Math
def tan(n):
    return math.tan(float(n))

def floor_func(n):
    return int(math.floor(float(n)))

def fix(n):
    """FIX: truncate toward zero (like INT but toward zero for negatives)."""
    n = float(n)
    return int(n)

def frac(n):
    """FRAC: return fractional part."""
    n = float(n)
    return n - int(n)

def round_func(n, decimals=0):
    """ROUND: round to specified decimal places."""
    return builtins.round(float(n), int(decimals))

def sgn(n):
    """SGN: returns -1, 0, or 1."""
    n = float(n)
    if n > 0: return 1
    if n < 0: return -1
    return 0

def cint(n):
    """CINT: round to nearest integer."""
    return int(builtins.round(float(n)))

def clng(n):
    """CLNG: round to nearest long integer."""
    return int(builtins.round(float(n)))

def iif(condition, true_val, false_val):
    """IIF: inline if — note both branches are evaluated (matches RapidP)."""
    return true_val if condition else false_val

def randomize(seed=None):
    """RANDOMIZE: seed the random number generator."""
    if seed is not None:
        random.seed(int(seed))
    else:
        random.seed()

# String
def insert_func(s, pos, substr):
    """INSERT$: insert substr into s at 1-based position pos."""
    s = str(s)
    pos = int(pos) - 1
    if pos < 0: pos = 0
    return s[:pos] + str(substr) + s[pos:]

def replace_func(s, old, new):
    """REPLACE$: replace all occurrences of old with new in s."""
    return str(s).replace(str(old), str(new))

def replacesubstr(s, old, new):
    """REPLACESUBSTR$: alias for REPLACE$."""
    return str(s).replace(str(old), str(new))

def reverse_func(s):
    """REVERSE$: reverse a string."""
    return str(s)[::-1]

def rinstr(s, substr):
    """RINSTR: find last occurrence of substr in s (1-based, 0 if not found)."""
    s = str(s)
    sub = str(substr)
    pos = s.rfind(sub)
    if pos == -1: return 0
    return pos + 1

def field_func(s, delimiter, n):
    """FIELD$: return the nth field (1-based) from s split by delimiter."""
    parts = str(s).split(str(delimiter))
    n = int(n)
    if n < 1 or n > builtins.len(parts):
        return ""
    return parts[n - 1]

def tally(s, substr):
    """TALLY: count occurrences of substr in s."""
    return str(s).count(str(substr))

def strf(val):
    """STRF$: convert number to string (same as STR$)."""
    return str(val)

def convbase(num_str, from_base, to_base):
    """CONVBASE$: convert a number string from one base to another."""
    from_base = int(from_base)
    to_base = int(to_base)
    try:
        decimal_val = int(str(num_str), from_base)
    except ValueError:
        return ""
    if to_base == 10:
        return str(decimal_val)
    elif to_base == 16:
        return builtins.hex(decimal_val)[2:].upper()
    elif to_base == 8:
        return builtins.oct(decimal_val)[2:]
    elif to_base == 2:
        return builtins.bin(decimal_val)[2:]
    else:
        digits = []
        n = builtins.abs(decimal_val)
        if n == 0:
            return "0"
        while n > 0:
            digits.append("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"[n % to_base])
            n //= to_base
        if decimal_val < 0:
            digits.append('-')
        return ''.join(reversed(digits))

# File/Dir
def mkdir_func(path):
    """MKDIR: create a directory."""
    os.makedirs(str(path), exist_ok=True)

def rmdir_func(path):
    """RMDIR: remove a directory."""
    os.rmdir(str(path))

def kill_func(filename):
    """KILL: delete a file."""
    os.remove(str(filename))

def rename_func(old_name, new_name):
    """RENAME: rename a file."""
    os.rename(str(old_name), str(new_name))

# Array helpers
def lbound(arr):
    """LBOUND: lower bound of array (always 0 in Python)."""
    return 0

def ubound(arr):
    """UBOUND: upper bound of array."""
    if isinstance(arr, (list, tuple)):
        return builtins.len(arr) - 1
    return 0

def quicksort(arr):
    """QUICKSORT: sort an array in place."""
    if isinstance(arr, list):
        arr.sort()

def initarray(arr, *values):
    """INITARRAY: initialize array with values."""
    if isinstance(arr, list):
        arr.clear()
        arr.extend(values)

# System
def doevents():
    """DOEVENTS: process pending GUI events."""
    try:
        if _tk_root is not None:
            _tk_root.update()
    except Exception:
        pass

def playwav(filename, flags=0):
    """PLAYWAV: play a WAV file."""
    filename = str(filename)
    try:
        if platform.system() == "Darwin":
            import subprocess
            subprocess.Popen(["afplay", filename])
        elif platform.system() == "Windows" and winsound:
            winsound.PlaySound(filename, winsound.SND_FILENAME | winsound.SND_ASYNC)
        elif pygame:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()
    except Exception:
        pass

def rgb(r, g, b):
    """RGB: create a BGR color integer (RapidP uses BGR byte order)."""
    return (int(b) << 16) | (int(g) << 8) | int(r)

def messagebox_func(hwnd, text, caption, flags=0):
    """MESSAGEBOX: Windows-style message box. Returns button ID."""
    get_tk_root()
    flags = int(flags)
    # MB_OK=0, MB_OKCANCEL=1, MB_YESNO=4, MB_YESNOCANCEL=3
    if flags == 4:  # MB_YESNO
        result = messagebox.askyesno(str(caption), str(text))
        return 6 if result else 7  # IDYES=6, IDNO=7
    elif flags == 1:  # MB_OKCANCEL
        result = messagebox.askokcancel(str(caption), str(text))
        return 1 if result else 2  # IDOK=1, IDCANCEL=2
    elif flags == 3:  # MB_YESNOCANCEL
        result = messagebox.askyesnocancel(str(caption), str(text))
        if result is True: return 6
        if result is False: return 7
        return 2  # IDCANCEL
    else:  # MB_OK
        messagebox.showinfo(str(caption), str(text))
        return 1

def messagedlg(text, dlg_type=0, buttons=0, help_ctx=0):
    """MESSAGEDLG: Delphi-style message dialog."""
    get_tk_root()
    messagebox.showinfo("Message", str(text))
    return 1

def run_func(command):
    """RUN: execute a program."""
    import subprocess
    subprocess.Popen(str(command), shell=True)

def end_func():
    """END: terminate the program."""
    sys.exit(0)

# Constants for MESSAGEBOX
MB_OK = 0
MB_OKCANCEL = 1
MB_ABORTRETRYIGNORE = 2
MB_YESNOCANCEL = 3
MB_YESNO = 4
MB_RETRYCANCEL = 5
IDOK = 1
IDCANCEL = 2
IDABORT = 3
IDRETRY = 4
IDIGNORE = 5
IDYES = 6
IDNO = 7

# Key constants
VK_LEFT = 37
VK_UP = 38
VK_RIGHT = 39
VK_DOWN = 40
VK_RETURN = 13
VK_ESCAPE = 27
VK_SPACE = 32
VK_TAB = 9
VK_DELETE = 46
VK_BACK = 8
VK_F1 = 112
VK_F2 = 113
VK_F3 = 114
VK_F4 = 115
VK_F5 = 116
VK_F6 = 117
VK_F7 = 118
VK_F8 = 119
VK_F9 = 120
VK_F10 = 121
VK_F11 = 122
VK_F12 = 123

# ── Console Screen Buffer (PEEK/POKE emulation) ──
_SCREEN_WIDTH = 80
_SCREEN_HEIGHT = 25
_screen_buffer = {}  # (row, col) -> (char, fg, bg)
_cursor_row = 1
_cursor_col = 1
_current_fg = 7
_current_bg = 0

def peek(address):
    """PEEK: read from console screen buffer. Address = row*256 + col."""
    row = (address >> 8) & 0xFF
    col = address & 0xFF
    cell = _screen_buffer.get((row, col), (' ', _current_fg, _current_bg))
    return ord(cell[0])

def poke(address, value):
    """POKE: write to console screen buffer. Address = row*256 + col."""
    global _screen_buffer
    row = (address >> 8) & 0xFF
    col = address & 0xFF
    _screen_buffer[(row, col)] = (builtins.chr(value & 0xFF), _current_fg, _current_bg)

def locate(row=None, col=None):
    """LOCATE: set cursor position (1-based)."""
    global _cursor_row, _cursor_col
    if row is not None:
        _cursor_row = int(row)
    if col is not None:
        _cursor_col = int(col)

def color(fg=None, bg=None):
    """COLOR: set foreground and background colors."""
    global _current_fg, _current_bg
    if fg is not None:
        _current_fg = int(fg)
    if bg is not None:
        _current_bg = int(bg)

def cls():
    """CLS: clear the console screen buffer."""
    global _screen_buffer, _cursor_row, _cursor_col
    _screen_buffer = {}
    _cursor_row = 1
    _cursor_col = 1

def csrlin():
    """CSRLIN: return current cursor row."""
    return _cursor_row

def pos_func(dummy=0):
    """POS: return current cursor column."""
    return _cursor_col

def screen_func(row, col, mode=0):
    """SCREEN: return character or color at position."""
    cell = _screen_buffer.get((int(row), int(col)), (' ', _current_fg, _current_bg))
    if mode == 0:
        return ord(cell[0])
    return cell[1]

def pcopy(src_page=0, dst_page=0):
    """PCOPY: copy screen page (no-op in this implementation)."""
    pass

def inkey():
    """INKEY$: non-blocking key read (returns empty string if no key)."""
    return ""

def sizeof(var):
    """SIZEOF: return size of variable in bytes."""
    if isinstance(var, int):
        return 4
    if isinstance(var, float):
        return 8
    if isinstance(var, str):
        return builtins.len(var)
    return sys.getsizeof(var)

def memcpy(dest, src, count):
    """MEMCPY: copy memory (operates on lists/bytearrays)."""
    count = int(count)
    if isinstance(dest, (list, bytearray)) and isinstance(src, (list, bytearray)):
        for i in range(min(count, builtins.len(src), builtins.len(dest))):
            dest[i] = src[i]
    return dest

def memset(dest, value, count):
    """MEMSET: fill memory with a value."""
    value = int(value)
    count = int(count)
    if isinstance(dest, (list, bytearray)):
        for i in range(min(count, builtins.len(dest))):
            dest[i] = value
    return dest

def memcmp(buf1, buf2, count):
    """MEMCMP: compare memory buffers."""
    count = int(count)
    for i in range(count):
        a = buf1[i] if i < builtins.len(buf1) else 0
        b = buf2[i] if i < builtins.len(buf2) else 0
        if a < b:
            return -1
        if a > b:
            return 1
    return 0

def codeptr(func):
    """CODEPTR: return function pointer (id in Python)."""
    return id(func)

def freefile():
    """FREEFILE: return the next available file number."""
    for i in range(1, 256):
        if i not in _file_handles:
            return i
    return 0

def filelen(filename):
    """FILELEN: return file size in bytes."""
    try:
        return os.path.getsize(str(filename))
    except OSError:
        return 0

def eof_func(file_num):
    """EOF: check if at end of file."""
    if file_num in _file_handles:
        f = _file_handles[file_num]
        pos = f.tell()
        f.seek(0, 2)
        end = f.tell()
        f.seek(pos)
        return pos >= end
    return True

def lof(file_num):
    """LOF: return length of open file."""
    if file_num in _file_handles:
        f = _file_handles[file_num]
        pos = f.tell()
        f.seek(0, 2)
        size = f.tell()
        f.seek(pos)
        return size
    return 0

def seek_func(file_num, position):
    """SEEK: set file position (1-based)."""
    if file_num in _file_handles:
        _file_handles[file_num].seek(int(position) - 1)

def line_input(file_num):
    """LINE INPUT: read a line from an open file."""
    if file_num in _file_handles:
        line = _file_handles[file_num].readline()
        if line.endswith('\n'):
            line = line[:-1]
        if line.endswith('\r'):
            line = line[:-1]
        return line
    return ""

def write_hash(file_num, *args):
    """WRITE #n: write comma-separated values to file."""
    if file_num in _file_handles:
        parts = []
        for a in args:
            if isinstance(a, str):
                parts.append('"' + a + '"')
            else:
                parts.append(str(a))
        _file_handles[file_num].write(",".join(parts) + "\n")
