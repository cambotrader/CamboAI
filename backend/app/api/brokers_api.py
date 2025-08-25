from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from modules.brokers.base import registry
from modules.security.secrets_manager import (
    store_secret, rotate_master_key, mask_secret,
    get_secret, enable_2fa, verify_2fa, export_audit
)

router = APIRouter(prefix="/brokers", tags=["brokers"])

class BrokerConfig(BaseModel):
    broker: str
    key: str | None = None
    secret: str | None = None
    token: str | None = None
    host: str | None = None
    port: int | None = None
    paper: bool | None = None

def _require_2fa(code: str | None):
    if not verify_2fa(code or "", "admin"):
        raise HTTPException(status_code=403, detail="2FA verification failed")

@router.get("/list")
def list_brokers():
    return {"brokers": registry.names()}

@router.post("/configure")
def configure_broker(payload: BrokerConfig):
    adapter = registry.get(payload.broker)
    if not adapter:
        return {"error": "unknown broker"}
    adapter.configure(**payload.dict())
    return {"status": "configured", "broker": payload.broker}

@router.get("/account/{broker}")
def account_info(broker: str):
    adapter = registry.get(broker)
    if not adapter:
        return {"error":"unknown broker"}
    return adapter.account_info()

# 2FA
@router.post("/secrets/2fa/enable")
def secrets_2fa_enable(label: str = "admin"):
    return enable_2fa(label)

@router.get("/secrets/2fa/verify")
def secrets_2fa_verify(code: str, label: str = "admin"):
    return {"ok": verify_2fa(code,label)}

# Secrets (2FA enforced)
@router.post("/secrets/set")
def set_secret(broker: str, key_id: str, value: str, code: str | None = None):
    _require_2fa(code)
    store_secret(broker,key_id,value)
    return {"status":"stored","broker":broker,"key_id":key_id}

@router.post("/secrets/rotate_master")
def rotate_master(code: str | None = None):
    _require_2fa(code)
    count = rotate_master_key()
    return {"status":"rotated","re_encrypted":count}

@router.get("/secrets/list/{broker}")
def list_secrets(broker: str):
    from modules.security import secrets_manager
    keys = secrets_manager.list_broker_keys(broker)
    masked = []
    for k in keys:
        v = secrets_manager.get_secret(broker,k["key_id"])
        masked.append({"key_id":k["key_id"],"created_ts":k["created_ts"],"value":mask_secret(v)})
    return {"broker":broker,"secrets":masked}

@router.get("/secrets/masked")
def get_masked(broker: str, key_id: str):
    val = get_secret(broker,key_id)
    return {"broker":broker,"key_id":key_id,"value":mask_secret(val)}

@router.get("/secrets/audit/{broker}")
def audit(broker: str, limit: int = 50):
    from modules.security import secrets_manager
    return {"broker":broker,"audit":secrets_manager.audit_log(broker, limit=limit)}

@router.get("/secrets/audit/export")
def secrets_audit_export(format: str = "json", code: str | None = None, label: str = "admin"):
    _require_2fa(code)
    return export_audit(format)