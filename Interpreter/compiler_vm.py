# compiler_vm.py
# Corvus Bytecode Compiler: Translates Corvus AST into CodeObject

from typing import List, Optional
from astnodes import (
    ProgramNode, LiteralNode, IdentifierNode, BinOpNode, UnaryOpNode,
    ListNode, TupleNode, DictNode, IndexAccessNode, MethodCallNode,
    VarDeclNode, ConstDeclNode, AssignmentNode, BlockNode, IfNode,
    WhileNode, ForNode, BreakNode, ContinueNode, PassNode, GivoutNode,
    FuncDeclNode, LambdaNode, FuncCallNode, TernaryNode, FStringNode, MatchNode
)
from bytecode import CodeObject, OpCode

class BytecodeCompiler:
    def __init__(self, filename: str = "<memory>"):
        self.filename = filename
        self.code = CodeObject(name="<module>", filename=filename)
        self.loop_stack: List[dict] = [] # tracks break & continue jump targets

    def compile(self, ast: ProgramNode) -> CodeObject:
        for stmt in ast.statements:
            self.visit(stmt)
        self.code.emit(OpCode.LOAD_CONST, self.code.add_const(None))
        self.code.emit(OpCode.RETURN)
        return self.code

    def visit(self, node):
        method_name = f"visit_{type(node).__name__}"
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        # Fallback NOP
        pass

    def visit_LiteralNode(self, node: LiteralNode):
        const_idx = self.code.add_const(node.value)
        self.code.emit(OpCode.LOAD_CONST, const_idx)

    def visit_IdentifierNode(self, node: IdentifierNode):
        name_idx = self.code.add_name(node.name)
        self.code.emit(OpCode.LOAD_VAR, name_idx)

    def visit_VarDeclNode(self, node: VarDeclNode):
        if node.value:
            self.visit(node.value)
        else:
            self.code.emit(OpCode.LOAD_CONST, self.code.add_const(None))
        name_idx = self.code.add_name(node.name)
        self.code.emit(OpCode.STORE_VAR, name_idx)

    def visit_ConstDeclNode(self, node: ConstDeclNode):
        self.visit(node.value)
        name_idx = self.code.add_name(node.name)
        self.code.emit(OpCode.STORE_VAR, name_idx)

    def visit_AssignmentNode(self, node: AssignmentNode):
        self.visit(node.value)
        if isinstance(node.target, IndexAccessNode):
            # Evaluate target and index
            self.visit(node.target.target)
            self.visit(node.target.index)
            self.code.emit(OpCode.INDEX_SET)
        else:
            target_name = node.target.name if isinstance(node.target, IdentifierNode) else str(node.target)
            name_idx = self.code.add_name(target_name)
            self.code.emit(OpCode.STORE_VAR, name_idx)

    def visit_BinOpNode(self, node: BinOpNode):
        self.visit(node.left)
        self.visit(node.right)
        op = node.op
        if op == '+': self.code.emit(OpCode.ADD)
        elif op == '-': self.code.emit(OpCode.SUB)
        elif op == '*': self.code.emit(OpCode.MUL)
        elif op == '/': self.code.emit(OpCode.DIV)
        elif op == '%': self.code.emit(OpCode.MOD)
        elif op == '**': self.code.emit(OpCode.POW)
        elif op == '@': self.code.emit(OpCode.MATMUL)
        elif op == '==': self.code.emit(OpCode.EQ)
        elif op == '!=': self.code.emit(OpCode.NEQ)
        elif op == '<': self.code.emit(OpCode.LT)
        elif op == '>': self.code.emit(OpCode.GT)
        elif op == '<=': self.code.emit(OpCode.LTE)
        elif op == '>=': self.code.emit(OpCode.GTE)
        elif op == 'in': self.code.emit(OpCode.IN)

    def visit_UnaryOpNode(self, node: UnaryOpNode):
        self.visit(node.operand)
        if node.op == '-':
            self.code.emit(OpCode.NEG)
        elif node.op == 'not':
            self.code.emit(OpCode.NOT)

    def visit_ListNode(self, node: ListNode):
        for elem in node.elements:
            self.visit(elem)
        self.code.emit(OpCode.BUILD_LIST, len(node.elements))

    def visit_TupleNode(self, node: TupleNode):
        for elem in node.elements:
            self.visit(elem)
        self.code.emit(OpCode.BUILD_TUPLE, len(node.elements))

    def visit_DictNode(self, node: DictNode):
        for k, v in zip(node.keys, node.values):
            self.visit(k)
            self.visit(v)
        self.code.emit(OpCode.BUILD_DICT, len(node.keys))

    def visit_IndexAccessNode(self, node: IndexAccessNode):
        self.visit(node.target)
        self.visit(node.index)
        self.code.emit(OpCode.INDEX_GET)

    def visit_FuncCallNode(self, node: FuncCallNode):
        for arg in node.args:
            self.visit(arg)
        self.visit(node.callee)
        self.code.emit(OpCode.CALL_FUNC, len(node.args))

    def visit_MethodCallNode(self, node: MethodCallNode):
        self.visit(node.target)
        for arg in node.args:
            self.visit(arg)
        method_idx = self.code.add_name(node.method_name)
        self.code.emit(OpCode.CALL_METHOD, (method_idx, len(node.args)))

    def visit_FStringNode(self, node: FStringNode):
        for part in node.parts:
            self.visit(part)
        self.code.emit(OpCode.BUILD_STRING, len(node.parts))

    def visit_TernaryNode(self, node: TernaryNode):
        self.visit(node.condition)
        false_jump = self.code.emit(OpCode.JUMP_IF_FALSE, 0)
        self.visit(node.true_expr)
        end_jump = self.code.emit(OpCode.JUMP, 0)
        self.code.instructions[false_jump].arg = len(self.code.instructions)
        self.visit(node.false_expr)
        self.code.instructions[end_jump].arg = len(self.code.instructions)

    def visit_BlockNode(self, node: BlockNode):
        for stmt in node.statements:
            self.visit(stmt)

    def visit_IfNode(self, node: IfNode):
        exit_jumps = []

        # Condition & Then block
        self.visit(node.condition)
        jump_next = self.code.emit(OpCode.JUMP_IF_FALSE, 0)
        self.visit(node.then_block)
        exit_jumps.append(self.code.emit(OpCode.JUMP, 0))
        self.code.instructions[jump_next].arg = len(self.code.instructions)

        # Elsif branches
        for cond, body in node.elsif_branches:
            self.visit(cond)
            jump_next = self.code.emit(OpCode.JUMP_IF_FALSE, 0)
            self.visit(body)
            exit_jumps.append(self.code.emit(OpCode.JUMP, 0))
            self.code.instructions[jump_next].arg = len(self.code.instructions)

        # Else block
        if node.else_block:
            self.visit(node.else_block)

        # Fixup all exit jumps to land here
        target = len(self.code.instructions)
        for j in exit_jumps:
            self.code.instructions[j].arg = target

    def visit_WhileNode(self, node: WhileNode):
        loop_start = len(self.code.instructions)
        self.loop_stack.append({'breaks': [], 'continues': loop_start})

        self.visit(node.condition)
        exit_jump = self.code.emit(OpCode.JUMP_IF_FALSE, 0)
        self.visit(node.body)
        self.code.emit(OpCode.JUMP, loop_start)

        loop_end = len(self.code.instructions)
        self.code.instructions[exit_jump].arg = loop_end

        loop_info = self.loop_stack.pop()
        for b in loop_info['breaks']:
            self.code.instructions[b].arg = loop_end

    def visit_ForNode(self, node: ForNode):
        self.visit(node.collection)
        self.code.emit(OpCode.GET_ITER)

        loop_start = len(self.code.instructions)
        self.loop_stack.append({'breaks': [], 'continues': loop_start})

        exit_jump = self.code.emit(OpCode.FOR_ITER, 0)
        iter_var_idx = self.code.add_name(node.iterator)
        self.code.emit(OpCode.STORE_VAR, iter_var_idx)

        self.visit(node.body)
        self.code.emit(OpCode.JUMP, loop_start)

        loop_end = len(self.code.instructions)
        self.code.instructions[exit_jump].arg = loop_end

        loop_info = self.loop_stack.pop()
        for b in loop_info['breaks']:
            self.code.instructions[b].arg = loop_end


    def visit_BreakNode(self, node: BreakNode):
        if self.loop_stack:
            j = self.code.emit(OpCode.JUMP, 0)
            self.loop_stack[-1]['breaks'].append(j)

    def visit_ContinueNode(self, node: ContinueNode):
        if self.loop_stack:
            target = self.loop_stack[-1]['continues']
            self.code.emit(OpCode.JUMP, target)

    def visit_PassNode(self, node: PassNode):
        self.code.emit(OpCode.NOP)

    def visit_GivoutNode(self, node: GivoutNode):
        if node.value:
            self.visit(node.value)
        else:
            self.code.emit(OpCode.LOAD_CONST, self.code.add_const(None))
        self.code.emit(OpCode.RETURN)

    def visit_FuncDeclNode(self, node: FuncDeclNode):
        # Create child compiler for function body
        fn_compiler = BytecodeCompiler(self.filename)
        fn_compiler.code.name = node.name
        fn_compiler.code.params = list(node.params)
        fn_code = fn_compiler.compile(ProgramNode(statements=node.body.statements))

        const_idx = self.code.add_const(fn_code)
        self.code.emit(OpCode.MAKE_FUNC, const_idx)
        name_idx = self.code.add_name(node.name)
        self.code.emit(OpCode.STORE_VAR, name_idx)

    def visit_LambdaNode(self, node: LambdaNode):
        fn_compiler = BytecodeCompiler(self.filename)
        fn_compiler.code.name = "<lambda>"
        fn_compiler.code.params = list(node.params)
        if isinstance(node.body, BlockNode):
            stmts = node.body.statements
        else:
            stmts = [GivoutNode(value=node.body)]
        fn_code = fn_compiler.compile(ProgramNode(statements=stmts))
        const_idx = self.code.add_const(fn_code)
        self.code.emit(OpCode.MAKE_FUNC, const_idx)

    def visit_MatchNode(self, node: MatchNode):
        # Evaluate target once and save in temp variable
        self.visit(node.target)
        temp_name = f"_match_target_{len(self.code.instructions)}"
        temp_idx = self.code.add_name(temp_name)
        self.code.emit(OpCode.STORE_VAR, temp_idx)

        exit_jumps = []
        for case in node.cases:
            self.code.emit(OpCode.LOAD_VAR, temp_idx)
            self.visit(case.pattern)
            self.code.emit(OpCode.EQ)
            next_case = self.code.emit(OpCode.JUMP_IF_FALSE, 0)
            if isinstance(case.body, BlockNode):
                self.visit(case.body)
            else:
                self.visit(case.body)
            exit_jumps.append(self.code.emit(OpCode.JUMP, 0))
            self.code.instructions[next_case].arg = len(self.code.instructions)

        if node.default_branch:
            if isinstance(node.default_branch, BlockNode):
                self.visit(node.default_branch)
            else:
                self.visit(node.default_branch)

        match_end = len(self.code.instructions)
        for j in exit_jumps:
            self.code.instructions[j].arg = match_end
