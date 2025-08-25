from .base import BrokerAdapter, registry

class IBKRAdapter(BrokerAdapter):
    name="ibkr"
    def __init__(self):
        self.gateway_host="127.0.0.1"
        self.gateway_port=4001
    def configure(self, **kwargs):
        self.gateway_host=kwargs.get("host",self.gateway_host)
        self.gateway_port=kwargs.get("port",self.gateway_port)
    def account_info(self):
        return {"broker":"ibkr","status":"stub","host":self.gateway_host}
    def place_order(self, symbol: str, qty: float, side: str, order_type: str="market"):
        return {"ok":True,"note":"ibkr stub"}

registry.register(IBKRAdapter())