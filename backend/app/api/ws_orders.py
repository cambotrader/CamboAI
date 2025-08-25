from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
import asyncio, json, time, hashlib
from typing import Set
from modules.orders.orders_store import list_orders

router = APIRouter()
clients: Set[WebSocket] = set()
_last_sent_hash = None

@router.websocket("/ws/orders")
async def ws_orders(ws: WebSocket, interval: int = Query(5)):
    await ws.accept()
    clients.add(ws)
    try:
        while True:
            data = list_orders(limit=25)
            await ws.send_text(json.dumps({"type":"orders","ts":time.time(),"orders":data}))
            await asyncio.sleep(interval)
    except WebSocketDisconnect:
        pass
    finally:
        clients.discard(ws)

async def _broadcast_loop():
    global _last_sent_hash
    while True:
        if clients:
            data = list_orders(limit=50)
            payload = {"type":"orders","orders":data}
            phash = hashlib.sha256(json.dumps(payload,default=str).encode()).hexdigest()
            if phash != _last_sent_hash:
                _last_sent_hash = phash
                msg = json.dumps(payload)
                for c in list(clients):
                    try:
                        await c.send_text(msg)
                    except Exception:
                        pass
        await asyncio.sleep(2)