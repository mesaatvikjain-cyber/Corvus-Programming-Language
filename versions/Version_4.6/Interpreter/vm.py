# vm.py
# Corvus Bytecode Virtual Machine (CorvusVM)
# Executes compiled CodeObject bytecode instructions with activation frames,
# builtins, and native matrix math support.

import sys
from typing import Any, Dict, List, Optional
from bytecode import OpCode, Instruction, CodeObject

class VMError(Exception):
    """Runtime error in the Corvus Virtual Machine."""
    pass

class VMFunction:
    """Represents a callable function in CorvusVM."""
    def __init__(self, code: CodeObject, name: str, params: List[str], closure: Optional[Dict[str, Any]] = None):
        self.code = code
        self.name = name
        self.params = params
        self.closure = closure or {}

    def __repr__(self):
        return f"<VMFunction {self.name}({', '.join(self.params)})>"

class Frame:
    """Activation call frame in CorvusVM."""
    def __init__(self, code: CodeObject, locals_dict: Optional[Dict[str, Any]] = None):
        self.code = code
        self.locals: Dict[str, Any] = locals_dict if locals_dict is not None else {}
        self.ip: int = 0

    def next_instruction(self) -> Optional[Instruction]:
        if self.ip < len(self.code.instructions):
            instr = self.code.instructions[self.ip]
            self.ip += 1
            return instr
        return None

class CorvusVM:
    """
    High-performance Stack-based Virtual Machine for Corvus bytecode.
    Includes execution limits for recursion depth and stack safety.
    """
    MAX_STACK_DEPTH = 10000
    MAX_STACK_SIZE = 100000

    def __init__(self, max_stack_depth: int = MAX_STACK_DEPTH):
        self.stack: List[Any] = []
        self.frames: List[Frame] = []
        self.globals: Dict[str, Any] = {}
        self.builtins: Dict[str, Any] = {}
        self.max_stack_depth = max_stack_depth
        self.setup_builtins()

    def setup_builtins(self):
        """Register built-in Corvus functions into VM builtins table."""
        self.builtins = {
            "log": print,
            "print": print,
            "len": len,
            "type": lambda x: type(x).__name__,
            "str": str,
            "int": int,
            "float": float,
            "bool": bool,
            "list": list,
            "dict": dict,
            "tuple": tuple,
            "sum": sum,
            "min": min,
            "max": max,
            "abs": abs,
            "round": round,
            "range": range,
            "reversed": reversed,
            "sorted": sorted,
        }

    def push(self, val: Any):
        if len(self.stack) >= self.MAX_STACK_SIZE:
            raise VMError("Stack overflow: Maximum evaluation stack size exceeded.")
        self.stack.append(val)

    def pop(self) -> Any:
        if not self.stack:
            raise VMError("Stack underflow")
        return self.stack.pop()

    def peek(self) -> Any:
        if not self.stack:
            raise VMError("Stack is empty on peek")
        return self.stack[-1]

    def run(self, code: CodeObject, globals_dict: Optional[Dict[str, Any]] = None) -> Any:
        """Run a top-level CodeObject."""
        if globals_dict is not None:
            self.globals = globals_dict

        top_frame = Frame(code, self.globals)
        self.frames.append(top_frame)

        result = None
        while self.frames:
            frame = self.frames[-1]
            instr = frame.next_instruction()

            if instr is None:
                self.frames.pop()
                continue

            op = instr.opcode
            arg = instr.arg

            if op == OpCode.NOP:
                continue

            elif op == OpCode.LOAD_CONST:
                self.push(frame.code.constants[arg])

            elif op == OpCode.LOAD_VAR:
                name = frame.code.names[arg]
                if name in frame.locals:
                    self.push(frame.locals[name])
                elif name in self.globals:
                    self.push(self.globals[name])
                elif name in self.builtins:
                    self.push(self.builtins[name])
                else:
                    raise VMError(f"NameError: name '{name}' is not defined (line {instr.line})")

            elif op == OpCode.STORE_VAR:
                name = frame.code.names[arg]
                val = self.pop()
                frame.locals[name] = val

            elif op == OpCode.POP:
                self.pop()

            elif op == OpCode.DUP:
                self.push(self.peek())

            # --- Arithmetic & Binary Ops ---
            elif op == OpCode.ADD:
                b = self.pop()
                a = self.pop()
                self.push(a + b)

            elif op == OpCode.SUB:
                b = self.pop()
                a = self.pop()
                self.push(a - b)

            elif op == OpCode.MUL:
                b = self.pop()
                a = self.pop()
                self.push(a * b)

            elif op == OpCode.DIV:
                b = self.pop()
                a = self.pop()
                if b == 0:
                    raise VMError(f"ZeroDivisionError: division by zero (line {instr.line})")
                self.push(a / b)

            elif op == OpCode.MOD:
                b = self.pop()
                a = self.pop()
                self.push(a % b)

            elif op == OpCode.POW:
                b = self.pop()
                a = self.pop()
                self.push(a ** b)

            elif op == OpCode.MATMUL:
                b = self.pop()
                a = self.pop()
                self.push(self._eval_matmul(a, b, instr.line))

            elif op == OpCode.NEG:
                val = self.pop()
                self.push(-val)

            elif op == OpCode.NOT:
                val = self.pop()
                self.push(not val)

            # --- Comparisons ---
            elif op == OpCode.EQ:
                b = self.pop()
                a = self.pop()
                self.push(a == b)

            elif op == OpCode.NEQ:
                b = self.pop()
                a = self.pop()
                self.push(a != b)

            elif op == OpCode.LT:
                b = self.pop()
                a = self.pop()
                self.push(a < b)

            elif op == OpCode.GT:
                b = self.pop()
                a = self.pop()
                self.push(a > b)

            elif op == OpCode.LTE:
                b = self.pop()
                a = self.pop()
                self.push(a <= b)

            elif op == OpCode.GTE:
                b = self.pop()
                a = self.pop()
                self.push(a >= b)

            elif op == OpCode.IN:
                b = self.pop()
                a = self.pop()
                self.push(a in b)

            # --- Control Flow / Jumps ---
            elif op == OpCode.JUMP:
                frame.ip = arg

            elif op == OpCode.JUMP_IF_FALSE:
                val = self.pop()
                if not val:
                    frame.ip = arg

            elif op == OpCode.GET_ITER:
                val = self.pop()
                try:
                    it = iter(val)
                except Exception as e:
                    raise VMError(f"TypeError: '{type(val).__name__}' object is not iterable (line {instr.line})")
                self.push(it)

            elif op == OpCode.FOR_ITER:
                it = self.peek()
                try:
                    next_val = next(it)
                    self.push(next_val)
                except StopIteration:
                    self.pop() # remove iterator from stack
                    frame.ip = arg

            # --- Collections ---
            elif op == OpCode.BUILD_LIST:
                count = arg
                items = [self.pop() for _ in range(count)]
                items.reverse()
                self.push(items)

            elif op == OpCode.BUILD_TUPLE:
                count = arg
                items = [self.pop() for _ in range(count)]
                items.reverse()
                self.push(tuple(items))

            elif op == OpCode.BUILD_DICT:
                count = arg
                mapping = {}
                pairs = []
                for _ in range(count):
                    val = self.pop()
                    key = self.pop()
                    pairs.append((key, val))
                pairs.reverse()
                for k, v in pairs:
                    mapping[k] = v
                self.push(mapping)

            elif op == OpCode.INDEX_GET:
                idx = self.pop()
                container = self.pop()
                try:
                    self.push(container[idx])
                except Exception as e:
                    raise VMError(f"Index/Key Error: {e} (line {instr.line})")

            elif op == OpCode.INDEX_SET:
                idx = self.pop()
                container = self.pop()
                val = self.pop()
                try:
                    container[idx] = val
                except Exception as e:
                    raise VMError(f"Index/Key Assignment Error: {e} (line {instr.line})")

            # --- Functions ---
            elif op == OpCode.MAKE_FUNC:
                code_obj = frame.code.constants[arg]
                fn = VMFunction(code_obj, code_obj.name, code_obj.params)
                self.push(fn)

            elif op == OpCode.CALL_FUNC:
                arg_count = arg
                callee = self.pop()
                args = [self.pop() for _ in range(arg_count)]
                args.reverse()

                if isinstance(callee, VMFunction):
                    if len(args) != len(callee.params):
                        raise VMError(
                            f"TypeError: {callee.name}() takes {len(callee.params)} arguments but {len(args)} were given (line {instr.line})"
                        )
                    if len(self.frames) >= self.max_stack_depth:
                        raise VMError(
                            f"RecursionError: Maximum call stack depth of {self.max_stack_depth} exceeded (line {instr.line})"
                        )
                    call_locals = dict(zip(callee.params, args))
                    new_frame = Frame(callee.code, call_locals)
                    self.frames.append(new_frame)

                elif callable(callee):
                    try:
                        res = callee(*args)
                        self.push(res)
                    except Exception as e:
                        raise VMError(f"Error calling {callee}: {e} (line {instr.line})")
                else:
                    raise VMError(f"TypeError: '{type(callee).__name__}' object is not callable (line {instr.line})")

            elif op == OpCode.CALL_METHOD:
                method_name_idx, arg_count = arg
                method_name = frame.code.names[method_name_idx]
                args = [self.pop() for _ in range(arg_count)]
                args.reverse()
                target = self.pop()
                
                if hasattr(target, method_name):
                    meth = getattr(target, method_name)
                    try:
                        res = meth(*args)
                        self.push(res)
                    except Exception as e:
                        raise VMError(f"Error calling method '{method_name}': {e} (line {instr.line})")
                else:
                    raise VMError(f"AttributeError: '{type(target).__name__}' object has no attribute '{method_name}' (line {instr.line})")

            elif op == OpCode.RETURN:
                ret_val = self.pop()
                self.frames.pop()
                if self.frames:
                    self.push(ret_val)
                else:
                    result = ret_val
                    break

            # --- String Interpolation ---
            elif op == OpCode.BUILD_STRING:
                count = arg
                parts = [str(self.pop()) for _ in range(count)]
                parts.reverse()
                self.push("".join(parts))

            elif op == OpCode.HALT:
                break

            else:
                raise VMError(f"Unhandled opcode: {op.name} (line {instr.line})")

        return result

    def _eval_matmul(self, a: Any, b: Any, line: int = 0) -> Any:
        """Matrix multiplication for lists of lists or numpy arrays."""
        if hasattr(a, "__matmul__"):
            return a @ b

        if isinstance(a, list) and isinstance(b, list):
            if not (a and isinstance(a[0], list) and b and isinstance(b[0], list)):
                raise VMError(f"Matrix multiplication @ requires 2D matrices (line {line})")

            rows_a = len(a)
            cols_a = len(a[0])
            rows_b = len(b)
            cols_b = len(b[0])

            if cols_a != rows_b:
                raise VMError(
                    f"Dimension mismatch for matrix multiplication @: {rows_a}x{cols_a} and {rows_b}x{cols_b} (line {line})"
                )

            c = [[0 for _ in range(cols_b)] for _ in range(rows_a)]
            for i in range(rows_a):
                for j in range(cols_b):
                    s = 0
                    for k in range(cols_a):
                        s += a[i][k] * b[k][j]
                    c[i][j] = s
            return c

        raise VMError(f"Unsupported operand types for @: {type(a).__name__} and {type(b).__name__} (line {line})")
