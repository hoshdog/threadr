"""
Authentication API routes for Threadr
Handles user registration, login, logout, and user management endpoints
"""

from fastapi import APIRouter, HTTPException, status, Request, Depends
from fastapi.responses import JSONResponse
from typing import Dict, Any
import logging
from datetime import datetime

try:
    from ..models.auth import (
        UserRegistrationRequest, UserLoginRequest, TokenResponse, UserResponse,
        TokenRefreshRequest, PasswordChangeRequest, UserAlreadyExistsError,
        UserNotFoundError, InvalidCredentialsError, AccountSuspendedError,
        AuthError, User
    )
except ImportError:
    from src.models.auth import (
        UserRegistrationRequest, UserLoginRequest, TokenResponse, UserResponse,
        TokenRefreshRequest, PasswordChangeRequest, UserAlreadyExistsError,
        UserNotFoundError, InvalidCredentialsError, AccountSuspendedError,
        AuthError, User
    )
try:
    from ..services.auth.auth_service import AuthService
except ImportError:
    from src.services.auth.auth_service import AuthService
try:
    from ..middleware.auth import create_auth_dependencies, log_request, get_request_context
except ImportError:
    from src.middleware.auth import create_auth_dependencies, log_request, get_request_context
try:
    from ..services.auth.auth_utils import SecurityUtils
except ImportError:
    from src.services.auth.auth_utils import SecurityUtils

logger = logging.getLogger(__name__)


def create_auth_router(auth_service: AuthService) -> APIRouter:
    """Create authentication router with all auth endpoints"""
    
    router = APIRouter(prefix="/api/auth", tags=["authentication"])
    
    # Create auth dependencies
    auth_deps = create_auth_dependencies(auth_service)
    get_current_user_optional = auth_deps["get_current_user_optional"]
    get_current_user_required = auth_deps["get_current_user_required"]
    require_active_user = auth_deps["require_active_user"]
    
    @router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
    async def register_user(
        registration_data: UserRegistrationRequest,
        request: Request
    ) -> TokenResponse:
        """Register a new user account"""
        client_ip = SecurityUtils.get_client_ip(request)
        log_request(request, f"User registration attempt for {SecurityUtils.mask_email(registration_data.email)}")
        
        try:
            # Manual password validation as fallback for model validation issues
            if registration_data.password != registration_data.confirm_password:
                log_request(request, f"Registration validation error: Passwords do not match", "warning")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Passwords do not match"
                )
                
            user, token_response = await auth_service.register_user(registration_data, client_ip)
            
            log_request(request, f"User registered successfully: {SecurityUtils.mask_email(user.email)}")
            
            return token_response
            
        except UserAlreadyExistsError:
            log_request(request, f"Registration failed - user exists: {SecurityUtils.mask_email(registration_data.email)}", "warning")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists"
            )
        except ValueError as e:
            log_request(request, f"Registration validation error: {str(e)}", "warning")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except AuthError as e:
            log_request(request, f"Registration auth error: {str(e)}", "error")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            log_request(request, f"Registration unexpected error: {str(e)}", "error")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Registration failed"
            )
    
    @router.post("/login", response_model=TokenResponse)
    async def login_user(
        login_data: UserLoginRequest,
        request: Request
    ) -> TokenResponse:
        """Authenticate user and return access token"""
        client_ip = SecurityUtils.get_client_ip(request)
        log_request(request, f"Login attempt for {SecurityUtils.mask_email(login_data.email)}")
        
        try:
            token_response = await auth_service.login_user(login_data, client_ip)
            
            log_request(request, f"User logged in successfully: {SecurityUtils.mask_email(login_data.email)}")
            
            return token_response
            
        except InvalidCredentialsError:
            log_request(request, f"Login failed - invalid credentials: {SecurityUtils.mask_email(login_data.email)}", "warning")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        except AccountSuspendedError as e:
            log_request(request, f"Login failed - account suspended: {SecurityUtils.mask_email(login_data.email)}", "warning")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e)
            )
        except AuthError as e:
            log_request(request, f"Login auth error: {str(e)}", "error")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            log_request(request, f"Login unexpected error: {str(e)}", "error")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Login failed"
            )
    
    @router.post("/logout")
    async def logout_user(
        request: Request,
        current_user: User = Depends(get_current_user_required)
    ) -> Dict[str, str]:
        """Logout user and invalidate session"""
        log_request(request, f"Logout request from {SecurityUtils.mask_email(current_user.email)}")
        
        try:
            # Get token from Authorization header
            auth_header = request.headers.get("authorization", "")
            if auth_header.startswith("Bearer "):
                access_token = auth_header[7:]  # Remove "Bearer " prefix
            else:
                access_token = ""
            
            success = await auth_service.logout_user(access_token, current_user.user_id)
            
            if success:
                log_request(request, f"User logged out successfully: {SecurityUtils.mask_email(current_user.email)}")
                return {"message": "Logged out successfully"}
            else:
                log_request(request, f"Logout failed for user: {SecurityUtils.mask_email(current_user.email)}", "warning")
                return {"message": "Logout completed (session may have already expired)"}
                
        except Exception as e:
            log_request(request, f"Logout error: {str(e)}", "error")
            # Don't fail logout on errors - just log and return success
            return {"message": "Logged out successfully"}
    
    @router.get("/me", response_model=UserResponse)
    async def get_current_user(
        request: Request,
        current_user: User = Depends(get_current_user_required)
    ) -> UserResponse:
        """Get current user information"""
        log_request(request, f"User info request from {SecurityUtils.mask_email(current_user.email)}")
        
        try:
            client_ip = SecurityUtils.get_client_ip(request)
            
            # Get premium access info
            premium_info = await auth_service.redis_manager.check_premium_access(client_ip, current_user.email)
            
            # Get usage stats
            usage_stats = await auth_service.redis_manager.get_usage_count(client_ip, current_user.email, "daily")
            monthly_usage = await auth_service.redis_manager.get_usage_count(client_ip, current_user.email, "monthly")
            usage_stats.update(monthly_usage)
            
            return current_user.to_response(
                is_premium=premium_info.get("has_premium", False),
                premium_expires_at=datetime.fromisoformat(premium_info["expires_at"]) if premium_info.get("expires_at") else None,
                usage_stats=usage_stats
            )
            
        except Exception as e:
            log_request(request, f"Error getting user info: {str(e)}", "error")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve user information"
            )
    
    @router.post("/refresh", response_model=TokenResponse)
    async def refresh_token(
        refresh_data: TokenRefreshRequest,
        request: Request
    ) -> TokenResponse:
        """Refresh access token using refresh token"""
        log_request(request, "Token refresh request")
        
        try:
            token_response = await auth_service.refresh_token(refresh_data.refresh_token)
            
            log_request(request, f"Token refreshed successfully for {SecurityUtils.mask_email(token_response.user.email)}")
            
            return token_response
            
        except InvalidCredentialsError:
            log_request(request, "Token refresh failed - invalid refresh token", "warning")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        except Exception as e:
            log_request(request, f"Token refresh error: {str(e)}", "error")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token refresh failed"
            )
    
    @router.post("/change-password")
    async def change_password(
        password_data: PasswordChangeRequest,
        request: Request,
        current_user: User = Depends(require_active_user)
    ) -> Dict[str, str]:
        """Change user password"""
        log_request(request, f"Password change request from {SecurityUtils.mask_email(current_user.email)}")
        
        try:
            # Verify current password
            try:
                from ..services.auth.auth_utils import verify_password, hash_password
            except ImportError:
                from src.services.auth.auth_utils import verify_password, hash_password
            
            if not verify_password(password_data.current_password, current_user.password_hash):
                log_request(request, f"Password change failed - invalid current password: {SecurityUtils.mask_email(current_user.email)}", "warning")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Current password is incorrect"
                )
            
            # Update password
            current_user.password_hash = hash_password(password_data.new_password)
            current_user.updated_at = datetime.utcnow()
            
            # Store updated user
            success = await auth_service._store_user(current_user)
            
            if success:
                log_request(request, f"Password changed successfully for {SecurityUtils.mask_email(current_user.email)}")
                return {"message": "Password changed successfully"}
            else:
                log_request(request, f"Password change storage failed for {SecurityUtils.mask_email(current_user.email)}", "error")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to update password"
                )
                
        except HTTPException:
            raise
        except ValueError as e:
            log_request(request, f"Password change validation error: {str(e)}", "warning")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            log_request(request, f"Password change unexpected error: {str(e)}", "error")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Password change failed"
            )
    
    @router.get("/password-strength")
    async def check_password_strength(
        password: str,
        request: Request
    ) -> Dict[str, Any]:
        """Check password strength (utility endpoint)"""
        try:
            strength_info = SecurityUtils.get_password_strength_score(password)
            return strength_info
            
        except Exception as e:
            log_request(request, f"Password strength check error: {str(e)}", "error")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Password strength check failed"
            )
    
    @router.get("/debug/deployment-test")
    async def deployment_test() -> Dict[str, str]:
        """Test endpoint to verify deployment changes"""
        return {
            "message": "Deployment test endpoint active", 
            "timestamp": datetime.utcnow().isoformat(),
            "fix_version": "dual-layer-password-validation-v2"
        }
    
    @router.get("/session/status")
    async def get_session_status(
        request: Request,
        current_user: User = Depends(get_current_user_optional)
    ) -> Dict[str, Any]:
        """Get current session status"""
        context = get_request_context(request)
        
        if current_user:
            # Get premium info
            client_ip = SecurityUtils.get_client_ip(request)
            premium_info = await auth_service.redis_manager.check_premium_access(client_ip, current_user.email)
            
            return {
                "authenticated": True,
                "user": {
                    "user_id": current_user.user_id,
                    "email": current_user.email,
                    "role": current_user.role.value,
                    "is_premium": premium_info.get("has_premium", False)
                },
                "session": {
                    "ip": context["client_ip"],
                    "user_agent": context["user_agent"]
                }
            }
        else:
            return {
                "authenticated": False,
                "session": {
                    "ip": context["client_ip"],
                    "user_agent": context["user_agent"]
                }
            }
    
    @router.get("/debug/storage")
    async def debug_storage_components(request: Request) -> Dict[str, Any]:
        """Debug endpoint to test storage components (Redis and PostgreSQL)"""
        log_request(request, "Storage components debug request")
        
        try:
            # Test storage components
            results = await auth_service.test_storage_components()
            
            # Add timestamp and request info
            results["timestamp"] = datetime.utcnow().isoformat()
            results["client_ip"] = SecurityUtils.get_client_ip(request)
            
            log_request(request, f"Storage debug completed: Redis={results.get('redis_client', False)}, PostgreSQL={results.get('postgres_connection', False)}")
            
            return {
                "status": "success",
                "storage_diagnostics": results
            }
        except Exception as e:
            log_request(request, f"Storage debug error: {e}", "error")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    return router


# Create a default router instance for backward compatibility with main.py imports
# This will be a minimal router that can be imported but requires proper initialization
router = APIRouter(prefix="/api/auth", tags=["authentication"])

# Add a note that this router needs to be properly initialized
@router.get("/")
async def auth_router_not_initialized():
    """Placeholder endpoint - this router needs proper initialization via create_auth_router()"""
    return {"error": "Auth router not properly initialized. Use create_auth_router() function."}