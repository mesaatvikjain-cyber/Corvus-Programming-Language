import sys
import urllib.parse

# Corvus Enterprise Diagnostic & Call Stack Traceback Engine (v4.4)
# Rust-Style Diagnostic Knowledge Base, Levenshtein Heuristics & AI-Fix Engine

class CallFrame:
    def __init__(self, func_name: str, filepath: str, line: int, column: int = 1):
        self.func_name = func_name
        self.filepath = filepath
        self.line = line
        self.column = column


def levenshtein_distance(s1: str, s2: str) -> int:
    """Calculate the Levenshtein edit distance between two strings."""
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            cost = 0 if s1[i - 1] == s2[j - 1] else 1
            dp[i][j] = min(
                dp[i - 1][j] + 1,      # Deletion
                dp[i][j - 1] + 1,      # Insertion
                dp[i - 1][j - 1] + cost # Substitution
            )
    return dp[m][n]


def find_closest_match(word: str, candidates: list, max_distance: int = 3) -> str:
    """Find the closest candidate match within max edit distance."""
    best_match = None
    best_dist = max_distance + 1
    w_lower = word.lower()
    for cand in candidates:
        if not cand or cand == word:
            continue
        dist = levenshtein_distance(w_lower, cand.lower())
        if dist < best_dist:
            best_dist = dist
            best_match = cand
    return best_match if best_dist <= max_distance else None


# Mapping of common programming language habit typos to native Corvus keywords
KEYWORD_TYPO_MAP = {
    "false": "fal",
    "def": "func (or 'mk func')",
    "function": "func",
    "fn": "func",
    "return": "givout",
    "elif": "elsif",
    "else if": "elsif",
    "break": "brk",
    "continue": "con",
    "none": "null",
    "nil": "null",
    "undefined": "null",
    "true": "true",
    "self": "self",
}


# Rust-Style Curated Diagnostic Catalog
ERROR_CATALOG = {
    "E0101": {
        "title": "Type Mismatch",
        "category": "Corvus TypeError",
        "summary": "An assigned value or expression does not match the variable's declared type.",
        "causes": [
            "Assigning a string or float to a variable strictly declared as 'int'.",
            "Passing an unexpected type into a strongly typed function argument."
        ],
        "bad_code": "set int; count = \"ten\"",
        "good_code": "set int; count = 10  // Or 'set str; count = \"ten\"'"
    },
    "E0102": {
        "title": "Cannot Reassign Constant",
        "category": "Corvus TypeError",
        "summary": "Attempted to overwrite or rebind an immutable identifier defined with 'const'.",
        "causes": [
            "Reassigning to a variable created with 'const <type>; name = value'."
        ],
        "bad_code": "const int; MAX = 100\nMAX = 200",
        "good_code": "set int; max_limit = 100\nmax_limit = 200  // Use 'set' for mutable state"
    },
    "E0201": {
        "title": "Undefined Identifier / Variable",
        "category": "Corvus NameError",
        "summary": "Referenced an identifier that has not been declared or is out of scope.",
        "causes": [
            "Typo in variable, function, or module name.",
            "Using a variable before declaring it with 'set <type>;' or 'var'."
        ],
        "bad_code": "log(total_ammount)",
        "good_code": "set int; total_amount = 50\nlog(total_amount)"
    },
    "E0202": {
        "title": "Assignment to Undefined Variable",
        "category": "Corvus NameError",
        "summary": "Assigned a value to a variable before declaring it in the current scope.",
        "causes": [
            "Omitting the 'set <type>; name = ...' or 'var name = ...' declaration."
        ],
        "bad_code": "score = 99",
        "good_code": "set int; score = 99  // Or 'var score = 99'"
    },
    "E0203": {
        "title": "Attribute or Method Not Found",
        "category": "Corvus AttributeError",
        "summary": "Invoked a method or accessed a property that does not exist on this object or module.",
        "causes": [
            "Typo in method name (e.g. calling .lenght() instead of .length()).",
            "Calling a method unsupported by the target collection or instance."
        ],
        "bad_code": "var lis = {1, 2, 3}\nlis.add_item(4)",
        "good_code": "var lis = {1, 2, 3}\nlis.add(4)"
    },
    "E0301": {
        "title": "Division by Zero",
        "category": "Corvus MathError",
        "summary": "Attempted to divide a number by zero or an expression evaluating to zero.",
        "causes": [
            "Denominator evaluated to 0 during runtime arithmetic."
        ],
        "bad_code": "set int; res = 100 / 0",
        "good_code": "if (denom != 0) [\n    set int; res = 100 / denom\n]"
    },
    "E0401": {
        "title": "Index Out of Bounds",
        "category": "Corvus IndexError",
        "summary": "Attempted to access a collection index that does not exist.",
        "causes": [
            "Index >= length of the list, string, or tuple.",
            "Off-by-one indexing errors."
        ],
        "bad_code": "var items = {10, 20}\nlog(items[5])",
        "good_code": "if (idx < items.length()) [\n    log(items[idx])\n]"
    },
    "E0402": {
        "title": "Dictionary Key Not Found",
        "category": "Corvus KeyError",
        "summary": "Looked up a key that does not exist inside the target dictionary.",
        "causes": [
            "Misspelled dictionary key or accessing a dynamic key that was not populated."
        ],
        "bad_code": "var user = {\"name\": \"Alice\"}\nlog(user[\"age\"])",
        "good_code": "var age = user.get(\"age\", 0)  // Or verify key exists before access"
    },
    "E0501": {
        "title": "Syntax Error / Unexpected Token",
        "category": "Corvus SyntaxError",
        "summary": "The parser encountered a token or structure that violates the Corvus language grammar.",
        "causes": [
            "Missing closing brackets, braces, or parentheses.",
            "Using keywords from other languages (like 'return' instead of 'givout')."
        ],
        "bad_code": "func add(a, b) [ return a + b ]",
        "good_code": "func add(a, b) [ givout a + b ]"
    },
    "E0601": {
        "title": "Package or Module Load Failure",
        "category": "Corvus ModuleError",
        "summary": "A required module or package could not be resolved in StdLib or local packages.",
        "causes": [
            "Typo in module name.",
            "Missing package dependency; run 'cpm install <pkg>'."
        ],
        "bad_code": "get unknown_lib",
        "good_code": "get tensorflow\n// Or install via 'cpm install unknown_lib'"
    }
}


def explain_error(code: str = None):
    """Print detailed Rust-style diagnostic guide for a Corvus error code."""
    divider = "=" * 62
    if not code or code.lower() in ("all", "list"):
        print(f"\n{divider}")
        print("  Corvus Diagnostic Knowledge Base (Catalog Index)")
        print(divider)
        for c, info in sorted(ERROR_CATALOG.items()):
            print(f"  {c:<7} | {info['category']:<22} | {info['title']}")
        print(f"\nRun 'python Corvus.py --explain <CODE>' for in-depth solutions.")
        print(f"{divider}\n")
        return

    code_upper = code.upper()
    info = ERROR_CATALOG.get(code_upper)
    if not info:
        print(f"[Error]: Unknown Corvus error code '{code}'.")
        print("Run 'python Corvus.py --explain all' to see all documented codes.")
        return

    print(f"\n{divider}")
    print(f"  Corvus Diagnostic Guide: {code_upper} - {info['title']}")
    print(f"  Category: {info['category']}")
    print(divider)
    print(f"\nSummary:\n  {info['summary']}\n")
    print("Common Causes:")
    for cause in info['causes']:
        print(f"  * {cause}")
    print("\nProblematic Code Pattern:")
    for line in info['bad_code'].splitlines():
        print(f"  [-] {line}")
    print("\nRecommended Fix:")
    for line in info['good_code'].splitlines():
        print(f"  [+] {line}")
    print(f"\n{divider}\n")


class CorvusError(Exception):
    def __init__(
        self,
        error_type: str,
        message: str,
        line: int = 1,
        col: int = 1,
        token_len: int = 1,
        suggestion: str = "",
        call_stack: list = None,
        error_code: str = ""
    ):
        self.error_type = error_type
        self.message = message
        self.line = line
        self.col = col
        self.token_len = max(1, token_len)
        self.suggestion = suggestion
        self.call_stack = call_stack or []
        self.error_code = error_code or self._infer_code(error_type)
        super().__init__(self.message)

    def _infer_code(self, error_type: str) -> str:
        if "Type" in error_type: return "E0101"
        if "Name" in error_type: return "E0201"
        if "Attribute" in error_type: return "E0203"
        if "Math" in error_type: return "E0301"
        if "Index" in error_type: return "E0401"
        if "Key" in error_type: return "E0402"
        if "Syntax" in error_type or "Parser" in error_type: return "E0501"
        if "Module" in error_type or "Package" in error_type: return "E0601"
        return "E0701"

    def print_formatted(self, filepath: str, source_code: str, ai_fix: bool = False):
        lines = source_code.splitlines()
        line_idx = self.line - 1

        divider = "======================================================"
        print(f"\n{divider}", file=sys.stderr)
        code_tag = f" {self.error_code}:" if self.error_code else ""
        print(f"[Corvus{code_tag} {self.error_type}]", file=sys.stderr)

        # Print Call Stack Traceback if active
        if self.call_stack:
            print("Call Stack Traceback (most recent call last):", file=sys.stderr)
            for frame in self.call_stack:
                f_name = frame.func_name if hasattr(frame, 'func_name') else str(frame)
                f_line = frame.line if hasattr(frame, 'line') else 1
                f_path = frame.filepath if hasattr(frame, 'filepath') else filepath
                print(f"  --> In function '{f_name}' at {f_path}:{f_line}", file=sys.stderr)
            print("------------------------------------------------------", file=sys.stderr)

        print(f"--> Location: File '{filepath}', Line {self.line}, Column {self.col}:", file=sys.stderr)

        target_line = ""
        if 0 <= line_idx < len(lines):
            if line_idx > 0:
                print(f"  {self.line - 1:4d} | {lines[line_idx - 1]}", file=sys.stderr)

            target_line = lines[line_idx]
            print(f"  {self.line:4d} | {target_line}", file=sys.stderr)

            indent = " " * (self.col - 1)
            carets = "^" * self.token_len
            print(f"       | {indent}{carets}", file=sys.stderr)

            if line_idx + 1 < len(lines):
                print(f"  {self.line + 1:4d} | {lines[line_idx + 1]}", file=sys.stderr)

        print(f"\nDetails: {self.message}", file=sys.stderr)
        if self.suggestion:
            print(f"Fix Hint: {self.suggestion}", file=sys.stderr)

        # Rust-style explanation pointer
        if self.error_code in ERROR_CATALOG:
            print(f"Explanation: For full guide, run: python Corvus.py --explain {self.error_code}", file=sys.stderr)

        # AI-Fix Smart Synthesis & 1-Click Search Link
        if ai_fix:
            print("------------------------------------------------------", file=sys.stderr)
            print("[Corvus AI-Fix Synthesized Solution]:", file=sys.stderr)
            
            # Find the true offending line if self.line was default 1
            effective_line = target_line
            import re
            m_orig = re.search(r"(?:variable|identifier|symbol|method|attribute)\s+'([^']+)'", self.message)
            if m_orig:
                bad_sym = m_orig.group(1)
                for line in lines:
                    if bad_sym in line:
                        effective_line = line
                        break

            # Synthesize smart replacement line if target line is known
            ai_solution = self._synthesize_ai_solution(effective_line)
            if ai_solution:
                print(f"  Suggested Patch:\n    [-] {effective_line.strip()}\n    [+] {ai_solution}", file=sys.stderr)

            
            # 1-Click Web Search Link
            query = f"Corvus {self.error_type} {self.message}"
            encoded_query = urllib.parse.quote_plus(query)
            search_url = f"https://www.google.com/search?q={encoded_query}"
            docs_url = f"https://github.com/mesaatvikjain-cyber/Corvus-Programming-Language-/wiki/Errors#{self.error_code.lower()}"
            print(f"  Web Search Direct Link:\n    🌐 {search_url}\n    📚 Documentation: {docs_url}", file=sys.stderr)

        print(f"{divider}\n", file=sys.stderr)

    def _synthesize_ai_solution(self, target_line: str) -> str:
        """Synthesize an actionable code replacement for the offending line."""
        if not target_line:
            return ""
        s = target_line.strip()
        # Check keyword typos
        for typo, fix in KEYWORD_TYPO_MAP.items():
            if f" {typo}" in s or s.startswith(typo):
                return s.replace(typo, fix)
        # Check division by zero
        if "/ 0" in s:
            return s.replace("/ 0", "/ non_zero_value /* ensure denominator > 0 */")
        # Check undefined variable typos if suggested
        if "Did you mean" in self.suggestion:
            import re
            m = re.search(r"Did you mean '([^']+)'\?", self.suggestion)
            if m:
                correct_var = m.group(1)
                m_orig = re.search(r"(?:variable|identifier|symbol|method|attribute)\s+'([^']+)'", self.message)
                if m_orig:
                    orig_var = m_orig.group(1)
                    return s.replace(orig_var, correct_var)
        return ""

