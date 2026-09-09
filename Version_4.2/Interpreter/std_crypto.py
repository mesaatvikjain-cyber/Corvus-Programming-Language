import hashlib
import base64

# Corvus Cryptography, Hashes, Base64 & Cipher Engine (v4.2)

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
        # High-speed XOR key cipher stream
        data_str = str(data)
        key_str = str(key)
        out = []
        for i, ch in enumerate(data_str):
            k = key_str[i % len(key_str)]
            out.append(chr(ord(ch) ^ ord(k)))
        raw_bytes = "".join(out).encode('latin1')
        return base64.b64encode(raw_bytes).decode('utf-8')

    @staticmethod
    def decrypt(cipher_text, key):
        try:
            raw_bytes = base64.b64decode(cipher_text.encode('utf-8')).decode('latin1')
            key_str = str(key)
            out = []
            for i, ch in enumerate(raw_bytes):
                k = key_str[i % len(key_str)]
                out.append(chr(ord(ch) ^ ord(k)))
            return "".join(out)
        except Exception as e:
            return ""

_global_crypto_engine = CryptoEngine()
