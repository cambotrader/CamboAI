import os, sqlite3, base64, json, time, shutil
from pathlib import Path
from typing import Optional
from cryptography.fernet import Fernet
import pyotp

DB_PATH = Path("data") / "pattern_detections.db"
KEY_PATH = Path("data") / "secret_key.bin"
KEY_PATH.parent.mkdir(parents=True, exist_ok=True)

MASTER_ENV_VAR = "CAMBOAI_MASTER_KEY"

DDL = """
CREATE TABLE IF NOT EXISTS broker_secrets (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  broker TEXT,
  key_id TEXT,
  enc_value BLOB,
  created_ts INTEGER,
  rotated_from INTEGER
);
CREATE UNIQUE INDEX IF NOT EXISTS ix_broker_key ON broker_secrets(broker,key_id);
CREATE TABLE IF NOT EXISTS broker_secrets_audit (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  broker TEXT,
  key_id TEXT,
  action TEXT,
  ts INTEGER,
  meta TEXT
);
CREATE TABLE IF NOT EXISTS security_2fa (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  label TEXT UNIQUE,
  secret TEXT,
  created_ts INTEGER
);
"""

def _init():
    with sqlite3.connect(DB_PATH) as c:
        c.executescript(DDL)

def _load_or_create_key():
    env_key = os.getenv(MASTER_ENV_VAR)
    if env_key:
        return env_key.encode()
    if not KEY_PATH.exists():
        KEY_PATH.write_bytes(Fernet.generate_key())
    return KEY_PATH.read_bytes()

def _fernet():
    return Fernet(_load_or_create_key())

def store_secret(broker: str, key_id: str, value: str):
    _init()
    f = _fernet()
    enc = f.encrypt(value.encode())
    now = int(time.time())
    with sqlite3.connect(DB_PATH) as c:
        cur = c.execute("SELECT id FROM broker_secrets WHERE broker=? AND key_id=?", (broker,key_id)).fetchone()
        rotated_from = cur[0] if cur else None
        c.execute("INSERT OR REPLACE INTO broker_secrets(broker,key_id,enc_value,created_ts,rotated_from) VALUES (?,?,?,?,?)",
                  (broker,key_id,enc,now,rotated_from))
        c.execute("INSERT INTO broker_secrets_audit(broker,key_id,action,ts,meta) VALUES (?,?,?,?,?)",
                  (broker,key_id,"SET",now,json.dumps({"rotated_from":rotated_from})))

def get_secret(broker: str, key_id: str) -> Optional[str]:
    _init()
    with sqlite3.connect(DB_PATH) as c:
        row = c.execute("SELECT enc_value FROM broker_secrets WHERE broker=? AND key_id=?", (broker,key_id)).fetchone()
    if not row: return None
    f = _fernet()
    try:
        return f.decrypt(row[0]).decode()
    except Exception:
        return None

def mask_secret(val: Optional[str]) -> Optional[str]:
    if not val: return None
    if len(val) <= 6: return "*" * len(val)
    return val[:3] + "*" * (len(val)-6) + val[-3:]

def list_broker_keys(broker: str):
    _init()
    with sqlite3.connect(DB_PATH) as c:
        rows = c.execute("SELECT key_id, created_ts FROM broker_secrets WHERE broker=?", (broker,)).fetchall()
    return [{"key_id": r[0], "created_ts": r[1]} for r in rows]

def audit_log(broker: str, limit: int = 50):
    _init()
    with sqlite3.connect(DB_PATH) as c:
        rows = c.execute("SELECT key_id, action, ts, meta FROM broker_secrets_audit WHERE broker=? ORDER BY ts DESC LIMIT ?", (broker,limit)).fetchall()
    out = []
    for k,a,t,m in rows:
        try: meta = json.loads(m) if m else {}
        except: meta = {}
        out.append({"key_id":k,"action":a,"ts":t,"meta":meta})
    return out

def rotate_master_key(backup: bool = True):
    if os.getenv(MASTER_ENV_VAR):
        raise RuntimeError("Rotation disabled with env master key.")
    old_key = KEY_PATH.read_bytes() if KEY_PATH.exists() else None
    new_key = Fernet.generate_key()
    if backup and old_key:
        shutil.copy(KEY_PATH, KEY_PATH.with_suffix(".bak"))
    _init()
    with sqlite3.connect(DB_PATH) as c:
        rows = c.execute("SELECT broker,key_id,enc_value FROM broker_secrets").fetchall()
    old_f = Fernet(old_key) if old_key else None
    new_f = Fernet(new_key)
    updated = []
    for broker,key_id,enc in rows:
        try:
            plain = old_f.decrypt(enc).decode() if old_f else ""
            updated.append((broker,key_id,new_f.encrypt(plain.encode()),int(time.time())))
        except Exception:
            pass
    KEY_PATH.write_bytes(new_key)
    with sqlite3.connect(DB_PATH) as c:
        for broker,key_id,new_enc,ts in updated:
            c.execute("UPDATE broker_secrets SET enc_value=?, created_ts=? WHERE broker=? AND key_id=?",
                      (new_enc, ts, broker, key_id))
            c.execute("INSERT INTO broker_secrets_audit(broker,key_id,action,ts,meta) VALUES (?,?,?,?,?)",
                      (broker,key_id,"ROTATE",ts,json.dumps({})))
    return len(updated)

def enable_2fa(label: str = "admin"):
    _init()
    secret = pyotp.random_base32()
    now = int(time.time())
    with sqlite3.connect(DB_PATH) as c:
        c.execute("INSERT OR REPLACE INTO security_2fa(label,secret,created_ts) VALUES (?,?,?)",
                  (label, secret, now))
    uri = pyotp.totp.TOTP(secret).provisioning_uri(name=label, issuer_name="CamboAI")
    return {"label": label, "secret": secret, "provisioning_uri": uri}

def verify_2fa(code: str, label: str = "admin") -> bool:
    _init()
    with sqlite3.connect(DB_PATH) as c:
        row = c.execute("SELECT secret FROM security_2fa WHERE label=?", (label,)).fetchone()
    if not row: return False
    return pyotp.TOTP(row[0]).verify(code, valid_window=1)

def export_audit(format_: str = "json"):
    _init()
    with sqlite3.connect(DB_PATH) as c:
        rows = c.execute("SELECT broker,key_id,action,ts,meta FROM broker_secrets_audit ORDER BY ts DESC").fetchall()
    data = [{"broker":r[0],"key_id":r[1],"action":r[2],"ts":r[3],"meta":r[4]} for r in rows]
    if format_ == "csv" and data:
        import csv, io
        buf = io.StringIO()
        w = csv.DictWriter(buf, fieldnames=data[0].keys())
        w.writeheader(); w.writerows(data)
        return {"format":"csv","data":buf.getvalue()}
    return {"format":"json","data":data}