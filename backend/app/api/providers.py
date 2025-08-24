from __future__ import annotations
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db, BrokerAPIKey
from app.models.trading_models import User as AuthUser, Account
from app.services.market_data_providers import get_market_data_router
# Soft auth resolver: prefer core, fallback to api, else no-op
try:
    from app.core.auth import get_current_user
except Exception:
    try:
        from app.api.auth import get_current_user
    except Exception:
        def get_current_user():
            return None
from app.services.user_preferences import UserPreferences, set_user_preferences, get_user_preferences
from app.services.crypto_secrets import get_crypto
from typing import Any, Optional, List

router = APIRouter(prefix="/api/v1/providers", tags=["Providers"]) 

class ProviderPreference(BaseModel):
    preferred_market_data: str  # "polygon" | "yahoo"

class BrokerKeyIn(BaseModel):
    broker_name: str  # e.g., ALPACA
    api_key: str
    api_secret: str
    base_url: str | None = None
    paper: bool = True

@router.post("/market-data/preferred")
async def set_preferred_provider(pref: ProviderPreference, db: Session = Depends(get_db), current_user: AuthUser | dict | None = Depends(get_current_user)):
    if not current_user:
        return {"ok": False, "error": "unauthorized"}
    # normalize user id
    uid = str(getattr(current_user, "id", None) or current_user.get("id"))
    set_user_preferences(db, current_user, UserPreferences(preferred_market_data=pref.preferred_market_data))
    get_market_data_router().set_preferred(pref.preferred_market_data)
    return {"ok": True, "preferred": pref.preferred_market_data}

@router.get("/market-data/preferred")
async def get_preferred_provider(db: Session = Depends(get_db)):
    # Public GET: no auth required
    try:
        # If later we support per-user prefs via API key, wire here; for now, return None
        return {"preferred": None}
    except Exception:
        return {"preferred": None}

@router.post("/broker/keys")
async def add_broker_key(data: BrokerKeyIn, db: Session = Depends(get_db), current_user: AuthUser | dict | None = Depends(get_current_user)):
    if not current_user:
        return {"ok": False, "error": "unauthorized"}
    uid = str(getattr(current_user, "id", None) or current_user.get("id"))
    # Encrypt secret if crypto is enabled
    crypto = get_crypto()
    enc_secret, _ = crypto.encrypt(data.api_secret)
    rec = BrokerAPIKey(
        user_id=uid,
        broker_name=data.broker_name,
        api_key=data.api_key,
        api_secret=enc_secret,
        base_url=data.base_url,
        is_paper_trading=data.paper,
        is_active=True,
    )
    db.add(rec)
    db.commit()
    return {"ok": True, "broker": data.broker_name}

@router.get("/broker/keys")
async def list_broker_keys(db: Session = Depends(get_db), current_user: AuthUser | dict | None = Depends(get_current_user)):
    if not current_user:
        return {"ok": False, "error": "unauthorized"}
    uid = str(getattr(current_user, "id", None) or current_user.get("id"))
    rows = db.query(BrokerAPIKey).filter(BrokerAPIKey.user_id == uid, BrokerAPIKey.is_active == True).all()
    return [{"id": str(r.id), "broker_name": r.broker_name, "paper": r.is_paper_trading, "base_url": r.base_url} for r in rows]

@router.delete("/broker/keys/{key_id}")
async def delete_broker_key(key_id: str, db: Session = Depends(get_db), current_user: AuthUser | dict | None = Depends(get_current_user)):
    if not current_user:
        return {"ok": False, "error": "unauthorized"}
    uid = str(getattr(current_user, "id", None) or current_user.get("id"))
    row = db.query(BrokerAPIKey).filter(BrokerAPIKey.user_id == uid, BrokerAPIKey.id == key_id).first()
    if not row:
        return {"ok": False, "error": "not_found"}
    db.delete(row)
    db.commit()
    return {"ok": True}