import asyncio
from modules.orders.orders_store import open_order_ids, update_order_status
from modules.brokers.base import registry

class OrdersPoller:
    def __init__(self, interval: int = 10):
        self.interval = interval
        self.running = False
    async def start(self):
        self.running = True
        while self.running:
            await self._poll_once()
            await asyncio.sleep(self.interval)
    async def _poll_once(self):
        ids = open_order_ids()
        for oid, broker in ids:
            adapter = registry.get(broker)
            if not adapter or not hasattr(adapter, "get_order"):
                continue
            try:
                resp = adapter.get_order(oid)
                if resp and "status" in resp:
                    update_order_status(oid, resp["status"], resp)
            except Exception:
                pass
    def stop(self):
        self.running = False

orders_poller = OrdersPoller()