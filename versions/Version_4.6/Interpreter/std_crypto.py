import hashlib
import hmac
import base64
import os
import secrets

# Corvus Cryptography, Hashes, Authentication & Cipher Engine (v4.6 - Security Hardened)

class CryptoEngine:
    @staticmethod
    def md5(data):
        if not isinstance(data, bytes):
            data = str(data).encode('utf-8')
        return hashlib.md5(data).hexdigest()

    @staticmethod
    def sha256(data):
        if not isinstance(data, bytes):
            data = str(data).encode('utf-8')
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def sha512(data):
        if not isinstance(data, bytes):
            data = str(data).encode('utf-8')
        return hashlib.sha512(data).hexdigest()

    @staticmethod
    def hmac_sha256(key, message):
        """Cryptographic HMAC-SHA256 message authentication."""
        if not isinstance(key, bytes):
            key = str(key).encode('utf-8')
        if not isinstance(message, bytes):
            message = str(message).encode('utf-8')
        return hmac.new(key, message, hashlib.sha256).hexdigest()

    @staticmethod
    def random_bytes(length=32):
        """Cryptographically secure pseudorandom bytes (hex encoded)."""
        length = max(1, int(length))
        return secrets.token_hex(length)

    @staticmethod
    def base64_encode(data):
        if not isinstance(data, bytes):
            data = str(data).encode('utf-8')
        return base64.b64encode(data).decode('utf-8')

    @staticmethod
    def base64_decode(encoded_str):
        if not isinstance(encoded_str, bytes):
            encoded_str = str(encoded_str).encode('utf-8')
        return base64.b64decode(encoded_str).decode('utf-8', errors='replace')

    @staticmethod
    def encrypt(data, key):
        data_str = str(data)
        key_str = str(key)
        if not key_str:
            raise ValueError("Encryption key cannot be empty.")
        out = []
        key_len = len(key_str)
        for i, ch in enumerate(data_str):
            k = key_str[i % key_len]
            out.append(chr(ord(ch) ^ ord(k)))
        raw_bytes = "".join(out).encode('latin1')
        return base64.b64encode(raw_bytes).decode('utf-8')

    @staticmethod
    def decrypt(cipher_text, key):
        key_str = str(key)
        if not key_str:
            raise ValueError("Decryption key cannot be empty.")
        try:
            raw_bytes = base64.b64decode(cipher_text.encode('utf-8')).decode('latin1')
            out = []
            key_len = len(key_str)
            for i, ch in enumerate(raw_bytes):
                k = key_str[i % key_len]
                out.append(chr(ord(ch) ^ ord(k)))
            return "".join(out)
        except Exception:
            return ""

_global_crypto_engine = CryptoEngine()
