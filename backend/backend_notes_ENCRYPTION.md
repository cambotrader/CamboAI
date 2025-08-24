# Secrets encryption

- Uses `cryptography.Fernet` with key from env `SECRET_ENC_KEY` (base64 URL-safe 32-byte key).
- If key missing or library unavailable, encryption is disabled and values are stored as-is (development fallback).
- API never returns `api_secret` values.

## Generate a key

```python
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
```

Set it:

```bash
set SECRET_ENC_KEY=PASTE_KEY_HERE
```