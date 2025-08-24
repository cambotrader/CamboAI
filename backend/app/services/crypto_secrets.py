from __future__ import annotations
import os
from typing import Tuple

try:
    from cryptography.fernet import Fernet, InvalidToken
except Exception:
    Fernet = None  # type: ignore
    InvalidToken = Exception  # type: ignore

ENV_KEY = "SECRET_ENC_KEY"

class SecretCrypto:
    def __init__(self):
        self._key = os.getenv(ENV_KEY)
        self._fernet = Fernet(self._key) if (self._key and Fernet is not None) else None

    @property
    def enabled(self) -> bool:
        return self._fernet is not None

    def encrypt(self, plaintext: str) -> Tuple[str, bool]:
        if not plaintext:
            return plaintext, False
        if self._fernet is None:
            return plaintext, False
        token = self._fernet.encrypt(plaintext.encode("utf-8")).decode("utf-8")
        return token, True

    def decrypt(self, token: str) -> Tuple[str, bool]:
        if not token:
            return token, False
        if self._fernet is None:
            return token, False
        try:
            pt = self._fernet.decrypt(token.encode("utf-8")).decode("utf-8")
            return pt, True
        except InvalidToken:
            return token, False

_singleton: SecretCrypto | None = None

def get_crypto() -> SecretCrypto:
    global _singleton
    if _singleton is None:
        _singleton = SecretCrypto()
    return _singleton