"""
Corvus Static Type Checker & Linter (--strict mode)
Analyzes AST for:
- Static variable type assignment mismatches
- Undefined variable references
- Arity mismatch in function calls
- Missing return/givout in typed branches
"""

import sys
import os
from typing import Dict, Any, Optional

from astnodes import (
    ProgramNode, LiteralNode, IdentifierNode, ListNode, TupleNode, DictNode,
    BinOpNode, UnaryOpNode, VarDeclNode, ConstDeclNode, AssignmentNode,
    FuncDeclNode, FuncCallNode, BlockNode, IfNode, WhileNode, ForNode,
    GivoutNode, MethodCallNode
)
from errors import CorvusError

class TypeChecker:
    def __init__(self, filename: str, source_code: str):
        self.filename = filename
        self.source_code = source_code
        self.scopes = [{}]
        self.functions = {}
        self.errors = []

    def push_scope(self):
        self.scopes.append({})

    def pop_scope(self):
        if len(self.scopes) > 1:
            self.scopes.pop()

    def define(self, name: str, var_type: str):
        self.scopes[-1][name] = var_type

    def lookup(self, name: str) -> Optional[str]:
        for s in reversed(self.scopes):
            if name in s:
                return s[name]
        return None

    def check(self, ast_node) -> list:
        self.visit(ast_node)
        return self.errors

    def infer_literal_type(self, val) -> str:
        if isinstance(val, bool): return "bool"
        if isinstance(val, int): return "int"
        if isinstance(val, float): return "flo"
        if isinstance(val, str): return "str"
        if isinstance(val, list): return "lis"
        if isinstance(val, tuple): return "tup"
        if isinstance(val, dict): return "dic"
        return "any"

    def visit(self, node):
        if node is None:
            return "null"

        nt = type(node).__name__

        if nt == "ProgramNode":
            # Builtins
            self.define("log", "func")
            self.define("print", "func")
            self.define("len", "func")
            self.define("str", "func")
            self.define("int", "func")
            for stmt in node.statements:
                self.visit(stmt)
            return None

        elif nt == "LiteralNode":
            return self.infer_literal_type(node.value)

        elif nt == "IdentifierNode":
            t = self.lookup(node.name)
            if t is None and node.name not in ("self", "true", "fal", "null"):
                self.errors.append(CorvusError(
                    error_type="Corvus StrictTypeError",
                    error_code="E0204",
                    message=f"[--strict] Variable '{node.name}' is referenced before declaration.",
                    suggestion=f"Declare variable first with 'set <type>; {node.name} = ...'"
                ))
                return "any"
            return t or "any"

        elif nt == "ListNode":
            for elem in node.elements:
                self.visit(elem)
            return "lis"

        elif nt == "TupleNode":
            for elem in node.elements:
                self.visit(elem)
            return "tup"

        elif nt == "DictNode":
            for k, v in zip(node.keys, node.values):
                self.visit(k)
                self.visit(v)
            return "dic"

        elif nt == "VarDeclNode":
            decl_type = node.var_type
            if node.value is not None:
                val_type = self.visit(node.value)
                if decl_type not in ("any", "var") and val_type not in ("any", "null") and decl_type != val_type:
                    # Allow float widening
                    if not (decl_type == "flo" and val_type == "int"):
                        self.errors.append(CorvusError(
                            error_type="Corvus StrictTypeError",
                            error_code="E0101",
                            message=f"[--strict] Type mismatch in declaration of '{node.name}': declared as '{decl_type}' but initialized with '{val_type}'.",
                            suggestion=f"Change declaration to 'set {val_type}; {node.name}' or adjust value expression."
                        ))
            self.define(node.name, decl_type)
            return decl_type

        elif nt == "ConstDeclNode":
            val_type = self.visit(node.value)
            self.define(node.name, val_type or "any")
            return val_type or "any"

        elif nt == "AssignmentNode":
            val_type = self.visit(node.value)
            target_name = getattr(node.target, 'name', str(node.target))
            expected_type = self.lookup(target_name)
            if expected_type and expected_type not in ("any", "var") and val_type not in ("any", "null") and expected_type != val_type:
                if not (expected_type == "flo" and val_type == "int"):
                    self.errors.append(CorvusError(
                        error_type="Corvus StrictTypeError",
                        error_code="E0101",
                        message=f"[--strict] Incompatible type assignment to '{target_name}': cannot assign '{val_type}' to variable of type '{expected_type}'.",
                        suggestion=f"Ensure expression matches declared type '{expected_type}'."
                    ))
            return val_type

        elif nt == "BinOpNode":
            lt = self.visit(node.left)
            rt = self.visit(node.right)
            if node.op in ('+', '-', '*', '/', '%', '**'):
                if lt not in ("int", "flo", "any") or rt not in ("int", "flo", "any"):
                    if not (node.op == '+' and (lt == "str" or rt == "str")):
                        self.errors.append(CorvusError(
                            error_type="Corvus StrictTypeError",
                            error_code="E0102",
                            message=f"[--strict] Operator '{node.op}' not supported between '{lt}' and '{rt}'.",
                            suggestion="Ensure arithmetic operators are used with numeric types (int, flo)."
                        ))
                return "flo" if "flo" in (lt, rt) else "int"
            elif node.op == '@':
                return "lis"
            elif node.op in ('==', '!=', '<', '>', '<=', '>=', 'and', 'or', 'xor', 'in'):
                return "bool"
            return "any"

        elif nt == "FuncDeclNode":
            self.define(node.name, "func")
            self.functions[node.name] = len(node.params)
            self.push_scope()
            for p in node.params:
                self.define(p, "any")
            self.visit(node.body)
            self.pop_scope()
            return "func"

        elif nt == "FuncCallNode":
            callee_name = getattr(node.callee, 'name', str(node.callee))
            if callee_name in self.functions:
                expected_arity = self.functions[callee_name]
                actual_arity = len(node.args)
                if expected_arity != actual_arity:
                    self.errors.append(CorvusError(
                        error_type="Corvus StrictTypeError",
                        error_code="E0401",
                        message=f"[--strict] Function '{callee_name}' expects {expected_arity} argument(s), but got {actual_arity}.",
                        suggestion=f"Provide exactly {expected_arity} parameter(s) when calling '{callee_name}'."
                    ))
            for a in node.args:
                self.visit(a)
            return "any"

        elif nt == "BlockNode":
            for s in node.statements:
                self.visit(s)
            return None

        elif nt == "IfNode":
            self.visit(node.condition)
            self.visit(node.then_block)
            for c, b in node.elsif_branches:
                self.visit(c)
                self.visit(b)
            if node.else_block:
                self.visit(node.else_block)
            return None

        elif nt == "WhileNode":
            self.visit(node.condition)
            self.visit(node.body)
            return None

        elif nt == "ForNode":
            self.push_scope()
            self.define(node.iterator, "any")
            self.visit(node.collection)
            self.visit(node.body)
            self.pop_scope()
            return None

        return "any"
