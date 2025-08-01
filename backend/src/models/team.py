"""
Team collaboration models for Threadr
Handles team structures, memberships, invites, and permissions
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Set
from pydantic import BaseModel, EmailStr, Field, field_validator
from enum import Enum
import uuid
import json


class TeamRole(str, Enum):
    """Team member roles with hierarchical permissions"""
    OWNER = "owner"       # Full access, billing, delete team
    ADMIN = "admin"       # User management, settings, all content
    EDITOR = "editor"     # Create/edit threads, limited settings
    VIEWER = "viewer"     # Read-only access


class TeamPlan(str, Enum):
    """Team subscription plans"""
    FREE = "free"         # 5 members, basic features
    STARTER = "starter"   # 15 members, advanced features
    PRO = "pro"          # 50 members, premium features
    ENTERPRISE = "enterprise"  # Unlimited, custom features


class InviteStatus(str, Enum):
    """Team invite status"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    EXPIRED = "expired"
    REVOKED = "revoked"


class ThreadStatus(str, Enum):
    """Thread workflow status"""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    PUBLISHED = "published"


# Core Models
class Team(BaseModel):
    """Team/workspace model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=3, max_length=50, pattern="^[a-z0-9-]+$")
    description: Optional[str] = Field(None, max_length=500)
    
    # Owner and billing
    owner_id: str
    plan: TeamPlan = TeamPlan.FREE
    billing_email: Optional[EmailStr] = None
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None
    
    # Settings
    settings: Dict[str, Any] = Field(default_factory=dict)
    features: Dict[str, bool] = Field(default_factory=dict)
    
    # Limits based on plan
    max_members: int = Field(default=5)
    max_monthly_threads: int = Field(default=100)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Status
    is_active: bool = Field(default=True)
    suspended_at: Optional[datetime] = None
    suspended_reason: Optional[str] = None
    
    @field_validator('slug')
    @classmethod
    def validate_slug(cls, v):
        """Validate team slug"""
        if not v or len(v) < 3:
            raise ValueError('Slug must be at least 3 characters')
        if not v.replace('-', '').isalnum():
            raise ValueError('Slug can only contain letters, numbers, and hyphens')
        return v.lower()
    
    def get_plan_limits(self) -> Dict[str, int]:
        """Get limits based on current plan"""
        limits = {
            TeamPlan.FREE: {"max_members": 5, "max_monthly_threads": 100},
            TeamPlan.STARTER: {"max_members": 15, "max_monthly_threads": 500},
            TeamPlan.PRO: {"max_members": 50, "max_monthly_threads": 2000},
            TeamPlan.ENTERPRISE: {"max_members": 1000, "max_monthly_threads": 10000}
        }
        return limits.get(self.plan, limits[TeamPlan.FREE])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "description": self.description,
            "plan": self.plan,
            "max_members": self.max_members,
            "max_monthly_threads": self.max_monthly_threads,
            "created_at": self.created_at.isoformat(),
            "is_active": self.is_active,
            "features": self.features
        }


class TeamMembership(BaseModel):
    """Team membership relationship"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    team_id: str
    user_id: str
    role: TeamRole
    
    # Permissions (granular control beyond role)
    permissions: Set[str] = Field(default_factory=set)
    
    # Status
    is_active: bool = Field(default=True)
    joined_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Activity tracking
    last_activity_at: Optional[datetime] = None
    thread_count: int = Field(default=0)
    
    def has_permission(self, permission: str) -> bool:
        """Check if membership has specific permission"""
        role_permissions = {
            TeamRole.OWNER: {
                "team.delete", "team.billing", "team.settings", 
                "members.invite", "members.remove", "members.manage",
                "threads.create", "threads.edit", "threads.delete", "threads.approve",
                "analytics.view"
            },
            TeamRole.ADMIN: {
                "team.settings", "members.invite", "members.remove",
                "threads.create", "threads.edit", "threads.delete", "threads.approve",
                "analytics.view"
            },
            TeamRole.EDITOR: {
                "threads.create", "threads.edit", "threads.submit",
                "analytics.view_own"
            },
            TeamRole.VIEWER: {
                "threads.view", "analytics.view_summary"
            }
        }
        
        base_permissions = role_permissions.get(self.role, set())
        return permission in base_permissions or permission in self.permissions


class TeamInvite(BaseModel):
    """Team invitation model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    team_id: str
    invited_by_user_id: str
    
    # Invitee info
    email: EmailStr
    role: TeamRole
    
    # Invite details
    token: str = Field(default_factory=lambda: str(uuid.uuid4()))
    message: Optional[str] = Field(None, max_length=500)
    
    # Status and timestamps
    status: InviteStatus = InviteStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime = Field(default_factory=lambda: datetime.utcnow() + timedelta(days=7))
    accepted_at: Optional[datetime] = None
    revoked_at: Optional[datetime] = None
    
    def is_valid(self) -> bool:
        """Check if invite is still valid"""
        return (
            self.status == InviteStatus.PENDING and
            datetime.utcnow() < self.expires_at
        )
    
    def expire(self) -> None:
        """Mark invite as expired"""
        self.status = InviteStatus.EXPIRED
    
    def revoke(self) -> None:
        """Revoke the invite"""
        self.status = InviteStatus.REVOKED
        self.revoked_at = datetime.utcnow()


class TeamThread(BaseModel):
    """Extended thread model for team collaboration"""
    # Base thread info (extends existing SavedThread)
    thread_id: str
    team_id: str
    
    # Collaboration fields
    author_id: str
    assigned_to_id: Optional[str] = None  # For workflow assignment
    status: ThreadStatus = ThreadStatus.DRAFT
    
    # Approval workflow
    submitted_at: Optional[datetime] = None
    submitted_by_id: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    reviewed_by_id: Optional[str] = None
    review_notes: Optional[str] = None
    
    # Collaboration metadata
    collaborators: List[str] = Field(default_factory=list)  # User IDs
    mentions: List[str] = Field(default_factory=list)      # User IDs mentioned
    
    # Version control (basic)
    version: int = Field(default=1)
    parent_version_id: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class TeamActivity(BaseModel):
    """Team activity/audit log"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    team_id: str
    user_id: str
    
    # Activity details
    action: str  # "thread.created", "member.invited", etc.
    resource_type: str  # "thread", "member", "team"
    resource_id: Optional[str] = None
    
    # Context
    details: Dict[str, Any] = Field(default_factory=dict)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    # Timestamp
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# API Request/Response Models
class CreateTeamRequest(BaseModel):
    """Request to create a new team"""
    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=3, max_length=50, pattern="^[a-z0-9-]+$")
    description: Optional[str] = Field(None, max_length=500)
    plan: TeamPlan = TeamPlan.FREE


class UpdateTeamRequest(BaseModel):
    """Request to update team details"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    settings: Optional[Dict[str, Any]] = None


class InviteMemberRequest(BaseModel):
    """Request to invite a team member"""
    email: EmailStr
    role: TeamRole
    message: Optional[str] = Field(None, max_length=500)


class UpdateMemberRequest(BaseModel):
    """Request to update member role/permissions"""
    role: Optional[TeamRole] = None
    permissions: Optional[List[str]] = None


class AcceptInviteRequest(BaseModel):
    """Request to accept team invite"""
    token: str


class TeamResponse(BaseModel):
    """Team response for API"""
    id: str
    name: str
    slug: str
    description: Optional[str]
    plan: TeamPlan
    member_count: int
    max_members: int
    owner_id: str
    created_at: datetime
    current_user_role: Optional[TeamRole] = None


class MemberResponse(BaseModel):
    """Team member response for API"""
    user_id: str
    email: str
    role: TeamRole
    joined_at: datetime
    last_activity_at: Optional[datetime]
    thread_count: int
    is_active: bool


class InviteResponse(BaseModel):
    """Team invite response for API"""
    id: str
    email: str
    role: TeamRole
    status: InviteStatus
    created_at: datetime
    expires_at: datetime
    invited_by: str  # Email of inviter


class TeamStatsResponse(BaseModel):
    """Team statistics response"""
    member_count: int
    active_members: int
    total_threads: int
    threads_this_month: int
    monthly_limit: int
    plan_usage_percent: float


# Exception Classes
class TeamError(Exception):
    """Base team error"""
    pass


class TeamNotFoundError(TeamError):
    """Team not found"""
    pass


class TeamAccessDeniedError(TeamError):
    """Access denied to team"""
    pass


class TeamLimitExceededError(TeamError):
    """Team limit exceeded"""
    pass


class InviteError(TeamError):
    """Invite related error"""
    pass


class InviteNotFoundError(InviteError):
    """Invite not found"""
    pass


class InviteExpiredError(InviteError):
    """Invite expired"""
    pass