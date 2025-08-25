"""Core datamodels (lightweight) used across strategy, scanner, sentiment, and pattern systems.

These are intentionally simple dataclasses to avoid heavy dependencies. They can be
upgraded to Pydantic models later if API serialization / validation becomes critical.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List, Optional
import uuid


def _id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:10]}"


@dataclass
class StrategySignal:
    symbol: str
    direction: str  # 'long' | 'short' | 'flat'
    confidence: float  # 0..1
    source: str  # strategy name
    timestamp: datetime = field(default_factory=datetime.utcnow)
    tags: List[str] = field(default_factory=list)
    meta: Dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: _id("sig"))


@dataclass
class PatternDetection:
    pattern_type: str
    direction: Optional[str]
    confidence: float
    symbol: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    meta: Dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: _id("pat"))


@dataclass
class SentimentSnapshot:
    symbol: str
    provider: str
    scores: Dict[str, float]
    label: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    raw: Any | None = None
    id: str = field(default_factory=lambda: _id("sent"))


@dataclass
class ScanFinding:
    symbol: str
    category: str
    description: str
    weight: float
    meta: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    id: str = field(default_factory=lambda: _id("scan"))


__all__ = [
    "StrategySignal",
    "PatternDetection",
    "SentimentSnapshot",
    "ScanFinding",
]
