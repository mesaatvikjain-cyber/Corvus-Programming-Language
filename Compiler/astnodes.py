from dataclasses import dataclass
from typing import Any, List, Optional

# Base class for all Corvus AST nodes
class ASTNode:
    pass

# Represents the entire Corvus program (a list of top-level statements)
@dataclass
class ProgramNode(ASTNode):
    statements: List[ASTNode]

# --- 1. Literals & Identifiers ---

@dataclass
class LiteralNode(ASTNode):
    value: Any  # int, float, str, bool (True/False), or None for null

@dataclass
class IdentifierNode(ASTNode):
    name: str

# --- 2. Data Structure Literals ---

@dataclass
class ListNode(ASTNode):
    elements: List[ASTNode]  # {item1, item2, ...}

@dataclass
class TupleNode(ASTNode):
    elements: List[ASTNode]  # ([item1, item2, ...])

@dataclass
class DictNode(ASTNode):
    keys: List[ASTNode]      # ("key": value)
    values: List[ASTNode]

# --- 3. Operators & Expressions ---

@dataclass
class BinOpNode(ASTNode):
    left: ASTNode
    op: str                  # +, -, *, /, %, **, ==, !=, <, >, <=, >=, and, or, xor, ??, =>
    right: ASTNode

@dataclass
class UnaryOpNode(ASTNode):
    op: str                  # not, -
    operand: ASTNode

@dataclass
class SafeNavNode(ASTNode):
    target: ASTNode          # object?.property
    property_name: str

@dataclass
class IndexAccessNode(ASTNode):
    target: ASTNode          # list[0], dic["key"], tup[1]
    index: ASTNode

@dataclass
class MethodCallNode(ASTNode):
    target: ASTNode          # numbers.add(10), name.upper()
    method_name: str
    args: List[ASTNode]

# --- 4. Declarations & Assignments ---

@dataclass
class VarDeclNode(ASTNode):
    var_type: str            # int, str, flo, bool, lis, tup, dic, func, lmb
    name: str
    value: Optional[ASTNode] # None if declared without initial value (set int; score)

@dataclass
class ConstDeclNode(ASTNode):
    name: str                # set const; NAME = value
    value: ASTNode

@dataclass
class AssignmentNode(ASTNode):
    target: str              # variable = new_value
    value: ASTNode

# --- 5. Control Flow Statements ---

@dataclass
class BlockNode(ASTNode):
    statements: List[ASTNode] # [ ... ]

@dataclass
class IfNode(ASTNode):
    condition: ASTNode       # if (condition) [ ... ]
    then_block: BlockNode
    elsif_branches: List[tuple] # List of (condition_node, block_node)
    else_block: Optional[BlockNode]

@dataclass
class WhileNode(ASTNode):
    condition: ASTNode       # while (condition) [ ... ]
    body: BlockNode

@dataclass
class ForNode(ASTNode):
    iterator: str            # for (item in collection) [ ... ]
    collection: ASTNode
    body: BlockNode

@dataclass
class BreakNode(ASTNode):
    pass                     # brk

@dataclass
class ContinueNode(ASTNode):
    pass                     # con

@dataclass
class PassNode(ASTNode):
    pass                     # pass

@dataclass
class GivoutNode(ASTNode):
    value: Optional[ASTNode] # givout expression?

# --- 6. Functions, Lambdas & Calls ---

@dataclass
class FuncDeclNode(ASTNode):
    name: str                # mk func name(params) [ ... ]
    params: List[str]
    body: BlockNode

@dataclass
class LambdaNode(ASTNode):
    params: List[str]        # lmb[params] => expr  or  lmb[params] [ ... ]
    body: ASTNode            # Can be an expression or a BlockNode

@dataclass
class FuncCallNode(ASTNode):
    callee: ASTNode          # log(...), add(5, 10), square_fn(val)
    args: List[ASTNode]

@dataclass
class InputNode(ASTNode):
    prompt: Optional[ASTNode] = None # input(prompt_expr)


# --- 7. Classes, Scope & Modules (Corvus 0.1 Targets) ---

@dataclass
class ClassDeclNode(ASTNode):
    name: str                # cls Person() [ ... ]
    body: BlockNode

@dataclass
class GlobalNode(ASTNode):
    name: str                # global(variable_name)

@dataclass
class GetNode(ASTNode):
    module_name: str         # get math, get system [os, args]
    imported_symbols: Optional[List[str]] = None

@dataclass
class AwaitNode(ASTNode):
    target: ASTNode          # awt fetchData()

# --- 8. Error Handling ---

@dataclass
class TryErrorNode(ASTNode):
    try_block: BlockNode     # try [ ... ]
    error_var: Optional[str] # error(e) [ ... ]
    error_block: Optional[BlockNode]
    final_block: Optional[BlockNode] # final [ ... ]