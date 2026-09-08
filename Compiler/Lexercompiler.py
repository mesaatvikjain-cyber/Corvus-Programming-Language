#========================================
# TOKENIZE THE CODE
#========================================
import re
# This the lexer it breaks the code up into "Tokens" or small keywords which are recognized by next steps of the interpreter
# Tokens have three parts
# type= what kind of token it is (e.g., 'KEYWORD', 'NUMBER', 'IDENTIFIER').
# value= The actual text matched from the code (e.g., 'set', '42', 'age').
# line and column= The location in the source code, so your error messages can point to the exact spot where a bug happened.
from dataclasses import dataclass

@dataclass
class Token:
    type: str
    value: str
    line: int = 1
    column: int = 1

RULES = [
    # Comments: ?{ ... }, // ..., # ...
    ('COMMENT',    r'\?\{[\s\S]*?\}|//[^\n]*|#[^\n]*'),

    # Whitespace
    ('NEWLINE',    r'\n'),
    ('SKIP',       r'[ \t\r]+'),

    # Literals
    ('NUMBER',     r'\d+(\.\d+)?'),
    ('STRING',     r'"[^"\n]*"'),

    # Keywords (control flow, declarations, boolean literals)
    ('KEYWORD',    r'\b(set|const|mk|givout|if|elsif|else|for|in|while|brk|con|try|error|final|true|fal|null|and|or|not|xor|async|awt|cls|global|pass|get|input|match|case)\b'),


    # Data Types (used in `set type; name = ...`)
    ('TYPE',       r'\b(int|flo|str|bool|lis|tup|dic|func|lmb)\b'),

    # Compound brackets & operators (must come before single symbols)
    ('TUP_OPEN',   r'\(\['),
    ('TUP_CLOSE',  r'\]\)'),
    ('FAT_ARROW',  r'=>'),
    ('PIPELINE',   r'\|>'),
    ('SAFE_NAV',   r'\?\.'),

    ('NULL_COAL',  r'\?\?'),
    ('POWER',      r'\*\*'),
    ('EQ',         r'=='),
    ('NEQ',        r'!='),
    ('LTE',        r'<='),
    ('GTE',        r'>='),

    # Single-character operators & punctuation
    ('ASSIGN',     r'='),
    ('PLUS',       r'\+'),
    ('MINUS',      r'-'),
    ('STAR',       r'\*'),
    ('SLASH',      r'/'),
    ('MOD',        r'%'),
    ('LT',         r'<'),
    ('GT',         r'>'),
    ('DOT',        r'\.'),
    ('COLON',      r':'),
    ('SEMI',       r';'),
    ('COMMA',      r','),
    ('LBRACKET',   r'\['),
    ('RBRACKET',   r'\]'),
    ('LBRACE',     r'\{'),
    ('RBRACE',     r'\}'),
    ('LPAREN',     r'\('),
    ('RPAREN',     r'\)'),

    # Identifiers (variable, function, parameter names)
    ('ID',         r'[A-Za-z_][A-Za-z0-9_]*'),

    # Catch-all
    ('MISMATCH',   r'.'),
]


def tokenize(code: str):
    # Combine patterns into a single master regex with named groups
    master_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in RULES)

    tokens = []
    line_num = 1
    line_start = 0

    for match in re.finditer(master_regex, code):
        kind = match.lastgroup
        value = match.group()
        column = match.start() - line_start + 1

        if kind == 'NEWLINE':
            line_num += 1
            line_start = match.end()
            continue
        elif kind == 'SKIP':
            continue
        elif kind == 'COMMENT':
            # Comments can span multiple lines, so count any newlines inside them
            line_num += value.count('\n')
            if '\n' in value:
                line_start = match.end() - (len(value) - value.rfind('\n') - 1)
            continue
        elif kind == 'MISMATCH':
            raise SyntaxError(f"Unexpected character '{value}' at line {line_num}, column {column}")

        tokens.append(Token(type=kind, value=value, line=line_num, column=column))


    return tokens

