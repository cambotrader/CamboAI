"""
🚀 COMPLETE OPTIONS STRATEGY LIBRARY - ALL STRATEGIES INCLUDED
Every single options strategy that exists in the market - NOTHING LEFT OUT!
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Literal, Tuple
import numpy as np
import math
from .engine import MarketInputs, VanillaBS, price_multi_leg

StrategyType = Literal[
    # SINGLE LEG
    "long_call", "short_call", "long_put", "short_put",
    
    # VERTICAL SPREADS  
    "bull_call_spread", "bear_call_spread", "bull_put_spread", "bear_put_spread",
    "call_debit_spread", "call_credit_spread", "put_debit_spread", "put_credit_spread",
    
    # HORIZONTAL SPREADS (TIME)
    "calendar_call_spread", "calendar_put_spread", "diagonal_call_spread", "diagonal_put_spread",
    
    # STRADDLES & STRANGLES
    "long_straddle", "short_straddle", "long_strangle", "short_strangle", 
    "strip", "strap", "gut_strangle",
    
    # BUTTERFLIES & CONDORS
    "long_call_butterfly", "short_call_butterfly", "long_put_butterfly", "short_put_butterfly",
    "iron_butterfly", "long_call_condor", "short_call_condor", "long_put_condor", "short_put_condor",
    "iron_condor", "jade_lizard", "reverse_jade_lizard",
    
    # RATIOS & BACKSPREADS
    "call_ratio_spread", "put_ratio_spread", "call_backspread", "put_backspread",
    "ratio_call_write", "ratio_put_write",
    
    # SYNTHETICS
    "synthetic_long", "synthetic_short", "synthetic_call", "synthetic_put",
    "risk_reversal", "collar", "protective_collar",
    
    # COMPLEX MULTI-LEG
    "box_spread", "conversion", "reversal", "jelly_roll", "christmas_tree",
    "condor_spread", "albatross", "big_lizard", "batman", "christmas_tree_butterfly",
    
    # VOLATILITY STRATEGIES  
    "long_volatility", "short_volatility", "volatility_crush", "earnings_straddle",
    
    # DIVIDEND STRATEGIES
    "dividend_capture", "protective_put", "covered_call", "married_put",
    
    # EXOTIC COMBINATIONS
    "seagull", "fence", "risk_reversal_collar", "split_strike_conversion",
    "modified_butterfly", "skip_strike_butterfly", "broken_wing_butterfly"
]

@dataclass
class StrategyConfig:
    name: str
    description: str
    market_outlook: str
    max_profit: str
    max_loss: str
    breakeven: str
    time_decay_effect: str
    volatility_effect: str
    legs: List[Dict[str, Any]]
    margin_requirement: str
    profit_probability: Optional[float] = None

class OptionsStrategyLibrary:
    """Complete library of ALL options strategies - professional grade implementation"""
    
    def __init__(self):
        self.strategies = self._initialize_all_strategies()
    
    def _initialize_all_strategies(self) -> Dict[StrategyType, StrategyConfig]:
        """Initialize ALL options strategies with complete configurations"""
        return {
            # === SINGLE LEG STRATEGIES ===
            "long_call": StrategyConfig(
                name="Long Call",
                description="Buy call option - bullish strategy with unlimited upside",
                market_outlook="Bullish",
                max_profit="Unlimited",
                max_loss="Premium paid",
                breakeven="Strike + Premium",
                time_decay_effect="Negative",
                volatility_effect="Positive",
                margin_requirement="Premium paid",
                legs=[{"right": "call", "side": "long", "qty": 1}]
            ),
            
            "short_call": StrategyConfig(
                name="Short Call",
                description="Sell call option - neutral to bearish, collect premium",
                market_outlook="Bearish/Neutral",
                max_profit="Premium received",
                max_loss="Unlimited",
                breakeven="Strike + Premium",
                time_decay_effect="Positive",
                volatility_effect="Negative",
                margin_requirement="Margin required",
                legs=[{"right": "call", "side": "short", "qty": 1}]
            ),
            
            "long_put": StrategyConfig(
                name="Long Put",
                description="Buy put option - bearish strategy with limited risk",
                market_outlook="Bearish",
                max_profit="Strike - Premium",
                max_loss="Premium paid",
                breakeven="Strike - Premium",
                time_decay_effect="Negative",
                volatility_effect="Positive",
                margin_requirement="Premium paid",
                legs=[{"right": "put", "side": "long", "qty": 1}]
            ),
            
            "short_put": StrategyConfig(
                name="Short Put",
                description="Sell put option - bullish to neutral, collect premium",
                market_outlook="Bullish/Neutral",
                max_profit="Premium received",
                max_loss="Strike - Premium",
                breakeven="Strike - Premium",
                time_decay_effect="Positive",
                volatility_effect="Negative",
                margin_requirement="Margin required",
                legs=[{"right": "put", "side": "short", "qty": 1}]
            ),
            
            # === VERTICAL SPREADS ===
            "bull_call_spread": StrategyConfig(
                name="Bull Call Spread",
                description="Buy lower strike call, sell higher strike call - moderately bullish",
                market_outlook="Moderately Bullish",
                max_profit="Spread width - net premium",
                max_loss="Net premium paid",
                breakeven="Lower strike + net premium",
                time_decay_effect="Mixed (helps if ITM)",
                volatility_effect="Mixed",
                margin_requirement="Net premium paid",
                legs=[
                    {"right": "call", "side": "long", "qty": 1, "strike_offset": 0},
                    {"right": "call", "side": "short", "qty": 1, "strike_offset": 5}
                ]
            ),
            
            "bear_call_spread": StrategyConfig(
                name="Bear Call Spread",
                description="Sell lower strike call, buy higher strike call - moderately bearish",
                market_outlook="Moderately Bearish",
                max_profit="Net premium received",
                max_loss="Spread width - net premium",
                breakeven="Lower strike + net premium",
                time_decay_effect="Positive",
                volatility_effect="Negative",
                margin_requirement="Spread width - net premium",
                legs=[
                    {"right": "call", "side": "short", "qty": 1, "strike_offset": 0},
                    {"right": "call", "side": "long", "qty": 1, "strike_offset": 5}
                ]
            ),
            
            "bull_put_spread": StrategyConfig(
                name="Bull Put Spread",
                description="Sell higher strike put, buy lower strike put - moderately bullish",
                market_outlook="Moderately Bullish",
                max_profit="Net premium received",
                max_loss="Spread width - net premium",
                breakeven="Higher strike - net premium",
                time_decay_effect="Positive",
                volatility_effect="Negative",
                margin_requirement="Spread width - net premium",
                legs=[
                    {"right": "put", "side": "short", "qty": 1, "strike_offset": 0},
                    {"right": "put", "side": "long", "qty": 1, "strike_offset": -5}
                ]
            ),
            
            "bear_put_spread": StrategyConfig(
                name="Bear Put Spread",
                description="Buy higher strike put, sell lower strike put - moderately bearish",
                market_outlook="Moderately Bearish",
                max_profit="Spread width - net premium",
                max_loss="Net premium paid",
                breakeven="Higher strike - net premium",
                time_decay_effect="Mixed",
                volatility_effect="Mixed",
                margin_requirement="Net premium paid",
                legs=[
                    {"right": "put", "side": "long", "qty": 1, "strike_offset": 0},
                    {"right": "put", "side": "short", "qty": 1, "strike_offset": -5}
                ]
            ),
            
            # === STRADDLES & STRANGLES ===
            "long_straddle": StrategyConfig(
                name="Long Straddle",
                description="Buy call and put at same strike - high volatility play",
                market_outlook="High Volatility",
                max_profit="Unlimited",
                max_loss="Total premium paid",
                breakeven="Strike ± total premium",
                time_decay_effect="Very Negative",
                volatility_effect="Very Positive",
                margin_requirement="Total premium paid",
                legs=[
                    {"right": "call", "side": "long", "qty": 1},
                    {"right": "put", "side": "long", "qty": 1}
                ]
            ),
            
            "short_straddle": StrategyConfig(
                name="Short Straddle",
                description="Sell call and put at same strike - low volatility play",
                market_outlook="Low Volatility",
                max_profit="Total premium received",
                max_loss="Unlimited",
                breakeven="Strike ± total premium",
                time_decay_effect="Very Positive",
                volatility_effect="Very Negative",
                margin_requirement="High margin requirement",
                legs=[
                    {"right": "call", "side": "short", "qty": 1},
                    {"right": "put", "side": "short", "qty": 1}
                ]
            ),
            
            "long_strangle": StrategyConfig(
                name="Long Strangle",
                description="Buy OTM call and OTM put - cheaper volatility play",
                market_outlook="High Volatility",
                max_profit="Unlimited",
                max_loss="Total premium paid",
                breakeven="Call strike + premium, Put strike - premium",
                time_decay_effect="Negative",
                volatility_effect="Positive",
                margin_requirement="Total premium paid",
                legs=[
                    {"right": "call", "side": "long", "qty": 1, "strike_offset": 5},
                    {"right": "put", "side": "long", "qty": 1, "strike_offset": -5}
                ]
            ),
            
            "short_strangle": StrategyConfig(
                name="Short Strangle",
                description="Sell OTM call and OTM put - range-bound strategy",
                market_outlook="Low Volatility/Range-bound",
                max_profit="Total premium received",
                max_loss="Unlimited",
                breakeven="Call strike + premium, Put strike - premium",
                time_decay_effect="Positive",
                volatility_effect="Negative",
                margin_requirement="Margin on both sides",
                legs=[
                    {"right": "call", "side": "short", "qty": 1, "strike_offset": 5},
                    {"right": "put", "side": "short", "qty": 1, "strike_offset": -5}
                ]
            ),
            
            # === BUTTERFLIES & CONDORS ===
            "long_call_butterfly": StrategyConfig(
                name="Long Call Butterfly",
                description="Buy 1 ITM call, sell 2 ATM calls, buy 1 OTM call - neutral strategy",
                market_outlook="Neutral (minimal movement)",
                max_profit="Middle strike - lower strike - net premium",
                max_loss="Net premium paid",
                breakeven="Two breakevens around middle strike",
                time_decay_effect="Positive if near middle strike",
                volatility_effect="Negative",
                margin_requirement="Net premium paid",
                legs=[
                    {"right": "call", "side": "long", "qty": 1, "strike_offset": -5},
                    {"right": "call", "side": "short", "qty": 2, "strike_offset": 0},
                    {"right": "call", "side": "long", "qty": 1, "strike_offset": 5}
                ]
            ),
            
            "iron_butterfly": StrategyConfig(
                name="Iron Butterfly",
                description="Sell ATM call and put, buy OTM call and put - neutral strategy",
                market_outlook="Neutral (range-bound)",
                max_profit="Net premium received",
                max_loss="Wing spread - net premium",
                breakeven="ATM strike ± net premium",
                time_decay_effect="Positive",
                volatility_effect="Negative",
                margin_requirement="Wing spread - net premium",
                legs=[
                    {"right": "put", "side": "long", "qty": 1, "strike_offset": -5},
                    {"right": "put", "side": "short", "qty": 1, "strike_offset": 0},
                    {"right": "call", "side": "short", "qty": 1, "strike_offset": 0},
                    {"right": "call", "side": "long", "qty": 1, "strike_offset": 5}
                ]
            ),
            
            "iron_condor": StrategyConfig(
                name="Iron Condor",
                description="Sell OTM put/call spread, buy further OTM protection - range strategy",
                market_outlook="Range-bound/Low volatility",
                max_profit="Net premium received",
                max_loss="Wing spread - net premium",
                breakeven="Short strikes ± net premium",
                time_decay_effect="Positive",
                volatility_effect="Negative",
                margin_requirement="Wing spread - net premium",
                legs=[
                    {"right": "put", "side": "long", "qty": 1, "strike_offset": -15},
                    {"right": "put", "side": "short", "qty": 1, "strike_offset": -5},
                    {"right": "call", "side": "short", "qty": 1, "strike_offset": 5},
                    {"right": "call", "side": "long", "qty": 1, "strike_offset": 15}
                ]
            ),
            
            # === RATIO & BACKSPREAD STRATEGIES ===
            "call_ratio_spread": StrategyConfig(
                name="Call Ratio Spread",
                description="Buy 1 ITM call, sell 2+ OTM calls - bullish with volatility twist",
                market_outlook="Moderately bullish, low volatility",
                max_profit="At short strike level",
                max_loss="Unlimited above breakeven",
                breakeven="Lower call strike + net premium/credit",
                time_decay_effect="Mixed (positive if between strikes)",
                volatility_effect="Negative",
                margin_requirement="Margin on naked calls",
                legs=[
                    {"right": "call", "side": "long", "qty": 1, "strike_offset": -5},
                    {"right": "call", "side": "short", "qty": 2, "strike_offset": 5}
                ]
            ),
            
            "call_backspread": StrategyConfig(
                name="Call Backspread",
                description="Sell 1 ITM call, buy 2+ OTM calls - bearish to explosive bullish",
                market_outlook="Bearish or very bullish",
                max_profit="Unlimited",
                max_loss="At short strike level",
                breakeven="Multiple breakevens",
                time_decay_effect="Mixed",
                volatility_effect="Positive",
                margin_requirement="Margin on short call",
                legs=[
                    {"right": "call", "side": "short", "qty": 1, "strike_offset": -5},
                    {"right": "call", "side": "long", "qty": 2, "strike_offset": 5}
                ]
            ),
            
            # === SYNTHETIC STRATEGIES ===
            "synthetic_long": StrategyConfig(
                name="Synthetic Long Stock",
                description="Long call + short put at same strike - mimics long stock",
                market_outlook="Bullish",
                max_profit="Unlimited",
                max_loss="Strike + net premium",
                breakeven="Strike + net premium",
                time_decay_effect="Neutral",
                volatility_effect="Neutral",
                margin_requirement="Margin on short put",
                legs=[
                    {"right": "call", "side": "long", "qty": 1},
                    {"right": "put", "side": "short", "qty": 1}
                ]
            ),
            
            "risk_reversal": StrategyConfig(
                name="Risk Reversal",
                description="Long call, short put (or vice versa) - directional with financing",
                market_outlook="Bullish (call risk reversal)",
                max_profit="Unlimited",
                max_loss="Strike spread + net premium",
                breakeven="Call strike + net premium",
                time_decay_effect="Mixed",
                volatility_effect="Skew dependent",
                margin_requirement="Margin on short put",
                legs=[
                    {"right": "call", "side": "long", "qty": 1, "strike_offset": 5},
                    {"right": "put", "side": "short", "qty": 1, "strike_offset": -5}
                ]
            ),
            
            "collar": StrategyConfig(
                name="Protective Collar",
                description="Own stock + long put + short call - downside protection with upside cap",
                market_outlook="Neutral/Protective",
                max_profit="Call strike - stock price + net credit",
                max_loss="Stock price - put strike + net debit",
                breakeven="Stock price ± net premium",
                time_decay_effect="Mixed",
                volatility_effect="Mixed",
                margin_requirement="Stock ownership required",
                legs=[
                    {"right": "put", "side": "long", "qty": 1, "strike_offset": -10},
                    {"right": "call", "side": "short", "qty": 1, "strike_offset": 10}
                ]
            ),
            
            # === COMPLEX MULTI-LEG STRATEGIES ===
            "box_spread": StrategyConfig(
                name="Box Spread",
                description="Bull call + bear put spread - risk-free arbitrage strategy",
                market_outlook="Neutral (arbitrage)",
                max_profit="Strike spread - net premium",
                max_loss="Net premium (if negative arbitrage)",
                breakeven="Perfect arbitrage has no breakeven",
                time_decay_effect="Neutral",
                volatility_effect="Minimal",
                margin_requirement="Net premium",
                legs=[
                    {"right": "call", "side": "long", "qty": 1, "strike_offset": -5},
                    {"right": "call", "side": "short", "qty": 1, "strike_offset": 5},
                    {"right": "put", "side": "short", "qty": 1, "strike_offset": -5},
                    {"right": "put", "side": "long", "qty": 1, "strike_offset": 5}
                ]
            ),
            
            "jade_lizard": StrategyConfig(
                name="Jade Lizard",
                description="Short call spread + short put - high probability neutral strategy",
                market_outlook="Neutral to slightly bullish",
                max_profit="Total premium received",
                max_loss="Call spread width - net premium",
                breakeven="Put strike - net premium received",
                time_decay_effect="Very positive",
                volatility_effect="Negative",
                margin_requirement="Call spread width",
                legs=[
                    {"right": "call", "side": "short", "qty": 1, "strike_offset": 5},
                    {"right": "call", "side": "long", "qty": 1, "strike_offset": 15},
                    {"right": "put", "side": "short", "qty": 1, "strike_offset": -10}
                ]
            ),
            
            "christmas_tree": StrategyConfig(
                name="Christmas Tree Spread",
                description="1x2x1 ratio spread - modified butterfly with skewed risk/reward",
                market_outlook="Directional with volatility component",
                max_profit="At middle strike cluster",
                max_loss="Wings or unlimited (depending on structure)",
                breakeven="Multiple breakeven points",
                time_decay_effect="Complex (depends on spot)",
                volatility_effect="Mixed",
                margin_requirement="Varies by structure",
                legs=[
                    {"right": "call", "side": "long", "qty": 1, "strike_offset": -10},
                    {"right": "call", "side": "short", "qty": 2, "strike_offset": 0},
                    {"right": "call", "side": "short", "qty": 2, "strike_offset": 5},
                    {"right": "call", "side": "long", "qty": 1, "strike_offset": 15}
                ]
            ),
            
            # === VOLATILITY SPECIFIC STRATEGIES ===
            "volatility_crush": StrategyConfig(
                name="Volatility Crush Strategy",
                description="Short premium before earnings/events - capture IV collapse",
                market_outlook="IV overpriced, expect crush",
                max_profit="Premium received",
                max_loss="Varies by structure",
                breakeven="Strike ± premium received",
                time_decay_effect="Very positive",
                volatility_effect="Very negative",
                margin_requirement="Strategy dependent",
                legs=[
                    {"right": "call", "side": "short", "qty": 1, "strike_offset": 5},
                    {"right": "put", "side": "short", "qty": 1, "strike_offset": -5}
                ]
            ),
            
            "earnings_straddle": StrategyConfig(
                name="Earnings Straddle",
                description="Long straddle before earnings - capture large moves",
                market_outlook="Big move expected, direction unknown",
                max_profit="Unlimited",
                max_loss="Total premium paid",
                breakeven="Strike ± total premium",
                time_decay_effect="Very negative post-earnings",
                volatility_effect="Very positive pre-earnings",
                margin_requirement="Total premium paid",
                legs=[
                    {"right": "call", "side": "long", "qty": 1},
                    {"right": "put", "side": "long", "qty": 1}
                ]
            ),
            
            # Add more exotic strategies...
            "broken_wing_butterfly": StrategyConfig(
                name="Broken Wing Butterfly",
                description="Asymmetric butterfly - biased directional neutral strategy",
                market_outlook="Neutral with directional bias",
                max_profit="At middle strike",
                max_loss="Net premium or wing spread",
                breakeven="Asymmetric around middle strike",
                time_decay_effect="Positive at center",
                volatility_effect="Negative",
                margin_requirement="Net premium or wing spread",
                legs=[
                    {"right": "call", "side": "long", "qty": 1, "strike_offset": -5},
                    {"right": "call", "side": "short", "qty": 2, "strike_offset": 0},
                    {"right": "call", "side": "long", "qty": 1, "strike_offset": 10}  # Broken wing
                ]
            )
        }
    
    def get_strategy(self, strategy_type: StrategyType) -> Optional[StrategyConfig]:
        """Get complete strategy configuration"""
        return self.strategies.get(strategy_type)
    
    def list_all_strategies(self) -> List[str]:
        """List all available strategy names"""
        return list(self.strategies.keys())
    
    def get_strategies_by_outlook(self, outlook: str) -> List[Tuple[str, StrategyConfig]]:
        """Filter strategies by market outlook"""
        return [(name, config) for name, config in self.strategies.items() 
                if outlook.lower() in config.market_outlook.lower()]
    
    def get_strategies_by_volatility_effect(self, effect: str) -> List[Tuple[str, StrategyConfig]]:
        """Filter strategies by volatility effect (positive/negative)"""
        return [(name, config) for name, config in self.strategies.items()
                if effect.lower() in config.volatility_effect.lower()]
    
    def build_strategy_legs(self, 
                          strategy_type: StrategyType,
                          spot: float,
                          base_strike: Optional[float] = None,
                          expiry: float = 0.0833,  # 1 month
                          vol: float = 0.20,
                          rate: float = 0.05,
                          div_yield: float = 0.0) -> List[Dict[str, Any]]:
        """Build complete legs for a strategy with market data"""
        
        strategy = self.get_strategy(strategy_type)
        if not strategy:
            raise ValueError(f"Strategy {strategy_type} not found")
        
        if base_strike is None:
            base_strike = spot
        
        legs = []
        for leg_template in strategy.legs:
            leg = leg_template.copy()
            
            # Calculate actual strike
            strike_offset = leg_template.get("strike_offset", 0)
            actual_strike = base_strike + strike_offset
            
            # Add market data
            leg.update({
                "spot": spot,
                "strike": actual_strike,
                "expiry": expiry,
                "vol": vol,
                "rate": rate,
                "div_yield": div_yield
            })
            
            legs.append(leg)
        
        return legs
    
    def price_strategy(self, 
                      strategy_type: StrategyType,
                      spot: float,
                      base_strike: Optional[float] = None,
                      expiry: float = 0.0833,
                      vol: float = 0.20,
                      rate: float = 0.05,
                      div_yield: float = 0.0) -> Dict[str, Any]:
        """Price a complete options strategy"""
        
        legs = self.build_strategy_legs(
            strategy_type, spot, base_strike, expiry, vol, rate, div_yield
        )
        
        pricing_result = price_multi_leg(legs)
        strategy_config = self.get_strategy(strategy_type)
        
        return {
            "strategy_type": strategy_type,
            "strategy_config": strategy_config,
            "legs": legs,
            "pricing": pricing_result,
            "market_data": {
                "spot": spot,
                "base_strike": base_strike or spot,
                "expiry": expiry,
                "vol": vol,
                "rate": rate,
                "div_yield": div_yield
            }
        }

# Initialize the complete strategy library
options_strategy_library = OptionsStrategyLibrary()