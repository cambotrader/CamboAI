"""
⚡ FUTURES TRADING ENGINE - BEYOND CME GROUP
Complete futures trading, analysis, and risk management system
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Literal, Tuple
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import asyncio
import math
from enum import Enum

class FuturesAssetClass(Enum):
    EQUITY_INDEX = "equity_index"
    COMMODITY = "commodity"
    CURRENCY = "currency"
    INTEREST_RATE = "interest_rate"
    ENERGY = "energy"
    METALS = "metals"
    AGRICULTURE = "agriculture"
    CRYPTO = "crypto"

class ContractSpecs(Enum):
    # Equity Index Futures
    ES = {"name": "E-mini S&P 500", "tick_size": 0.25, "tick_value": 12.50, "margin": 12000}
    NQ = {"name": "E-mini Nasdaq 100", "tick_size": 0.25, "tick_value": 5.00, "margin": 17000}
    YM = {"name": "E-mini Dow", "tick_size": 1.0, "tick_value": 5.00, "margin": 8500}
    RTY = {"name": "E-mini Russell 2000", "tick_size": 0.10, "tick_value": 5.00, "margin": 5500}
    
    # Energy Futures
    CL = {"name": "Crude Oil", "tick_size": 0.01, "tick_value": 10.00, "margin": 7000}
    NG = {"name": "Natural Gas", "tick_size": 0.001, "tick_value": 10.00, "margin": 3500}
    RB = {"name": "RBOB Gasoline", "tick_size": 0.0001, "tick_value": 4.20, "margin": 6000}
    HO = {"name": "Heating Oil", "tick_size": 0.0001, "tick_value": 4.20, "margin": 5500}
    
    # Metals
    GC = {"name": "Gold", "tick_size": 0.10, "tick_value": 10.00, "margin": 11000}
    SI = {"name": "Silver", "tick_size": 0.005, "tick_value": 25.00, "margin": 14000}
    PL = {"name": "Platinum", "tick_size": 0.10, "tick_value": 5.00, "margin": 2750}
    PA = {"name": "Palladium", "tick_size": 0.05, "tick_value": 5.00, "margin": 6750}
    HG = {"name": "Copper", "tick_size": 0.0005, "tick_value": 12.50, "margin": 4000}
    
    # Agriculture
    C = {"name": "Corn", "tick_size": 0.25, "tick_value": 12.50, "margin": 2000}
    S = {"name": "Soybeans", "tick_size": 0.25, "tick_value": 12.50, "margin": 4500}
    W = {"name": "Wheat", "tick_size": 0.25, "tick_value": 12.50, "margin": 2500}
    KC = {"name": "Coffee", "tick_size": 0.05, "tick_value": 18.75, "margin": 4500}
    SB = {"name": "Sugar", "tick_size": 0.01, "tick_value": 11.20, "margin": 2000}
    
    # Currency Futures
    EUR = {"name": "Euro", "tick_size": 0.00005, "tick_value": 6.25, "margin": 2500}
    JPY = {"name": "Japanese Yen", "tick_size": 0.0000005, "tick_value": 6.25, "margin": 2000}
    GBP = {"name": "British Pound", "tick_size": 0.0001, "tick_value": 6.25, "margin": 3000}
    CHF = {"name": "Swiss Franc", "tick_size": 0.0001, "tick_value": 12.50, "margin": 2750}
    
    # Interest Rate Futures
    ZN = {"name": "10-Year Note", "tick_size": 0.015625, "tick_value": 15.625, "margin": 1500}
    ZB = {"name": "30-Year Bond", "tick_size": 0.03125, "tick_value": 31.25, "margin": 4500}
    ZF = {"name": "5-Year Note", "tick_size": 0.0078125, "tick_value": 7.8125, "margin": 1000}

@dataclass
class FuturesContract:
    symbol: str
    asset_class: FuturesAssetClass
    expiry_month: str
    expiry_year: int
    contract_size: float
    tick_size: float
    tick_value: float
    margin_requirement: float
    settlement_type: Literal["cash", "physical"]
    trading_hours: Dict[str, str]
    last_trading_day: datetime

@dataclass
class FuturesPosition:
    position_id: str
    symbol: str
    contract: FuturesContract
    side: Literal["long", "short"]
    quantity: int
    entry_price: float
    current_price: float
    unrealized_pnl: float
    margin_used: float
    margin_excess: float
    days_held: int
    entry_timestamp: datetime

@dataclass
class SpreadPosition:
    spread_id: str
    spread_type: Literal["calendar", "inter_commodity", "inter_market"]
    leg_1: FuturesPosition
    leg_2: FuturesPosition
    spread_ratio: Tuple[int, int]  # (leg1_qty, leg2_qty)
    net_premium: float
    spread_pnl: float
    margin_requirement: float

class FuturesContractDatabase:
    """Complete futures contract specifications database"""
    
    def __init__(self):
        self.contracts = self._initialize_contracts()
        self.expiry_calendar = self._generate_expiry_calendar()
        
    def _initialize_contracts(self) -> Dict[str, FuturesContract]:
        """Initialize all major futures contracts"""
        contracts = {}
        
        # Equity Index Futures
        contracts["ES"] = FuturesContract(
            symbol="ES",
            asset_class=FuturesAssetClass.EQUITY_INDEX,
            expiry_month="H",  # March
            expiry_year=2024,
            contract_size=50.0,  # $50 per point
            tick_size=0.25,
            tick_value=12.50,
            margin_requirement=12000,
            settlement_type="cash",
            trading_hours={"open": "17:00", "close": "16:00", "timezone": "CT"},
            last_trading_day=datetime(2024, 3, 15)
        )
        
        contracts["NQ"] = FuturesContract(
            symbol="NQ",
            asset_class=FuturesAssetClass.EQUITY_INDEX,
            expiry_month="H",
            expiry_year=2024,
            contract_size=20.0,  # $20 per point
            tick_size=0.25,
            tick_value=5.00,
            margin_requirement=17000,
            settlement_type="cash",
            trading_hours={"open": "17:00", "close": "16:00", "timezone": "CT"},
            last_trading_day=datetime(2024, 3, 15)
        )
        
        # Energy Futures
        contracts["CL"] = FuturesContract(
            symbol="CL",
            asset_class=FuturesAssetClass.ENERGY,
            expiry_month="F",  # January
            expiry_year=2024,
            contract_size=1000.0,  # 1000 barrels
            tick_size=0.01,
            tick_value=10.00,
            margin_requirement=7000,
            settlement_type="physical",
            trading_hours={"open": "17:00", "close": "16:00", "timezone": "CT"},
            last_trading_day=datetime(2024, 1, 22)
        )
        
        contracts["NG"] = FuturesContract(
            symbol="NG",
            asset_class=FuturesAssetClass.ENERGY,
            expiry_month="F",
            expiry_year=2024,
            contract_size=10000.0,  # 10,000 MMBtu
            tick_size=0.001,
            tick_value=10.00,
            margin_requirement=3500,
            settlement_type="physical",
            trading_hours={"open": "17:00", "close": "16:00", "timezone": "CT"},
            last_trading_day=datetime(2024, 1, 26)
        )
        
        # Metals
        contracts["GC"] = FuturesContract(
            symbol="GC",
            asset_class=FuturesAssetClass.METALS,
            expiry_month="G",  # February
            expiry_year=2024,
            contract_size=100.0,  # 100 troy oz
            tick_size=0.10,
            tick_value=10.00,
            margin_requirement=11000,
            settlement_type="physical",
            trading_hours={"open": "17:00", "close": "16:00", "timezone": "CT"},
            last_trading_day=datetime(2024, 2, 27)
        )
        
        # Add more contracts...
        return contracts
    
    def _generate_expiry_calendar(self) -> Dict[str, List[datetime]]:
        """Generate expiry calendar for all contracts"""
        calendar = {}
        
        # Generate monthly expiries for next 24 months
        base_date = datetime.now()
        for symbol in self.contracts.keys():
            expiries = []
            for i in range(24):
                expiry_date = base_date + timedelta(days=30*i)
                # Set to 3rd Friday of month (simplified)
                expiry_date = expiry_date.replace(day=15)
                expiries.append(expiry_date)
            calendar[symbol] = expiries
        
        return calendar
    
    def get_contract(self, symbol: str, expiry: Optional[datetime] = None) -> Optional[FuturesContract]:
        """Get contract specification"""
        if symbol not in self.contracts:
            return None
        
        contract = self.contracts[symbol]
        if expiry:
            # Update expiry information
            contract.last_trading_day = expiry
        
        return contract
    
    def get_active_contracts(self, asset_class: Optional[FuturesAssetClass] = None) -> List[str]:
        """Get list of active contracts"""
        if asset_class:
            return [symbol for symbol, contract in self.contracts.items() 
                    if contract.asset_class == asset_class]
        return list(self.contracts.keys())

class FuturesPricingEngine:
    """Advanced futures pricing and fair value calculations"""
    
    def __init__(self):
        self.risk_free_rate = 0.05
        self.storage_costs = {}
        self.convenience_yields = {}
        
    def calculate_fair_value(self, 
                           spot_price: float,
                           contract: FuturesContract,
                           time_to_expiry: float,
                           dividend_yield: float = 0.0,
                           storage_cost: float = 0.0,
                           convenience_yield: float = 0.0) -> Dict[str, Any]:
        """Calculate theoretical fair value for futures contract"""
        
        if contract.asset_class == FuturesAssetClass.EQUITY_INDEX:
            # Equity index futures: F = S * e^((r-d)*T)
            fair_value = spot_price * math.exp((self.risk_free_rate - dividend_yield) * time_to_expiry)
            
        elif contract.asset_class in [FuturesAssetClass.COMMODITY, FuturesAssetClass.ENERGY, FuturesAssetClass.METALS]:
            # Commodity futures: F = S * e^((r + storage - convenience)*T)
            cost_of_carry = self.risk_free_rate + storage_cost - convenience_yield
            fair_value = spot_price * math.exp(cost_of_carry * time_to_expiry)
            
        elif contract.asset_class == FuturesAssetClass.CURRENCY:
            # Currency futures: F = S * e^((r_domestic - r_foreign)*T)
            foreign_rate = 0.02  # Simplified
            fair_value = spot_price * math.exp((self.risk_free_rate - foreign_rate) * time_to_expiry)
            
        elif contract.asset_class == FuturesAssetClass.INTEREST_RATE:
            # Interest rate futures - more complex pricing
            fair_value = self._price_interest_rate_future(spot_price, time_to_expiry)
            
        else:
            fair_value = spot_price  # Fallback
        
        return {
            "fair_value": fair_value,
            "spot_price": spot_price,
            "time_to_expiry": time_to_expiry,
            "cost_of_carry": self.risk_free_rate + storage_cost - convenience_yield,
            "basis": fair_value - spot_price,
            "theoretical_edge": 0.0  # To be calculated vs market price
        }
    
    def _price_interest_rate_future(self, current_yield: float, time_to_expiry: float) -> float:
        """Price interest rate futures (simplified)"""
        # For bond futures, price = 100 - implied_yield
        # This is a simplified calculation
        implied_yield = current_yield + 0.01  # Mock calculation
        return 100 - implied_yield
    
    def calculate_spread_fair_value(self, 
                                   contract1: FuturesContract,
                                   contract2: FuturesContract,
                                   spot1: float,
                                   spot2: float,
                                   correlation: float = 0.8) -> Dict[str, Any]:
        """Calculate fair value for futures spreads"""
        
        # Calculate individual fair values
        fv1 = self.calculate_fair_value(spot1, contract1, 0.25)  # 3 months
        fv2 = self.calculate_fair_value(spot2, contract2, 0.25)
        
        # Calculate spread fair value
        spread_fair_value = fv1["fair_value"] - fv2["fair_value"]
        
        # Calculate spread volatility (simplified)
        vol1, vol2 = 0.25, 0.30  # Mock volatilities
        spread_vol = math.sqrt(vol1**2 + vol2**2 - 2*correlation*vol1*vol2)
        
        return {
            "spread_fair_value": spread_fair_value,
            "spread_volatility": spread_vol,
            "correlation": correlation,
            "hedge_ratio": self._calculate_hedge_ratio(spot1, spot2, vol1, vol2, correlation)
        }
    
    def _calculate_hedge_ratio(self, price1: float, price2: float, vol1: float, vol2: float, corr: float) -> float:
        """Calculate optimal hedge ratio for spread"""
        return (vol1 / vol2) * corr

class FuturesRiskManager:
    """Advanced futures risk management and margin calculations"""
    
    def __init__(self):
        self.portfolio_margin_model = "SPAN"  # Standard Portfolio Analysis of Risk
        self.intraday_margin_multiplier = 0.75
        self.overnight_margin_multiplier = 1.0
        
    def calculate_portfolio_margin(self, positions: List[FuturesPosition]) -> Dict[str, Any]:
        """Calculate total portfolio margin requirement"""
        
        total_initial_margin = 0
        total_maintenance_margin = 0
        net_liquidation_value = 0
        
        # Group positions by asset class for cross-margining
        positions_by_class = {}
        for pos in positions:
            asset_class = pos.contract.asset_class
            if asset_class not in positions_by_class:
                positions_by_class[asset_class] = []
            positions_by_class[asset_class].append(pos)
        
        # Calculate margin for each asset class
        margin_by_class = {}
        for asset_class, class_positions in positions_by_class.items():
            class_margin = self._calculate_class_margin(class_positions)
            margin_by_class[asset_class.value] = class_margin
            total_initial_margin += class_margin["initial_margin"]
            total_maintenance_margin += class_margin["maintenance_margin"]
        
        # Calculate net liquidation value
        for pos in positions:
            position_value = pos.quantity * pos.current_price * pos.contract.contract_size
            if pos.side == "short":
                position_value *= -1
            net_liquidation_value += position_value + pos.unrealized_pnl
        
        # Calculate margin utilization
        margin_excess = net_liquidation_value - total_initial_margin
        utilization = total_initial_margin / net_liquidation_value if net_liquidation_value > 0 else 1.0
        
        return {
            "total_initial_margin": total_initial_margin,
            "total_maintenance_margin": total_maintenance_margin,
            "net_liquidation_value": net_liquidation_value,
            "margin_excess": margin_excess,
            "margin_utilization": utilization,
            "margin_by_asset_class": margin_by_class,
            "buying_power": margin_excess,
            "max_position_size": self._calculate_max_position_size(margin_excess)
        }
    
    def _calculate_class_margin(self, positions: List[FuturesPosition]) -> Dict[str, Any]:
        """Calculate margin for positions within same asset class"""
        
        if not positions:
            return {"initial_margin": 0, "maintenance_margin": 0}
        
        # Simplified SPAN-like calculation
        gross_margin = sum(pos.margin_used for pos in positions)
        
        # Apply netting benefits for opposite positions
        long_exposure = sum(pos.quantity * pos.contract.contract_size 
                           for pos in positions if pos.side == "long")
        short_exposure = sum(pos.quantity * pos.contract.contract_size 
                            for pos in positions if pos.side == "short")
        
        net_exposure = abs(long_exposure - short_exposure)
        gross_exposure = long_exposure + short_exposure
        
        # Netting benefit (simplified)
        netting_benefit = min(gross_margin * 0.3, gross_margin - net_exposure/gross_exposure * gross_margin) if gross_exposure > 0 else 0
        
        net_margin = max(gross_margin - netting_benefit, gross_margin * 0.5)  # Min 50% of gross
        
        return {
            "initial_margin": net_margin,
            "maintenance_margin": net_margin * 0.8,  # 80% of initial
            "gross_margin": gross_margin,
            "netting_benefit": netting_benefit,
            "net_exposure": net_exposure
        }
    
    def _calculate_max_position_size(self, available_margin: float) -> Dict[str, int]:
        """Calculate maximum position size for each contract type"""
        max_sizes = {}
        
        # Sample margin requirements (would come from contract database)
        margin_requirements = {
            "ES": 12000, "NQ": 17000, "CL": 7000, "GC": 11000,
            "NG": 3500, "ZN": 1500, "EUR": 2500
        }
        
        for symbol, margin in margin_requirements.items():
            max_contracts = int(available_margin / margin)
            max_sizes[symbol] = max_contracts
        
        return max_sizes
    
    def calculate_var(self, 
                     positions: List[FuturesPosition],
                     confidence_level: float = 0.95,
                     holding_period: int = 1) -> Dict[str, Any]:
        """Calculate Value at Risk for futures portfolio"""
        
        if not positions:
            return {"var": 0, "component_var": {}}
        
        # Calculate position deltas (price sensitivity)
        position_deltas = {}
        total_portfolio_value = 0
        
        for pos in positions:
            position_value = pos.quantity * pos.current_price * pos.contract.contract_size
            if pos.side == "short":
                position_value *= -1
            
            position_deltas[pos.symbol] = position_value
            total_portfolio_value += position_value
        
        # Simplified VaR calculation (in practice, would use historical simulation or Monte Carlo)
        portfolio_volatility = 0.20  # 20% annual volatility assumption
        daily_volatility = portfolio_volatility / math.sqrt(252)
        
        # Scale for holding period
        period_volatility = daily_volatility * math.sqrt(holding_period)
        
        # VaR calculation
        z_score = 1.645 if confidence_level == 0.95 else 2.326  # 95% or 99%
        portfolio_var = abs(total_portfolio_value) * period_volatility * z_score
        
        # Component VaR (simplified)
        component_var = {}
        for symbol, delta in position_deltas.items():
            component_contribution = abs(delta) / abs(total_portfolio_value) * portfolio_var if total_portfolio_value != 0 else 0
            component_var[symbol] = component_contribution
        
        return {
            "portfolio_var": portfolio_var,
            "confidence_level": confidence_level,
            "holding_period_days": holding_period,
            "portfolio_value": total_portfolio_value,
            "component_var": component_var,
            "concentration_risk": max(component_var.values()) / portfolio_var if portfolio_var > 0 else 0
        }

class FuturesStrategyEngine:
    """Advanced futures trading strategies"""
    
    def __init__(self):
        self.strategy_library = {
            "trend_following": self._trend_following_strategy,
            "mean_reversion": self._mean_reversion_strategy,
            "calendar_spread": self._calendar_spread_strategy,
            "inter_commodity": self._inter_commodity_strategy,
            "carry_trade": self._carry_trade_strategy,
            "momentum": self._momentum_strategy,
            "pairs_trading": self._pairs_trading_strategy,
            "volatility_breakout": self._volatility_breakout_strategy
        }
    
    async def generate_strategy_signals(self, 
                                      market_data: Dict[str, pd.DataFrame],
                                      strategy_type: str) -> List[Dict[str, Any]]:
        """Generate trading signals for specified strategy"""
        
        if strategy_type not in self.strategy_library:
            raise ValueError(f"Unknown strategy: {strategy_type}")
        
        strategy_func = self.strategy_library[strategy_type]
        signals = await strategy_func(market_data)
        
        return signals
    
    async def _trend_following_strategy(self, market_data: Dict[str, pd.DataFrame]) -> List[Dict[str, Any]]:
        """Generate trend following signals"""
        signals = []
        
        for symbol, data in market_data.items():
            if data.empty:
                continue
            
            # Calculate trend indicators
            sma_short = data['close'].rolling(20).mean()
            sma_long = data['close'].rolling(50).mean()
            atr = self._calculate_atr(data)
            
            current_price = data['close'].iloc[-1]
            current_sma_short = sma_short.iloc[-1]
            current_sma_long = sma_long.iloc[-1]
            current_atr = atr.iloc[-1]
            
            # Trend following logic
            if current_sma_short > current_sma_long * 1.02:  # Strong uptrend
                signals.append({
                    "symbol": symbol,
                    "strategy": "trend_following",
                    "signal": "buy",
                    "entry_price": current_price,
                    "stop_loss": current_price - 2 * current_atr,
                    "take_profit": current_price + 4 * current_atr,
                    "confidence": 0.75,
                    "risk_reward": 2.0,
                    "reasoning": "Strong uptrend with SMA crossover"
                })
            
            elif current_sma_short < current_sma_long * 0.98:  # Strong downtrend
                signals.append({
                    "symbol": symbol,
                    "strategy": "trend_following",
                    "signal": "sell",
                    "entry_price": current_price,
                    "stop_loss": current_price + 2 * current_atr,
                    "take_profit": current_price - 4 * current_atr,
                    "confidence": 0.75,
                    "risk_reward": 2.0,
                    "reasoning": "Strong downtrend with SMA crossover"
                })
        
        return signals
    
    async def _mean_reversion_strategy(self, market_data: Dict[str, pd.DataFrame]) -> List[Dict[str, Any]]:
        """Generate mean reversion signals"""
        signals = []
        
        for symbol, data in market_data.items():
            if data.empty or len(data) < 50:
                continue
            
            # Calculate Bollinger Bands
            sma = data['close'].rolling(20).mean()
            std = data['close'].rolling(20).std()
            upper_band = sma + 2 * std
            lower_band = sma - 2 * std
            
            current_price = data['close'].iloc[-1]
            current_upper = upper_band.iloc[-1]
            current_lower = lower_band.iloc[-1]
            current_sma = sma.iloc[-1]
            
            # RSI calculation
            rsi = self._calculate_rsi(data['close'])
            current_rsi = rsi.iloc[-1]
            
            # Mean reversion logic
            if current_price < current_lower and current_rsi < 30:
                signals.append({
                    "symbol": symbol,
                    "strategy": "mean_reversion",
                    "signal": "buy",
                    "entry_price": current_price,
                    "stop_loss": current_price * 0.97,
                    "take_profit": current_sma,
                    "confidence": 0.70,
                    "reasoning": "Oversold condition at lower Bollinger Band"
                })
            
            elif current_price > current_upper and current_rsi > 70:
                signals.append({
                    "symbol": symbol,
                    "strategy": "mean_reversion",
                    "signal": "sell",
                    "entry_price": current_price,
                    "stop_loss": current_price * 1.03,
                    "take_profit": current_sma,
                    "confidence": 0.70,
                    "reasoning": "Overbought condition at upper Bollinger Band"
                })
        
        return signals
    
    async def _calendar_spread_strategy(self, market_data: Dict[str, pd.DataFrame]) -> List[Dict[str, Any]]:
        """Generate calendar spread signals"""
        signals = []
        
        # Look for calendar spread opportunities
        for symbol in market_data.keys():
            if f"{symbol}_front" in market_data and f"{symbol}_back" in market_data:
                front_data = market_data[f"{symbol}_front"]
                back_data = market_data[f"{symbol}_back"]
                
                if front_data.empty or back_data.empty:
                    continue
                
                # Calculate spread
                spread = front_data['close'] - back_data['close']
                spread_mean = spread.rolling(20).mean().iloc[-1]
                spread_std = spread.rolling(20).std().iloc[-1]
                current_spread = spread.iloc[-1]
                
                # Calendar spread signals
                if current_spread > spread_mean + 2 * spread_std:
                    signals.append({
                        "symbol": symbol,
                        "strategy": "calendar_spread",
                        "signal": "sell_front_buy_back",
                        "spread_value": current_spread,
                        "target_spread": spread_mean,
                        "confidence": 0.65,
                        "reasoning": "Front month overpriced relative to back month"
                    })
                
                elif current_spread < spread_mean - 2 * spread_std:
                    signals.append({
                        "symbol": symbol,
                        "strategy": "calendar_spread",
                        "signal": "buy_front_sell_back",
                        "spread_value": current_spread,
                        "target_spread": spread_mean,
                        "confidence": 0.65,
                        "reasoning": "Front month underpriced relative to back month"
                    })
        
        return signals
    
    async def _inter_commodity_strategy(self, market_data: Dict[str, pd.DataFrame]) -> List[Dict[str, Any]]:
        """Generate inter-commodity spread signals"""
        signals = []
        
        # Crack spread (CL vs RB + HO)
        if all(symbol in market_data for symbol in ["CL", "RB", "HO"]):
            cl_price = market_data["CL"]['close'].iloc[-1] if not market_data["CL"].empty else 0
            rb_price = market_data["RB"]['close'].iloc[-1] if not market_data["RB"].empty else 0
            ho_price = market_data["HO"]['close'].iloc[-1] if not market_data["HO"].empty else 0
            
            # Simplified crack spread calculation
            crack_spread = cl_price - (rb_price + ho_price) / 2
            
            # Historical analysis would determine normal range
            if crack_spread > 15:  # Simplified threshold
                signals.append({
                    "strategy": "inter_commodity",
                    "signal": "crack_spread_short",
                    "spread_value": crack_spread,
                    "confidence": 0.60,
                    "reasoning": "Crack spread elevated, refining margins compressed"
                })
        
        # Gold/Silver ratio
        if "GC" in market_data and "SI" in market_data:
            gold_price = market_data["GC"]['close'].iloc[-1] if not market_data["GC"].empty else 0
            silver_price = market_data["SI"]['close'].iloc[-1] if not market_data["SI"].empty else 0
            
            if silver_price > 0:
                gs_ratio = gold_price / silver_price
                
                if gs_ratio > 80:  # Silver undervalued
                    signals.append({
                        "strategy": "inter_commodity",
                        "signal": "long_silver_short_gold",
                        "ratio": gs_ratio,
                        "confidence": 0.55,
                        "reasoning": "Gold/Silver ratio extended, silver catch-up likely"
                    })
                elif gs_ratio < 60:  # Gold undervalued
                    signals.append({
                        "strategy": "inter_commodity",
                        "signal": "long_gold_short_silver",
                        "ratio": gs_ratio,
                        "confidence": 0.55,
                        "reasoning": "Gold/Silver ratio compressed, gold outperformance likely"
                    })
        
        return signals
    
    async def _carry_trade_strategy(self, market_data: Dict[str, pd.DataFrame]) -> List[Dict[str, Any]]:
        """Generate carry trade signals"""
        signals = []
        
        # Currency carry trades
        currency_pairs = [("EUR", "USD"), ("JPY", "USD"), ("GBP", "USD")]
        interest_rates = {"EUR": 0.02, "USD": 0.05, "JPY": -0.001, "GBP": 0.04}  # Mock rates
        
        for base, quote in currency_pairs:
            if base in market_data and quote in market_data:
                carry = interest_rates.get(quote, 0) - interest_rates.get(base, 0)
                
                if carry > 0.02:  # Positive carry > 2%
                    signals.append({
                        "strategy": "carry_trade",
                        "signal": f"long_{quote}_short_{base}",
                        "carry": carry,
                        "confidence": 0.50,
                        "reasoning": f"Positive carry of {carry:.2%} favors {quote}"
                    })
        
        # Commodity storage carry
        for symbol in ["CL", "NG", "GC"]:
            if symbol in market_data:
                data = market_data[symbol]
                if not data.empty:
                    # Simplified carry calculation
                    convenience_yield = 0.02  # Mock
                    storage_cost = 0.01  # Mock
                    risk_free_rate = 0.05
                    
                    net_carry = risk_free_rate + storage_cost - convenience_yield
                    
                    if net_carry > 0.03:
                        signals.append({
                            "strategy": "carry_trade",
                            "signal": f"calendar_spread_{symbol}",
                            "net_carry": net_carry,
                            "confidence": 0.45,
                            "reasoning": f"Positive carry structure in {symbol}"
                        })
        
        return signals
    
    async def _momentum_strategy(self, market_data: Dict[str, pd.DataFrame]) -> List[Dict[str, Any]]:
        """Generate momentum signals"""
        signals = []
        
        for symbol, data in market_data.items():
            if data.empty or len(data) < 30:
                continue
            
            # Calculate momentum indicators
            returns_1m = (data['close'].iloc[-1] / data['close'].iloc[-20] - 1) * 100
            returns_3m = (data['close'].iloc[-1] / data['close'].iloc[-60] - 1) * 100 if len(data) >= 60 else 0
            
            volume_trend = data['volume'].rolling(10).mean().iloc[-1] / data['volume'].rolling(30).mean().iloc[-1] if len(data) >= 30 else 1
            
            # Momentum signals
            if returns_1m > 5 and returns_3m > 10 and volume_trend > 1.2:
                signals.append({
                    "symbol": symbol,
                    "strategy": "momentum",
                    "signal": "buy",
                    "returns_1m": returns_1m,
                    "returns_3m": returns_3m,
                    "volume_trend": volume_trend,
                    "confidence": 0.68,
                    "reasoning": "Strong momentum with volume confirmation"
                })
            
            elif returns_1m < -5 and returns_3m < -10 and volume_trend > 1.2:
                signals.append({
                    "symbol": symbol,
                    "strategy": "momentum",
                    "signal": "sell", 
                    "returns_1m": returns_1m,
                    "returns_3m": returns_3m,
                    "volume_trend": volume_trend,
                    "confidence": 0.68,
                    "reasoning": "Strong negative momentum with volume confirmation"
                })
        
        return signals
    
    async def _pairs_trading_strategy(self, market_data: Dict[str, pd.DataFrame]) -> List[Dict[str, Any]]:
        """Generate pairs trading signals"""
        signals = []
        
        # Define correlated pairs
        pairs = [
            ("ES", "NQ"),  # Equity indices
            ("CL", "RB"),  # Energy products
            ("GC", "SI"),  # Precious metals
        ]
        
        for symbol1, symbol2 in pairs:
            if symbol1 in market_data and symbol2 in market_data:
                data1 = market_data[symbol1]
                data2 = market_data[symbol2]
                
                if data1.empty or data2.empty or len(data1) < 50 or len(data2) < 50:
                    continue
                
                # Calculate spread
                spread = data1['close'] / data2['close']
                spread_mean = spread.rolling(30).mean()
                spread_std = spread.rolling(30).std()
                z_score = (spread - spread_mean) / spread_std
                
                current_z = z_score.iloc[-1]
                
                # Pairs trading signals
                if current_z > 2:  # Spread too wide
                    signals.append({
                        "strategy": "pairs_trading",
                        "signal": f"short_{symbol1}_long_{symbol2}",
                        "z_score": current_z,
                        "confidence": 0.62,
                        "reasoning": f"{symbol1} overvalued relative to {symbol2}"
                    })
                
                elif current_z < -2:  # Spread too narrow
                    signals.append({
                        "strategy": "pairs_trading",
                        "signal": f"long_{symbol1}_short_{symbol2}",
                        "z_score": current_z,
                        "confidence": 0.62,
                        "reasoning": f"{symbol1} undervalued relative to {symbol2}"
                    })
        
        return signals
    
    async def _volatility_breakout_strategy(self, market_data: Dict[str, pd.DataFrame]) -> List[Dict[str, Any]]:
        """Generate volatility breakout signals"""
        signals = []
        
        for symbol, data in market_data.items():
            if data.empty or len(data) < 30:
                continue
            
            # Calculate volatility indicators
            atr = self._calculate_atr(data)
            current_atr = atr.iloc[-1]
            avg_atr = atr.rolling(20).mean().iloc[-1]
            
            # Price range compression
            range_compression = current_atr / avg_atr
            
            current_price = data['close'].iloc[-1]
            high_20 = data['high'].rolling(20).max().iloc[-1]
            low_20 = data['low'].rolling(20).min().iloc[-1]
            
            # Breakout signals
            if range_compression < 0.5:  # Volatility compression
                if current_price > high_20 * 1.01:  # Upside breakout
                    signals.append({
                        "symbol": symbol,
                        "strategy": "volatility_breakout",
                        "signal": "buy",
                        "breakout_level": high_20,
                        "range_compression": range_compression,
                        "confidence": 0.70,
                        "reasoning": "Upside breakout after volatility compression"
                    })
                
                elif current_price < low_20 * 0.99:  # Downside breakout
                    signals.append({
                        "symbol": symbol,
                        "strategy": "volatility_breakout",
                        "signal": "sell",
                        "breakout_level": low_20,
                        "range_compression": range_compression,
                        "confidence": 0.70,
                        "reasoning": "Downside breakout after volatility compression"
                    })
        
        return signals
    
    # Helper methods for technical indicators
    def _calculate_atr(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average True Range"""
        high_low = data['high'] - data['low']
        high_close = np.abs(data['high'] - data['close'].shift())
        low_close = np.abs(data['low'] - data['close'].shift())
        
        true_range = np.maximum(high_low, np.maximum(high_close, low_close))
        return true_range.rolling(period).mean()
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

# Initialize the futures system components
contract_database = FuturesContractDatabase()
pricing_engine = FuturesPricingEngine()
risk_manager = FuturesRiskManager()
strategy_engine = FuturesStrategyEngine()