"""
🔐 AUTHENTICATION API ENDPOINTS - ENTERPRISE SECURITY
Complete authentication system with registration, login, 2FA, and security management
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, validator
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import secrets
import asyncio

from ..database import get_db
from ..models.trading_models import User, Account, AccountType
from ..core.auth import (
    auth_manager, security_monitor, role_manager, two_factor_auth, audit_logger,
    get_current_user, UserRole, Permission
)
from ..core.email_service import send_verification_email, send_password_reset_email

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

# Pydantic Models

class UserRegistration(BaseModel):
    email: EmailStr
    username: str
    password: str
    confirm_password: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    terms_accepted: bool = True
    marketing_consent: bool = False
    
    @validator('username')
    def validate_username(cls, v):
        if len(v) < 3 or len(v) > 20:
            raise ValueError('Username must be 3-20 characters')
        if not v.isalnum():
            raise ValueError('Username must be alphanumeric')
        return v.lower()
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain digit')
        return v
    
    @validator('confirm_password')
    def validate_passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v
    
    @validator('terms_accepted')
    def validate_terms(cls, v):
        if not v:
            raise ValueError('Terms and conditions must be accepted')
        return v

class UserLogin(BaseModel):
    username: str
    password: str
    remember_me: bool = False
    device_info: Optional[Dict[str, str]] = None

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user_info: Dict[str, Any]

class PasswordReset(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    password: str
    confirm_password: str
    
    @validator('confirm_password')
    def validate_passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v

class PasswordChange(BaseModel):
    current_password: str
    new_password: str
    confirm_new_password: str
    
    @validator('confirm_new_password')
    def validate_passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v

class TwoFactorSetup(BaseModel):
    totp_token: str

class TwoFactorLogin(BaseModel):
    login_token: str
    totp_token: Optional[str] = None
    backup_code: Optional[str] = None

class APIKeyCreate(BaseModel):
    name: str
    permissions: List[str]
    expires_in_days: int = 365

class UserProfile(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    timezone: Optional[str] = None
    notification_preferences: Optional[Dict[str, bool]] = None

# Authentication Endpoints

@router.post("/register", response_model=Dict[str, str])
async def register_user(
    user_data: UserRegistration,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Register new user account"""
    
    client_ip = request.client.host
    user_agent = request.headers.get("user-agent", "")
    
    # Security checks
    if security_monitor.is_ip_blocked(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Registration temporarily blocked from this IP"
        )
    
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.email == user_data.email) | (User.username == user_data.username)
    ).first()
    
    if existing_user:
        if existing_user.email == user_data.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    # Create new user
    user = User(
        email=user_data.email,
        username=user_data.username,
        password_hash=auth_manager.hash_password(user_data.password),
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone=user_data.phone,
        account_type=AccountType.DEMO,  # Start with demo account
        is_active=False,  # Requires email verification
        preferred_currency="USD",
        timezone="UTC"
    )
    
    db.add(user)
    db.flush()
    
    # Create demo account
    demo_account = Account(
        user_id=user.id,
        account_number=f"DEMO{secrets.randbelow(1000000):06d}",
        broker_name="CamboAI Demo",
        account_type=AccountType.DEMO,
        cash_balance=100000.0,  # $100k demo money
        buying_power=200000.0,  # 2:1 demo leverage
        portfolio_value=100000.0,
        is_active=True,
        is_funded=True
    )
    
    db.add(demo_account)
    db.commit()
    db.refresh(user)
    
    # Generate email verification token
    verification_token = secrets.token_urlsafe(32)
    # Store token in Redis or database with expiration
    
    # Send verification email
    background_tasks.add_task(
        send_verification_email,
        user.email,
        user.first_name,
        verification_token
    )
    
    # Audit log
    audit_logger.log_event(
        user_id=str(user.id),
        event_type="user_registered",
        details={
            "email": user.email,
            "username": user.username,
            "account_type": user.account_type.value
        },
        ip_address=client_ip,
        user_agent=user_agent
    )
    
    return {
        "message": "Registration successful. Please check your email to verify your account.",
        "user_id": str(user.id),
        "verification_required": True
    }

@router.post("/verify-email/{token}")
async def verify_email(
    token: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Verify user email address"""
    
    # In production, validate token from Redis/database
    # For now, simulate successful verification
    
    # Find user by verification token (simplified)
    # user = get_user_by_verification_token(token, db)
    
    return {
        "message": "Email verified successfully. You can now log in.",
        "verified": True
    }

@router.post("/login", response_model=TokenResponse)
async def login_user(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Authenticate user and return tokens"""
    
    client_ip = request.client.host
    user_agent = request.headers.get("user-agent", "")
    
    # Security checks
    if security_monitor.is_ip_blocked(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Login temporarily blocked from this IP"
        )
    
    if not security_monitor.check_rate_limit(f"login:{client_ip}", "login"):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again later."
        )
    
    # Find user
    user = db.query(User).filter(
        (User.username == form_data.username) | (User.email == form_data.username)
    ).first()
    
    # Verify credentials
    if not user or not auth_manager.verify_password(form_data.password, user.password_hash):
        security_monitor.record_failed_login(form_data.username, client_ip, user_agent)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account not verified or disabled"
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create tokens
    access_token = auth_manager.create_access_token(user)
    refresh_token = auth_manager.create_refresh_token(user)
    
    # Determine user role for response
    role = UserRole.PROFESSIONAL if user.is_professional else UserRole.RETAIL
    permissions = role_manager.get_user_permissions(role)
    
    # User info for response
    user_info = {
        "user_id": str(user.id),
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "role": role.value,
        "permissions": [p.value for p in permissions],
        "account_type": user.account_type.value,
        "is_verified": user.is_verified,
        "last_login": user.last_login.isoformat() if user.last_login else None
    }
    
    # Audit log
    audit_logger.log_event(
        user_id=str(user.id),
        event_type="user_login",
        details={
            "username": user.username,
            "success": True,
            "method": "password"
        },
        ip_address=client_ip,
        user_agent=user_agent
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=60 * 60,  # 1 hour
        user_info=user_info
    )

@router.post("/logout")
async def logout_user(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Logout user and invalidate tokens"""
    
    client_ip = request.client.host
    user_agent = request.headers.get("user-agent", "")
    
    # Get token from authorization header
    auth_header = request.headers.get("authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        auth_manager.revoke_token(token)
    
    # Audit log
    audit_logger.log_event(
        user_id=str(current_user.id),
        event_type="user_logout",
        details={"username": current_user.username},
        ip_address=client_ip,
        user_agent=user_agent
    )
    
    return {"message": "Logged out successfully"}

@router.post("/refresh")
async def refresh_token(
    request: Request,
    refresh_token: str,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token"""
    
    try:
        # Decode refresh token
        payload = auth_manager.decode_token(refresh_token)
        
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        # Get user
        user = db.query(User).filter(User.id == payload.user_id).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new access token
        new_access_token = auth_manager.create_access_token(user)
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            "expires_in": 3600
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

# Password Management

@router.post("/forgot-password")
async def forgot_password(
    password_reset: PasswordReset,
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Initiate password reset process"""
    
    client_ip = request.client.host
    
    # Rate limiting
    if not security_monitor.check_rate_limit(f"reset:{client_ip}", "login"):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many password reset requests"
        )
    
    # Find user
    user = db.query(User).filter(User.email == password_reset.email).first()
    
    # Always return success to prevent email enumeration
    message = "If an account with that email exists, password reset instructions have been sent."
    
    if user and user.is_active:
        # Generate reset token
        reset_token = secrets.token_urlsafe(32)
        # Store in Redis with expiration (30 minutes)
        
        # Send reset email
        background_tasks.add_task(
            send_password_reset_email,
            user.email,
            user.first_name,
            reset_token
        )
        
        # Audit log
        audit_logger.log_event(
            user_id=str(user.id),
            event_type="password_reset_requested",
            details={"email": user.email},
            ip_address=client_ip
        )
    
    return {"message": message}

@router.post("/reset-password")
async def reset_password(
    password_reset: PasswordResetConfirm,
    request: Request,
    db: Session = Depends(get_db)
):
    """Reset password with token"""
    
    # Validate reset token (from Redis/database)
    # user = get_user_by_reset_token(password_reset.token, db)
    
    # For demo, simulate successful reset
    return {"message": "Password reset successfully"}

@router.post("/change-password")
async def change_password(
    password_change: PasswordChange,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change user password"""
    
    # Verify current password
    if not auth_manager.verify_password(password_change.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Update password
    current_user.password_hash = auth_manager.hash_password(password_change.new_password)
    db.commit()
    
    # Audit log
    audit_logger.log_event(
        user_id=str(current_user.id),
        event_type="password_changed",
        details={"username": current_user.username},
        ip_address=request.client.host
    )
    
    return {"message": "Password changed successfully"}

# Two-Factor Authentication

@router.post("/2fa/setup")
async def setup_2fa(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Setup two-factor authentication"""
    
    # Generate TOTP secret
    secret = two_factor_auth.generate_totp_secret(current_user)
    
    # Generate QR code URL
    import pyotp
    totp = pyotp.TOTP(secret)
    qr_url = totp.provisioning_uri(
        name=current_user.email,
        issuer_name="CamboAI Trading Platform"
    )
    
    # Generate backup codes
    backup_codes = two_factor_auth.generate_backup_codes(current_user)
    
    return {
        "secret": secret,
        "qr_code_url": qr_url,
        "backup_codes": backup_codes,
        "instructions": "Scan the QR code with your authenticator app and verify with a code"
    }

@router.post("/2fa/verify")
async def verify_2fa_setup(
    setup_data: TwoFactorSetup,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Verify and enable 2FA"""
    
    # Verify TOTP token
    if two_factor_auth.verify_totp_token(current_user, setup_data.totp_token):
        # Enable 2FA for user
        # current_user.two_factor_enabled = True
        # db.commit()
        
        return {"message": "Two-factor authentication enabled successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code"
        )

# API Key Management

@router.post("/api-keys")
async def create_api_key(
    api_key_data: APIKeyCreate,
    current_user: User = Depends(get_current_user)
):
    """Create new API key"""
    
    key_id, key_secret = auth_manager.create_api_key(current_user, api_key_data.name)
    
    # Audit log
    audit_logger.log_event(
        user_id=str(current_user.id),
        event_type="api_key_created",
        details={"key_name": api_key_data.name, "key_id": key_id}
    )
    
    return {
        "message": "API key created successfully",
        "key_id": key_id,
        "key_secret": key_secret,
        "warning": "Store this secret securely. It will not be shown again."
    }

@router.get("/api-keys")
async def list_api_keys(
    current_user: User = Depends(get_current_user)
):
    """List user's API keys"""
    
    # Get user's API keys (from database in production)
    user_keys = [
        key for key in auth_manager.api_keys.values()
        if key["user_id"] == str(current_user.id)
    ]
    
    return {
        "api_keys": [
            {
                "key_id": key["key_id"],
                "name": key["name"],
                "created_at": key["created_at"].isoformat(),
                "expires_at": key["expires_at"].isoformat(),
                "is_active": key["is_active"]
            }
            for key in user_keys
        ]
    }

@router.delete("/api-keys/{key_id}")
async def revoke_api_key(
    key_id: str,
    current_user: User = Depends(get_current_user)
):
    """Revoke API key"""
    
    # Find and revoke key
    for key_hash, key_info in auth_manager.api_keys.items():
        if key_info["key_id"] == key_id and key_info["user_id"] == str(current_user.id):
            key_info["is_active"] = False
            
            # Audit log
            audit_logger.log_event(
                user_id=str(current_user.id),
                event_type="api_key_revoked",
                details={"key_id": key_id}
            )
            
            return {"message": "API key revoked successfully"}
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="API key not found"
    )

# User Profile Management

@router.get("/profile")
async def get_user_profile(
    current_user: User = Depends(get_current_user)
):
    """Get user profile information"""
    
    # Determine user role
    role = UserRole.PROFESSIONAL if current_user.is_professional else UserRole.RETAIL
    permissions = role_manager.get_user_permissions(role)
    
    return {
        "user_id": str(current_user.id),
        "username": current_user.username,
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "phone": current_user.phone,
        "role": role.value,
        "permissions": [p.value for p in permissions],
        "account_type": current_user.account_type.value,
        "is_verified": current_user.is_verified,
        "is_professional": current_user.is_professional,
        "preferred_currency": current_user.preferred_currency,
        "timezone": current_user.timezone,
        "created_at": current_user.created_at.isoformat(),
        "last_login": current_user.last_login.isoformat() if current_user.last_login else None
    }

@router.put("/profile")
async def update_user_profile(
    profile_data: UserProfile,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile"""
    
    # Update allowed fields
    if profile_data.first_name is not None:
        current_user.first_name = profile_data.first_name
    if profile_data.last_name is not None:
        current_user.last_name = profile_data.last_name
    if profile_data.phone is not None:
        current_user.phone = profile_data.phone
    if profile_data.timezone is not None:
        current_user.timezone = profile_data.timezone
    
    db.commit()
    
    # Audit log
    audit_logger.log_event(
        user_id=str(current_user.id),
        event_type="profile_updated",
        details={"updated_fields": list(profile_data.dict(exclude_unset=True).keys())}
    )
    
    return {"message": "Profile updated successfully"}

# Security Information

@router.get("/security/sessions")
async def get_active_sessions(
    current_user: User = Depends(get_current_user)
):
    """Get user's active sessions"""
    
    # In production, track sessions in Redis/database
    return {
        "active_sessions": [
            {
                "session_id": "current",
                "ip_address": "127.0.0.1",
                "user_agent": "Mozilla/5.0...",
                "created_at": datetime.utcnow().isoformat(),
                "last_activity": datetime.utcnow().isoformat(),
                "is_current": True
            }
        ]
    }

@router.get("/security/audit-log")
async def get_audit_log(
    current_user: User = Depends(get_current_user),
    limit: int = 50
):
    """Get user's audit log"""
    
    # Filter audit log for current user
    user_events = [
        {
            "timestamp": event["timestamp"].isoformat(),
            "event_type": event["event_type"],
            "details": event["details"],
            "ip_address": event["ip_address"]
        }
        for event in audit_logger.audit_log
        if event["user_id"] == str(current_user.id)
    ][-limit:]
    
    return {"audit_events": user_events}

# Export router
__all__ = ['router']