"""
Authentication models and Pydantic schemas for Threadr
Handles user data structures and validation for the authentication system
"""

from pydantic import BaseModel, EmailStr, field_validator, Field, model_validator, ValidationError
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum
import re


class UserRole(str, Enum):
    """User role enumeration"""
    USER = "user"
    PREMIUM = "premium"
    ADMIN = "admin"


class UserStatus(str, Enum):
    """User account status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


# Request/Response Models
class UserRegistrationRequest(BaseModel):
    """User registration request schema"""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    confirm_password: str = Field(..., min_length=8, max_length=128)
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        """Validate email format and domain"""
        if not v or '@' not in v:
            raise ValueError('Invalid email format')
        
        # Basic email validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError('Invalid email format')
        
        return v.lower().strip()
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        """validate password strength"""
        if not v:
            raise ValueError('Password is required')
        
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        if len(v) > 128:
            raise ValueError('Password must not exceed 128 characters')
        
        # Check for at least one uppercase, one lowercase, one digit
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        
        return v
    
    @field_validator('confirm_password')
    @classmethod
    def validate_password_match(cls, v, info):
        """Validate password confirmation matches password"""
        if 'password' in info.data and v != info.data['password']:
            raise ValueError('Passwords do not match')
        return v


class UserLoginRequest(BaseModel):
    """User login request schema"""
    email: EmailStr
    password: str = Field(..., min_length=1, max_length=128)
    remember_me: bool = Field(default=False, description="Extended session duration for 30 days")
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        """Validate and normalize email"""
        return v.lower().strip()


class UserResponse(BaseModel):
    """User response schema (public user data)"""
    user_id: str
    email: str
    role: UserRole
    status: UserStatus
    created_at: datetime
    last_login_at: Optional[datetime] = None
    is_premium: bool = False
    premium_expires_at: Optional[datetime] = None
    usage_stats: Optional[Dict[str, Any]] = None


class TokenResponse(BaseModel):
    """JWT token response schema"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    refresh_token: Optional[str] = None
    user: UserResponse


class TokenRefreshRequest(BaseModel):
    """Token refresh request schema"""
    refresh_token: str


class TokenPayload(BaseModel):
    """JWT token payload schema"""
    sub: str  # user_id
    email: str
    role: str
    exp: int
    iat: int
    type: str = "access"  # access or refresh


class PasswordChangeRequest(BaseModel):
    """Password change request schema"""
    current_password: str = Field(..., min_length=1, max_length=128)
    new_password: str = Field(..., min_length=8, max_length=128)
    confirm_new_password: str = Field(..., min_length=8, max_length=128)
    
    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v):
        """Validate new password strength"""
        if not v:
            raise ValueError('New password is required')
        
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        if len(v) > 128:
            raise ValueError('Password must not exceed 128 characters')
        
        # Check for at least one uppercase, one lowercase, one digit
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        
        return v
    
    @field_validator('confirm_new_password')
    @classmethod
    def validate_new_password_match(cls, v, info):
        """Validate new password confirmation matches new password"""
        if 'new_password' in info.data and v != info.data['new_password']:
            raise ValueError('New passwords do not match')
        return v


# Internal Data Models (for storage)
class User(BaseModel):
    """Internal user model for storage"""
    user_id: str
    email: str
    password_hash: str
    role: UserRole = UserRole.USER
    status: UserStatus = UserStatus.ACTIVE
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None
    login_count: int = 0
    failed_login_attempts: int = 0
    last_failed_login: Optional[datetime] = None
    is_email_verified: bool = False
    email_verification_token: Optional[str] = None
    password_reset_token: Optional[str] = None
    password_reset_expires: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def to_response(self, is_premium: bool = False, premium_expires_at: Optional[datetime] = None, 
                   usage_stats: Optional[Dict[str, Any]] = None) -> UserResponse:
        """Convert to public user response"""
        return UserResponse(
            user_id=self.user_id,
            email=self.email,
            role=self.role,
            status=self.status,
            created_at=self.created_at,
            last_login_at=self.last_login_at,
            is_premium=is_premium,
            premium_expires_at=premium_expires_at,
            usage_stats=usage_stats
        )
    
    def is_active(self) -> bool:
        """Check if user account is active"""
        return self.status == UserStatus.ACTIVE
    
    def is_suspended(self) -> bool:
        """Check if user account is suspended"""
        return self.status == UserStatus.SUSPENDED
    
    def should_lock_account(self, max_attempts: int = 5) -> bool:
        """Check if account should be locked due to failed login attempts"""
        return self.failed_login_attempts >= max_attempts


class AuthError(Exception):
    """Authentication error base class"""
    pass


class InvalidCredentialsError(AuthError):
    """Invalid credentials error"""
    pass


class UserNotFoundError(AuthError):
    """User not found error"""
    pass


class UserAlreadyExistsError(AuthError):
    """User already exists error"""
    pass


class AccountSuspendedError(AuthError):
    """Account suspended error"""
    pass


class InvalidTokenError(AuthError):
    """Invalid token error"""
    pass


class TokenExpiredError(AuthError):
    """Token expired error"""
    pass