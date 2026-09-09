// Corvus WebAssembly (Wasm) In-Browser Runtime Playground Engine
// Author: Saatvik Jain

let pyodideInstance = null;
let isWasmLoaded = false;

// Sample Corvus Code Templates
const SAMPLE_PROGRAMS = {
    "hello": `# Corvus Hello World & Control Flow Sample
var name = "Developer"
log("Hello, " + name + "! Welcome to Corvus WebAssembly Playground.")

var score = 95
if (score >= 90) [
    log("Status: Excellent Grade (A+)")
] else [
    log("Status: Good Effort")
]
`,
    "factorial": `# Recursion & Factorial Benchmark
func factorial(n) [
    if (n <= 1) [
        givout 1
    ]
    givout n * factorial(n - 1)
]

log("Factorial of 5: " + str(factorial(5)))
log("Factorial of 7: " + str(factorial(7)))
`,
    "stdlib": `# Native Math & String Standard Library Modules
var a = 0 - 15
var b = 42

log("Abs of -15: " + str(math.abs(a)))
log("Max of (-15, 42): " + str(math.max(a, b)))
log("Sqrt approx of 144: " + str(math.sqrt_approx(144)))

var text = "Corvus Wasm"
log("Is string empty: " + str(string.is_empty(text)))
`,
    "pipeline": `# Functional Pipeline (|>) & Pattern Matching
func double(x) [ givout x * 2 ]
func add_ten(x) [ givout x + 10 ]

var result = 5 |> double |> add_ten
log("Pipeline result (5 -> double -> add_ten): " + str(result))

var status_code = 200
match (status_code) [
    case 200: log("Matched 200: HTTP OK")
    case 404: log("Matched 404: Not Found")
    else: log("Unknown Code")
]
`,
    "optimizer": `# v4.1 Super High-Level Optimization Engine Preview
var a = 10
var b = 5
var c = a * b + 2  # Constant propagated: 10 * 5 + 2 = 52
log("Super Optimizer Constant Folding Result: " + str(c))

var x = 8
var mult_4 = x * 4  # Reduced to SHL x, 2
log("Strength Reduction (8 * 4): " + str(mult_4))
`,
    "crows_v42": `# Corvus v4.2 Expanded "Murder of Crows" Concurrency Showcase
# Features parallel_map, channels, and worker nests

func compute_square(x) [
    givout x * x
]

var numbers = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10}
log("Original array: " + str(numbers))

log("Evaluating parallel_map across worker crows...")
var squared = crow.parallel_map(compute_square, numbers)
log("Parallel map results: " + str(squared))

log("Creating thread-safe CrowChannel...")
var ch = crow.channel()
ch.send("Message from Crow Thread A")
ch.send("Message from Crow Thread B")

log("Channel recv 1: " + str(ch.recv()))
log("Channel recv 2: " + str(ch.recv()))
`,
    "graphics_demo": `# Corvus v4.2 Zero-Config Graphics & Game Engine Preview
# Initializing 2D Desktop Graphics Window

log("Initializing Corvus Desktop Window (800x600)...")
graphics.init_window("Corvus v4.2 Graphics Demo", 800, 600, "#0f172a")

log("Drawing shapes, text, and player entities...")
graphics.clear("#0f172a")

# Draw player paddle & ball
graphics.draw_rect(20, 200, 16, 100, "#38bdf8", 1)
graphics.draw_rect(764, 200, 16, 100, "#fb923c", 1)
graphics.draw_circle(400, 250, 12, "#4ade80", 1)

graphics.draw_text("Corvus v4.2 Desktop Graphics Active!", 220, 30, 20, "#38bdf8")
graphics.draw_text("Playable Snake, Pong & Multi-Threaded Particles Included!", 140, 70, 16, "#94a3b8")

log("[Graphics Engine]: Canvas rendered successfully.")
`
};

// Embed Core Corvus Interpreter Engine Python Source
const CORVUS_ENGINE_PY = `
import sys
import io

class CorvusError(Exception):
    def __init__(self, error_type, message, suggestion=""):
        self.error_type = error_type
        self.message = message
        self.suggestion = suggestion
        super().__init__(f"[{error_type}]: {message}")

class Token:
    def __init__(self, type_, value, line, col):
        self.type = type_
        self.value = value
        self.line = line
        self.col = col

def tokenize(code):
    tokens = []
    i = 0
    line, col = 1, 1
    keywords = {"set", "var", "const", "mk", "func", "givout", "if", "elsif", "else", "while", "for", "try", "catch", "lambda", "match", "case", "class"}
    
    while i < len(code):
        ch = code[i]
        if ch in ' \t\r':
            i += 1; col += 1; continue
        if ch == '\n':
            i += 1; line += 1; col = 1; continue
        if ch == '#':
            while i < len(code) and code[i] != '\n': i += 1
            continue
        if ch in '0123456789':
            num = ""
            while i < len(code) and (code[i].isdigit() or code[i] == '.'):
                num += code[i]; i += 1
            val = float(num) if '.' in num else int(num)
            tokens.append(Token("NUMBER", val, line, col))
            continue
        if ch.isalpha() or ch == '_':
            ident = ""
            while i < len(code) and (code[i].isalnum() or code[i] == '_'):
                ident += code[i]; i += 1
            t_type = ident.upper() if ident in keywords else "IDENTIFIER"
            tokens.append(Token(t_type, ident, line, col))
            continue
        if ch == '"':
            i += 1; str_val = ""
            while i < len(code) and code[i] != '"':
                str_val += code[i]; i += 1
            i += 1
            tokens.append(Token("STRING", str_val, line, col))
            continue
        if code[i:i+2] == '|>':
            tokens.append(Token("PIPE", "|>", line, col)); i += 2; continue
        if code[i:i+2] == '->':
            tokens.append(Token("ARROW", "->", line, col)); i += 2; continue
        if code[i:i+2] == '==':
            tokens.append(Token("EQ", "==", line, col)); i += 2; continue
        if code[i:i+2] == '!=':
            tokens.append(Token("NEQ", "!=", line, col)); i += 2; continue
        if code[i:i+2] == '>=':
            tokens.append(Token("GTE", ">=", line, col)); i += 2; continue
        if code[i:i+2] == '<=':
            tokens.append(Token("LTE", "<=", line, col)); i += 2; continue
            
        single_ops = {'+': 'PLUS', '-': 'MINUS', '*': 'MUL', '/': 'DIV', '%': 'MOD', 
                      '=': 'ASSIGN', '(': 'LPAREN', ')': 'RPAREN', '[': 'LBRACKET', 
                      ']': 'RBRACKET', '{': 'LBRACE', '}': 'RBRACE', ',': 'COMMA', 
                      ':': 'COLON', '>': 'GT', '<': 'LT'}
        if ch in single_ops:
            tokens.append(Token(single_ops[ch], ch, line, col))
            i += 1; col += 1; continue
        i += 1
    tokens.append(Token("EOF", None, line, col))
    return tokens

class ASTNode: pass
class ProgramNode(ASTNode):
    def __init__(self, stmts): self.statements = stmts
class LiteralNode(ASTNode):
    def __init__(self, val): self.value = val
class IdentifierNode(ASTNode):
    def __init__(self, name): self.name = name
class VarDeclNode(ASTNode):
    def __init__(self, name, val): self.name = name; self.value = val
class AssignmentNode(ASTNode):
    def __init__(self, target, val): self.target = target; self.value = val
class BinOpNode(ASTNode):
    def __init__(self, left, op, right): self.left = left; self.op = op; self.right = right
class BlockNode(ASTNode):
    def __init__(self, stmts): self.statements = stmts
class IfNode(ASTNode):
    def __init__(self, cond, then_b, else_b=None): self.condition = cond; self.then_block = then_b; self.else_block = else_b
class WhileNode(ASTNode):
    def __init__(self, cond, body): self.condition = cond; self.body = body
class GivoutNode(ASTNode):
    def __init__(self, val): self.value = val
class FuncDeclNode(ASTNode):
    def __init__(self, name, params, body): self.name = name; self.params = params; self.body = body
class FuncCallNode(ASTNode):
    def __init__(self, callee, args): self.callee = callee; self.args = args

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self): return self.tokens[self.pos]
    def consume(self, expected=None):
        tok = self.peek()
        if expected and tok.type != expected:
            raise CorvusError("SyntaxError", f"Expected token {expected} but got {tok.type}")
        self.pos += 1
        return tok

    def parse(self):
        stmts = []
        while self.peek().type != "EOF":
            stmts.append(self.parse_statement())
        return ProgramNode(stmts)

    def parse_statement(self):
        tok = self.peek()
        if tok.type == "VAR":
            self.consume("VAR")
            name = self.consume("IDENTIFIER").value
            val = None
            if self.peek().type == "ASSIGN":
                self.consume("ASSIGN")
                val = self.parse_expr()
            return VarDeclNode(name, val)
        elif tok.type == "SET":
            self.consume("SET")
            name = self.consume("IDENTIFIER").value
            self.consume("ASSIGN")
            val = self.parse_expr()
            return AssignmentNode(IdentifierNode(name), val)
        elif tok.type == "IF":
            return self.parse_if()
        elif tok.type == "WHILE":
            self.consume("WHILE")
            self.consume("LPAREN")
            cond = self.parse_expr()
            self.consume("RPAREN")
            body = self.parse_block()
            return WhileNode(cond, body)
        elif tok.type == "FUNC":
            self.consume("FUNC")
            name = self.consume("IDENTIFIER").value
            self.consume("LPAREN")
            params = []
            if self.peek().type != "RPAREN":
                params.append(self.consume("IDENTIFIER").value)
                while self.peek().type == "COMMA":
                    self.consume("COMMA")
                    params.append(self.consume("IDENTIFIER").value)
            self.consume("RPAREN")
            body = self.parse_block()
            return FuncDeclNode(name, params, body)
        elif tok.type == "GIVOUT":
            self.consume("GIVOUT")
            val = self.parse_expr()
            return GivoutNode(val)
        else:
            return self.parse_expr()

    def parse_block(self):
        if self.peek().type == "LBRACKET":
            self.consume("LBRACKET")
            stmts = []
            while self.peek().type != "RBRACKET" and self.peek().type != "EOF":
                stmts.append(self.parse_statement())
            self.consume("RBRACKET")
            return BlockNode(stmts)
        elif self.peek().type == "LBRACE":
            self.consume("LBRACE")
            stmts = []
            while self.peek().type != "RBRACE" and self.peek().type != "EOF":
                stmts.append(self.parse_statement())
            self.consume("RBRACE")
            return BlockNode(stmts)
        return BlockNode([self.parse_statement()])

    def parse_if(self):
        self.consume("IF")
        self.consume("LPAREN")
        cond = self.parse_expr()
        self.consume("RPAREN")
        then_b = self.parse_block()
        else_b = None
        if self.peek().type == "ELSE":
            self.consume("ELSE")
            else_b = self.parse_block()
        return IfNode(cond, then_b, else_b)

    def parse_expr(self):
        return self.parse_binary(0)

    def parse_binary(self, min_prec):
        left = self.parse_primary()
        while True:
            tok = self.peek()
            prec = self.get_prec(tok.type)
            if prec < min_prec or prec == 0: break
            self.consume()
            right = self.parse_binary(prec + 1)
            left = BinOpNode(left, tok.value, right)
        return left

    def get_prec(self, tok_type):
        precs = {"PIPE": 1, "EQ": 2, "NEQ": 2, "LT": 3, "GT": 3, "LTE": 3, "GTE": 3, "PLUS": 4, "MINUS": 4, "MUL": 5, "DIV": 5}
        return precs.get(tok_type, 0)

    def parse_primary(self):
        tok = self.peek()
        if tok.type == "NUMBER":
            self.consume()
            return LiteralNode(tok.value)
        elif tok.type == "STRING":
            self.consume()
            return LiteralNode(tok.value)
        elif tok.type == "IDENTIFIER":
            self.consume()
            name = tok.value
            if self.peek().type == "LPAREN":
                self.consume("LPAREN")
                args = []
                if self.peek().type != "RPAREN":
                    args.append(self.parse_expr())
                    while self.peek().type == "COMMA":
                        self.consume("COMMA")
                        args.append(self.parse_expr())
                self.consume("RPAREN")
                return FuncCallNode(IdentifierNode(name), args)
            return IdentifierNode(name)
        elif tok.type == "LPAREN":
            self.consume("LPAREN")
            expr = self.parse_expr()
            self.consume("RPAREN")
            return expr
        raise CorvusError("SyntaxError", f"Unexpected token {tok.type}")

class Environment:
    def __init__(self, parent=None):
        self.values = {}
        self.parent = parent

    def define(self, name, val): self.values[name] = val
    def assign(self, name, val):
        if name in self.values:
            self.values[name] = val
        elif self.parent:
            self.parent.assign(name, val)
        else:
            self.values[name] = val

    def get(self, name):
        if name in self.values: return self.values[name]
        if self.parent: return self.parent.get(name)
        raise CorvusError("NameError", f"Undefined variable '{name}'")

class ReturnException(Exception):
    def __init__(self, val): self.value = val

class Evaluator:
    def __init__(self, env):
        self.env = env
        self._setup_builtins()

    def _setup_builtins(self):
        self.env.define("log", print)
        self.env.define("print", print)
        self.env.define("str", str)
        self.env.define("int", int)
        self.env.define("float", float)
        
        # Native Math StdLib namespace
        class MathLib:
            @staticmethod
            def abs(x): return abs(x)
            @staticmethod
            def max(a, b): return max(a, b)
            @staticmethod
            def min(a, b): return min(a, b)
            @staticmethod
            def factorial(n):
                res = 1
                for i in range(1, int(n)+1): res *= i
                return res
            @staticmethod
            def sqrt_approx(n): return float(int(n)**0.5)
        
        # Native Crow Concurrency Engine Wasm Shim
        class CrowChannelShim:
            def __init__(self): self.q = []
            def send(self, val): self.q.append(val)
            def recv(self): return self.q.pop(0) if self.q else None
            def poll(self): return self.q.pop(0) if self.q else None

        class CrowLib:
            @staticmethod
            def fly(fn, *args): return fn(*args)
            @staticmethod
            def flock(crows): return list(crows)
            @staticmethod
            def channel(): return CrowChannelShim()
            @staticmethod
            def race(crows): return crows[0] if crows else None
            @staticmethod
            def select(channels):
                for i, c in enumerate(channels):
                    v = c.poll()
                    if v is not None: return [i, v]
                return [0, None]
            @staticmethod
            def parallel_map(fn, items): return [fn(x) for x in items]

        # Native Graphics Engine Wasm Sandbox Shim
        class GraphicsLib:
            @staticmethod
            def init_window(title, w, h, bg): print(f"[GraphicsEngine Wasm]: Desktop window initialized ({w}x{h}, bg='{bg}') - title: '{title}'")
            @staticmethod
            def clear(bg): pass
            @staticmethod
            def draw_rect(x, y, w, h, c, f=1): print(f"[Canvas Draw]: Rectangle at ({x}, {y}) size ({w}x{h}), color='{c}'")
            @staticmethod
            def draw_circle(x, y, r, c, f=1): print(f"[Canvas Draw]: Circle at ({x}, {y}) radius={r}, color='{c}'")
            @staticmethod
            def draw_line(x1, y1, x2, y2, c, t=2): print(f"[Canvas Draw]: Line from ({x1},{y1}) to ({x2},{y2}), color='{c}'")
            @staticmethod
            def draw_text(txt, x, y, size=16, c="white"): print(f"[Canvas Text]: '{txt}' at ({x},{y})")
            @staticmethod
            def is_open(): return False
            @staticmethod
            def poll_events(): return False
            @staticmethod
            def update(): pass
            @staticmethod
            def is_key_pressed(k): return False
            @staticmethod
            def sleep(s): pass
            @staticmethod
            def fps(f): pass
            @staticmethod
            def close(): pass

        self.env.define("math", MathLib)
        self.env.define("string", StringLib)
        self.env.define("crow", CrowLib)
        self.env.define("graphics", GraphicsLib)

    def evaluate(self, node):
        if node is None: return None
        n_type = type(node).__name__
        if n_type == "ProgramNode":
            res = None
            for s in node.statements: res = self.evaluate(s)
            return res
        elif n_type == "LiteralNode": return node.value
        elif n_type == "IdentifierNode": return self.env.get(node.name)
        elif n_type == "VarDeclNode":
            val = self.evaluate(node.value) if node.value else None
            self.env.define(node.name, val)
            return val
        elif n_type == "AssignmentNode":
            val = self.evaluate(node.value)
            self.env.assign(node.target.name, val)
            return val
        elif n_type == "BinOpNode":
            if node.op == '|>':
                # Pipeline operator: left |> right
                left_val = self.evaluate(node.left)
                if isinstance(node.right, FuncCallNode):
                    node.right.args.insert(0, LiteralNode(left_val))
                    return self.evaluate(node.right)
                elif isinstance(node.right, IdentifierNode):
                    fn = self.env.get(node.right.name)
                    return fn(left_val)
            left_v = self.evaluate(node.left)
            right_v = self.evaluate(node.right)
            if node.op == '+': return left_v + right_v
            elif node.op == '-': return left_v - right_v
            elif node.op == '*': return left_v * right_v
            elif node.op == '/': return left_v / right_v if right_v != 0 else 0
            elif node.op == '==': return left_v == right_v
            elif node.op == '!=': return left_v != right_v
            elif node.op == '>': return left_v > right_v
            elif node.op == '<': return left_v < right_v
            elif node.op == '>=': return left_v >= right_v
            elif node.op == '<=': return left_v <= right_v
        elif n_type == "BlockNode":
            res = None
            for s in node.statements: res = self.evaluate(s)
            return res
        elif n_type == "IfNode":
            cond_v = self.evaluate(node.condition)
            if cond_v: return self.evaluate(node.then_block)
            elif node.else_block: return self.evaluate(node.else_block)
        elif n_type == "WhileNode":
            while self.evaluate(node.condition):
                try: self.evaluate(node.body)
                except ReturnException as rx: raise rx
        elif n_type == "FuncDeclNode":
            def user_fn(*args):
                prev_env = self.env
                fn_env = Environment(parent=prev_env)
                for p_name, arg_val in zip(node.params, args):
                    fn_env.define(p_name, arg_val)
                self.env = fn_env
                try:
                    self.evaluate(node.body)
                except ReturnException as rx:
                    return rx.value
                finally:
                    self.env = prev_env
                return None
            self.env.define(node.name, user_fn)
            return user_fn
        elif n_type == "GivoutNode":
            val = self.evaluate(node.value) if node.value else None
            raise ReturnException(val)
        elif n_type == "FuncCallNode":
            callee_v = self.evaluate(node.callee)
            args_v = [self.evaluate(arg) for arg in node.args]
            if callable(callee_v): return callee_v(*args_v)
            elif hasattr(callee_v, '__name__'): return getattr(callee_v, '__name__')(*args_v)

def run_corvus_code(code_str):
    buffer = io.StringIO()
    sys.stdout = buffer
    try:
        tokens = tokenize(code_str)
        parser = Parser(tokens)
        ast = parser.parse()
        env = Environment()
        evaluator = Evaluator(env)
        evaluator.evaluate(ast)
        output = buffer.getvalue()
        return output if output else "[Program completed with zero output]"
    except Exception as ex:
        return f"[Corvus Execution Error]: {ex}"
    finally:
        sys.stdout = sys.__stdout__
`;

// Initialize Pyodide WebAssembly Engine
async function initPyodideWasm() {
    const statusText = document.getElementById('wasm-status');
    const runBtn = document.getElementById('run-wasm-btn');

    try {
        if (statusText) statusText.innerText = "⏳ Loading WebAssembly Runtime (Pyodide)...";
        pyodideInstance = await loadPyodide();
        await pyodideInstance.runPythonAsync(CORVUS_ENGINE_PY);
        isWasmLoaded = true;

        if (statusText) {
            statusText.innerText = "⚡ WebAssembly Engine Ready!";
            statusText.style.color = "#4ade80";
        }
        if (runBtn) {
            runBtn.disabled = false;
            runBtn.style.opacity = "1";
        }
    } catch (err) {
        if (statusText) {
            statusText.innerText = "❌ WebAssembly Initialization Failed";
            statusText.style.color = "#fb923c";
        }
        console.error("Pyodide Wasm Init Error:", err);
    }
}

// Execute Corvus Code inside WebAssembly Sandbox
async function runCorvusWasm() {
    const codeEditor = document.getElementById('wasm-code-editor');
    const terminalOutput = document.getElementById('wasm-terminal-output');
    const statusText = document.getElementById('wasm-status');

    if (!isWasmLoaded || !pyodideInstance) {
        alert("WebAssembly runtime is still initializing. Please wait a moment.");
        return;
    }

    const code = codeEditor.value;
    if (!code.trim()) {
        terminalOutput.innerText = "[Corvus Wasm]: Code editor is empty.";
        return;
    }

    terminalOutput.innerText = "▶ Running Corvus code in WebAssembly Sandbox...\n";
    statusText.innerText = "⚙️ Executing in Wasm...";
    statusText.style.color = "#38bdf8";

    const startTime = performance.now();

    try {
        // Escaping input string for Python call
        const escapedCode = JSON.stringify(code);
        const result = await pyodideInstance.runPythonAsync(`run_corvus_code(${escapedCode})`);
        const endTime = performance.now();
        const execTime = (endTime - startTime).toFixed(2);

        terminalOutput.innerText = result + `\n\n[Execution completed in ${execTime} ms]`;
        statusText.innerText = `⚡ Execution Done (${execTime} ms)`;
        statusText.style.color = "#4ade80";
    } catch (ex) {
        terminalOutput.innerText = `[Wasm Sandbox Error]: ${ex.message}`;
        statusText.innerText = "❌ Execution Error";
        statusText.style.color = "#fb923c";
    }
}

// Event Listeners for Playground Controls
document.addEventListener('DOMContentLoaded', () => {
    // 1. Initialize Pyodide WebAssembly Engine
    initPyodideWasm();

    // 2. Attach Sample Code Dropdown Handler
    const sampleSelect = document.getElementById('wasm-sample-select');
    const codeEditor = document.getElementById('wasm-code-editor');

    if (sampleSelect && codeEditor) {
        codeEditor.value = SAMPLE_PROGRAMS['hello']; // Default template

        sampleSelect.addEventListener('change', (e) => {
            const key = e.target.value;
            if (SAMPLE_PROGRAMS[key]) {
                codeEditor.value = SAMPLE_PROGRAMS[key];
            }
        });
    }

    // 3. Attach Run Button Handler
    const runBtn = document.getElementById('run-wasm-btn');
    if (runBtn) {
        runBtn.addEventListener('click', runCorvusWasm);
    }

    // 4. Attach Clear Terminal Handler
    const clearBtn = document.getElementById('clear-wasm-terminal');
    if (clearBtn) {
        clearBtn.addEventListener('click', () => {
            const terminalOutput = document.getElementById('wasm-terminal-output');
            if (terminalOutput) terminalOutput.innerText = "[Terminal cleared]";
        });
    }
});
