from .base import BrokerAdapter, registry
from modules.security.secrets_manager import store_secret, get_secret

class TradierAdapter(BrokerAdapter):
    name="tradier"
    def __init__(self):
        pass
    def configure(self, **kwargs):
        if kwargs.get("token"):
            store_secret("tradier","TOKEN", kwargs["token"])
    def account_info(self):
        tok = get_secret("tradier","TOKEN")
        return {"broker":"tradier","status":"stub","options_supported":True,"configured": bool(tok)}
    def place_order(self, symbol: str, qty: float, side: str, order_type: str="market"):
        return {"ok":True,"note":"tradier stub"}

registry.register(TradierAdapter())