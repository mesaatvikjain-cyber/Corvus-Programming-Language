import urllib.request
import urllib.parse
import socket
import json
import re

# Corvus Native Network Standard Library Engine (v4.2)

def validate_url(url: str) -> str:
    try:
        if "/../" in url or re.search(r"/%2e%2e/", url, re.IGNORECASE):
            raise ValueError("Invalid path")
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme not in ("http", "https"):
            raise ValueError("Invalid protocol")
        if not parsed.hostname:
            raise ValueError("Invalid host")
        allowed_domains = ["example.com"]  # add your allowed domains here
        if parsed.hostname.lower() not in allowed_domains:
            raise ValueError("Invalid host")
        return url
    except Exception:
        raise ValueError("Invalid URL")

class NetworkEngine:
    @staticmethod
    def http_get(url, headers=None):
        req = urllib.request.Request(url, headers=headers or {})
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                body = response.read().decode('utf-8', errors='replace')
                return {
                    "status": response.status,
                    "body": body,
                    "ok": response.status >= 200 and response.status < 300
                }
        except urllib.error.HTTPError as e:
            return {"status": e.code, "body": e.read().decode('utf-8', errors='replace'), "ok": False}
        except Exception as e:
            return {"status": 500, "body": str(e), "ok": False}

    @staticmethod
    def http_post(url, body="", headers=None):
        url = validate_url(url)
        headers = headers or {}
        if isinstance(body, dict):
            body_bytes = json.dumps(body).encode('utf-8')
            headers['Content-Type'] = 'application/json'
        elif isinstance(body, str):
            body_bytes = body.encode('utf-8')
        else:
            body_bytes = str(body).encode('utf-8')

        req = urllib.request.Request(url, data=body_bytes, headers=headers, method='POST')
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                res_body = response.read().decode('utf-8', errors='replace')
                return {
                    "status": response.status,
                    "body": res_body,
                    "ok": response.status >= 200 and response.status < 300
                }
        except urllib.error.HTTPError as e:
            return {"status": e.code, "body": e.read().decode('utf-8', errors='replace'), "ok": False}
        except Exception as e:
            return {"status": 500, "body": str(e), "ok": False}

    @staticmethod
    def tcp_connect(host, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, int(port)))
        return sock

    @staticmethod
    def tcp_send(sock, data):
        if isinstance(data, str):
            data = data.encode('utf-8')
        sock.sendall(data)
        return len(data)

    @staticmethod
    def tcp_recv(sock, bufsize=1024):
        res = sock.recv(int(bufsize))
        return res.decode('utf-8', errors='replace')

    @staticmethod
    def tcp_close(sock):
        sock.close()

_global_net_engine = NetworkEngine()
