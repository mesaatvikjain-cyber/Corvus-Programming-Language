import sys

# Corvus Enterprise Diagnostic & Call Stack Traceback Engine (v3.1)

class CallFrame:
    def __init__(self, func_name: str, filepath: str, line: int, column: int = 1):
        self.func_name = func_name
        self.filepath = filepath
        self.line = line
        self.column = column


class CorvusError(Exception):
    def __init__(
        self,
        error_type: str,
        message: str,
        line: int = 1,
        col: int = 1,
        token_len: int = 1,
        suggestion: str = "",
        call_stack: list = None
    ):
        self.error_type = error_type
        self.message = message
        self.line = line
        self.col = col
        self.token_len = max(1, token_len)
        self.suggestion = suggestion
        self.call_stack = call_stack or []
        super().__init__(self.message)

    def print_formatted(self, filepath: str, source_code: str):
        lines = source_code.splitlines()
        line_idx = self.line - 1

        divider = "======================================================"
        print(f"\n{divider}", file=sys.stderr)
        print(f"[{self.error_type}]", file=sys.stderr)

        # Print Call Stack Traceback if nested function calls were active
        if self.call_stack:
            print("Call Stack Traceback (most recent call last):", file=sys.stderr)
            for frame in self.call_stack:
                f_name = frame.func_name if hasattr(frame, 'func_name') else str(frame)
                f_line = frame.line if hasattr(frame, 'line') else 1
                f_path = frame.filepath if hasattr(frame, 'filepath') else filepath
                print(f"  --> In function '{f_name}' at {f_path}:{f_line}", file=sys.stderr)
            print("------------------------------------------------------", file=sys.stderr)

        print(f"--> Location: File '{filepath}', Line {self.line}, Column {self.col}:", file=sys.stderr)

        # Multi-line Snippet Context (line before, target line, line after)
        if 0 <= line_idx < len(lines):
            if line_idx > 0:
                print(f"  {self.line - 1:4d} | {lines[line_idx - 1]}", file=sys.stderr)

            target_line = lines[line_idx]
            print(f"  {self.line:4d} | {target_line}", file=sys.stderr)

            # Caret Pointer
            indent = " " * (self.col - 1)
            carets = "^" * self.token_len
            print(f"       | {indent}{carets}", file=sys.stderr)

            if line_idx + 1 < len(lines):
                print(f"  {self.line + 1:4d} | {lines[line_idx + 1]}", file=sys.stderr)

        print(f"\nDetails: {self.message}", file=sys.stderr)
        if self.suggestion:
            print(f"Fix Hint: {self.suggestion}", file=sys.stderr)

        print(f"{divider}\n", file=sys.stderr)