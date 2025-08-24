import redis
from typing import Any, Optional, Dict, List
import json
import pickle
from datetime import datetime, timedelta
import logging
from functools import wraps
import asyncio
import hashlib

logger = logging.getLogger(__name__)

class CacheService:
    """Redis-based caching service for performance optimization"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        try:
            self.redis_client = redis.from_url(redis_url, decode_responses=False)
            # Test connection
            self.redis_client.ping()
            logger.info("Redis cache service initialized successfully")
        except Exception as e:
            logger.warning(f"Redis not available, using in-memory cache: {e}")
            self.redis_client = None
            self.memory_cache = {}
            self.cache_timestamps = {}
    
    def _get_cache_key(self, key: str, prefix: str = "cambo") -> str:
        """Generate cache key with prefix"""
        return f"{prefix}:{key}"
    
    def _is_memory_cache_valid(self, key: str, ttl: int) -> bool:
        """Check if memory cache entry is still valid"""
        if key not in self.cache_timestamps:
            return False
        
        timestamp = self.cache_timestamps[key]
        return datetime.now() - timestamp < timedelta(seconds=ttl)
    
    async def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache"""
        cache_key = self._get_cache_key(key)
        
        try:
            if self.redis_client:
                value = self.redis_client.get(cache_key)
                if value:
                    return pickle.loads(value)
            else:
                # Use memory cache
                if key in self.memory_cache and self._is_memory_cache_valid(key, 300):  # 5 min default
                    return self.memory_cache[key]
            
            return default
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return default
    
    async def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Set value in cache with TTL"""
        cache_key = self._get_cache_key(key)
        
        try:
            if self.redis_client:
                serialized_value = pickle.dumps(value)
                return self.redis_client.setex(cache_key, ttl, serialized_value)
            else:
                # Use memory cache
                self.memory_cache[key] = value
                self.cache_timestamps[key] = datetime.now()
                return True
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        cache_key = self._get_cache_key(key)
        
        try:
            if self.redis_client:
                return bool(self.redis_client.delete(cache_key))
            else:
                # Use memory cache
                if key in self.memory_cache:
                    del self.memory_cache[key]
                if key in self.cache_timestamps:
                    del self.cache_timestamps[key]
                return True
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        try:
            if self.redis_client:
                keys = self.redis_client.keys(self._get_cache_key(pattern))
                if keys:
                    return self.redis_client.delete(*keys)
                return 0
            else:
                # Use memory cache
                keys_to_delete = [k for k in self.memory_cache.keys() if pattern in k]
                for key in keys_to_delete:
                    if key in self.memory_cache:
                        del self.memory_cache[key]
                    if key in self.cache_timestamps:
                        del self.cache_timestamps[key]
                return len(keys_to_delete)
        except Exception as e:
            logger.error(f"Cache clear pattern error for {pattern}: {e}")
            return 0
    
    async def get_or_set(self, key: str, callback, ttl: int = 300, *args, **kwargs) -> Any:
        """Get from cache or set using callback if not found"""
        value = await self.get(key)
        if value is not None:
            return value
        
        # Value not in cache, compute it
        if asyncio.iscoroutinefunction(callback):
            value = await callback(*args, **kwargs)
        else:
            value = callback(*args, **kwargs)
        
        await self.set(key, value, ttl)
        return value

# Global cache instance
cache = CacheService()

def cache_result(key_prefix: str, ttl: int = 300, include_user: bool = True):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            key_parts = [key_prefix]
            
            # Include user ID if requested
            if include_user and 'current_user' in kwargs:
                user = kwargs['current_user']
                if hasattr(user, 'id'):
                    key_parts.append(f"user:{user.id}")
            
            # Include function arguments in key
            arg_str = str(args) + str(sorted(kwargs.items()))
            arg_hash = hashlib.md5(arg_str.encode()).hexdigest()[:8]
            key_parts.append(arg_hash)
            
            cache_key = ":".join(key_parts)
            
            # Try to get from cache
            cached_result = await cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached_result
            
            # Cache miss, execute function
            logger.debug(f"Cache miss for {cache_key}")
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            # Store in cache
            await cache.set(cache_key, result, ttl)
            return result
        
        return wrapper
    return decorator

class PaginationService:
    """Service for handling paginated queries"""
    
    @staticmethod
    def get_offset_limit(page: int, per_page: int, max_per_page: int = 100) -> tuple:
        """Calculate offset and limit for pagination"""
        page = max(1, page)  # Ensure page is at least 1
        per_page = min(max(1, per_page), max_per_page)  # Ensure per_page is between 1 and max
        
        offset = (page - 1) * per_page
        return offset, per_page
    
    @staticmethod
    def create_pagination_info(total: int, page: int, per_page: int) -> Dict:
        """Create pagination metadata"""
        total_pages = (total + per_page - 1) // per_page  # Ceiling division
        
        return {
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
            "next_page": page + 1 if page < total_pages else None,
            "prev_page": page - 1 if page > 1 else None
        }

class PerformanceOptimizer:
    """Collection of performance optimization utilities"""
    
    @staticmethod
    async def batch_process(items: List[Any], batch_size: int, processor, *args, **kwargs) -> List[Any]:
        """Process items in batches to avoid memory issues"""
        results = []
        
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            
            if asyncio.iscoroutinefunction(processor):
                batch_results = await processor(batch, *args, **kwargs)
            else:
                batch_results = processor(batch, *args, **kwargs)
            
            if isinstance(batch_results, list):
                results.extend(batch_results)
            else:
                results.append(batch_results)
            
            # Allow other tasks to run
            await asyncio.sleep(0)
        
        return results
    
    @staticmethod
    def memoize_with_ttl(ttl: int = 300):
        """In-memory memoization with TTL"""
        def decorator(func):
            cache_data = {}
            cache_timestamps = {}
            
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Create cache key
                key = str(args) + str(sorted(kwargs.items()))
                
                # Check if cached and not expired
                if key in cache_data:
                    if datetime.now() - cache_timestamps[key] < timedelta(seconds=ttl):
                        return cache_data[key]
                    else:
                        # Expired, remove from cache
                        del cache_data[key]
                        del cache_timestamps[key]
                
                # Calculate and cache result
                result = func(*args, **kwargs)
                cache_data[key] = result
                cache_timestamps[key] = datetime.now()
                
                return result
            
            return wrapper
        return decorator
    
    @staticmethod
    async def parallel_requests(requests: List, max_concurrent: int = 10) -> List[Any]:
        """Execute multiple async requests in parallel with concurrency limit"""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def limited_request(request):
            async with semaphore:
                if asyncio.iscoroutinefunction(request):
                    return await request()
                else:
                    return request()
        
        tasks = [limited_request(req) for req in requests]
        return await asyncio.gather(*tasks, return_exceptions=True)

# Cache invalidation utilities
class CacheInvalidator:
    """Utility to manage cache invalidation"""
    
    @staticmethod
    async def invalidate_user_cache(user_id: str):
        """Invalidate all cache entries for a user"""
        pattern = f"*user:{user_id}*"
        await cache.clear_pattern(pattern)
        logger.info(f"Invalidated cache for user {user_id}")
    
    @staticmethod
    async def invalidate_portfolio_cache(portfolio_id: str):
        """Invalidate cache entries for a portfolio"""
        patterns = [
            f"*portfolio:{portfolio_id}*",
            f"*positions:{portfolio_id}*",
            f"*performance:{portfolio_id}*",
            f"*risk:{portfolio_id}*"
        ]
        
        for pattern in patterns:
            await cache.clear_pattern(pattern)
        
        logger.info(f"Invalidated cache for portfolio {portfolio_id}")
    
    @staticmethod
    async def invalidate_market_data_cache():
        """Invalidate market data cache"""
        patterns = ["*market_data*", "*quotes*", "*prices*"]
        
        for pattern in patterns:
            await cache.clear_pattern(pattern)
        
        logger.info("Invalidated market data cache")

# Database query optimization
class QueryOptimizer:
    """Database query optimization utilities"""
    
    @staticmethod
    def build_filters(filters: Dict) -> tuple:
        """Build SQL filters from dictionary"""
        where_clauses = []
        params = {}
        
        for key, value in filters.items():
            if value is not None:
                if isinstance(value, list):
                    placeholders = ', '.join([f":{key}_{i}" for i in range(len(value))])
                    where_clauses.append(f"{key} IN ({placeholders})")
                    for i, v in enumerate(value):
                        params[f"{key}_{i}"] = v
                else:
                    where_clauses.append(f"{key} = :{key}")
                    params[key] = value
        
        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
        return where_sql, params
    
    @staticmethod
    def build_order_by(sort_by: str, order: str = "asc") -> str:
        """Build ORDER BY clause safely"""
        # Whitelist of allowed sort columns
        allowed_columns = [
            "created_at", "updated_at", "symbol", "quantity", "current_price",
            "market_value", "pnl", "pnl_percent", "date", "total_value"
        ]
        
        if sort_by not in allowed_columns:
            sort_by = "created_at"
        
        order = order.lower()
        if order not in ["asc", "desc"]:
            order = "asc"
        
        return f"ORDER BY {sort_by} {order.upper()}"
