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

import socket
import hashlib
import base64
import struct

class CorvusWebSocketServer:
    """Pure Standard Library RFC 6455 WebSocket Server for Corvus."""
    WS_GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

    def __init__(self, port: int = 8081):
        self.port = int(port)
        self.clients = []
        self.running = False
        self.server_sock = None
        self.thread = None
        self._on_connect_cb = None
        self._on_message_cb = None
        self._on_close_cb = None

    def on_connect(self, callback: Any):
        self._on_connect_cb = callback
        return self

    def on_message(self, callback: Any):
        self._on_message_cb = callback
        return self

    def on_close(self, callback: Any):
        self._on_close_cb = callback
        return self

    def start(self, blocking: bool = False):
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_sock.bind(('0.0.0.0', self.port))
        self.server_sock.listen(128)
        self.running = True
        print(f"[Corvus WebSocket Server] Active at ws://127.0.0.1:{self.port}")

        if blocking:
            self._listen_loop()
        else:
            self.thread = threading.Thread(target=self._listen_loop, daemon=True)
            self.thread.start()
        return self

    def _listen_loop(self):
        while self.running:
            try:
                client_sock, addr = self.server_sock.accept()
                t = threading.Thread(target=self._handle_client, args=(client_sock, addr), daemon=True)
                t.start()
            except Exception:
                break

    def _handle_client(self, client_sock: socket.socket, addr: tuple):
        # 1. Perform RFC 6455 Handshake
        try:
            req_data = client_sock.recv(4096).decode('utf-8', errors='replace')
            headers = {}
            for line in req_data.split("\r\n"):
                if ": " in line:
                    k, v = line.split(": ", 1)
                    headers[k.lower()] = v.strip()

            sec_key = headers.get("sec-websocket-key")
            if not sec_key:
                client_sock.close()
                return

            accept_token = base64.b64encode(
                hashlib.sha1((sec_key + self.WS_GUID).encode('utf-8')).digest()
            ).decode('utf-8')

            handshake_resp = (
                "HTTP/1.1 101 Switching Protocols\r\n"
                "Upgrade: websocket\r\n"
                "Connection: Upgrade\r\n"
                f"Sec-WebSocket-Accept: {accept_token}\r\n\r\n"
            )
            client_sock.sendall(handshake_resp.encode('utf-8'))
            self.clients.append(client_sock)

            if self._on_connect_cb:
                self._invoke_cb(self._on_connect_cb, client_sock, str(addr))

            # 2. Read WebSocket Frames
            while self.running:
                head = client_sock.recv(2)
                if not head or len(head) < 2:
                    break
                b1, b2 = head[0], head[1]
                opcode = b1 & 0x0F
                masked = (b2 & 0x80) != 0
                payload_len = b2 & 0x7F

                if payload_len == 126:
                    ext = client_sock.recv(2)
                    payload_len = struct.unpack(">H", ext)[0]
                elif payload_len == 127:
                    ext = client_sock.recv(8)
                    payload_len = struct.unpack(">Q", ext)[0]

                masks = client_sock.recv(4) if masked else b""
                raw_payload = bytearray()
                while len(raw_payload) < payload_len:
                    chunk = client_sock.recv(min(4096, payload_len - len(raw_payload)))
                    if not chunk:
                        break
                    raw_payload.extend(chunk)

                if masked:
                    decoded = bytearray(raw_payload[i] ^ masks[i % 4] for i in range(len(raw_payload)))
                else:
                    decoded = raw_payload

                if opcode == 0x8:  # Close frame
                    break
                elif opcode == 0x9:  # Ping
                    # Reply with Pong (0xA)
                    pong_frame = bytearray([0x8A, 0])
                    client_sock.sendall(pong_frame)
                elif opcode == 0x1:  # Text frame
                    msg_text = decoded.decode('utf-8', errors='replace')
                    if self._on_message_cb:
                        self._invoke_cb(self._on_message_cb, client_sock, msg_text)

        except Exception:
            pass
        finally:
            if client_sock in self.clients:
                self.clients.remove(client_sock)
            if self._on_close_cb:
                self._invoke_cb(self._on_close_cb, client_sock)
            try:
                client_sock.close()
            except Exception:
                pass

    def send(self, client_sock: socket.socket, message: str) -> bool:
        """Send a UTF-8 text message to a client socket."""
        try:
            data = str(message).encode('utf-8')
            length = len(data)
            frame = bytearray([0x81])  # FIN + Text Opcode

            if length <= 125:
                frame.append(length)
            elif length <= 65535:
                frame.append(126)
                frame.extend(struct.pack(">H", length))
            else:
                frame.append(127)
                frame.extend(struct.pack(">Q", length))

            frame.extend(data)
            client_sock.sendall(frame)
            return True
        except Exception:
            return False

    def broadcast(self, message: str) -> int:
        """Broadcast a message to all connected WebSocket clients."""
        sent_count = 0
        for c in list(self.clients):
            if self.send(c, message):
                sent_count += 1
        return sent_count

    def stop(self):
        self.running = False
        for c in self.clients:
            try:
                c.close()
            except Exception:
                pass
        self.clients.clear()
        if self.server_sock:
            try:
                self.server_sock.close()
            except Exception:
                pass
        print("[Corvus WebSocket Server] Stopped.")

    def _invoke_cb(self, cb: Any, *args):
        try:
            if hasattr(cb, "call"):
                cb.call(list(args))
            elif callable(cb):
                cb(*args)
        except Exception as e:
            print(f"[Corvus WS Callback Error]: {e}")

def create_server():
    return CorvusWebServer()

def create_ws_server(port: int = 8081):
    return CorvusWebSocketServer(port=port)

