# Corvus AST Optimization Engine
# Passes: Constant Folding, Dead Branch Elimination, Algebraic Simplifications, Ternary Folding

import math
from typing import Any
from astnodes import (
    ASTNode, ProgramNode, LiteralNode, IdentifierNode, ListNode, TupleNode, DictNode,
    BinOpNode, UnaryOpNode, SafeNavNode, IndexAccessNode, MethodCallNode,
    VarDeclNode, ConstDeclNode, AssignmentNode, BlockNode, IfNode, WhileNode,
    ForNode, BreakNode, ContinueNode, PassNode, GivoutNode, FuncDeclNode,
    LambdaNode, FuncCallNode, ClassDeclNode, GlobalNode, GetNode, AwaitNode,
    TryErrorNode, InputNode, PipelineNode, MatchNode, CaseNode, TernaryNode, FStringNode
)

class AstOptimizer:
    def __init__(self):
        self.folded_constants = 0
        self.pruned_branches = 0
        self.algebraic_simplifications = 0

    def optimize(self, node: ASTNode) -> ASTNode:
        if node is None:
            return None
        method_name = f'opt_{type(node).__name__}'
        optimizer = getattr(self, method_name, self.generic_opt)
        return optimizer(node)

    def generic_opt(self, node: ASTNode) -> ASTNode:
        return node

    def opt_ProgramNode(self, node: ProgramNode) -> ProgramNode:
        new_stmts = []
        for stmt in node.statements:
            opt_stmt = self.optimize(stmt)
            if opt_stmt is not None:
                if isinstance(opt_stmt, list):
                    new_stmts.extend(opt_stmt)
                else:
                    new_stmts.append(opt_stmt)
        return ProgramNode(statements=new_stmts)

    def opt_BlockNode(self, node: BlockNode) -> BlockNode:
        new_stmts = []
        for stmt in node.statements:
            opt_stmt = self.optimize(stmt)
            if opt_stmt is not None:
                if isinstance(opt_stmt, list):
                    new_stmts.extend(opt_stmt)
                else:
                    new_stmts.append(opt_stmt)
        return BlockNode(statements=new_stmts)

    def opt_VarDeclNode(self, node: VarDeclNode) -> VarDeclNode:
        opt_val = self.optimize(node.value) if node.value else None
        return VarDeclNode(var_type=node.var_type, name=node.name, value=opt_val)

    def opt_ConstDeclNode(self, node: ConstDeclNode) -> ConstDeclNode:
        opt_val = self.optimize(node.value)
        return ConstDeclNode(name=node.name, value=opt_val)

    def opt_AssignmentNode(self, node: AssignmentNode) -> AssignmentNode:
        opt_val = self.optimize(node.value)
        return AssignmentNode(target=node.target, value=opt_val)

    def opt_GivoutNode(self, node: GivoutNode) -> GivoutNode:
        opt_val = self.optimize(node.value) if node.value else None
        return GivoutNode(value=opt_val)

    def opt_FuncCallNode(self, node: FuncCallNode) -> FuncCallNode:
        opt_callee = self.optimize(node.callee)
        opt_args = [self.optimize(a) for a in node.args]
        return FuncCallNode(callee=opt_callee, args=opt_args)

    def opt_MethodCallNode(self, node: MethodCallNode) -> MethodCallNode:
        opt_target = self.optimize(node.target)
        opt_args = [self.optimize(a) for a in node.args]
        return MethodCallNode(target=opt_target, method_name=node.method_name, args=opt_args)

    def opt_ListNode(self, node: ListNode) -> ListNode:
        return ListNode(elements=[self.optimize(e) for e in node.elements])

    def opt_TupleNode(self, node: TupleNode) -> TupleNode:
        return TupleNode(elements=[self.optimize(e) for e in node.elements])

    def opt_DictNode(self, node: DictNode) -> DictNode:
        return DictNode(
            keys=[self.optimize(k) for k in node.keys],
            values=[self.optimize(v) for v in node.values]
        )

    def opt_UnaryOpNode(self, node: UnaryOpNode) -> ASTNode:
        operand = self.optimize(node.operand)
        if isinstance(operand, LiteralNode):
            val = operand.value
            if node.op == '-':
                if isinstance(val, (int, float)):
                    self.folded_constants += 1
                    return LiteralNode(value=-val)
            elif node.op == 'not':
                self.folded_constants += 1
                return LiteralNode(value=not bool(val))
        return UnaryOpNode(op=node.op, operand=operand)

    def opt_BinOpNode(self, node: BinOpNode) -> ASTNode:
        left = self.optimize(node.left)
        right = self.optimize(node.right)
        op = node.op

        # 1. Constant Folding
        if isinstance(left, LiteralNode) and isinstance(right, LiteralNode):
            lval = left.value
            rval = right.value
            try:
                if op == '+':
                    self.folded_constants += 1
                    return LiteralNode(value=lval + rval)
                elif op == '-':
                    if isinstance(lval, (int, float)) and isinstance(rval, (int, float)):
                        self.folded_constants += 1
                        return LiteralNode(value=lval - rval)
                elif op == '*':
                    if (isinstance(lval, (int, float)) and isinstance(rval, (int, float))) or (isinstance(lval, str) and isinstance(rval, int)):
                        self.folded_constants += 1
                        return LiteralNode(value=lval * rval)
                elif op == '/':
                    if isinstance(lval, (int, float)) and isinstance(rval, (int, float)) and rval != 0:
                        self.folded_constants += 1
                        val = lval // rval if isinstance(lval, int) and isinstance(rval, int) and lval % rval == 0 else lval / rval
                        return LiteralNode(value=val)
                elif op == '%':
                    if isinstance(lval, int) and isinstance(rval, int) and rval != 0:
                        self.folded_constants += 1
                        return LiteralNode(value=lval % rval)
                elif op == '**':
                    if isinstance(lval, (int, float)) and isinstance(rval, (int, float)) and rval < 1000:
                        self.folded_constants += 1
                        return LiteralNode(value=lval ** rval)
                elif op == '==':
                    self.folded_constants += 1
                    return LiteralNode(value=lval == rval)
                elif op == '!=':
                    self.folded_constants += 1
                    return LiteralNode(value=lval != rval)
                elif op == '<':
                    self.folded_constants += 1
                    return LiteralNode(value=lval < rval)
                elif op == '<=':
                    self.folded_constants += 1
                    return LiteralNode(value=lval <= rval)
                elif op == '>':
                    self.folded_constants += 1
                    return LiteralNode(value=lval > rval)
                elif op == '>=':
                    self.folded_constants += 1
                    return LiteralNode(value=lval >= rval)
                elif op == 'and':
                    self.folded_constants += 1
                    return LiteralNode(value=bool(lval and rval))
                elif op == 'or':
                    self.folded_constants += 1
                    return LiteralNode(value=bool(lval or rval))
                elif op == 'xor':
                    self.folded_constants += 1
                    return LiteralNode(value=bool(lval) ^ bool(rval))
            except Exception:
                pass

        # 2. Algebraic Simplifications
        if op == '*':
            if isinstance(left, LiteralNode) and left.value == 0:
                self.algebraic_simplifications += 1
                return LiteralNode(value=0)
            if isinstance(right, LiteralNode) and right.value == 0:
                self.algebraic_simplifications += 1
                return LiteralNode(value=0)
            if isinstance(left, LiteralNode) and left.value == 1:
                self.algebraic_simplifications += 1
                return right
            if isinstance(right, LiteralNode) and right.value == 1:
                self.algebraic_simplifications += 1
                return left
        elif op == '+':
            if isinstance(left, LiteralNode) and left.value == 0:
                self.algebraic_simplifications += 1
                return right
            if isinstance(right, LiteralNode) and right.value == 0:
                self.algebraic_simplifications += 1
                return left
        elif op == '-':
            if isinstance(right, LiteralNode) and right.value == 0:
                self.algebraic_simplifications += 1
                return left

        return BinOpNode(left=left, op=op, right=right)

    def opt_TernaryNode(self, node: TernaryNode) -> ASTNode:
        cond = self.optimize(node.condition)
        true_expr = self.optimize(node.true_expr)
        false_expr = self.optimize(node.false_expr)

        if isinstance(cond, LiteralNode):
            self.folded_constants += 1
            if bool(cond.value):
                return true_expr
            else:
                return false_expr
        return TernaryNode(condition=cond, true_expr=true_expr, false_expr=false_expr)

    def opt_FStringNode(self, node: FStringNode) -> ASTNode:
        new_parts = []
        for part in node.parts:
            opt_part = self.optimize(part)
            if new_parts and isinstance(new_parts[-1], LiteralNode) and isinstance(opt_part, LiteralNode):
                new_parts[-1] = LiteralNode(value=str(new_parts[-1].value) + str(opt_part.value))
                self.folded_constants += 1
            else:
                new_parts.append(opt_part)

        if len(new_parts) == 1 and isinstance(new_parts[0], LiteralNode):
            return new_parts[0]
        return FStringNode(parts=new_parts)

    def opt_IfNode(self, node: IfNode) -> ASTNode:
        cond = self.optimize(node.condition)
        then_block = self.optimize(node.then_block)

        if isinstance(cond, LiteralNode):
            if bool(cond.value):
                self.pruned_branches += 1
                return then_block.statements
            else:
                self.pruned_branches += 1
                for el_cond, el_body in node.elsif_branches:
                    el_c = self.optimize(el_cond)
                    if isinstance(el_c, LiteralNode):
                        if bool(el_c.value):
                            return self.optimize(el_body).statements
                    else:
                        return IfNode(condition=el_c, then_block=self.optimize(el_body), elsif_branches=[], else_block=self.optimize(node.else_block))
                if node.else_block:
                    return self.optimize(node.else_block).statements
                return None

        opt_elsifs = [(self.optimize(c), self.optimize(b)) for c, b in node.elsif_branches]
        opt_else = self.optimize(node.else_block) if node.else_block else None
        return IfNode(condition=cond, then_block=then_block, elsif_branches=opt_elsifs, else_block=opt_else)

    def opt_WhileNode(self, node: WhileNode) -> ASTNode:
        cond = self.optimize(node.condition)
        if isinstance(cond, LiteralNode) and not bool(cond.value):
            self.pruned_branches += 1
            return None
        body = self.optimize(node.body)
        return WhileNode(condition=cond, body=body)

    def opt_ForNode(self, node: ForNode) -> ForNode:
        coll = self.optimize(node.collection)
        body = self.optimize(node.body)
        return ForNode(iterator=node.iterator, collection=coll, body=body)

    def opt_FuncDeclNode(self, node: FuncDeclNode) -> FuncDeclNode:
        body = self.optimize(node.body)
        return FuncDeclNode(name=node.name, params=node.params, body=body, is_async=node.is_async)

    def opt_LambdaNode(self, node: LambdaNode) -> LambdaNode:
        body = self.optimize(node.body)
        return LambdaNode(params=node.params, body=body)
