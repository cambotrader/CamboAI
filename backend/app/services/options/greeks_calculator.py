"""
🧮 ADVANCED GREEKS CALCULATOR & RISK MANAGEMENT
Complete Greeks analysis, sensitivity testing, and portfolio risk management
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import math
from .engine import MarketInputs, VanillaBS

@dataclass
class GreeksProfile:
    delta: float
    gamma: float
    theta: float
    vega: float
    rho: float
    # Second-order Greeks
    vanna: float  # d²V/dS dσ
    charm: float  # d²V/dS dt (delta decay)
    volga: float  # d²V/dσ² (vega convexity)
    veta: float   # d²V/dσ dt (vega decay)
    speed: float  # d³V/dS³ (gamma acceleration)
    color: float  # d³V/dS² dt (gamma decay)

@dataclass
class GreeksAnalysis:
    individual_greeks: List[Dict[str, Any]]
    portfolio_greeks: GreeksProfile
    risk_metrics: Dict[str, float]
    sensitivity_analysis: Dict[str, Dict[str, float]]
    hedge_recommendations: List[Dict[str, Any]]

class AdvancedGreeksCalculator:
    """Complete Greeks calculation and risk management system"""
    
    def __init__(self):
        self.bump_sizes = {
            "delta": 0.01,    # 1% spot move
            "gamma": 0.01,    # 1% spot move for gamma
            "theta": 1/365,   # 1 day time decay
            "vega": 0.01,     # 1% vol move
            "rho": 0.0001,    # 1bp rate move
        }
    
    def calculate_all_greeks(self, 
                           legs: List[Dict[str, Any]], 
                           include_second_order: bool = True) -> GreeksAnalysis:
        """Calculate complete Greeks analysis for options strategy"""
        
        individual_greeks = []
        portfolio_totals = {
            "delta": 0.0, "gamma": 0.0, "theta": 0.0, "vega": 0.0, "rho": 0.0,
            "vanna": 0.0, "charm": 0.0, "volga": 0.0, "veta": 0.0,
            "speed": 0.0, "color": 0.0
        }
        
        for i, leg in enumerate(legs):
            leg_greeks = self._calculate_single_leg_greeks(leg, include_second_order)
            leg_greeks["leg_id"] = i
            leg_greeks["leg_description"] = f"{leg.get('side', 'long').title()} {leg['right'].title()}"
            
            individual_greeks.append(leg_greeks)
            
            # Aggregate to portfolio level
            side_multiplier = 1 if leg.get("side", "long") == "long" else -1
            qty = leg.get("qty", 1)
            multiplier = side_multiplier * qty
            
            for greek in portfolio_totals:
                if greek in leg_greeks:
                    portfolio_totals[greek] += leg_greeks[greek] * multiplier
        
        # Create portfolio Greeks profile
        portfolio_greeks = GreeksProfile(
            delta=portfolio_totals["delta"],
            gamma=portfolio_totals["gamma"],
            theta=portfolio_totals["theta"],
            vega=portfolio_totals["vega"],
            rho=portfolio_totals["rho"],
            vanna=portfolio_totals["vanna"],
            charm=portfolio_totals["charm"],
            volga=portfolio_totals["volga"],
            veta=portfolio_totals["veta"],
            speed=portfolio_totals["speed"],
            color=portfolio_totals["color"]
        )
        
        # Calculate risk metrics
        risk_metrics = self._calculate_risk_metrics(legs, portfolio_greeks)
        
        # Sensitivity analysis
        sensitivity_analysis = self._perform_sensitivity_analysis(legs)
        
        # Generate hedge recommendations
        hedge_recommendations = self._generate_hedge_recommendations(portfolio_greeks, legs)
        
        return GreeksAnalysis(
            individual_greeks=individual_greeks,
            portfolio_greeks=portfolio_greeks,
            risk_metrics=risk_metrics,
            sensitivity_analysis=sensitivity_analysis,
            hedge_recommendations=hedge_recommendations
        )
    
    def _calculate_single_leg_greeks(self, leg: Dict[str, Any], include_second_order: bool) -> Dict[str, float]:
        """Calculate all Greeks for a single option leg"""
        
        inputs = MarketInputs(
            spot=leg["spot"],
            strike=leg["strike"],
            rate=leg.get("rate", 0.05),
            div_yield=leg.get("div_yield", 0.0),
            vol=leg["vol"],
            t=leg["expiry"]
        )
        
        # Base case pricing
        base_result = VanillaBS.price(inputs, leg["right"])
        greeks = base_result.greeks.copy()
        
        if include_second_order:
            # Calculate second-order Greeks using finite differences
            second_order = self._calculate_second_order_greeks(inputs, leg["right"])
            greeks.update(second_order)
        
        return greeks
    
    def _calculate_second_order_greeks(self, inputs: MarketInputs, right: str) -> Dict[str, float]:
        """Calculate second-order Greeks using finite difference methods"""
        
        base_price = VanillaBS.price(inputs, right).price
        base_greeks = VanillaBS.price(inputs, right).greeks
        
        # Bump parameters for finite difference
        spot_bump = inputs.spot * 0.01
        vol_bump = 0.01
        time_bump = 1/365
        
        second_order = {}
        
        # Vanna: d²V/dS dσ (delta sensitivity to vol)
        inputs_spot_up = MarketInputs(inputs.spot + spot_bump, inputs.strike, inputs.rate, 
                                    inputs.div_yield, inputs.vol, inputs.t)
        inputs_spot_vol_up = MarketInputs(inputs.spot + spot_bump, inputs.strike, inputs.rate,
                                        inputs.div_yield, inputs.vol + vol_bump, inputs.t)
        
        delta_base = VanillaBS.price(inputs_spot_up, right).greeks["delta"]
        delta_vol_up = VanillaBS.price(inputs_spot_vol_up, right).greeks["delta"]
        second_order["vanna"] = (delta_vol_up - delta_base) / vol_bump
        
        # Charm: d²V/dS dt (delta decay)
        inputs_time_down = MarketInputs(inputs.spot, inputs.strike, inputs.rate,
                                      inputs.div_yield, inputs.vol, max(0.001, inputs.t - time_bump))
        inputs_spot_time_down = MarketInputs(inputs.spot + spot_bump, inputs.strike, inputs.rate,
                                           inputs.div_yield, inputs.vol, max(0.001, inputs.t - time_bump))
        
        delta_time_down = VanillaBS.price(inputs_spot_time_down, right).greeks["delta"]
        delta_base_time = VanillaBS.price(inputs_time_down, right).greeks["delta"]
        second_order["charm"] = -(delta_time_down - delta_base_time) / time_bump
        
        # Volga: d²V/dσ² (vega convexity)
        inputs_vol_up = MarketInputs(inputs.spot, inputs.strike, inputs.rate,
                                   inputs.div_yield, inputs.vol + vol_bump, inputs.t)
        inputs_vol_down = MarketInputs(inputs.spot, inputs.strike, inputs.rate,
                                     inputs.div_yield, max(0.01, inputs.vol - vol_bump), inputs.t)
        
        vega_up = VanillaBS.price(inputs_vol_up, right).greeks["vega"]
        vega_down = VanillaBS.price(inputs_vol_down, right).greeks["vega"]
        second_order["volga"] = (vega_up - vega_down) / (2 * vol_bump)
        
        # Veta: d²V/dσ dt (vega decay)
        inputs_vol_time_down = MarketInputs(inputs.spot, inputs.strike, inputs.rate,
                                          inputs.div_yield, inputs.vol + vol_bump, 
                                          max(0.001, inputs.t - time_bump))
        
        vega_base = base_greeks["vega"]
        vega_time_down = VanillaBS.price(inputs_vol_time_down, right).greeks["vega"]
        vega_base_time = VanillaBS.price(inputs_time_down, right).greeks["vega"]
        second_order["veta"] = -(vega_time_down - vega_base_time) / time_bump
        
        # Speed: d³V/dS³ (gamma acceleration)
        inputs_spot_down = MarketInputs(max(0.01, inputs.spot - spot_bump), inputs.strike, inputs.rate,
                                      inputs.div_yield, inputs.vol, inputs.t)
        
        gamma_up = VanillaBS.price(inputs_spot_up, right).greeks["gamma"]
        gamma_down = VanillaBS.price(inputs_spot_down, right).greeks["gamma"]
        second_order["speed"] = (gamma_up - gamma_down) / (2 * spot_bump)
        
        # Color: d³V/dS² dt (gamma decay)
        gamma_time_down = VanillaBS.price(inputs_time_down, right).greeks["gamma"]
        second_order["color"] = -(base_greeks["gamma"] - gamma_time_down) / time_bump
        
        return second_order
    
    def _calculate_risk_metrics(self, legs: List[Dict[str, Any]], portfolio_greeks: GreeksProfile) -> Dict[str, float]:
        """Calculate comprehensive risk metrics"""
        
        # Get representative market data from first leg
        spot = legs[0]["spot"]
        vol = legs[0]["vol"]
        
        # Dollar Greeks (normalized by $10k portfolio)
        portfolio_value = 10000  # Assume $10k portfolio for standardization
        
        risk_metrics = {
            # Position sizing risk
            "delta_dollars_per_1pct_move": portfolio_greeks.delta * spot * 0.01,
            "gamma_dollars_per_1pct_move": portfolio_greeks.gamma * spot * spot * 0.01 * 0.01,
            "vega_dollars_per_1pct_vol": portfolio_greeks.vega * 0.01,
            "theta_dollars_per_day": portfolio_greeks.theta,
            "rho_dollars_per_1bp": portfolio_greeks.rho * 0.0001,
            
            # Risk concentration
            "delta_risk_ratio": abs(portfolio_greeks.delta * spot) / portfolio_value,
            "gamma_risk_ratio": abs(portfolio_greeks.gamma * spot * spot * 0.01) / portfolio_value,
            "vega_risk_ratio": abs(portfolio_greeks.vega * vol * 0.1) / portfolio_value,
            
            # Time decay risk
            "theta_decay_rate": portfolio_greeks.theta / portfolio_value,  # Daily decay as % of portfolio
            "time_to_breakeven": abs(portfolio_value / portfolio_greeks.theta) if portfolio_greeks.theta != 0 else float('inf'),
            
            # Volatility risk
            "vol_sensitivity": portfolio_greeks.vega / portfolio_value,
            "vol_convexity": portfolio_greeks.volga if hasattr(portfolio_greeks, 'volga') else 0.0,
            
            # Second-order risks
            "gamma_scalping_pnl": portfolio_greeks.gamma * vol * vol * spot * spot / 252,  # Daily gamma P&L
            "delta_hedging_cost": abs(portfolio_greeks.gamma) * vol * spot * 0.02,  # Assuming 2bp transaction costs
        }
        
        return risk_metrics
    
    def _perform_sensitivity_analysis(self, legs: List[Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
        """Perform comprehensive sensitivity analysis"""
        
        base_legs = legs.copy()
        base_price = sum(self._price_single_leg(leg) for leg in base_legs)
        
        sensitivity_scenarios = {
            "spot_moves": [-10, -5, -2, -1, 1, 2, 5, 10],  # Percent moves
            "vol_moves": [-5, -2, -1, -0.5, 0.5, 1, 2, 5],  # Vol point moves  
            "time_decay": [1, 7, 14, 30, 60, 90],  # Days forward
            "rate_moves": [-50, -25, -10, 10, 25, 50]  # Basis point moves
        }
        
        sensitivity_results = {}
        
        # Spot sensitivity
        sensitivity_results["spot_sensitivity"] = {}
        for spot_move in sensitivity_scenarios["spot_moves"]:
            stressed_legs = []
            for leg in base_legs:
                stressed_leg = leg.copy()
                stressed_leg["spot"] *= (1 + spot_move / 100)
                stressed_legs.append(stressed_leg)
            
            stressed_price = sum(self._price_single_leg(leg) for leg in stressed_legs)
            pnl_change = stressed_price - base_price
            sensitivity_results["spot_sensitivity"][f"spot_{spot_move:+}pct"] = pnl_change
        
        # Volatility sensitivity
        sensitivity_results["vol_sensitivity"] = {}
        for vol_move in sensitivity_scenarios["vol_moves"]:
            stressed_legs = []
            for leg in base_legs:
                stressed_leg = leg.copy()
                stressed_leg["vol"] += vol_move / 100
                stressed_leg["vol"] = max(0.01, stressed_leg["vol"])  # Floor at 1%
                stressed_legs.append(stressed_leg)
            
            stressed_price = sum(self._price_single_leg(leg) for leg in stressed_legs)
            pnl_change = stressed_price - base_price
            sensitivity_results["vol_sensitivity"][f"vol_{vol_move:+}pts"] = pnl_change
        
        # Time decay sensitivity
        sensitivity_results["time_sensitivity"] = {}
        for days_forward in sensitivity_scenarios["time_decay"]:
            stressed_legs = []
            for leg in base_legs:
                stressed_leg = leg.copy()
                stressed_leg["expiry"] = max(0.001, stressed_leg["expiry"] - days_forward / 365)
                stressed_legs.append(stressed_leg)
            
            stressed_price = sum(self._price_single_leg(leg) for leg in stressed_legs)
            pnl_change = stressed_price - base_price
            sensitivity_results["time_sensitivity"][f"t_minus_{days_forward}d"] = pnl_change
        
        # Interest rate sensitivity
        sensitivity_results["rate_sensitivity"] = {}
        for rate_move in sensitivity_scenarios["rate_moves"]:
            stressed_legs = []
            for leg in base_legs:
                stressed_leg = leg.copy()
                stressed_leg["rate"] = stressed_leg.get("rate", 0.05) + rate_move / 10000
                stressed_legs.append(stressed_leg)
            
            stressed_price = sum(self._price_single_leg(leg) for leg in stressed_legs)
            pnl_change = stressed_price - base_price
            sensitivity_results["rate_sensitivity"][f"rate_{rate_move:+}bp"] = pnl_change
        
        return sensitivity_results
    
    def _price_single_leg(self, leg: Dict[str, Any]) -> float:
        """Price a single option leg"""
        inputs = MarketInputs(
            spot=leg["spot"],
            strike=leg["strike"],
            rate=leg.get("rate", 0.05),
            div_yield=leg.get("div_yield", 0.0),
            vol=leg["vol"],
            t=leg["expiry"]
        )
        
        result = VanillaBS.price(inputs, leg["right"])
        side_multiplier = 1 if leg.get("side", "long") == "long" else -1
        qty = leg.get("qty", 1)
        
        return result.price * side_multiplier * qty
    
    def _generate_hedge_recommendations(self, 
                                      portfolio_greeks: GreeksProfile, 
                                      legs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate intelligent hedging recommendations"""
        
        spot = legs[0]["spot"]
        vol = legs[0]["vol"]
        expiry = legs[0]["expiry"]
        
        recommendations = []
        
        # Delta hedging
        if abs(portfolio_greeks.delta) > 0.1:  # More than 10 delta exposure
            hedge_shares = -portfolio_greeks.delta * 100  # Convert to share equivalent
            recommendations.append({
                "type": "delta_hedge",
                "description": f"{'Buy' if hedge_shares > 0 else 'Sell'} {abs(hedge_shares):.0f} shares to neutralize delta",
                "action": "buy" if hedge_shares > 0 else "sell",
                "quantity": abs(hedge_shares),
                "instrument": "underlying_stock",
                "reason": f"Portfolio delta: {portfolio_greeks.delta:.3f}",
                "urgency": "high" if abs(portfolio_greeks.delta) > 0.5 else "medium"
            })
        
        # Gamma hedging
        if abs(portfolio_greeks.gamma) > 0.05:  # Significant gamma exposure
            # Recommend straddle or strangle to hedge gamma
            recommendations.append({
                "type": "gamma_hedge",
                "description": f"Consider {'selling' if portfolio_greeks.gamma > 0 else 'buying'} straddles to hedge gamma",
                "action": "sell" if portfolio_greeks.gamma > 0 else "buy",
                "quantity": abs(portfolio_greeks.gamma) * 50,  # Rough estimate
                "instrument": "atm_straddle",
                "reason": f"Portfolio gamma: {portfolio_greeks.gamma:.3f}",
                "urgency": "medium"
            })
        
        # Vega hedging
        if abs(portfolio_greeks.vega) > 5:  # More than $5 per vol point
            recommendations.append({
                "type": "vega_hedge",
                "description": f"Consider {'selling' if portfolio_greeks.vega > 0 else 'buying'} long-dated options to hedge vega",
                "action": "sell" if portfolio_greeks.vega > 0 else "buy",
                "quantity": abs(portfolio_greeks.vega) / 10,  # Rough estimate
                "instrument": "long_dated_options",
                "reason": f"Portfolio vega: {portfolio_greeks.vega:.1f}",
                "urgency": "medium" if abs(portfolio_greeks.vega) < 20 else "high"
            })
        
        # Theta management
        if portfolio_greeks.theta < -10:  # Losing more than $10/day to theta
            recommendations.append({
                "type": "theta_management",
                "description": "High time decay - consider closing positions or rolling to longer dates",
                "action": "manage",
                "quantity": 0,
                "instrument": "position_management",
                "reason": f"Daily theta decay: ${portfolio_greeks.theta:.2f}",
                "urgency": "high" if portfolio_greeks.theta < -50 else "medium"
            })
        
        return recommendations
    
    def calculate_portfolio_var(self, 
                               legs: List[Dict[str, Any]], 
                               confidence_level: float = 0.95,
                               holding_period_days: int = 1) -> Dict[str, float]:
        """Calculate Value at Risk for options portfolio"""
        
        portfolio_greeks = self.calculate_all_greeks(legs).portfolio_greeks
        spot = legs[0]["spot"]
        vol = legs[0]["vol"]
        
        # Convert to daily volatility
        daily_vol = vol / math.sqrt(252)
        
        # Calculate VaR components
        z_score = 1.645 if confidence_level == 0.95 else 2.33  # 95% or 99%
        time_scaling = math.sqrt(holding_period_days)
        
        # Delta VaR (linear risk)
        delta_var = portfolio_greeks.delta * spot * daily_vol * z_score * time_scaling
        
        # Gamma VaR (convexity adjustment)
        gamma_var = 0.5 * portfolio_greeks.gamma * (spot * daily_vol * z_score * time_scaling) ** 2
        
        # Vega VaR (volatility risk)
        vol_of_vol = 0.5  # Assume 50% vol of vol
        vega_var = portfolio_greeks.vega * vol * vol_of_vol * z_score * time_scaling
        
        # Theta VaR (time decay risk)
        theta_var = abs(portfolio_greeks.theta) * holding_period_days
        
        # Combined VaR (simplified - assumes independence)
        total_var = math.sqrt(delta_var**2 + vega_var**2) + gamma_var + theta_var
        
        return {
            "total_var": total_var,
            "delta_var": delta_var,
            "gamma_var": gamma_var,
            "vega_var": vega_var,
            "theta_var": theta_var,
            "confidence_level": confidence_level,
            "holding_period_days": holding_period_days
        }

# Initialize the Greeks calculator
greeks_calculator = AdvancedGreeksCalculator()