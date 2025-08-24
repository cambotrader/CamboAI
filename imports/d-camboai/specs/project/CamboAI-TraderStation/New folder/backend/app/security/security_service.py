from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Optional
import time
import asyncio
import logging
from datetime import datetime, timedelta
import hashlib
import re
from pydantic import BaseModel, validator
import secrets
import string

logger = logging.getLogger(__name__)

class RateLimitConfig(BaseModel):
    """Rate limit configuration"""
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    requests_per_day: int = 10000
    burst_limit: int = 10  # Allow burst of requests

class RateLimiter:
    """Redis-backed or in-memory rate limiter"""
    
    def __init__(self, redis_client=None):
        self.redis_client = redis_client
        self.memory_store = {}  # Fallback for when Redis is not available
        self.cleanup_interval = 300  # 5 minutes
        self.last_cleanup = time.time()
    
    def _cleanup_memory_store(self):
        """Clean up expired entries from memory store"""
        current_time = time.time()
        if current_time - self.last_cleanup > self.cleanup_interval:
            # Remove entries older than 1 hour
            cutoff_time = current_time - 3600
            keys_to_remove = [
                key for key, data in self.memory_store.items()
                if data.get('timestamp', 0) < cutoff_time
            ]
            for key in keys_to_remove:
                del self.memory_store[key]
            self.last_cleanup = current_time
    
    async def is_rate_limited(self, identifier: str, config: RateLimitConfig) -> tuple[bool, Dict]:
        """Check if request should be rate limited"""
        current_time = time.time()
        minute_key = f"rate_limit:{identifier}:minute:{int(current_time // 60)}"
        hour_key = f"rate_limit:{identifier}:hour:{int(current_time // 3600)}"
        day_key = f"rate_limit:{identifier}:day:{int(current_time // 86400)}"
        burst_key = f"rate_limit:{identifier}:burst"
        
        try:
            if self.redis_client:
                # Use Redis for distributed rate limiting
                pipe = self.redis_client.pipeline()
                
                # Check current counts
                pipe.get(minute_key)
                pipe.get(hour_key)
                pipe.get(day_key)
                pipe.get(burst_key)
                
                results = pipe.execute()
                minute_count = int(results[0] or 0)
                hour_count = int(results[1] or 0)
                day_count = int(results[2] or 0)
                burst_count = int(results[3] or 0)
                
                # Check limits
                if (minute_count >= config.requests_per_minute or
                    hour_count >= config.requests_per_hour or
                    day_count >= config.requests_per_day or
                    burst_count >= config.burst_limit):
                    
                    return True, {
                        'minute_count': minute_count,
                        'hour_count': hour_count,
                        'day_count': day_count,
                        'burst_count': burst_count,
                        'limits': {
                            'minute': config.requests_per_minute,
                            'hour': config.requests_per_hour,
                            'day': config.requests_per_day,
                            'burst': config.burst_limit
                        }
                    }
                
                # Increment counters
                pipe = self.redis_client.pipeline()
                pipe.incr(minute_key)
                pipe.expire(minute_key, 60)
                pipe.incr(hour_key)
                pipe.expire(hour_key, 3600)
                pipe.incr(day_key)
                pipe.expire(day_key, 86400)
                pipe.incr(burst_key)
                pipe.expire(burst_key, 10)  # 10 second burst window
                pipe.execute()
                
            else:
                # Use memory store as fallback
                self._cleanup_memory_store()
                
                # Get current counts
                minute_data = self.memory_store.get(minute_key, {'count': 0, 'timestamp': current_time})
                hour_data = self.memory_store.get(hour_key, {'count': 0, 'timestamp': current_time})
                day_data = self.memory_store.get(day_key, {'count': 0, 'timestamp': current_time})
                burst_data = self.memory_store.get(burst_key, {'count': 0, 'timestamp': current_time})
                
                # Check if windows have expired
                if current_time - minute_data['timestamp'] > 60:
                    minute_data = {'count': 0, 'timestamp': current_time}
                if current_time - hour_data['timestamp'] > 3600:
                    hour_data = {'count': 0, 'timestamp': current_time}
                if current_time - day_data['timestamp'] > 86400:
                    day_data = {'count': 0, 'timestamp': current_time}
                if current_time - burst_data['timestamp'] > 10:
                    burst_data = {'count': 0, 'timestamp': current_time}
                
                # Check limits
                if (minute_data['count'] >= config.requests_per_minute or
                    hour_data['count'] >= config.requests_per_hour or
                    day_data['count'] >= config.requests_per_day or
                    burst_data['count'] >= config.burst_limit):
                    
                    return True, {
                        'minute_count': minute_data['count'],
                        'hour_count': hour_data['count'],
                        'day_count': day_data['count'],
                        'burst_count': burst_data['count'],
                        'limits': {
                            'minute': config.requests_per_minute,
                            'hour': config.requests_per_hour,
                            'day': config.requests_per_day,
                            'burst': config.burst_limit
                        }
                    }
                
                # Increment counters
                minute_data['count'] += 1
                hour_data['count'] += 1
                day_data['count'] += 1
                burst_data['count'] += 1
                
                self.memory_store[minute_key] = minute_data
                self.memory_store[hour_key] = hour_data
                self.memory_store[day_key] = day_data
                self.memory_store[burst_key] = burst_data
            
            return False, {}
            
        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            # On error, allow the request (fail open)
            return False, {}

class InputValidator:
    """Input validation and sanitization"""
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 255) -> str:
        """Sanitize string input"""
        if not isinstance(value, str):
            raise ValueError("Value must be a string")
        
        # Remove control characters
        value = ''.join(char for char in value if ord(char) >= 32 or char in '\n\r\t')
        
        # Limit length
        if len(value) > max_length:
            raise ValueError(f"String too long (max {max_length} characters)")
        
        return value.strip()
    
    @staticmethod
    def validate_symbol(symbol: str) -> str:
        """Validate stock symbol"""
        symbol = symbol.upper().strip()
        
        # Check format (1-5 alphanumeric characters)
        if not re.match(r'^[A-Z0-9]{1,5}$', symbol):
            raise ValueError("Invalid symbol format")
        
        return symbol
    
    @staticmethod
    def validate_email(email: str) -> str:
        """Validate email format"""
        email = email.lower().strip()
        
        # Basic email regex
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValueError("Invalid email format")
        
        if len(email) > 254:
            raise ValueError("Email too long")
        
        return email
    
    @staticmethod
    def validate_password(password: str) -> str:
        """Validate password strength"""
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters")
        
        if len(password) > 128:
            raise ValueError("Password too long")
        
        # Check for at least one uppercase, lowercase, digit, and special char
        if not re.search(r'[A-Z]', password):
            raise ValueError("Password must contain at least one uppercase letter")
        
        if not re.search(r'[a-z]', password):
            raise ValueError("Password must contain at least one lowercase letter")
        
        if not re.search(r'\d', password):
            raise ValueError("Password must contain at least one digit")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValueError("Password must contain at least one special character")
        
        return password
    
    @staticmethod
    def validate_amount(amount: float, min_value: float = 0.01, max_value: float = 1_000_000) -> float:
        """Validate monetary amount"""
        if not isinstance(amount, (int, float)):
            raise ValueError("Amount must be a number")
        
        if amount < min_value:
            raise ValueError(f"Amount must be at least {min_value}")
        
        if amount > max_value:
            raise ValueError(f"Amount cannot exceed {max_value}")
        
        # Round to 2 decimal places
        return round(float(amount), 2)
    
    @staticmethod
    def validate_quantity(quantity: float, min_value: float = 0.001) -> float:
        """Validate share quantity"""
        if not isinstance(quantity, (int, float)):
            raise ValueError("Quantity must be a number")
        
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        if quantity < min_value:
            raise ValueError(f"Quantity must be at least {min_value}")
        
        return float(quantity)

class SecurityHeaders:
    """Security headers middleware"""
    
    @staticmethod
    def get_security_headers() -> Dict[str, str]:
        """Get recommended security headers"""
        return {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline' https://s.tradingview.com; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; connect-src 'self' wss: https:; frame-src https://s.tradingview.com;",
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Permissions-Policy': 'camera=(), microphone=(), geolocation=()'
        }

class AuditLogger:
    """Security audit logging"""
    
    def __init__(self):
        self.audit_logger = logging.getLogger('audit')
        
        # Configure audit logger if not already configured
        if not self.audit_logger.handlers:
            handler = logging.FileHandler('logs/audit.log')
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            handler.setFormatter(formatter)
            self.audit_logger.addHandler(handler)
            self.audit_logger.setLevel(logging.INFO)
    
    def log_authentication(self, user_id: str, action: str, success: bool, ip_address: str, user_agent: str):
        """Log authentication events"""
        self.audit_logger.info(
            f"AUTH - User: {user_id} - Action: {action} - Success: {success} - "
            f"IP: {ip_address} - UserAgent: {user_agent}"
        )
    
    def log_trading_action(self, user_id: str, action: str, symbol: str, quantity: float, amount: float, ip_address: str):
        """Log trading actions"""
        self.audit_logger.info(
            f"TRADE - User: {user_id} - Action: {action} - Symbol: {symbol} - "
            f"Quantity: {quantity} - Amount: {amount} - IP: {ip_address}"
        )
    
    def log_security_event(self, event_type: str, details: str, ip_address: str, user_id: Optional[str] = None):
        """Log security events"""
        self.audit_logger.warning(
            f"SECURITY - Type: {event_type} - Details: {details} - "
            f"IP: {ip_address} - User: {user_id or 'Unknown'}"
        )
    
    def log_api_access(self, user_id: str, endpoint: str, method: str, status_code: int, ip_address: str):
        """Log API access"""
        self.audit_logger.info(
            f"API - User: {user_id} - Endpoint: {endpoint} - Method: {method} - "
            f"Status: {status_code} - IP: {ip_address}"
        )

class APIKeyManager:
    """API key management and validation"""
    
    @staticmethod
    def generate_api_key() -> str:
        """Generate a secure API key"""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(32))
    
    @staticmethod
    def hash_api_key(api_key: str) -> str:
        """Hash API key for storage"""
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    @staticmethod
    def validate_api_key_format(api_key: str) -> bool:
        """Validate API key format"""
        return bool(re.match(r'^[A-Za-z0-9]{32}$', api_key))

class CSRFProtection:
    """CSRF protection utilities"""
    
    @staticmethod
    def generate_csrf_token() -> str:
        """Generate CSRF token"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def validate_csrf_token(token: str, stored_token: str) -> bool:
        """Validate CSRF token"""
        return secrets.compare_digest(token, stored_token)

# Global instances
rate_limiter = RateLimiter()
audit_logger = AuditLogger()

# Rate limiting configurations
RATE_LIMIT_CONFIGS = {
    'default': RateLimitConfig(),
    'auth': RateLimitConfig(requests_per_minute=10, requests_per_hour=50, burst_limit=3),
    'trading': RateLimitConfig(requests_per_minute=30, requests_per_hour=200, burst_limit=5),
    'market_data': RateLimitConfig(requests_per_minute=120, requests_per_hour=2000, burst_limit=20)
}
