from fastapi import APIRouter
from pydantic import BaseModel
from modules.brokers.base import registry
from modules.orders.orders_store import (
    save_order, list_orders, update_order_status
)

router = APIRouter(prefix="/orders", tags=["orders"])

class OrderIn(BaseModel):
    broker: str
    symbol: str
    side: str
    qty: float
    order_type: str = "market"

@router.post("/place")
def place_order(payload: OrderIn):
    adapter = registry.get(payload.broker)
    if not adapter:
        return {"error":"unknown broker"}
    resp = adapter.place_order(payload.symbol, payload.qty, payload.side, payload.order_type)
    if resp.get("ok"):
        save_order(resp.get("id","tmp_"+payload.symbol), payload.broker,
                   payload.symbol, payload.side, payload.qty,
                   payload.order_type, resp.get("status","new"), resp)
    return resp

@router.get("/list")
def orders_list(limit: int = 50):
    return {"orders": list_orders(limit)}

@router.get("/status/{broker}/{order_id}")
def order_status(broker: str, order_id: str):
    adapter = registry.get(broker)
    if not adapter or not hasattr(adapter,"get_order"):
        return {"error":"unsupported"}
    resp = adapter.get_order(order_id)
    if "status" in resp:
        update_order_status(order_id, resp["status"], resp)
    return resp

@router.post("/cancel")
def cancel_order(broker: str, order_id: str):
    adapter = registry.get(broker)
    if not adapter or not hasattr(adapter,"cancel_order"):
        return {"error":"unsupported"}
    resp = adapter.cancel_order(order_id)
    if resp.get("ok"):
        update_order_status(order_id, "canceled", resp)
    return resp