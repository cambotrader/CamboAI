"""
🎯 OPTIONS STRATEGIES API ROUTER
Complete REST API for all options strategies and analysis
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta

from app.services.options.strategy_library import options_strategy_library, StrategyType
from app.services.options.payoff_analyzer import payoff_analyzer
from app.services.options.greeks_calculator import greeks_calculator
from app.services.options.strategy_backtester import strategy_backtester, BacktestConfig
from app.services.options.trading_manager import order_manager, portfolio_monitor, strategy_recommender
from app.models.auth import get_current_user, User

router = APIRouter(prefix="/api/options/strategies", tags=["Options Strategies"])

# === REQUEST/RESPONSE MODELS ===

class StrategyPricingRequest(BaseModel):
    strategy_type: StrategyType
    spot: float
    base_strike: Optional[float] = None
    expiry_days: int = 30
    vol: float = 0.20
    rate: float = 0.05
    div_yield: float = 0.0

class PayoffAnalysisRequest(BaseModel):
    legs: List[Dict[str, Any]]
    current_spot: float
    spot_range: Optional[List[float]] = None
    at_expiration: bool = True

class BacktestRequest(BaseModel):
    strategy_type: StrategyType
    start_date: datetime
    end_date: datetime
    initial_capital: float = 100000
    entry_criteria: Dict[str, Any] = {}
    exit_criteria: Dict[str, Any] = {}
    position_sizing: Dict[str, Any] = {"method": "fixed_contracts", "contracts": 1}
    transaction_costs: Dict[str, float] = {"per_contract": 1.0}

class StrategyOrderRequest(BaseModel):
    strategy_type: StrategyType
    underlying_symbol: str
    spot_price: float
    vol: float = 0.20
    target_dte: int = 30
    position_size: int = 1
    custom_strikes: Optional[Dict[str, float]] = None

# === STRATEGY LIBRARY ENDPOINTS ===

@router.get("/list")
async def list_all_strategies():
    """Get list of all available options strategies"""
    strategies = options_strategy_library.list_all_strategies()
    
    strategy_details = []
    for strategy_name in strategies:
        config = options_strategy_library.get_strategy(strategy_name)
        strategy_details.append({
            "strategy_type": strategy_name,
            "name": config.name,
            "description": config.description,
            "market_outlook": config.market_outlook,
            "risk_level": _assess_risk_level(strategy_name),
            "leg_count": len(config.legs)
        })
    
    return {
        "total_strategies": len(strategies),
        "strategies": strategy_details
    }

@router.get("/filter")
async def filter_strategies(
    outlook: Optional[str] = Query(None, description="Market outlook filter"),
    volatility_effect: Optional[str] = Query(None, description="Volatility effect filter"),
    risk_level: Optional[str] = Query(None, description="Risk level filter")
):
    """Filter strategies by criteria"""
    
    all_strategies = options_strategy_library.list_all_strategies()
    filtered_strategies = []
    
    for strategy_name in all_strategies:
        config = options_strategy_library.get_strategy(strategy_name)
        
        # Apply filters
        if outlook and outlook.lower() not in config.market_outlook.lower():
            continue
        if volatility_effect and volatility_effect.lower() not in config.volatility_effect.lower():
            continue
        if risk_level and risk_level != _assess_risk_level(strategy_name):
            continue
            
        filtered_strategies.append({
            "strategy_type": strategy_name,
            "name": config.name,
            "description": config.description,
            "market_outlook": config.market_outlook,
            "volatility_effect": config.volatility_effect,
            "risk_level": _assess_risk_level(strategy_name)
        })
    
    return {
        "filters_applied": {
            "outlook": outlook,
            "volatility_effect": volatility_effect,
            "risk_level": risk_level
        },
        "matched_strategies": len(filtered_strategies),
        "strategies": filtered_strategies
    }

@router.get("/{strategy_type}/details")
async def get_strategy_details(strategy_type: StrategyType):
    """Get detailed information about a specific strategy"""
    
    config = options_strategy_library.get_strategy(strategy_type)
    if not config:
        raise HTTPException(status_code=404, detail=f"Strategy {strategy_type} not found")
    
    return {
        "strategy_type": strategy_type,
        "config": {
            "name": config.name,
            "description": config.description,
            "market_outlook": config.market_outlook,
            "max_profit": config.max_profit,
            "max_loss": config.max_loss,
            "breakeven": config.breakeven,
            "time_decay_effect": config.time_decay_effect,
            "volatility_effect": config.volatility_effect,
            "margin_requirement": config.margin_requirement,
            "legs": config.legs
        },
        "risk_assessment": _assess_risk_level(strategy_type),
        "complexity": "Simple" if len(config.legs) <= 2 else "Complex"
    }

# === STRATEGY PRICING ENDPOINTS ===

@router.post("/price")
async def price_strategy(request: StrategyPricingRequest):
    """Price any options strategy with current market data"""
    
    try:
        pricing_result = options_strategy_library.price_strategy(
            strategy_type=request.strategy_type,
            spot=request.spot,
            base_strike=request.base_strike,
            expiry=request.expiry_days / 365,
            vol=request.vol,
            rate=request.rate,
            div_yield=request.div_yield
        )
        
        return {
            "success": True,
            "strategy_type": request.strategy_type,
            "market_data": pricing_result["market_data"],
            "legs": pricing_result["legs"],
            "pricing": {
                "net_premium": pricing_result["pricing"]["price"],
                "total_greeks": pricing_result["pricing"]["greeks"],
                "individual_legs": pricing_result["pricing"]["legs"]
            },
            "strategy_info": {
                "name": pricing_result["strategy_config"].name,
                "description": pricing_result["strategy_config"].description,
                "market_outlook": pricing_result["strategy_config"].market_outlook
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Pricing error: {str(e)}")

@router.post("/batch-price")
async def batch_price_strategies(
    strategies: List[StrategyPricingRequest],
    current_user: User = Depends(get_current_user)
):
    """Price multiple strategies at once"""
    
    if len(strategies) > 20:
        raise HTTPException(status_code=400, detail="Maximum 20 strategies per batch")
    
    results = []
    
    for request in strategies:
        try:
            pricing_result = options_strategy_library.price_strategy(
                strategy_type=request.strategy_type,
                spot=request.spot,
                base_strike=request.base_strike,
                expiry=request.expiry_days / 365,
                vol=request.vol,
                rate=request.rate,
                div_yield=request.div_yield
            )
            
            results.append({
                "strategy_type": request.strategy_type,
                "success": True,
                "net_premium": pricing_result["pricing"]["price"],
                "total_greeks": pricing_result["pricing"]["greeks"],
                "risk_level": _assess_risk_level(request.strategy_type)
            })
            
        except Exception as e:
            results.append({
                "strategy_type": request.strategy_type,
                "success": False,
                "error": str(e)
            })
    
    return {
        "batch_results": results,
        "successful_pricings": len([r for r in results if r["success"]]),
        "failed_pricings": len([r for r in results if not r["success"]])
    }

# === PAYOFF ANALYSIS ENDPOINTS ===

@router.post("/payoff-analysis")
async def analyze_strategy_payoff(request: PayoffAnalysisRequest):
    """Complete payoff analysis with P&L curves and breakeven points"""
    
    try:
        spot_range = tuple(request.spot_range) if request.spot_range else None
        
        analysis = payoff_analyzer.analyze_strategy_payoff(
            legs=request.legs,
            current_spot=request.current_spot,
            spot_range=spot_range,
            at_expiration=request.at_expiration
        )
        
        # Generate chart data
        chart_data = payoff_analyzer.generate_payoff_chart_data(analysis)
        
        return {
            "success": True,
            "analysis": {
                "breakeven_points": analysis.breakeven_points,
                "max_profit": analysis.max_profit,
                "max_loss": analysis.max_loss,
                "profit_probability": analysis.profit_probability,
                "risk_reward_ratio": analysis.risk_reward_ratio
            },
            "strategy_summary": analysis.strategy_summary,
            "chart_data": chart_data,
            "payoff_points": len(analysis.payoff_curve)
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Payoff analysis error: {str(e)}")

@router.post("/compare-strategies")
async def compare_multiple_strategies(
    strategies_data: List[Dict[str, Any]],
    current_user: User = Depends(get_current_user)
):
    """Compare payoff profiles of multiple strategies"""
    
    if len(strategies_data) > 5:
        raise HTTPException(status_code=400, detail="Maximum 5 strategies for comparison")
    
    analyses = []
    
    for strategy_data in strategies_data:
        try:
            analysis = payoff_analyzer.analyze_strategy_payoff(
                legs=strategy_data["legs"],
                current_spot=strategy_data["current_spot"],
                at_expiration=strategy_data.get("at_expiration", True)
            )
            
            analyses.append((strategy_data.get("name", "Strategy"), analysis))
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error analyzing strategy: {str(e)}")
    
    # Generate comparison
    comparison = payoff_analyzer.compare_strategies(analyses)
    
    return {
        "success": True,
        "comparison": comparison,
        "strategies_compared": len(analyses)
    }

# === GREEKS ANALYSIS ENDPOINTS ===

@router.post("/greeks-analysis")
async def analyze_strategy_greeks(
    legs: List[Dict[str, Any]],
    include_second_order: bool = True
):
    """Complete Greeks analysis for any strategy"""
    
    try:
        analysis = greeks_calculator.calculate_all_greeks(legs, include_second_order)
        
        return {
            "success": True,
            "portfolio_greeks": {
                "delta": analysis.portfolio_greeks.delta,
                "gamma": analysis.portfolio_greeks.gamma,
                "theta": analysis.portfolio_greeks.theta,
                "vega": analysis.portfolio_greeks.vega,
                "rho": analysis.portfolio_greeks.rho
            },
            "second_order_greeks": {
                "vanna": analysis.portfolio_greeks.vanna,
                "charm": analysis.portfolio_greeks.charm,
                "volga": analysis.portfolio_greeks.volga,
                "veta": analysis.portfolio_greeks.veta,
                "speed": analysis.portfolio_greeks.speed,
                "color": analysis.portfolio_greeks.color
            } if include_second_order else None,
            "individual_legs": analysis.individual_greeks,
            "risk_metrics": analysis.risk_metrics,
            "hedge_recommendations": analysis.hedge_recommendations
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Greeks analysis error: {str(e)}")

@router.post("/portfolio-var")
async def calculate_portfolio_var(
    legs: List[Dict[str, Any]],
    confidence_level: float = 0.95,
    holding_period_days: int = 1
):
    """Calculate Value at Risk for options portfolio"""
    
    try:
        var_result = greeks_calculator.calculate_portfolio_var(
            legs, confidence_level, holding_period_days
        )
        
        return {
            "success": True,
            "var_analysis": var_result,
            "interpretation": {
                "total_risk": f"${abs(var_result['total_var']):.2f}",
                "confidence": f"{confidence_level*100}%",
                "holding_period": f"{holding_period_days} day(s)",
                "main_risk_source": _identify_main_risk_source(var_result)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"VaR calculation error: {str(e)}")

# === STRATEGY RECOMMENDATIONS ===

@router.post("/recommendations")
async def get_strategy_recommendations(
    market_conditions: Dict[str, Any],
    risk_tolerance: str = "moderate",
    account_size: float = 100000,
    current_user: User = Depends(get_current_user)
):
    """Get AI-powered strategy recommendations"""
    
    if risk_tolerance not in ["conservative", "moderate", "aggressive"]:
        raise HTTPException(status_code=400, detail="Risk tolerance must be: conservative, moderate, or aggressive")
    
    try:
        recommendations = strategy_recommender.recommend_strategies(
            market_conditions=market_conditions,
            risk_tolerance=risk_tolerance,
            account_size=account_size
        )
        
        return {
            "success": True,
            "market_conditions": market_conditions,
            "risk_tolerance": risk_tolerance,
            "recommendations": recommendations,
            "recommendation_count": len(recommendations)
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Recommendation error: {str(e)}")

# === UTILITY FUNCTIONS ===

def _assess_risk_level(strategy_type: str) -> str:
    """Assess risk level of strategy"""
    high_risk = ["short_call", "short_put", "short_straddle", "short_strangle", "call_backspread"]
    low_risk = ["long_call", "long_put", "bull_call_spread", "bear_put_spread", "iron_butterfly"]
    
    if strategy_type in high_risk:
        return "high"
    elif strategy_type in low_risk:
        return "low"
    else:
        return "medium"

def _identify_main_risk_source(var_result: Dict[str, float]) -> str:
    """Identify the main source of risk in VaR calculation"""
    components = {
        "Delta Risk": abs(var_result.get("delta_var", 0)),
        "Gamma Risk": abs(var_result.get("gamma_var", 0)),
        "Vega Risk": abs(var_result.get("vega_var", 0)),
        "Theta Risk": abs(var_result.get("theta_var", 0))
    }
    
    return max(components, key=components.get)

@router.get("/health")
async def health_check():
    """Health check for options strategies API"""
    return {
        "status": "healthy",
        "strategies_loaded": len(options_strategy_library.list_all_strategies()),
        "timestamp": datetime.now().isoformat()
    }