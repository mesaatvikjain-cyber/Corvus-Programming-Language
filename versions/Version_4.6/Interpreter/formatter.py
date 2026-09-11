"""
Corvus Code Formatter (corvus fmt) Engine
Converts arbitrary Corvus source code into clean, canonical styling:
- 4-space indentation
- Canonical brackets [ ... ] spacing
- Normalized operators (a + b, a = b, a @ b)
- Preserved comments
"""

import sys
import os
import re

def format_corvus_code(code: str) -> str:
    lines = code.splitlines()
    formatted_lines = []
    indent_level = 0
    in_block_comment = False

    for raw_line in lines:
        stripped = raw_line.strip()
        
        # Blank lines
        if not stripped:
            formatted_lines.append("")
            continue

        # Check block comments ?{ ... }
        if stripped.startswith("?{") and not stripped.endswith("}"):
            in_block_comment = True
            formatted_lines.append("    " * indent_level + stripped)
            continue
        if in_block_comment:
            formatted_lines.append("    " * indent_level + stripped)
            if "}" in stripped:
                in_block_comment = False
            continue

        # Outdent for closing brackets at line start
        # Check if line starts with closing bracket
        leading_closers = len(re.match(r'^[\]\}\)]+', stripped).group(0)) if re.match(r'^[\]\}\)]+', stripped) else 0
        if leading_closers > 0:
            current_indent = max(0, indent_level - 1)
        else:
            current_indent = indent_level

        # Normalization of common spacing around operators
        line_norm = stripped
        # Keep strings intact by splitting on quotes
        parts = re.split(r'("[^"\n]*"|\'[^\'\n]*\')', line_norm)
        for i in range(0, len(parts), 2):
            p = parts[i]
            # Replace multiple spaces
            p = re.sub(r'[ \t]+', ' ', p)
            # Ensure space before opening bracket if preceded by keyword/paren
            p = re.sub(r'(\))\s*(\[)', r'\1 \2', p)
            # Ensure space after comma
            p = re.sub(r',\s*', ', ', p)
            # Ensure spacing around binary ops: +, -, *, /, %, @, ==, !=, <=, >=, =, |>
            p = re.sub(r'\s*([=+\-*/%@]|==|!=|<=|>=|\|>)\s*', r' \1 ', p)
            # Clean up multi-char ops that got split
            p = p.replace('=  =', '==').replace('!  =', '!=').replace('<  =', '<=').replace('>  =', '>=')
            p = p.replace('|  >', '|>')
            # Semicolon spacing: set int; x
            p = re.sub(r'\s*;\s*', '; ', p)
            parts[i] = p
        line_norm = "".join(parts)

        formatted_lines.append("    " * current_indent + line_norm)

        # Count open vs close brackets to adjust indent for next lines
        # Only count brackets outside of string literals
        code_without_strings = re.sub(r'"[^"\n]*"|\'[^\'\n]*\'', '', stripped)
        opens = code_without_strings.count('[') + code_without_strings.count('{')
        closes = code_without_strings.count(']') + code_without_strings.count('}')
        indent_level = max(0, indent_level + (opens - closes))

    return "\n".join(formatted_lines) + "\n"


def format_file(filepath: str, check_only: bool = False) -> bool:
    if not os.path.exists(filepath):
        print(f"[ERROR] File '{filepath}' not found.")
        return False

    with open(filepath, "r", encoding="utf-8") as f:
        orig = f.read()

    formatted = format_corvus_code(orig)

    if check_only:
        if orig != formatted:
            print(f"[DIFF] {filepath} needs formatting.")
            return False
        else:
            print(f"[OK] {filepath} is cleanly formatted.")
            return True
    else:
        if orig != formatted:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(formatted)
            print(f"[FORMATTED] {filepath}")
        else:
            print(f"[UNCHANGED] {filepath}")
        return True
