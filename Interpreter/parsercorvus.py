from lexercorvus import Token, tokenize
from errors import CorvusError
from astnodes import (
    ProgramNode, LiteralNode, IdentifierNode, ListNode, TupleNode, DictNode,
    BinOpNode, UnaryOpNode, SafeNavNode, IndexAccessNode, MethodCallNode,
    VarDeclNode, ConstDeclNode, AssignmentNode, BlockNode, IfNode, WhileNode,
    ForNode, BreakNode, ContinueNode, PassNode, GivoutNode, FuncDeclNode,
    LambdaNode, FuncCallNode, ClassDeclNode, GlobalNode, GetNode, AwaitNode,
    TryErrorNode, InputNode
)


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos = 0

    # --- Helper Methods ---

    def peek(self) -> Token | None:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def advance(self) -> Token:
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def match(self, token_type: str, value: str = None) -> bool:
        tok = self.peek()
        if tok and tok.type == 'TUP_CLOSE' and token_type == 'RBRACKET':
            tok.type = 'RBRACKET'
            tok.value = ']'
            self.tokens.insert(self.pos + 1, Token(type='RPAREN', value=')', line=tok.line, column=tok.column + 1))
        if tok and tok.type == token_type:
            if value is None or tok.value == value:
                self.advance()
                return True
        return False

    def expect(self, token_type: str, value: str = None) -> Token:
        tok = self.peek()
        if tok and tok.type == 'TUP_CLOSE' and token_type == 'RBRACKET':
            tok.type = 'RBRACKET'
            tok.value = ']'
            self.tokens.insert(self.pos + 1, Token(type='RPAREN', value=')', line=tok.line, column=tok.column + 1))
        if not tok:
            last = self.tokens[-1] if self.tokens else None
            line = last.line if last else 1
            col = last.column if last else 1
            raise CorvusError(
                error_type="Corvus SyntaxError",
                message=f"Unexpected end of input. Expected {token_type} '{value or ''}'",
                line=line,
                col=col,
                suggestion="Check for unclosed brackets, missing semicolons, or incomplete statements."
            )
        if tok.type != token_type or (value is not None and tok.value != value):
            suggestion = "Ensure your syntax matches the Corvus language specification."
            if token_type == 'LBRACKET':
                suggestion = "Use '[' and ']' to delimit blocks."
            elif token_type == 'SEMI':
                suggestion = "Statements such as 'set <type>;' require a semicolon after the type."
            elif token_type == 'RPAREN':
                suggestion = "Close your parentheses ')' before opening a code block."
            elif token_type == 'TUP_CLOSE':
                suggestion = "Tuples must be closed with '])'."

            raise CorvusError(
                error_type="Corvus SyntaxError",
                message=f"Expected {token_type} '{value or ''}', but got '{tok.value}'",
                line=tok.line,
                col=tok.column,
                suggestion=suggestion
            )
        return self.advance()


    # --- Program and Statements ---

    def parse(self) -> ProgramNode:
        statements = []
        while self.peek() is not None:
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        return ProgramNode(statements=statements)

    def parse_statement(self):
        tok = self.peek()
        if not tok:
            return None

        if tok.type == 'KEYWORD' and tok.value == 'set':
            return self.parse_var_or_const_decl()

        if tok.type == 'KEYWORD' and tok.value == 'async':
            nxt = self.tokens[self.pos + 1] if self.pos + 1 < len(self.tokens) else None
            if nxt and nxt.value == 'mk':
                return self.parse_func_decl(is_async=True)

        if tok.type == 'KEYWORD' and tok.value == 'mk':
            return self.parse_func_decl(is_async=False)

        if tok.type == 'KEYWORD' and tok.value == 'givout':
            self.advance()
            val = None
            nxt = self.peek()
            if nxt and nxt.type not in ('RBRACKET',):
                val = self.parse_expression()
            return GivoutNode(value=val)

        if tok.type == 'KEYWORD' and tok.value == 'if':
            return self.parse_if()

        if tok.type == 'KEYWORD' and tok.value == 'while':
            return self.parse_while()

        if tok.type == 'KEYWORD' and tok.value == 'for':
            return self.parse_for()

        if tok.type == 'KEYWORD' and tok.value == 'brk':
            self.advance()
            return BreakNode()
        if tok.type == 'KEYWORD' and tok.value == 'con':
            self.advance()
            return ContinueNode()
        if tok.type == 'KEYWORD' and tok.value == 'pass':
            self.advance()
            return PassNode()

        if tok.type == 'KEYWORD' and tok.value == 'global':
            self.advance()
            self.expect('LPAREN')
            var_name = self.expect('ID').value
            self.expect('RPAREN')
            return GlobalNode(name=var_name)

        if tok.type == 'KEYWORD' and tok.value == 'get':
            self.advance()
            mod_name = self.expect('ID').value
            imported_symbols = None
            if self.match('LBRACKET'):
                imported_symbols = []
                while not self.match('RBRACKET'):
                    sym = self.expect('ID').value
                    imported_symbols.append(sym)
                    self.match('COMMA')
            return GetNode(module_name=mod_name, imported_symbols=imported_symbols)

        if tok.type == 'KEYWORD' and tok.value == 'try':
            return self.parse_try()

        if tok.type == 'KEYWORD' and tok.value == 'cls':
            self.advance()
            name = self.expect('ID').value
            self.expect('LPAREN')
            self.expect('RPAREN')
            body = self.parse_block()
            return ClassDeclNode(name=name, body=body)

        expr = self.parse_expression()
        if self.match('ASSIGN'):
            val = self.parse_expression()
            return AssignmentNode(target=expr, value=val)
        return expr


    # --- Declarations & Control Structures ---

    def parse_var_or_const_decl(self):
        self.expect('KEYWORD', 'set')
        nxt = self.peek()

        if nxt and nxt.type == 'KEYWORD' and nxt.value == 'const':
            self.advance()
            self.expect('SEMI')
            name = self.expect('ID').value
            self.expect('ASSIGN')
            val = self.parse_expression()
            return ConstDeclNode(name=name, value=val)

        tok = self.peek()
        if tok and tok.type in ('TYPE', 'ID'):
            var_type = self.advance().value
        else:
            raise CorvusError(
                error_type="Corvus SyntaxError",
                message=f"Expected type specification after 'set', but got '{tok.value if tok else 'EOF'}'",
                line=tok.line if tok else 1,
                col=tok.column if tok else 1,
                suggestion="Use syntax: set <type>; <name> = <value>"
            )

        self.expect('SEMI')
        name = self.expect('ID').value
        val = None
        if self.match('ASSIGN'):
            val = self.parse_expression()
        return VarDeclNode(var_type=var_type, name=name, value=val)


    def parse_func_decl(self, is_async: bool = False):
        if is_async:
            self.expect('KEYWORD', 'async')

        self.expect('KEYWORD', 'mk')

        tok = self.peek()
        if tok and tok.value == 'func':
            self.advance()
        else:
            raise CorvusError(
                error_type="Corvus SyntaxError",
                message=f"Expected 'func' after 'mk', but got '{tok.value if tok else 'EOF'}'",
                line=tok.line if tok else 1,
                col=tok.column if tok else 1,
                suggestion="Declare functions using syntax: mk func <name>(<params>) [ ... ] or async mk func <name>(<params>) [ ... ]"
            )

        name = self.expect('ID').value
        self.expect('LPAREN')
        params = []
        if not self.match('RPAREN'):
            while True:
                params.append(self.expect('ID').value)
                if not self.match('COMMA'):
                    break
            self.expect('RPAREN')
        body = self.parse_block()
        return FuncDeclNode(name=name, params=params, body=body, is_async=is_async)


    def parse_block(self) -> BlockNode:
        self.expect('LBRACKET')
        stmts = []
        while self.peek() and self.peek().type != 'RBRACKET':
            stmts.append(self.parse_statement())
        self.expect('RBRACKET')
        return BlockNode(statements=stmts)

    def parse_if(self) -> IfNode:
        self.expect('KEYWORD', 'if')
        self.expect('LPAREN')
        cond = self.parse_expression()
        self.expect('RPAREN')
        then_block = self.parse_block()

        elsif_branches = []
        while self.peek() and self.peek().type == 'KEYWORD' and self.peek().value == 'elsif':
            self.advance()
            self.expect('LPAREN')
            e_cond = self.parse_expression()
            self.expect('RPAREN')
            e_block = self.parse_block()
            elsif_branches.append((e_cond, e_block))

        else_block = None
        if self.peek() and self.peek().type == 'KEYWORD' and self.peek().value == 'else':
            self.advance()
            else_block = self.parse_block()

        return IfNode(condition=cond, then_block=then_block, elsif_branches=elsif_branches, else_block=else_block)

    def parse_while(self) -> WhileNode:
        self.expect('KEYWORD', 'while')
        self.expect('LPAREN')
        cond = self.parse_expression()
        self.expect('RPAREN')
        body = self.parse_block()
        return WhileNode(condition=cond, body=body)

    def parse_for(self) -> ForNode:
        self.expect('KEYWORD', 'for')
        self.expect('LPAREN')
        var_name = self.expect('ID').value
        self.expect('KEYWORD', 'in')
        collection = self.parse_expression()
        self.expect('RPAREN')
        body = self.parse_block()
        return ForNode(iterator=var_name, collection=collection, body=body)

    def parse_try(self) -> TryErrorNode:
        self.expect('KEYWORD', 'try')
        try_block = self.parse_block()
        err_var = None
        err_block = None
        if self.peek() and self.peek().type == 'KEYWORD' and self.peek().value == 'error':
            self.advance()
            self.expect('LPAREN')
            err_var = self.expect('ID').value
            self.expect('RPAREN')
            err_block = self.parse_block()

        final_block = None
        if self.peek() and self.peek().type == 'KEYWORD' and self.peek().value == 'final':
            self.advance()
            final_block = self.parse_block()

        return TryErrorNode(try_block=try_block, error_var=err_var, error_block=err_block, final_block=final_block)

    # --- Precedence Ladder for Expressions ---

    def parse_expression(self):
        return self.parse_null_coalesce()

    def parse_null_coalesce(self):
        node = self.parse_logic_or()
        while self.match('NULL_COAL'):
            right = self.parse_logic_or()
            node = BinOpNode(left=node, op='??', right=right)
        return node

    def parse_logic_or(self):
        node = self.parse_logic_and()
        while self.peek() and self.peek().type == 'KEYWORD' and self.peek().value in ('or', 'xor'):
            op = self.advance().value
            right = self.parse_logic_and()
            node = BinOpNode(left=node, op=op, right=right)
        return node

    def parse_logic_and(self):
        node = self.parse_comparison()
        while self.peek() and self.peek().type == 'KEYWORD' and self.peek().value == 'and':
            op = self.advance().value
            right = self.parse_comparison()
            node = BinOpNode(left=node, op=op, right=right)
        return node

    def parse_comparison(self):
        node = self.parse_additive()
        comp_types = ('EQ', 'NEQ', 'LT', 'GT', 'LTE', 'GTE', 'FAT_ARROW')
        while self.peek() and self.peek().type in comp_types:
            op = self.advance().value
            right = self.parse_additive()
            node = BinOpNode(left=node, op=op, right=right)
        return node

    def parse_additive(self):
        node = self.parse_multiplicative()
        while self.peek() and self.peek().type in ('PLUS', 'MINUS'):
            op = self.advance().value
            right = self.parse_multiplicative()
            node = BinOpNode(left=node, op=op, right=right)
        return node

    def parse_multiplicative(self):
        node = self.parse_power()
        while self.peek() and self.peek().type in ('STAR', 'SLASH', 'MOD'):
            op = self.advance().value
            right = self.parse_power()
            node = BinOpNode(left=node, op=op, right=right)
        return node

    def parse_power(self):
        node = self.parse_unary()
        while self.match('POWER'):
            right = self.parse_unary()
            node = BinOpNode(left=node, op='**', right=right)
        return node

    def parse_unary(self):
        tok = self.peek()
        if tok and (tok.type == 'MINUS' or (tok.type == 'KEYWORD' and tok.value == 'not')):
            op = self.advance().value
            operand = self.parse_unary()
            return UnaryOpNode(op=op, operand=operand)
        if tok and tok.type == 'KEYWORD' and tok.value == 'awt':
            self.advance()
            target = self.parse_postfix()
            return AwaitNode(target=target)
        return self.parse_postfix()

    def parse_postfix(self):
        node = self.parse_primary()
        while True:
            if self.match('DOT'):
                tok = self.peek()
                if tok and tok.type in ('ID', 'KEYWORD', 'TYPE'):
                    name = self.advance().value
                else:
                    name = self.expect('ID').value
                if self.match('LPAREN'):
                    args = self.parse_arguments()
                    self.expect('RPAREN')
                    node = MethodCallNode(target=node, method_name=name, args=args)
                else:
                    node = MethodCallNode(target=node, method_name=name, args=[])
            elif self.match('SAFE_NAV'):
                tok = self.peek()
                if tok and tok.type in ('ID', 'KEYWORD', 'TYPE'):
                    name = self.advance().value
                else:
                    name = self.expect('ID').value
                node = SafeNavNode(target=node, property_name=name)

            elif self.match('LBRACKET'):
                idx = self.parse_expression()
                self.expect('RBRACKET')
                node = IndexAccessNode(target=node, index=idx)
            elif self.match('LPAREN'):
                args = self.parse_arguments()
                self.expect('RPAREN')
                node = FuncCallNode(callee=node, args=args)
            else:
                break
        return node

    def parse_arguments(self) -> list:
        args = []
        if self.peek() and self.peek().type != 'RPAREN':
            while True:
                args.append(self.parse_expression())
                if not self.match('COMMA'):
                    break
        return args

    # --- Primaries & Literals ---

    def parse_primary(self):
        tok = self.peek()
        if not tok:
            raise CorvusError(
                error_type="Corvus SyntaxError",
                message="Unexpected end of file while parsing expression.",
                suggestion="Check for an incomplete mathematical operation or missing operand."
            )

        if tok.type == 'NUMBER':
            self.advance()
            val = float(tok.value) if '.' in tok.value else int(tok.value)
            return LiteralNode(value=val)

        if tok.type == 'STRING':
            self.advance()
            return LiteralNode(value=tok.value[1:-1])

        if tok.value == 'lmb':
            self.advance()
            self.expect('LBRACKET')
            params = []
            if not self.match('RBRACKET'):
                while True:
                    params.append(self.expect('ID').value)
                    if not self.match('COMMA'):
                        break
                self.expect('RBRACKET')

            if self.match('FAT_ARROW'):
                body = self.parse_expression()
            else:
                body = self.parse_block()
            return LambdaNode(params=params, body=body)

        if tok.type in ('KEYWORD', 'TYPE'):
            if tok.value == 'true':
                self.advance()
                return LiteralNode(value=True)
            if tok.value == 'fal':
                self.advance()
                return LiteralNode(value=False)
            if tok.value == 'null':
                self.advance()
                return LiteralNode(value=None)
            if tok.value == 'input':
                self.advance()
                self.expect('LPAREN')
                prompt = None
                if not self.match('RPAREN'):
                    prompt = self.parse_expression()
                    self.expect('RPAREN')
                return InputNode(prompt=prompt)
            if tok.type == 'TYPE':
                self.advance()
                return IdentifierNode(name=tok.value)

        if tok.type == 'ID':
            self.advance()
            return IdentifierNode(name=tok.value)

        if self.match('TUP_OPEN'):
            elements = []
            if not self.match('TUP_CLOSE'):
                while True:
                    elements.append(self.parse_expression())
                    if not self.match('COMMA'):
                        break
                self.expect('TUP_CLOSE')
            return TupleNode(elements=elements)

        if self.match('LBRACE'):
            elements = []
            if not self.match('RBRACE'):
                while True:
                    elements.append(self.parse_expression())
                    if not self.match('COMMA'):
                        break
                self.expect('RBRACE')
            return ListNode(elements=elements)

        if self.match('LPAREN'):
            if self.peek() and self.peek().type == 'STRING' and self.pos + 1 < len(self.tokens) and self.tokens[self.pos + 1].type == 'COLON':
                keys = []
                values = []
                while not self.match('RPAREN'):
                    k = self.parse_expression()
                    self.expect('COLON')
                    v = self.parse_expression()
                    keys.append(k)
                    values.append(v)
                    self.match('COMMA')
                return DictNode(keys=keys, values=values)

            expr = self.parse_expression()
            self.expect('RPAREN')
            return expr

        raise CorvusError(
            error_type="Corvus SyntaxError",
            message=f"Unexpected token {tok.type} '{tok.value}'",
            line=tok.line,
            col=tok.column,
            suggestion="Check for typos or invalid syntax at this position."
        )

def parse_code(code: str) -> ProgramNode:
    tokens = tokenize(code)
    parser = Parser(tokens)
    return parser.parse()
