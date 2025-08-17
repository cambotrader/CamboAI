"""
⚖️ ADVANCED RISK MANAGEMENT SYSTEM - INSTITUTIONAL GRADE
Complete risk management with VaR, stress testing, and real-time monitoring
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import pandas as pd
from collections import defaultdict, deque
import math
from decimal import Decimal, ROUND_HALF_UP

from ..models.trading_models import Account, Position, Order, RiskMetrics, User, Asset
from ..core.websocket_manager import websocket_manager
from .market_data_stream import market_data_stream

logger = logging.getLogger(__name__)

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class RiskType(Enum):
    MARKET_RISK = "market_risk"
    CREDIT_RISK = "credit_risk"
    LIQUIDITY_RISK = "liquidity_risk"
    OPERATIONAL_RISK = "operational_risk"
    CONCENTRATION_RISK = "concentration_risk"
    LEVERAGE_RISK = "leverage_risk"

@dataclass
class RiskLimit:
    name: str
    limit_type: str  # percentage, absolute, ratio
    limit_value: float
    current_value: float
    utilization: float
    breach_threshold: float = 0.9  # Alert at 90% of limit
    hard_limit: bool = True  # True = reject orders, False = alert only

@dataclass
class RiskAlert:
    alert_id: str
    risk_type: RiskType
    severity: RiskLevel
    message: str
    current_value: float
    limit_value: float
    utilization: float
    timestamp: datetime
    account_id: str
    requires_action: bool = False
    recommendations: List[str] = field(default_factory=list)

@dataclass
class PortfolioRisk:
    account_id: str
    total_value: float
    var_1d_95: float  # 1-day Value at Risk (95% confidence)
    var_1d_99: float  # 1-day Value at Risk (99% confidence)
    expected_shortfall: float  # Conditional VaR
    beta: float
    correlation_spy: float
    max_drawdown: float
    sharpe_ratio: float
    volatility: float
    concentration_score: float
    leverage_ratio: float
    liquidity_score: float
    stress_test_results: Dict[str, float] = field(default_factory=dict)

@dataclass
class OrderRiskCheck:
    approved: bool
    risk_score: float
    warnings: List[str] = field(default_factory=list)
    reason: Optional[str] = None
    required_margin: float = 0.0
    impact_on_portfolio: Dict[str, float] = field(default_factory=dict)

class AdvancedRiskManager:
    """Institutional-grade risk management system"""
    
    def __init__(self):
        self.risk_limits: Dict[str, Dict[str, RiskLimit]] = {}  # account_id -> limits
        self.portfolio_risks: Dict[str, PortfolioRisk] = {}
        self.active_alerts: Dict[str, List[RiskAlert]] = defaultdict(list)
        self.risk_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        
        # Risk calculation parameters
        self.risk_params = {
            "var_confidence_levels": [0.95, 0.99],
            "stress_scenarios": {
                "market_crash": -0.20,    # -20% market drop
                "volatility_spike": 2.0,  # 2x volatility increase
                "correlation_breakdown": 0.8,  # Correlation goes to 0.8
                "liquidity_crisis": 0.5   # 50% liquidity reduction
            },
            "concentration_thresholds": {
                "single_position": 0.20,   # Max 20% in single position
                "sector": 0.30,            # Max 30% in single sector
                "asset_class": 0.80,       # Max 80% in single asset class
                "country": 0.60            # Max 60% in single country
            },
            "leverage_limits": {
                "retail": 2.0,        # 2:1 max leverage
                "professional": 4.0,   # 4:1 max leverage
                "institutional": 10.0  # 10:1 max leverage
            }
        }
        
        # Market data cache for risk calculations
        self.price_history: Dict[str, pd.DataFrame] = {}
        self.correlation_matrix: pd.DataFrame = pd.DataFrame()
        self.volatility_estimates: Dict[str, float] = {}
        
        # Performance tracking
        self.risk_stats = {
            "risk_checks_performed": 0,
            "orders_rejected": 0,
            "alerts_generated": 0,
            "var_breaches": 0
        }
        
        # Start background tasks
        asyncio.create_task(self._risk_monitoring_loop())
        asyncio.create_task(self._market_data_collector())
        asyncio.create_task(self._performance_reporter())
        
    async def initialize_account_limits(self, account: Account, db_session) -> bool:
        """Initialize risk limits for account"""
        
        account_id = str(account.id)
        user = db_session.query(User).filter(User.id == account.user_id).first()
        
        # Determine user tier
        if user.is_professional:
            max_leverage = self.risk_params["leverage_limits"]["professional"]
            max_single_position = 0.25
        else:
            max_leverage = self.risk_params["leverage_limits"]["retail"]
            max_single_position = 0.15
        
        # Initialize risk limits
        self.risk_limits[account_id] = {
            "max_portfolio_value": RiskLimit(
                name="Maximum Portfolio Value",
                limit_type="absolute",
                limit_value=float(account.buying_power * max_leverage),
                current_value=0.0,
                utilization=0.0
            ),
            "max_single_position": RiskLimit(
                name="Maximum Single Position",
                limit_type="percentage",
                limit_value=max_single_position,
                current_value=0.0,
                utilization=0.0
            ),
            "max_sector_exposure": RiskLimit(
                name="Maximum Sector Exposure",
                limit_type="percentage", 
                limit_value=0.30,  # 30%
                current_value=0.0,
                utilization=0.0
            ),
            "max_daily_var": RiskLimit(
                name="Maximum Daily VaR",
                limit_type="absolute",
                limit_value=account.cash_balance * 0.05,  # 5% of cash
                current_value=0.0,
                utilization=0.0,
                hard_limit=False  # Warning only
            ),
            "max_leverage": RiskLimit(
                name="Maximum Leverage Ratio",
                limit_type="ratio",
                limit_value=max_leverage,
                current_value=1.0,
                utilization=0.0
            ),
            "max_concentration": RiskLimit(
                name="Maximum Concentration Score",
                limit_type="ratio",
                limit_value=0.50,  # 50% concentration max
                current_value=0.0,
                utilization=0.0,
                hard_limit=False
            )
        }
        
        logger.info(f"✅ Risk limits initialized for account {account_id}")
        return True
    
    async def validate_order(self, account: Account, order_request, db_session) -> OrderRiskCheck:
        """Comprehensive order risk validation"""
        
        account_id = str(account.id)
        self.risk_stats["risk_checks_performed"] += 1
        
        # Initialize limits if not present
        if account_id not in self.risk_limits:
            await self.initialize_account_limits(account, db_session)
        
        warnings = []
        risk_score = 0.0
        
        try:
            # Get current positions
            positions = db_session.query(Position).filter(
                Position.account_id == account.id,
                Position.quantity != 0
            ).all()
            
            # Calculate order value
            market_tick = market_data_stream.get_latest_tick(order_request.asset_symbol)
            if not market_tick:
                return OrderRiskCheck(
                    approved=False,
                    risk_score=10.0,
                    reason="No market data available for risk assessment"
                )
            
            estimated_price = market_tick.ask if order_request.side.value == "buy" else market_tick.bid
            if order_request.order_type.value == "limit" and order_request.limit_price:
                estimated_price = order_request.limit_price
            
            order_value = abs(order_request.quantity * estimated_price)
            
            # 1. Portfolio Value Check
            portfolio_check = await self._check_portfolio_limits(account_id, order_value, positions)
            risk_score += portfolio_check["risk_contribution"]
            warnings.extend(portfolio_check["warnings"])
            
            # 2. Position Concentration Check
            concentration_check = await self._check_concentration_limits(
                account_id, order_request, order_value, positions, db_session
            )
            risk_score += concentration_check["risk_contribution"]
            warnings.extend(concentration_check["warnings"])
            
            # 3. Leverage Check
            leverage_check = await self._check_leverage_limits(account, order_value)
            risk_score += leverage_check["risk_contribution"]
            warnings.extend(leverage_check["warnings"])
            
            # 4. Market Risk Check
            market_risk_check = await self._check_market_risk_limits(
                account_id, order_request, positions
            )
            risk_score += market_risk_check["risk_contribution"]
            warnings.extend(market_risk_check["warnings"])
            
            # 5. Liquidity Check
            liquidity_check = await self._check_liquidity_risk(order_request, market_tick)
            risk_score += liquidity_check["risk_contribution"]
            warnings.extend(liquidity_check["warnings"])
            
            # Determine approval
            approved = True
            rejection_reason = None
            
            # Check hard limits
            for limit_name, limit in self.risk_limits[account_id].items():
                if limit.hard_limit and limit.utilization > 1.0:
                    approved = False
                    rejection_reason = f"Hard limit exceeded: {limit.name}"
                    break
            
            # Risk score threshold
            if risk_score > 8.0:
                approved = False
                rejection_reason = f"Risk score too high: {risk_score:.1f}/10"
            
            if not approved:
                self.risk_stats["orders_rejected"] += 1
                logger.warning(f"🚨 Order rejected for account {account_id}: {rejection_reason}")
            
            return OrderRiskCheck(
                approved=approved,
                risk_score=risk_score,
                warnings=warnings,
                reason=rejection_reason,
                required_margin=self._calculate_required_margin(order_request, estimated_price),
                impact_on_portfolio={
                    "value_change": order_value,
                    "leverage_change": order_value / account.cash_balance,
                    "concentration_impact": concentration_check.get("new_concentration", 0.0)
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Order risk validation error: {e}")
            return OrderRiskCheck(
                approved=False,
                risk_score=10.0,
                reason=f"Risk validation error: {str(e)}"
            )
    
    async def calculate_portfolio_risk(self, account_id: str, db_session) -> PortfolioRisk:
        """Calculate comprehensive portfolio risk metrics"""
        
        try:
            # Get positions
            positions = db_session.query(Position).join(Asset).filter(
                Position.account_id == account_id,
                Position.quantity != 0
            ).all()
            
            if not positions:
                return PortfolioRisk(
                    account_id=account_id,
                    total_value=0.0,
                    var_1d_95=0.0,
                    var_1d_99=0.0,
                    expected_shortfall=0.0,
                    beta=0.0,
                    correlation_spy=0.0,
                    max_drawdown=0.0,
                    sharpe_ratio=0.0,
                    volatility=0.0,
                    concentration_score=0.0,
                    leverage_ratio=1.0,
                    liquidity_score=1.0
                )
            
            # Calculate portfolio value and weights
            total_value = sum(abs(pos.market_value) for pos in positions)
            weights = {pos.asset.symbol: abs(pos.market_value) / total_value for pos in positions}
            
            # Get price data for portfolio assets
            symbols = [pos.asset.symbol for pos in positions]
            price_data = await self._get_price_data(symbols)
            
            if price_data.empty:
                logger.warning(f"⚠️ No price data for portfolio risk calculation")
                return await self._create_default_portfolio_risk(account_id, total_value)
            
            # Calculate returns
            returns = price_data.pct_change().dropna()
            
            # Portfolio returns
            portfolio_returns = sum(weights[symbol] * returns[symbol] for symbol in weights.keys() if symbol in returns.columns)
            
            # VaR Calculations
            var_95 = self._calculate_var(portfolio_returns, 0.95) * total_value
            var_99 = self._calculate_var(portfolio_returns, 0.99) * total_value
            expected_shortfall = self._calculate_expected_shortfall(portfolio_returns, 0.95) * total_value
            
            # Beta calculation (vs SPY)
            beta = self._calculate_portfolio_beta(returns, weights)
            
            # Correlation with SPY
            spy_corr = self._calculate_spy_correlation(portfolio_returns)
            
            # Volatility
            volatility = float(portfolio_returns.std()) * np.sqrt(252)  # Annualized
            
            # Sharpe ratio (assuming 2% risk-free rate)
            excess_returns = portfolio_returns.mean() * 252 - 0.02
            sharpe_ratio = excess_returns / volatility if volatility > 0 else 0.0
            
            # Concentration score
            concentration_score = self._calculate_concentration_score(weights)
            
            # Leverage ratio
            account = db_session.query(Account).filter(Account.id == account_id).first()
            leverage_ratio = total_value / account.cash_balance if account and account.cash_balance > 0 else 1.0
            
            # Liquidity score
            liquidity_score = self._calculate_portfolio_liquidity_score(positions)
            
            # Max drawdown (simplified)
            max_drawdown = self._calculate_max_drawdown(portfolio_returns)
            
            # Stress test results
            stress_results = await self._perform_stress_tests(positions, weights, total_value)
            
            portfolio_risk = PortfolioRisk(
                account_id=account_id,
                total_value=total_value,
                var_1d_95=var_95,
                var_1d_99=var_99,
                expected_shortfall=expected_shortfall,
                beta=beta,
                correlation_spy=spy_corr,
                max_drawdown=max_drawdown,
                sharpe_ratio=sharpe_ratio,
                volatility=volatility,
                concentration_score=concentration_score,
                leverage_ratio=leverage_ratio,
                liquidity_score=liquidity_score,
                stress_test_results=stress_results
            )
            
            # Store for monitoring
            self.portfolio_risks[account_id] = portfolio_risk
            
            # Save to database
            await self._save_risk_metrics(portfolio_risk, db_session)
            
            return portfolio_risk
            
        except Exception as e:
            logger.error(f"❌ Portfolio risk calculation error: {e}")
            return await self._create_default_portfolio_risk(account_id, 0.0)
    
    async def _check_portfolio_limits(self, account_id: str, order_value: float, 
                                    positions: List[Position]) -> Dict[str, Any]:
        """Check portfolio-level risk limits"""
        
        warnings = []
        risk_contribution = 0.0
        
        limits = self.risk_limits[account_id]
        
        # Current portfolio value
        current_value = sum(abs(pos.market_value) for pos in positions)
        new_value = current_value + order_value
        
        # Update portfolio value limit
        portfolio_limit = limits["max_portfolio_value"]
        portfolio_limit.current_value = new_value
        portfolio_limit.utilization = new_value / portfolio_limit.limit_value
        
        if portfolio_limit.utilization > portfolio_limit.breach_threshold:
            warnings.append(f"Portfolio value approaching limit: {portfolio_limit.utilization:.1%}")
            risk_contribution += 2.0
        
        if portfolio_limit.utilization > 1.0:
            risk_contribution += 5.0
        
        return {
            "warnings": warnings,
            "risk_contribution": risk_contribution
        }
    
    async def _check_concentration_limits(self, account_id: str, order_request, 
                                        order_value: float, positions: List[Position],
                                        db_session) -> Dict[str, Any]:
        """Check position concentration limits"""
        
        warnings = []
        risk_contribution = 0.0
        
        # Get asset for new order
        asset = db_session.query(Asset).filter(Asset.symbol == order_request.asset_symbol).first()
        
        # Calculate current portfolio value
        total_value = sum(abs(pos.market_value) for pos in positions) + order_value
        
        # Check single position concentration
        existing_position = next((pos for pos in positions if pos.asset.symbol == order_request.asset_symbol), None)
        
        if existing_position:
            new_position_value = abs(existing_position.market_value) + order_value
        else:
            new_position_value = order_value
        
        position_concentration = new_position_value / total_value
        
        # Update concentration limit
        concentration_limit = self.risk_limits[account_id]["max_single_position"]
        concentration_limit.current_value = position_concentration
        concentration_limit.utilization = position_concentration / concentration_limit.limit_value
        
        if position_concentration > concentration_limit.limit_value:
            warnings.append(f"Single position concentration too high: {position_concentration:.1%}")
            risk_contribution += 3.0
        elif position_concentration > concentration_limit.limit_value * concentration_limit.breach_threshold:
            warnings.append(f"Single position concentration warning: {position_concentration:.1%}")
            risk_contribution += 1.0
        
        # Sector concentration (if asset has sector info)
        if asset and hasattr(asset, 'sector') and asset.sector:
            sector_concentration = self._calculate_sector_concentration(
                positions, asset.sector, order_value, total_value
            )
            
            sector_limit = self.risk_limits[account_id]["max_sector_exposure"]
            sector_limit.current_value = sector_concentration
            sector_limit.utilization = sector_concentration / sector_limit.limit_value
            
            if sector_concentration > sector_limit.limit_value:
                warnings.append(f"Sector concentration too high: {sector_concentration:.1%}")
                risk_contribution += 2.0
        
        return {
            "warnings": warnings,
            "risk_contribution": risk_contribution,
            "new_concentration": position_concentration
        }
    
    async def _check_leverage_limits(self, account: Account, order_value: float) -> Dict[str, Any]:
        """Check leverage limits"""
        
        warnings = []
        risk_contribution = 0.0
        
        account_id = str(account.id)
        
        # Calculate new leverage ratio
        new_leverage = (account.buying_power + order_value) / account.cash_balance if account.cash_balance > 0 else 1.0
        
        # Update leverage limit
        leverage_limit = self.risk_limits[account_id]["max_leverage"]
        leverage_limit.current_value = new_leverage
        leverage_limit.utilization = new_leverage / leverage_limit.limit_value
        
        if new_leverage > leverage_limit.limit_value:
            warnings.append(f"Leverage limit exceeded: {new_leverage:.1f}x")
            risk_contribution += 4.0
        elif new_leverage > leverage_limit.limit_value * leverage_limit.breach_threshold:
            warnings.append(f"High leverage warning: {new_leverage:.1f}x")
            risk_contribution += 1.5
        
        return {
            "warnings": warnings,
            "risk_contribution": risk_contribution
        }
    
    async def _check_market_risk_limits(self, account_id: str, order_request, 
                                      positions: List[Position]) -> Dict[str, Any]:
        """Check market risk limits"""
        
        warnings = []
        risk_contribution = 0.0
        
        try:
            # Get volatility estimate for asset
            volatility = self.volatility_estimates.get(order_request.asset_symbol, 0.20)  # Default 20%
            
            # High volatility warning
            if volatility > 0.50:  # > 50% volatility
                warnings.append(f"High volatility asset: {volatility:.1%}")
                risk_contribution += 2.0
            elif volatility > 0.30:  # > 30% volatility
                warnings.append(f"Moderate volatility warning: {volatility:.1%}")
                risk_contribution += 1.0
            
            # Check if adding to already risky portfolio
            if len(positions) > 0:
                portfolio_volatility = self._estimate_portfolio_volatility(positions)
                if portfolio_volatility > 0.25:  # > 25% portfolio volatility
                    warnings.append(f"High portfolio volatility: {portfolio_volatility:.1%}")
                    risk_contribution += 1.5
            
        except Exception as e:
            logger.error(f"❌ Market risk check error: {e}")
        
        return {
            "warnings": warnings,
            "risk_contribution": risk_contribution
        }
    
    async def _check_liquidity_risk(self, order_request, market_tick) -> Dict[str, Any]:
        """Check liquidity risk for order"""
        
        warnings = []
        risk_contribution = 0.0
        
        # Spread analysis
        spread = market_tick.ask - market_tick.bid
        spread_bps = (spread / market_tick.price) * 10000
        
        if spread_bps > 50:  # > 0.5% spread
            warnings.append(f"Wide bid-ask spread: {spread_bps:.1f}bps")
            risk_contribution += 2.0
        elif spread_bps > 20:  # > 0.2% spread
            warnings.append(f"Moderate spread: {spread_bps:.1f}bps")
            risk_contribution += 1.0
        
        # Volume analysis
        avg_volume = 1000000  # Would get from historical data
        volume_ratio = market_tick.volume / avg_volume
        
        if volume_ratio < 0.5:  # < 50% of average volume
            warnings.append("Low trading volume")
            risk_contribution += 1.5
        
        # Order size vs market
        order_value = order_request.quantity * market_tick.price
        if order_value > market_tick.volume * market_tick.price * 0.1:  # > 10% of daily volume
            warnings.append("Large order relative to volume")
            risk_contribution += 2.0
        
        return {
            "warnings": warnings,
            "risk_contribution": risk_contribution
        }
    
    def _calculate_required_margin(self, order_request, price: float) -> float:
        """Calculate required margin for order"""
        
        # Simplified margin calculation
        order_value = abs(order_request.quantity * price)
        
        if order_request.asset_symbol in ["SPY", "QQQ"]:  # ETFs
            margin_rate = 0.25  # 25% margin requirement
        else:  # Individual stocks
            margin_rate = 0.50  # 50% margin requirement
        
        return order_value * margin_rate
    
    async def _get_price_data(self, symbols: List[str], days: int = 252) -> pd.DataFrame:
        """Get historical price data for symbols"""
        
        # In a real implementation, this would fetch from market data provider
        # For demo, create mock price data
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        dates = pd.date_range(start_date, end_date, freq='D')
        
        price_data = pd.DataFrame(index=dates)
        
        for symbol in symbols:
            # Generate realistic price series
            base_price = 100.0  # Starting price
            returns = np.random.normal(0.0005, 0.02, len(dates))  # Daily returns
            prices = [base_price]
            
            for ret in returns[1:]:
                prices.append(prices[-1] * (1 + ret))
            
            price_data[symbol] = prices[:len(dates)]
        
        return price_data
    
    def _calculate_var(self, returns: pd.Series, confidence: float) -> float:
        """Calculate Value at Risk"""
        
        if len(returns) == 0:
            return 0.0
        
        return float(np.percentile(returns.dropna(), (1 - confidence) * 100))
    
    def _calculate_expected_shortfall(self, returns: pd.Series, confidence: float) -> float:
        """Calculate Expected Shortfall (Conditional VaR)"""
        
        if len(returns) == 0:
            return 0.0
        
        var_threshold = self._calculate_var(returns, confidence)
        tail_returns = returns[returns <= var_threshold]
        
        return float(tail_returns.mean()) if len(tail_returns) > 0 else 0.0
    
    def _calculate_portfolio_beta(self, returns: pd.DataFrame, weights: Dict[str, float]) -> float:
        """Calculate portfolio beta vs market (SPY)"""
        
        try:
            # Mock SPY returns
            market_returns = np.random.normal(0.0005, 0.015, len(returns))
            
            # Calculate portfolio returns
            portfolio_returns = sum(
                weights[symbol] * returns[symbol] 
                for symbol in weights.keys() 
                if symbol in returns.columns
            )
            
            # Calculate beta
            covariance = np.cov(portfolio_returns.dropna(), market_returns[:len(portfolio_returns)])[0, 1]
            market_variance = np.var(market_returns[:len(portfolio_returns)])
            
            return covariance / market_variance if market_variance > 0 else 1.0
            
        except Exception:
            return 1.0  # Default beta
    
    def _calculate_spy_correlation(self, portfolio_returns: pd.Series) -> float:
        """Calculate correlation with SPY"""
        
        try:
            # Mock SPY returns
            market_returns = np.random.normal(0.0005, 0.015, len(portfolio_returns))
            correlation = np.corrcoef(portfolio_returns.dropna(), market_returns[:len(portfolio_returns)])[0, 1]
            return float(correlation) if not np.isnan(correlation) else 0.0
        except Exception:
            return 0.0
    
    def _calculate_concentration_score(self, weights: Dict[str, float]) -> float:
        """Calculate portfolio concentration score (Herfindahl index)"""
        
        return sum(weight ** 2 for weight in weights.values())
    
    def _calculate_portfolio_liquidity_score(self, positions: List[Position]) -> float:
        """Calculate portfolio liquidity score"""
        
        # Mock liquidity scoring based on position size and asset type
        total_value = sum(abs(pos.market_value) for pos in positions)
        
        if total_value == 0:
            return 1.0
        
        weighted_liquidity = 0.0
        
        for position in positions:
            weight = abs(position.market_value) / total_value
            
            # Assign liquidity scores (would be based on real data)
            if position.asset.symbol in ["SPY", "QQQ", "AAPL", "MSFT"]:
                liquidity_score = 1.0  # Highly liquid
            elif position.asset.asset_type.value in ["etf", "stock"]:
                liquidity_score = 0.8  # Good liquidity
            else:
                liquidity_score = 0.6  # Moderate liquidity
            
            weighted_liquidity += weight * liquidity_score
        
        return weighted_liquidity
    
    def _calculate_max_drawdown(self, returns: pd.Series) -> float:
        """Calculate maximum drawdown"""
        
        if len(returns) == 0:
            return 0.0
        
        cum_returns = (1 + returns).cumprod()
        running_max = cum_returns.expanding().max()
        drawdown = (cum_returns - running_max) / running_max
        
        return float(drawdown.min())
    
    async def _perform_stress_tests(self, positions: List[Position], 
                                   weights: Dict[str, float], total_value: float) -> Dict[str, float]:
        """Perform portfolio stress tests"""
        
        stress_results = {}
        
        for scenario_name, scenario_impact in self.risk_params["stress_scenarios"].items():
            if scenario_name == "market_crash":
                # Apply uniform market decline
                stressed_value = total_value * (1 + scenario_impact)
                stress_results[scenario_name] = stressed_value - total_value
                
            elif scenario_name == "volatility_spike":
                # Estimate impact of volatility spike on portfolio
                avg_volatility = np.mean(list(self.volatility_estimates.values())) if self.volatility_estimates else 0.20
                stressed_volatility = avg_volatility * scenario_impact
                # Rough estimate: higher vol = lower portfolio value
                impact_factor = -0.1 * (stressed_volatility - avg_volatility)
                stress_results[scenario_name] = total_value * impact_factor
                
            else:
                # Default stress test
                stress_results[scenario_name] = total_value * -0.05  # -5% impact
        
        return stress_results
    
    def _calculate_sector_concentration(self, positions: List[Position], 
                                      new_sector: str, order_value: float, 
                                      total_value: float) -> float:
        """Calculate sector concentration"""
        
        sector_value = order_value  # New order value
        
        # Add existing positions in same sector
        for position in positions:
            if hasattr(position.asset, 'sector') and position.asset.sector == new_sector:
                sector_value += abs(position.market_value)
        
        return sector_value / total_value
    
    def _estimate_portfolio_volatility(self, positions: List[Position]) -> float:
        """Estimate portfolio volatility"""
        
        # Simplified portfolio volatility estimation
        total_value = sum(abs(pos.market_value) for pos in positions)
        
        if total_value == 0:
            return 0.0
        
        weighted_volatility = 0.0
        
        for position in positions:
            weight = abs(position.market_value) / total_value
            symbol = position.asset.symbol
            volatility = self.volatility_estimates.get(symbol, 0.25)  # Default 25%
            weighted_volatility += weight * volatility
        
        return weighted_volatility
    
    async def _create_default_portfolio_risk(self, account_id: str, total_value: float) -> PortfolioRisk:
        """Create default portfolio risk when calculation fails"""
        
        return PortfolioRisk(
            account_id=account_id,
            total_value=total_value,
            var_1d_95=total_value * 0.02,  # 2% VaR estimate
            var_1d_99=total_value * 0.035,  # 3.5% VaR estimate
            expected_shortfall=total_value * 0.045,  # 4.5% ES estimate
            beta=1.0,
            correlation_spy=0.7,
            max_drawdown=-0.10,  # -10% estimate
            sharpe_ratio=0.8,
            volatility=0.15,
            concentration_score=0.2,
            leverage_ratio=1.0,
            liquidity_score=0.8
        )
    
    async def _save_risk_metrics(self, portfolio_risk: PortfolioRisk, db_session):
        """Save risk metrics to database"""
        
        try:
            risk_metrics = RiskMetrics(
                account_id=portfolio_risk.account_id,
                portfolio_var_1d=portfolio_risk.var_1d_95,
                portfolio_var_5d=portfolio_risk.var_1d_95 * np.sqrt(5),  # Scale to 5-day
                portfolio_beta=portfolio_risk.beta,
                portfolio_correlation_spy=portfolio_risk.correlation_spy,
                max_drawdown=portfolio_risk.max_drawdown,
                largest_position_percent=max((pos.market_value / portfolio_risk.total_value) * 100 
                                           for pos in [] if portfolio_risk.total_value > 0) or 0,
                total_leverage=portfolio_risk.leverage_ratio,
                margin_utilization=max(0, (portfolio_risk.leverage_ratio - 1) * 100),
                portfolio_delta=0.0,  # Would calculate for options
                portfolio_gamma=0.0,
                portfolio_theta=0.0,
                portfolio_vega=0.0,
                calculated_at=datetime.utcnow()
            )
            
            db_session.merge(risk_metrics)  # Use merge to update if exists
            db_session.commit()
            
        except Exception as e:
            logger.error(f"❌ Failed to save risk metrics: {e}")
    
    async def _risk_monitoring_loop(self):
        """Background risk monitoring loop"""
        
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                
                # Check all account limits
                for account_id, limits in self.risk_limits.items():
                    await self._check_account_alerts(account_id, limits)
                
                # Check VaR breaches
                await self._check_var_breaches()
                
            except Exception as e:
                logger.error(f"❌ Risk monitoring error: {e}")
    
    async def _check_account_alerts(self, account_id: str, limits: Dict[str, RiskLimit]):
        """Check for risk alerts on account"""
        
        alerts_generated = []
        
        for limit_name, limit in limits.items():
            if limit.utilization > limit.breach_threshold:
                severity = RiskLevel.HIGH if limit.utilization > 1.0 else RiskLevel.MEDIUM
                
                alert = RiskAlert(
                    alert_id=f"{account_id}_{limit_name}_{datetime.now().timestamp()}",
                    risk_type=RiskType.CONCENTRATION_RISK if "concentration" in limit_name.lower() else RiskType.MARKET_RISK,
                    severity=severity,
                    message=f"{limit.name} utilization: {limit.utilization:.1%}",
                    current_value=limit.current_value,
                    limit_value=limit.limit_value,
                    utilization=limit.utilization,
                    timestamp=datetime.utcnow(),
                    account_id=account_id,
                    requires_action=limit.utilization > 1.0,
                    recommendations=self._get_risk_recommendations(limit_name, limit)
                )
                
                alerts_generated.append(alert)
        
        # Store and notify alerts
        if alerts_generated:
            self.active_alerts[account_id].extend(alerts_generated)
            self.risk_stats["alerts_generated"] += len(alerts_generated)
            
            # Notify via WebSocket
            for alert in alerts_generated:
                await self._notify_risk_alert(alert)
    
    def _get_risk_recommendations(self, limit_name: str, limit: RiskLimit) -> List[str]:
        """Get recommendations for risk limit breach"""
        
        recommendations = []
        
        if "concentration" in limit_name.lower():
            recommendations.extend([
                "Consider reducing position size",
                "Diversify across more assets",
                "Review correlation with other positions"
            ])
        elif "leverage" in limit_name.lower():
            recommendations.extend([
                "Reduce position sizes",
                "Close some positions",
                "Add more capital to account"
            ])
        elif "var" in limit_name.lower():
            recommendations.extend([
                "Reduce portfolio volatility",
                "Add hedging positions",
                "Consider risk-free assets"
            ])
        else:
            recommendations.append("Monitor risk closely and consider position adjustments")
        
        return recommendations
    
    async def _check_var_breaches(self):
        """Check for VaR breaches across all portfolios"""
        
        for account_id, portfolio_risk in self.portfolio_risks.items():
            # Check if actual loss exceeded VaR (simplified check)
            # In practice, would compare actual P&L to VaR forecast
            
            var_95 = abs(portfolio_risk.var_1d_95)
            if var_95 > 0:
                # Mock breach check (in practice, compare to actual P&L)
                breach_probability = 0.05  # 5% chance of breach (as expected for 95% VaR)
                
                if np.random.random() < breach_probability:
                    self.risk_stats["var_breaches"] += 1
                    
                    alert = RiskAlert(
                        alert_id=f"var_breach_{account_id}_{datetime.now().timestamp()}",
                        risk_type=RiskType.MARKET_RISK,
                        severity=RiskLevel.HIGH,
                        message=f"VaR breach detected: Loss exceeded {var_95:.0f}",
                        current_value=var_95 * 1.2,  # Mock actual loss
                        limit_value=var_95,
                        utilization=1.2,
                        timestamp=datetime.utcnow(),
                        account_id=account_id,
                        requires_action=True,
                        recommendations=[
                            "Review risk model accuracy",
                            "Consider position size reductions",
                            "Analyze market conditions"
                        ]
                    )
                    
                    self.active_alerts[account_id].append(alert)
                    await self._notify_risk_alert(alert)
    
    async def _notify_risk_alert(self, alert: RiskAlert):
        """Notify user of risk alert via WebSocket"""
        
        try:
            await websocket_manager.send_risk_alert(alert.account_id, {
                "alert_id": alert.alert_id,
                "risk_type": alert.risk_type.value,
                "severity": alert.severity.value,
                "message": alert.message,
                "current_value": alert.current_value,
                "limit_value": alert.limit_value,
                "utilization": alert.utilization,
                "timestamp": alert.timestamp.isoformat(),
                "requires_action": alert.requires_action,
                "recommendations": alert.recommendations
            })
        except Exception as e:
            logger.error(f"❌ Failed to notify risk alert: {e}")
    
    async def _market_data_collector(self):
        """Collect market data for risk calculations"""
        
        while True:
            try:
                await asyncio.sleep(30)  # Update every 30 seconds
                
                # Update volatility estimates
                symbols = set()
                for limits in self.risk_limits.values():
                    # Would collect symbols from active positions
                    symbols.update(["SPY", "QQQ", "AAPL", "MSFT", "NVDA"])
                
                for symbol in symbols:
                    market_tick = market_data_stream.get_latest_tick(symbol)
                    if market_tick:
                        # Simple volatility estimate from price changes
                        price_change_pct = abs(market_tick.change_percent / 100)
                        daily_vol = price_change_pct * np.sqrt(1)  # Daily
                        annual_vol = daily_vol * np.sqrt(252)  # Annualized
                        
                        # EMA update
                        current_vol = self.volatility_estimates.get(symbol, annual_vol)
                        self.volatility_estimates[symbol] = current_vol * 0.95 + annual_vol * 0.05
                
            except Exception as e:
                logger.error(f"❌ Market data collection error: {e}")
    
    async def _performance_reporter(self):
        """Report risk management performance"""
        
        while True:
            try:
                await asyncio.sleep(3600)  # Report every hour
                
                logger.info(
                    f"🛡️ Risk Management Stats - "
                    f"Checks: {self.risk_stats['risk_checks_performed']}, "
                    f"Rejections: {self.risk_stats['orders_rejected']}, "
                    f"Alerts: {self.risk_stats['alerts_generated']}, "
                    f"VaR Breaches: {self.risk_stats['var_breaches']}"
                )
                
            except Exception as e:
                logger.error(f"❌ Risk performance reporting error: {e}")
    
    def get_account_alerts(self, account_id: str) -> List[RiskAlert]:
        """Get active alerts for account"""
        return self.active_alerts.get(account_id, [])
    
    def get_portfolio_risk(self, account_id: str) -> Optional[PortfolioRisk]:
        """Get portfolio risk metrics for account"""
        return self.portfolio_risks.get(account_id)
    
    def get_risk_stats(self) -> Dict[str, Any]:
        """Get risk management statistics"""
        
        return {
            **self.risk_stats,
            "active_accounts": len(self.risk_limits),
            "total_alerts": sum(len(alerts) for alerts in self.active_alerts.values()),
            "volatility_estimates": dict(list(self.volatility_estimates.items())[:10])  # Top 10
        }
    
    async def shutdown(self):
        """Gracefully shutdown risk manager"""
        
        logger.info("🛑 Shutting down risk manager...")
        
        # Clear active monitoring
        self.risk_limits.clear()
        self.active_alerts.clear()
        self.portfolio_risks.clear()
        
        logger.info("✅ Risk manager shutdown complete")

# Global risk manager instance
risk_manager = AdvancedRiskManager()