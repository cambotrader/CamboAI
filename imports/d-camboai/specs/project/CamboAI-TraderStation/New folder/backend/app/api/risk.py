from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from ..services.risk_service import PortfolioRiskAnalyzer
from ..services.database_service import PortfolioService, PerformanceService
from ..models.auth import get_current_user, User
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/risk", tags=["risk"])

@router.get("/portfolio/{portfolio_id}/analysis")
async def get_portfolio_risk_analysis(
    portfolio_id: str,
    days: int = Query(90, ge=1, le=365, description="Number of days to analyze"),
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive risk analysis for a portfolio"""
    try:
        portfolio_service = PortfolioService()
        performance_service = PerformanceService()
        
        # Verify portfolio ownership
        portfolio = await portfolio_service.get_portfolio(portfolio_id)
        if not portfolio or portfolio.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        
        # Get performance data for the specified period
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        performance_records = await performance_service.get_performance_history(
            portfolio_id, start_date, end_date
        )
        
        if not performance_records:
            raise HTTPException(
                status_code=404, 
                detail="Insufficient performance data for risk analysis"
            )
        
        # Extract portfolio values and dates
        portfolio_values = [record.total_value for record in performance_records]
        dates = [record.date for record in performance_records]
        
        # Perform risk analysis
        risk_analyzer = PortfolioRiskAnalyzer()
        risk_analysis = risk_analyzer.analyze_portfolio_risk(portfolio_values, dates)
        
        return {
            "portfolio_id": portfolio_id,
            "portfolio_name": portfolio.name,
            "analysis_period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days_analyzed": len(portfolio_values)
            },
            "risk_analysis": risk_analysis
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error performing risk analysis: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/portfolio/{portfolio_id}/alerts")
async def get_risk_alerts(
    portfolio_id: str,
    active_only: bool = Query(True, description="Return only active alerts"),
    current_user: User = Depends(get_current_user)
):
    """Get risk alerts for a portfolio"""
    try:
        portfolio_service = PortfolioService()
        
        # Verify portfolio ownership
        portfolio = await portfolio_service.get_portfolio(portfolio_id)
        if not portfolio or portfolio.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        
        # Get current risk metrics to check against thresholds
        risk_analyzer = PortfolioRiskAnalyzer()
        performance_service = PerformanceService()
        
        # Get recent performance data (last 30 days)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        
        performance_records = await performance_service.get_performance_history(
            portfolio_id, start_date, end_date
        )
        
        alerts = []
        
        if performance_records:
            portfolio_values = [record.total_value for record in performance_records]
            dates = [record.date for record in performance_records]
            
            risk_analysis = risk_analyzer.analyze_portfolio_risk(portfolio_values, dates)
            
            # Check various risk thresholds
            current_time = datetime.utcnow()
            
            # Maximum drawdown alert
            max_dd = abs(risk_analysis['risk_metrics']['maximum_drawdown'])
            if max_dd > 0.15:  # 15% drawdown threshold
                alerts.append({
                    "id": f"dd_{portfolio_id}_{int(current_time.timestamp())}",
                    "type": "DRAWDOWN_WARNING",
                    "severity": "HIGH" if max_dd > 0.25 else "MEDIUM",
                    "title": "High Drawdown Alert",
                    "message": f"Portfolio has experienced a {max_dd:.1%} drawdown",
                    "value": max_dd,
                    "threshold": 0.15,
                    "created_at": current_time.isoformat(),
                    "is_active": True
                })
            
            # Volatility alert
            volatility = risk_analysis['risk_metrics']['volatility']
            if volatility > 0.25:  # 25% annualized volatility threshold
                alerts.append({
                    "id": f"vol_{portfolio_id}_{int(current_time.timestamp())}",
                    "type": "VOLATILITY_WARNING",
                    "severity": "HIGH" if volatility > 0.4 else "MEDIUM",
                    "title": "High Volatility Alert",
                    "message": f"Portfolio volatility is {volatility:.1%} (annualized)",
                    "value": volatility,
                    "threshold": 0.25,
                    "created_at": current_time.isoformat(),
                    "is_active": True
                })
            
            # Sharpe ratio alert
            sharpe = risk_analysis['risk_metrics']['sharpe_ratio']
            if sharpe < 0.5:
                alerts.append({
                    "id": f"sharpe_{portfolio_id}_{int(current_time.timestamp())}",
                    "type": "PERFORMANCE_WARNING",
                    "severity": "HIGH" if sharpe < 0 else "MEDIUM",
                    "title": "Poor Risk-Adjusted Returns",
                    "message": f"Sharpe ratio is {sharpe:.2f}, indicating poor risk-adjusted performance",
                    "value": sharpe,
                    "threshold": 0.5,
                    "created_at": current_time.isoformat(),
                    "is_active": True
                })
            
            # Value at Risk alert
            var_95 = abs(risk_analysis['risk_metrics']['value_at_risk_95'])
            if var_95 > 0.05:  # 5% daily VaR threshold
                alerts.append({
                    "id": f"var_{portfolio_id}_{int(current_time.timestamp())}",
                    "type": "VAR_WARNING",
                    "severity": "HIGH" if var_95 > 0.1 else "MEDIUM",
                    "title": "High Value at Risk",
                    "message": f"95% VaR is {var_95:.1%}, indicating high potential daily losses",
                    "value": var_95,
                    "threshold": 0.05,
                    "created_at": current_time.isoformat(),
                    "is_active": True
                })
        
        # Filter active alerts if requested
        if active_only:
            alerts = [alert for alert in alerts if alert.get('is_active', True)]
        
        return {
            "portfolio_id": portfolio_id,
            "alerts": alerts,
            "alert_count": len(alerts),
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting risk alerts: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/metrics/definitions")
async def get_risk_metrics_definitions():
    """Get definitions and explanations of risk metrics"""
    return {
        "risk_metrics": {
            "value_at_risk_95": {
                "name": "Value at Risk (95%)",
                "description": "Maximum expected loss over one day with 95% confidence",
                "interpretation": "Lower (more negative) values indicate higher risk",
                "good_range": "> -0.02 (less than 2% daily loss)",
                "unit": "percentage"
            },
            "value_at_risk_99": {
                "name": "Value at Risk (99%)",
                "description": "Maximum expected loss over one day with 99% confidence",
                "interpretation": "Lower (more negative) values indicate higher risk",
                "good_range": "> -0.03 (less than 3% daily loss)",
                "unit": "percentage"
            },
            "conditional_var_95": {
                "name": "Conditional Value at Risk (95%)",
                "description": "Expected loss on days when VaR threshold is exceeded",
                "interpretation": "Lower (more negative) values indicate higher tail risk",
                "good_range": "> -0.03 (less than 3% expected loss)",
                "unit": "percentage"
            },
            "sharpe_ratio": {
                "name": "Sharpe Ratio",
                "description": "Risk-adjusted return measure (excess return per unit of risk)",
                "interpretation": "Higher values indicate better risk-adjusted performance",
                "good_range": "> 1.0 (excellent), > 0.5 (good)",
                "unit": "ratio"
            },
            "sortino_ratio": {
                "name": "Sortino Ratio",
                "description": "Risk-adjusted return focusing only on downside risk",
                "interpretation": "Higher values indicate better downside-adjusted performance",
                "good_range": "> 1.0 (excellent), > 0.5 (good)",
                "unit": "ratio"
            },
            "maximum_drawdown": {
                "name": "Maximum Drawdown",
                "description": "Largest peak-to-trough decline in portfolio value",
                "interpretation": "Lower absolute values indicate better downside protection",
                "good_range": "< 0.10 (less than 10% decline)",
                "unit": "percentage"
            },
            "volatility": {
                "name": "Annualized Volatility",
                "description": "Standard deviation of returns, annualized",
                "interpretation": "Lower values indicate more stable returns",
                "good_range": "< 0.20 (less than 20% annual volatility)",
                "unit": "percentage"
            },
            "beta": {
                "name": "Beta",
                "description": "Sensitivity to market movements (relative to S&P 500)",
                "interpretation": "1.0 = market level risk, >1.0 = higher risk, <1.0 = lower risk",
                "good_range": "0.8 - 1.2 (depending on strategy)",
                "unit": "ratio"
            },
            "alpha": {
                "name": "Alpha",
                "description": "Excess return above what beta would predict",
                "interpretation": "Positive values indicate outperformance vs. market",
                "good_range": "> 0.02 (positive alpha preferred)",
                "unit": "percentage"
            }
        },
        "risk_levels": {
            "VERY_LOW": "Excellent risk profile with strong metrics across all measures",
            "LOW": "Good risk profile with acceptable metrics",
            "MODERATE": "Moderate risk with some areas for improvement",
            "HIGH": "Elevated risk requiring attention and potential adjustments",
            "VERY_HIGH": "High risk profile requiring immediate risk management actions"
        },
        "alert_types": {
            "DRAWDOWN_WARNING": "Portfolio has experienced significant losses from peak",
            "VOLATILITY_WARNING": "Portfolio returns are highly volatile",
            "PERFORMANCE_WARNING": "Poor risk-adjusted returns",
            "VAR_WARNING": "High potential for daily losses",
            "CONCENTRATION_WARNING": "Portfolio lacks diversification"
        }
    }

@router.post("/portfolio/{portfolio_id}/stress-test")
async def run_stress_test(
    portfolio_id: str,
    scenarios: Dict = None,
    current_user: User = Depends(get_current_user)
):
    """Run stress tests on portfolio under various market scenarios"""
    try:
        portfolio_service = PortfolioService()
        
        # Verify portfolio ownership
        portfolio = await portfolio_service.get_portfolio(portfolio_id)
        if not portfolio or portfolio.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        
        # Default stress test scenarios if none provided
        if not scenarios:
            scenarios = {
                "market_crash": {"market_return": -0.20, "volatility_multiplier": 2.0},
                "moderate_decline": {"market_return": -0.10, "volatility_multiplier": 1.5},
                "high_volatility": {"market_return": 0.0, "volatility_multiplier": 2.5},
                "interest_rate_shock": {"market_return": -0.05, "bond_impact": -0.15},
                "sector_rotation": {"growth_impact": -0.15, "value_impact": 0.05}
            }
        
        # Get current portfolio composition
        positions = await portfolio_service.get_positions(portfolio_id)
        
        stress_results = {}
        
        for scenario_name, scenario_params in scenarios.items():
            # Simulate portfolio impact under scenario
            # This is a simplified stress test - in production you'd use more sophisticated models
            
            market_return = scenario_params.get("market_return", 0.0)
            volatility_multiplier = scenario_params.get("volatility_multiplier", 1.0)
            
            scenario_impact = 0.0
            portfolio_value = sum(pos.current_value for pos in positions)
            
            for position in positions:
                # Apply market beta impact
                position_beta = getattr(position, 'beta', 1.0)  # Default beta if not available
                position_impact = market_return * position_beta * volatility_multiplier
                
                # Weight by position size
                position_weight = position.current_value / portfolio_value if portfolio_value > 0 else 0
                scenario_impact += position_impact * position_weight
            
            stress_results[scenario_name] = {
                "scenario_description": scenario_params,
                "portfolio_impact": scenario_impact,
                "estimated_loss": portfolio_value * abs(scenario_impact) if scenario_impact < 0 else 0,
                "scenario_severity": "HIGH" if abs(scenario_impact) > 0.15 else "MEDIUM" if abs(scenario_impact) > 0.05 else "LOW"
            }
        
        return {
            "portfolio_id": portfolio_id,
            "current_portfolio_value": portfolio_value,
            "stress_test_results": stress_results,
            "worst_case_scenario": max(stress_results.items(), key=lambda x: abs(x[1]["portfolio_impact"]))[0],
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error running stress test: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
