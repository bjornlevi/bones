import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

NONCE_LEN = 12

def encrypt(plaintext: bytes, dek: bytes) -> bytes:
    aes = AESGCM(dek)
    nonce = os.urandom(NONCE_LEN)
    ct = aes.encrypt(nonce, plaintext, None)
    return nonce + ct

def decrypt(blob: bytes, dek: bytes) -> bytes:
    nonce, ct = blob[:NONCE_LEN], blob[NONCE_LEN:]
    aes = AESGCM(dek)
    return aes.decrypt(nonce, ct, None)
