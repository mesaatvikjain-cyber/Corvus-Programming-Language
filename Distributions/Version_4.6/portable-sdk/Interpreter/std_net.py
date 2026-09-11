import urllib.request
import urllib.parse
import socket
import json

# Corvus Native Network Standard Library Engine (v4.6 - Security Hardened)

ALLOWED_SCHEMES = {"http", "https"}
MAX_RESPONSE_BYTES = 10 * 1024 * 1024  # 10 MB maximum payload to prevent memory DoS

def _validate_url(url: str):
    parsed = urllib.parse.urlparse(str(url).strip())
    if not parsed.scheme or parsed.scheme.lower() not in ALLOWED_SCHEMES:
        raise ValueError(f"Insecure or invalid URL scheme '{parsed.scheme}'. Only http and https are permitted.")
    if not parsed.netloc:
        raise ValueError("Invalid URL: Missing network host domain/IP.")
    return parsed.geturl()

class NetworkEngine:
    @staticmethod
    def http_get(url, headers=None, timeout=10):
        try:
            safe_url = _validate_url(url)
            req = urllib.request.Request(safe_url, headers=headers or {})
            with urllib.request.urlopen(req, timeout=timeout) as response:
                body_bytes = response.read(MAX_RESPONSE_BYTES + 1)
                if len(body_bytes) > MAX_RESPONSE_BYTES:
                    return {"status": 413, "body": "Payload Too Large (Exceeds 10MB limit)", "ok": False}
                body = body_bytes.decode("utf-8", errors="replace")
                return {
                    "status": response.status,
                    "body": body,
                    "ok": 200 <= response.status < 300
                }
        except urllib.error.HTTPError as e:
            err_body = e.read(MAX_RESPONSE_BYTES).decode("utf-8", errors="replace")
            return {"status": e.code, "body": err_body, "ok": False}
        except Exception as e:
            return {"status": 500, "body": str(e), "ok": False}

    @staticmethod
    def http_post(url, body="", headers=None, timeout=10):
        try:
            safe_url = _validate_url(url)
            headers = dict(headers or {})
            if isinstance(body, dict):
                body_bytes = json.dumps(body).encode("utf-8")
                headers["Content-Type"] = "application/json"
            elif isinstance(body, str):
                body_bytes = body.encode("utf-8")
            else:
                body_bytes = str(body).encode("utf-8")

            req = urllib.request.Request(safe_url, data=body_bytes, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=timeout) as response:
                res_bytes = response.read(MAX_RESPONSE_BYTES + 1)
                if len(res_bytes) > MAX_RESPONSE_BYTES:
                    return {"status": 413, "body": "Payload Too Large (Exceeds 10MB limit)", "ok": False}
                res_body = res_bytes.decode("utf-8", errors="replace")
                return {
                    "status": response.status,
                    "body": res_body,
                    "ok": 200 <= response.status < 300
                }
        except urllib.error.HTTPError as e:
            err_body = e.read(MAX_RESPONSE_BYTES).decode("utf-8", errors="replace")
            return {"status": e.code, "body": err_body, "ok": False}
        except Exception as e:
            return {"status": 500, "body": str(e), "ok": False}

    @staticmethod
    def tcp_connect(host, port, timeout=10):
        port_num = int(port)
        if not (1 <= port_num <= 65535):
            raise ValueError(f"Invalid TCP port {port_num}. Must be in range 1-65535.")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((str(host), port_num))
        return sock

    @staticmethod
    def tcp_send(sock, data):
        if isinstance(data, str):
            data = data.encode("utf-8")
        sock.sendall(data)
        return len(data)

    @staticmethod
    def tcp_recv(sock, bufsize=1024):
        bufsize = min(int(bufsize), 65536)
        res = sock.recv(bufsize)
        return res.decode("utf-8", errors="replace")

    @staticmethod
    def tcp_close(sock):
        try:
            sock.close()
        except Exception:
            pass

_global_net_engine = NetworkEngine()
