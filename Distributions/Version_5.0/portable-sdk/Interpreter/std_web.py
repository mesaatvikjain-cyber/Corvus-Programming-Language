"""Corvus Native Micro Web Server Engine
Zero-dependency lightweight HTTP REST API framework.
"""

import http.server
import json
import threading
import urllib.parse
from typing import Dict, Any, Callable

class CorvusWebServer:
    def __init__(self):
        self.routes: Dict[str, Any] = {}
        self.server = None
        self.thread = None
        self.running = False

    def route(self, path: str, handler: Any, method: str = "GET"):
        """Register a route handler for a path."""
        key = f"{method.upper()}:{path}"
        self.routes[key] = handler
        if path not in self.routes:
            self.routes[path] = handler
        return self

    def get(self, path: str, handler: Any):
        return self.route(path, handler, "GET")

    def post(self, path: str, handler: Any):
        return self.route(path, handler, "POST")

    def listen(self, port: int = 8080, blocking: bool = False):
        """Start the HTTP server on the specified port."""
        routes = self.routes

        class CorvusHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
            def log_message(self, format, *args):
                pass

            def do_GET(self):
                self._dispatch("GET")

            def do_POST(self):
                self._dispatch("POST")

            def do_OPTIONS(self):
                self.send_response(204)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
                self.send_header("Access-Control-Allow-Headers", "Content-Type")
                self.end_headers()

            def _dispatch(self, method: str):
                parsed = urllib.parse.urlparse(self.path)
                req_path = parsed.path
                query = urllib.parse.parse_qs(parsed.query)
                params = {k: v[0] if len(v) == 1 else v for k, v in query.items()}

                body = None
                content_len = int(self.headers.get('Content-Length', 0))
                if content_len > 0:
                    raw = self.rfile.read(content_len).decode('utf-8', errors='replace')
                    try:
                        body = json.loads(raw)
                    except Exception:
                        body = raw

                req_obj = {
                    "method": method,
                    "path": req_path,
                    "params": params,
                    "body": body,
                    "headers": dict(self.headers)
                }

                handler = routes.get(f"{method}:{req_path}") or routes.get(req_path)
                if handler is None:
                    self.send_response(404)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    payload = json.dumps({"error": "Not Found", "status": 404, "path": req_path})
                    self.wfile.write(payload.encode("utf-8"))
                    return

                try:
                    if callable(handler):
                        res = handler(req_obj)
                    elif hasattr(handler, "call"):
                        # Corvus AST Lambda / Function object
                        res = handler.call([req_obj])
                    elif hasattr(handler, "__call__"):
                        res = handler(req_obj)
                    else:
                        res = str(handler)

                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()

                    if isinstance(res, (dict, list)):
                        out = json.dumps(res)
                    else:
                        out = str(res)
                    self.wfile.write(out.encode("utf-8"))
                except Exception as e:
                    self.send_response(500)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    err_payload = json.dumps({"error": str(e), "status": 500})
                    self.wfile.write(err_payload.encode("utf-8"))

        server_address = ('', int(port))
        self.server = http.server.HTTPServer(server_address, CorvusHTTPRequestHandler)
        self.running = True
        print(f"[Corvus Web Server] Active at http://127.0.0.1:{port}")

        if blocking:
            try:
                self.server.serve_forever()
            except KeyboardInterrupt:
                self.stop()
        else:
            self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.thread.start()
        return True

    def stop(self):
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            self.running = False
            print("[Corvus Web Server] Stopped.")

def create_server():
    return CorvusWebServer()
