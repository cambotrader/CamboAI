"""
⚡ OPTIONS TRADING EXECUTION & MANAGEMENT
Real-time options trading, order management, and position monitoring
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Literal, Callable
from datetime import datetime, timedelta
import asyncio
import uuid
import numpy as np
from enum import Enum

from .engine import MarketInputs, VanillaBS
from .strategy_library import OptionsStrategyLibrary, StrategyType
from .greeks_calculator import AdvancedGreeksCalculator
from .payoff_analyzer import OptionsPayoffAnalyzer

class OrderStatus(Enum):
    PENDING = "pending"
    PARTIAL_FILL = "partial_fill"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"

class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"
    BRACKET = "bracket"

@dataclass
class OptionsLeg:
    symbol: str
    option_type: Literal["call", "put"]
    strike: float
    expiry: datetime
    side: Literal["buy", "sell"]
    quantity: int
    price: Optional[float] = None

@dataclass
class OptionsOrder:
    order_id: str
    strategy_name: str
    legs: List[OptionsLeg]
    order_type: OrderType
    status: OrderStatus
    created_at: datetime
    net_premium: Optional[float] = None
    filled_premium: Optional[float] = None
    filled_quantity: int = 0
    stop_loss: Optional[float] = None
    profit_target: Optional[float] = None
    time_in_force: Literal["DAY", "GTC", "IOC", "FOK"] = "DAY"
    broker_order_id: Optional[str] = None

@dataclass
class OptionsPosition:
    position_id: str
    strategy_type: StrategyType
    legs: List[Dict[str, Any]]
    entry_date: datetime
    entry_premium: float
    current_value: float
    unrealized_pnl: float
    realized_pnl: float
    max_profit: Optional[float]
    max_loss: Optional[float]
    theta_decay: float
    delta: float
    gamma: float
    vega: float
    days_held: int
    target_exit_date: Optional[datetime] = None

class OptionsAlert:
    def __init__(self, alert_type: str, message: str, urgency: str, position_id: str = None):
        self.alert_type = alert_type
        self.message = message
        self.urgency = urgency  # low, medium, high, critical
        self.position_id = position_id
        self.timestamp = datetime.now()

class OptionsOrderManager:
    """Complete options order management system"""
    
    def __init__(self):
        self.pending_orders: Dict[str, OptionsOrder] = {}
        self.filled_orders: Dict[str, OptionsOrder] = {}
        self.active_positions: Dict[str, OptionsPosition] = {}
        self.order_callbacks: Dict[str, Callable] = {}
        
    def place_strategy_order(self,
                           strategy_type: StrategyType,
                           underlying_symbol: str,
                           spot_price: float,
                           vol: float,
                           target_dte: int = 30,
                           order_type: OrderType = OrderType.MARKET,
                           custom_strikes: Optional[Dict[str, float]] = None,
                           position_size: int = 1) -> OptionsOrder:
        """Place a complete options strategy order"""
        
        strategy_lib = OptionsStrategyLibrary()
        strategy_config = strategy_lib.get_strategy(strategy_type)
        
        if not strategy_config:
            raise ValueError(f"Unknown strategy type: {strategy_type}")
        
        # Build strategy legs
        expiry_date = datetime.now() + timedelta(days=target_dte)
        expiry_years = target_dte / 365
        
        legs = strategy_lib.build_strategy_legs(
            strategy_type=strategy_type,
            spot=spot_price,
            base_strike=custom_strikes.get('base', spot_price) if custom_strikes else spot_price,
            expiry=expiry_years,
            vol=vol,
            rate=0.05,  # Default risk-free rate
            div_yield=0.0
        )
        
        # Convert to OptionsLeg objects
        options_legs = []
        for leg in legs:
            options_leg = OptionsLeg(
                symbol=f"{underlying_symbol}_{int(leg['strike'])}_{leg['right'][0].upper()}_{expiry_date.strftime('%Y%m%d')}",
                option_type=leg['right'],
                strike=leg['strike'],
                expiry=expiry_date,
                side='buy' if leg.get('side', 'long') == 'long' else 'sell',
                quantity=int(leg.get('qty', 1) * position_size)
            )
            options_legs.append(options_leg)
        
        # Calculate net premium
        net_premium = sum(
            self._estimate_leg_price(leg, spot_price, vol, expiry_years) * 
            leg.quantity * (1 if leg.side == 'buy' else -1)
            for leg in options_legs
        )
        
        # Create order
        order = OptionsOrder(
            order_id=str(uuid.uuid4()),
            strategy_name=strategy_type,
            legs=options_legs,
            order_type=order_type,
            status=OrderStatus.PENDING,
            created_at=datetime.now(),
            net_premium=net_premium
        )
        
        self.pending_orders[order.order_id] = order
        
        # Simulate order processing (replace with real broker integration)
        asyncio.create_task(self._process_order(order))
        
        return order
    
    async def _process_order(self, order: OptionsOrder):
        """Process order (simulate broker execution)"""
        
        # Simulate processing delay
        await asyncio.sleep(0.5)
        
        if order.order_type == OrderType.MARKET:
            # Market orders fill immediately (in simulation)
            order.status = OrderStatus.FILLED
            order.filled_premium = order.net_premium
            order.filled_quantity = sum(leg.quantity for leg in order.legs)
            
            # Move to filled orders
            self.filled_orders[order.order_id] = order
            del self.pending_orders[order.order_id]
            
            # Create position
            await self._create_position_from_order(order)
            
        elif order.order_type == OrderType.LIMIT:
            # Simulate limit order logic
            # For now, assume 80% fill probability
            if np.random.random() < 0.8:
                await asyncio.sleep(2)  # Simulate fill delay
                order.status = OrderStatus.FILLED
                order.filled_premium = order.net_premium
                order.filled_quantity = sum(leg.quantity for leg in order.legs)
                
                self.filled_orders[order.order_id] = order
                del self.pending_orders[order.order_id]
                
                await self._create_position_from_order(order)
            else:
                # Order stays pending
                pass
    
    async def _create_position_from_order(self, order: OptionsOrder):
        """Create options position from filled order"""
        
        position = OptionsPosition(
            position_id=str(uuid.uuid4()),
            strategy_type=order.strategy_name,
            legs=[{
                "symbol": leg.symbol,
                "right": leg.option_type,
                "strike": leg.strike,
                "expiry": (leg.expiry - datetime.now()).days / 365,
                "side": "long" if leg.side == "buy" else "short",
                "qty": leg.quantity,
                "spot": self._get_current_spot(leg.symbol.split('_')[0])  # Extract underlying
            } for leg in order.legs],
            entry_date=datetime.now(),
            entry_premium=order.filled_premium,
            current_value=order.filled_premium,  # Initialize with entry value
            unrealized_pnl=0.0,
            realized_pnl=0.0,
            max_profit=None,
            max_loss=None,
            theta_decay=0.0,
            delta=0.0,
            gamma=0.0,
            vega=0.0,
            days_held=0
        )
        
        self.active_positions[position.position_id] = position
        
        # Calculate initial Greeks
        await self._update_position_metrics(position)
    
    async def _update_position_metrics(self, position: OptionsPosition):
        """Update position Greeks and P&L"""
        
        greeks_calc = AdvancedGreeksCalculator()
        payoff_analyzer = OptionsPayoffAnalyzer()
        
        # Calculate current Greeks
        greeks_analysis = greeks_calc.calculate_all_greeks(position.legs)
        
        position.delta = greeks_analysis.portfolio_greeks.delta
        position.gamma = greeks_analysis.portfolio_greeks.gamma
        position.theta = greeks_analysis.portfolio_greeks.theta
        position.vega = greeks_analysis.portfolio_greeks.vega
        
        # Calculate current value and P&L
        current_spot = self._get_current_spot(position.legs[0]["symbol"].split('_')[0])
        
        # Update spot prices in legs
        for leg in position.legs:
            leg["spot"] = current_spot
        
        # Calculate current position value
        current_value = sum(
            self._calculate_leg_value(leg) * leg.get('qty', 1) * 
            (1 if leg.get('side', 'long') == 'long' else -1)
            for leg in position.legs
        )
        
        position.current_value = current_value
        position.unrealized_pnl = current_value - position.entry_premium
        position.days_held = (datetime.now() - position.entry_date).days
        
        # Calculate payoff analysis
        payoff_analysis = payoff_analyzer.analyze_strategy_payoff(
            position.legs, current_spot, at_expiration=False
        )
        position.max_profit = payoff_analysis.max_profit
        position.max_loss = payoff_analysis.max_loss
    
    def _estimate_leg_price(self, leg: OptionsLeg, spot: float, vol: float, time_to_expiry: float) -> float:
        """Estimate option price for leg"""
        
        inputs = MarketInputs(
            spot=spot,
            strike=leg.strike,
            rate=0.05,
            div_yield=0.0,
            vol=vol,
            t=time_to_expiry
        )
        
        result = VanillaBS.price(inputs, leg.option_type)
        return result.price
    
    def _calculate_leg_value(self, leg: Dict[str, Any]) -> float:
        """Calculate current value of option leg"""
        
        inputs = MarketInputs(
            spot=leg["spot"],
            strike=leg["strike"],
            rate=leg.get("rate", 0.05),
            div_yield=leg.get("div_yield", 0.0),
            vol=leg.get("vol", 0.20),
            t=leg.get("expiry", 0.0833)
        )
        
        result = VanillaBS.price(inputs, leg["right"])
        return result.price
    
    def _get_current_spot(self, symbol: str) -> float:
        """Get current spot price (mock implementation)"""
        # In real implementation, this would fetch from market data feed
        return 100.0  # Mock price
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel pending order"""
        
        if order_id in self.pending_orders:
            order = self.pending_orders[order_id]
            order.status = OrderStatus.CANCELLED
            del self.pending_orders[order_id]
            return True
        return False
    
    def close_position(self, position_id: str, close_type: Literal["market", "limit"] = "market") -> OptionsOrder:
        """Close existing position"""
        
        if position_id not in self.active_positions:
            raise ValueError(f"Position {position_id} not found")
        
        position = self.active_positions[position_id]
        
        # Create closing order (reverse of opening legs)
        closing_legs = []
        for leg_data in position.legs:
            # Reverse the side
            original_side = leg_data.get("side", "long")
            closing_side = "sell" if original_side == "long" else "buy"
            
            closing_leg = OptionsLeg(
                symbol=leg_data["symbol"],
                option_type=leg_data["right"],
                strike=leg_data["strike"],
                expiry=datetime.now() + timedelta(days=leg_data["expiry"] * 365),
                side=closing_side,
                quantity=leg_data.get("qty", 1)
            )
            closing_legs.append(closing_leg)
        
        # Create closing order
        closing_order = OptionsOrder(
            order_id=str(uuid.uuid4()),
            strategy_name=f"CLOSE_{position.strategy_type}",
            legs=closing_legs,
            order_type=OrderType.MARKET if close_type == "market" else OrderType.LIMIT,
            status=OrderStatus.PENDING,
            created_at=datetime.now()
        )
        
        self.pending_orders[closing_order.order_id] = closing_order
        
        # Process closing order
        asyncio.create_task(self._process_closing_order(closing_order, position_id))
        
        return closing_order
    
    async def _process_closing_order(self, order: OptionsOrder, position_id: str):
        """Process closing order and remove position"""
        
        await asyncio.sleep(0.5)  # Simulate processing
        
        order.status = OrderStatus.FILLED
        order.filled_premium = sum(leg.price or 0 for leg in order.legs)
        
        # Calculate realized P&L
        position = self.active_positions[position_id]
        closing_value = order.filled_premium
        position.realized_pnl = closing_value - position.entry_premium
        
        # Remove from active positions
        del self.active_positions[position_id]
        
        # Move order to filled
        self.filled_orders[order.order_id] = order
        del self.pending_orders[order.order_id]

class OptionsPortfolioMonitor:
    """Real-time options portfolio monitoring and alerts"""
    
    def __init__(self, order_manager: OptionsOrderManager):
        self.order_manager = order_manager
        self.alerts: List[OptionsAlert] = []
        self.risk_thresholds = {
            "max_portfolio_delta": 100,
            "max_portfolio_gamma": 50,
            "max_daily_theta": -100,
            "max_position_loss_pct": 0.5,  # 50% loss
            "dte_warning_threshold": 7,  # Days to expiration
            "vol_expansion_threshold": 0.25  # 25% vol increase
        }
    
    async def monitor_portfolio(self):
        """Continuous portfolio monitoring"""
        
        while True:
            await self._check_portfolio_risks()
            await self._check_position_alerts()
            await self._check_expiration_alerts()
            await asyncio.sleep(60)  # Check every minute
    
    async def _check_portfolio_risks(self):
        """Check portfolio-level risk metrics"""
        
        if not self.order_manager.active_positions:
            return
        
        # Calculate portfolio Greeks
        total_delta = sum(pos.delta for pos in self.order_manager.active_positions.values())
        total_gamma = sum(pos.gamma for pos in self.order_manager.active_positions.values())
        total_theta = sum(pos.theta for pos in self.order_manager.active_positions.values())
        total_vega = sum(pos.vega for pos in self.order_manager.active_positions.values())
        
        # Check delta risk
        if abs(total_delta) > self.risk_thresholds["max_portfolio_delta"]:
            self._create_alert(
                "portfolio_delta_risk",
                f"Portfolio delta exposure: {total_delta:.1f} (threshold: ±{self.risk_thresholds['max_portfolio_delta']})",
                "high"
            )
        
        # Check gamma risk
        if abs(total_gamma) > self.risk_thresholds["max_portfolio_gamma"]:
            self._create_alert(
                "portfolio_gamma_risk",
                f"Portfolio gamma exposure: {total_gamma:.1f} (threshold: ±{self.risk_thresholds['max_portfolio_gamma']})",
                "medium"
            )
        
        # Check theta decay
        if total_theta < self.risk_thresholds["max_daily_theta"]:
            self._create_alert(
                "portfolio_theta_decay",
                f"Daily theta decay: ${total_theta:.2f} (threshold: ${self.risk_thresholds['max_daily_theta']})",
                "medium"
            )
    
    async def _check_position_alerts(self):
        """Check individual position alerts"""
        
        for position_id, position in self.order_manager.active_positions.items():
            await self.order_manager._update_position_metrics(position)
            
            # Check for large losses
            loss_pct = position.unrealized_pnl / abs(position.entry_premium) if position.entry_premium != 0 else 0
            if loss_pct <= -self.risk_thresholds["max_position_loss_pct"]:
                self._create_alert(
                    "position_large_loss",
                    f"Position {position.strategy_type} down {loss_pct:.1%} (${position.unrealized_pnl:.2f})",
                    "critical",
                    position_id
                )
            
            # Check for high theta positions approaching expiration
            min_expiry = min(leg.get("expiry", 1) for leg in position.legs)
            days_to_expiry = min_expiry * 365
            
            if days_to_expiry <= self.risk_thresholds["dte_warning_threshold"] and position.theta < -10:
                self._create_alert(
                    "expiration_theta_warning",
                    f"Position {position.strategy_type} expires in {days_to_expiry:.0f} days with theta ${position.theta:.2f}",
                    "high",
                    position_id
                )
    
    async def _check_expiration_alerts(self):
        """Check for approaching expirations"""
        
        for position_id, position in self.order_manager.active_positions.items():
            min_expiry = min(leg.get("expiry", 1) for leg in position.legs)
            days_to_expiry = min_expiry * 365
            
            if days_to_expiry <= 1:
                self._create_alert(
                    "expiration_tomorrow",
                    f"Position {position.strategy_type} expires tomorrow!",
                    "critical",
                    position_id
                )
            elif days_to_expiry <= 3:
                self._create_alert(
                    "expiration_soon",
                    f"Position {position.strategy_type} expires in {days_to_expiry:.0f} days",
                    "high",
                    position_id
                )
    
    def _create_alert(self, alert_type: str, message: str, urgency: str, position_id: str = None):
        """Create new alert if not duplicate"""
        
        # Check for duplicate alerts (same type and position in last hour)
        recent_alerts = [
            alert for alert in self.alerts 
            if alert.alert_type == alert_type and 
               alert.position_id == position_id and
               (datetime.now() - alert.timestamp).seconds < 3600
        ]
        
        if not recent_alerts:
            alert = OptionsAlert(alert_type, message, urgency, position_id)
            self.alerts.append(alert)
            
            # Limit alert history
            self.alerts = self.alerts[-100:]  # Keep last 100 alerts
    
    def get_active_alerts(self, urgency_filter: str = None) -> List[OptionsAlert]:
        """Get active alerts, optionally filtered by urgency"""
        
        if urgency_filter:
            return [alert for alert in self.alerts if alert.urgency == urgency_filter]
        return self.alerts.copy()

class OptionsStrategyRecommendationEngine:
    """AI-powered options strategy recommendations"""
    
    def __init__(self):
        self.strategy_lib = OptionsStrategyLibrary()
        self.greeks_calc = AdvancedGreeksCalculator()
    
    def recommend_strategies(self,
                           market_conditions: Dict[str, Any],
                           risk_tolerance: Literal["conservative", "moderate", "aggressive"],
                           account_size: float,
                           current_positions: List[OptionsPosition] = None) -> List[Dict[str, Any]]:
        """Generate options strategy recommendations"""
        
        spot = market_conditions.get("spot", 100)
        vol = market_conditions.get("vol", 0.20)
        vol_rank = market_conditions.get("vol_rank", 50)  # Percentile
        trend = market_conditions.get("trend", "neutral")  # bullish, bearish, neutral
        days_to_earnings = market_conditions.get("days_to_earnings", None)
        
        recommendations = []
        
        # High volatility strategies
        if vol_rank > 70:  # High vol environment
            if trend == "neutral":
                recommendations.append(self._create_recommendation(
                    "iron_condor",
                    "High volatility + neutral trend = Iron Condor opportunity",
                    "Sell premium in high vol environment with range-bound expectation",
                    {"confidence": 0.8, "max_allocation": 0.15}
                ))
                
                recommendations.append(self._create_recommendation(
                    "short_strangle",
                    "High volatility range-bound play",
                    "Collect premium from elevated volatility with neutral bias",
                    {"confidence": 0.75, "max_allocation": 0.10}
                ))
        
        # Low volatility strategies
        elif vol_rank < 30:  # Low vol environment
            if trend == "bullish":
                recommendations.append(self._create_recommendation(
                    "bull_call_spread",
                    "Low volatility bullish play",
                    "Defined risk bullish strategy in low vol environment",
                    {"confidence": 0.7, "max_allocation": 0.20}
                ))
            elif trend == "bearish":
                recommendations.append(self._create_recommendation(
                    "bear_put_spread",
                    "Low volatility bearish play", 
                    "Defined risk bearish strategy in low vol environment",
                    {"confidence": 0.7, "max_allocation": 0.20}
                ))
        
        # Earnings plays
        if days_to_earnings and days_to_earnings <= 7:
            if vol_rank < 50:  # Vol hasn't expanded yet
                recommendations.append(self._create_recommendation(
                    "long_straddle",
                    "Pre-earnings volatility expansion play",
                    "Buy volatility before earnings announcement",
                    {"confidence": 0.6, "max_allocation": 0.05}
                ))
        
        # Portfolio hedging
        if current_positions:
            portfolio_delta = sum(pos.delta for pos in current_positions)
            if abs(portfolio_delta) > 50:
                hedge_strategy = "short_call" if portfolio_delta > 50 else "short_put"
                recommendations.append(self._create_recommendation(
                    hedge_strategy,
                    f"Portfolio delta hedge ({portfolio_delta:.0f} delta exposure)",
                    "Hedge existing portfolio delta exposure",
                    {"confidence": 0.9, "max_allocation": 0.10}
                ))
        
        # Risk tolerance adjustments
        recommendations = self._adjust_for_risk_tolerance(recommendations, risk_tolerance)
        
        # Sort by confidence
        recommendations.sort(key=lambda x: x["analysis"]["confidence"], reverse=True)
        
        return recommendations[:5]  # Return top 5
    
    def _create_recommendation(self, strategy_type: str, title: str, description: str, analysis: Dict) -> Dict[str, Any]:
        """Create structured recommendation"""
        
        strategy_config = self.strategy_lib.get_strategy(strategy_type)
        
        return {
            "strategy_type": strategy_type,
            "title": title,
            "description": description,
            "strategy_config": strategy_config,
            "analysis": analysis,
            "market_outlook": strategy_config.market_outlook if strategy_config else "Unknown",
            "risk_level": self._assess_risk_level(strategy_type),
            "estimated_probability": analysis.get("confidence", 0.5)
        }
    
    def _adjust_for_risk_tolerance(self, recommendations: List[Dict], risk_tolerance: str) -> List[Dict]:
        """Adjust recommendations based on risk tolerance"""
        
        if risk_tolerance == "conservative":
            # Filter out high-risk strategies and reduce allocations
            filtered = [r for r in recommendations if r["risk_level"] in ["low", "medium"]]
            for rec in filtered:
                rec["analysis"]["max_allocation"] *= 0.5
            return filtered
        
        elif risk_tolerance == "aggressive":
            # Increase allocations and include high-risk strategies
            for rec in recommendations:
                rec["analysis"]["max_allocation"] *= 1.5
            return recommendations
        
        return recommendations  # Moderate - no changes
    
    def _assess_risk_level(self, strategy_type: str) -> str:
        """Assess risk level of strategy"""
        
        high_risk_strategies = ["short_call", "short_put", "short_straddle", "short_strangle", "call_backspread"]
        low_risk_strategies = ["long_call", "long_put", "bull_call_spread", "bear_put_spread", "iron_butterfly"]
        
        if strategy_type in high_risk_strategies:
            return "high"
        elif strategy_type in low_risk_strategies:
            return "low"
        else:
            return "medium"

# Initialize the trading manager components
order_manager = OptionsOrderManager()
portfolio_monitor = OptionsPortfolioMonitor(order_manager)
strategy_recommender = OptionsStrategyRecommendationEngine()"""
⚡ OPTIONS TRADING EXECUTION & MANAGEMENT
Real-time options trading, order management, and position monitoring
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Literal, Callable
from datetime import datetime, timedelta
import asyncio
import uuid
import numpy as np
from enum import Enum

from .engine import MarketInputs, VanillaBS
from .strategy_library import OptionsStrategyLibrary, StrategyType
from .greeks_calculator import AdvancedGreeksCalculator
from .payoff_analyzer import OptionsPayoffAnalyzer

class OrderStatus(Enum):
    PENDING = "pending"
    PARTIAL_FILL = "partial_fill"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"

class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"
    BRACKET = "bracket"

@dataclass
class OptionsLeg:
    symbol: str
    option_type: Literal["call", "put"]
    strike: float
    expiry: datetime
    side: Literal["buy", "sell"]
    quantity: int
    price: Optional[float] = None

@dataclass
class OptionsOrder:
    order_id: str
    strategy_name: str
    legs: List[OptionsLeg]
    order_type: OrderType
    status: OrderStatus
    created_at: datetime
    net_premium: Optional[float] = None
    filled_premium: Optional[float] = None
    filled_quantity: int = 0
    stop_loss: Optional[float] = None
    profit_target: Optional[float] = None
    time_in_force: Literal["DAY", "GTC", "IOC", "FOK"] = "DAY"
    broker_order_id: Optional[str] = None

@dataclass
class OptionsPosition:
    position_id: str
    strategy_type: StrategyType
    legs: List[Dict[str, Any]]
    entry_date: datetime
    entry_premium: float
    current_value: float
    unrealized_pnl: float
    realized_pnl: float
    max_profit: Optional[float]
    max_loss: Optional[float]
    theta_decay: float
    delta: float
    gamma: float
    vega: float
    days_held: int
    target_exit_date: Optional[datetime] = None

class OptionsAlert:
    def __init__(self, alert_type: str, message: str, urgency: str, position_id: str = None):
        self.alert_type = alert_type
        self.message = message
        self.urgency = urgency  # low, medium, high, critical
        self.position_id = position_id
        self.timestamp = datetime.now()

class OptionsOrderManager:
    """Complete options order management system"""
    
    def __init__(self):
        self.pending_orders: Dict[str, OptionsOrder] = {}
        self.filled_orders: Dict[str, OptionsOrder] = {}
        self.active_positions: Dict[str, OptionsPosition] = {}
        self.order_callbacks: Dict[str, Callable] = {}
        
    def place_strategy_order(self,
                           strategy_type: StrategyType,
                           underlying_symbol: str,
                           spot_price: float,
                           vol: float,
                           target_dte: int = 30,
                           order_type: OrderType = OrderType.MARKET,
                           custom_strikes: Optional[Dict[str, float]] = None,
                           position_size: int = 1) -> OptionsOrder:
        """Place a complete options strategy order"""
        
        strategy_lib = OptionsStrategyLibrary()
        strategy_config = strategy_lib.get_strategy(strategy_type)
        
        if not strategy_config:
            raise ValueError(f"Unknown strategy type: {strategy_type}")
        
        # Build strategy legs
        expiry_date = datetime.now() + timedelta(days=target_dte)
        expiry_years = target_dte / 365
        
        legs = strategy_lib.build_strategy_legs(
            strategy_type=strategy_type,
            spot=spot_price,
            base_strike=custom_strikes.get('base', spot_price) if custom_strikes else spot_price,
            expiry=expiry_years,
            vol=vol,
            rate=0.05,  # Default risk-free rate
            div_yield=0.0
        )
        
        # Convert to OptionsLeg objects
        options_legs = []
        for leg in legs:
            options_leg = OptionsLeg(
                symbol=f"{underlying_symbol}_{int(leg['strike'])}_{leg['right'][0].upper()}_{expiry_date.strftime('%Y%m%d')}",
                option_type=leg['right'],
                strike=leg['strike'],
                expiry=expiry_date,
                side='buy' if leg.get('side', 'long') == 'long' else 'sell',
                quantity=int(leg.get('qty', 1) * position_size)
            )
            options_legs.append(options_leg)
        
        # Calculate net premium
        net_premium = sum(
            self._estimate_leg_price(leg, spot_price, vol, expiry_years) * 
            leg.quantity * (1 if leg.side == 'buy' else -1)
            for leg in options_legs
        )
        
        # Create order
        order = OptionsOrder(
            order_id=str(uuid.uuid4()),
            strategy_name=strategy_type,
            legs=options_legs,
            order_type=order_type,
            status=OrderStatus.PENDING,
            created_at=datetime.now(),
            net_premium=net_premium
        )
        
        self.pending_orders[order.order_id] = order
        
        # Simulate order processing (replace with real broker integration)
        asyncio.create_task(self._process_order(order))
        
        return order
    
    async def _process_order(self, order: OptionsOrder):
        """Process order (simulate broker execution)"""
        
        # Simulate processing delay
        await asyncio.sleep(0.5)
        
        if order.order_type == OrderType.MARKET:
            # Market orders fill immediately (in simulation)
            order.status = OrderStatus.FILLED
            order.filled_premium = order.net_premium
            order.filled_quantity = sum(leg.quantity for leg in order.legs)
            
            # Move to filled orders
            self.filled_orders[order.order_id] = order
            del self.pending_orders[order.order_id]
            
            # Create position
            await self._create_position_from_order(order)
            
        elif order.order_type == OrderType.LIMIT:
            # Simulate limit order logic
            # For now, assume 80% fill probability
            if np.random.random() < 0.8:
                await asyncio.sleep(2)  # Simulate fill delay
                order.status = OrderStatus.FILLED
                order.filled_premium = order.net_premium
                order.filled_quantity = sum(leg.quantity for leg in order.legs)
                
                self.filled_orders[order.order_id] = order
                del self.pending_orders[order.order_id]
                
                await self._create_position_from_order(order)
            else:
                # Order stays pending
                pass
    
    async def _create_position_from_order(self, order: OptionsOrder):
        """Create options position from filled order"""
        
        position = OptionsPosition(
            position_id=str(uuid.uuid4()),
            strategy_type=order.strategy_name,
            legs=[{
                "symbol": leg.symbol,
                "right": leg.option_type,
                "strike": leg.strike,
                "expiry": (leg.expiry - datetime.now()).days / 365,
                "side": "long" if leg.side == "buy" else "short",
                "qty": leg.quantity,
                "spot": self._get_current_spot(leg.symbol.split('_')[0])  # Extract underlying
            } for leg in order.legs],
            entry_date=datetime.now(),
            entry_premium=order.filled_premium,
            current_value=order.filled_premium,  # Initialize with entry value
            unrealized_pnl=0.0,
            realized_pnl=0.0,
            max_profit=None,
            max_loss=None,
            theta_decay=0.0,
            delta=0.0,
            gamma=0.0,
            vega=0.0,
            days_held=0
        )
        
        self.active_positions[position.position_id] = position
        
        # Calculate initial Greeks
        await self._update_position_metrics(position)
    
    async def _update_position_metrics(self, position: OptionsPosition):
        """Update position Greeks and P&L"""
        
        greeks_calc = AdvancedGreeksCalculator()
        payoff_analyzer = OptionsPayoffAnalyzer()
        
        # Calculate current Greeks
        greeks_analysis = greeks_calc.calculate_all_greeks(position.legs)
        
        position.delta = greeks_analysis.portfolio_greeks.delta
        position.gamma = greeks_analysis.portfolio_greeks.gamma
        position.theta = greeks_analysis.portfolio_greeks.theta
        position.vega = greeks_analysis.portfolio_greeks.vega
        
        # Calculate current value and P&L
        current_spot = self._get_current_spot(position.legs[0]["symbol"].split('_')[0])
        
        # Update spot prices in legs
        for leg in position.legs:
            leg["spot"] = current_spot
        
        # Calculate current position value
        current_value = sum(
            self._calculate_leg_value(leg) * leg.get('qty', 1) * 
            (1 if leg.get('side', 'long') == 'long' else -1)
            for leg in position.legs
        )
        
        position.current_value = current_value
        position.unrealized_pnl = current_value - position.entry_premium
        position.days_held = (datetime.now() - position.entry_date).days
        
        # Calculate payoff analysis
        payoff_analysis = payoff_analyzer.analyze_strategy_payoff(
            position.legs, current_spot, at_expiration=False
        )
        position.max_profit = payoff_analysis.max_profit
        position.max_loss = payoff_analysis.max_loss
    
    def _estimate_leg_price(self, leg: OptionsLeg, spot: float, vol: float, time_to_expiry: float) -> float:
        """Estimate option price for leg"""
        
        inputs = MarketInputs(
            spot=spot,
            strike=leg.strike,
            rate=0.05,
            div_yield=0.0,
            vol=vol,
            t=time_to_expiry
        )
        
        result = VanillaBS.price(inputs, leg.option_type)
        return result.price
    
    def _calculate_leg_value(self, leg: Dict[str, Any]) -> float:
        """Calculate current value of option leg"""
        
        inputs = MarketInputs(
            spot=leg["spot"],
            strike=leg["strike"],
            rate=leg.get("rate", 0.05),
            div_yield=leg.get("div_yield", 0.0),
            vol=leg.get("vol", 0.20),
            t=leg.get("expiry", 0.0833)
        )
        
        result = VanillaBS.price(inputs, leg["right"])
        return result.price
    
    def _get_current_spot(self, symbol: str) -> float:
        """Get current spot price (mock implementation)"""
        # In real implementation, this would fetch from market data feed
        return 100.0  # Mock price
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel pending order"""
        
        if order_id in self.pending_orders:
            order = self.pending_orders[order_id]
            order.status = OrderStatus.CANCELLED
            del self.pending_orders[order_id]
            return True
        return False
    
    def close_position(self, position_id: str, close_type: Literal["market", "limit"] = "market") -> OptionsOrder:
        """Close existing position"""
        
        if position_id not in self.active_positions:
            raise ValueError(f"Position {position_id} not found")
        
        position = self.active_positions[position_id]
        
        # Create closing order (reverse of opening legs)
        closing_legs = []
        for leg_data in position.legs:
            # Reverse the side
            original_side = leg_data.get("side", "long")
            closing_side = "sell" if original_side == "long" else "buy"
            
            closing_leg = OptionsLeg(
                symbol=leg_data["symbol"],
                option_type=leg_data["right"],
                strike=leg_data["strike"],
                expiry=datetime.now() + timedelta(days=leg_data["expiry"] * 365),
                side=closing_side,
                quantity=leg_data.get("qty", 1)
            )
            closing_legs.append(closing_leg)
        
        # Create closing order
        closing_order = OptionsOrder(
            order_id=str(uuid.uuid4()),
            strategy_name=f"CLOSE_{position.strategy_type}",
            legs=closing_legs,
            order_type=OrderType.MARKET if close_type == "market" else OrderType.LIMIT,
            status=OrderStatus.PENDING,
            created_at=datetime.now()
        )
        
        self.pending_orders[closing_order.order_id] = closing_order
        
        # Process closing order
        asyncio.create_task(self._process_closing_order(closing_order, position_id))
        
        return closing_order
    
    async def _process_closing_order(self, order: OptionsOrder, position_id: str):
        """Process closing order and remove position"""
        
        await asyncio.sleep(0.5)  # Simulate processing
        
        order.status = OrderStatus.FILLED
        order.filled_premium = sum(leg.price or 0 for leg in order.legs)
        
        # Calculate realized P&L
        position = self.active_positions[position_id]
        closing_value = order.filled_premium
        position.realized_pnl = closing_value - position.entry_premium
        
        # Remove from active positions
        del self.active_positions[position_id]
        
        # Move order to filled
        self.filled_orders[order.order_id] = order
        del self.pending_orders[order.order_id]

class OptionsPortfolioMonitor:
    """Real-time options portfolio monitoring and alerts"""
    
    def __init__(self, order_manager: OptionsOrderManager):
        self.order_manager = order_manager
        self.alerts: List[OptionsAlert] = []
        self.risk_thresholds = {
            "max_portfolio_delta": 100,
            "max_portfolio_gamma": 50,
            "max_daily_theta": -100,
            "max_position_loss_pct": 0.5,  # 50% loss
            "dte_warning_threshold": 7,  # Days to expiration
            "vol_expansion_threshold": 0.25  # 25% vol increase
        }
    
    async def monitor_portfolio(self):
        """Continuous portfolio monitoring"""
        
        while True:
            await self._check_portfolio_risks()
            await self._check_position_alerts()
            await self._check_expiration_alerts()
            await asyncio.sleep(60)  # Check every minute
    
    async def _check_portfolio_risks(self):
        """Check portfolio-level risk metrics"""
        
        if not self.order_manager.active_positions:
            return
        
        # Calculate portfolio Greeks
        total_delta = sum(pos.delta for pos in self.order_manager.active_positions.values())
        total_gamma = sum(pos.gamma for pos in self.order_manager.active_positions.values())
        total_theta = sum(pos.theta for pos in self.order_manager.active_positions.values())
        total_vega = sum(pos.vega for pos in self.order_manager.active_positions.values())
        
        # Check delta risk
        if abs(total_delta) > self.risk_thresholds["max_portfolio_delta"]:
            self._create_alert(
                "portfolio_delta_risk",
                f"Portfolio delta exposure: {total_delta:.1f} (threshold: ±{self.risk_thresholds['max_portfolio_delta']})",
                "high"
            )
        
        # Check gamma risk
        if abs(total_gamma) > self.risk_thresholds["max_portfolio_gamma"]:
            self._create_alert(
                "portfolio_gamma_risk",
                f"Portfolio gamma exposure: {total_gamma:.1f} (threshold: ±{self.risk_thresholds['max_portfolio_gamma']})",
                "medium"
            )
        
        # Check theta decay
        if total_theta < self.risk_thresholds["max_daily_theta"]:
            self._create_alert(
                "portfolio_theta_decay",
                f"Daily theta decay: ${total_theta:.2f} (threshold: ${self.risk_thresholds['max_daily_theta']})",
                "medium"
            )
    
    async def _check_position_alerts(self):
        """Check individual position alerts"""
        
        for position_id, position in self.order_manager.active_positions.items():
            await self.order_manager._update_position_metrics(position)
            
            # Check for large losses
            loss_pct = position.unrealized_pnl / abs(position.entry_premium) if position.entry_premium != 0 else 0
            if loss_pct <= -self.risk_thresholds["max_position_loss_pct"]:
                self._create_alert(
                    "position_large_loss",
                    f"Position {position.strategy_type} down {loss_pct:.1%} (${position.unrealized_pnl:.2f})",
                    "critical",
                    position_id
                )
            
            # Check for high theta positions approaching expiration
            min_expiry = min(leg.get("expiry", 1) for leg in position.legs)
            days_to_expiry = min_expiry * 365
            
            if days_to_expiry <= self.risk_thresholds["dte_warning_threshold"] and position.theta < -10:
                self._create_alert(
                    "expiration_theta_warning",
                    f"Position {position.strategy_type} expires in {days_to_expiry:.0f} days with theta ${position.theta:.2f}",
                    "high",
                    position_id
                )
    
    async def _check_expiration_alerts(self):
        """Check for approaching expirations"""
        
        for position_id, position in self.order_manager.active_positions.items():
            min_expiry = min(leg.get("expiry", 1) for leg in position.legs)
            days_to_expiry = min_expiry * 365
            
            if days_to_expiry <= 1:
                self._create_alert(
                    "expiration_tomorrow",
                    f"Position {position.strategy_type} expires tomorrow!",
                    "critical",
                    position_id
                )
            elif days_to_expiry <= 3:
                self._create_alert(
                    "expiration_soon",
                    f"Position {position.strategy_type} expires in {days_to_expiry:.0f} days",
                    "high",
                    position_id
                )
    
    def _create_alert(self, alert_type: str, message: str, urgency: str, position_id: str = None):
        """Create new alert if not duplicate"""
        
        # Check for duplicate alerts (same type and position in last hour)
        recent_alerts = [
            alert for alert in self.alerts 
            if alert.alert_type == alert_type and 
               alert.position_id == position_id and
               (datetime.now() - alert.timestamp).seconds < 3600
        ]
        
        if not recent_alerts:
            alert = OptionsAlert(alert_type, message, urgency, position_id)
            self.alerts.append(alert)
            
            # Limit alert history
            self.alerts = self.alerts[-100:]  # Keep last 100 alerts
    
    def get_active_alerts(self, urgency_filter: str = None) -> List[OptionsAlert]:
        """Get active alerts, optionally filtered by urgency"""
        
        if urgency_filter:
            return [alert for alert in self.alerts if alert.urgency == urgency_filter]
        return self.alerts.copy()

class OptionsStrategyRecommendationEngine:
    """AI-powered options strategy recommendations"""
    
    def __init__(self):
        self.strategy_lib = OptionsStrategyLibrary()
        self.greeks_calc = AdvancedGreeksCalculator()
    
    def recommend_strategies(self,
                           market_conditions: Dict[str, Any],
                           risk_tolerance: Literal["conservative", "moderate", "aggressive"],
                           account_size: float,
                           current_positions: List[OptionsPosition] = None) -> List[Dict[str, Any]]:
        """Generate options strategy recommendations"""
        
        spot = market_conditions.get("spot", 100)
        vol = market_conditions.get("vol", 0.20)
        vol_rank = market_conditions.get("vol_rank", 50)  # Percentile
        trend = market_conditions.get("trend", "neutral")  # bullish, bearish, neutral
        days_to_earnings = market_conditions.get("days_to_earnings", None)
        
        recommendations = []
        
        # High volatility strategies
        if vol_rank > 70:  # High vol environment
            if trend == "neutral":
                recommendations.append(self._create_recommendation(
                    "iron_condor",
                    "High volatility + neutral trend = Iron Condor opportunity",
                    "Sell premium in high vol environment with range-bound expectation",
                    {"confidence": 0.8, "max_allocation": 0.15}
                ))
                
                recommendations.append(self._create_recommendation(
                    "short_strangle",
                    "High volatility range-bound play",
                    "Collect premium from elevated volatility with neutral bias",
                    {"confidence": 0.75, "max_allocation": 0.10}
                ))
        
        # Low volatility strategies
        elif vol_rank < 30:  # Low vol environment
            if trend == "bullish":
                recommendations.append(self._create_recommendation(
                    "bull_call_spread",
                    "Low volatility bullish play",
                    "Defined risk bullish strategy in low vol environment",
                    {"confidence": 0.7, "max_allocation": 0.20}
                ))
            elif trend == "bearish":
                recommendations.append(self._create_recommendation(
                    "bear_put_spread",
                    "Low volatility bearish play", 
                    "Defined risk bearish strategy in low vol environment",
                    {"confidence": 0.7, "max_allocation": 0.20}
                ))
        
        # Earnings plays
        if days_to_earnings and days_to_earnings <= 7:
            if vol_rank < 50:  # Vol hasn't expanded yet
                recommendations.append(self._create_recommendation(
                    "long_straddle",
                    "Pre-earnings volatility expansion play",
                    "Buy volatility before earnings announcement",
                    {"confidence": 0.6, "max_allocation": 0.05}
                ))
        
        # Portfolio hedging
        if current_positions:
            portfolio_delta = sum(pos.delta for pos in current_positions)
            if abs(portfolio_delta) > 50:
                hedge_strategy = "short_call" if portfolio_delta > 50 else "short_put"
                recommendations.append(self._create_recommendation(
                    hedge_strategy,
                    f"Portfolio delta hedge ({portfolio_delta:.0f} delta exposure)",
                    "Hedge existing portfolio delta exposure",
                    {"confidence": 0.9, "max_allocation": 0.10}
                ))
        
        # Risk tolerance adjustments
        recommendations = self._adjust_for_risk_tolerance(recommendations, risk_tolerance)
        
        # Sort by confidence
        recommendations.sort(key=lambda x: x["analysis"]["confidence"], reverse=True)
        
        return recommendations[:5]  # Return top 5
    
    def _create_recommendation(self, strategy_type: str, title: str, description: str, analysis: Dict) -> Dict[str, Any]:
        """Create structured recommendation"""
        
        strategy_config = self.strategy_lib.get_strategy(strategy_type)
        
        return {
            "strategy_type": strategy_type,
            "title": title,
            "description": description,
            "strategy_config": strategy_config,
            "analysis": analysis,
            "market_outlook": strategy_config.market_outlook if strategy_config else "Unknown",
            "risk_level": self._assess_risk_level(strategy_type),
            "estimated_probability": analysis.get("confidence", 0.5)
        }
    
    def _adjust_for_risk_tolerance(self, recommendations: List[Dict], risk_tolerance: str) -> List[Dict]:
        """Adjust recommendations based on risk tolerance"""
        
        if risk_tolerance == "conservative":
            # Filter out high-risk strategies and reduce allocations
            filtered = [r for r in recommendations if r["risk_level"] in ["low", "medium"]]
            for rec in filtered:
                rec["analysis"]["max_allocation"] *= 0.5
            return filtered
        
        elif risk_tolerance == "aggressive":
            # Increase allocations and include high-risk strategies
            for rec in recommendations:
                rec["analysis"]["max_allocation"] *= 1.5
            return recommendations
        
        return recommendations  # Moderate - no changes
    
    def _assess_risk_level(self, strategy_type: str) -> str:
        """Assess risk level of strategy"""
        
        high_risk_strategies = ["short_call", "short_put", "short_straddle", "short_strangle", "call_backspread"]
        low_risk_strategies = ["long_call", "long_put", "bull_call_spread", "bear_put_spread", "iron_butterfly"]
        
        if strategy_type in high_risk_strategies:
            return "high"
        elif strategy_type in low_risk_strategies:
            return "low"
        else:
            return "medium"

# Initialize the trading manager components
order_manager = OptionsOrderManager()
portfolio_monitor = OptionsPortfolioMonitor(order_manager)
strategy_recommender = OptionsStrategyRecommendationEngine()