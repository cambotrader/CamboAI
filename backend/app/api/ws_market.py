import asyncio, json, time
from typing import Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from backend.app.services.external_feed import external_feed

router = APIRouter()
connections: Set[WebSocket] = set()
subscribers: Set[WebSocket] = set()

async def fetch_latest(symbol: str):
    # Placeholder: extend with real cache/DB quotes
    return {"symbol":symbol, "ts": time.time(), "price": None}

def _broadcast_tick(tick):
    for conn in list(subscribers):
        try:
            asyncio.create_task(conn.send_text(json.dumps({"type":"ext_tick","data":tick})))
        except Exception:
            pass

@router.websocket("/ws/marketdata")
async def ws_marketdata(ws: WebSocket, symbol: str = Query("AAPL"),
                        interval: int = Query(10), external: bool = Query(False)):
    await ws.accept()
    connections.add(ws)
    subscribers.add(ws)
    try:
        if external and external_feed.last_tick and external_feed.last_tick.get("symbol","").lower() == symbol.lower():
            await ws.send_text(json.dumps({"type":"ext_tick","data":external_feed.last_tick}))
        while True:
            if not external:
                data = await fetch_latest(symbol)
                if data:
                    await ws.send_text(json.dumps({"type":"tick","data":data,"t":time.time()}))
            await asyncio.sleep(interval)
    except WebSocketDisconnect:
        pass
    finally:
        connections.discard(ws)
        subscribers.discard(ws)