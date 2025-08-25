"""Universal Scanner Framework (MVP)

Each source emits ScanFinding items. Scanner aggregates & scores.
"""
from __future__ import annotations

from typing import List, Protocol, Dict, Any
from modules.models import ScanFinding


class ScannerSource(Protocol):  # structural typing
    name: str
    weight: float
    def scan(self, symbol: str, context: Dict[str, Any]) -> List[ScanFinding]: ...  # noqa: D401,E701


class SimplePriceMomentumSource:
    name = "price_momentum"
    weight = 1.0
    def scan(self, symbol: str, context: Dict[str, Any]) -> List[ScanFinding]:
        df = context.get("data")
        if df is None or len(df) < 10:
            return []
        close = df["Close"] if "Close" in df.columns else df.iloc[:, 0]
        ret = (close.iloc[-1] / close.iloc[-10]) - 1
        if ret > 0.05:
            return [ScanFinding(symbol=symbol, category="momentum", description=f"10-bar momentum +{ret:.1%}", weight=self.weight, meta={"return_10": ret})]
        return []


class BasicVolSpikeSource:
    name = "volume_spike"
    weight = 1.0
    def scan(self, symbol: str, context: Dict[str, Any]) -> List[ScanFinding]:
        df = context.get("data")
        if df is None or "Volume" not in df.columns or len(df) < 30:
            return []
        vol = df["Volume"]
        avg = vol.iloc[-30:-1].mean()
        latest = vol.iloc[-1]
        if avg and latest > 2.5 * avg:
            return [ScanFinding(symbol=symbol, category="volume", description="Volume spike >2.5x 30-bar avg", weight=self.weight, meta={"latest": int(latest), "avg": float(avg)})]
        return []


class Scanner:
    def __init__(self, sources: List[ScannerSource]):
        self.sources = sources

    def run(self, symbol: str, context: Dict[str, Any]) -> List[ScanFinding]:
        findings: List[ScanFinding] = []
        for src in self.sources:
            try:
                findings.extend(src.scan(symbol, context))
            except Exception as e:  # noqa: BLE001
                findings.append(ScanFinding(symbol=symbol, category="error", description=f"{src.name} failed: {e}", weight=0.0))
        return findings


def default_scanner() -> Scanner:
    return Scanner(sources=[SimplePriceMomentumSource(), BasicVolSpikeSource()])


__all__ = ["Scanner", "default_scanner", "ScannerSource"]
