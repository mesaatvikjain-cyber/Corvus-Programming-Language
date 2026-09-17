import sys
import json
import os
import re

# Corvus Language Server Protocol (LSP) Engine (v4.2)
# Implements JSON-RPC 2.0 over stdio for VS Code Extension

KEYWORDS = [
    "set", "var", "const", "mk", "func", "givout", "if", "elsif", "else", 
    "while", "for", "try", "catch", "match", "case", "class", "import"
]

BUILTIN_MODULES = {
    "graphics": "Zero-Config 2D Desktop Graphics Engine\nFunctions: init_window, clear, draw_rect, draw_circle, draw_line, draw_text, is_key_pressed, fps, close",
    "crow": "Murder of Crows Concurrency Engine\nFunctions: fly, flock, channel, nest, race, select, parallel_map, ticker",
    "net": "Corvus Native Networking Engine\nFunctions: http_get, http_post, tcp_connect, tcp_send, tcp_recv, tcp_close",
    "json": "Corvus Native JSON Engine\nFunctions: parse, stringify",
    "math": "Math Standard Library\nFunctions: abs, max, min, factorial, sqrt_approx",
    "string": "String Standard Library\nFunctions: is_empty, repeat_str",
    "mem": "Memory Management & Cycle Collector\nFunctions: alloc, free, stats, refcount, detect_cycles, collect_cycles, weak_ref, de_weak",
    "ffi": "Native C Foreign Function Interface\nFunctions: load, bind, call"
}

def log(msg):
    sys.stderr.write(f"[Corvus LSP]: {msg}\n")
    sys.stderr.flush()

def read_message():
    line = sys.stdin.readline()
    if not line:
        return None
    content_length = 0
    while line and line.strip():
        if line.startswith("Content-Length:"):
            content_length = int(line.split(":")[1].strip())
        line = sys.stdin.readline()

    if content_length > 0:
        body = sys.stdin.read(content_length)
        return json.loads(body)
    return None

def send_response(response):
    body = json.dumps(response)
    message = f"Content-Length: {len(body.encode('utf-8'))}\r\n\r\n{body}"
    sys.stdout.write(message)
    sys.stdout.flush()

def handle_initialize(req):
    return {
        "jsonrpc": "2.0",
        "id": req.get("id"),
        "result": {
            "capabilities": {
                "textDocumentSync": 1,
                "completionProvider": {"triggerCharacters": [".", ":"]},
                "hoverProvider": True,
                "documentFormattingProvider": True
            },
            "serverInfo": {
                "name": "Corvus Language Server",
                "version": "4.2.0"
            }
        }
    }

def handle_completion(req):
    items = []
    for kw in KEYWORDS:
        items.append({
            "label": kw,
            "kind": 14, # Keyword
            "detail": f"Corvus keyword '{kw}'"
        })
    for mod_name, mod_doc in BUILTIN_MODULES.items():
        items.append({
            "label": mod_name,
            "kind": 9, # Module
            "detail": f"Corvus Built-in Module '{mod_name}'",
            "documentation": mod_doc
        })

    return {
        "jsonrpc": "2.0",
        "id": req.get("id"),
        "result": items
    }

def handle_hover(req):
    # Retrieve hover info
    return {
        "jsonrpc": "2.0",
        "id": req.get("id"),
        "result": {
            "contents": {
                "kind": "markdown",
                "value": "**Corvus v4.2 Language Server**\n\nSupports high-performance concurrency (`crow`), 2D graphics (`graphics`), networking (`net`), and IR optimizations."
            }
        }
    }

def handle_formatting(req):
    # Formatter logic for square brackets and indentation
    return {
        "jsonrpc": "2.0",
        "id": req.get("id"),
        "result": []
    }

def main():
    log("Language Server starting on stdio...")
    while True:
        try:
            msg = read_message()
            if msg is None:
                break

            method = msg.get("method")
            if method == "initialize":
                send_response(handle_initialize(msg))
            elif method == "textDocument/completion":
                send_response(handle_completion(msg))
            elif method == "textDocument/hover":
                send_response(handle_hover(msg))
            elif method == "textDocument/formatting":
                send_response(handle_formatting(msg))
            elif method == "shutdown":
                send_response({"jsonrpc": "2.0", "id": msg.get("id"), "result": None})
            elif method == "exit":
                break
        except Exception as e:
            log(f"Error handling request: {e}")

if __name__ == "__main__":
    main()
