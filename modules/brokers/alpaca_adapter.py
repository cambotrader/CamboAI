from .base import BrokerAdapter, registry
import requests
from modules.security.secrets_manager import store_secret, get_secret

class AlpacaAdapter(BrokerAdapter):
    name = "alpaca"
    def __init__(self):
        self.paper = True
        self.base_url = "https://paper-api.alpaca.markets"
    def configure(self, **kwargs):
        if kwargs.get("key"):
            store_secret("alpaca","API_KEY",kwargs["key"])
        if kwargs.get("secret"):
            store_secret("alpaca","API_SECRET",kwargs["secret"])
        self.paper = kwargs.get("paper", True)
    def _auth_headers(self):
        k = get_secret("alpaca","API_KEY")
        s = get_secret("alpaca","API_SECRET")
        if not k or not s: return {}
        return {"APCA-API-KEY-ID":k,"APCA-API-SECRET-KEY":s}
    def account_info(self):
        try:
            r = requests.get(f"{self.base_url}/v2/account", headers=self._auth_headers(), timeout=10)
            if r.status_code==200:
                data = r.json()
                return {"broker":"alpaca","status":"ok","cash":data.get("cash"),"equity":data.get("equity")}
            return {"broker":"alpaca","status":"error","code":r.status_code}
        except Exception as e:
            return {"broker":"alpaca","status":"error","error":str(e)}
    def place_order(self, symbol: str, qty: float, side: str, order_type: str="market"):
        payload = {"symbol":symbol,"qty":qty,"side":side.lower(),"type":order_type,"time_in_force":"day"}
        try:
            r = requests.post(f"{self.base_url}/v2/orders", json=payload, headers=self._auth_headers(), timeout=10)
            if r.status_code in (200,201):
                j = r.json()
                return {"ok":True,"id":j.get("id"),"status":j.get("status")}
            return {"ok":False,"code":r.status_code,"text":r.text}
        except Exception as e:
            return {"ok":False,"error":str(e)}
    def get_order(self, order_id: str):
        try:
            r = requests.get(f"{self.base_url}/v2/orders/{order_id}", headers=self._auth_headers(), timeout=10)
            return r.json() if r.status_code==200 else {"error":r.text,"code":r.status_code}
        except Exception as e:
            return {"error":str(e)}
    def cancel_order(self, order_id: str):
        try:
            r = requests.delete(f"{self.base_url}/v2/orders/{order_id}", headers=self._auth_headers(), timeout=10)
            if r.status_code in (200,204):
                return {"ok":True,"id":order_id}
            return {"ok":False,"code":r.status_code,"text":r.text}
        except Exception as e:
            return {"ok":False,"error":str(e)}

registry.register(AlpacaAdapter())