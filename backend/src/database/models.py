"""
SQLAlchemy models for Threadr PostgreSQL database.
Production-ready with proper relationships, indexes, and constraints.
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text, 
    ForeignKey, Index, CheckConstraint, UniqueConstraint, JSON,
    event, func
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship, validates
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.mutable import MutableDict
from passlib.context import CryptContext

from .config import Base

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Helper function for UUID generation
def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    """User model for authentication and profile management."""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=True, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # Profile information
    full_name = Column(String(255), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    
    # Account status
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_premium = Column(Boolean, default=False, nullable=False)
    premium_expires_at = Column(DateTime, nullable=True)
    
    # OAuth fields
    google_id = Column(String(255), unique=True, nullable=True)
    twitter_id = Column(String(255), unique=True, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = Column(DateTime, nullable=True)
    
    # Relationships
    threads = relationship("Thread", back_populates="user", cascade="all, delete-orphan")
    team_memberships = relationship("TeamMembership", back_populates="user", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
    usage_tracking = relationship("UsageTracking", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    thread_analytics = relationship("ThreadAnalytics", back_populates="user")
    
    # Indexes
    __table_args__ = (
        Index('idx_users_email_active', 'email', 'is_active'),
        Index('idx_users_premium_expires', 'is_premium', 'premium_expires_at'),
    )
    
    def set_password(self, password: str):
        """Hash and set user password."""
        self.password_hash = pwd_context.hash(password)
    
    def check_password(self, password: str) -> bool:
        """Check if provided password matches hash."""
        return pwd_context.verify(password, self.password_hash)
    
    @hybrid_property
    def is_premium_active(self) -> bool:
        """Check if premium subscription is currently active."""
        if not self.is_premium:
            return False
        if not self.premium_expires_at:
            return True
        return self.premium_expires_at > datetime.utcnow()

class Team(Base):
    """Team model for collaborative workspaces."""
    __tablename__ = "teams"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Team settings
    logo_url = Column(String(500), nullable=True)
    website_url = Column(String(500), nullable=True)
    max_members = Column(Integer, default=5, nullable=False)
    
    # Billing
    is_active = Column(Boolean, default=True, nullable=False)
    subscription_tier = Column(String(50), default='free', nullable=False)
    billing_email = Column(String(255), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    memberships = relationship("TeamMembership", back_populates="team", cascade="all, delete-orphan")
    invites = relationship("TeamInvite", back_populates="team", cascade="all, delete-orphan")
    activities = relationship("TeamActivity", back_populates="team", cascade="all, delete-orphan")
    
    __table_args__ = (
        CheckConstraint('max_members >= 1', name='check_max_members_positive'),
    )

class TeamMembership(Base):
    """Team membership model for user-team relationships."""
    __tablename__ = "team_memberships"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    team_id = Column(UUID(as_uuid=True), ForeignKey('teams.id'), nullable=False)
    
    role = Column(String(50), default='member', nullable=False)
    permissions = Column(JSONB, default={}, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    joined_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    left_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="team_memberships")
    team = relationship("Team", back_populates="memberships")
    
    __table_args__ = (
        UniqueConstraint('user_id', 'team_id', name='unique_user_team'),
        Index('idx_team_memberships_active', 'team_id', 'is_active'),
        CheckConstraint("role IN ('owner', 'admin', 'member', 'viewer')", name='check_valid_role'),
    )

class TeamInvite(Base):
    """Team invitation model."""
    __tablename__ = "team_invites"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    team_id = Column(UUID(as_uuid=True), ForeignKey('teams.id'), nullable=False)
    
    email = Column(String(255), nullable=False)
    role = Column(String(50), default='member', nullable=False)
    token = Column(String(255), unique=True, nullable=False, index=True)
    
    # Status
    status = Column(String(50), default='pending', nullable=False)
    invited_by_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    accepted_by_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    accepted_at = Column(DateTime, nullable=True)
    
    # Relationships
    team = relationship("Team", back_populates="invites")
    
    __table_args__ = (
        Index('idx_invites_status_expires', 'status', 'expires_at'),
        CheckConstraint("status IN ('pending', 'accepted', 'expired', 'cancelled')", name='check_invite_status'),
    )

class Thread(Base):
    """Thread model for storing generated Twitter threads."""
    __tablename__ = "threads"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    
    # Thread content
    title = Column(String(500), nullable=True)
    source_url = Column(String(1000), nullable=True)
    source_content = Column(Text, nullable=True)
    tweets = Column(JSONB, nullable=False)  # Array of tweet objects
    tweet_count = Column(Integer, nullable=False)
    
    # Metadata
    template_id = Column(String(100), nullable=True)
    status = Column(String(50), default='draft', nullable=False)
    is_published = Column(Boolean, default=False, nullable=False)
    published_at = Column(DateTime, nullable=True)
    twitter_thread_id = Column(String(255), nullable=True)
    
    # Analytics
    view_count = Column(Integer, default=0, nullable=False)
    share_count = Column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="threads")
    analytics = relationship("ThreadAnalytics", back_populates="thread", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_threads_user_created', 'user_id', 'created_at'),
        Index('idx_threads_status', 'status', 'is_published'),
        CheckConstraint("status IN ('draft', 'published', 'scheduled', 'archived')", name='check_thread_status'),
    )

class Subscription(Base):
    """Subscription model for Stripe integration."""
    __tablename__ = "subscriptions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    
    # Stripe data
    stripe_customer_id = Column(String(255), unique=True, nullable=False, index=True)
    stripe_subscription_id = Column(String(255), unique=True, nullable=True, index=True)
    stripe_payment_method_id = Column(String(255), nullable=True)
    
    # Subscription details
    plan_id = Column(String(100), nullable=False)
    status = Column(String(50), nullable=False)
    current_period_start = Column(DateTime, nullable=False)
    current_period_end = Column(DateTime, nullable=False)
    
    # Billing
    amount_cents = Column(Integer, nullable=False)
    currency = Column(String(3), default='USD', nullable=False)
    interval = Column(String(20), nullable=False)  # monthly, yearly
    
    # Flags
    cancel_at_period_end = Column(Boolean, default=False, nullable=False)
    is_trial = Column(Boolean, default=False, nullable=False)
    trial_ends_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    cancelled_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="subscriptions")
    
    __table_args__ = (
        Index('idx_subscriptions_status', 'status', 'current_period_end'),
        CheckConstraint("status IN ('active', 'cancelled', 'past_due', 'unpaid', 'trialing')", name='check_subscription_status'),
    )

class UsageTracking(Base):
    """Usage tracking model for rate limiting and analytics."""
    __tablename__ = "usage_tracking"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    
    # Period tracking
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    period_type = Column(String(20), nullable=False)  # daily, monthly
    
    # Usage counts
    threads_generated = Column(Integer, default=0, nullable=False)
    tweets_generated = Column(Integer, default=0, nullable=False)
    api_calls = Column(Integer, default=0, nullable=False)
    
    # Limits
    thread_limit = Column(Integer, nullable=False)
    exceeded_limit = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="usage_tracking")
    
    __table_args__ = (
        UniqueConstraint('user_id', 'period_start', 'period_type', name='unique_user_period'),
        Index('idx_usage_period', 'period_type', 'period_start', 'period_end'),
    )

class UserSession(Base):
    """User session model for JWT token management."""
    __tablename__ = "user_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    
    # Token data
    access_token_hash = Column(String(255), unique=True, nullable=False, index=True)
    refresh_token_hash = Column(String(255), unique=True, nullable=True, index=True)
    
    # Session info
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    device_info = Column(JSONB, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    last_activity = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    revoked_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    
    __table_args__ = (
        Index('idx_sessions_active', 'user_id', 'is_active', 'expires_at'),
    )

class ThreadAnalytics(Base):
    """Thread analytics model for performance tracking."""
    __tablename__ = "thread_analytics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    thread_id = Column(UUID(as_uuid=True), ForeignKey('threads.id'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    
    # Engagement metrics
    impressions = Column(Integer, default=0, nullable=False)
    engagements = Column(Integer, default=0, nullable=False)
    likes = Column(Integer, default=0, nullable=False)
    retweets = Column(Integer, default=0, nullable=False)
    replies = Column(Integer, default=0, nullable=False)
    
    # Calculated metrics
    engagement_rate = Column(Float, default=0.0, nullable=False)
    viral_score = Column(Float, default=0.0, nullable=False)
    
    # Timestamps
    calculated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    thread = relationship("Thread", back_populates="analytics")
    user = relationship("User", back_populates="thread_analytics")
    
    __table_args__ = (
        UniqueConstraint('thread_id', 'calculated_at', name='unique_thread_analytics_period'),
        Index('idx_analytics_calculated', 'calculated_at', 'engagement_rate'),
    )

class AnalyticsTimeseries(Base):
    """Time-series data for analytics charts."""
    __tablename__ = "analytics_timeseries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    
    # Time bucket
    timestamp = Column(DateTime, nullable=False, index=True)
    granularity = Column(String(20), nullable=False)  # hourly, daily, weekly, monthly
    
    # Metrics
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Float, nullable=False)
    metric_metadata = Column(JSONB, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        UniqueConstraint('user_id', 'timestamp', 'granularity', 'metric_name', name='unique_timeseries_point'),
        Index('idx_timeseries_query', 'user_id', 'metric_name', 'timestamp'),
    )

class TeamActivity(Base):
    """Team activity log for audit trail."""
    __tablename__ = "team_activities"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    team_id = Column(UUID(as_uuid=True), ForeignKey('teams.id'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    
    # Activity details
    action = Column(String(100), nullable=False)
    entity_type = Column(String(50), nullable=True)
    entity_id = Column(String(255), nullable=True)
    activity_data = Column(JSONB, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    team = relationship("Team", back_populates="activities")
    
    __table_args__ = (
        Index('idx_team_activities', 'team_id', 'created_at'),
    )