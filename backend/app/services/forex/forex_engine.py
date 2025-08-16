"""
💱 FOREX TRADING ENGINE - BEYOND INSTITUTIONAL LEVEL
Complete FX trading, analysis, and multi-asset arbitrage system
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Literal, Tuple, Union
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import asyncio
import math
from enum import Enum
import warnings
warnings.filterwarnings('ignore')

class CurrencyPair(Enum):
    # Major Pairs
    EURUSD = "EURUSD"
    GBPUSD = "GBPUSD"
    USDJPY = "USDJPY"
    USDCHF = "USDCHF"
    AUDUSD = "AUDUSD"
    USDCAD = "USDCAD"
    NZDUSD = "NZDUSD"
    
    # Minor Pairs (Cross Pairs)
    EURJPY = "EURJPY"
    EURGBP = "EURGBP"
    EURCHF = "EURCHF"
    EURAUD = "EURAUD"
    EURCAD = "EURCAD"
    GBPJPY = "GBPJPY"
    GBPCHF = "GBPCHF"
    AUDJPY = "AUDJPY"
    CADJPY = "CADJPY"
    CHFJPY = "CHFJPY"
    
    # Exotic Pairs
    USDTRY = "USDTRY"
    USDZAR = "USDZAR"
    USDMXN = "USDMXN"
    USDRUB = "USDRUB"
    EURTRY = "EURTRY"
    GBPTRY = "GBPTRY"

class ForexSession(Enum):
    SYDNEY = "sydney"
    TOKYO = "tokyo"
    LONDON = "london"
    NEW_YORK = "new_york"

@dataclass
class CurrencyInfo:
    currency: str
    name: str
    central_bank: str
    interest_rate: float
    inflation_rate: float
    gdp_growth: float
    unemployment_rate: float
    debt_to_gdp: float
    current_account: float  # % of GDP
    political_stability: float  # 0-1 scale
    commodity_currency: bool = False
    safe_haven: bool = False

@dataclass
class ForexPair:
    pair: CurrencyPair
    base_currency: str
    quote_currency: str
    pip_size: float
    pip_value_usd: float
    spread_typical: float
    daily_range_pips: int
    volatility_annual: float
    correlation_spy: float
    session_activity: Dict[ForexSession, float]

@dataclass
class ForexPosition:
    position_id: str
    pair: CurrencyPair
    side: Literal["long", "short"]
    size: float  # in base currency
    entry_rate: float
    current_rate: float
    unrealized_pnl_usd: float
    swap_daily: float
    days_held: int
    margin_used: float
    leverage: float
    entry_timestamp: datetime

class ForexMarketAnalyzer:
    """Advanced forex market analysis and intelligence"""
    
    def __init__(self):
        self.currency_info = self._initialize_currency_data()
        self.pair_specs = self._initialize_pair_specs()
        self.correlation_matrix = self._initialize_correlations()
        self.interest_rate_differentials = {}
        
    def _initialize_currency_data(self) -> Dict[str, CurrencyInfo]:
        """Initialize comprehensive currency fundamental data"""
        return {
            "USD": CurrencyInfo(
                currency="USD",
                name="US Dollar",
                central_bank="Federal Reserve",
                interest_rate=5.25,  # Fed Funds Rate
                inflation_rate=3.2,
                gdp_growth=2.4,
                unemployment_rate=3.7,
                debt_to_gdp=120.0,
                current_account=-3.2,
                political_stability=0.85,
                safe_haven=True
            ),
            "EUR": CurrencyInfo(
                currency="EUR",
                name="Euro",
                central_bank="European Central Bank",
                interest_rate=4.50,
                inflation_rate=2.9,
                gdp_growth=0.8,
                unemployment_rate=6.4,
                debt_to_gdp=95.0,
                current_account=2.1,
                political_stability=0.78
            ),
            "GBP": CurrencyInfo(
                currency="GBP",
                name="British Pound",
                central_bank="Bank of England",
                interest_rate=5.25,
                inflation_rate=4.0,
                gdp_growth=0.5,
                unemployment_rate=3.9,
                debt_to_gdp=101.0,
                current_account=-2.8,
                political_stability=0.80
            ),
            "JPY": CurrencyInfo(
                currency="JPY",
                name="Japanese Yen",
                central_bank="Bank of Japan",
                interest_rate=-0.10,
                inflation_rate=3.1,
                gdp_growth=1.2,
                unemployment_rate=2.6,
                debt_to_gdp=260.0,
                current_account=2.9,
                political_stability=0.88,
                safe_haven=True
            ),
            "CHF": CurrencyInfo(
                currency="CHF",
                name="Swiss Franc",
                central_bank="Swiss National Bank",
                interest_rate=1.75,
                inflation_rate=2.1,
                gdp_growth=1.1,
                unemployment_rate=2.1,
                debt_to_gdp=41.0,
                current_account=8.5,
                political_stability=0.95,
                safe_haven=True
            ),
            "AUD": CurrencyInfo(
                currency="AUD",
                name="Australian Dollar",
                central_bank="Reserve Bank of Australia",
                interest_rate=4.35,
                inflation_rate=4.1,
                gdp_growth=1.5,
                unemployment_rate=3.6,
                debt_to_gdp=45.0,
                current_account=-2.1,
                political_stability=0.90,
                commodity_currency=True
            ),
            "CAD": CurrencyInfo(
                currency="CAD",
                name="Canadian Dollar",
                central_bank="Bank of Canada",
                interest_rate=5.00,
                inflation_rate=3.4,
                gdp_growth=1.8,
                unemployment_rate=5.0,
                debt_to_gdp=88.0,
                current_account=-0.9,
                political_stability=0.92,
                commodity_currency=True
            ),
            "NZD": CurrencyInfo(
                currency="NZD",
                name="New Zealand Dollar",
                central_bank="Reserve Bank of New Zealand",
                interest_rate=5.50,
                inflation_rate=4.7,
                gdp_growth=0.9,
                unemployment_rate=3.4,
                debt_to_gdp=33.0,
                current_account=-7.1,
                political_stability=0.93,
                commodity_currency=True
            )
        }
    
    def _initialize_pair_specs(self) -> Dict[CurrencyPair, ForexPair]:
        """Initialize forex pair specifications"""
        return {
            CurrencyPair.EURUSD: ForexPair(
                pair=CurrencyPair.EURUSD,
                base_currency="EUR",
                quote_currency="USD",
                pip_size=0.0001,
                pip_value_usd=10.0,  # for 100k lot
                spread_typical=0.1,  # pips
                daily_range_pips=80,
                volatility_annual=0.12,
                correlation_spy=0.65,
                session_activity={
                    ForexSession.LONDON: 1.0,
                    ForexSession.NEW_YORK: 0.9,
                    ForexSession.TOKYO: 0.3,
                    ForexSession.SYDNEY: 0.2
                }
            ),
            CurrencyPair.GBPUSD: ForexPair(
                pair=CurrencyPair.GBPUSD,
                base_currency="GBP",
                quote_currency="USD",
                pip_size=0.0001,
                pip_value_usd=10.0,
                spread_typical=0.2,
                daily_range_pips=120,
                volatility_annual=0.15,
                correlation_spy=0.58,
                session_activity={
                    ForexSession.LONDON: 1.0,
                    ForexSession.NEW_YORK: 0.8,
                    ForexSession.TOKYO: 0.2,
                    ForexSession.SYDNEY: 0.1
                }
            ),
            CurrencyPair.USDJPY: ForexPair(
                pair=CurrencyPair.USDJPY,
                base_currency="USD",
                quote_currency="JPY",
                pip_size=0.01,
                pip_value_usd=9.17,  # Approximate
                spread_typical=0.1,
                daily_range_pips=70,
                volatility_annual=0.11,
                correlation_spy=-0.25,  # Often negative correlation
                session_activity={
                    ForexSession.TOKYO: 1.0,
                    ForexSession.LONDON: 0.7,
                    ForexSession.NEW_YORK: 0.6,
                    ForexSession.SYDNEY: 0.4
                }
            ),
            # Add more pairs...
        }
    
    def _initialize_correlations(self) -> pd.DataFrame:
        """Initialize currency pair correlation matrix"""
        pairs = ["EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "USDCAD", "NZDUSD"]
        
        # Mock correlation matrix (in practice would be calculated from historical data)
        correlation_data = np.array([
            [1.00, 0.89, -0.85, -0.95, 0.78, -0.82, 0.85],  # EURUSD
            [0.89, 1.00, -0.78, -0.87, 0.82, -0.85, 0.88],  # GBPUSD
            [-0.85, -0.78, 1.00, 0.88, -0.65, 0.75, -0.70],  # USDJPY
            [-0.95, -0.87, 0.88, 1.00, -0.72, 0.79, -0.82],  # USDCHF
            [0.78, 0.82, -0.65, -0.72, 1.00, -0.95, 0.96],  # AUDUSD
            [-0.82, -0.85, 0.75, 0.79, -0.95, 1.00, -0.93],  # USDCAD
            [0.85, 0.88, -0.70, -0.82, 0.96, -0.93, 1.00]   # NZDUSD
        ])
        
        return pd.DataFrame(correlation_data, index=pairs, columns=pairs)
    
    async def analyze_currency_strength(self) -> Dict[str, Any]:
        """Analyze relative currency strength across all majors"""
        
        currencies = ["USD", "EUR", "GBP", "JPY", "CHF", "AUD", "CAD", "NZD"]
        strength_scores = {}
        
        for currency in currencies:
            if currency not in self.currency_info:
                continue
                
            info = self.currency_info[currency]
            
            # Calculate fundamental strength score
            strength_factors = {
                "interest_rate": self._normalize_score(info.interest_rate, 0, 6, 0.25),
                "gdp_growth": self._normalize_score(info.gdp_growth, -2, 4, 0.20),
                "inflation_control": self._normalize_score(abs(info.inflation_rate - 2), 0, 5, -0.15),  # Target 2%
                "unemployment": self._normalize_score(info.unemployment_rate, 15, 2, -0.15),  # Lower is better
                "debt_stability": self._normalize_score(info.debt_to_gdp, 200, 20, -0.10),
                "current_account": self._normalize_score(info.current_account, -10, 10, 0.10),
                "political_stability": info.political_stability * 0.05
            }
            
            total_strength = sum(strength_factors.values())
            strength_scores[currency] = {
                "total_score": total_strength,
                "factors": strength_factors,
                "rank": 0  # Will be calculated after all scores
            }
        
        # Rank currencies
        ranked_currencies = sorted(strength_scores.items(), key=lambda x: x[1]["total_score"], reverse=True)
        for i, (currency, data) in enumerate(ranked_currencies):
            strength_scores[currency]["rank"] = i + 1
        
        return {
            "currency_rankings": strength_scores,
            "strongest_currency": ranked_currencies[0][0],
            "weakest_currency": ranked_currencies[-1][0],
            "analysis_timestamp": datetime.now().isoformat()
        }
    
    def _normalize_score(self, value: float, min_val: float, max_val: float, weight: float) -> float:
        """Normalize a value to 0-1 range and apply weight"""
        if max_val == min_val:
            return 0
        normalized = (value - min_val) / (max_val - min_val)
        normalized = max(0, min(1, normalized))  # Clamp to 0-1
        return normalized * weight
    
    async def analyze_carry_trade_opportunities(self) -> List[Dict[str, Any]]:
        """Identify carry trade opportunities based on interest rate differentials"""
        
        opportunities = []
        currencies = list(self.currency_info.keys())
        
        for i, base_curr in enumerate(currencies):
            for j, quote_curr in enumerate(currencies):
                if i >= j:  # Avoid duplicates and self-comparison
                    continue
                
                base_info = self.currency_info[base_curr]
                quote_info = self.currency_info[quote_curr]
                
                # Calculate interest rate differential
                rate_diff = base_info.interest_rate - quote_info.interest_rate
                
                if abs(rate_diff) > 1.0:  # Minimum 1% differential
                    # Calculate carry trade attractiveness
                    volatility_penalty = 0.15 if base_curr in ["GBP", "AUD", "NZD"] else 0.10
                    political_risk = (2 - base_info.political_stability - quote_info.political_stability) * 0.02
                    
                    net_carry = rate_diff - volatility_penalty - political_risk
                    
                    pair_name = f"{base_curr}{quote_curr}"
                    direction = "long" if rate_diff > 0 else "short"
                    
                    opportunities.append({
                        "pair": pair_name,
                        "direction": direction,
                        "gross_carry": rate_diff,
                        "net_carry": net_carry,
                        "volatility_risk": volatility_penalty,
                        "political_risk": political_risk,
                        "attractiveness": net_carry / abs(rate_diff) if rate_diff != 0 else 0,
                        "funding_currency": quote_curr if rate_diff > 0 else base_curr,
                        "target_currency": base_curr if rate_diff > 0 else quote_curr
                    })
        
        # Sort by attractiveness
        opportunities.sort(key=lambda x: x["attractiveness"], reverse=True)
        return opportunities[:10]  # Top 10 opportunities
    
    async def detect_central_bank_intervention_risk(self, pair: CurrencyPair) -> Dict[str, Any]:
        """Detect potential central bank intervention risk"""
        
        if pair not in self.pair_specs:
            return {"risk": "unknown", "probability": 0.0}
        
        pair_info = self.pair_specs[pair]
        base_curr = pair_info.base_currency
        quote_curr = pair_info.quote_currency
        
        intervention_signals = {
            "verbal_intervention": 0.0,
            "extreme_move": 0.0,
            "policy_divergence": 0.0,
            "economic_imbalance": 0.0
        }
        
        # Mock current rate (in practice, would fetch real-time data)
        current_rate = 1.0950 if pair == CurrencyPair.EURUSD else 150.25 if pair == CurrencyPair.USDJPY else 1.0
        
        # Analyze extreme moves (simplified)
        if pair == CurrencyPair.USDJPY and current_rate > 155:
            intervention_signals["extreme_move"] = 0.8
            intervention_signals["verbal_intervention"] = 0.6
        elif pair == CurrencyPair.EURUSD and current_rate < 1.05:
            intervention_signals["extreme_move"] = 0.4
            intervention_signals["verbal_intervention"] = 0.3
        
        # Policy divergence analysis
        if base_curr in self.currency_info and quote_curr in self.currency_info:
            base_info = self.currency_info[base_curr]
            quote_info = self.currency_info[quote_curr]
            
            rate_diff = abs(base_info.interest_rate - quote_info.interest_rate)
            if rate_diff > 5.0:  # Extreme policy divergence
                intervention_signals["policy_divergence"] = min(0.6, rate_diff / 10)
        
        # Economic imbalance
        intervention_signals["economic_imbalance"] = 0.2  # Mock value
        
        overall_risk = np.mean(list(intervention_signals.values()))
        
        risk_level = "low"
        if overall_risk > 0.7:
            risk_level = "high"
        elif overall_risk > 0.4:
            risk_level = "medium"
        
        return {
            "pair": pair.value,
            "overall_risk": risk_level,
            "probability": overall_risk,
            "signals": intervention_signals,
            "potential_triggers": self._get_intervention_triggers(pair, overall_risk)
        }
    
    def _get_intervention_triggers(self, pair: CurrencyPair, risk_level: float) -> List[str]:
        """Get potential intervention triggers"""
        triggers = []
        
        if risk_level > 0.5:
            triggers.extend([
                "Excessive currency volatility",
                "Disorderly market conditions",
                "Threat to economic stability"
            ])
        
        if pair == CurrencyPair.USDJPY and risk_level > 0.6:
            triggers.append("USD/JPY approaching 155-160 intervention zone")
        
        if pair == CurrencyPair.EURUSD and risk_level > 0.4:
            triggers.append("EUR/USD testing parity levels")
        
        return triggers

class ForexTechnicalAnalyzer:
    """Advanced technical analysis for forex markets"""
    
    def __init__(self):
        self.indicators = {}
        
    async def comprehensive_technical_analysis(self, 
                                             pair: CurrencyPair,
                                             data: pd.DataFrame,
                                             timeframes: List[str] = ["M15", "H1", "H4", "D1"]) -> Dict[str, Any]:
        """Perform comprehensive multi-timeframe technical analysis"""
        
        if data.empty:
            return {"error": "No data provided"}
        
        analysis = {
            "pair": pair.value,
            "timeframe_analysis": {},
            "overall_bias": "neutral",
            "confidence": 0.0,
            "key_levels": {},
            "patterns": [],
            "signals": []
        }
        
        # Multi-timeframe analysis
        for tf in timeframes:
            tf_data = self._resample_data(data, tf)
            tf_analysis = await self._analyze_single_timeframe(tf_data, tf)
            analysis["timeframe_analysis"][tf] = tf_analysis
        
        # Calculate overall bias
        analysis["overall_bias"] = self._calculate_overall_bias(analysis["timeframe_analysis"])
        analysis["confidence"] = self._calculate_confidence(analysis["timeframe_analysis"])
        
        # Key levels analysis
        analysis["key_levels"] = await self._identify_key_levels(data)
        
        # Pattern recognition
        analysis["patterns"] = await self._detect_patterns(data)
        
        # Generate trading signals
        analysis["signals"] = self._generate_technical_signals(analysis)
        
        return analysis
    
    def _resample_data(self, data: pd.DataFrame, timeframe: str) -> pd.DataFrame:
        """Resample data to specified timeframe"""
        # Simplified resampling (in practice, would handle various timeframes properly)
        if timeframe == "M15":
            return data  # Assume input is already M15
        elif timeframe == "H1":
            return data.resample('1H').agg({
                'open': 'first',
                'high': 'max',
                'low': 'min',
                'close': 'last',
                'volume': 'sum'
            }).dropna()
        elif timeframe == "H4":
            return data.resample('4H').agg({
                'open': 'first',
                'high': 'max',
                'low': 'min',
                'close': 'last',
                'volume': 'sum'
            }).dropna()
        elif timeframe == "D1":
            return data.resample('1D').agg({
                'open': 'first',
                'high': 'max',
                'low': 'min',
                'close': 'last',
                'volume': 'sum'
            }).dropna()
        else:
            return data
    
    async def _analyze_single_timeframe(self, data: pd.DataFrame, timeframe: str) -> Dict[str, Any]:
        """Analyze single timeframe"""
        
        if data.empty or len(data) < 50:
            return {"trend": "unknown", "strength": 0.0, "indicators": {}}
        
        indicators = {}
        
        # Moving averages
        indicators["sma_20"] = data['close'].rolling(20).mean().iloc[-1]
        indicators["sma_50"] = data['close'].rolling(50).mean().iloc[-1] if len(data) >= 50 else None
        indicators["ema_12"] = data['close'].ewm(span=12).mean().iloc[-1]
        indicators["ema_26"] = data['close'].ewm(span=26).mean().iloc[-1]
        
        # MACD
        macd_line = indicators["ema_12"] - indicators["ema_26"]
        macd_signal = macd_line  # Simplified
        indicators["macd"] = {
            "line": macd_line,
            "signal": macd_signal,
            "histogram": macd_line - macd_signal
        }
        
        # RSI
        indicators["rsi"] = self._calculate_rsi(data['close']).iloc[-1] if len(data) >= 14 else 50
        
        # Bollinger Bands
        bb_middle = data['close'].rolling(20).mean()
        bb_std = data['close'].rolling(20).std()
        indicators["bollinger"] = {
            "upper": (bb_middle + 2 * bb_std).iloc[-1],
            "middle": bb_middle.iloc[-1],
            "lower": (bb_middle - 2 * bb_std).iloc[-1]
        }
        
        # Stochastic
        indicators["stochastic"] = self._calculate_stochastic(data)
        
        # ATR
        indicators["atr"] = self._calculate_atr(data).iloc[-1] if len(data) >= 14 else 0
        
        # Determine trend
        current_price = data['close'].iloc[-1]
        trend = "neutral"
        strength = 0.0
        
        if indicators["sma_50"] is not None:
            if current_price > indicators["sma_50"] * 1.01:
                trend = "bullish"
                strength = min(1.0, (current_price - indicators["sma_50"]) / indicators["sma_50"] * 10)
            elif current_price < indicators["sma_50"] * 0.99:
                trend = "bearish"
                strength = min(1.0, (indicators["sma_50"] - current_price) / indicators["sma_50"] * 10)
        
        return {
            "timeframe": timeframe,
            "trend": trend,
            "strength": strength,
            "indicators": indicators,
            "current_price": current_price
        }
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_stochastic(self, data: pd.DataFrame, k_period: int = 14, d_period: int = 3) -> Dict[str, float]:
        """Calculate Stochastic oscillator"""
        if len(data) < k_period:
            return {"k": 50, "d": 50}
        
        low_min = data['low'].rolling(window=k_period).min()
        high_max = data['high'].rolling(window=k_period).max()
        k_percent = 100 * ((data['close'] - low_min) / (high_max - low_min))
        d_percent = k_percent.rolling(window=d_period).mean()
        
        return {
            "k": k_percent.iloc[-1] if not pd.isna(k_percent.iloc[-1]) else 50,
            "d": d_percent.iloc[-1] if not pd.isna(d_percent.iloc[-1]) else 50
        }
    
    def _calculate_atr(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average True Range"""
        high_low = data['high'] - data['low']
        high_close = np.abs(data['high'] - data['close'].shift())
        low_close = np.abs(data['low'] - data['close'].shift())
        true_range = np.maximum(high_low, np.maximum(high_close, low_close))
        return true_range.rolling(period).mean()
    
    def _calculate_overall_bias(self, timeframe_analysis: Dict[str, Any]) -> str:
        """Calculate overall bias from multi-timeframe analysis"""
        bullish_votes = 0
        bearish_votes = 0
        total_weight = 0
        
        # Weight different timeframes
        weights = {"M15": 1, "H1": 2, "H4": 3, "D1": 4}
        
        for tf, analysis in timeframe_analysis.items():
            weight = weights.get(tf, 1)
            trend = analysis.get("trend", "neutral")
            strength = analysis.get("strength", 0)
            
            if trend == "bullish":
                bullish_votes += weight * (1 + strength)
            elif trend == "bearish":
                bearish_votes += weight * (1 + strength)
            
            total_weight += weight
        
        if bullish_votes > bearish_votes * 1.2:
            return "bullish"
        elif bearish_votes > bullish_votes * 1.2:
            return "bearish"
        else:
            return "neutral"
    
    def _calculate_confidence(self, timeframe_analysis: Dict[str, Any]) -> float:
        """Calculate confidence in the analysis"""
        agreements = 0
        total = 0
        
        trends = [analysis.get("trend", "neutral") for analysis in timeframe_analysis.values()]
        
        for i in range(len(trends)):
            for j in range(i + 1, len(trends)):
                if trends[i] == trends[j] and trends[i] != "neutral":
                    agreements += 1
                total += 1
        
        return agreements / total if total > 0 else 0.0
    
    async def _identify_key_levels(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Identify key support and resistance levels"""
        
        if data.empty or len(data) < 50:
            return {"support": [], "resistance": []}
        
        # Find pivot points
        highs = data['high'].rolling(window=5, center=True).max()
        lows = data['low'].rolling(window=5, center=True).min()
        
        pivot_highs = data['high'][(data['high'] == highs)].tolist()
        pivot_lows = data['low'][(data['low'] == lows)].tolist()
        
        # Identify significant levels (simplified)
        current_price = data['close'].iloc[-1]
        
        resistance_levels = [level for level in pivot_highs[-10:] if level > current_price]
        support_levels = [level for level in pivot_lows[-10:] if level < current_price]
        
        return {
            "support": sorted(support_levels, reverse=True)[:5],  # Closest 5 support levels
            "resistance": sorted(resistance_levels)[:5],  # Closest 5 resistance levels
            "current_price": current_price
        }
    
    async def _detect_patterns(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect chart patterns"""
        patterns = []
        
        if data.empty or len(data) < 20:
            return patterns
        
        # Simple pattern detection (in practice, would be much more sophisticated)
        
        # Double top/bottom detection
        highs = data['high'].rolling(window=5, center=True).max()
        lows = data['low'].rolling(window=5, center=True).min()
        
        pivot_highs = data['high'][data['high'] == highs].iloc[-10:]
        pivot_lows = data['low'][data['low'] == lows].iloc[-10:]
        
        # Double top
        if len(pivot_highs) >= 2:
            last_two_highs = pivot_highs.iloc[-2:]
            if abs(last_two_highs.iloc[0] - last_two_highs.iloc[1]) / last_two_highs.iloc[0] < 0.002:  # Within 0.2%
                patterns.append({
                    "pattern": "double_top",
                    "confidence": 0.65,
                    "direction": "bearish",
                    "target": data['close'].iloc[-1] * 0.98,
                    "stop": max(last_two_highs) * 1.001
                })
        
        # Double bottom
        if len(pivot_lows) >= 2:
            last_two_lows = pivot_lows.iloc[-2:]
            if abs(last_two_lows.iloc[0] - last_two_lows.iloc[1]) / last_two_lows.iloc[0] < 0.002:
                patterns.append({
                    "pattern": "double_bottom",
                    "confidence": 0.65,
                    "direction": "bullish",
                    "target": data['close'].iloc[-1] * 1.02,
                    "stop": min(last_two_lows) * 0.999
                })
        
        # Head and shoulders (very simplified)
        if len(pivot_highs) >= 3:
            last_three = pivot_highs.iloc[-3:]
            if (last_three.iloc[1] > last_three.iloc[0] * 1.005 and 
                last_three.iloc[1] > last_three.iloc[2] * 1.005):
                patterns.append({
                    "pattern": "head_and_shoulders",
                    "confidence": 0.70,
                    "direction": "bearish",
                    "target": data['close'].iloc[-1] * 0.95,
                    "stop": last_three.iloc[1] * 1.002
                })
        
        return patterns
    
    def _generate_technical_signals(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate trading signals from technical analysis"""
        signals = []
        
        overall_bias = analysis.get("overall_bias", "neutral")
        confidence = analysis.get("confidence", 0.0)
        patterns = analysis.get("patterns", [])
        
        # Signal from overall bias
        if overall_bias != "neutral" and confidence > 0.6:
            signals.append({
                "signal_type": "trend_following",
                "direction": overall_bias,
                "strength": confidence,
                "timeframe": "multiple",
                "reasoning": f"Multi-timeframe {overall_bias} bias with {confidence:.1%} confidence"
            })
        
        # Signals from patterns
        for pattern in patterns:
            if pattern["confidence"] > 0.65:
                signals.append({
                    "signal_type": "pattern",
                    "direction": pattern["direction"],
                    "strength": pattern["confidence"],
                    "pattern": pattern["pattern"],
                    "target": pattern.get("target"),
                    "stop": pattern.get("stop"),
                    "reasoning": f"{pattern['pattern']} pattern detected"
                })
        
        # RSI signals
        for tf, tf_analysis in analysis.get("timeframe_analysis", {}).items():
            indicators = tf_analysis.get("indicators", {})
            rsi = indicators.get("rsi")
            
            if rsi is not None:
                if rsi < 25:
                    signals.append({
                        "signal_type": "oversold",
                        "direction": "bullish",
                        "strength": 0.6,
                        "timeframe": tf,
                        "indicator": "RSI",
                        "value": rsi,
                        "reasoning": f"RSI oversold at {rsi:.1f}"
                    })
                elif rsi > 75:
                    signals.append({
                        "signal_type": "overbought",
                        "direction": "bearish",
                        "strength": 0.6,
                        "timeframe": tf,
                        "indicator": "RSI",
                        "value": rsi,
                        "reasoning": f"RSI overbought at {rsi:.1f}"
                    })
        
        return signals

class ForexArbitrageEngine:
    """Advanced forex arbitrage and cross-currency opportunities"""
    
    def __init__(self):
        self.triangular_combinations = self._generate_triangular_combinations()
        self.spread_threshold = 0.0005  # 5 pips minimum profit threshold
        
    def _generate_triangular_combinations(self) -> List[Tuple[str, str, str]]:
        """Generate all possible triangular arbitrage combinations"""
        return [
            ("EUR", "USD", "JPY"),
            ("EUR", "USD", "GBP"),
            ("EUR", "USD", "CHF"),
            ("EUR", "USD", "AUD"),
            ("EUR", "USD", "CAD"),
            ("GBP", "USD", "JPY"),
            ("GBP", "USD", "CHF"),
            ("AUD", "USD", "JPY"),
            ("AUD", "USD", "NZD"),
            ("CHF", "JPY", "USD"),
            # Add more combinations...
        ]
    
    async def scan_triangular_arbitrage(self, rates: Dict[str, float]) -> List[Dict[str, Any]]:
        """Scan for triangular arbitrage opportunities"""
        
        opportunities = []
        
        for base, quote, cross in self.triangular_combinations:
            # Get required rates
            direct_rate = rates.get(f"{base}{quote}")
            cross_rate_1 = rates.get(f"{base}{cross}")
            cross_rate_2 = rates.get(f"{cross}{quote}")
            
            # Try inverse rates if direct rates not available
            if direct_rate is None:
                inverse_rate = rates.get(f"{quote}{base}")
                direct_rate = 1 / inverse_rate if inverse_rate else None
            
            if cross_rate_1 is None:
                inverse_rate = rates.get(f"{cross}{base}")
                cross_rate_1 = 1 / inverse_rate if inverse_rate else None
            
            if cross_rate_2 is None:
                inverse_rate = rates.get(f"{quote}{cross}")
                cross_rate_2 = 1 / inverse_rate if inverse_rate else None
            
            if all(rate is not None for rate in [direct_rate, cross_rate_1, cross_rate_2]):
                # Calculate triangular arbitrage
                synthetic_rate = cross_rate_1 * cross_rate_2
                spread = abs(direct_rate - synthetic_rate) / direct_rate
                
                if spread > self.spread_threshold:
                    profit_direction = "buy_direct" if direct_rate < synthetic_rate else "sell_direct"
                    
                    opportunities.append({
                        "currencies": (base, quote, cross),
                        "direct_rate": direct_rate,
                        "synthetic_rate": synthetic_rate,
                        "spread_pct": spread,
                        "profit_direction": profit_direction,
                        "estimated_profit": spread - 0.0002,  # Account for spreads
                        "execution_complexity": "medium",
                        "time_sensitivity": "high"
                    })
        
        # Sort by profitability
        opportunities.sort(key=lambda x: x["estimated_profit"], reverse=True)
        return opportunities[:5]  # Top 5 opportunities
    
    async def scan_carry_arbitrage(self, rates: Dict[str, float], interest_rates: Dict[str, float]) -> List[Dict[str, Any]]:
        """Scan for carry trade arbitrage opportunities"""
        
        opportunities = []
        
        # Cross-broker arbitrage (simplified)
        for pair, rate in rates.items():
            if len(pair) == 6:  # Standard currency pair format
                base_curr = pair[:3]
                quote_curr = pair[3:]
                
                base_rate = interest_rates.get(base_curr, 0)
                quote_rate = interest_rates.get(quote_curr, 0)
                
                carry_differential = base_rate - quote_rate
                
                # Look for high carry with favorable technical setup
                if abs(carry_differential) > 2.0:  # Minimum 2% differential
                    opportunities.append({
                        "pair": pair,
                        "carry_differential": carry_differential,
                        "funding_currency": quote_curr if carry_differential > 0 else base_curr,
                        "target_currency": base_curr if carry_differential > 0 else quote_curr,
                        "estimated_annual_return": abs(carry_differential),
                        "risk_level": self._assess_carry_risk(base_curr, quote_curr),
                        "optimal_position_size": self._calculate_optimal_carry_size(carry_differential)
                    })
        
        return sorted(opportunities, key=lambda x: x["estimated_annual_return"], reverse=True)[:10]
    
    def _assess_carry_risk(self, base_curr: str, quote_curr: str) -> str:
        """Assess risk level for carry trade"""
        
        high_risk_currencies = ["TRY", "ZAR", "MXN", "RUB"]
        volatile_currencies = ["GBP", "AUD", "NZD"]
        
        if any(curr in high_risk_currencies for curr in [base_curr, quote_curr]):
            return "high"
        elif any(curr in volatile_currencies for curr in [base_curr, quote_curr]):
            return "medium"
        else:
            return "low"
    
    def _calculate_optimal_carry_size(self, carry_differential: float) -> float:
        """Calculate optimal position size for carry trade"""
        
        # Kelly criterion for carry trades (simplified)
        win_probability = 0.55 if abs(carry_differential) > 3 else 0.52
        average_win = abs(carry_differential) / 100  # Convert to decimal
        average_loss = 0.05  # 5% average loss
        
        kelly_fraction = (win_probability * average_win - (1 - win_probability) * average_loss) / average_win
        optimal_size = max(0.1, min(0.25, kelly_fraction))  # Between 10% and 25%
        
        return optimal_size

# Initialize forex engine components
market_analyzer = ForexMarketAnalyzer()
technical_analyzer = ForexTechnicalAnalyzer()
arbitrage_engine = ForexArbitrageEngine()