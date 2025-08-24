import numpy as np
import pandas as pd
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import yfinance as yf
from scipy import stats
import logging

logger = logging.getLogger(__name__)

class RiskCalculator:
    """Portfolio risk metrics calculator"""
    
    @staticmethod
    def calculate_returns(prices: List[float]) -> np.ndarray:
        """Calculate returns from price series"""
        prices_array = np.array(prices)
        returns = np.diff(prices_array) / prices_array[:-1]
        return returns
    
    @staticmethod
    def value_at_risk(returns: np.ndarray, confidence_level: float = 0.95) -> float:
        """Calculate Value at Risk (VaR)"""
        if len(returns) == 0:
            return 0.0
        
        return np.percentile(returns, (1 - confidence_level) * 100)
    
    @staticmethod
    def conditional_value_at_risk(returns: np.ndarray, confidence_level: float = 0.95) -> float:
        """Calculate Conditional Value at Risk (CVaR/Expected Shortfall)"""
        if len(returns) == 0:
            return 0.0
        
        var = RiskCalculator.value_at_risk(returns, confidence_level)
        return returns[returns <= var].mean()
    
    @staticmethod
    def sharpe_ratio(returns: np.ndarray, risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe ratio"""
        if len(returns) == 0 or np.std(returns) == 0:
            return 0.0
        
        excess_returns = returns - (risk_free_rate / 252)  # Daily risk-free rate
        return np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252)
    
    @staticmethod
    def sortino_ratio(returns: np.ndarray, risk_free_rate: float = 0.02) -> float:
        """Calculate Sortino ratio"""
        if len(returns) == 0:
            return 0.0
        
        excess_returns = returns - (risk_free_rate / 252)
        downside_returns = excess_returns[excess_returns < 0]
        
        if len(downside_returns) == 0:
            return float('inf')
        
        downside_deviation = np.std(downside_returns)
        if downside_deviation == 0:
            return float('inf')
        
        return np.mean(excess_returns) / downside_deviation * np.sqrt(252)
    
    @staticmethod
    def maximum_drawdown(prices: List[float]) -> Tuple[float, int, int]:
        """Calculate maximum drawdown and its duration"""
        if len(prices) == 0:
            return 0.0, 0, 0
        
        prices_array = np.array(prices)
        cumulative = np.cumprod(1 + RiskCalculator.calculate_returns(prices))
        running_max = np.maximum.accumulate(cumulative)
        drawdown = (cumulative - running_max) / running_max
        
        max_dd = np.min(drawdown)
        max_dd_idx = np.argmin(drawdown)
        
        # Find the start of the drawdown period
        start_idx = 0
        for i in range(max_dd_idx, -1, -1):
            if drawdown[i] == 0:
                start_idx = i
                break
        
        duration = max_dd_idx - start_idx
        return max_dd, start_idx, duration
    
    @staticmethod
    def beta(portfolio_returns: np.ndarray, market_returns: np.ndarray) -> float:
        """Calculate portfolio beta against market"""
        if len(portfolio_returns) == 0 or len(market_returns) == 0:
            return 0.0
        
        min_length = min(len(portfolio_returns), len(market_returns))
        portfolio_returns = portfolio_returns[-min_length:]
        market_returns = market_returns[-min_length:]
        
        covariance = np.cov(portfolio_returns, market_returns)[0, 1]
        market_variance = np.var(market_returns)
        
        if market_variance == 0:
            return 0.0
        
        return covariance / market_variance
    
    @staticmethod
    def alpha(portfolio_returns: np.ndarray, market_returns: np.ndarray, risk_free_rate: float = 0.02) -> float:
        """Calculate portfolio alpha"""
        if len(portfolio_returns) == 0:
            return 0.0
        
        beta = RiskCalculator.beta(portfolio_returns, market_returns)
        portfolio_return = np.mean(portfolio_returns) * 252
        market_return = np.mean(market_returns) * 252 if len(market_returns) > 0 else 0
        
        return portfolio_return - (risk_free_rate + beta * (market_return - risk_free_rate))
    
    @staticmethod
    def volatility(returns: np.ndarray) -> float:
        """Calculate annualized volatility"""
        if len(returns) == 0:
            return 0.0
        
        return np.std(returns) * np.sqrt(252)
    
    @staticmethod
    def information_ratio(portfolio_returns: np.ndarray, benchmark_returns: np.ndarray) -> float:
        """Calculate information ratio"""
        if len(portfolio_returns) == 0 or len(benchmark_returns) == 0:
            return 0.0
        
        min_length = min(len(portfolio_returns), len(benchmark_returns))
        portfolio_returns = portfolio_returns[-min_length:]
        benchmark_returns = benchmark_returns[-min_length:]
        
        excess_returns = portfolio_returns - benchmark_returns
        tracking_error = np.std(excess_returns)
        
        if tracking_error == 0:
            return 0.0
        
        return np.mean(excess_returns) / tracking_error * np.sqrt(252)

class PortfolioRiskAnalyzer:
    """Complete portfolio risk analysis"""
    
    def __init__(self, risk_free_rate: float = 0.02, benchmark_symbol: str = 'SPY'):
        self.risk_free_rate = risk_free_rate
        self.benchmark_symbol = benchmark_symbol
        self.benchmark_data = None
        
    def get_benchmark_data(self, start_date: datetime, end_date: datetime) -> np.ndarray:
        """Get benchmark returns for the period"""
        try:
            if self.benchmark_data is None:
                ticker = yf.Ticker(self.benchmark_symbol)
                data = ticker.history(start=start_date, end=end_date)
                if not data.empty:
                    self.benchmark_data = RiskCalculator.calculate_returns(data['Close'].values)
                else:
                    self.benchmark_data = np.array([])
            
            return self.benchmark_data
        except Exception as e:
            logger.error(f"Error fetching benchmark data: {e}")
            return np.array([])
    
    def analyze_portfolio_risk(self, portfolio_values: List[float], dates: List[datetime]) -> Dict:
        """Comprehensive portfolio risk analysis"""
        if len(portfolio_values) < 2:
            return self._empty_risk_metrics()
        
        # Calculate portfolio returns
        portfolio_returns = RiskCalculator.calculate_returns(portfolio_values)
        
        # Get benchmark data for the same period
        start_date = min(dates)
        end_date = max(dates)
        benchmark_returns = self.get_benchmark_data(start_date, end_date)
        
        # Calculate risk metrics
        var_95 = RiskCalculator.value_at_risk(portfolio_returns, 0.95)
        var_99 = RiskCalculator.value_at_risk(portfolio_returns, 0.99)
        cvar_95 = RiskCalculator.conditional_value_at_risk(portfolio_returns, 0.95)
        cvar_99 = RiskCalculator.conditional_value_at_risk(portfolio_returns, 0.99)
        
        sharpe = RiskCalculator.sharpe_ratio(portfolio_returns, self.risk_free_rate)
        sortino = RiskCalculator.sortino_ratio(portfolio_returns, self.risk_free_rate)
        
        max_dd, dd_start, dd_duration = RiskCalculator.maximum_drawdown(portfolio_values)
        
        volatility = RiskCalculator.volatility(portfolio_returns)
        
        # Market-relative metrics
        beta = RiskCalculator.beta(portfolio_returns, benchmark_returns) if len(benchmark_returns) > 0 else 0
        alpha = RiskCalculator.alpha(portfolio_returns, benchmark_returns, self.risk_free_rate) if len(benchmark_returns) > 0 else 0
        info_ratio = RiskCalculator.information_ratio(portfolio_returns, benchmark_returns) if len(benchmark_returns) > 0 else 0
        
        # Portfolio statistics
        total_return = (portfolio_values[-1] - portfolio_values[0]) / portfolio_values[0] if portfolio_values[0] != 0 else 0
        annualized_return = (1 + total_return) ** (252 / len(portfolio_values)) - 1 if len(portfolio_values) > 0 else 0
        
        # Win/Loss statistics
        positive_returns = portfolio_returns[portfolio_returns > 0]
        negative_returns = portfolio_returns[portfolio_returns < 0]
        
        win_rate = len(positive_returns) / len(portfolio_returns) if len(portfolio_returns) > 0 else 0
        avg_win = np.mean(positive_returns) if len(positive_returns) > 0 else 0
        avg_loss = np.mean(negative_returns) if len(negative_returns) > 0 else 0
        profit_factor = abs(np.sum(positive_returns) / np.sum(negative_returns)) if np.sum(negative_returns) != 0 else float('inf')
        
        return {
            'risk_metrics': {
                'value_at_risk_95': float(var_95),
                'value_at_risk_99': float(var_99),
                'conditional_var_95': float(cvar_95),
                'conditional_var_99': float(cvar_99),
                'sharpe_ratio': float(sharpe),
                'sortino_ratio': float(sortino),
                'information_ratio': float(info_ratio),
                'maximum_drawdown': float(max_dd),
                'drawdown_duration': int(dd_duration),
                'volatility': float(volatility),
                'beta': float(beta),
                'alpha': float(alpha)
            },
            'performance_metrics': {
                'total_return': float(total_return),
                'annualized_return': float(annualized_return),
                'win_rate': float(win_rate),
                'average_win': float(avg_win),
                'average_loss': float(avg_loss),
                'profit_factor': float(profit_factor) if profit_factor != float('inf') else None,
                'best_day': float(np.max(portfolio_returns)) if len(portfolio_returns) > 0 else 0,
                'worst_day': float(np.min(portfolio_returns)) if len(portfolio_returns) > 0 else 0
            },
            'portfolio_stats': {
                'current_value': float(portfolio_values[-1]),
                'initial_value': float(portfolio_values[0]),
                'peak_value': float(np.max(portfolio_values)),
                'trough_value': float(np.min(portfolio_values)),
                'days_analyzed': len(portfolio_values),
                'analysis_period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                }
            },
            'risk_assessment': self._assess_risk_level(sharpe, max_dd, volatility),
            'recommendations': self._generate_recommendations(sharpe, max_dd, volatility, win_rate)
        }
    
    def _empty_risk_metrics(self) -> Dict:
        """Return empty risk metrics structure"""
        return {
            'risk_metrics': {
                'value_at_risk_95': 0.0,
                'value_at_risk_99': 0.0,
                'conditional_var_95': 0.0,
                'conditional_var_99': 0.0,
                'sharpe_ratio': 0.0,
                'sortino_ratio': 0.0,
                'information_ratio': 0.0,
                'maximum_drawdown': 0.0,
                'drawdown_duration': 0,
                'volatility': 0.0,
                'beta': 0.0,
                'alpha': 0.0
            },
            'performance_metrics': {
                'total_return': 0.0,
                'annualized_return': 0.0,
                'win_rate': 0.0,
                'average_win': 0.0,
                'average_loss': 0.0,
                'profit_factor': None,
                'best_day': 0.0,
                'worst_day': 0.0
            },
            'portfolio_stats': {
                'current_value': 0.0,
                'initial_value': 0.0,
                'peak_value': 0.0,
                'trough_value': 0.0,
                'days_analyzed': 0,
                'analysis_period': {
                    'start_date': datetime.now().isoformat(),
                    'end_date': datetime.now().isoformat()
                }
            },
            'risk_assessment': 'INSUFFICIENT_DATA',
            'recommendations': ['Insufficient data for analysis']
        }
    
    def _assess_risk_level(self, sharpe_ratio: float, max_drawdown: float, volatility: float) -> str:
        """Assess overall risk level"""
        risk_score = 0
        
        # Sharpe ratio assessment
        if sharpe_ratio < 0:
            risk_score += 3
        elif sharpe_ratio < 0.5:
            risk_score += 2
        elif sharpe_ratio < 1.0:
            risk_score += 1
        
        # Max drawdown assessment
        if abs(max_drawdown) > 0.3:  # 30%+
            risk_score += 3
        elif abs(max_drawdown) > 0.2:  # 20-30%
            risk_score += 2
        elif abs(max_drawdown) > 0.1:  # 10-20%
            risk_score += 1
        
        # Volatility assessment
        if volatility > 0.4:  # 40%+
            risk_score += 3
        elif volatility > 0.25:  # 25-40%
            risk_score += 2
        elif volatility > 0.15:  # 15-25%
            risk_score += 1
        
        if risk_score >= 7:
            return 'VERY_HIGH'
        elif risk_score >= 5:
            return 'HIGH'
        elif risk_score >= 3:
            return 'MODERATE'
        elif risk_score >= 1:
            return 'LOW'
        else:
            return 'VERY_LOW'
    
    def _generate_recommendations(self, sharpe_ratio: float, max_drawdown: float, 
                                volatility: float, win_rate: float) -> List[str]:
        """Generate risk management recommendations"""
        recommendations = []
        
        if sharpe_ratio < 0.5:
            recommendations.append("Consider improving risk-adjusted returns through better diversification")
        
        if abs(max_drawdown) > 0.2:
            recommendations.append("Implement stop-loss strategies to limit downside risk")
        
        if volatility > 0.3:
            recommendations.append("Reduce portfolio volatility through asset allocation adjustments")
        
        if win_rate < 0.4:
            recommendations.append("Review trading strategy - low win rate may indicate poor entry/exit timing")
        
        if len(recommendations) == 0:
            recommendations.append("Portfolio risk metrics are within acceptable ranges")
        
        return recommendations
