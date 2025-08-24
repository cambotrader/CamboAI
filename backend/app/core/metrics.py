from prometheus_client import Counter, Histogram, Gauge
from typing import Dict

# Request metrics
REQUEST_COUNT = Counter(
    'http_request_total',
    'Total number of HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency in seconds',
    ['method', 'endpoint'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0]
)

# Business metrics
MARKET_DATA_REQUESTS = Counter(
    'market_data_requests_total',
    'Total number of market data requests',
    ['symbol', 'timeframe']
)

ANALYSIS_REQUESTS = Counter(
    'analysis_requests_total',
    'Total number of analysis requests',
    ['type']
)

TRADING_ORDERS = Counter(
    'trading_orders_total',
    'Total number of trading orders',
    ['type', 'symbol', 'status']
)

# System metrics
ACTIVE_CONNECTIONS = Gauge(
    'active_connections',
    'Number of active WebSocket connections'
)

SYSTEM_MEMORY = Gauge(
    'system_memory_usage_bytes',
    'Memory usage in bytes'
)

API_ERROR_COUNT = Counter(
    'api_errors_total',
    'Total number of API errors',
    ['endpoint', 'error_type']
)

# Cache metrics
CACHE_HITS = Counter(
    'cache_hits_total',
    'Total number of cache hits',
    ['cache_type']
)

CACHE_MISSES = Counter(
    'cache_misses_total',
    'Total number of cache misses',
    ['cache_type']
)

# Provider usage metrics
MARKET_DATA_PROVIDER_USED = Counter(
    'market_data_provider_used_total',
    'Count of market data provider usage by domain and provider',
    ['domain', 'provider']
)

# Database metrics
DB_CONNECTION_POOL = Gauge(
    'db_connection_pool_size',
    'Number of connections in the database pool',
    ['status']
)

DB_QUERY_DURATION = Histogram(
    'db_query_duration_seconds',
    'Database query duration in seconds',
    ['query_type'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0]
)

class MetricsManager:
    @staticmethod
    def record_request(method: str, endpoint: str, status: int, duration: float):
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status).inc()
        REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(duration)

    @staticmethod
    def record_market_data_request(symbol: str, timeframe: str):
        MARKET_DATA_REQUESTS.labels(symbol=symbol, timeframe=timeframe).inc()

    @staticmethod
    def record_analysis_request(analysis_type: str):
        ANALYSIS_REQUESTS.labels(type=analysis_type).inc()

    @staticmethod
    def record_trading_order(order_type: str, symbol: str, status: str):
        TRADING_ORDERS.labels(type=order_type, symbol=symbol, status=status).inc()

    @staticmethod
    def update_active_connections(count: int):
        ACTIVE_CONNECTIONS.set(count)

    @staticmethod
    def record_api_error(endpoint: str, error_type: str):
        API_ERROR_COUNT.labels(endpoint=endpoint, error_type=error_type).inc()

    @staticmethod
    def record_cache_operation(cache_type: str, hit: bool):
        if hit:
            CACHE_HITS.labels(cache_type=cache_type).inc()
        else:
            CACHE_MISSES.labels(cache_type=cache_type).inc()

    @staticmethod
    def record_provider_used(domain: str, provider: str):
        MARKET_DATA_PROVIDER_USED.labels(domain=domain, provider=provider).inc()

    @staticmethod
    def update_db_pool_status(status: str, count: int):
        DB_CONNECTION_POOL.labels(status=status).set(count)

    @staticmethod
    def record_db_query_duration(query_type: str, duration: float):
        DB_QUERY_DURATION.labels(query_type=query_type).observe(duration)