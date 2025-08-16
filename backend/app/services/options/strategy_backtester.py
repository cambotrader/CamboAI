"""
📊 OPTIONS STRATEGY BACKTESTING ENGINE
Complete historical backtesting, performance analysis, and strategy optimization
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Tuple, Callable
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import math
from .engine import MarketInputs, VanillaBS
from .strategy_library import OptionsStrategyLibrary, StrategyType

@dataclass
class BacktestConfig:
    start_date: datetime
    end_date: datetime
    initial_capital: float
    strategy_type: StrategyType
    entry_criteria: Dict[str, Any]
    exit_criteria: Dict[str, Any]
    position_sizing: Dict[str, Any]
    transaction_costs: Dict[str, float]
    slippage: float
    max_positions: int

@dataclass
class Trade:
    entry_date: datetime
    exit_date: Optional[datetime]
    strategy_type: StrategyType
    legs: List[Dict[str, Any]]
    entry_price: float
    exit_price: Optional[float]
    pnl: Optional[float]
    max_profit: Optional[float]
    max_loss: Optional[float]
    days_held: Optional[int]
    exit_reason: str

@dataclass
class BacktestResults:
    trades: List[Trade]
    performance_metrics: Dict[str, float]
    equity_curve: pd.DataFrame
    drawdown_analysis: Dict[str, float]
    strategy_stats: Dict[str, Any]
    risk_metrics: Dict[str, float]

class OptionsStrategyBacktester:
    """Complete options strategy backtesting and performance analysis"""
    
    def __init__(self):
        self.strategy_lib = OptionsStrategyLibrary()
        
    def run_backtest(self, 
                    config: BacktestConfig,
                    market_data: pd.DataFrame) -> BacktestResults:
        """
        Run complete options strategy backtest
        
        market_data should contain: ['date', 'spot', 'vol', 'rate', 'div_yield']
        """
        
        trades = []
        equity_curve_data = []
        current_capital = config.initial_capital
        active_positions = []
        
        # Sort market data by date
        market_data = market_data.sort_values('date').reset_index(drop=True)
        
        for i, row in market_data.iterrows():
            current_date = pd.to_datetime(row['date'])
            spot = row['spot']
            vol = row['vol']
            rate = row.get('rate', 0.05)
            div_yield = row.get('div_yield', 0.0)
            
            # Check exit conditions for active positions
            active_positions, closed_trades = self._check_exit_conditions(
                active_positions, current_date, spot, vol, rate, div_yield, config.exit_criteria
            )
            trades.extend(closed_trades)
            
            # Check entry conditions for new positions
            if len(active_positions) < config.max_positions:
                new_position = self._check_entry_conditions(
                    config, current_date, spot, vol, rate, div_yield
                )
                if new_position:
                    active_positions.append(new_position)
            
            # Calculate current portfolio value
            portfolio_value = self._calculate_portfolio_value(
                active_positions, current_date, spot, vol, rate, div_yield
            )
            
            current_capital = config.initial_capital + sum(t.pnl for t in trades if t.pnl is not None)
            total_value = current_capital + portfolio_value
            
            equity_curve_data.append({
                'date': current_date,
                'capital': current_capital,
                'portfolio_value': portfolio_value,
                'total_value': total_value,
                'active_positions': len(active_positions)
            })
        
        # Close any remaining positions at end date
        final_trades, _ = self._close_all_positions(
            active_positions, config.end_date, market_data.iloc[-1]
        )
        trades.extend(final_trades)
        
        # Create equity curve DataFrame
        equity_curve = pd.DataFrame(equity_curve_data)
        
        # Calculate performance metrics
        performance_metrics = self._calculate_performance_metrics(equity_curve, trades)
        
        # Calculate drawdown analysis
        drawdown_analysis = self._calculate_drawdown_analysis(equity_curve)
        
        # Generate strategy statistics
        strategy_stats = self._generate_strategy_stats(trades, config)
        
        # Calculate risk metrics
        risk_metrics = self._calculate_risk_metrics(equity_curve)
        
        return BacktestResults(
            trades=trades,
            performance_metrics=performance_metrics,
            equity_curve=equity_curve,
            drawdown_analysis=drawdown_analysis,
            strategy_stats=strategy_stats,
            risk_metrics=risk_metrics
        )
    
    def _check_entry_conditions(self, 
                               config: BacktestConfig,
                               date: datetime,
                               spot: float,
                               vol: float,
                               rate: float,
                               div_yield: float) -> Optional[Trade]:
        """Check if entry conditions are met and create new position"""
        
        entry_criteria = config.entry_criteria
        
        # Volume expansion filter
        if 'min_vol' in entry_criteria and vol < entry_criteria['min_vol']:
            return None
        if 'max_vol' in entry_criteria and vol > entry_criteria['max_vol']:
            return None
        
        # Technical indicators (simplified)
        if 'rsi_range' in entry_criteria:
            # Placeholder for RSI calculation
            rsi = 50  # Would calculate from price data
            if not (entry_criteria['rsi_range'][0] <= rsi <= entry_criteria['rsi_range'][1]):
                return None
        
        # Volatility rank/percentile
        if 'vol_rank_min' in entry_criteria:
            # Placeholder for vol rank calculation
            vol_rank = 50  # Would calculate rolling vol percentile
            if vol_rank < entry_criteria['vol_rank_min']:
                return None
        
        # Days to expiration
        dte = entry_criteria.get('days_to_expiration', 30)
        expiry = dte / 365
        
        # Build strategy legs
        legs = self.strategy_lib.build_strategy_legs(
            config.strategy_type,
            spot=spot,
            base_strike=spot,  # ATM entry
            expiry=expiry,
            vol=vol,
            rate=rate,
            div_yield=div_yield
        )
        
        # Calculate entry price (net premium)
        entry_price = sum(
            self._price_leg(leg) * leg.get('qty', 1) * 
            (1 if leg.get('side', 'long') == 'long' else -1)
            for leg in legs
        )
        
        # Apply transaction costs
        total_cost = sum(abs(self._price_leg(leg)) * config.transaction_costs.get('per_contract', 1.0)
                        for leg in legs)
        entry_price -= total_cost
        
        # Position sizing
        position_size = self._calculate_position_size(
            config.position_sizing, config.initial_capital, entry_price
        )
        
        # Scale legs by position size
        for leg in legs:
            leg['qty'] = leg.get('qty', 1) * position_size
        
        return Trade(
            entry_date=date,
            exit_date=None,
            strategy_type=config.strategy_type,
            legs=legs,
            entry_price=entry_price * position_size,
            exit_price=None,
            pnl=None,
            max_profit=None,
            max_loss=None,
            days_held=None,
            exit_reason=""
        )
    
    def _check_exit_conditions(self, 
                              active_positions: List[Trade],
                              date: datetime,
                              spot: float,
                              vol: float,
                              rate: float,
                              div_yield: float,
                              exit_criteria: Dict[str, Any]) -> Tuple[List[Trade], List[Trade]]:
        """Check exit conditions and close positions if met"""
        
        remaining_positions = []
        closed_trades = []
        
        for position in active_positions:
            should_exit, exit_reason = self._evaluate_exit_conditions(
                position, date, spot, vol, rate, div_yield, exit_criteria
            )
            
            if should_exit:
                # Calculate current position value
                current_value = sum(
                    self._price_leg({**leg, "spot": spot, "vol": vol, 
                                   "rate": rate, "div_yield": div_yield}) * 
                    leg.get('qty', 1) * (1 if leg.get('side', 'long') == 'long' else -1)
                    for leg in position.legs
                )
                
                # Complete the trade
                position.exit_date = date
                position.exit_price = current_value
                position.pnl = current_value - position.entry_price
                position.days_held = (date - position.entry_date).days
                position.exit_reason = exit_reason
                
                closed_trades.append(position)
            else:
                remaining_positions.append(position)
        
        return remaining_positions, closed_trades
    
    def _evaluate_exit_conditions(self, 
                                 position: Trade,
                                 date: datetime,
                                 spot: float,
                                 vol: float,
                                 rate: float,
                                 div_yield: float,
                                 exit_criteria: Dict[str, Any]) -> Tuple[bool, str]:
        """Evaluate if position should be exited"""
        
        # Time-based exit
        days_held = (date - position.entry_date).days
        if 'max_days' in exit_criteria and days_held >= exit_criteria['max_days']:
            return True, "max_days_reached"
        
        # Days to expiration
        if 'exit_dte' in exit_criteria:
            # Calculate remaining DTE for shortest expiry leg
            min_expiry = min(leg['expiry'] for leg in position.legs)
            remaining_dte = min_expiry * 365
            if remaining_dte <= exit_criteria['exit_dte']:
                return True, "exit_dte_reached"
        
        # P&L based exits
        current_value = sum(
            self._price_leg({**leg, "spot": spot, "vol": vol, 
                           "rate": rate, "div_yield": div_yield}) * 
            leg.get('qty', 1) * (1 if leg.get('side', 'long') == 'long' else -1)
            for leg in position.legs
        )
        current_pnl = current_value - position.entry_price
        pnl_pct = current_pnl / abs(position.entry_price) if position.entry_price != 0 else 0
        
        # Profit target
        if 'profit_target_pct' in exit_criteria and pnl_pct >= exit_criteria['profit_target_pct']:
            return True, "profit_target"
        
        # Stop loss
        if 'stop_loss_pct' in exit_criteria and pnl_pct <= -exit_criteria['stop_loss_pct']:
            return True, "stop_loss"
        
        # Volatility expansion exit
        if 'vol_expansion_exit' in exit_criteria:
            # Compare current vol to entry vol
            entry_vol = position.legs[0]['vol']  # Use first leg's entry vol
            vol_change = (vol - entry_vol) / entry_vol
            if vol_change >= exit_criteria['vol_expansion_exit']:
                return True, "vol_expansion"
        
        return False, ""
    
    def _price_leg(self, leg: Dict[str, Any]) -> float:
        """Price a single option leg"""
        inputs = MarketInputs(
            spot=leg["spot"],
            strike=leg["strike"],
            rate=leg.get("rate", 0.05),
            div_yield=leg.get("div_yield", 0.0),
            vol=leg["vol"],
            t=leg.get("expiry", 0.0833)
        )
        
        result = VanillaBS.price(inputs, leg["right"])
        return result.price
    
    def _calculate_position_size(self, 
                                position_sizing: Dict[str, Any],
                                capital: float,
                                entry_price: float) -> int:
        """Calculate position size based on sizing rules"""
        
        sizing_method = position_sizing.get('method', 'fixed_contracts')
        
        if sizing_method == 'fixed_contracts':
            return position_sizing.get('contracts', 1)
        
        elif sizing_method == 'percent_capital':
            pct = position_sizing.get('percent', 0.02)  # 2% default
            max_risk = capital * pct
            return max(1, int(max_risk / abs(entry_price)))
        
        elif sizing_method == 'kelly':
            # Kelly criterion (simplified)
            win_rate = position_sizing.get('win_rate', 0.5)
            avg_win = position_sizing.get('avg_win', 1.0)
            avg_loss = position_sizing.get('avg_loss', 1.0)
            
            kelly_pct = (win_rate * avg_win - (1 - win_rate) * avg_loss) / avg_win
            kelly_pct = max(0, min(kelly_pct, 0.25))  # Cap at 25%
            
            risk_amount = capital * kelly_pct
            return max(1, int(risk_amount / abs(entry_price)))
        
        return 1
    
    def _calculate_portfolio_value(self,
                                  positions: List[Trade],
                                  date: datetime,
                                  spot: float,
                                  vol: float,
                                  rate: float,
                                  div_yield: float) -> float:
        """Calculate current value of all active positions"""
        
        total_value = 0.0
        
        for position in positions:
            position_value = sum(
                self._price_leg({**leg, "spot": spot, "vol": vol, 
                               "rate": rate, "div_yield": div_yield}) * 
                leg.get('qty', 1) * (1 if leg.get('side', 'long') == 'long' else -1)
                for leg in position.legs
            )
            total_value += position_value
        
        return total_value
    
    def _close_all_positions(self,
                            positions: List[Trade],
                            date: datetime,
                            market_row: pd.Series) -> Tuple[List[Trade], float]:
        """Close all remaining positions at final date"""
        
        closed_trades = []
        total_pnl = 0.0
        
        spot = market_row['spot']
        vol = market_row['vol']
        rate = market_row.get('rate', 0.05)
        div_yield = market_row.get('div_yield', 0.0)
        
        for position in positions:
            current_value = sum(
                self._price_leg({**leg, "spot": spot, "vol": vol, 
                               "rate": rate, "div_yield": div_yield}) * 
                leg.get('qty', 1) * (1 if leg.get('side', 'long') == 'long' else -1)
                for leg in position.legs
            )
            
            position.exit_date = date
            position.exit_price = current_value
            position.pnl = current_value - position.entry_price
            position.days_held = (date - position.entry_date).days
            position.exit_reason = "backtest_end"
            
            closed_trades.append(position)
            total_pnl += position.pnl
        
        return closed_trades, total_pnl
    
    def _calculate_performance_metrics(self, 
                                     equity_curve: pd.DataFrame,
                                     trades: List[Trade]) -> Dict[str, float]:
        """Calculate comprehensive performance metrics"""
        
        if equity_curve.empty or not trades:
            return {}
        
        # Returns calculation
        equity_curve['returns'] = equity_curve['total_value'].pct_change()
        total_return = (equity_curve['total_value'].iloc[-1] / equity_curve['total_value'].iloc[0]) - 1
        
        # Annualized metrics
        trading_days = len(equity_curve)
        annualized_return = (1 + total_return) ** (252 / trading_days) - 1
        
        returns_std = equity_curve['returns'].std()
        annualized_vol = returns_std * math.sqrt(252)
        
        sharpe_ratio = annualized_return / annualized_vol if annualized_vol > 0 else 0
        
        # Trade-based metrics
        winning_trades = [t for t in trades if t.pnl and t.pnl > 0]
        losing_trades = [t for t in trades if t.pnl and t.pnl <= 0]
        
        win_rate = len(winning_trades) / len(trades) if trades else 0
        avg_win = np.mean([t.pnl for t in winning_trades]) if winning_trades else 0
        avg_loss = np.mean([t.pnl for t in losing_trades]) if losing_trades else 0
        profit_factor = abs(sum(t.pnl for t in winning_trades) / sum(t.pnl for t in losing_trades)) if losing_trades else float('inf')
        
        # Additional metrics
        max_consecutive_wins = self._calculate_consecutive_wins(trades, True)
        max_consecutive_losses = self._calculate_consecutive_wins(trades, False)
        avg_trade_duration = np.mean([t.days_held for t in trades if t.days_held]) if trades else 0
        
        return {
            'total_return': total_return,
            'annualized_return': annualized_return,
            'annualized_volatility': annualized_vol,
            'sharpe_ratio': sharpe_ratio,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'total_trades': len(trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'max_consecutive_wins': max_consecutive_wins,
            'max_consecutive_losses': max_consecutive_losses,
            'avg_trade_duration': avg_trade_duration,
            'total_pnl': sum(t.pnl for t in trades if t.pnl)
        }
    
    def _calculate_drawdown_analysis(self, equity_curve: pd.DataFrame) -> Dict[str, float]:
        """Calculate drawdown metrics"""
        
        if equity_curve.empty:
            return {}
        
        # Calculate rolling maximum (peak)
        equity_curve['peak'] = equity_curve['total_value'].expanding().max()
        
        # Calculate drawdown
        equity_curve['drawdown'] = (equity_curve['total_value'] - equity_curve['peak']) / equity_curve['peak']
        
        max_drawdown = equity_curve['drawdown'].min()
        avg_drawdown = equity_curve['drawdown'].mean()
        
        # Drawdown duration analysis
        in_drawdown = equity_curve['drawdown'] < 0
        drawdown_periods = []
        
        current_period = 0
        for is_dd in in_drawdown:
            if is_dd:
                current_period += 1
            else:
                if current_period > 0:
                    drawdown_periods.append(current_period)
                    current_period = 0
        
        if current_period > 0:
            drawdown_periods.append(current_period)
        
        max_drawdown_duration = max(drawdown_periods) if drawdown_periods else 0
        avg_drawdown_duration = np.mean(drawdown_periods) if drawdown_periods else 0
        
        return {
            'max_drawdown': max_drawdown,
            'avg_drawdown': avg_drawdown,
            'max_drawdown_duration': max_drawdown_duration,
            'avg_drawdown_duration': avg_drawdown_duration,
            'num_drawdown_periods': len(drawdown_periods)
        }
    
    def _generate_strategy_stats(self, trades: List[Trade], config: BacktestConfig) -> Dict[str, Any]:
        """Generate strategy-specific statistics"""
        
        # Group trades by exit reason
        exit_reasons = {}
        for trade in trades:
            reason = trade.exit_reason
            if reason not in exit_reasons:
                exit_reasons[reason] = []
            exit_reasons[reason].append(trade)
        
        # Calculate stats by exit reason
        exit_stats = {}
        for reason, reason_trades in exit_reasons.items():
            exit_stats[reason] = {
                'count': len(reason_trades),
                'avg_pnl': np.mean([t.pnl for t in reason_trades if t.pnl]),
                'win_rate': len([t for t in reason_trades if t.pnl and t.pnl > 0]) / len(reason_trades)
            }
        
        return {
            'strategy_type': config.strategy_type,
            'backtest_period': (config.end_date - config.start_date).days,
            'exit_reason_stats': exit_stats,
            'avg_trade_frequency': len(trades) / ((config.end_date - config.start_date).days / 30),  # Per month
        }
    
    def _calculate_risk_metrics(self, equity_curve: pd.DataFrame) -> Dict[str, float]:
        """Calculate risk-adjusted performance metrics"""
        
        if equity_curve.empty:
            return {}
        
        returns = equity_curve['total_value'].pct_change().dropna()
        
        # Sortino ratio (using downside deviation)
        negative_returns = returns[returns < 0]
        downside_std = negative_returns.std() if len(negative_returns) > 0 else 0
        sortino_ratio = returns.mean() / downside_std * math.sqrt(252) if downside_std > 0 else 0
        
        # Calmar ratio (return / max drawdown)
        max_dd = self._calculate_drawdown_analysis(equity_curve).get('max_drawdown', 0)
        calmar_ratio = returns.mean() * 252 / abs(max_dd) if max_dd != 0 else 0
        
        # VaR (Value at Risk)
        var_95 = returns.quantile(0.05)
        var_99 = returns.quantile(0.01)
        
        return {
            'sortino_ratio': sortino_ratio,
            'calmar_ratio': calmar_ratio,
            'var_95': var_95,
            'var_99': var_99,
            'skewness': returns.skew(),
            'kurtosis': returns.kurtosis()
        }
    
    def _calculate_consecutive_wins(self, trades: List[Trade], wins: bool) -> int:
        """Calculate maximum consecutive wins or losses"""
        
        max_consecutive = 0
        current_consecutive = 0
        
        for trade in trades:
            if trade.pnl is None:
                continue
                
            is_win = trade.pnl > 0
            if (wins and is_win) or (not wins and not is_win):
                current_consecutive += 1
                max_consecutive = max(max_consecutive, current_consecutive)
            else:
                current_consecutive = 0
        
        return max_consecutive
    
    def optimize_strategy(self,
                         base_config: BacktestConfig,
                         market_data: pd.DataFrame,
                         optimization_params: Dict[str, List]) -> Dict[str, Any]:
        """Optimize strategy parameters using grid search"""
        
        best_result = None
        best_params = None
        best_metric_value = float('-inf')
        optimization_metric = optimization_params.get('metric', 'sharpe_ratio')
        
        results = []
        
        # Generate parameter combinations
        param_names = [k for k in optimization_params.keys() if k != 'metric']
        param_values = [optimization_params[k] for k in param_names]
        
        import itertools
        for param_combo in itertools.product(*param_values):
            # Create modified config
            test_config = base_config
            param_dict = dict(zip(param_names, param_combo))
            
            # Update config with test parameters
            for param, value in param_dict.items():
                if param in ['profit_target_pct', 'stop_loss_pct', 'max_days']:
                    test_config.exit_criteria[param] = value
                elif param in ['days_to_expiration', 'min_vol', 'max_vol']:
                    test_config.entry_criteria[param] = value
            
            try:
                # Run backtest with test parameters
                result = self.run_backtest(test_config, market_data)
                metric_value = result.performance_metrics.get(optimization_metric, float('-inf'))
                
                results.append({
                    'params': param_dict,
                    'metric_value': metric_value,
                    'performance': result.performance_metrics
                })
                
                if metric_value > best_metric_value:
                    best_metric_value = metric_value
                    best_params = param_dict
                    best_result = result
                    
            except Exception as e:
                # Log error and continue
                print(f"Error in optimization with params {param_dict}: {e}")
                continue
        
        return {
            'best_params': best_params,
            'best_result': best_result,
            'best_metric_value': best_metric_value,
            'all_results': results,
            'optimization_metric': optimization_metric
        }

# Initialize the backtester
strategy_backtester = OptionsStrategyBacktester()