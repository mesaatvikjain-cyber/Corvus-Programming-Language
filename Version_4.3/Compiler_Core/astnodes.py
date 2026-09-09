from dataclasses import dataclass
from typing import Any, List, Optional

# Base class for all Corvus AST nodes
class ASTNode:
    pass

# Represents the entire Corvus program
@dataclass
class ProgramNode(ASTNode):
    statements: List[ASTNode]

# --- 1. Literals & Identifiers ---

@dataclass
class LiteralNode(ASTNode):
    value: Any

@dataclass
class IdentifierNode(ASTNode):
    name: str

# --- 2. Data Structure Literals ---

@dataclass
class ListNode(ASTNode):
    elements: List[ASTNode]

@dataclass
class TupleNode(ASTNode):
    elements: List[ASTNode]

@dataclass
class DictNode(ASTNode):
    keys: List[ASTNode]
    values: List[ASTNode]

# --- 3. Operators & Expressions ---

@dataclass
class BinOpNode(ASTNode):
    left: ASTNode
    op: str
    right: ASTNode

@dataclass
class UnaryOpNode(ASTNode):
    op: str
    operand: ASTNode

@dataclass
class SafeNavNode(ASTNode):
    target: ASTNode
    property_name: str

@dataclass
class IndexAccessNode(ASTNode):
    target: ASTNode
    index: ASTNode

@dataclass
class MethodCallNode(ASTNode):
    target: ASTNode
    method_name: str
    args: List[ASTNode]

# --- 4. Declarations & Assignments ---

@dataclass
class VarDeclNode(ASTNode):
    var_type: str
    name: str
    value: Optional[ASTNode]

@dataclass
class ConstDeclNode(ASTNode):
    name: str
    value: ASTNode

@dataclass
class AssignmentNode(ASTNode):
    target: Any
    value: ASTNode

# --- 5. Control Flow Statements ---

@dataclass
class BlockNode(ASTNode):
    statements: List[ASTNode]

@dataclass
class CaseNode(ASTNode):
    pattern: ASTNode
    body: ASTNode

@dataclass
class MatchNode(ASTNode):
    target: ASTNode
    cases: List[CaseNode]
    default_branch: Optional[ASTNode] = None

@dataclass
class PipelineNode(ASTNode):
    left: ASTNode
    right: ASTNode

@dataclass
class IfNode(ASTNode):
    condition: ASTNode
    then_block: BlockNode
    elsif_branches: List[tuple]
    else_block: Optional[BlockNode]

@dataclass
class WhileNode(ASTNode):
    condition: ASTNode
    body: BlockNode

@dataclass
class ForNode(ASTNode):
    iterator: str
    collection: ASTNode
    body: BlockNode

@dataclass
class BreakNode(ASTNode):
    pass

@dataclass
class ContinueNode(ASTNode):
    pass

@dataclass
class PassNode(ASTNode):
    pass

@dataclass
class GivoutNode(ASTNode):
    value: Optional[ASTNode]

# --- 6. Functions, Lambdas & Calls ---

@dataclass
class FuncDeclNode(ASTNode):
    name: str
    params: List[str]
    body: BlockNode
    is_async: bool = False

@dataclass
class LambdaNode(ASTNode):
    params: List[str]
    body: ASTNode

@dataclass
class FuncCallNode(ASTNode):
    callee: ASTNode
    args: List[ASTNode]

@dataclass
class InputNode(ASTNode):
    prompt: Optional[ASTNode] = None

# --- 7. Classes, Scope & Modules ---

@dataclass
class ClassDeclNode(ASTNode):
    name: str
    body: BlockNode

@dataclass
class GlobalNode(ASTNode):
    name: str

@dataclass
class GetNode(ASTNode):
    module_name: str
    imported_symbols: Optional[List[str]] = None

@dataclass
class AwaitNode(ASTNode):
    target: ASTNode

# --- 8. Error Handling ---

@dataclass
class TryErrorNode(ASTNode):
    try_block: BlockNode
    error_var: Optional[str]
    error_block: Optional[BlockNode]
    final_block: Optional[BlockNode]
