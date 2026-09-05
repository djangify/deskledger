"""Fernet encryption utilities for sensitive fields (e.g. the OCR API key).

The key comes from ``settings.ENCRYPTION_KEY``, which the settings module always
populates — from the ``ENCRYPTION_KEY`` env var, or a per-install key persisted
outside the database. Ported from the sister project's shop.encryption so the two
apps behave identically.
"""

import base64
import logging
from functools import lru_cache

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings

logger = logging.getLogger(__name__)


class EncryptionError(Exception):
    """Raised when encryption fails (no usable key)."""


@lru_cache(maxsize=1)
def get_fernet() -> Fernet | None:
    """Return a cached Fernet built from settings.ENCRYPTION_KEY, or None."""
    key = getattr(settings, "ENCRYPTION_KEY", None)
    if not key:
        logger.warning("ENCRYPTION_KEY not configured — encrypted fields will not work")
        return None
    try:
        if isinstance(key, str):
            key = key.encode("utf-8")
        return Fernet(key)
    except Exception as exc:  # invalid key material
        logger.error("Invalid ENCRYPTION_KEY: %s", exc)
        return None


def encrypt_value(plaintext: str) -> str:
    """Encrypt a string, returning base64 ciphertext. Empty in, empty out."""
    if not plaintext:
        return ""
    fernet = get_fernet()
    if not fernet:
        raise EncryptionError("ENCRYPTION_KEY not configured")
    encrypted = fernet.encrypt(plaintext.encode("utf-8"))
    return base64.urlsafe_b64encode(encrypted).decode("utf-8")


def decrypt_value(ciphertext: str) -> str:
    """Decrypt base64 ciphertext back to plaintext. Returns "" on any failure."""
    if not ciphertext:
        return ""
    fernet = get_fernet()
    if not fernet:
        logger.warning("Cannot decrypt: ENCRYPTION_KEY not configured")
        return ""
    try:
        encrypted = base64.urlsafe_b64decode(ciphertext.encode("utf-8"))
        return fernet.decrypt(encrypted).decode("utf-8")
    except InvalidToken:
        logger.error("Decryption failed: invalid token (wrong key or corrupted data)")
        return ""
    except Exception as exc:
        logger.error("Decryption failed: %s", exc)
        return ""


def generate_encryption_key() -> str:
    """Generate a fresh Fernet key string (for populating ENCRYPTION_KEY)."""
    return Fernet.generate_key().decode("utf-8")
