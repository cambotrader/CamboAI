from __future__ import annotations
from typing import Optional, Dict, Any
from pydantic import BaseModel
from sqlalchemy.orm import Session

try:
    from app.models.trading_models import User as TradingUser
except Exception:
    # Fallback to simple User model (app.database) if trading_models not used
    from app.database import User as TradingUser

class UserPreferences(BaseModel):
    preferred_market_data: Optional[str] = None  # "polygon" | "yahoo"


def _ensure_ui_prefs(u: TradingUser, db: Session) -> Dict[str, Any]:
    # Attempt to read from user_profiles first if available in app.database
    try:
        from app.database import UserProfile
        prof = db.query(UserProfile).filter(UserProfile.user_id == str(u.id)).first()
        if prof and prof.ui_preferences:
            return dict(prof.ui_preferences)
    except Exception:
        pass
    # Fallback to attribute on TradingUser (trading_models)
    return dict(getattr(u, 'ui_preferences', {}) or {})


def get_user_preferences(db: Session, user: TradingUser) -> UserPreferences:
    # Reload to ensure we operate on ORM instance
    u = db.query(TradingUser).filter(TradingUser.id == user.id).first()
    if not u:
        return UserPreferences()
    ui = _ensure_ui_prefs(u, db)
    md = None
    md_cfg = ui.get("market_data") if isinstance(ui.get("market_data"), dict) else None
    if md_cfg:
        md = md_cfg.get("preferred_provider")
    return UserPreferences(preferred_market_data=md)


def set_user_preferences(db: Session, user: TradingUser, prefs: UserPreferences) -> UserPreferences:
    u = db.query(TradingUser).filter(TradingUser.id == user.id).first()
    if not u:
        return prefs
    ui = _ensure_ui_prefs(u, db)
    md_cfg = ui.get("market_data") if isinstance(ui.get("market_data"), dict) else {}
    if prefs.preferred_market_data:
        md_cfg["preferred_provider"] = prefs.preferred_market_data
    ui["market_data"] = md_cfg
    # Try to persist in user_profiles if available; otherwise fallback to attribute on TradingUser
    try:
        from app.database import UserProfile
        prof = db.query(UserProfile).filter(UserProfile.user_id == str(u.id)).first()
        if not prof:
            prof = UserProfile(user_id=str(u.id), ui_preferences=ui)
            db.add(prof)
        else:
            prof.ui_preferences = ui
        db.commit()
    except Exception:
        u.ui_preferences = ui
        db.add(u)
        db.commit()
        db.refresh(u)
    return prefs