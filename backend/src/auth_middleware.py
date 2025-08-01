"""
Authentication middleware for Threadr FastAPI application
Handles JWT token validation and user authentication
"""

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any
import logging
from auth_models import User, InvalidTokenError, TokenExpiredError
from auth_service import AuthService
from auth_utils import SecurityUtils

logger = logging.getLogger(__name__)

# Security scheme for JWT tokens
security = HTTPBearer()
optional_security = HTTPBearer(auto_error=False)


class AuthMiddleware:
    """Authentication middleware class"""
    
    def __init__(self, auth_service: AuthService):
        """Initialize middleware with auth service"""
        self.auth_service = auth_service
    
    async def get_current_user_optional(
        self, 
        request: Request,
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_security)
    ) -> Optional[User]:
        """Get current user from token (optional - doesn't raise on failure)"""
        if not credentials:
            return None
        
        try:
            user = await self.auth_service.get_current_user_from_token(credentials.credentials)
            if user:
                # Add user info to request state for logging
                request.state.user = user
                request.state.authenticated = True
            return user
        except Exception as e:
            logger.debug(f"Optional auth failed: {e}")
            return None
    
    async def get_current_user_required(
        self,
        request: Request,
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ) -> User:
        """Get current user from token (required - raises HTTPException on failure)"""
        if not credentials:
            logger.warning("Missing authorization credentials")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        try:
            user = await self.auth_service.get_current_user_from_token(credentials.credentials)
            if not user:
                logger.warning("Invalid or expired token")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired token",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            # Add user info to request state
            request.state.user = user
            request.state.authenticated = True
            
            return user
            
        except InvalidTokenError:
            logger.warning("Invalid token format")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except TokenExpiredError:
            logger.warning("Token expired")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    async def require_role(
        self,
        required_role: str,
        user: User = Depends(get_current_user_required)
    ) -> User:
        """Require specific user role"""
        if user.role.value != required_role and user.role.value != "admin":
            logger.warning(f"Insufficient permissions: user {SecurityUtils.mask_email(user.email)} attempted {required_role} access")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return user
    
    async def require_active_user(
        self,
        user: User = Depends(get_current_user_required)
    ) -> User:
        """Require active user account"""
        if not user.is_active():
            logger.warning(f"Inactive user attempted access: {SecurityUtils.mask_email(user.email)}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive"
            )
        return user
    
    async def require_premium_user(
        self,
        request: Request,
        user: User = Depends(get_current_user_required)
    ) -> User:
        """Require premium user access"""
        client_ip = SecurityUtils.get_client_ip(request)
        premium_info = await self.auth_service.redis_manager.check_premium_access(client_ip, user.email)
        
        if not premium_info.get("has_premium", False):
            logger.warning(f"Non-premium user attempted premium access: {SecurityUtils.mask_email(user.email)}")
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Premium subscription required"
            )
        
        # Add premium info to request state
        request.state.premium_info = premium_info
        
        return user


def create_auth_dependencies(auth_service: AuthService) -> Dict[str, Any]:
    """Create authentication dependency functions"""
    middleware = AuthMiddleware(auth_service)
    
    return {
        "get_current_user_optional": middleware.get_current_user_optional,
        "get_current_user_required": middleware.get_current_user_required,
        "require_active_user": middleware.require_active_user,
        "require_premium_user": middleware.require_premium_user,
        "require_admin": lambda user=Depends(middleware.get_current_user_required): middleware.require_role("admin", user),
    }


def get_request_context(request: Request) -> Dict[str, Any]:
    """Extract request context for logging and analytics"""
    context = {
        "client_ip": SecurityUtils.get_client_ip(request),
        "user_agent": request.headers.get("user-agent", "unknown"),
        "method": request.method,
        "url": str(request.url),
        "authenticated": getattr(request.state, "authenticated", False),
    }
    
    # Add user info if authenticated
    user = getattr(request.state, "user", None)
    if user:
        context.update({
            "user_id": user.user_id,
            "user_email": SecurityUtils.mask_email(user.email),
            "user_role": user.role.value,
        })
    
    # Add premium info if available
    premium_info = getattr(request.state, "premium_info", None)
    if premium_info:
        context["is_premium"] = premium_info.get("has_premium", False)
    
    return context


def log_request(request: Request, message: str, level: str = "info"):
    """Log request with context"""
    context = get_request_context(request)
    log_message = f"{message} - {context}"
    
    if level == "debug":
        logger.debug(log_message)
    elif level == "warning":
        logger.warning(log_message)
    elif level == "error":
        logger.error(log_message)
    else:
        logger.info(log_message)