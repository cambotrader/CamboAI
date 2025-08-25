from dataclasses import dataclass

@dataclass
class HarmonicDetectionConfig:
    pct_zigzag: float = 0.03
    min_legs: int = 5
    min_leg_price_delta: float = 0.002
    score_threshold: float = 0.55
    volatility_window: int = 30
    volatility_filter_multiplier: float = 0.4
    max_patterns: int = 25
    dynamic_tolerance_scale: float = 0.15
    use_numba: bool = True
    cache_enabled: bool = True

DEFAULT_HARMONIC_CONFIG = HarmonicDetectionConfig()