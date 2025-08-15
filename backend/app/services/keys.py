from __future__ import annotations
from typing import Dict, Any, Optional
import json
import os
from pathlib import Path

SECRETS_DIR = Path(__file__).resolve().parents[2] / "secrets"
SECRETS_DIR.mkdir(parents=True, exist_ok=True)
SECRETS_FILE = SECRETS_DIR / "api_keys.json"

DEFAULT_SCHEMA: Dict[str, Any] = {
    "twitter": {"key": None},
    "youtube": {"key": None},
    "reddit": {"client_id": None, "client_secret": None},
    "finnhub": {"key": None},
    "benzinga": {"key": None},
    "newsapi": {"key": None},
    "telegram": {"bot_token": None},
    "discord": {"bot_token": None},
}


def _load_raw() -> Dict[str, Any]:
    if not SECRETS_FILE.exists():
        return DEFAULT_SCHEMA.copy()
    try:
        return json.loads(SECRETS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return DEFAULT_SCHEMA.copy()


def _save_raw(data: Dict[str, Any]) -> None:
    SECRETS_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def get_all() -> Dict[str, Any]:
    data = _load_raw()
    # merge with default schema to ensure keys exist
    merged = DEFAULT_SCHEMA.copy()
    for k, v in data.items():
        if isinstance(v, dict) and k in merged:
            merged[k].update(v)
        else:
            merged[k] = v
    return merged


def set_key(provider: str, values: Dict[str, Any]) -> Dict[str, Any]:
    data = get_all()
    if provider not in data:
        data[provider] = {}
    if not isinstance(data[provider], dict):
        data[provider] = {}
    data[provider].update(values)
    _save_raw(data)
    return data[provider]


def status() -> Dict[str, Any]:
    data = get_all()
    # return redacted status booleans so UI can show which are configured
    out = {}
    for provider, conf in data.items():
        if isinstance(conf, dict):
            out[provider] = any(bool(v) for v in conf.values())
        else:
            out[provider] = bool(conf)
    return out