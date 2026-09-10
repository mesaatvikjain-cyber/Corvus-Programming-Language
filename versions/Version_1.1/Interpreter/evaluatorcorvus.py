import math
import sys
import os
import random
import time
import json
import importlib
from concurrent.futures import ThreadPoolExecutor, Future

from errors import CorvusError
try:
    from std_memory import _global_mem_manager
    from std_ffi import FFIEngine
    from std_concurrency import _global_crow_engine
except ImportError:
    from .std_memory import _global_mem_manager
    from .std_ffi import FFIEngine
    from .std_concurrency import _global_crow_engine
from astnodes import (
    ProgramNode, LiteralNode, IdentifierNode, ListNode, TupleNode, DictNode,
    BinOpNode, UnaryOpNode, SafeNavNode, IndexAccessNode, MethodCallNode,
    VarDeclNode, ConstDeclNode, AssignmentNode, BlockNode, IfNode, WhileNode,
    ForNode, BreakNode, ContinueNode, PassNode, GivoutNode, FuncDeclNode,
    LambdaNode, FuncCallNode, ClassDeclNode, GlobalNode, GetNode, AwaitNode,
    TryErrorNode, InputNode
)


class Environment:
    def __init__(self, parent=None):
        self.values = {}       # Stores variable values
        self.types = {}        # Stores declared types
        self.constants = set() # Tracks immutable variables defined with `const`
        self.parent = parent   # Link to outer scope

    def define(self, name: str, value, var_type: str, is_const: bool = False):
        if name in self.values:
            raise CorvusError(
                error_type="Corvus NameError",
                message=f"Variable '{name}' is already declared in this scope.",
                suggestion="Use a different variable name or assign to the existing variable without re-declaring."
            )

        self.values[name] = value
        self.types[name] = var_type
        if is_const:
            self.constants.add(name)

    def assign(self, name: str, value):
        if name in self.values:
            if name in self.constants:
                raise CorvusError(
                    error_type="Corvus TypeError",
                    message=f"Cannot reassign constant '{name}'.",
                    suggestion="Declare the identifier with 'set <type>;' if you need it to be mutable."
                )
            self.values[name] = value
            return

        if self.parent:
            self.parent.assign(name, value)
            return

        raise CorvusError(
            error_type="Corvus NameError",
            message=f"Cannot assign to undefined variable '{name}'.",
            suggestion=f"Declare '{name}' using 'set <type>; {name} = ...' before assigning to it."
        )

    def get(self, name: str):
        if name in self.values:
            return self.values[name]
        if self.parent:
            return self.parent.get(name)
        raise CorvusError(
            error_type="Corvus NameError",
            message=f"Undefined variable '{name}'.",
            suggestion=f"Verify that '{name}' is declared and spelled correctly in this scope."
        )

    def get_type(self, name: str):
        if name in self.types:
            return self.types[name]
        if self.parent:
            return self.parent.get_type(name)
        return None


class ReturnException(Exception):
    def __init__(self, value):
        self.value = value


class BreakException(Exception):
    pass


class ContinueException(Exception):
    pass


class CorvusClass:
    def __init__(self, name: str, body: BlockNode, closure_env: Environment):
        self.name = name
        self.body = body
        self.closure_env = closure_env

    def instantiate(self, evaluator, args):
        instance = CorvusInstance(self)
        class_env = Environment(parent=self.closure_env)
        class_env.define("self", instance, "any")

        prev_env = evaluator.env
        evaluator.env = class_env
        try:
            for stmt in self.body.statements:
                evaluator.visit(stmt)
            instance.fields = class_env.values
        finally:
            evaluator.env = prev_env

        if "init" in instance.fields and callable(instance.fields["init"]):
            instance.call_method(evaluator, "init", args)

        return instance


class CorvusInstance:
    def __init__(self, corvus_class: CorvusClass):
        self.corvus_class = corvus_class
        self.fields = {}

    def call_method(self, evaluator, method_name: str, args):
        if method_name in self.fields:
            fn = self.fields[method_name]
            if callable(fn):
                prev_env = evaluator.env
                method_env = Environment(parent=prev_env)
                method_env.define("self", self, "any")
                evaluator.env = method_env
                try:
                    return fn(*args)
                finally:
                    evaluator.env = prev_env
            return fn
        raise CorvusError(
            error_type="Corvus AttributeError",
            message=f"Object of class '{self.corvus_class.name}' has no attribute or method '{method_name}'.",
            suggestion=f"Ensure method '{method_name}' is declared inside class '{self.corvus_class.name}'."
        )


class ModuleNamespace:
    def __init__(self, name: str, symbols: dict):
        self.name = name
        self.symbols = symbols
        for k, v in symbols.items():
            setattr(self, k, v)


class Evaluator:
    def __init__(self, global_env: Environment):
        self.global_env = global_env
        self.env = global_env
        self.executor = ThreadPoolExecutor(max_workers=8)
        self._setup_builtins()

    def _setup_builtins(self):
        self.global_env.define("log", lambda *args: print(*args), "func")
        self.global_env.define("str", lambda val: str(val), "func")
        self.global_env.define("int", lambda val: int(val), "func")
        self.global_env.define("flo", lambda val: float(val), "func")
        self.global_env.define("bool", lambda val: bool(val), "func")
        self.global_env.define("len", lambda val: len(val), "func")
        
        # Expanded Python Built-in Utility Functions
        def corvus_type(val):
            if val is None: return "null"
            if isinstance(val, bool): return "bool"
            if isinstance(val, int): return "int"
            if isinstance(val, float): return "flo"
            if isinstance(val, str): return "str"
            if isinstance(val, list): return "lis"
            if isinstance(val, tuple): return "tup"
            if isinstance(val, dict): return "dic"
            if callable(val): return "func"
            return type(val).__name__

        self.global_env.define("type", corvus_type, "func")
        self.global_env.define("range", lambda *args: list(range(*args)), "func")
        self.global_env.define("sum", lambda lis: sum(lis), "func")
        self.global_env.define("min", lambda *args: min(*args) if len(args) > 1 else min(args[0]), "func")
        self.global_env.define("max", lambda *args: max(*args) if len(args) > 1 else max(args[0]), "func")
        self.global_env.define("abs", lambda val: abs(val), "func")
        self.global_env.define("round", lambda val, n=0: round(val, n), "func")
        self.global_env.define("any", lambda lis: any(lis), "func")
        self.global_env.define("all", lambda lis: all(lis), "func")
        self.global_env.define("reversed", lambda lis: list(reversed(lis)), "func")
        self.global_env.define("sorted", lambda lis, rev=False: sorted(lis, reverse=rev), "func")
        self.global_env.define("enumerate", lambda lis: list(enumerate(lis)), "func")

        # Corvus Enterprise Built-in Modules
        self.global_env.define("mem", ModuleNamespace("mem", {
            "alloc": lambda *args: _global_mem_manager.alloc(*args),
            "free": lambda *args: _global_mem_manager.free(*args),
            "stats": lambda *args: _global_mem_manager.stats(),
            "refcount": lambda *args: _global_mem_manager.refcount(*args)
        }), "any")

        self.global_env.define("ffi", ModuleNamespace("ffi", {
            "load": lambda *args: FFIEngine.load(*args),
            "bind": lambda *args: FFIEngine.bind(*args),
            "call": lambda *args: FFIEngine.call(*args)
        }), "any")

        self.global_env.define("crow", ModuleNamespace("crow", {
            "fly": lambda *args: _global_crow_engine.fly(*args),
            "flock": lambda *args: _global_crow_engine.flock(args[0] if args else []),
            "channel": lambda *args: _global_crow_engine.channel()
        }), "any")


    def evaluate(self, node):
        return self.visit(node)

    def visit(self, node):
        method_name = f"visit_{type(node).__name__}"
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise CorvusError(
            error_type="Corvus RuntimeError",
            message=f"No execution rule defined for AST node '{type(node).__name__}'",
            suggestion="Verify this language feature is supported by the runtime engine."
        )

    def _validate_type(self, expected_type: str, val, var_name: str):
        if val is None or expected_type in ("any", "const"):
            return

        type_matches = True
        if expected_type == "int":
            type_matches = isinstance(val, int) and not isinstance(val, bool)
        elif expected_type == "flo":
            type_matches = isinstance(val, (float, int)) and not isinstance(val, bool)
        elif expected_type == "str":
            type_matches = isinstance(val, str)
        elif expected_type == "bool":
            type_matches = isinstance(val, bool)
        elif expected_type == "lis":
            type_matches = isinstance(val, list)
        elif expected_type == "tup":
            type_matches = isinstance(val, tuple)
        elif expected_type == "dic":
            type_matches = isinstance(val, dict)
        elif expected_type in ("func", "lmb"):
            type_matches = callable(val) or isinstance(val, Future)

        if not type_matches:
            actual_type = type(val).__name__
            if isinstance(val, bool): actual_type = "bool"
            elif isinstance(val, int): actual_type = "int"
            elif isinstance(val, float): actual_type = "flo"
            elif isinstance(val, str): actual_type = "str"
            elif isinstance(val, list): actual_type = "lis"
            elif isinstance(val, tuple): actual_type = "tup"
            elif isinstance(val, dict): actual_type = "dic"

            raise CorvusError(
                error_type="Corvus TypeError",
                message=f"Type mismatch for variable '{var_name}': expected type '{expected_type}', but got '{actual_type}' ({repr(val)}).",
                suggestion=f"Ensure the assigned value matches the declared type '{expected_type}'."
            )

    def visit_LiteralNode(self, node: LiteralNode):
        return node.value

    def visit_IdentifierNode(self, node: IdentifierNode):
        return self.env.get(node.name)

    def visit_ListNode(self, node: ListNode):
        return [self.visit(elem) for elem in node.elements]

    def visit_TupleNode(self, node: TupleNode):
        return tuple(self.visit(elem) for elem in node.elements)

    def visit_DictNode(self, node: DictNode):
        d = {}
        for k_node, v_node in zip(node.keys, node.values):
            k = self.visit(k_node)
            v = self.visit(v_node)
            d[k] = v
        return d

    def visit_UnaryOpNode(self, node: UnaryOpNode):
        val = self.visit(node.operand)
        if node.op == '-':
            return -val
        elif node.op == 'not':
            return not bool(val)
        return val

    def visit_BinOpNode(self, node: BinOpNode):
        left = self.visit(node.left)
        right = self.visit(node.right)
        op = node.op

        if op == '+':   return left + right
        if op == '-':   return left - right
        if op == '*':   return left * right
        if op == '/':
            if right == 0:
                raise CorvusError(
                    error_type="Corvus MathError",
                    message="Division by zero.",
                    suggestion="Ensure your denominator expression evaluates to a non-zero number."
                )
            return left / right
        if op == '%':   return left % right
        if op == '**':  return left ** right
        if op == '==':  return left == right
        if op == '!=':  return left != right
        if op == '<':   return left < right
        if op == '>':   return left > right
        if op == '<=':  return left <= right
        if op == '>=':  return left >= right
        if op == 'and': return left and right
        if op == 'or':  return left or right
        if op == 'xor': return bool(left) ^ bool(right)
        if op == '??':  return left if left is not None else right

        raise CorvusError(
            error_type="Corvus RuntimeError",
            message=f"Unsupported operator '{op}'.",
            suggestion="Check if this operator is supported in Corvus."
        )

    def visit_IndexAccessNode(self, node: IndexAccessNode):
        target = self.visit(node.target)
        index = self.visit(node.index)
        try:
            return target[index]
        except IndexError:
            raise CorvusError(
                error_type="Corvus IndexError",
                message=f"Index {index} is out of bounds for collection of length {len(target)}.",
                suggestion="Verify the index bounds before accessing collection elements."
            )
        except KeyError:
            raise CorvusError(
                error_type="Corvus KeyError",
                message=f"Key '{index}' not found in dictionary.",
                suggestion="Check that the key exists in the dictionary before accessing."
            )
        except TypeError:
            raise CorvusError(
                error_type="Corvus TypeError",
                message=f"Type '{type(target).__name__}' does not support indexing.",
                suggestion="Index access is only valid on lists, tuples, dictionaries, and strings."
            )

    def visit_MethodCallNode(self, node: MethodCallNode):
        target = self.visit(node.target)
        method_name = node.method_name
        args = [self.visit(a) for a in node.args]

        if isinstance(target, list):
            if method_name == 'add':
                target.append(args[0])
                return target
            elif method_name == 'remove':
                target.remove(args[0])
                return target
            elif method_name == 'pop':
                idx = args[0] if args else -1
                return target.pop(idx)
            elif method_name in ('len', 'length'):
                return len(target)
            elif method_name == 'clear':
                target.clear()
                return target
            elif method_name == 'map' and args and callable(args[0]):
                return [args[0](item) for item in target]
            elif method_name == 'filter' and args and callable(args[0]):
                return [item for item in target if args[0](item)]

        if isinstance(target, str):
            if method_name in ('len', 'length'):
                return len(target)
            elif method_name == 'upper':
                return target.upper()
            elif method_name == 'lower':
                return target.lower()
            elif method_name == 'trim':
                return target.strip()
            elif method_name == 'split':
                delim = args[0] if args else None
                return target.split(delim)

        if isinstance(target, (tuple, dict)):
            if method_name in ('len', 'length'):
                return len(target)

            if isinstance(target, dict):
                if method_name == 'keys':
                    return list(target.keys())
                elif method_name == 'values':
                    return list(target.values())

        if isinstance(target, CorvusInstance):
            return target.call_method(self, method_name, args)

        if hasattr(target, method_name):
            fn = getattr(target, method_name)
            if callable(fn):
                return fn(*args)
            return fn

        raise CorvusError(
            error_type="Corvus AttributeError",
            message=f"Type '{type(target).__name__}' has no method or attribute '{method_name}'.",
            suggestion=f"Check that method '{method_name}' is supported on this data structure."
        )

    def visit_SafeNavNode(self, node: SafeNavNode):
        target = self.visit(node.target)
        if target is None:
            return None
        if isinstance(target, CorvusInstance):
            return target.fields.get(node.property_name, None)
        if isinstance(target, dict):
            return target.get(node.property_name, None)
        if isinstance(target, ModuleNamespace):
            return getattr(target, node.property_name, None)
        return getattr(target, node.property_name, None)

    def visit_ProgramNode(self, node: ProgramNode):
        result = None
        for stmt in node.statements:
            result = self.visit(stmt)
        return result

    def visit_BlockNode(self, node: BlockNode):
        prev_env = self.env
        self.env = Environment(parent=prev_env)
        try:
            result = None
            for stmt in node.statements:
                result = self.visit(stmt)
            return result
        finally:
            self.env = prev_env

    def visit_VarDeclNode(self, node: VarDeclNode):
        val = self.visit(node.value) if node.value else None
        if val is not None:
            self._validate_type(node.var_type, val, node.name)
        self.env.define(node.name, val, node.var_type, is_const=False)
        return val

    def visit_ConstDeclNode(self, node: ConstDeclNode):
        val = self.visit(node.value)
        self.env.define(node.name, val, "const", is_const=True)
        return val

    def visit_AssignmentNode(self, node: AssignmentNode):
        val = self.visit(node.value)
        target = node.target

        if isinstance(target, str):
            expected_type = self.env.get_type(target)
            if expected_type and expected_type != "any":
                self._validate_type(expected_type, val, target)
            self.env.assign(target, val)
        elif isinstance(target, IdentifierNode):
            expected_type = self.env.get_type(target.name)
            if expected_type and expected_type != "any":
                self._validate_type(expected_type, val, target.name)
            self.env.assign(target.name, val)
        elif isinstance(target, MethodCallNode):
            obj = self.visit(target.target)
            prop = target.method_name
            if isinstance(obj, CorvusInstance):
                obj.fields[prop] = val
            elif isinstance(obj, dict):
                obj[prop] = val
            else:
                setattr(obj, prop, val)
        elif isinstance(target, IndexAccessNode):
            obj = self.visit(target.target)
            idx = self.visit(target.index)
            obj[idx] = val
        else:
            raise CorvusError(
                error_type="Corvus AssignmentError",
                message=f"Invalid target for assignment: {type(target).__name__}",
                suggestion="Assignment target must be a variable, object property, or index position."
            )
        return val

    def visit_IfNode(self, node: IfNode):
        if self.visit(node.condition):
            return self.visit(node.then_block)

        for cond, branch in node.elsif_branches:
            if self.visit(cond):
                return self.visit(branch)

        if node.else_block:
            return self.visit(node.else_block)

        return None

    def visit_WhileNode(self, node: WhileNode):
        while self.visit(node.condition):
            try:
                self.visit(node.body)
            except BreakException:
                break
            except ContinueException:
                continue

    def visit_ForNode(self, node: ForNode):
        iterable = self.visit(node.collection)
        for item in iterable:
            prev_env = self.env
            self.env = Environment(parent=prev_env)
            self.env.define(node.iterator, item, "any")
            try:
                self.visit(node.body)
            except BreakException:
                self.env = prev_env
                break
            except ContinueException:
                self.env = prev_env
                continue
            finally:
                self.env = prev_env

    def visit_BreakNode(self, node: BreakNode):
        raise BreakException()

    def visit_ContinueNode(self, node: ContinueNode):
        raise ContinueException()

    def visit_PassNode(self, node: PassNode):
        return None

    def visit_GivoutNode(self, node: GivoutNode):
        val = self.visit(node.value) if node.value else None
        raise ReturnException(val)

    def visit_FuncDeclNode(self, node: FuncDeclNode):
        closure_env = self.env
        def user_func(*args):
            func_env = Environment(parent=closure_env)
            for param, arg in zip(node.params, args):
                func_env.define(param, arg, "any")

            evaluator_thread = Evaluator(func_env)
            evaluator_thread.executor = self.executor
            try:
                evaluator_thread.visit(node.body)
            except ReturnException as ret:
                return ret.value
            return None

        if getattr(node, 'is_async', False):
            def async_wrapper(*args):
                return self.executor.submit(user_func, *args)
            self.env.define(node.name, async_wrapper, "func")
        else:
            self.env.define(node.name, user_func, "func")

    def visit_LambdaNode(self, node: LambdaNode):
        closure_env = self.env
        def lambda_func(*args):
            lmb_env = Environment(parent=closure_env)
            for param, arg in zip(node.params, args):
                lmb_env.define(param, arg, "any")

            evaluator_thread = Evaluator(lmb_env)
            evaluator_thread.executor = self.executor
            try:
                return evaluator_thread.visit(node.body)
            except ReturnException as ret:
                return ret.value
        return lambda_func

    def visit_ClassDeclNode(self, node: ClassDeclNode):
        corvus_class = CorvusClass(node.name, node.body, self.env)
        def constructor(*args):
            return corvus_class.instantiate(self, args)
        self.env.define(node.name, constructor, "cls")

    def visit_FuncCallNode(self, node: FuncCallNode):
        callee = self.visit(node.callee) if not isinstance(node.callee, IdentifierNode) else self.env.get(node.callee.name)
        args = [self.visit(a) for a in node.args]

        if not callable(callee):
            raise CorvusError(
                error_type="Corvus TypeError",
                message=f"'{getattr(node.callee, 'name', 'expression')}' is not callable.",
                suggestion="Make sure the identifier is declared as a function before calling it with '()'."
            )
        return callee(*args)

    def visit_GetNode(self, node: GetNode):
        mod_name = node.module_name
        if mod_name == "math":
            math_symbols = {
                "sqrt": math.sqrt,
                "pow": math.pow,
                "sin": math.sin,
                "cos": math.cos,
                "tan": math.tan,
                "pi": math.pi,
                "floor": math.floor,
                "ceil": math.ceil,
                "abs": abs,
                "log": math.log,
                "exp": math.exp,
                "radians": math.radians,
                "degrees": math.degrees,
                "factorial": math.factorial,
                "gcd": math.gcd
            }
            mod_obj = ModuleNamespace("math", math_symbols)
            self.env.define("math", mod_obj, "module")

        elif mod_name == "system":
            sys_symbols = {
                "os": os.name,
                "args": sys.argv,
                "exit": sys.exit,
                "platform": sys.platform,
                "version": sys.version,
                "getenv": os.getenv
            }
            mod_obj = ModuleNamespace("system", sys_symbols)
            self.env.define("system", mod_obj, "module")

        elif mod_name == "random":
            rand_symbols = {
                "randint": random.randint,
                "choice": random.choice,
                "random": random.random,
                "shuffle": random.shuffle,
                "sample": random.sample,
                "uniform": random.uniform,
                "randrange": random.randrange
            }
            mod_obj = ModuleNamespace("random", rand_symbols)
            self.env.define("random", mod_obj, "module")

        elif mod_name == "time":
            time_symbols = {
                "time": time.time,
                "sleep": time.sleep,
                "ctime": time.ctime,
                "stamp": lambda: int(time.time())
            }
            mod_obj = ModuleNamespace("time", time_symbols)
            self.env.define("time", mod_obj, "module")

        elif mod_name == "json":
            json_symbols = {
                "dumps": json.dumps,
                "loads": json.loads,
                "stringify": json.dumps,
                "parse": json.loads
            }
            mod_obj = ModuleNamespace("json", json_symbols)
            self.env.define("json", mod_obj, "module")

        elif mod_name == "file":
            def file_read(path):
                with open(path, "r", encoding="utf-8") as f:
                    return f.read()

            def file_write(path, content):
                with open(path, "w", encoding="utf-8") as f:
                    f.write(str(content))
                return True

            def file_append(path, content):
                with open(path, "a", encoding="utf-8") as f:
                    f.write(str(content))
                return True

            def file_lines(path):
                with open(path, "r", encoding="utf-8") as f:
                    return [line.rstrip("\n") for line in f]

            file_symbols = {
                "read": file_read,
                "write": file_write,
                "append": file_append,
                "lines": file_lines,
                "exists": os.path.exists,
                "remove": os.remove
            }
            mod_obj = ModuleNamespace("file", file_symbols)
            self.env.define("file", mod_obj, "module")

        elif mod_name == "gui":
            def gui_alert(title, msg=""):
                try:
                    import tkinter.messagebox as mb
                    mb.showinfo(str(title), str(msg))
                except Exception:
                    print(f"[GUI Alert] {title}: {msg}")
                return True

            def gui_prompt(title, prompt_str=""):
                try:
                    import tkinter.simpledialog as sd
                    return sd.askstring(str(title), str(prompt_str))
                except Exception:
                    return input(f"{title} ({prompt_str}): ")

            def gui_info(msg):
                return gui_alert("Corvus Info", msg)

            gui_symbols = {
                "alert": gui_alert,
                "prompt": gui_prompt,
                "info": gui_info
            }
            mod_obj = ModuleNamespace("gui", gui_symbols)
            self.env.define("gui", mod_obj, "module")

        elif mod_name == "http":
            def validate_url(url: str) -> str:
                import re
                from urllib.parse import urlparse, urlunparse
                try:
                    url_str = str(url)
                    if "/../" in url_str or re.search(r"/%2e%2e/", url_str, re.IGNORECASE):
                        raise ValueError("Invalid path")
                    parsed = urlparse(url_str)
                    if parsed.scheme not in ("http", "https"):
                        raise ValueError("Invalid protocol")
                    if not parsed.hostname:
                        raise ValueError("Invalid host")
                    allowed_domains = ["example.com"]  # add your allowed domains here
                    if parsed.hostname.lower() not in allowed_domains:
                        raise ValueError("Invalid host")
                    return urlunparse(parsed)
                except Exception:
                    raise ValueError("Invalid URL")

            def http_get(url):
                import urllib.request
                validated_url = validate_url(url)
                req = urllib.request.urlopen(validated_url)
                return req.read().decode("utf-8")

            def http_post(url, data=""):
                import urllib.request
                validated_url = validate_url(url)
                encoded = str(data).encode("utf-8")
                req = urllib.request.Request(validated_url, data=encoded, headers={"Content-Type": "application/json"})
                res = urllib.request.urlopen(req)
                return res.read().decode("utf-8")

            def http_download(url, filename):
                import urllib.request
                validated_url = validate_url(url)
                urllib.request.urlretrieve(validated_url, str(filename))
                return True

            http_symbols = {
                "get": http_get,
                "post": http_post,
                "download": http_download
            }
            mod_obj = ModuleNamespace("http", http_symbols)
            self.env.define("http", mod_obj, "module")

        elif mod_name == "process":
            def process_run(cmd):
                import subprocess
                res = subprocess.run(str(cmd), shell=True, capture_output=True, text=True)
                return res.stdout.strip()

            def process_shell(cmd):
                import subprocess
                res = subprocess.run(str(cmd), shell=True, capture_output=True, text=True)
                return {"stdout": res.stdout, "stderr": res.stderr, "code": res.returncode}

            def process_cwd():
                return os.getcwd()

            proc_symbols = {
                "run": process_run,
                "shell": process_shell,
                "cwd": process_cwd
            }
            mod_obj = ModuleNamespace("process", proc_symbols)
            self.env.define("process", mod_obj, "module")


        else:
            # 1. First attempt to load a Corvus package from corvus_modules/ or global package store
            if self._try_load_corvus_package(mod_name):
                return

            # 2. Universal Python Module Bridge fallback: dynamically import any Python library
            try:
                py_mod = importlib.import_module(mod_name)
                mod_symbols = {
                    attr: getattr(py_mod, attr)
                    for attr in dir(py_mod)
                    if not attr.startswith("__")
                }
                mod_obj = ModuleNamespace(mod_name, mod_symbols)
                self.env.define(mod_name, mod_obj, "module")
            except ImportError:
                raise CorvusError(
                    error_type="Corvus ModuleError",
                    message=f"Module or Corvus package '{mod_name}' could not be loaded.",
                    suggestion=f"Ensure '{mod_name}' is installed via 'cpm install {mod_name}' or available in Python."
                )

    def _try_load_corvus_package(self, mod_name: str) -> bool:
        search_dirs = [
            os.path.join(os.getcwd(), "corvus_modules", mod_name),
            os.path.expanduser(os.path.join("~", ".corvus", "packages", mod_name))
        ]

        current_script = getattr(self, "current_file_path", None)
        if current_script:
            script_dir = os.path.dirname(os.path.abspath(current_script))
            search_dirs.insert(0, os.path.join(script_dir, "corvus_modules", mod_name))

        package_dir = None
        for s_dir in search_dirs:
            if os.path.isdir(s_dir):
                package_dir = s_dir
                break

        if not package_dir:
            return False

        entry_file = None
        manifest_path = os.path.join(package_dir, "corvus.json")
        if os.path.exists(manifest_path):
            try:
                with open(manifest_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    main_rel = data.get("main", "main.crv")
                    entry_file = os.path.join(package_dir, main_rel)
            except Exception:
                pass

        if not entry_file or not os.path.exists(entry_file):
            for candidate in ["main.crv", f"{mod_name}.crv", "index.crv"]:
                cand_path = os.path.join(package_dir, candidate)
                if os.path.exists(cand_path):
                    entry_file = cand_path
                    break

        if not entry_file or not os.path.exists(entry_file):
            return False

        try:
            with open(entry_file, "r", encoding="utf-8") as f:
                code = f.read()

            from lexercorvus import tokenize
            from parsercorvus import Parser

            tokens = tokenize(code)
            parser = Parser(tokens)
            ast = parser.parse()

            pkg_env = Environment(parent=self.global_env)
            pkg_evaluator = Evaluator(pkg_env)
            pkg_evaluator.current_file_path = entry_file
            pkg_evaluator.evaluate(ast)

            mod_symbols = {k: v for k, v in pkg_env.values.items()}
            mod_obj = ModuleNamespace(mod_name, mod_symbols)
            self.env.define(mod_name, mod_obj, "module")
            return True
        except Exception as e:
            raise CorvusError(
                error_type="Corvus PackageError",
                message=f"Failed to load Corvus package '{mod_name}' from '{entry_file}': {str(e)}",
                suggestion="Verify the syntax and structure of the Corvus package."
            )



    def visit_TryErrorNode(self, node: TryErrorNode):
        res = None
        try:
            res = self.visit(node.try_block)
        except Exception as err:
            if node.error_block:
                prev_env = self.env
                self.env = Environment(parent=prev_env)
                err_msg = getattr(err, 'message', str(err))
                err_type = getattr(err, 'error_type', 'Error')
                err_obj = {"message": err_msg, "type": err_type}
                if node.error_var:
                    self.env.define(node.error_var, err_obj, "dic")
                try:
                    res = self.visit(node.error_block)
                finally:
                    self.env = prev_env
        finally:
            if node.final_block:
                self.visit(node.final_block)
        return res

    def visit_GlobalNode(self, node: GlobalNode):
        return self.global_env.get(node.name)

    def visit_AwaitNode(self, node: AwaitNode):
        target_val = self.visit(node.target)
        if hasattr(target_val, 'result') and callable(target_val.result):
            return target_val.result()
        return target_val

    def visit_InputNode(self, node: InputNode):
        prompt_text = ""
        if node.prompt is not None:
            prompt_text = str(self.visit(node.prompt))
        return input(prompt_text)

    def visit_PipelineNode(self, node: PipelineNode):
        left_val = self.visit(node.left)
        if isinstance(node.right, FuncCallNode):
            callee = self.visit(node.right.callee) if not isinstance(node.right.callee, IdentifierNode) else self.env.get(node.right.callee.name)
            args = [left_val] + [self.visit(a) for a in node.right.args]
            return callee(*args)
        elif isinstance(node.right, MethodCallNode):
            method_name = node.right.method_name
            args = [self.visit(a) for a in node.right.args]
            mock_call = MethodCallNode(target=LiteralNode(value=left_val), method_name=method_name, args=[LiteralNode(value=a) for a in args])
            return self.visit_MethodCallNode(mock_call)
        else:
            right_val = self.visit(node.right)
            if callable(right_val):
                return right_val(left_val)
            return right_val

    def visit_MatchNode(self, node: MatchNode):
        target_val = self.visit(node.target)
        for case in node.cases:
            pattern_val = self.visit(case.pattern)
            if target_val == pattern_val:
                return self.visit(case.body)
        if node.default_branch:
            return self.visit(node.default_branch)
        return None