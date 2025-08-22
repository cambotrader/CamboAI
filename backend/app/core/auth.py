"""
🔐 ADVANCED AUTHENTICATION & SECURITY - INSTITUTIONAL GRADE
Complete authentication system with JWT, API keys, RBAC, and security monitoring
"""

import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from sqlalchemy.orm import Session
import secrets
import hashlib
import redis
from dataclasses import dataclass
from enum import Enum
import logging
import asyncio
from collections import defaultdict, deque
import time
import os

from ..database import get_db
from ..models.trading_models import User, Account

logger = logging.getLogger(__name__)

# Security Configuration
_env_secret = os.getenv("JWT_SECRET_KEY")
if _env_secret and len(_env_secret) >= 32:
    SECRET_KEY = _env_secret
else:
    # Generate an ephemeral development key if not provided; warn loudly
    SECRET_KEY = secrets.token_hex(32)
    logger.warning("JWT_SECRET_KEY not set or too short; using ephemeral in-memory key for development. Set JWT_SECRET_KEY in the environment for production.")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 30
API_KEY_EXPIRE_DAYS = 365

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security schemes
security = HTTPBearer()
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

class UserRole(Enum):
    ADMIN = "admin"
    PROFESSIONAL = "professional"
    RETAIL = "retail"
    DEMO = "demo"
    READONLY = "readonly"

class Permission(Enum):
    # Trading permissions
    TRADE_STOCKS = "trade_stocks"
    TRADE_OPTIONS = "trade_options"
    TRADE_FUTURES = "trade_futures"
    TRADE_FOREX = "trade_forex"
    TRADE_CRYPTO = "trade_crypto"
    
    # Account permissions
    VIEW_ACCOUNT = "view_account"
    MODIFY_ACCOUNT = "modify_account"
    TRANSFER_FUNDS = "transfer_funds"
    
    # Data permissions
    VIEW_MARKET_DATA = "view_market_data"
    VIEW_LEVEL2_DATA = "view_level2_data"
    VIEW_OPTIONS_CHAIN = "view_options_chain"
    
    # AI and Strategies
    USE_AI_SIGNALS = "use_ai_signals"
    CREATE_STRATEGIES = "create_strategies"
    USE_ADVANCED_ANALYTICS = "use_advanced_analytics"
    
    # Administrative
    ADMIN_USERS = "admin_users"
    ADMIN_SYSTEM = "admin_system"
    VIEW_ALL_ACCOUNTS = "view_all_accounts"

@dataclass
class TokenData:
    user_id: str
    username: str
    email: str
    role: UserRole
    permissions: List[Permission]
    account_ids: List[str]
    expires_at: datetime

@dataclass
class SecurityEvent:
    event_type: str
    user_id: Optional[str]
    ip_address: str
    user_agent: str
    timestamp: datetime
    details: Dict[str, Any]
    severity: str  # low, medium, high, critical

class SecurityMonitor:
    """Advanced security monitoring and threat detection"""
    
    def __init__(self):
        self.failed_attempts = defaultdict(lambda: deque(maxlen=100))
        self.suspicious_activity = defaultdict(list)
        self.rate_limiters = defaultdict(lambda: deque(maxlen=1000))
        self.blocked_ips = set()
        self.security_events = deque(maxlen=10000)
        
        # Rate limiting thresholds
        self.rate_limits = {
            "login": (5, 300),      # 5 attempts per 5 minutes
            "api_calls": (1000, 60), # 1000 calls per minute
            "order_placement": (100, 60), # 100 orders per minute
            "data_requests": (500, 60)    # 500 data requests per minute
        }
        
        # Start monitoring tasks
        asyncio.create_task(self._cleanup_expired_data())
        asyncio.create_task(self._analyze_security_patterns())
    
    def record_failed_login(self, identifier: str, ip_address: str, user_agent: str):
        """Record failed login attempt"""
        
        now = time.time()
        self.failed_attempts[identifier].append(now)
        
        # Check for brute force attack
        recent_attempts = [t for t in self.failed_attempts[identifier] if now - t < 300]  # 5 minutes
        
        if len(recent_attempts) >= 5:
            self._trigger_security_event(
                event_type="brute_force_attempt",
                user_id=None,
                ip_address=ip_address,
                user_agent=user_agent,
                details={"identifier": identifier, "attempts": len(recent_attempts)},
                severity="high"
            )
            
            # Temporarily block IP
            self.blocked_ips.add(ip_address)
            logger.warning(f"🚨 IP {ip_address} blocked due to brute force attempts")
    
    def check_rate_limit(self, identifier: str, action_type: str) -> bool:
        """Check if action is within rate limits"""
        
        if action_type not in self.rate_limits:
            return True
        
        max_requests, time_window = self.rate_limits[action_type]
        now = time.time()
        
        # Clean old entries
        key = f"{identifier}:{action_type}"
        self.rate_limiters[key] = deque(
            [t for t in self.rate_limiters[key] if now - t < time_window],
            maxlen=1000
        )
        
        # Check limit
        if len(self.rate_limiters[key]) >= max_requests:
            self._trigger_security_event(
                event_type="rate_limit_exceeded",
                user_id=identifier if "@" not in identifier else None,
                ip_address=identifier if "." in identifier else "unknown",
                user_agent="",
                details={"action": action_type, "requests": len(self.rate_limiters[key])},
                severity="medium"
            )
            return False
        
        # Record request
        self.rate_limiters[key].append(now)
        return True
    
    def is_ip_blocked(self, ip_address: str) -> bool:
        """Check if IP address is blocked"""
        return ip_address in self.blocked_ips
    
    def _trigger_security_event(self, event_type: str, user_id: Optional[str], 
                              ip_address: str, user_agent: str, 
                              details: Dict[str, Any], severity: str):
        """Record security event"""
        
        event = SecurityEvent(
            event_type=event_type,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            timestamp=datetime.utcnow(),
            details=details,
            severity=severity
        )
        
        self.security_events.append(event)
        
        # Log high severity events
        if severity in ["high", "critical"]:
            logger.warning(f"🚨 Security Event [{severity.upper()}]: {event_type} from {ip_address}")
    
    async def _cleanup_expired_data(self):
        """Clean up expired security data"""
        while True:
            try:
                await asyncio.sleep(3600)  # Every hour
                
                now = time.time()
                cutoff = now - 86400  # 24 hours
                
                # Clean failed attempts
                for identifier in list(self.failed_attempts.keys()):
                    self.failed_attempts[identifier] = deque(
                        [t for t in self.failed_attempts[identifier] if t > cutoff],
                        maxlen=100
                    )
                    if not self.failed_attempts[identifier]:
                        del self.failed_attempts[identifier]
                
                # Clean rate limiters
                for key in list(self.rate_limiters.keys()):
                    self.rate_limiters[key] = deque(
                        [t for t in self.rate_limiters[key] if t > cutoff],
                        maxlen=1000
                    )
                    if not self.rate_limiters[key]:
                        del self.rate_limiters[key]
                
                logger.info("🧹 Security data cleanup completed")
                
            except Exception as e:
                logger.error(f"❌ Security cleanup error: {e}")
    
    async def _analyze_security_patterns(self):
        """Analyze security events for patterns"""
        while True:
            try:
                await asyncio.sleep(300)  # Every 5 minutes
                
                # Analyze recent events
                recent_events = [
                    event for event in self.security_events 
                    if (datetime.utcnow() - event.timestamp).total_seconds() < 3600
                ]
                
                # Pattern detection logic would go here
                # For now, just log summary
                if recent_events:
                    event_counts = defaultdict(int)
                    for event in recent_events:
                        event_counts[event.event_type] += 1
                    
                    logger.info(f"🔍 Security summary: {dict(event_counts)}")
                
            except Exception as e:
                logger.error(f"❌ Security analysis error: {e}")

# Global security monitor
security_monitor = SecurityMonitor()

class RolePermissionManager:
    """Manage role-based permissions"""
    
    def __init__(self):
        self.role_permissions = {
            UserRole.ADMIN: [
                Permission.TRADE_STOCKS, Permission.TRADE_OPTIONS, Permission.TRADE_FUTURES,
                Permission.TRADE_FOREX, Permission.TRADE_CRYPTO, Permission.VIEW_ACCOUNT,
                Permission.MODIFY_ACCOUNT, Permission.TRANSFER_FUNDS, Permission.VIEW_MARKET_DATA,
                Permission.VIEW_LEVEL2_DATA, Permission.VIEW_OPTIONS_CHAIN, Permission.USE_AI_SIGNALS,
                Permission.CREATE_STRATEGIES, Permission.USE_ADVANCED_ANALYTICS, Permission.ADMIN_USERS,
                Permission.ADMIN_SYSTEM, Permission.VIEW_ALL_ACCOUNTS
            ],
            UserRole.PROFESSIONAL: [
                Permission.TRADE_STOCKS, Permission.TRADE_OPTIONS, Permission.TRADE_FUTURES,
                Permission.TRADE_FOREX, Permission.TRADE_CRYPTO, Permission.VIEW_ACCOUNT,
                Permission.MODIFY_ACCOUNT, Permission.TRANSFER_FUNDS, Permission.VIEW_MARKET_DATA,
                Permission.VIEW_LEVEL2_DATA, Permission.VIEW_OPTIONS_CHAIN, Permission.USE_AI_SIGNALS,
                Permission.CREATE_STRATEGIES, Permission.USE_ADVANCED_ANALYTICS
            ],
            UserRole.RETAIL: [
                Permission.TRADE_STOCKS, Permission.TRADE_OPTIONS, Permission.VIEW_ACCOUNT,
                Permission.MODIFY_ACCOUNT, Permission.TRANSFER_FUNDS, Permission.VIEW_MARKET_DATA,
                Permission.VIEW_OPTIONS_CHAIN, Permission.USE_AI_SIGNALS
            ],
            UserRole.DEMO: [
                Permission.VIEW_ACCOUNT, Permission.VIEW_MARKET_DATA, Permission.USE_AI_SIGNALS
            ],
            UserRole.READONLY: [
                Permission.VIEW_ACCOUNT, Permission.VIEW_MARKET_DATA
            ]
        }
    
    def get_user_permissions(self, role: UserRole) -> List[Permission]:
        """Get permissions for user role"""
        return self.role_permissions.get(role, [])
    
    def has_permission(self, role: UserRole, permission: Permission) -> bool:
        """Check if role has specific permission"""
        return permission in self.get_user_permissions(role)

role_manager = RolePermissionManager()

class AuthenticationManager:
    """Core authentication functionality"""
    
    def __init__(self):
        self.redis_client = None
        self.active_tokens = set()
        self.api_keys = {}  # In production, store in database
    
    async def initialize_redis(self, redis_url: str = "redis://localhost:6379"):
        """Initialize Redis for token management"""
        try:
            import redis.asyncio as redis
            self.redis_client = redis.from_url(redis_url)
            await self.redis_client.ping()
            logger.info("✅ Redis initialized for authentication")
        except Exception as e:
            logger.warning(f"⚠️ Redis not available for auth: {e}")
    
    def hash_password(self, password: str) -> str:
        """Hash password securely"""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def create_access_token(self, user: User) -> str:
        """Create JWT access token"""
        
        # Determine user role
        role = UserRole.PROFESSIONAL if user.is_professional else UserRole.RETAIL
        if user.account_type.value == "demo":
            role = UserRole.DEMO
        
        # Get user permissions
        permissions = role_manager.get_user_permissions(role)
        
        # Get user account IDs
        account_ids = [str(account.id) for account in user.accounts if account.is_active]
        
        # Create token payload
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {
            "user_id": str(user.id),
            "username": user.username,
            "email": user.email,
            "role": role.value,
            "permissions": [p.value for p in permissions],
            "account_ids": account_ids,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        }
        
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        self.active_tokens.add(token)
        
        return token
    
    def create_refresh_token(self, user: User) -> str:
        """Create refresh token"""
        
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        payload = {
            "user_id": str(user.id),
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        }
        
        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    
    def decode_token(self, token: str) -> TokenData:
        """Decode and validate JWT token"""
        
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            
            # Check if token is active
            if token not in self.active_tokens:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has been revoked"
                )
            
            # Extract data
            user_id = payload.get("user_id")
            username = payload.get("username")
            email = payload.get("email")
            role = UserRole(payload.get("role"))
            permissions = [Permission(p) for p in payload.get("permissions", [])]
            account_ids = payload.get("account_ids", [])
            expires_at = datetime.fromtimestamp(payload.get("exp"))
            
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload"
                )
            
            return TokenData(
                user_id=user_id,
                username=username,
                email=email,
                role=role,
                permissions=permissions,
                account_ids=account_ids,
                expires_at=expires_at
            )
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
    
    def revoke_token(self, token: str):
        """Revoke a token"""
        self.active_tokens.discard(token)
        
        # In production, add to Redis blacklist with expiration
        if self.redis_client:
            # Would implement Redis-based token blacklist
            pass
    
    def create_api_key(self, user: User, name: str) -> tuple[str, str]:
        """Create API key for user"""
        
        key_id = secrets.token_urlsafe(16)
        key_secret = secrets.token_urlsafe(32)
        key_hash = hashlib.sha256(f"{key_id}:{key_secret}".encode()).hexdigest()
        
        # Store API key info
        self.api_keys[key_hash] = {
            "user_id": str(user.id),
            "key_id": key_id,
            "name": name,
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(days=API_KEY_EXPIRE_DAYS),
            "is_active": True
        }
        
        return key_id, key_secret
    
    def validate_api_key(self, key_id: str, key_secret: str) -> Optional[Dict[str, Any]]:
        """Validate API key"""
        
        key_hash = hashlib.sha256(f"{key_id}:{key_secret}".encode()).hexdigest()
        key_info = self.api_keys.get(key_hash)
        
        if not key_info or not key_info["is_active"]:
            return None
        
        if key_info["expires_at"] < datetime.utcnow():
            return None
        
        return key_info

# Global authentication manager
auth_manager = AuthenticationManager()

# Dependency functions

async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token"""
    
    # Security checks
    client_ip = request.client.host
    user_agent = request.headers.get("user-agent", "")
    
    if security_monitor.is_ip_blocked(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="IP address temporarily blocked due to suspicious activity"
        )
    
    # Rate limiting
    if not security_monitor.check_rate_limit(client_ip, "api_calls"):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded"
        )
    
    # Decode token
    token_data = auth_manager.decode_token(credentials.credentials)
    
    # Get user from database
    user = db.query(User).filter(User.id == token_data.user_id).first()
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    return user

async def get_current_user_api_key(
    request: Request,
    api_key: Optional[str] = Depends(api_key_header),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Authenticate user via API key"""
    
    if not api_key:
        return None
    
    # Parse API key (format: key_id:key_secret)
    try:
        key_id, key_secret = api_key.split(":", 1)
    except ValueError:
        return None
    
    # Validate API key
    key_info = auth_manager.validate_api_key(key_id, key_secret)
    if not key_info:
        return None
    
    # Get user
    user = db.query(User).filter(User.id == key_info["user_id"]).first()
    if user is None or not user.is_active:
        return None
    
    return user

def require_permission(permission: Permission):
    """Decorator to require specific permission"""
    
    def permission_checker(current_user: User = Depends(get_current_user)):
        # Determine user role
        role = UserRole.PROFESSIONAL if current_user.is_professional else UserRole.RETAIL
        if current_user.account_type.value == "demo":
            role = UserRole.DEMO
        
        # Check permission
        if not role_manager.has_permission(role, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: {permission.value}"
            )
        
        return current_user
    
    return permission_checker

def require_any_permission(permissions: List[Permission]):
    """Decorator to require any of the specified permissions"""
    
    def permission_checker(current_user: User = Depends(get_current_user)):
        # Determine user role
        role = UserRole.PROFESSIONAL if current_user.is_professional else UserRole.RETAIL
        if current_user.account_type.value == "demo":
            role = UserRole.DEMO
        
        # Check if user has any of the required permissions
        has_permission = any(
            role_manager.has_permission(role, perm) 
            for perm in permissions
        )
        
        if not has_permission:
            permission_names = [p.value for p in permissions]
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required one of: {permission_names}"
            )
        
        return current_user
    
    return permission_checker

# Authentication endpoints would be added to a separate auth router

class TwoFactorAuth:
    """Two-factor authentication implementation"""
    
    def __init__(self):
        self.pending_2fa = {}  # In production, use Redis
        self.backup_codes = {}  # In production, use database
    
    def generate_totp_secret(self, user: User) -> str:
        """Generate TOTP secret for user"""
        import pyotp
        
        secret = pyotp.random_base32()
        # Store secret in user profile (encrypted)
        return secret
    
    def verify_totp_token(self, user: User, token: str) -> bool:
        """Verify TOTP token"""
        import pyotp
        
        # Get user's TOTP secret from database
        secret = "user_totp_secret"  # Would get from user profile
        totp = pyotp.TOTP(secret)
        
        return totp.verify(token, valid_window=1)
    
    def generate_backup_codes(self, user: User) -> List[str]:
        """Generate backup codes for 2FA"""
        
        codes = [secrets.token_hex(4).upper() for _ in range(10)]
        self.backup_codes[str(user.id)] = [
            pwd_context.hash(code) for code in codes
        ]
        
        return codes
    
    def verify_backup_code(self, user: User, code: str) -> bool:
        """Verify backup code and invalidate it"""
        
        user_codes = self.backup_codes.get(str(user.id), [])
        
        for i, hashed_code in enumerate(user_codes):
            if pwd_context.verify(code, hashed_code):
                # Remove used code
                self.backup_codes[str(user.id)].pop(i)
                return True
        
        return False

# Global 2FA manager
two_factor_auth = TwoFactorAuth()

# Audit logging
class AuditLogger:
    """Comprehensive audit logging for compliance"""
    
    def __init__(self):
        self.audit_log = deque(maxlen=100000)  # In production, use database
    
    def log_event(self, user_id: str, event_type: str, details: Dict[str, Any],
                  ip_address: str = None, user_agent: str = None):
        """Log audit event"""
        
        event = {
            "timestamp": datetime.utcnow(),
            "user_id": user_id,
            "event_type": event_type,
            "details": details,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "session_id": details.get("session_id")
        }
        
        self.audit_log.append(event)
        
        # Log critical events immediately
        if event_type in ["login", "logout", "password_change", "order_placed", "funds_transfer"]:
            logger.info(f"🔍 Audit: {event_type} by user {user_id}")

# Global audit logger
audit_logger = AuditLogger()

# Export main components
__all__ = [
    'auth_manager', 'security_monitor', 'role_manager', 'two_factor_auth', 'audit_logger',
    'get_current_user', 'get_current_user_api_key', 'require_permission', 'require_any_permission',
    'UserRole', 'Permission', 'TokenData'
]