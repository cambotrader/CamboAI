from abc import ABC, abstractmethod

class BrokerAdapter(ABC):
    name: str = "base"

    @abstractmethod
    def configure(self, **kwargs): ...
    @abstractmethod
    def account_info(self): ...
    @abstractmethod
    def place_order(self, symbol: str, qty: float, side: str, order_type: str = "market"): ...

class BrokerRegistry:
    def __init__(self):
        self._adapters = {}
    def register(self, adapter: BrokerAdapter):
        self._adapters[adapter.name] = adapter
    def get(self, name: str):
        return self._adapters.get(name)
    def names(self):
        return list(self._adapters.keys())

registry = BrokerRegistry()