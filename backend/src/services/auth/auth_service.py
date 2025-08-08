"""
Authentication service for Threadr
Handles user registration, login, and session management
Integrates with Redis for user storage and session tracking
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
import logging
import json
import secrets
try:
    from ...models.auth import (
        User, UserRole, UserStatus, UserRegistrationRequest, UserLoginRequest,
        TokenResponse, UserResponse, UserAlreadyExistsError, UserNotFoundError,
        InvalidCredentialsError, AccountSuspendedError, AuthError
    )
except ImportError:
    from src.models.auth import (
        User, UserRole, UserStatus, UserRegistrationRequest, UserLoginRequest,
        TokenResponse, UserResponse, UserAlreadyExistsError, UserNotFoundError,
        InvalidCredentialsError, AccountSuspendedError, AuthError
    )
try:
    from .auth_utils import (
        PasswordService, TokenService, SecurityUtils, hash_password, 
        verify_password, create_access_token, create_refresh_token,
        generate_user_id
    )
except ImportError:
    from src.services.auth.auth_utils import (
        PasswordService, TokenService, SecurityUtils, hash_password, 
        verify_password, create_access_token, create_refresh_token,
        generate_user_id
    )

logger = logging.getLogger(__name__)


class AuthService:
    """Authentication service that manages users via Redis"""
    
    def __init__(self, redis_manager):
        """Initialize auth service with Redis manager"""
        self.redis_manager = redis_manager
        self.user_prefix = "threadr:user:"
        self.user_email_index = "threadr:user:email:"
        self.session_prefix = "threadr:session:"
        self.failed_login_prefix = "threadr:failed_login:"
        self.max_failed_attempts = 5
        self.account_lockout_duration = timedelta(minutes=30)
    
    async def register_user(self, registration_data: UserRegistrationRequest, 
                          client_ip: str) -> Tuple[User, TokenResponse]:
        """Register a new user"""
        try:
            # Check if user already exists
            existing_user = await self.get_user_by_email(registration_data.email)
            if existing_user:
                logger.warning(f"Registration attempt for existing email: {SecurityUtils.mask_email(registration_data.email)}")
                raise UserAlreadyExistsError("User with this email already exists")
            
            # Create user
            user_id = generate_user_id()
            password_hash = hash_password(registration_data.password)
            
            current_time = datetime.utcnow()
            user = User(
                user_id=user_id,
                email=registration_data.email,
                password_hash=password_hash,
                role=UserRole.USER,
                status=UserStatus.ACTIVE,
                created_at=current_time,
                updated_at=current_time,
                is_email_verified=False,  # TODO: Implement email verification
                metadata={
                    "registration_ip": client_ip,
                    "registration_timestamp": current_time.isoformat()
                }
            )
            
            # Store user in Redis
            store_success = await self._store_user(user)
            if not store_success:
                logger.error(f"Failed to store user in Redis: {SecurityUtils.mask_email(user.email)}")
                raise AuthError("Failed to create user account")
            
            # Create tokens
            access_token = create_access_token(user)
            refresh_token = create_refresh_token(user)
            
            # Create session
            await self._create_session(user, client_ip, access_token)
            
            # Check premium access
            premium_info = await self.redis_manager.check_premium_access(client_ip, user.email)
            
            # Create response
            token_response = TokenResponse(
                access_token=access_token,
                token_type="bearer",
                expires_in=TokenService.get_token_expiry_seconds(),
                refresh_token=refresh_token,
                user=user.to_response(
                    is_premium=premium_info.get("has_premium", False),
                    premium_expires_at=datetime.fromisoformat(premium_info["expires_at"]) if premium_info.get("expires_at") else None
                )
            )
            
            logger.info(f"User registered successfully: {SecurityUtils.mask_email(user.email)}")
            return user, token_response
            
        except UserAlreadyExistsError:
            raise
        except Exception as e:
            logger.error(f"Registration error: {e}")
            raise AuthError("Registration failed")
    
    async def login_user(self, login_data: UserLoginRequest, 
                        client_ip: str) -> TokenResponse:
        """Authenticate user and create session"""
        try:
            # Check for account lockout
            if await self._is_account_locked(login_data.email, client_ip):
                logger.warning(f"Login attempt on locked account: {SecurityUtils.mask_email(login_data.email)}")
                raise AccountSuspendedError("Account temporarily locked due to failed login attempts")
            
            # Get user
            user = await self.get_user_by_email(login_data.email)
            if not user:
                await self._record_failed_login(login_data.email, client_ip)
                logger.warning(f"Login attempt for non-existent user: {SecurityUtils.mask_email(login_data.email)}")
                raise InvalidCredentialsError("Invalid email or password")
            
            # Check user status
            if not user.is_active():
                logger.warning(f"Login attempt for inactive user: {SecurityUtils.mask_email(user.email)}")
                raise AccountSuspendedError("Account is suspended")
            
            # Verify password
            if not verify_password(login_data.password, user.password_hash):
                await self._record_failed_login(login_data.email, client_ip)
                await self._increment_failed_attempts(user)
                logger.warning(f"Invalid password for user: {SecurityUtils.mask_email(user.email)}")
                raise InvalidCredentialsError("Invalid email or password")
            
            # Reset failed attempts on successful login
            await self._reset_failed_attempts(user)
            await self._clear_failed_login_records(login_data.email, client_ip)
            
            # Update user login info
            user.last_login_at = datetime.utcnow()
            user.login_count += 1
            user.updated_at = datetime.utcnow()
            await self._store_user(user)
            
            # Create tokens with extended expiration if remember_me is True
            extended_delta = timedelta(days=30) if login_data.remember_me else None
            if login_data.remember_me:
                # Extended token expiration: 30 days for remember me
                access_token = create_access_token(user, extended_delta)
                refresh_token = create_refresh_token(user)  # Refresh token already has 30 days
            else:
                # Standard token expiration: 1 hour
                access_token = create_access_token(user)
                refresh_token = create_refresh_token(user)
            
            # Create session
            await self._create_session(user, client_ip, access_token)
            
            # Check premium access
            premium_info = await self.redis_manager.check_premium_access(client_ip, user.email)
            
            # Get usage stats
            usage_stats = await self.redis_manager.get_usage_count(client_ip, user.email)
            
            # Create response with correct expiration time
            expires_in = TokenService.get_token_expiry_seconds(extended_delta) if extended_delta else TokenService.get_token_expiry_seconds()
            token_response = TokenResponse(
                access_token=access_token,
                token_type="bearer",
                expires_in=expires_in,
                refresh_token=refresh_token,
                user=user.to_response(
                    is_premium=premium_info.get("has_premium", False),
                    premium_expires_at=datetime.fromisoformat(premium_info["expires_at"]) if premium_info.get("expires_at") else None,
                    usage_stats=usage_stats
                )
            )
            
            logger.info(f"User logged in successfully: {SecurityUtils.mask_email(user.email)}")
            return token_response
            
        except (InvalidCredentialsError, AccountSuspendedError):
            raise
        except Exception as e:
            logger.error(f"Login error: {e}")
            raise AuthError("Login failed")
    
    async def logout_user(self, access_token: str, user_id: str) -> bool:
        """Logout user and invalidate session"""
        try:
            # Remove session
            session_key = f"{self.session_prefix}{user_id}"
            
            def _logout():
                with self.redis_manager._redis_operation() as r:
                    if not r:
                        return False
                    try:
                        # Remove session
                        r.delete(session_key)
                        # TODO: Add token to blacklist
                        return True
                    except Exception as e:
                        logger.error(f"Error during logout: {e}")
                        return False
            
            # Run in thread pool
            import asyncio
            loop = asyncio.get_event_loop()
            success = await loop.run_in_executor(self.redis_manager.executor, _logout)
            
            if success:
                logger.info(f"User logged out successfully: {user_id}")
            return success
            
        except Exception as e:
            logger.error(f"Logout error: {e}")
            return False
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID from Redis"""
        user_key = f"{self.user_prefix}{user_id}"
        
        def _get():
            with self.redis_manager._redis_operation() as r:
                if not r:
                    return None
                try:
                    user_data = r.get(user_key)
                    if user_data:
                        data = json.loads(user_data)
                        return User(**data)
                    return None
                except Exception as e:
                    logger.error(f"Error retrieving user by ID {user_id}: {e}")
                    return None
        
        # Run in thread pool
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.redis_manager.executor, _get)
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email from Redis"""
        email = SecurityUtils.sanitize_email(email)
        email_index_key = f"{self.user_email_index}{email}"
        
        def _get():
            with self.redis_manager._redis_operation() as r:
                if not r:
                    return None
                try:
                    user_id = r.get(email_index_key)
                    if not user_id:
                        return None
                    
                    user_key = f"{self.user_prefix}{user_id}"
                    user_data = r.get(user_key)
                    if user_data:
                        data = json.loads(user_data)
                        return User(**data)
                    return None
                except Exception as e:
                    logger.error(f"Error retrieving user by email {SecurityUtils.mask_email(email)}: {e}")
                    return None
        
        # Run in thread pool
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.redis_manager.executor, _get)
    
    async def get_current_user_from_token(self, access_token: str) -> Optional[User]:
        """Get current user from access token"""
        try:
            # Verify token
            token_payload = TokenService.verify_token(access_token, "access")
            
            # Get user
            user = await self.get_user_by_id(token_payload.sub)
            if not user:
                logger.warning(f"Token valid but user not found: {token_payload.sub}")
                return None
            
            # Check if user is still active
            if not user.is_active():
                logger.warning(f"Token valid but user inactive: {SecurityUtils.mask_email(user.email)}")
                return None
            
            return user
            
        except Exception as e:
            logger.debug(f"Error getting user from token: {e}")
            return None
    
    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        """Refresh access token using refresh token"""
        try:
            # Verify refresh token
            token_payload = TokenService.verify_token(refresh_token, "refresh")
            
            # Get user
            user = await self.get_user_by_id(token_payload.sub)
            if not user or not user.is_active():
                logger.warning(f"Refresh token valid but user not found/inactive: {token_payload.sub}")
                raise InvalidCredentialsError("Invalid refresh token")
            
            # Create new tokens
            new_access_token = create_access_token(user)
            new_refresh_token = create_refresh_token(user)
            
            # Check premium access
            premium_info = await self.redis_manager.check_premium_access("refresh", user.email)
            
            # Create response
            token_response = TokenResponse(
                access_token=new_access_token,
                token_type="bearer",
                expires_in=TokenService.get_token_expiry_seconds(),
                refresh_token=new_refresh_token,
                user=user.to_response(
                    is_premium=premium_info.get("has_premium", False),
                    premium_expires_at=datetime.fromisoformat(premium_info["expires_at"]) if premium_info.get("expires_at") else None
                )
            )
            
            logger.info(f"Token refreshed for user: {SecurityUtils.mask_email(user.email)}")
            return token_response
            
        except Exception as e:
            logger.warning(f"Token refresh error: {e}")
            raise InvalidCredentialsError("Invalid refresh token")
    
    async def _store_user(self, user: User) -> bool:
        """Store user in Redis with email index"""
        user_key = f"{self.user_prefix}{user.user_id}"
        email_index_key = f"{self.user_email_index}{user.email}"
        
        def _store():
            with self.redis_manager._redis_operation() as r:
                if not r:
                    return False
                try:
                    pipe = r.pipeline()
                    
                    # Store user data (2 year expiry)
                    user_ttl = 2 * 365 * 24 * 3600
                    pipe.setex(user_key, user_ttl, user.model_dump_json())
                    
                    # Store email index
                    pipe.setex(email_index_key, user_ttl, user.user_id)
                    
                    results = pipe.execute()
                    return all(results)
                except Exception as e:
                    logger.error(f"Error storing user: {e}")
                    return False
        
        # Run in thread pool
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.redis_manager.executor, _store)
    
    async def _create_session(self, user: User, client_ip: str, access_token: str) -> bool:
        """Create user session in Redis"""
        session_key = f"{self.session_prefix}{user.user_id}"
        session_data = SecurityUtils.create_session_data(user, client_ip)
        session_data["access_token_hash"] = hash(access_token)  # Store token hash for validation
        
        def _create():
            with self.redis_manager._redis_operation() as r:
                if not r:
                    return False
                try:
                    # Session expires with access token + buffer
                    session_ttl = TokenService.get_token_expiry_seconds() + 300  # 5 min buffer
                    r.setex(session_key, session_ttl, json.dumps(session_data))
                    return True
                except Exception as e:
                    logger.error(f"Error creating session: {e}")
                    return False
        
        # Run in thread pool
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.redis_manager.executor, _create)
    
    async def _is_account_locked(self, email: str, client_ip: str) -> bool:
        """Check if account is locked due to failed attempts"""
        email = SecurityUtils.sanitize_email(email)
        failed_login_key = f"{self.failed_login_prefix}{email}:{client_ip}"
        
        def _check():
            with self.redis_manager._redis_operation() as r:
                if not r:
                    return False
                try:
                    attempts_data = r.get(failed_login_key)
                    if not attempts_data:
                        return False
                    
                    data = json.loads(attempts_data)
                    attempts = data.get("attempts", 0)
                    last_attempt = datetime.fromisoformat(data.get("last_attempt", ""))
                    
                    # Check if lockout period has expired
                    if datetime.utcnow() - last_attempt > self.account_lockout_duration:
                        # Clear expired lockout
                        r.delete(failed_login_key)
                        return False
                    
                    return attempts >= self.max_failed_attempts
                except Exception as e:
                    logger.error(f"Error checking account lock: {e}")
                    return False
        
        # Run in thread pool
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.redis_manager.executor, _check)
    
    async def _record_failed_login(self, email: str, client_ip: str) -> bool:
        """Record failed login attempt"""
        email = SecurityUtils.sanitize_email(email)
        failed_login_key = f"{self.failed_login_prefix}{email}:{client_ip}"
        
        def _record():
            with self.redis_manager._redis_operation() as r:
                if not r:
                    return False
                try:
                    # Get current attempts
                    attempts_data = r.get(failed_login_key)
                    if attempts_data:
                        data = json.loads(attempts_data)
                        attempts = data.get("attempts", 0) + 1
                    else:
                        attempts = 1
                    
                    # Store updated attempts
                    data = {
                        "attempts": attempts,
                        "last_attempt": datetime.utcnow().isoformat(),
                        "email": email,
                        "client_ip": client_ip
                    }
                    
                    # Expire after lockout duration + buffer
                    ttl = int(self.account_lockout_duration.total_seconds()) + 3600
                    r.setex(failed_login_key, ttl, json.dumps(data))
                    return True
                except Exception as e:
                    logger.error(f"Error recording failed login: {e}")
                    return False
        
        # Run in thread pool
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.redis_manager.executor, _record)
    
    async def _clear_failed_login_records(self, email: str, client_ip: str) -> bool:
        """Clear failed login records on successful login"""
        email = SecurityUtils.sanitize_email(email)
        failed_login_key = f"{self.failed_login_prefix}{email}:{client_ip}"
        
        def _clear():
            with self.redis_manager._redis_operation() as r:
                if not r:
                    return False
                try:
                    r.delete(failed_login_key)
                    return True
                except Exception as e:
                    logger.error(f"Error clearing failed login records: {e}")
                    return False
        
        # Run in thread pool
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.redis_manager.executor, _clear)
    
    async def _increment_failed_attempts(self, user: User) -> bool:
        """Increment user's failed login attempts"""
        user.failed_login_attempts += 1
        user.last_failed_login = datetime.utcnow()
        user.updated_at = datetime.utcnow()
        return await self._store_user(user)
    
    async def _reset_failed_attempts(self, user: User) -> bool:
        """Reset user's failed login attempts"""
        user.failed_login_attempts = 0
        user.last_failed_login = None
        user.updated_at = datetime.utcnow()
        return await self._store_user(user)