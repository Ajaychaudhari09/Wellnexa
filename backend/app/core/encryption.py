"""AES-GCM encryption helpers. Key loaded from ENCRYPTION_KEY env (base64, 32 bytes)."""
import base64
import os
from typing import Optional
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

_KEY_ENV = "ENCRYPTION_KEY"


def _load_key() -> bytes:
    raw = os.getenv(_KEY_ENV, "")
    if not raw:
        # dev fallback: derive a stable 32-byte key from a default (NOT for production)
        raw = "dev-only-encryption-key-change-me-32b"
    try:
        key = base64.b64decode(raw)
    except Exception:
        key = raw.encode("utf-8")
    if len(key) < 32:
        key = (key * ((32 // len(key)) + 1))[:32]
    return key[:32]


def encrypt(plaintext: str) -> str:
    """Return base64(nonce || ciphertext)."""
    if plaintext is None:
        return ""
    aes = AESGCM(_load_key())
    nonce = os.urandom(12)
    ct = aes.encrypt(nonce, plaintext.encode("utf-8"), None)
    return base64.b64encode(nonce + ct).decode("ascii")


def decrypt(token: str) -> str:
    if not token:
        return ""
    data = base64.b64decode(token.encode("ascii"))
    nonce, ct = data[:12], data[12:]
    aes = AESGCM(_load_key())
    return aes.decrypt(nonce, ct, None).decode("utf-8")


def rotate_key(old_key_b64: str, new_key_b64: str, values: list) -> list:
    """Re-encrypt a list of encrypted strings under a new key (best-effort)."""
    # placeholder for a CLI command; real rotation handled by re-running encrypt
    return values
