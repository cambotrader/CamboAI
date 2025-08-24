"""
🏗️ ADVANCED TRADING DATABASE MODELS - INSTITUTIONAL GRADE
Complete database schema for professional trading platform
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, JSON, Enum, Index, UniqueConstraint
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime
from enum import Enum as PyEnum
import uuid

Base = declarative_base()

class OrderStatus(PyEnum):
    PENDING = "pending"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"

class OrderType(PyEnum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"
    TRAILING_STOP = "trailing_stop"
    MOC = "market_on_close"
    LOC = "limit_on_close"

class OrderSide(PyEnum):
    BUY = "buy"
    SELL = "sell"
    SHORT = "short"
    COVER = "cover"

class AssetType(PyEnum):
    STOCK = "stock"
    OPTION = "option"
    FUTURE = "future"
    FOREX = "forex"
    CRYPTO = "crypto"
    BOND = "bond"
    ETF = "etf"
    INDEX = "index"

class AccountType(PyEnum):
    PAPER = "paper"
    LIVE = "live"
    DEMO = "demo"

class RiskLevel(PyEnum):
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"
    PROFESSIONAL = "professional"

# Core Models

class User(Base):
    __tablename__ = 'users'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    phone = Column(String(20))
    
    # Account Settings
    risk_tolerance = Column(Enum(RiskLevel), default=RiskLevel.MODERATE)
    account_type = Column(Enum(AccountType), default=AccountType.PAPER)
    is_professional = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # KYC/AML
    ssn_encrypted = Column(String(255))  # Encrypted SSN
    date_of_birth = Column(DateTime)
    address = Column(Text)
    net_worth = Column(Float)
    income_range = Column(String(50))
    investment_experience = Column(String(50))
    
    # Platform Settings
    preferred_currency = Column(String(3), default='USD')
    timezone = Column(String(50), default='UTC')
    notification_preferences = Column(JSONB)
    ui_preferences = Column(JSONB)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Relationships
    accounts = relationship("Account", back_populates="user", cascade="all, delete-orphan")
    watchlists = relationship("Watchlist", back_populates="user", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="user", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_user_email_active', email, is_active),
    )

class Account(Base):
    __tablename__ = 'accounts'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    account_number = Column(String(50), unique=True, nullable=False, index=True)
    broker_name = Column(String(100), nullable=False)
    account_type = Column(Enum(AccountType), nullable=False)
    
    # Account Balances
    cash_balance = Column(Float, default=0.0)
    buying_power = Column(Float, default=0.0)
    portfolio_value = Column(Float, default=0.0)
    day_trade_buying_power = Column(Float, default=0.0)
    maintenance_excess = Column(Float, default=0.0)
    
    # Account Settings
    is_pattern_day_trader = Column(Boolean, default=False)
    is_margin_enabled = Column(Boolean, default=False)
    is_options_enabled = Column(Boolean, default=False)
    margin_multiplier = Column(Float, default=2.0)
    
    # Risk Management
    max_position_size = Column(Float)
    max_daily_loss = Column(Float)
    max_total_risk = Column(Float)
    allowed_asset_types = Column(JSONB)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_funded = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="accounts")
    orders = relationship("Order", back_populates="account", cascade="all, delete-orphan")
    positions = relationship("Position", back_populates="account", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="account", cascade="all, delete-orphan")

class Asset(Base):
    __tablename__ = 'assets'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    symbol = Column(String(20), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    asset_type = Column(Enum(AssetType), nullable=False)
    exchange = Column(String(50))
    currency = Column(String(3), default='USD')
    
    # Asset Details
    sector = Column(String(100))
    industry = Column(String(100))
    market_cap = Column(Float)
    shares_outstanding = Column(Float)
    
    # Trading Info
    is_tradable = Column(Boolean, default=True)
    is_shortable = Column(Boolean, default=True)
    tick_size = Column(Float, default=0.01)
    lot_size = Column(Integer, default=1)
    
    # Options Specific (for options)
    underlying_symbol = Column(String(20))
    strike_price = Column(Float)
    expiry_date = Column(DateTime)
    option_type = Column(String(4))  # CALL or PUT
    contract_size = Column(Integer, default=100)
    
    # Futures Specific
    contract_month = Column(String(10))
    first_notice_date = Column(DateTime)
    last_trading_date = Column(DateTime)
    
    # Crypto Specific
    circulating_supply = Column(Float)
    total_supply = Column(Float)
    
    # Metadata
    description = Column(Text)
    website = Column(String(255))
    extra_metadata = Column(JSONB)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    positions = relationship("Position", back_populates="asset")
    orders = relationship("Order", back_populates="asset")
    market_data = relationship("MarketData", back_populates="asset")
    
    __table_args__ = (
        UniqueConstraint('symbol', 'asset_type', 'exchange', name='unique_asset_symbol'),
        Index('idx_asset_symbol_type', symbol, asset_type),
        Index('idx_asset_tradable', is_tradable),
    )

class Position(Base):
    __tablename__ = 'positions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey('accounts.id'), nullable=False)
    asset_id = Column(UUID(as_uuid=True), ForeignKey('assets.id'), nullable=False)
    
    # Position Details
    quantity = Column(Float, nullable=False)  # Can be negative for short positions
    average_price = Column(Float, nullable=False)
    market_price = Column(Float)
    market_value = Column(Float)
    
    # P&L Calculations
    unrealized_pnl = Column(Float, default=0.0)
    realized_pnl = Column(Float, default=0.0)
    total_pnl = Column(Float, default=0.0)
    unrealized_pnl_percent = Column(Float, default=0.0)
    
    # Cost Basis
    cost_basis = Column(Float)
    accumulated_cost = Column(Float, default=0.0)
    
    # Greeks (for options)
    delta = Column(Float)
    gamma = Column(Float)
    theta = Column(Float)
    vega = Column(Float)
    rho = Column(Float)
    implied_volatility = Column(Float)
    
    # Risk Metrics
    var_1_day = Column(Float)  # 1-day Value at Risk
    beta = Column(Float)
    correlation_spy = Column(Float)
    
    # Timestamps
    opened_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    closed_at = Column(DateTime)
    
    # Relationships
    account = relationship("Account", back_populates="positions")
    asset = relationship("Asset", back_populates="positions")
    
    __table_args__ = (
        UniqueConstraint('account_id', 'asset_id', name='unique_position_per_asset'),
        Index('idx_position_account_asset', account_id, asset_id),
        Index('idx_position_quantity', quantity),
    )

class Order(Base):
    __tablename__ = 'orders'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey('accounts.id'), nullable=False)
    asset_id = Column(UUID(as_uuid=True), ForeignKey('assets.id'), nullable=False)
    
    # Order Identification
    broker_order_id = Column(String(100), index=True)  # Broker's order ID
    client_order_id = Column(String(100))  # Our internal ID
    parent_order_id = Column(UUID(as_uuid=True), ForeignKey('orders.id'))  # For bracket orders
    
    # Order Details
    order_type = Column(Enum(OrderType), nullable=False)
    side = Column(Enum(OrderSide), nullable=False)
    quantity = Column(Float, nullable=False)
    filled_quantity = Column(Float, default=0.0)
    remaining_quantity = Column(Float)
    
    # Pricing
    limit_price = Column(Float)
    stop_price = Column(Float)
    average_fill_price = Column(Float)
    trail_amount = Column(Float)
    trail_percent = Column(Float)
    
    # Status and Timing
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING, index=True)
    time_in_force = Column(String(10), default='DAY')  # DAY, GTC, IOC, FOK
    extended_hours = Column(Boolean, default=False)
    
    # Execution Details
    commission = Column(Float, default=0.0)
    fees = Column(Float, default=0.0)
    estimated_commission = Column(Float)
    
    # Strategy Info
    strategy_name = Column(String(100))
    strategy_id = Column(UUID(as_uuid=True))
    signal_id = Column(UUID(as_uuid=True))
    
    # Risk Management
    risk_check_passed = Column(Boolean, default=True)
    risk_check_notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    submitted_at = Column(DateTime)
    filled_at = Column(DateTime)
    cancelled_at = Column(DateTime)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Additional Data
    notes = Column(Text)
    extra_metadata = Column(JSONB)
    
    # Relationships
    account = relationship("Account", back_populates="orders")
    asset = relationship("Asset", back_populates="orders")
    fills = relationship("OrderFill", back_populates="order", cascade="all, delete-orphan")
    parent_order = relationship("Order", remote_side=[id], backref="child_orders")
    
    __table_args__ = (
        Index('idx_order_account_status', account_id, status),
        Index('idx_order_broker_id', broker_order_id),
        Index('idx_order_created_at', created_at),
    )

class OrderFill(Base):
    __tablename__ = 'order_fills'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey('orders.id'), nullable=False)
    
    # Fill Details
    fill_price = Column(Float, nullable=False)
    fill_quantity = Column(Float, nullable=False)
    fill_time = Column(DateTime, nullable=False)
    
    # Execution Info
    execution_id = Column(String(100))  # Broker execution ID
    venue = Column(String(50))  # Execution venue
    liquidity_flag = Column(String(10))  # Add/Remove liquidity
    
    # Costs
    commission = Column(Float, default=0.0)
    fees = Column(Float, default=0.0)
    sec_fee = Column(Float, default=0.0)
    orf_fee = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    order = relationship("Order", back_populates="fills")

class Transaction(Base):
    __tablename__ = 'transactions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey('accounts.id'), nullable=False)
    
    # Transaction Details
    transaction_type = Column(String(50), nullable=False)  # TRADE, DIVIDEND, INTEREST, etc.
    amount = Column(Float, nullable=False)  # Positive or negative
    description = Column(String(255))
    reference_id = Column(String(100))  # Order ID, dividend ID, etc.
    
    # Related Asset (optional)
    asset_id = Column(UUID(as_uuid=True), ForeignKey('assets.id'))
    quantity = Column(Float)  # For trades
    price = Column(Float)  # For trades
    
    # Running Balances
    cash_balance_after = Column(Float)
    
    # Timestamps
    transaction_date = Column(DateTime, nullable=False)
    settlement_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    account = relationship("Account", back_populates="transactions")

class MarketData(Base):
    __tablename__ = 'market_data'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asset_id = Column(UUID(as_uuid=True), ForeignKey('assets.id'), nullable=False)
    
    # OHLCV Data
    open_price = Column(Float)
    high_price = Column(Float)
    low_price = Column(Float)
    close_price = Column(Float)
    volume = Column(Float)
    
    # Additional Market Data
    bid_price = Column(Float)
    ask_price = Column(Float)
    bid_size = Column(Float)
    ask_size = Column(Float)
    last_price = Column(Float)
    last_size = Column(Float)
    
    # Calculated Fields
    vwap = Column(Float)  # Volume Weighted Average Price
    twap = Column(Float)  # Time Weighted Average Price
    change = Column(Float)
    change_percent = Column(Float)
    
    # Greeks (for options)
    implied_volatility = Column(Float)
    delta = Column(Float)
    gamma = Column(Float)
    theta = Column(Float)
    vega = Column(Float)
    rho = Column(Float)
    
    # Time and Source
    timestamp = Column(DateTime, nullable=False)
    timeframe = Column(String(10))  # 1m, 5m, 1h, 1d, etc.
    data_source = Column(String(50))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    asset = relationship("Asset", back_populates="market_data")
    
    __table_args__ = (
        Index('idx_market_data_asset_time', asset_id, timestamp),
        Index('idx_market_data_timeframe', timeframe, timestamp),
    )

class Watchlist(Base):
    __tablename__ = 'watchlists'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    
    name = Column(String(100), nullable=False)
    description = Column(Text)
    is_default = Column(Boolean, default=False)
    is_public = Column(Boolean, default=False)
    
    # Settings
    sort_order = Column(String(20), default='symbol')  # symbol, change, volume, etc.
    refresh_interval = Column(Integer, default=5)  # seconds
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="watchlists")
    items = relationship("WatchlistItem", back_populates="watchlist", cascade="all, delete-orphan")

class WatchlistItem(Base):
    __tablename__ = 'watchlist_items'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    watchlist_id = Column(UUID(as_uuid=True), ForeignKey('watchlists.id'), nullable=False)
    asset_id = Column(UUID(as_uuid=True), ForeignKey('assets.id'), nullable=False)
    
    # Display Settings
    sort_order = Column(Integer, default=0)
    notes = Column(Text)
    
    # Custom Alerts
    price_alert_high = Column(Float)
    price_alert_low = Column(Float)
    volume_alert_threshold = Column(Float)
    
    # Timestamps
    added_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    watchlist = relationship("Watchlist", back_populates="items")
    asset = relationship("Asset")
    
    __table_args__ = (
        UniqueConstraint('watchlist_id', 'asset_id', name='unique_watchlist_asset'),
    )

class Alert(Base):
    __tablename__ = 'alerts'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    asset_id = Column(UUID(as_uuid=True), ForeignKey('assets.id'))
    
    # Alert Details
    alert_type = Column(String(50), nullable=False)  # price, volume, news, etc.
    condition = Column(String(20), nullable=False)  # above, below, equals, etc.
    threshold_value = Column(Float)
    message = Column(Text)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_triggered = Column(Boolean, default=False)
    trigger_count = Column(Integer, default=0)
    max_triggers = Column(Integer, default=1)
    
    # Delivery Settings
    notify_email = Column(Boolean, default=True)
    notify_sms = Column(Boolean, default=False)
    notify_push = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    triggered_at = Column(DateTime)
    expires_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="alerts")

# AI and Strategy Models

class TradingStrategy(Base):
    __tablename__ = 'trading_strategies'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    
    # Strategy Details
    name = Column(String(100), nullable=False)
    description = Column(Text)
    strategy_type = Column(String(50))  # mean_reversion, momentum, arbitrage, etc.
    asset_class = Column(String(20))  # stocks, options, forex, etc.
    
    # Configuration
    parameters = Column(JSONB)  # Strategy parameters
    risk_parameters = Column(JSONB)  # Risk management settings
    entry_rules = Column(JSONB)  # Entry conditions
    exit_rules = Column(JSONB)  # Exit conditions
    
    # Performance Tracking
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    total_pnl = Column(Float, default=0.0)
    max_drawdown = Column(Float, default=0.0)
    sharpe_ratio = Column(Float)
    win_rate = Column(Float)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_paper_trading = Column(Boolean, default=True)
    auto_execute = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_run_at = Column(DateTime)

class AISignal(Base):
    __tablename__ = 'ai_signals'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asset_id = Column(UUID(as_uuid=True), ForeignKey('assets.id'), nullable=False)
    strategy_id = Column(UUID(as_uuid=True), ForeignKey('trading_strategies.id'))
    
    # Signal Details
    signal_type = Column(String(20), nullable=False)  # BUY, SELL, HOLD
    confidence_score = Column(Float, nullable=False)  # 0-1
    strength_score = Column(Float)  # Signal strength
    target_price = Column(Float)
    stop_loss_price = Column(Float)
    
    # Model Info
    model_name = Column(String(100))
    model_version = Column(String(20))
    features_used = Column(JSONB)
    prediction_horizon = Column(String(20))  # 1h, 1d, 1w, etc.
    
    # Metadata
    market_conditions = Column(JSONB)
    sentiment_score = Column(Float)
    volatility_estimate = Column(Float)
    
    # Status
    is_executed = Column(Boolean, default=False)
    execution_order_id = Column(UUID(as_uuid=True))
    
    # Timestamps
    generated_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    executed_at = Column(DateTime)

class RiskMetrics(Base):
    __tablename__ = 'risk_metrics'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(UUID(as_uuid=True), ForeignKey('accounts.id'), nullable=False)
    
    # Portfolio Risk
    portfolio_var_1d = Column(Float)  # 1-day VaR
    portfolio_var_5d = Column(Float)  # 5-day VaR
    portfolio_beta = Column(Float)
    portfolio_correlation_spy = Column(Float)
    max_drawdown = Column(Float)
    
    # Concentration Risk
    largest_position_percent = Column(Float)
    sector_concentration = Column(JSONB)
    asset_type_concentration = Column(JSONB)
    
    # Leverage and Margin
    total_leverage = Column(Float)
    margin_utilization = Column(Float)
    buying_power_utilization = Column(Float)
    
    # Greeks (if applicable)
    portfolio_delta = Column(Float)
    portfolio_gamma = Column(Float)
    portfolio_theta = Column(Float)
    portfolio_vega = Column(Float)
    
    # Calculated At
    calculated_at = Column(DateTime, default=datetime.utcnow)

# Create all indexes for optimal performance
def create_performance_indexes(engine):
    """Create additional indexes for performance optimization"""
    with engine.connect() as conn:
        # Market data time-series indexes
        conn.execute("CREATE INDEX IF NOT EXISTS idx_market_data_asset_timestamp_desc ON market_data (asset_id, timestamp DESC)")
        
        # Order status tracking
        conn.execute("CREATE INDEX IF NOT EXISTS idx_orders_account_status_created ON orders (account_id, status, created_at DESC)")
        
        # Position tracking
        conn.execute("CREATE INDEX IF NOT EXISTS idx_positions_account_quantity_nonzero ON positions (account_id) WHERE quantity != 0")
        
        # Real-time data lookups
        conn.execute("CREATE INDEX IF NOT EXISTS idx_assets_symbol_tradable ON assets (symbol) WHERE is_tradable = true")
        
        conn.commit()

# Export all models
__all__ = [
    'Base', 'User', 'Account', 'Asset', 'Position', 'Order', 'OrderFill', 
    'Transaction', 'MarketData', 'Watchlist', 'WatchlistItem', 'Alert',
    'TradingStrategy', 'AISignal', 'RiskMetrics',
    'OrderStatus', 'OrderType', 'OrderSide', 'AssetType', 'AccountType', 'RiskLevel'
]