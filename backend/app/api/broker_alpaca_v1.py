from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from app.database import get_db, BrokerAPIKey
from app.services.crypto_secrets import get_crypto
from app.services.broker_service import AlpacaBrokerService, BrokerPosition

# Soft auth resolver: prefer core, fallback to api, else no-op
try:
    from app.core.auth import get_current_user
except Exception:
    try:
        from app.api.auth import get_current_user
    except Exception:
        def get_current_user():  # type: ignore
            return None

router = APIRouter(prefix="/api/v1/broker/alpaca", tags=["Broker - Alpaca"]) 


class BrokerConfigIn(BaseModel):
    api_key: str
    api_secret: str
    base_url: str | None = None
    paper: bool = True


def _get_user_alpaca(db: Session, current_user) -> AlpacaBrokerService:
    if not current_user:
        raise HTTPException(status_code=401, detail="unauthorized")
    uid = str(getattr(current_user, "id", None) or current_user.get("id"))
    row = (
        db.query(BrokerAPIKey)
        .filter(BrokerAPIKey.user_id == uid, BrokerAPIKey.broker_name.in_(["ALPACA", "alpaca"]), BrokerAPIKey.is_active == True)
        .order_by(BrokerAPIKey.created_at.desc())
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="missing_alpaca_keys")
    crypto = get_crypto()
    api_secret, _ = crypto.decrypt(row.api_secret)
    base_url = row.base_url or ("https://paper-api.alpaca.markets" if row.is_paper_trading else "https://api.alpaca.markets")
    try:
        svc = AlpacaBrokerService(api_key=row.api_key, api_secret=api_secret or row.api_secret, base_url=base_url, paper=row.is_paper_trading)
        return svc
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"alpaca_connect_error: {e}")


@router.get("/account")
async def get_account(db: Session = Depends(get_db), current_user = Depends(get_current_user)) -> Dict[str, Any]:
    svc = _get_user_alpaca(db, current_user)
    return svc.get_account_info()


@router.get("/positions")
async def get_positions(db: Session = Depends(get_db), current_user = Depends(get_current_user)) -> List[Dict[str, Any]]:
    svc = _get_user_alpaca(db, current_user)
    rows = svc.get_positions()
    return [r.dict() for r in rows]

@router.post("/config")
async def set_config(data: BrokerConfigIn, db: Session = Depends(get_db), current_user = Depends(get_current_user)) -> Dict[str, Any]:
    if not current_user:
        raise HTTPException(status_code=401, detail="unauthorized")
    uid = str(getattr(current_user, "id", None) or current_user.get("id"))
    crypto = get_crypto()
    enc_secret, _ = crypto.encrypt(data.api_secret)
    row = BrokerAPIKey(
        user_id=uid,
        broker_name="ALPACA",
        api_key=data.api_key,
        api_secret=enc_secret,
        base_url=data.base_url,
        is_paper_trading=data.paper,
        is_active=True,
    )
    db.add(row)
    db.commit()
    return {"ok": True}