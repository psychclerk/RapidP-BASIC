import re
from enum import Enum, auto
from typing import NamedTuple, List
from .errors import RapidPSyntaxError

class TokenType(Enum):
    # Keywords
    DIM = auto()
    AS = auto()
    INTEGER = auto()
    STRING = auto()
    DOUBLE = auto()
    SINGLE = auto()
    BYTE = auto()
    WORD = auto()
    DWORD = auto()
    LONG = auto()
    INT64 = auto()
    CURRENCY = auto()
    POBJECT = auto()
    IF = auto()
    THEN = auto()
    ELSE = auto()
    ELSEIF = auto()
    END = auto()
    FOR = auto()
    TO = auto()
    STEP = auto()
    NEXT = auto()
    WHILE = auto()
    WEND = auto()
    DO = auto()
    LOOP = auto()
    UNTIL = auto()
    SELECT = auto()
    CASE = auto()
    SUB = auto()
    FUNCTION = auto()
    CALL = auto()
    RETURN = auto()
    EXIT = auto()
    PRINT = auto()
    INPUT = auto()
    GOTO = auto()
    GOSUB = auto()
    IMPORT = auto() # Our custom external Python import keyword
    CREATE = auto()
    CONST = auto()
    TYPE = auto()
    DECLARE = auto()
    LIB = auto()
    ALIAS = auto()
    WITH = auto()
    
    # Directives
    DIRECTIVE = auto() # e.g. $APPTYPE, $INCLUDE, $TYPECHECK
    
    # Operators
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    BACKSLASH = auto() # Integer division in BASIC may sometimes be \ 
    CARET = auto() # ^ for exponentiation
    MOD = auto()
    AMPERSAND = auto()
    
    DEFSTR = auto()
    DEFINT = auto()
    DEFBYTE = auto()
    DEFWORD = auto()
    DEFDWORD = auto()
    DEFLONG = auto()
    DEFSNG = auto()
    DEFDBL = auto()
    DEFCUR = auto()
    EXTENDS = auto()
    PROPERTY = auto()
    SET = auto()
    BYVAL = auto()
    BYREF = auto()
    BIND = auto()
    CONSTRUCTOR = auto()
    
    # Relational Operators
    EQ = auto()
    NEQ = auto()
    LT = auto()
    LTE = auto()
    GT = auto()
    GTE = auto()
    
    # Logical Operators
    AND = auto()
    OR = auto()
    NOT = auto()
    XOR = auto()
    
    # Symbols
    LPAREN = auto()
    RPAREN = auto()
    COMMA = auto()
    COLON = auto() # Delimiter for multi-statement lines
    SEMI = auto() # For print formatting
    DOT = auto() # Object member access
    
    # Literals and Identifiers
    IDENTIFIER = auto()
    NUMBER = auto()
    STRING_LIT = auto()
    
    # Special Types
    NEWLINE = auto()
    EOF = auto()

class Token(NamedTuple):
    type: TokenType
    value: str
    line: int
    column: int
    
class Lexer:
    """Tokenizer for RapidP Basic."""
    
    # Keywords mapping (case insensitive)
    KEYWORDS = {
        'DIM': TokenType.DIM,
        'AS': TokenType.AS,
        'INTEGER': TokenType.INTEGER,
        'STRING': TokenType.STRING,
        'DOUBLE': TokenType.DOUBLE,
        'SINGLE': TokenType.SINGLE,
        'BYTE': TokenType.BYTE,
        'WORD': TokenType.WORD,
        'DWORD': TokenType.DWORD,
        'LONG': TokenType.LONG,
        'INT64': TokenType.INT64,
        'CURRENCY': TokenType.CURRENCY,
        'POBJECT': TokenType.POBJECT,
        'IF': TokenType.IF,
        'THEN': TokenType.THEN,
        'ELSE': TokenType.ELSE,
        'ELSEIF': TokenType.ELSEIF,
        'END': TokenType.END,
        'FOR': TokenType.FOR,
        'TO': TokenType.TO,
        'STEP': TokenType.STEP,
        'NEXT': TokenType.NEXT,
        'WHILE': TokenType.WHILE,
        'WEND': TokenType.WEND,
        'DO': TokenType.DO,
        'LOOP': TokenType.LOOP,
        'UNTIL': TokenType.UNTIL,
        'SELECT': TokenType.SELECT,
        'CASE': TokenType.CASE,
        'SUB': TokenType.SUB,
        'FUNCTION': TokenType.FUNCTION,
        'CALL': TokenType.CALL,
        'RETURN': TokenType.RETURN,
        'EXIT': TokenType.EXIT,
        'PRINT': TokenType.PRINT,
        'INPUT': TokenType.INPUT,
        'GOTO': TokenType.GOTO,
        'GOSUB': TokenType.GOSUB,
        'IMPORT': TokenType.IMPORT,
        'CREATE': TokenType.CREATE,
        'CONST': TokenType.CONST,
        'TYPE': TokenType.TYPE,
        'DECLARE': TokenType.DECLARE,
        'LIB': TokenType.LIB,
        'ALIAS': TokenType.ALIAS,
        'WITH': TokenType.WITH,
        'EXTENDS': TokenType.EXTENDS,
        'PROPERTY': TokenType.PROPERTY,
        'SET': TokenType.SET,
        'BYVAL': TokenType.BYVAL,
        'BYREF': TokenType.BYREF,
        'BIND': TokenType.BIND,
        'CONSTRUCTOR': TokenType.CONSTRUCTOR,
        'AND': TokenType.AND,
        'OR': TokenType.OR,
        'NOT': TokenType.NOT,
        'XOR': TokenType.XOR,
        'XOR': TokenType.XOR,
        'MOD': TokenType.MOD,
        'DEFSTR': TokenType.DEFSTR,
        'DEFINT': TokenType.DEFINT,
        'DEFBYTE': TokenType.DEFBYTE,
        'DEFWORD': TokenType.DEFWORD,
        'DEFDWORD': TokenType.DEFDWORD,
        'DEFLONG': TokenType.DEFLONG,
        'DEFSNG': TokenType.DEFSNG,
        'DEFDBL': TokenType.DEFDBL,
        'DEFCUR': TokenType.DEFCUR,
    }

    # Built-in suffixes for identifiers in Basic
    # string$, integer%, double#
    
    rules = [
        ('COMMENT',   r"('.*|REM\b.*)"),               # ' comment or REM comment
        ('DIRECTIVE', r'\$[A-Za-z_]+.*'),              # Compiler directives e.g. $APPTYPE CONSOLE
        ('NUMBER',    r'(?:&[Hh][0-9A-Fa-f]+|&[Oo][0-7]+|&[Bb][01]+|\b\d+(?:\.\d*)?(?:[eE][+-]?\d+)?\b)'), # Integer, decimal, hex, octal, binary
        ('STRING_LIT',r'"[^"]*"'),                     # String literal
        ('LINE_CONT', r'_[ \t]*\r?\n'),                # Line continuation (swallowed like WS)
        ('IDENTIFIER',r'[A-Za-z_][A-Za-z0-9_]*[\$%#&!]?'), # Identifiers (variables/functions)
        ('NEQ',       r'<>'),                          # Not equal
        ('LTE',       r'<='),                          # Less than or equal
        ('GTE',       r'>='),                          # Greater than or equal
        ('EQ',        r'='),                           # Equal
        ('LT',        r'<'),                           # Less than
        ('GT',        r'>'),                           # Greater than
        ('PLUS',      r'\+'),                          # Plus
        ('MINUS',     r'-'),                           # Minus
        ('STAR',      r'\*'),                          # Multiply
        ('SLASH',     r'/'),                           # Divide
        ('BACKSLASH', r'\\'),                          # Integer divide
        ('AMPERSAND', r'&'),                           # String Concat
        ('CARET',     r'\^'),                          # Exponent
        ('LPAREN',    r'\('),                          # Left Parenthesis
        ('RPAREN',    r'\)'),                          # Right Parenthesis
        ('COMMA',     r','),                           # Comma
        ('COLON',     r':'),                           # Colon
        ('SEMI',      r';'),                           # Semicolon
        ('DOT',       r'\.'),                          # Dot
        ('WS',        r'[ \t]+'),                      # Whitespace
        ('NEWLINE',   r'\r?\n'),                       # Newline
    ]

    def __init__(self, code: str, file_path: str = None):
        self.code = code
        self.file_path = file_path
        self._build_regex()
        
    def _build_regex(self):
        parts = []
        for name, pattern in self.rules:
            parts.append(f'(?P<{name}>{pattern})')
        self.regex = re.compile('|'.join(parts))

    def tokenize(self) -> List[Token]:
        tokens = []
        line_num = 1
        line_start = 0
        
        for match in self.regex.finditer(self.code):
            kind = match.lastgroup
            value = match.group()
            column = match.start() - line_start + 1
            
            if kind == 'WS' or kind == 'COMMENT' or kind == 'LINE_CONT':
                if kind == 'LINE_CONT':
                    line_start = match.end()
                    line_num += 1
                continue
            elif kind == 'NEWLINE':
                # We emit explicit NEWLINE tokens in Basic since it's statement terminator
                tokens.append(Token(TokenType.NEWLINE, value, line_num, column))
                line_start = match.end()
                line_num += 1
                continue
            elif kind == 'IDENTIFIER':
                upper_val = value.upper()
                if upper_val in self.KEYWORDS:
                    tokens.append(Token(self.KEYWORDS[upper_val], upper_val, line_num, column))
                else:
                    tokens.append(Token(TokenType.IDENTIFIER, value, line_num, column))
            elif kind == 'STRING_LIT':
                # Remove quotes for value
                tokens.append(Token(TokenType.STRING_LIT, value[1:-1], line_num, column))
            elif kind == 'DIRECTIVE':
                tokens.append(Token(TokenType.DIRECTIVE, value, line_num, column))
            elif kind == 'NUMBER':
                val_upper = value.upper()
                if val_upper.startswith('&H'):
                    value = '0x' + value[2:]
                elif val_upper.startswith('&O'):
                    value = '0o' + value[2:]
                elif val_upper.startswith('&B'):
                    value = '0b' + value[2:]
                tokens.append(Token(TokenType.NUMBER, value, line_num, column))
            else:
                # Direct match for operators and symbols
                tokens.append(Token(getattr(TokenType, kind), value, line_num, column))
                
        # Check for un-tokenizable characters
        last_end = 0
        for match in self.regex.finditer(self.code):
            if match.start() > last_end:
                bad_char = self.code[last_end:match.start()]
                if bad_char.strip():
                    raise RapidPSyntaxError(f"Unexpected character: {bad_char}", line_num, match.start() - line_start + 1, self.file_path)
            last_end = match.end()
            
        if last_end < len(self.code):
            bad_char = self.code[last_end:]
            if bad_char.strip():
                 raise RapidPSyntaxError(f"Unexpected character: {bad_char}", line_num, last_end - line_start + 1, self.file_path)
        
        # Add EOF
        # Find final position
        lines = self.code.splitlines(True)
        final_line = len(lines) if lines else 1
        final_col = len(lines[-1]) + 1 if lines else 1
        tokens.append(Token(TokenType.EOF, '', final_line, final_col))
        
        return tokens
