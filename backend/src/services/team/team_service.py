"""
Team service for Threadr
Handles team operations, membership management, and permissions
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
import json
import uuid
from email_validator import validate_email

# Import models
try:
    from ...models.team import (
        Team, TeamMembership, TeamInvite, TeamActivity, TeamRole, TeamPlan,
        InviteStatus, ThreadStatus, TeamError, TeamNotFoundError,
        TeamAccessDeniedError, TeamLimitExceededError, InviteError,
        InviteNotFoundError, InviteExpiredError
    )
    from ...models.auth import User
except ImportError:
    from src.models.team import (
        Team, TeamMembership, TeamInvite, TeamActivity, TeamRole, TeamPlan,
        InviteStatus, ThreadStatus, TeamError, TeamNotFoundError,
        TeamAccessDeniedError, TeamLimitExceededError, InviteError,
        InviteNotFoundError, InviteExpiredError
    )
    from src.models.auth import User


logger = logging.getLogger(__name__)


class TeamService:
    """Service for team collaboration operations"""
    
    def __init__(self, redis_manager, auth_service=None):
        self.redis = redis_manager
        self.auth_service = auth_service
        self.redis_prefix = "team:"
        
    # Team CRUD Operations
    async def create_team(self, owner_id: str, team_data: Dict[str, Any]) -> Team:
        """Create a new team"""
        try:
            # Check if slug is available
            if await self._is_slug_taken(team_data["slug"]):
                raise TeamError(f"Team slug '{team_data['slug']}' is already taken")
            
            # Create team
            team = Team(
                owner_id=owner_id,
                **team_data
            )
            
            # Set plan limits
            limits = team.get_plan_limits()
            team.max_members = limits["max_members"]
            team.max_monthly_threads = limits["max_monthly_threads"]
            
            # Store team
            await self._store_team(team)
            
            # Create owner membership
            membership = TeamMembership(
                team_id=team.id,
                user_id=owner_id,
                role=TeamRole.OWNER
            )
            await self._store_membership(membership)
            
            # Log activity
            await self._log_activity(
                team.id, owner_id, "team.created", "team", team.id,
                {"team_name": team.name, "plan": team.plan}
            )
            
            logger.info(f"Team created: {team.id} by user {owner_id}")
            return team
            
        except Exception as e:
            logger.error(f"Failed to create team: {e}")
            raise TeamError(f"Failed to create team: {str(e)}")
    
    async def get_team(self, team_id: str, user_id: Optional[str] = None) -> Team:
        """Get team by ID"""
        team = await self._get_team_by_id(team_id)
        if not team:
            raise TeamNotFoundError(f"Team {team_id} not found")
        
        # Check access if user_id provided
        if user_id and not await self._has_team_access(team_id, user_id):
            raise TeamAccessDeniedError("Access denied to team")
        
        return team
    
    async def update_team(self, team_id: str, user_id: str, updates: Dict[str, Any]) -> Team:
        """Update team details"""
        # Check permissions
        if not await self._has_permission(team_id, user_id, "team.settings"):
            raise TeamAccessDeniedError("Insufficient permissions to update team")
        
        team = await self.get_team(team_id, user_id)
        
        # Apply updates
        for field, value in updates.items():
            if hasattr(team, field) and field not in ["id", "owner_id", "created_at"]:
                setattr(team, field, value)
        
        team.updated_at = datetime.utcnow()
        
        # Store updated team
        await self._store_team(team)
        
        # Log activity
        await self._log_activity(
            team_id, user_id, "team.updated", "team", team_id, updates
        )
        
        return team
    
    async def delete_team(self, team_id: str, user_id: str) -> bool:
        """Delete team (owner only)"""
        # Check ownership
        membership = await self._get_membership(team_id, user_id)
        if not membership or membership.role != TeamRole.OWNER:
            raise TeamAccessDeniedError("Only team owner can delete team")
        
        try:
            # Delete all team data
            await self._delete_team_data(team_id)
            
            # Log activity
            await self._log_activity(
                team_id, user_id, "team.deleted", "team", team_id
            )
            
            logger.info(f"Team deleted: {team_id} by user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete team {team_id}: {e}")
            raise TeamError(f"Failed to delete team: {str(e)}")
    
    # Member Management
    async def invite_member(self, team_id: str, inviter_id: str, 
                          email: str, role: TeamRole, message: Optional[str] = None) -> TeamInvite:
        """Invite a new team member"""
        # Check permissions
        if not await self._has_permission(team_id, inviter_id, "members.invite"):
            raise TeamAccessDeniedError("Insufficient permissions to invite members")
        
        # Validate email
        try:
            valid_email = validate_email(email)
            email = valid_email.email
        except Exception:
            raise TeamError("Invalid email address")
        
        # Check team limits
        team = await self.get_team(team_id)
        member_count = await self._get_member_count(team_id)
        
        if member_count >= team.max_members:
            raise TeamLimitExceededError(f"Team has reached maximum member limit ({team.max_members})")
        
        # Check if user is already a member
        if await self._is_team_member_by_email(team_id, email):
            raise TeamError("User is already a team member")
        
        # Check for existing pending invite
        existing_invite = await self._get_pending_invite_by_email(team_id, email)
        if existing_invite:
            raise TeamError("Pending invite already exists for this email")
        
        # Create invite
        invite = TeamInvite(
            team_id=team_id,
            invited_by_user_id=inviter_id,
            email=email,
            role=role,
            message=message
        )
        
        # Store invite
        await self._store_invite(invite)
        
        # Log activity
        await self._log_activity(
            team_id, inviter_id, "member.invited", "invite", invite.id,
            {"email": email, "role": role}
        )
        
        # TODO: Send email invitation
        await self._send_invite_email(invite, team)
        
        logger.info(f"Member invited: {email} to team {team_id} by {inviter_id}")
        return invite
    
    async def accept_invite(self, token: str, user_id: str) -> TeamMembership:
        """Accept team invitation"""
        invite = await self._get_invite_by_token(token)
        if not invite:
            raise InviteNotFoundError("Invite not found")
        
        if not invite.is_valid():
            raise InviteExpiredError("Invite has expired or been revoked")
        
        # Get user email to verify
        if self.auth_service:
            user = await self.auth_service.get_user_by_id(user_id)
            if not user or user.email.lower() != invite.email.lower():
                raise TeamError("Invite email does not match user account")
        
        # Check team limits again
        team = await self.get_team(invite.team_id)
        member_count = await self._get_member_count(invite.team_id)
        
        if member_count >= team.max_members:
            raise TeamLimitExceededError("Team is now full")
        
        # Create membership
        membership = TeamMembership(
            team_id=invite.team_id,
            user_id=user_id,
            role=invite.role
        )
        
        # Store membership
        await self._store_membership(membership)
        
        # Mark invite as accepted
        invite.status = InviteStatus.ACCEPTED
        invite.accepted_at = datetime.utcnow()
        await self._store_invite(invite)
        
        # Log activity
        await self._log_activity(
            invite.team_id, user_id, "member.joined", "member", membership.id,
            {"role": invite.role, "via_invite": True}
        )
        
        logger.info(f"Invite accepted: {token} by user {user_id}")
        return membership
    
    async def remove_member(self, team_id: str, remover_id: str, member_id: str) -> bool:
        """Remove team member"""
        # Check permissions
        if not await self._has_permission(team_id, remover_id, "members.remove"):
            raise TeamAccessDeniedError("Insufficient permissions to remove members")
        
        # Cannot remove owner
        member_membership = await self._get_membership(team_id, member_id)
        if not member_membership:
            raise TeamError("Member not found")
        
        if member_membership.role == TeamRole.OWNER:
            raise TeamError("Cannot remove team owner")
        
        # Remove membership
        await self._delete_membership(team_id, member_id)
        
        # Log activity
        await self._log_activity(
            team_id, remover_id, "member.removed", "member", member_id
        )
        
        logger.info(f"Member removed: {member_id} from team {team_id} by {remover_id}")
        return True
    
    async def update_member_role(self, team_id: str, updater_id: str, 
                               member_id: str, new_role: TeamRole) -> TeamMembership:
        """Update team member role"""
        # Check permissions
        if not await self._has_permission(team_id, updater_id, "members.manage"):
            raise TeamAccessDeniedError("Insufficient permissions to manage members")
        
        membership = await self._get_membership(team_id, member_id)
        if not membership:
            raise TeamError("Member not found")
        
        # Cannot change owner role
        if membership.role == TeamRole.OWNER:
            raise TeamError("Cannot change owner role")
        
        old_role = membership.role
        membership.role = new_role
        membership.updated_at = datetime.utcnow()
        
        await self._store_membership(membership)
        
        # Log activity
        await self._log_activity(
            team_id, updater_id, "member.role_updated", "member", member_id,
            {"old_role": old_role, "new_role": new_role}
        )
        
        return membership
    
    # Team Listings and Search
    async def get_user_teams(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all teams for a user"""
        memberships = await self._get_user_memberships(user_id)
        teams = []
        
        for membership in memberships:
            if membership.is_active:
                team = await self._get_team_by_id(membership.team_id)
                if team and team.is_active:
                    team_data = team.to_dict()
                    team_data["current_user_role"] = membership.role
                    team_data["member_count"] = await self._get_member_count(team.id)
                    teams.append(team_data)
        
        return teams
    
    async def get_team_members(self, team_id: str, user_id: str) -> List[Dict[str, Any]]:
        """Get all team members"""
        # Check access
        if not await self._has_team_access(team_id, user_id):
            raise TeamAccessDeniedError("Access denied to team")
        
        memberships = await self._get_team_memberships(team_id)
        members = []
        
        for membership in memberships:
            if membership.is_active:
                # Get user details if auth_service available
                user_email = "unknown@example.com"  # Default
                if self.auth_service:
                    user = await self.auth_service.get_user_by_id(membership.user_id)
                    if user:
                        user_email = user.email
                
                members.append({
                    "user_id": membership.user_id,
                    "email": user_email,
                    "role": membership.role,
                    "joined_at": membership.joined_at,
                    "last_activity_at": membership.last_activity_at,
                    "thread_count": membership.thread_count,
                    "is_active": membership.is_active
                })
        
        return members
    
    async def get_team_invites(self, team_id: str, user_id: str) -> List[Dict[str, Any]]:
        """Get pending team invites"""
        # Check permissions
        if not await self._has_permission(team_id, user_id, "members.invite"):
            raise TeamAccessDeniedError("Insufficient permissions to view invites")
        
        invites = await self._get_team_invites(team_id)
        invite_list = []
        
        for invite in invites:
            if invite.status == InviteStatus.PENDING:
                # Get inviter email
                inviter_email = "unknown@example.com"
                if self.auth_service:
                    inviter = await self.auth_service.get_user_by_id(invite.invited_by_user_id)
                    if inviter:
                        inviter_email = inviter.email
                
                invite_list.append({
                    "id": invite.id,
                    "email": invite.email,
                    "role": invite.role,
                    "status": invite.status,
                    "created_at": invite.created_at,
                    "expires_at": invite.expires_at,
                    "invited_by": inviter_email
                })
        
        return invite_list
    
    # Permission System
    async def has_permission(self, team_id: str, user_id: str, permission: str) -> bool:
        """Check if user has specific permission in team"""
        return await self._has_permission(team_id, user_id, permission)
    
    async def get_user_role(self, team_id: str, user_id: str) -> Optional[TeamRole]:
        """Get user's role in team"""
        membership = await self._get_membership(team_id, user_id)
        return membership.role if membership else None
    
    # Team Statistics
    async def get_team_stats(self, team_id: str, user_id: str) -> Dict[str, Any]:
        """Get team usage statistics"""
        # Check access
        if not await self._has_team_access(team_id, user_id):
            raise TeamAccessDeniedError("Access denied to team")
        
        team = await self.get_team(team_id)
        member_count = await self._get_member_count(team_id)
        active_members = await self._get_active_member_count(team_id)
        
        # Get thread statistics
        total_threads = await self._get_team_thread_count(team_id)
        threads_this_month = await self._get_monthly_thread_count(team_id)
        
        usage_percent = (threads_this_month / team.max_monthly_threads) * 100 if team.max_monthly_threads > 0 else 0
        
        return {
            "member_count": member_count,
            "active_members": active_members,
            "total_threads": total_threads,
            "threads_this_month": threads_this_month,
            "monthly_limit": team.max_monthly_threads,
            "plan_usage_percent": round(usage_percent, 2)
        }
    
    # Activity Logging
    async def get_team_activity(self, team_id: str, user_id: str, 
                              limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Get team activity feed"""
        # Check access
        if not await self._has_team_access(team_id, user_id):
            raise TeamAccessDeniedError("Access denied to team")
        
        activities = await self._get_team_activities(team_id, limit, offset)
        
        # Enrich with user information
        enriched_activities = []
        for activity in activities:
            activity_dict = activity.model_dump()
            
            # Add user email if available
            if self.auth_service:
                user = await self.auth_service.get_user_by_id(activity.user_id)
                if user:
                    activity_dict["user_email"] = user.email
                    activity_dict["user_name"] = user.email.split("@")[0]  # Simple name extraction
            
            enriched_activities.append(activity_dict)
        
        return enriched_activities
    
    # Private Helper Methods
    async def _is_slug_taken(self, slug: str) -> bool:
        """Check if team slug is already taken"""
        def _check():
            return self.redis.client.exists(f"{self.redis_prefix}slug:{slug}")
        
        return await asyncio.get_event_loop().run_in_executor(None, _check)
    
    async def _store_team(self, team: Team) -> bool:
        """Store team in Redis"""
        def _store():
            pipe = self.redis.client.pipeline()
            pipe.hset(f"{self.redis_prefix}data:{team.id}", mapping=team.model_dump_json())
            pipe.set(f"{self.redis_prefix}slug:{team.slug}", team.id)
            pipe.sadd(f"{self.redis_prefix}all", team.id)
            pipe.execute()
            return True
        
        return await asyncio.get_event_loop().run_in_executor(None, _store)
    
    async def _get_team_by_id(self, team_id: str) -> Optional[Team]:
        """Get team by ID from Redis"""
        def _get():
            data = self.redis.client.hgetall(f"{self.redis_prefix}data:{team_id}")
            if data:
                return Team.model_validate_json(data.get('team', '{}'))
            return None
        
        return await asyncio.get_event_loop().run_in_executor(None, _get)
    
    async def _store_membership(self, membership: TeamMembership) -> bool:
        """Store team membership"""
        def _store():
            pipe = self.redis.client.pipeline()
            pipe.hset(f"{self.redis_prefix}membership:{membership.team_id}:{membership.user_id}", 
                     mapping=membership.model_dump_json())
            pipe.sadd(f"{self.redis_prefix}members:{membership.team_id}", membership.user_id)
            pipe.sadd(f"user:teams:{membership.user_id}", membership.team_id)
            pipe.execute()
            return True
        
        return await asyncio.get_event_loop().run_in_executor(None, _store)
    
    async def _get_membership(self, team_id: str, user_id: str) -> Optional[TeamMembership]:
        """Get team membership"""
        def _get():
            data = self.redis.client.hgetall(f"{self.redis_prefix}membership:{team_id}:{user_id}")
            if data:
                return TeamMembership.model_validate_json(data.get('membership', '{}'))
            return None
        
        return await asyncio.get_event_loop().run_in_executor(None, _get)
    
    async def _has_team_access(self, team_id: str, user_id: str) -> bool:
        """Check if user has access to team"""
        membership = await self._get_membership(team_id, user_id)
        return membership is not None and membership.is_active
    
    async def _has_permission(self, team_id: str, user_id: str, permission: str) -> bool:
        """Check if user has specific permission"""
        membership = await self._get_membership(team_id, user_id)
        return membership and membership.is_active and membership.has_permission(permission)
    
    async def _store_invite(self, invite: TeamInvite) -> bool:
        """Store team invite"""
        def _store():
            pipe = self.redis.client.pipeline()
            pipe.hset(f"{self.redis_prefix}invite:{invite.id}", mapping=invite.model_dump_json())
            pipe.set(f"{self.redis_prefix}invite_token:{invite.token}", invite.id)
            pipe.sadd(f"{self.redis_prefix}invites:{invite.team_id}", invite.id)
            pipe.execute()
            return True
        
        return await asyncio.get_event_loop().run_in_executor(None, _store)
    
    async def _get_invite_by_token(self, token: str) -> Optional[TeamInvite]:
        """Get invite by token"""
        def _get():
            invite_id = self.redis.client.get(f"{self.redis_prefix}invite_token:{token}")
            if invite_id:
                data = self.redis.client.hgetall(f"{self.redis_prefix}invite:{invite_id}")
                if data:
                    return TeamInvite.model_validate_json(data.get('invite', '{}'))
            return None
        
        return await asyncio.get_event_loop().run_in_executor(None, _get)
    
    async def _get_member_count(self, team_id: str) -> int:
        """Get team member count"""
        def _count():
            return self.redis.client.scard(f"{self.redis_prefix}members:{team_id}") or 0
        
        return await asyncio.get_event_loop().run_in_executor(None, _count)
    
    async def _is_team_member_by_email(self, team_id: str, email: str) -> bool:
        """Check if email is already a team member"""
        # This would require scanning all memberships - simplified for MVP
        # In production, consider maintaining email->user_id mapping
        return False
    
    async def _get_pending_invite_by_email(self, team_id: str, email: str) -> Optional[TeamInvite]:
        """Get pending invite by email"""
        # Simplified - in production, maintain email->invite mapping
        return None
    
    async def _send_invite_email(self, invite: TeamInvite, team: Team) -> bool:
        """Send invitation email (placeholder)"""
        # TODO: Implement email sending
        logger.info(f"Sending invite email to {invite.email} for team {team.name}")
        return True
    
    async def _log_activity(self, team_id: str, user_id: str, action: str, 
                          resource_type: str, resource_id: Optional[str] = None,
                          details: Optional[Dict[str, Any]] = None) -> bool:
        """Log team activity"""
        activity = TeamActivity(
            team_id=team_id,
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {}
        )
        
        def _log():
            pipe = self.redis.client.pipeline()
            pipe.lpush(f"{self.redis_prefix}activity:{team_id}", activity.model_dump_json())
            pipe.ltrim(f"{self.redis_prefix}activity:{team_id}", 0, 999)  # Keep last 1000 activities
            pipe.execute()
            return True
        
        return await asyncio.get_event_loop().run_in_executor(None, _log)
    
    # Additional placeholder methods for completeness
    async def _delete_team_data(self, team_id: str) -> bool:
        """Delete all team data"""
        # Implementation would delete all related data
        return True
    
    async def _get_user_memberships(self, user_id: str) -> List[TeamMembership]:
        """Get all user memberships"""
        return []
    
    async def _get_team_memberships(self, team_id: str) -> List[TeamMembership]:
        """Get all team memberships"""
        return []
    
    async def _get_team_invites(self, team_id: str) -> List[TeamInvite]:
        """Get all team invites"""
        return []
    
    async def _delete_membership(self, team_id: str, user_id: str) -> bool:
        """Delete team membership"""
        return True
    
    async def _get_active_member_count(self, team_id: str) -> int:
        """Get active member count"""
        return 0
    
    async def _get_team_thread_count(self, team_id: str) -> int:
        """Get total team thread count"""
        return 0
    
    async def _get_monthly_thread_count(self, team_id: str) -> int:
        """Get monthly thread count"""
        return 0
    
    async def _get_team_activities(self, team_id: str, limit: int, offset: int) -> List[TeamActivity]:
        """Get team activities"""
        return []