"""Custom model fields for the accounts app.

``EncryptedCharField`` stores its value encrypted at rest (Fernet) and decrypts
transparently on read, so a leaked database or backup file never exposes the
plaintext. Ported from the sister project's shop.fields.
"""

import base64

from django import forms
from django.db import models

from .encryption import decrypt_value, encrypt_value


class EncryptedCharField(models.CharField):
    """A CharField that encrypts data at rest.

    Ciphertext is longer than plaintext, so pick a max_length of roughly 2–3×
    the longest plaintext you expect to store.
    """

    description = "An encrypted string"

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("max_length", 500)
        kwargs.setdefault("blank", True)
        kwargs.setdefault("default", "")
        super().__init__(*args, **kwargs)

    def get_prep_value(self, value):
        """Encrypt before writing to the database."""
        if value is None or value == "":
            return ""
        if self._is_encrypted(value):
            return value  # already encrypted — don't double-encrypt
        try:
            return encrypt_value(value)
        except Exception:
            # Never fall back to storing plaintext.
            return ""

    def from_db_value(self, value, expression, connection):
        """Decrypt when reading from the database."""
        if value is None or value == "":
            return ""
        return decrypt_value(value)

    def to_python(self, value):
        if value is None:
            return ""
        return str(value)

    def _is_encrypted(self, value):
        """Heuristic: our ciphertext is base64 wrapping a Fernet token, whose
        first byte is the version marker 0x80."""
        if not value or len(value) < 50:
            return False
        try:
            decoded = base64.urlsafe_b64decode(value.encode("utf-8"))
            return decoded[0:1] == b"\x80"
        except Exception:
            return False

    def formfield(self, **kwargs):
        defaults = {
            "widget": forms.PasswordInput(
                attrs={"autocomplete": "new-password"}
            ),
            "required": False,
        }
        defaults.update(kwargs)
        return super().formfield(**defaults)
