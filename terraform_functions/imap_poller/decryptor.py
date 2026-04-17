import base64
import json
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend


def decrypt(encrypted_data: str, secret: str) -> dict:
    """
    Дешифровка данных с использованием AES-256-GCM.
    
    Формат: base64(salt[16] + iv[12] + ciphertext)
    """
    try:
        data = base64.b64decode(encrypted_data)
    except Exception as e:
        raise ValueError(f"Invalid base64: {e}")

    if len(data) < 28:
        raise ValueError("Data too short")

    salt = data[:16]
    iv = data[16:28]
    ciphertext = data[28:]

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = kdf.derive(secret.encode())

    aesgcm = AESGCM(key)
    plaintext = aesgcm.decrypt(iv, ciphertext, None)

    return json.loads(plaintext.decode('utf-8'))