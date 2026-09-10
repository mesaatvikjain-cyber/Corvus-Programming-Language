import sys

class CorvusError(Exception):
    def __init__(self, error_type: str, message: str, line: int = 1, col: int = 1, suggestion: str = ""):
        self.error_type = error_type
        self.message = message
        self.line = line
        self.col = col
        self.suggestion = suggestion
        super().__init__(self.message)

    def print_formatted(self, filepath: str, source_code: str):
        lines = source_code.splitlines()
        offending_line = lines[self.line - 1] if 0 <= self.line - 1 < len(lines) else ""
        pointer = " " * (self.col - 1) + "^"

        divider = "=" * 54
        print(f"\n{divider}", file=sys.stderr)
        print(f"[{self.error_type}]", file=sys.stderr)
        print(f"--> File '{filepath}', Line {self.line}, Column {self.col}:", file=sys.stderr)
        if offending_line:
            print(f"    {offending_line}", file=sys.stderr)
            print(f"    {pointer}", file=sys.stderr)
        print(f"Error: {self.message}", file=sys.stderr)
        if self.suggestion:
            print(f"Suggestion: {self.suggestion}", file=sys.stderr)
        print(f"{divider}\n", file=sys.stderr)
