"""
JWT Token utilities and authentication helper functions for Threadr
Handles token generation, validation, and password hashing
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import os
import secrets
import logging
from passlib.context import CryptContext
from jose import JWTError, jwt
from auth_models import TokenPayload, User, InvalidTokenError, TokenExpiredError

logger = logging.getLogger(__name__)

# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32))
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "60"))  # 1 hour
JWT_REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "30"))  # 30 days

# Log warning if using default secret key
if not os.getenv("JWT_SECRET_KEY"):
    logger.warning("Using auto-generated JWT_SECRET_KEY. This should be set in production!")


class TokenService:
    """Service for handling JWT tokens"""
    
    @staticmethod
    def create_access_token(user: User, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token for user"""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        
        payload = {
            "sub": user.user_id,
            "email": user.email,
            "role": user.role.value,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        }
        
        try:
            token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
            logger.debug(f"Created access token for user {user.email}")
            return token
        except Exception as e:
            logger.error(f"Error creating access token: {e}")
            raise InvalidTokenError("Failed to create access token")
    
    @staticmethod
    def create_refresh_token(user: User, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT refresh token for user"""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=JWT_REFRESH_TOKEN_EXPIRE_DAYS)
        
        payload = {
            "sub": user.user_id,
            "email": user.email,
            "role": user.role.value,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        }
        
        try:
            token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
            logger.debug(f"Created refresh token for user {user.email}")
            return token
        except Exception as e:
            logger.error(f"Error creating refresh token: {e}")
            raise InvalidTokenError("Failed to create refresh token")
    
    @staticmethod
    def verify_token(token: str, expected_type: str = "access") -> TokenPayload:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            
            # Validate token type
            token_type = payload.get("type", "access")
            if token_type != expected_type:
                logger.warning(f"Invalid token type: expected {expected_type}, got {token_type}")
                raise InvalidTokenError(f"Invalid token type")
            
            # Validate required fields
            user_id = payload.get("sub")
            email = payload.get("email")
            role = payload.get("role")
            exp = payload.get("exp")
            iat = payload.get("iat")
            
            if not all([user_id, email, role, exp, iat]):
                logger.warning("Token missing required fields")
                raise InvalidTokenError("Invalid token payload")
            
            # Check expiration
            if datetime.utcnow().timestamp() > exp:
                logger.debug(f"Token expired for user {email}")
                raise TokenExpiredError("Token has expired")
            
            return TokenPayload(
                sub=user_id,
                email=email,
                role=role,
                exp=exp,
                iat=iat,
                type=token_type
            )
            
        except JWTError as e:
            logger.warning(f"JWT decode error: {e}")
            raise InvalidTokenError("Invalid token")
        except TokenExpiredError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error verifying token: {e}")
            raise InvalidTokenError("Token verification failed")
    
    @staticmethod
    def get_token_expiry_seconds(expires_delta: Optional[timedelta] = None) -> int:
        """Get token expiry time in seconds"""
        if expires_delta:
            return int(expires_delta.total_seconds())
        return JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60


class PasswordService:
    """Service for password hashing and verification"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt"""
        try:
            return pwd_context.hash(password)
        except Exception as e:
            logger.error(f"Error hashing password: {e}")
            raise ValueError("Failed to hash password")
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            logger.error(f"Error verifying password: {e}")
            return False
    
    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """Generate secure random token"""
        return secrets.token_urlsafe(length)


class SecurityUtils:
    """Security utility functions"""
    
    @staticmethod
    def generate_user_id() -> str:
        """Generate unique user ID"""
        return f"user_{secrets.token_urlsafe(16)}"
    
    @staticmethod
    def is_email_valid(email: str) -> bool:
        """Basic email validation"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def sanitize_email(email: str) -> str:
        """Sanitize and normalize email"""
        if not email:
            return ""
        return email.lower().strip()
    
    @staticmethod
    def get_client_ip(request) -> str:
        """Extract client IP from request"""
        # Check for forwarded headers (Railway, Cloudflare, etc.)
        forwarded_for = getattr(request, 'headers', {}).get('x-forwarded-for')
        if forwarded_for:
            # Get the first IP in the chain (original client)
            return forwarded_for.split(',')[0].strip()
        
        real_ip = getattr(request, 'headers', {}).get('x-real-ip')
        if real_ip:
            return real_ip.strip()
        
        # Fallback to direct client IP
        client_host = getattr(request, 'client', None)
        if client_host and hasattr(client_host, 'host'):
            return client_host.host
        
        return "unknown"
    
    @staticmethod
    def create_session_data(user: User, client_ip: str) -> Dict[str, Any]:
        """Create session data for Redis storage"""
        return {
            "user_id": user.user_id,
            "email": user.email,
            "role": user.role.value,
            "status": user.status.value,
            "login_timestamp": datetime.utcnow().isoformat(),
            "client_ip": client_ip,
            "last_activity": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def mask_email(email: str) -> str:
        """Mask email for logging/display purposes"""
        if not email or '@' not in email:
            return "***"
        
        local, domain = email.split('@', 1)
        if len(local) <= 2:
            masked_local = '*' * len(local)
        else:
            masked_local = local[0] + '*' * (len(local) - 2) + local[-1]
        
        return f"{masked_local}@{domain}"
    
    @staticmethod
    def get_password_strength_score(password: str) -> Dict[str, Any]:
        """Calculate password strength score"""
        score = 0
        feedback = []
        
        # Length check
        if len(password) >= 8:
            score += 1
        else:
            feedback.append("Use at least 8 characters")
        
        if len(password) >= 12:
            score += 1
        
        # Character variety checks
        if any(c.islower() for c in password):
            score += 1
        else:
            feedback.append("Include lowercase letters")
        
        if any(c.isupper() for c in password):
            score += 1
        else:
            feedback.append("Include uppercase letters")
        
        if any(c.isdigit() for c in password):
            score += 1
        else:
            feedback.append("Include numbers")
        
        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            score += 1
            feedback.append("Good! Contains special characters")
        else:
            feedback.append("Consider adding special characters")
        
        # Common patterns check
        common_patterns = ['123', 'abc', 'password', 'qwerty']
        if any(pattern in password.lower() for pattern in common_patterns):
            score -= 1
            feedback.append("Avoid common patterns")
        
        strength_levels = {
            0: "Very Weak",
            1: "Very Weak", 
            2: "Weak",
            3: "Fair",
            4: "Good",
            5: "Strong",
            6: "Very Strong"
        }
        
        strength = strength_levels.get(max(0, min(6, score)), "Unknown")
        
        return {
            "score": max(0, score),
            "max_score": 6,
            "strength": strength,
            "feedback": feedback
        }


# Export commonly used functions
hash_password = PasswordService.hash_password
verify_password = PasswordService.verify_password
create_access_token = TokenService.create_access_token
create_refresh_token = TokenService.create_refresh_token
verify_token = TokenService.verify_token
generate_user_id = SecurityUtils.generate_user_id