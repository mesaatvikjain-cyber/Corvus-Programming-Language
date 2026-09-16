"""Corvus WebAssembly (Wasm) Backend
Compiles Corvus AST into WebAssembly Text Format (.wat) and standalone browser runner.
"""

import os
import re
from lexercorvus import tokenize
from parsercorvus import Parser
from astnodes import (
    ProgramNode, FuncDeclNode, GivoutNode, BinOpNode, LiteralNode, IdentifierNode,
    VarDeclNode, AssignmentNode, IfNode, WhileNode
)

class WasmCompiler:
    def __init__(self):
        self.functions = []
        self.exports = []
        self.wat_lines = []

    def compile(self, code_or_ast, output_path: str = None) -> str:
        """Compile Corvus code to WebAssembly Text Format (.wat)."""
        if isinstance(code_or_ast, str):
            tokens = tokenize(code_or_ast)
            ast = Parser(tokens).parse()
        else:
            ast = code_or_ast

        wat = [
            ";; [Compiled from Corvus to WebAssembly Text Format (.wat)]",
            "(module",
            '  ;; Host environment import for log(i32)',
            '  (import "env" "log_i32" (func $log_i32 (param i32)))',
            ""
        ]

        # Scan for functions in AST
        for stmt in ast.statements:
            if isinstance(stmt, FuncDeclNode):
                fn_wat = self._compile_function(stmt)
                wat.extend(fn_wat)
                wat.append(f'  (export "{stmt.name}" (func ${stmt.name}))')
                wat.append("")

        # Also emit a default main export if statements exist outside functions
        top_level_stmts = [s for s in ast.statements if not isinstance(stmt, FuncDeclNode)]
        if top_level_stmts or not any(isinstance(s, FuncDeclNode) for s in ast.statements):
            wat.append('  ;; Top-level execution entry point')
            wat.append('  (func $main (result i32)')
            wat.append('    (local $tmp i32)')
            for s in ast.statements:
                if not isinstance(s, FuncDeclNode):
                    wat.extend(self._compile_statement(s, indent="    "))
            wat.append('    i32.const 0')
            wat.append('    return')
            wat.append('  )')
            wat.append('  (export "main" (func $main))')
            wat.append("")

        wat.append(")")
        wat_content = "\n".join(wat)

        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(wat_content)

            # Also generate a companion HTML/JS runner file
            html_path = output_path.replace(".wat", ".html").replace(".wasm", ".html")
            if not html_path.endswith(".html"):
                html_path += ".html"
            wat_basename = os.path.basename(output_path)
            html_content = self._generate_html_runner(wat_basename)
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html_content)

        return wat_content

    def _compile_function(self, fn_node: FuncDeclNode) -> list:
        params_wat = " ".join([f"(param ${p} i32)" for p in fn_node.params])
        res_wat = "(result i32)"
        lines = [
            f"  (func ${fn_node.name} {params_wat} {res_wat}".strip(),
            "    (local $ret i32)"
        ]

        stmts = fn_node.body.statements if hasattr(fn_node.body, "statements") else (fn_node.body if isinstance(fn_node.body, (list, tuple)) else [fn_node.body])
        for stmt in stmts:
            lines.extend(self._compile_statement(stmt, indent="    "))

        lines.append("    i32.const 0")
        lines.append("  )")
        return lines

    def _compile_statement(self, stmt, indent="    ") -> list:
        lines = []
        if isinstance(stmt, GivoutNode):
            val = getattr(stmt, "value", None) or getattr(stmt, "expr", None)
            if val:
                lines.extend(self._compile_expr(val, indent))
            lines.append(f"{indent}return")
        elif isinstance(stmt, VarDeclNode) or isinstance(stmt, AssignmentNode):
            target_var = getattr(stmt, "name", None) or getattr(stmt, "target", None)
            expr = getattr(stmt, "expr", None) or getattr(stmt, "value", None)
            if expr and target_var:
                lines.extend(self._compile_expr(expr, indent))
                lines.append(f"{indent}local.set ${target_var}")
        elif isinstance(stmt, IfNode):
            lines.extend(self._compile_expr(stmt.condition, indent))
            lines.append(f"{indent}(if")
            lines.append(f"{indent}  (then")
            then_stmts = stmt.then_body.statements if hasattr(stmt.then_body, "statements") else (stmt.then_body if isinstance(stmt.then_body, (list, tuple)) else [stmt.then_body])
            for s in then_stmts:
                lines.extend(self._compile_statement(s, indent + "    "))
            lines.append(f"{indent}  )")
            if stmt.else_body:
                lines.append(f"{indent}  (else")
                else_stmts = stmt.else_body.statements if hasattr(stmt.else_body, "statements") else (stmt.else_body if isinstance(stmt.else_body, (list, tuple)) else [stmt.else_body])
                for s in else_stmts:
                    lines.extend(self._compile_statement(s, indent + "    "))
                lines.append(f"{indent}  )")
            lines.append(f"{indent})")
        return lines

    def _compile_expr(self, expr, indent="    ") -> list:
        lines = []
        if isinstance(expr, LiteralNode):
            val = expr.value
            if isinstance(val, int):
                lines.append(f"{indent}i32.const {val}")
            elif isinstance(val, bool):
                lines.append(f"{indent}i32.const {1 if val else 0}")
            else:
                lines.append(f"{indent}i32.const 0")
        elif isinstance(expr, IdentifierNode):
            lines.append(f"{indent}local.get ${expr.name}")
        elif isinstance(expr, BinOpNode):
            lines.extend(self._compile_expr(expr.left, indent))
            lines.extend(self._compile_expr(expr.right, indent))
            op_map = {
                "+": "i32.add",
                "-": "i32.sub",
                "*": "i32.mul",
                "/": "i32.div_s",
                "==": "i32.eq",
                "!=": "i32.ne",
                "<": "i32.lt_s",
                ">": "i32.gt_s",
                "<=": "i32.le_s",
                ">=": "i32.ge_s",
                "and": "i32.and",
                "or": "i32.or"
            }
            instr = op_map.get(expr.op, "i32.add")
            lines.append(f"{indent}{instr}")
        else:
            lines.append(f"{indent}i32.const 0")
        return lines

    def _generate_html_runner(self, wat_filename: str) -> str:
        return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Corvus WebAssembly Runner</title>
</head>
<body>
  <h1>Corvus WebAssembly Execution Engine</h1>
  <p>Module: <code>{wat_filename}</code></p>
  <div id="output" style="font-family: monospace; background: #1e1e1e; color: #4ade80; padding: 15px; border-radius: 6px;"></div>

  <script>
    const outDiv = document.getElementById("output");
    function logToScreen(msg) {{
      outDiv.innerHTML += msg + "<br/>";
      console.log(msg);
    }}

    const importObject = {{
      env: {{
        log_i32: function(val) {{
          logToScreen("[Corvus Wasm log]: " + val);
        }}
      }}
    }};

    logToScreen("Initializing Corvus WebAssembly Module...");
    // Load compiled Wasm
    // fetch('{wat_filename.replace(".wat", ".wasm")}').then(response =>
    //   WebAssembly.instantiateStreaming(response, importObject)
    // ).then(results => {{
    //   logToScreen("Wasm Instance Ready!");
    //   if (results.instance.exports.main) {{
    //     const res = results.instance.exports.main();
    //     logToScreen("main() return code: " + res);
    //   }}
    // }}).catch(e => logToScreen("Error: " + e));
  </script>
</body>
</html>
"""

def compile_corvus_to_wasm(filepath: str, output_path: str = None) -> str:
    with open(filepath, "r", encoding="utf-8") as f:
        code = f.read()

    if not output_path:
        output_path = filepath.rsplit(".", 1)[0] + ".wat"

    compiler = WasmCompiler()
    wat = compiler.compile(code, output_path)
    print(f"[Corvus Wasm Compiler] Compiled '{filepath}' -> '{output_path}'")
    return wat
