"""
Fixed Authentication service for Threadr
Handles Redis unavailability properly and successfully stores users in PostgreSQL
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
import logging
import uuid

# Import auth models
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

# Import auth utilities
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

# Database imports
try:
    from ...database import get_async_db, User as DBUser
    POSTGRES_AVAILABLE = True
except ImportError:
    try:
        from src.database import get_async_db, User as DBUser
        POSTGRES_AVAILABLE = True
    except ImportError:
        get_async_db = None
        DBUser = None
        POSTGRES_AVAILABLE = False

# SQLAlchemy imports
try:
    from sqlalchemy import select, text
    from sqlalchemy.exc import IntegrityError
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False

logger = logging.getLogger(__name__)


class AuthServiceFixed:
    """Fixed authentication service with proper Redis/PostgreSQL handling"""
    
    def __init__(self, redis_manager=None):
        """Initialize auth service"""
        self.redis_manager = redis_manager
        self.user_prefix = "threadr:user:"
        self.user_email_index = "threadr:user:email:"
        self.session_prefix = "threadr:session:"
        
        # Check Redis availability properly
        self._redis_available = self._check_redis_availability()
        
        # Log initialization status
        logger.info(f"AuthServiceFixed initialized - Redis available: {self._redis_available}, PostgreSQL available: {POSTGRES_AVAILABLE}")
    
    def _check_redis_availability(self) -> bool:
        """Properly check if Redis is actually available and functional"""
        if not self.redis_manager:
            logger.debug("No Redis manager provided")
            return False
        
        # Check if the manager claims to be available
        if not getattr(self.redis_manager, 'is_available', False):
            logger.debug("Redis manager reports not available")
            return False
        
        # Try an actual operation to verify functionality
        try:
            with self.redis_manager._redis_operation() as r:
                if not r:
                    logger.debug("Redis operation context returned None")
                    return False
                # Try a simple ping
                r.ping()
                logger.debug("Redis ping successful")
                return True
        except Exception as e:
            logger.debug(f"Redis functionality test failed: {e}")
            return False
    
    async def register_user(self, registration_data: UserRegistrationRequest, 
                          client_ip: str) -> Tuple[User, TokenResponse]:
        """Register a new user with fixed storage logic"""
        try:
            logger.info(f"Starting user registration for: {SecurityUtils.mask_email(registration_data.email)}")
            
            # Check if user already exists
            existing_user = await self._get_user_by_email(registration_data.email)
            if existing_user:
                logger.warning(f"Registration attempt for existing email: {SecurityUtils.mask_email(registration_data.email)}")
                raise UserAlreadyExistsError("User with this email already exists")
            
            # Create user object
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
                is_email_verified=False,
                metadata={
                    "registration_ip": client_ip,
                    "registration_timestamp": current_time.isoformat()
                }
            )
            
            # Store user using fixed logic
            logger.info(f"Attempting to store user: {SecurityUtils.mask_email(user.email)}")
            success = await self._store_user_fixed(user)
            
            if not success:
                logger.error(f"Failed to store user: {SecurityUtils.mask_email(user.email)}")
                raise AuthError("Failed to create user account")
            
            logger.info(f"User stored successfully: {SecurityUtils.mask_email(user.email)}")
            
            # Create tokens
            access_token = create_access_token(user)
            refresh_token = create_refresh_token(user)
            
            # Create session (optional, don't fail if Redis unavailable)
            await self._create_session_optional(user, client_ip, access_token)
            
            # Get premium info (graceful fallback)
            premium_info = await self._get_premium_info_safe(client_ip, user.email)
            
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
            
            logger.info(f"User registration completed successfully: {SecurityUtils.mask_email(user.email)}")
            return user, token_response
            
        except UserAlreadyExistsError:
            raise
        except Exception as e:
            logger.error(f"Registration error - Type: {type(e).__name__}, Message: {e}")
            import traceback
            logger.error(f"Registration error full traceback: {traceback.format_exc()}")
            raise AuthError(f"Registration failed: {type(e).__name__}: {str(e)}")
    
    async def login_user(self, login_data: UserLoginRequest, 
                        client_ip: str) -> TokenResponse:
        """Login user with fixed logic"""
        try:
            # Get user
            user = await self._get_user_by_email(login_data.email)
            if not user:
                logger.warning(f"Login attempt for non-existent user: {SecurityUtils.mask_email(login_data.email)}")
                raise InvalidCredentialsError("Invalid email or password")
            
            # Check user status
            if not user.is_active():
                logger.warning(f"Login attempt for inactive user: {SecurityUtils.mask_email(user.email)}")
                raise AccountSuspendedError("Account is suspended")
            
            # Verify password
            if not verify_password(login_data.password, user.password_hash):
                logger.warning(f"Invalid password for user: {SecurityUtils.mask_email(user.email)}")
                raise InvalidCredentialsError("Invalid email or password")
            
            # Update user login info
            user.last_login_at = datetime.utcnow()
            user.login_count += 1
            user.updated_at = datetime.utcnow()
            user.failed_login_attempts = 0  # Reset on successful login
            await self._store_user_fixed(user)
            
            # Create tokens
            extended_delta = timedelta(days=30) if login_data.remember_me else None
            access_token = create_access_token(user, extended_delta)
            refresh_token = create_refresh_token(user)
            
            # Create session (optional)
            await self._create_session_optional(user, client_ip, access_token)
            
            # Get premium and usage info (graceful fallback)
            premium_info = await self._get_premium_info_safe(client_ip, user.email)
            usage_stats = await self._get_usage_stats_safe(client_ip, user.email)
            
            # Create response
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
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID with fixed storage logic"""
        return await self._get_user_by_id_fixed(user_id)
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email with fixed storage logic"""
        return await self._get_user_by_email(email)
    
    async def get_current_user_from_token(self, access_token: str) -> Optional[User]:
        """Get current user from access token"""
        try:
            # Verify token
            token_payload = TokenService.verify_token(access_token, "access")
            
            # Get user
            user = await self._get_user_by_id_fixed(token_payload.sub)
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
            user = await self._get_user_by_id_fixed(token_payload.sub)
            if not user or not user.is_active():
                logger.warning(f"Refresh token valid but user not found/inactive: {token_payload.sub}")
                raise InvalidCredentialsError("Invalid refresh token")
            
            # Create new tokens
            new_access_token = create_access_token(user)
            new_refresh_token = create_refresh_token(user)
            
            # Get premium info
            premium_info = await self._get_premium_info_safe("refresh", user.email)
            
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
    
    # Fixed storage methods
    
    async def _store_user_fixed(self, user: User) -> bool:
        """Fixed user storage logic with proper PostgreSQL handling"""
        logger.info(f"_store_user_fixed called for: {SecurityUtils.mask_email(user.email)}")
        
        # If Redis is available and functional, use it
        if self._redis_available:
            logger.info(f"Redis is available, attempting Redis storage for: {SecurityUtils.mask_email(user.email)}")
            redis_success = await self._store_user_redis_simple(user)
            if redis_success:
                logger.info(f"Redis storage successful for: {SecurityUtils.mask_email(user.email)}")
                return True
            else:
                logger.warning(f"Redis storage failed for: {SecurityUtils.mask_email(user.email)}")
        
        # Use PostgreSQL (primary or fallback)
        if POSTGRES_AVAILABLE and SQLALCHEMY_AVAILABLE:
            logger.info(f"Attempting PostgreSQL storage for: {SecurityUtils.mask_email(user.email)}")
            postgres_success = await self._store_user_postgres_fixed(user)
            if postgres_success:
                logger.info(f"PostgreSQL storage successful for: {SecurityUtils.mask_email(user.email)}")
                return True
            else:
                logger.error(f"PostgreSQL storage failed for: {SecurityUtils.mask_email(user.email)}")
        else:
            logger.error("PostgreSQL not available - no storage method available")
        
        return False
    
    async def _store_user_redis_simple(self, user: User) -> bool:
        """Simplified Redis storage without complex operations"""
        try:
            with self.redis_manager._redis_operation() as r:
                if not r:
                    return False
                
                user_key = f"{self.user_prefix}{user.user_id}"
                email_index_key = f"{self.user_email_index}{user.email}"
                user_json = user.model_dump_json()
                
                # Simple set operations
                ttl = 365 * 24 * 3600  # 1 year
                r.set(user_key, user_json, ex=ttl)
                r.set(email_index_key, user.user_id, ex=ttl)
                
                return True
                
        except Exception as e:
            logger.error(f"Redis storage error: {e}")
            return False
    
    async def _store_user_postgres_fixed(self, user: User) -> bool:
        """Fixed PostgreSQL storage with proper model handling"""
        try:
            async for db_session in get_async_db():
                try:
                    # Check if user already exists
                    stmt = select(DBUser).where(DBUser.email == user.email)
                    result = await db_session.execute(stmt)
                    existing_user = result.scalar_one_or_none()
                    
                    if existing_user:
                        # Update existing user
                        existing_user.password_hash = user.password_hash
                        existing_user.is_active = (user.status == UserStatus.ACTIVE)
                        existing_user.is_verified = user.is_email_verified
                        existing_user.is_premium = (user.role == UserRole.PREMIUM)
                        existing_user.updated_at = user.updated_at
                        existing_user.last_login_at = user.last_login_at
                        if hasattr(existing_user, 'metadata'):
                            existing_user.metadata = user.metadata or {}
                        
                        logger.info(f"Updated existing user in PostgreSQL: {SecurityUtils.mask_email(user.email)}")
                    else:
                        # Create new user
                        user_uuid = user.user_id if isinstance(user.user_id, uuid.UUID) else uuid.UUID(user.user_id)
                        
                        db_user = DBUser(
                            id=user_uuid,
                            email=user.email,
                            username=None,  # Optional field
                            password_hash=user.password_hash,
                            is_active=(user.status == UserStatus.ACTIVE),
                            is_verified=user.is_email_verified,
                            is_premium=(user.role == UserRole.PREMIUM),
                            created_at=user.created_at,
                            updated_at=user.updated_at,
                            last_login_at=user.last_login_at
                        )
                        
                        # Add metadata if supported by model
                        if hasattr(db_user, 'metadata'):
                            db_user.metadata = user.metadata or {}
                        
                        db_session.add(db_user)
                        logger.info(f"Created new user in PostgreSQL: {SecurityUtils.mask_email(user.email)}")
                    
                    await db_session.commit()
                    return True
                    
                except IntegrityError as e:
                    await db_session.rollback()
                    if "unique constraint" in str(e).lower():
                        logger.warning(f"User already exists in PostgreSQL: {SecurityUtils.mask_email(user.email)}")
                        return True  # User exists, consider it success
                    else:
                        logger.error(f"PostgreSQL integrity error: {e}")
                        return False
                except Exception as e:
                    await db_session.rollback()
                    logger.error(f"PostgreSQL storage error: {e}")
                    return False
                finally:
                    await db_session.close()
                    
        except Exception as e:
            logger.error(f"PostgreSQL connection error: {e}")
            return False
    
    async def _get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email with fixed storage logic"""
        email = SecurityUtils.sanitize_email(email)
        
        # Try Redis first if available
        if self._redis_available:
            redis_user = await self._get_user_by_email_redis(email)
            if redis_user:
                return redis_user
        
        # Try PostgreSQL
        return await self._get_user_by_email_postgres_fixed(email)
    
    async def _get_user_by_id_fixed(self, user_id: str) -> Optional[User]:
        """Get user by ID with fixed storage logic"""
        # Try Redis first if available
        if self._redis_available:
            redis_user = await self._get_user_by_id_redis(user_id)
            if redis_user:
                return redis_user
        
        # Try PostgreSQL
        return await self._get_user_by_id_postgres_fixed(user_id)
    
    async def _get_user_by_email_redis(self, email: str) -> Optional[User]:
        """Get user from Redis by email"""
        try:
            with self.redis_manager._redis_operation() as r:
                if not r:
                    return None
                
                email_index_key = f"{self.user_email_index}{email}"
                user_id = r.get(email_index_key)
                if not user_id:
                    return None
                
                user_key = f"{self.user_prefix}{user_id}"
                user_data = r.get(user_key)
                if user_data:
                    import json
                    data = json.loads(user_data)
                    return User(**data)
                return None
                
        except Exception as e:
            logger.error(f"Redis user lookup error: {e}")
            return None
    
    async def _get_user_by_id_redis(self, user_id: str) -> Optional[User]:
        """Get user from Redis by ID"""
        try:
            with self.redis_manager._redis_operation() as r:
                if not r:
                    return None
                
                user_key = f"{self.user_prefix}{user_id}"
                user_data = r.get(user_key)
                if user_data:
                    import json
                    data = json.loads(user_data)
                    return User(**data)
                return None
                
        except Exception as e:
            logger.error(f"Redis user lookup error: {e}")
            return None
    
    async def _get_user_by_email_postgres_fixed(self, email: str) -> Optional[User]:
        """Get user from PostgreSQL by email with fixed model conversion"""
        if not POSTGRES_AVAILABLE or not SQLALCHEMY_AVAILABLE:
            return None
        
        try:
            async for db_session in get_async_db():
                try:
                    stmt = select(DBUser).where(DBUser.email == email)
                    result = await db_session.execute(stmt)
                    db_user = result.scalar_one_or_none()
                    
                    if not db_user:
                        return None
                    
                    # Convert to our User model
                    user = User(
                        user_id=str(db_user.id),
                        email=db_user.email,
                        password_hash=db_user.password_hash,
                        role=UserRole.PREMIUM if getattr(db_user, 'is_premium', False) else UserRole.USER,
                        status=UserStatus.ACTIVE if getattr(db_user, 'is_active', True) else UserStatus.SUSPENDED,
                        created_at=db_user.created_at,
                        updated_at=db_user.updated_at or db_user.created_at,
                        last_login_at=db_user.last_login_at,
                        is_email_verified=getattr(db_user, 'is_verified', False),
                        metadata=getattr(db_user, 'metadata', {}) or {}
                    )
                    
                    return user
                    
                except Exception as e:
                    logger.error(f"PostgreSQL user lookup error: {e}")
                    return None
                finally:
                    await db_session.close()
                    
        except Exception as e:
            logger.error(f"PostgreSQL connection error: {e}")
            return None
    
    async def _get_user_by_id_postgres_fixed(self, user_id: str) -> Optional[User]:
        """Get user from PostgreSQL by ID with fixed model conversion"""
        if not POSTGRES_AVAILABLE or not SQLALCHEMY_AVAILABLE:
            return None
        
        try:
            # Convert string to UUID
            user_uuid = user_id if isinstance(user_id, uuid.UUID) else uuid.UUID(user_id)
            
            async for db_session in get_async_db():
                try:
                    stmt = select(DBUser).where(DBUser.id == user_uuid)
                    result = await db_session.execute(stmt)
                    db_user = result.scalar_one_or_none()
                    
                    if not db_user:
                        return None
                    
                    # Convert to our User model
                    user = User(
                        user_id=str(db_user.id),
                        email=db_user.email,
                        password_hash=db_user.password_hash,
                        role=UserRole.PREMIUM if getattr(db_user, 'is_premium', False) else UserRole.USER,
                        status=UserStatus.ACTIVE if getattr(db_user, 'is_active', True) else UserStatus.SUSPENDED,
                        created_at=db_user.created_at,
                        updated_at=db_user.updated_at or db_user.created_at,
                        last_login_at=db_user.last_login_at,
                        is_email_verified=getattr(db_user, 'is_verified', False),
                        metadata=getattr(db_user, 'metadata', {}) or {}
                    )
                    
                    return user
                    
                except Exception as e:
                    logger.error(f"PostgreSQL user lookup error: {e}")
                    return None
                finally:
                    await db_session.close()
                    
        except (ValueError, TypeError) as e:
            logger.error(f"Invalid user ID format: {user_id} - {e}")
            return None
        except Exception as e:
            logger.error(f"PostgreSQL connection error: {e}")
            return None
    
    # Helper methods
    
    async def _create_session_optional(self, user: User, client_ip: str, access_token: str) -> bool:
        """Create session if Redis is available, don't fail if not"""
        if not self._redis_available:
            logger.debug(f"Redis unavailable, skipping session creation for: {SecurityUtils.mask_email(user.email)}")
            return True
        
        try:
            session_key = f"{self.session_prefix}{user.user_id}"
            session_data = SecurityUtils.create_session_data(user, client_ip)
            session_data["access_token_hash"] = hash(access_token)
            
            with self.redis_manager._redis_operation() as r:
                if not r:
                    return True
                
                session_ttl = TokenService.get_token_expiry_seconds() + 300  # 5 min buffer
                import json
                r.setex(session_key, session_ttl, json.dumps(session_data))
                return True
                
        except Exception as e:
            logger.warning(f"Session creation failed: {e}")
            return True  # Don't fail auth if sessions fail
    
    async def _get_premium_info_safe(self, client_ip: str, email: str) -> Dict[str, Any]:
        """Get premium info with safe fallback"""
        if self._redis_available and self.redis_manager:
            try:
                return await self.redis_manager.check_premium_access(client_ip, email)
            except Exception as e:
                logger.debug(f"Premium info lookup failed: {e}")
        
        return {"has_premium": False, "expires_at": None}
    
    async def _get_usage_stats_safe(self, client_ip: str, email: str) -> Dict[str, Any]:
        """Get usage stats with safe fallback"""
        if self._redis_available and self.redis_manager:
            try:
                return await self.redis_manager.get_usage_count(client_ip, email)
            except Exception as e:
                logger.debug(f"Usage stats lookup failed: {e}")
        
        return {"daily_count": 0, "monthly_count": 0}
    
    async def test_storage_components_fixed(self) -> dict:
        """Test storage components with fixed logic"""
        results = {
            "redis_manager": bool(self.redis_manager),
            "redis_available": self._redis_available,
            "redis_functional": False,
            "postgres_available": POSTGRES_AVAILABLE,
            "postgres_functional": False,
            "sqlalchemy_available": SQLALCHEMY_AVAILABLE
        }
        
        # Test Redis functionality
        if self._redis_available:
            try:
                with self.redis_manager._redis_operation() as r:
                    if r:
                        r.ping()
                        results["redis_functional"] = True
            except Exception as e:
                results["redis_error"] = str(e)
        
        # Test PostgreSQL functionality
        if POSTGRES_AVAILABLE and SQLALCHEMY_AVAILABLE:
            try:
                async for db_session in get_async_db():
                    try:
                        await db_session.execute(text("SELECT 1"))
                        results["postgres_functional"] = True
                    except Exception as e:
                        results["postgres_error"] = str(e)
                    finally:
                        await db_session.close()
                        break
            except Exception as e:
                results["postgres_connection_error"] = str(e)
        
        return results