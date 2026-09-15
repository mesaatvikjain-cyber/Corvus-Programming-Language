# Corvus v4.6 Security Hardening Verification Suite
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Interpreter')))

from std_net import NetworkEngine, _validate_url
from std_crypto import CryptoEngine
from std_process import ProcessEngine
from bytecode import deserialize, MAGIC_HEADER
from vm import CorvusVM, VMError

print("=== 1. Testing Net Security Guardrails ===")
# file:// scheme should be rejected
try:
    _validate_url("file:///etc/passwd")
    print("FAIL: Net allowed file:// scheme")
    sys.exit(1)
except ValueError as e:
    print("PASS: Net blocked file scheme:", e)

res = NetworkEngine.http_get("file:///etc/passwd")
assert not res["ok"] and res["status"] == 500
print("PASS: NetworkEngine.http_get safely caught invalid scheme and returned status 500")

# Invalid port should be rejected
try:
    NetworkEngine.tcp_connect("127.0.0.1", 70000)
    print("FAIL: Net allowed invalid port")
    sys.exit(1)
except ValueError as e:
    print("PASS: Net blocked invalid port:", e)

print("\n=== 2. Testing Crypto Enhancements ===")
# Zero key check
try:
    CryptoEngine.encrypt("hello", "")
    print("FAIL: Allowed empty key")
    sys.exit(1)
except ValueError as e:
    print("PASS: Blocked empty key:", e)

rb = CryptoEngine.random_bytes(16)
assert len(rb) == 32, f"Expected 32 hex chars, got {len(rb)}"
print("PASS: random_bytes(16) generated securely:", rb)

h512 = CryptoEngine.sha512("corvus")
assert len(h512) == 128
print("PASS: sha512 generated:", h512[:16] + "...")

mac = CryptoEngine.hmac_sha256("secret_key", "message")
assert len(mac) == 64
print("PASS: hmac_sha256 generated:", mac[:16] + "...")

print("\n=== 3. Testing Process Security ===")
res = ProcessEngine.run([sys.executable, "-c", "print('secure execution')"])
assert "secure execution" in res["stdout"]
print("PASS: Safe array process run succeeded:", res["stdout"].strip())

print("\n=== 4. Testing Bytecode Deserialization Bounds Check ===")
bad_bytes = MAGIC_HEADER + b"\x00\x00"  # truncated payload with valid header
try:
    deserialize(bad_bytes)
    print("FAIL: Allowed corrupted bytecode")
    sys.exit(1)
except ValueError as e:
    print("PASS: Blocked truncated bytecode:", e)

print("\nALL SECURITY CHECKS PASSED SUCCESSFULLY!")
