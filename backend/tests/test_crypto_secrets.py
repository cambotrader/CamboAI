from app.services.crypto_secrets import get_crypto
import os

def test_encrypt_decrypt_roundtrip(monkeypatch):
    try:
        from cryptography.fernet import Fernet
    except Exception:
        return  # cryptography not installed in this env
    key = Fernet.generate_key().decode()
    monkeypatch.setenv("SECRET_ENC_KEY", key)
    # reinit
    from importlib import reload
    import app.services.crypto_secrets as cs
    reload(cs)
    crypto = cs.get_crypto()
    token, enc = crypto.encrypt("secret")
    assert enc and token != "secret"
    pt, dec = crypto.decrypt(token)
    assert dec and pt == "secret"


def test_encrypt_disabled(monkeypatch):
    monkeypatch.delenv("SECRET_ENC_KEY", raising=False)
    from importlib import reload
    import app.services.crypto_secrets as cs
    reload(cs)
    crypto = cs.get_crypto()
    token, enc = crypto.encrypt("secret")
    assert not enc and token == "secret"