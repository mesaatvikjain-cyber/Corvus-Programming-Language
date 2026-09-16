"""Corvus Language Server Protocol (LSP) Daemon
Standard JSON-RPC 2.0 Language Server for VS Code, Neovim, Sublime, and Helix.
"""

import sys
import json
import os
import re

from lexercorvus import tokenize
from parsercorvus import Parser
from errors import CorvusError

CORVUS_DOCS = {
    "log": "### `log(...)` (Builtin Function)\nPrints one or more values or expressions to standard output.",
    "set": "### `set` (Keyword)\nDeclares or assigns a mutable variable.\n```corvus\nset int; count = 10\nset name = \"Corvus\"\n```",
    "const": "### `const` (Keyword)\nDeclares an immutable constant identifier.\n```corvus\nconst PI = 3.14159\n```",
    "mk": "### `mk func` (Keyword Pair)\nDeclares a function in Corvus.\n```corvus\nmk func add(a, b) [\n    givout a + b\n]\n```",
    "func": "### `func` (Keyword)\nSpecifies a function definition when paired with `mk`.",
    "givout": "### `givout` (Keyword)\nReturns a value from a function or subroutine.\n```corvus\ngivout result\n```",
    "cls": "### `cls Name() [ ... ]` (Keyword)\nDeclares an object-oriented class.\n```corvus\ncls Person() [\n    set name\n    mk func init(n) [ self.name = n ]\n]\n```",
    "self": "### `self` (Identifier)\nRefers to the current class instance.",
    "if": "### `if (condition) [ ... ]`\nConditional branch execution block.",
    "elsif": "### `elsif (condition) [ ... ]`\nAlternative conditional branch.",
    "else": "### `else [ ... ]`\nFallback execution block when previous conditions fail.",
    "while": "### `while (condition) [ ... ]`\nRepeats block while condition evaluates to true.",
    "for": "### `for item in collection [ ... ]`\nIterates across items in a list or range.",
    "try": "### `try [ ... ] error(e) [ ... ] final [ ... ]`\nStructured exception recovery block.",
    "get": "### `get <module>`\nImports a built-in, standard library, or external CPM package.",
    "@": "### `@` (Matrix Multiplication Operator)\nPerforms native 2D matrix multiplication on arrays, NumPy, and PyTorch tensors."
}

COMPLETIONS = [
    {"label": "log", "kind": 3, "detail": "Builtin print function", "insertText": "log(${1:val})"},
    {"label": "mk func", "kind": 14, "detail": "Function declaration", "insertText": "mk func ${1:name}(${2:params}) [\n    givout ${3:result}\n]"},
    {"label": "cls", "kind": 7, "detail": "Class declaration", "insertText": "cls ${1:Name}() [\n    mk func init(${2:args}) [\n        ${3:self.val = args}\n    ]\n]"},
    {"label": "set", "kind": 14, "detail": "Variable declaration", "insertText": "set ${1:name} = ${2:value}"},
    {"label": "const", "kind": 14, "detail": "Constant declaration", "insertText": "const ${1:NAME} = ${2:value}"},
    {"label": "givout", "kind": 14, "detail": "Return statement", "insertText": "givout ${1:val}"},
    {"label": "if", "kind": 14, "detail": "If conditional", "insertText": "if (${1:condition}) [\n    ${2}\n]"},
    {"label": "while", "kind": 14, "detail": "While loop", "insertText": "while (${1:condition}) [\n    ${2}\n]"},
    {"label": "for", "kind": 14, "detail": "For loop", "insertText": "for ${1:item} in ${2:collection} [\n    ${3}\n]"},
    {"label": "try", "kind": 14, "detail": "Try/Error block", "insertText": "try [\n    ${1}\n] error(err) [\n    log(err[\"message\"])\n]"},
    {"label": "get", "kind": 9, "detail": "Import module", "insertText": "get ${1:module}"},
    {"label": "crow", "kind": 9, "detail": "Concurrency module", "insertText": "crow"},
    {"label": "web", "kind": 9, "detail": "Micro web framework", "insertText": "web"},
    {"label": "crypto", "kind": 9, "detail": "Cryptography module", "insertText": "crypto"},
    {"label": "sqlite", "kind": 9, "detail": "SQLite database module", "insertText": "sqlite"},
    {"label": "math", "kind": 9, "detail": "Math module", "insertText": "math"},
]

class CorvusLanguageServer:
    def __init__(self):
        self.documents = {}

    def read_message(self):
        """Read a JSON-RPC message from standard input."""
        content_length = None
        while True:
            line = sys.stdin.readline()
            if not line:
                return None
            line = line.strip()
            if not line:
                break
            if line.startswith("Content-Length:"):
                content_length = int(line.split(":")[1].strip())

        if content_length is None:
            return None

        body = sys.stdin.read(content_length)
        return json.loads(body)

    def write_message(self, response_dict):
        """Send a JSON-RPC response to standard output."""
        body = json.dumps(response_dict)
        header = f"Content-Length: {len(body.encode('utf-8'))}\r\n\r\n"
        sys.stdout.write(header + body)
        sys.stdout.flush()

    def publish_diagnostics(self, uri: str, text: str):
        """Check syntax of document and publish LSP diagnostics."""
        diagnostics = []
        try:
            tokens = tokenize(text)
            parser = Parser(tokens)
            parser.parse()
        except CorvusError as e:
            line = max(0, getattr(e, "line", 1) - 1)
            col = max(0, getattr(e, "column", 1) - 1)
            diagnostics.append({
                "range": {
                    "start": {"line": line, "character": col},
                    "end": {"line": line, "character": col + 10}
                },
                "severity": 1, # Error
                "message": f"Corvus Syntax Error: {e.message}",
                "source": "corvus-lsp"
            })
        except Exception as e:
            diagnostics.append({
                "range": {
                    "start": {"line": 0, "character": 0},
                    "end": {"line": 0, "character": 5}
                },
                "severity": 1,
                "message": f"Parse Error: {str(e)}",
                "source": "corvus-lsp"
            })

        self.write_message({
            "jsonrpc": "2.0",
            "method": "textDocument/publishDiagnostics",
            "params": {
                "uri": uri,
                "diagnostics": diagnostics
            }
        })

    def handle_request(self, msg):
        msg_id = msg.get("id")
        method = msg.get("method")
        params = msg.get("params", {})

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "capabilities": {
                        "textDocumentSync": 1, # Full sync
                        "hoverProvider": True,
                        "completionProvider": {
                            "resolveProvider": False,
                            "triggerCharacters": [".", "@", " "]
                        }
                    },
                    "serverInfo": {
                        "name": "corvus-lsp",
                        "version": "5.0.0"
                    }
                }
            }

        elif method == "textDocument/didOpen":
            doc = params.get("textDocument", {})
            uri = doc.get("uri")
            text = doc.get("text", "")
            self.documents[uri] = text
            self.publish_diagnostics(uri, text)
            return None

        elif method == "textDocument/didChange":
            doc = params.get("textDocument", {})
            uri = doc.get("uri")
            changes = params.get("contentChanges", [])
            if changes:
                text = changes[-1].get("text", "")
                self.documents[uri] = text
                self.publish_diagnostics(uri, text)
            return None

        elif method == "textDocument/hover":
            doc = params.get("textDocument", {})
            uri = doc.get("uri")
            pos = params.get("position", {})
            line_idx = pos.get("line", 0)
            char_idx = pos.get("character", 0)

            content = self.documents.get(uri, "")
            lines = content.splitlines()
            hover_md = None
            if line_idx < len(lines):
                line = lines[line_idx]
                # Find word at character index
                for word, docstring in CORVUS_DOCS.items():
                    if word in line:
                        hover_md = docstring
                        break

            if not hover_md:
                hover_md = "Corvus Language Primitive"

            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "contents": {
                        "kind": "markdown",
                        "value": hover_md
                    }
                }
            }

        elif method == "textDocument/completion":
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": COMPLETIONS
            }

        elif method == "shutdown":
            return {"jsonrpc": "2.0", "id": msg_id, "result": None}

        elif method == "exit":
            sys.exit(0)

        return {"jsonrpc": "2.0", "id": msg_id, "result": None}

    def start(self):
        """Start the Language Server message loop."""
        while True:
            msg = self.read_message()
            if not msg:
                break
            resp = self.handle_request(msg)
            if resp:
                self.write_message(resp)

def start_lsp_server():
    server = CorvusLanguageServer()
    server.start()
