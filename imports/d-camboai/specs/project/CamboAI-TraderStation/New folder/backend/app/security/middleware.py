from fastapi import Request, Response, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Callable
import time
import logging
from .security_service import (
    rate_limiter, audit_logger, RATE_LIMIT_CONFIGS, 
    SecurityHeaders, InputValidator, RateLimitConfig
)

logger = logging.getLogger(__name__)
security = HTTPBearer()

def get_client_ip(request: Request) -> str:
    """Get client IP address from request"""
    # Check for forwarded headers (load balancer/proxy)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fallback to direct connection
    return request.client.host if request.client else "unknown"

def rate_limit(config_name: str = 'default'):
    """Rate limiting decorator"""
    def decorator(func):
        async def wrapper(request: Request, *args, **kwargs):
            # Get rate limit configuration
            config = RATE_LIMIT_CONFIGS.get(config_name, RATE_LIMIT_CONFIGS['default'])
            
            # Create identifier (IP + user if available)
            ip_address = get_client_ip(request)
            identifier = ip_address
            
            # Add user ID to identifier if authenticated
            try:
                if hasattr(request.state, 'user') and request.state.user:
                    identifier = f"{ip_address}:{request.state.user.id}"
            except:
                pass
            
            # Check rate limit
            is_limited, limit_info = await rate_limiter.is_rate_limited(identifier, config)
            
            if is_limited:
                audit_logger.log_security_event(
                    "RATE_LIMIT_EXCEEDED",
                    f"Config: {config_name}, Limits: {limit_info}",
                    ip_address,
                    getattr(request.state, 'user', {}).get('id') if hasattr(request.state, 'user') else None
                )
                
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "error": "Rate limit exceeded",
                        "retry_after": 60,  # seconds
                        "limits": limit_info.get('limits', {}),
                        "current": {
                            'minute': limit_info.get('minute_count', 0),
                            'hour': limit_info.get('hour_count', 0),
                            'day': limit_info.get('day_count', 0)
                        }
                    }
                )
            
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator

async def security_headers_middleware(request: Request, call_next):
    """Add security headers to all responses"""
    response = await call_next(request)
    
    # Add security headers
    headers = SecurityHeaders.get_security_headers()
    for name, value in headers.items():
        response.headers[name] = value
    
    return response

async def audit_middleware(request: Request, call_next):
    """Audit logging middleware"""
    start_time = time.time()
    ip_address = get_client_ip(request)
    user_agent = request.headers.get("User-Agent", "Unknown")
    
    # Log request start
    logger.debug(f"Request start: {request.method} {request.url.path} from {ip_address}")
    
    try:
        response = await call_next(request)
        
        # Calculate response time
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        # Log API access
        user_id = "unknown"
        if hasattr(request.state, 'user') and request.state.user:
            user_id = request.state.user.id
        
        audit_logger.log_api_access(
            user_id,
            str(request.url.path),
            request.method,
            response.status_code,
            ip_address
        )
        
        return response
        
    except Exception as e:
        # Log errors
        audit_logger.log_security_event(
            "REQUEST_ERROR",
            f"Error processing request: {str(e)}",
            ip_address
        )
        raise

def validate_input(validator_func: Callable):
    """Input validation decorator"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                # Apply validation function to kwargs
                validated_kwargs = {}
                for key, value in kwargs.items():
                    if key in ['request', 'current_user', 'background_tasks']:
                        # Skip framework parameters
                        validated_kwargs[key] = value
                    else:
                        # Apply validation
                        validated_kwargs[key] = validator_func(key, value)
                
                return await func(*args, **validated_kwargs)
                
            except ValueError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Validation error: {str(e)}"
                )
        return wrapper
    return decorator

# Common validation functions
def validate_trading_inputs(field: str, value):
    """Validate trading-related inputs"""
    if field == 'symbol':
        return InputValidator.validate_symbol(value)
    elif field == 'quantity':
        return InputValidator.validate_quantity(value)
    elif field == 'price' or field == 'amount':
        return InputValidator.validate_amount(value)
    elif field in ['notes', 'description']:
        return InputValidator.sanitize_string(value, max_length=500)
    else:
        return value

def validate_user_inputs(field: str, value):
    """Validate user-related inputs"""
    if field == 'email':
        return InputValidator.validate_email(value)
    elif field == 'password':
        return InputValidator.validate_password(value)
    elif field in ['name', 'username']:
        return InputValidator.sanitize_string(value, max_length=100)
    else:
        return value

def require_https(request: Request):
    """Ensure HTTPS is used in production"""
    if request.url.scheme != "https" and request.headers.get("X-Forwarded-Proto") != "https":
        # Allow HTTP in development
        if request.headers.get("Host", "").startswith("localhost") or request.headers.get("Host", "").startswith("127.0.0.1"):
            return
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="HTTPS required"
        )

async def check_ip_whitelist(request: Request, whitelist: list = None):
    """Check if IP is in whitelist (for admin endpoints)"""
    if not whitelist:
        return  # No whitelist configured
    
    ip_address = get_client_ip(request)
    
    if ip_address not in whitelist:
        audit_logger.log_security_event(
            "IP_NOT_WHITELISTED",
            f"IP {ip_address} attempted to access restricted endpoint",
            ip_address
        )
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

def sanitize_query_params(request: Request):
    """Sanitize query parameters"""
    sanitized_params = {}
    
    for key, value in request.query_params.items():
        try:
            # Basic sanitization
            if isinstance(value, str):
                sanitized_value = InputValidator.sanitize_string(value)
                sanitized_params[key] = sanitized_value
            else:
                sanitized_params[key] = value
        except ValueError:
            # Skip invalid parameters
            logger.warning(f"Invalid query parameter: {key}={value}")
            continue
    
    return sanitized_params

def get_rate_limit_status(request: Request) -> dict:
    """Get current rate limit status for debugging"""
    ip_address = get_client_ip(request)
    identifier = ip_address
    
    # Add user ID if available
    if hasattr(request.state, 'user') and request.state.user:
        identifier = f"{ip_address}:{request.state.user.id}"
    
    # This would need to be implemented in the rate limiter
    # to return current counts without incrementing
    return {
        "identifier": identifier,
        "ip_address": ip_address,
        "user_id": getattr(request.state, 'user', {}).get('id') if hasattr(request.state, 'user') else None
    }
