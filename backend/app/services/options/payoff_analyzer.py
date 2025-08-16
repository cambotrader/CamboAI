"""
🎯 OPTIONS PAYOFF ANALYZER & VISUALIZER
Complete P&L analysis, breakeven calculation, and risk visualization
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import math
from .engine import MarketInputs, VanillaBS

@dataclass
class PayoffPoint:
    spot_price: float
    payoff: float
    profit_loss: float
    delta: float
    gamma: float
    theta: float
    vega: float

@dataclass 
class PayoffAnalysis:
    breakeven_points: List[float]
    max_profit: float
    max_loss: float
    profit_probability: float
    payoff_curve: List[PayoffPoint]
    risk_reward_ratio: float
    strategy_summary: Dict[str, Any]

class OptionsPayoffAnalyzer:
    """Complete options strategy payoff analysis and visualization"""
    
    def __init__(self):
        self.spot_range_multiplier = 0.5  # ±50% for payoff analysis
        self.analysis_points = 100
    
    def analyze_strategy_payoff(self,
                               legs: List[Dict[str, Any]],
                               current_spot: float,
                               spot_range: Optional[Tuple[float, float]] = None,
                               at_expiration: bool = True) -> PayoffAnalysis:
        """
        Complete payoff analysis for any options strategy
        
        Args:
            legs: List of option legs with all parameters
            current_spot: Current underlying price
            spot_range: Custom spot price range for analysis
            at_expiration: If True, analyze at expiry (T=0), else current time
        """
        
        if spot_range is None:
            range_size = current_spot * self.spot_range_multiplier
            spot_min = current_spot - range_size
            spot_max = current_spot + range_size
        else:
            spot_min, spot_max = spot_range
        
        # Generate spot price array for analysis
        spot_prices = np.linspace(spot_min, spot_max, self.analysis_points)
        
        payoff_curve = []
        total_premium_paid = 0.0
        
        # Calculate initial premium for each leg
        for leg in legs:
            side_multiplier = 1 if leg.get("side", "long") == "long" else -1
            qty = leg.get("qty", 1)
            
            # Price at current market conditions
            inputs = MarketInputs(
                spot=leg["spot"],
                strike=leg["strike"], 
                rate=leg.get("rate", 0.05),
                div_yield=leg.get("div_yield", 0.0),
                vol=leg["vol"],
                t=leg["expiry"]
            )
            
            result = VanillaBS.price(inputs, leg["right"])
            leg_premium = result.price * qty * side_multiplier
            total_premium_paid -= leg_premium  # Net cost (negative = paid premium)
        
        # Calculate payoff at each spot price
        for spot in spot_prices:
            total_payoff = 0.0
            total_greeks = {"delta": 0.0, "gamma": 0.0, "theta": 0.0, "vega": 0.0}
            
            for leg in legs:
                side_multiplier = 1 if leg.get("side", "long") == "long" else -1
                qty = leg.get("qty", 1)
                strike = leg["strike"]
                right = leg["right"]
                
                if at_expiration:
                    # Intrinsic value at expiry
                    if right == "call":
                        intrinsic = max(0, spot - strike)
                    else:  # put
                        intrinsic = max(0, strike - spot)
                    
                    leg_payoff = intrinsic * qty * side_multiplier
                    
                    # Greeks are zero at expiration
                    leg_greeks = {"delta": 0.0, "gamma": 0.0, "theta": 0.0, "vega": 0.0}
                    
                else:
                    # Current time value
                    inputs = MarketInputs(
                        spot=spot,
                        strike=strike,
                        rate=leg.get("rate", 0.05),
                        div_yield=leg.get("div_yield", 0.0),
                        vol=leg["vol"],
                        t=leg["expiry"]
                    )
                    
                    result = VanillaBS.price(inputs, right)
                    leg_payoff = result.price * qty * side_multiplier
                    leg_greeks = {k: v * qty * side_multiplier for k, v in result.greeks.items()}
                
                total_payoff += leg_payoff
                for greek, value in leg_greeks.items():
                    total_greeks[greek] += value
            
            # Calculate P&L (payoff minus net premium paid)
            profit_loss = total_payoff + total_premium_paid
            
            payoff_curve.append(PayoffPoint(
                spot_price=spot,
                payoff=total_payoff,
                profit_loss=profit_loss,
                delta=total_greeks["delta"],
                gamma=total_greeks["gamma"],
                theta=total_greeks["theta"],
                vega=total_greeks["vega"]
            ))
        
        # Calculate analysis metrics
        breakeven_points = self._find_breakeven_points(payoff_curve)
        max_profit = max(point.profit_loss for point in payoff_curve)
        max_loss = min(point.profit_loss for point in payoff_curve)
        profit_probability = self._calculate_profit_probability(payoff_curve, current_spot)
        risk_reward_ratio = self._calculate_risk_reward_ratio(max_profit, max_loss)
        
        strategy_summary = self._generate_strategy_summary(
            legs, total_premium_paid, max_profit, max_loss, breakeven_points
        )
        
        return PayoffAnalysis(
            breakeven_points=breakeven_points,
            max_profit=max_profit,
            max_loss=max_loss,
            profit_probability=profit_probability,
            payoff_curve=payoff_curve,
            risk_reward_ratio=risk_reward_ratio,
            strategy_summary=strategy_summary
        )
    
    def _find_breakeven_points(self, payoff_curve: List[PayoffPoint]) -> List[float]:
        """Find breakeven points where P&L crosses zero"""
        breakeven_points = []
        
        for i in range(len(payoff_curve) - 1):
            current_pl = payoff_curve[i].profit_loss
            next_pl = payoff_curve[i + 1].profit_loss
            
            # Check for zero crossing
            if (current_pl <= 0 <= next_pl) or (current_pl >= 0 >= next_pl):
                # Linear interpolation for more precise breakeven
                if next_pl != current_pl:
                    ratio = -current_pl / (next_pl - current_pl)
                    spot_diff = payoff_curve[i + 1].spot_price - payoff_curve[i].spot_price
                    breakeven = payoff_curve[i].spot_price + ratio * spot_diff
                    breakeven_points.append(breakeven)
        
        return breakeven_points
    
    def _calculate_profit_probability(self, payoff_curve: List[PayoffPoint], current_spot: float) -> float:
        """Estimate probability of profit assuming normal distribution"""
        profitable_points = [p for p in payoff_curve if p.profit_loss > 0]
        total_points = len(payoff_curve)
        
        if total_points == 0:
            return 0.0
        
        return len(profitable_points) / total_points
    
    def _calculate_risk_reward_ratio(self, max_profit: float, max_loss: float) -> float:
        """Calculate risk/reward ratio"""
        if max_loss >= 0:  # No risk
            return float('inf') if max_profit > 0 else 0.0
        
        return max_profit / abs(max_loss) if max_loss != 0 else float('inf')
    
    def _generate_strategy_summary(self, 
                                  legs: List[Dict[str, Any]], 
                                  net_premium: float,
                                  max_profit: float,
                                  max_loss: float,
                                  breakeven_points: List[float]) -> Dict[str, Any]:
        """Generate comprehensive strategy summary"""
        
        # Analyze leg composition
        call_legs = [leg for leg in legs if leg["right"] == "call"]
        put_legs = [leg for leg in legs if leg["right"] == "put"]
        long_legs = [leg for leg in legs if leg.get("side", "long") == "long"]
        short_legs = [leg for leg in legs if leg.get("side", "long") == "short"]
        
        # Strategy classification
        total_legs = len(legs)
        is_spread = total_legs == 2
        is_butterfly = total_legs == 3 or (total_legs == 4 and any(leg.get("qty", 1) == 2 for leg in legs))
        is_condor = total_legs == 4 and all(leg.get("qty", 1) == 1 for leg in legs)
        is_straddle = total_legs == 2 and len(call_legs) == 1 and len(put_legs) == 1
        
        strategy_type = "Complex Multi-Leg"
        if is_straddle:
            strategy_type = "Straddle/Strangle"
        elif is_spread:
            strategy_type = "Vertical Spread"
        elif is_butterfly:
            strategy_type = "Butterfly"
        elif is_condor:
            strategy_type = "Condor/Iron Condor"
        
        # Risk characteristics
        is_limited_risk = max_loss > -float('inf')
        is_limited_profit = max_profit < float('inf')
        is_net_debit = net_premium < 0
        is_net_credit = net_premium > 0
        
        return {
            "strategy_type": strategy_type,
            "total_legs": total_legs,
            "call_legs": len(call_legs),
            "put_legs": len(put_legs),
            "long_legs": len(long_legs),
            "short_legs": len(short_legs),
            "net_premium": net_premium,
            "is_net_debit": is_net_debit,
            "is_net_credit": is_net_credit,
            "is_limited_risk": is_limited_risk,
            "is_limited_profit": is_limited_profit,
            "max_profit": max_profit,
            "max_loss": max_loss,
            "breakeven_count": len(breakeven_points),
            "strike_range": {
                "min_strike": min(leg["strike"] for leg in legs),
                "max_strike": max(leg["strike"] for leg in legs),
                "strike_span": max(leg["strike"] for leg in legs) - min(leg["strike"] for leg in legs)
            },
            "expiry_range": {
                "min_expiry": min(leg["expiry"] for leg in legs),
                "max_expiry": max(leg["expiry"] for leg in legs)
            }
        }
    
    def generate_payoff_chart_data(self, analysis: PayoffAnalysis) -> Dict[str, Any]:
        """Generate data for payoff diagram visualization"""
        
        spot_prices = [point.spot_price for point in analysis.payoff_curve]
        profit_loss = [point.profit_loss for point in analysis.payoff_curve]
        payoffs = [point.payoff for point in analysis.payoff_curve]
        
        return {
            "chart_data": {
                "spot_prices": spot_prices,
                "profit_loss": profit_loss,
                "payoffs": payoffs,
                "breakeven_points": analysis.breakeven_points
            },
            "annotations": {
                "max_profit": analysis.max_profit,
                "max_loss": analysis.max_loss,
                "breakeven_points": analysis.breakeven_points,
                "profit_zone": [i for i, p in enumerate(profit_loss) if p > 0],
                "loss_zone": [i for i, p in enumerate(profit_loss) if p < 0]
            },
            "greeks_data": {
                "delta": [point.delta for point in analysis.payoff_curve],
                "gamma": [point.gamma for point in analysis.payoff_curve], 
                "theta": [point.theta for point in analysis.payoff_curve],
                "vega": [point.vega for point in analysis.payoff_curve]
            }
        }
    
    def compare_strategies(self, 
                          strategy_analyses: List[Tuple[str, PayoffAnalysis]]) -> Dict[str, Any]:
        """Compare multiple strategies side by side"""
        
        comparison = {
            "strategies": [],
            "metrics_comparison": {},
            "best_strategy": {}
        }
        
        metrics = ["max_profit", "max_loss", "risk_reward_ratio", "profit_probability"]
        
        for strategy_name, analysis in strategy_analyses:
            strategy_data = {
                "name": strategy_name,
                "max_profit": analysis.max_profit,
                "max_loss": analysis.max_loss,
                "risk_reward_ratio": analysis.risk_reward_ratio,
                "profit_probability": analysis.profit_probability,
                "breakeven_count": len(analysis.breakeven_points),
                "net_premium": analysis.strategy_summary.get("net_premium", 0)
            }
            comparison["strategies"].append(strategy_data)
        
        # Find best strategy for each metric
        for metric in metrics:
            values = [(s["name"], s[metric]) for s in comparison["strategies"]]
            if metric in ["max_profit", "risk_reward_ratio", "profit_probability"]:
                best = max(values, key=lambda x: x[1] if not math.isinf(x[1]) else -1)
            else:  # max_loss (higher is better, closer to 0)
                best = max(values, key=lambda x: x[1])
            
            comparison["metrics_comparison"][metric] = {
                "best_strategy": best[0],
                "best_value": best[1],
                "all_values": values
            }
        
        return comparison
    
    def monte_carlo_profit_probability(self,
                                     legs: List[Dict[str, Any]],
                                     current_spot: float,
                                     vol: float,
                                     time_to_expiry: float,
                                     num_simulations: int = 10000) -> Dict[str, Any]:
        """Monte Carlo simulation for profit probability"""
        
        profits = []
        
        for _ in range(num_simulations):
            # Generate random spot price at expiry
            z = np.random.normal()
            final_spot = current_spot * math.exp(
                (0.05 - 0.5 * vol**2) * time_to_expiry + vol * math.sqrt(time_to_expiry) * z
            )
            
            # Calculate P&L at this final spot
            analysis = self.analyze_strategy_payoff(
                legs, final_spot, at_expiration=True
            )
            
            # Find P&L at final spot
            for point in analysis.payoff_curve:
                if abs(point.spot_price - final_spot) < 0.01:  # Close enough
                    profits.append(point.profit_loss)
                    break
        
        profits = np.array(profits)
        
        return {
            "profit_probability": np.mean(profits > 0),
            "expected_profit": np.mean(profits),
            "profit_std": np.std(profits),
            "percentiles": {
                "5th": np.percentile(profits, 5),
                "25th": np.percentile(profits, 25),
                "50th": np.percentile(profits, 50),
                "75th": np.percentile(profits, 75),
                "95th": np.percentile(profits, 95)
            },
            "simulated_profits": profits.tolist()
        }

# Initialize the payoff analyzer
payoff_analyzer = OptionsPayoffAnalyzer()