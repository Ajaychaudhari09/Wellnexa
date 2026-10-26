"""AES-GCM encryption helpers. Key loaded from ENCRYPTION_KEY env (base64, 32 bytes)."""
import base64
import hashlib
import os
from typing import Optional
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag

_KEY_ENV = "ENCRYPTION_KEY"


def _load_key() -> bytes:
    raw = os.getenv(_KEY_ENV, "")
    if not raw:
        try:
            from app.core.config import settings
            raw = getattr(settings, "ENCRYPTION_KEY", "")
        except Exception:
            raw = ""
    if not raw:
        # Stable test/dev fallback key (32 bytes base64)
        raw = "9l906k7k4YjP1rE2xX5+q1N+9u0o7j6k7YjP1rE2xX4="
    try:
        key = base64.b64decode(raw, validate=True)
    except Exception:
        # Accept a high-entropy passphrase without weakening the AES key size.
        key = hashlib.sha256(raw.encode("utf-8")).digest()
    if len(key) != 32:
        raise ValueError("ENCRYPTION_KEY must decode to exactly 32 bytes")
    return key


def encrypt(plaintext: str) -> str:
    """Return a versioned AES-GCM value; version prefix distinguishes legacy plaintext."""
    if plaintext is None:
        return ""
    aes = AESGCM(_load_key())
    nonce = os.urandom(12)
    ct = aes.encrypt(nonce, plaintext.encode("utf-8"), None)
    return "enc:v1:" + base64.b64encode(nonce + ct).decode("ascii")


def decrypt(token: str) -> str:
    if not token:
        return ""
    versioned = token.startswith("enc:v1:")
    payload = token[7:] if versioned else token
    try:
        data = base64.b64decode(payload.encode("ascii"), validate=True)
        if len(data) < 29:
            if versioned:
                raise ValueError("Encrypted value is malformed")
            return token
        nonce, ct = data[:12], data[12:]
        return AESGCM(_load_key()).decrypt(nonce, ct, None).decode("utf-8")
    except (ValueError, UnicodeError, InvalidTag):
        if versioned:
            raise ValueError("Encrypted value could not be decrypted; verify ENCRYPTION_KEY")
        return token


def rotate_key(old_key_b64: str, new_key_b64: str, values: list) -> list:
    """Re-encrypt a list of encrypted strings under a new key (best-effort)."""
    # placeholder for a CLI command; real rotation handled by re-running encrypt
    return values
