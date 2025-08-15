import alpaca_trade_api as tradeapi
from typing import Dict, List, Optional
import yfinance as yf
from datetime import datetime, timedelta
import logging
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class BrokerOrder(BaseModel):
    symbol: str
    qty: float
    side: str  # 'buy' or 'sell'
    type: str  # 'market', 'limit', 'stop', 'stop_limit'
    time_in_force: str  # 'day', 'gtc', 'ioc', 'fok'
    limit_price: Optional[float] = None
    stop_price: Optional[float] = None

class BrokerPosition(BaseModel):
    symbol: str
    qty: float
    market_value: float
    cost_basis: float
    unrealized_pl: float
    unrealized_plpc: float
    current_price: float

class AlpacaBrokerService:
    def __init__(self, api_key: str, api_secret: str, base_url: str = None, paper: bool = True):
        """
        Initialize Alpaca broker service
        
        Args:
            api_key: Alpaca API key
            api_secret: Alpaca API secret
            base_url: Base URL (None for live, paper trading URL for paper)
            paper: Whether this is paper trading
        """
        self.paper = paper
        if paper:
            base_url = base_url or 'https://paper-api.alpaca.markets'
        else:
            base_url = base_url or 'https://api.alpaca.markets'
            
        try:
            self.api = tradeapi.REST(
                api_key,
                api_secret,
                base_url,
                api_version='v2'
            )
            # Test connection
            self.api.get_account()
            logger.info(f"Successfully connected to Alpaca ({'Paper' if paper else 'Live'} trading)")
        except Exception as e:
            logger.error(f"Failed to connect to Alpaca: {e}")
            raise
    
    def get_account_info(self) -> Dict:
        """Get account information"""
        try:
            account = self.api.get_account()
            return {
                'account_id': account.id,
                'account_number': account.account_number,
                'status': account.status,
                'currency': account.currency,
                'buying_power': float(account.buying_power),
                'cash': float(account.cash),
                'portfolio_value': float(account.portfolio_value),
                'equity': float(account.equity),
                'last_equity': float(account.last_equity),
                'multiplier': float(account.multiplier),
                'initial_margin': float(account.initial_margin),
                'maintenance_margin': float(account.maintenance_margin),
                'day_trading_buying_power': float(account.day_trading_buying_power),
                'regt_buying_power': float(account.regt_buying_power),
                'pattern_day_trader': account.pattern_day_trader,
                'trading_blocked': account.trading_blocked,
                'transfers_blocked': account.transfers_blocked,
                'account_blocked': account.account_blocked,
                'created_at': account.created_at,
                'trade_suspended_by_user': account.trade_suspended_by_user,
                'trading_configurations': {
                    'dtbp_check': account.dtbp_check,
                    'fractional_trading': account.fractional_trading,
                    'max_margin_multiplier': account.max_margin_multiplier,
                    'pdt_check': account.pdt_check,
                    'trade_confirm_email': account.trade_confirm_email
                }
            }
        except Exception as e:
            logger.error(f"Error getting account info: {e}")
            raise
    
    def get_positions(self) -> List[BrokerPosition]:
        """Get all current positions"""
        try:
            positions = self.api.list_positions()
            result = []
            
            for pos in positions:
                result.append(BrokerPosition(
                    symbol=pos.symbol,
                    qty=float(pos.qty),
                    market_value=float(pos.market_value),
                    cost_basis=float(pos.cost_basis),
                    unrealized_pl=float(pos.unrealized_pl),
                    unrealized_plpc=float(pos.unrealized_plpc),
                    current_price=float(pos.current_price) if pos.current_price else 0.0
                ))
            
            return result
        except Exception as e:
            logger.error(f"Error getting positions: {e}")
            raise
    
    def get_position(self, symbol: str) -> Optional[BrokerPosition]:
        """Get position for a specific symbol"""
        try:
            pos = self.api.get_position(symbol)
            return BrokerPosition(
                symbol=pos.symbol,
                qty=float(pos.qty),
                market_value=float(pos.market_value),
                cost_basis=float(pos.cost_basis),
                unrealized_pl=float(pos.unrealized_pl),
                unrealized_plpc=float(pos.unrealized_plpc),
                current_price=float(pos.current_price) if pos.current_price else 0.0
            )
        except Exception as e:
            if "position does not exist" in str(e).lower():
                return None
            logger.error(f"Error getting position for {symbol}: {e}")
            raise
    
    def place_order(self, order: BrokerOrder) -> Dict:
        """Place a trading order"""
        try:
            # Validate order
            if order.side not in ['buy', 'sell']:
                raise ValueError("Order side must be 'buy' or 'sell'")
            
            if order.type not in ['market', 'limit', 'stop', 'stop_limit']:
                raise ValueError("Order type must be 'market', 'limit', 'stop', or 'stop_limit'")
            
            if order.time_in_force not in ['day', 'gtc', 'ioc', 'fok']:
                raise ValueError("Time in force must be 'day', 'gtc', 'ioc', or 'fok'")
            
            # Build order parameters
            order_params = {
                'symbol': order.symbol,
                'qty': order.qty,
                'side': order.side,
                'type': order.type,
                'time_in_force': order.time_in_force
            }
            
            if order.type in ['limit', 'stop_limit'] and order.limit_price:
                order_params['limit_price'] = order.limit_price
            
            if order.type in ['stop', 'stop_limit'] and order.stop_price:
                order_params['stop_price'] = order.stop_price
            
            # Submit order
            submitted_order = self.api.submit_order(**order_params)
            
            return {
                'order_id': submitted_order.id,
                'client_order_id': submitted_order.client_order_id,
                'symbol': submitted_order.symbol,
                'asset_class': submitted_order.asset_class,
                'qty': float(submitted_order.qty),
                'filled_qty': float(submitted_order.filled_qty),
                'side': submitted_order.side,
                'order_type': submitted_order.order_type,
                'time_in_force': submitted_order.time_in_force,
                'limit_price': float(submitted_order.limit_price) if submitted_order.limit_price else None,
                'stop_price': float(submitted_order.stop_price) if submitted_order.stop_price else None,
                'status': submitted_order.status,
                'created_at': submitted_order.created_at,
                'updated_at': submitted_order.updated_at,
                'submitted_at': submitted_order.submitted_at,
                'filled_at': submitted_order.filled_at,
                'expired_at': submitted_order.expired_at,
                'canceled_at': submitted_order.canceled_at,
                'failed_at': submitted_order.failed_at,
                'replaced_at': submitted_order.replaced_at,
                'commission': float(submitted_order.commission) if submitted_order.commission else 0.0
            }
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            raise
    
    def get_orders(self, status: str = 'all', limit: int = 100) -> List[Dict]:
        """Get order history"""
        try:
            orders = self.api.list_orders(
                status=status,
                limit=limit,
                direction='desc'
            )
            
            result = []
            for order in orders:
                result.append({
                    'order_id': order.id,
                    'client_order_id': order.client_order_id,
                    'symbol': order.symbol,
                    'asset_class': order.asset_class,
                    'qty': float(order.qty),
                    'filled_qty': float(order.filled_qty),
                    'side': order.side,
                    'order_type': order.order_type,
                    'time_in_force': order.time_in_force,
                    'limit_price': float(order.limit_price) if order.limit_price else None,
                    'stop_price': float(order.stop_price) if order.stop_price else None,
                    'status': order.status,
                    'created_at': order.created_at,
                    'updated_at': order.updated_at,
                    'submitted_at': order.submitted_at,
                    'filled_at': order.filled_at,
                    'expired_at': order.expired_at,
                    'canceled_at': order.canceled_at,
                    'failed_at': order.failed_at,
                    'replaced_at': order.replaced_at,
                    'commission': float(order.commission) if order.commission else 0.0
                })
            
            return result
        except Exception as e:
            logger.error(f"Error getting orders: {e}")
            raise
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order"""
        try:
            self.api.cancel_order(order_id)
            return True
        except Exception as e:
            logger.error(f"Error canceling order {order_id}: {e}")
            return False
    
    def get_market_data(self, symbols: List[str], timeframe: str = '1Day', limit: int = 100) -> Dict:
        """Get market data for symbols"""
        try:
            # Alpaca market data
            bars = self.api.get_bars(
                symbols,
                timeframe,
                limit=limit
            ).df
            
            result = {}
            for symbol in symbols:
                if symbol in bars.index.get_level_values(0):
                    symbol_data = bars.loc[symbol]
                    result[symbol] = {
                        'bars': symbol_data.to_dict('records'),
                        'current_price': float(symbol_data['close'].iloc[-1]) if len(symbol_data) > 0 else None
                    }
            
            return result
        except Exception as e:
            logger.error(f"Error getting market data: {e}")
            # Fallback to yfinance
            result = {}
            for symbol in symbols:
                try:
                    ticker = yf.Ticker(symbol)
                    data = ticker.history(period=f"{limit}d")
                    if not data.empty:
                        result[symbol] = {
                            'bars': data.reset_index().to_dict('records'),
                            'current_price': float(data['Close'].iloc[-1])
                        }
                except Exception as yf_error:
                    logger.error(f"Error getting yfinance data for {symbol}: {yf_error}")
            
            return result
    
    def is_market_open(self) -> Dict:
        """Check if market is open"""
        try:
            calendar = self.api.get_calendar()
            clock = self.api.get_clock()
            
            return {
                'is_open': clock.is_open,
                'next_open': clock.next_open,
                'next_close': clock.next_close,
                'current_time': clock.timestamp
            }
        except Exception as e:
            logger.error(f"Error checking market status: {e}")
            raise

class BrokerFactory:
    """Factory class for creating broker instances"""
    
    @staticmethod
    def create_broker(broker_name: str, api_key: str, api_secret: str, base_url: str = None, paper: bool = True):
        """Create broker instance based on broker name"""
        if broker_name.upper() == 'ALPACA':
            return AlpacaBrokerService(api_key, api_secret, base_url, paper)
        else:
            raise ValueError(f"Unsupported broker: {broker_name}")
    
    @staticmethod
    def get_supported_brokers() -> List[str]:
        """Get list of supported brokers"""
        return ['ALPACA']
