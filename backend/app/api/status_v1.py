from __future__ import annotations
from fastapi import APIRouter
from typing import Dict, Any
import time

router = APIRouter(prefix="/api/v1", tags=["Status"]) 

@router.get("/status")
async def status() -> Dict[str, Any]:
    return {
        "name": "CamboAI Trading Platform",
        "version": "1.0.0",
        "uptime_hint": time.time(),
        "services": {
            "api": "online",
            "signals": "online",
        }
    }