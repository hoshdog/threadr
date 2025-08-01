"""
Team collaboration API routes for Threadr
Handles team CRUD, member management, and invite flows
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from fastapi.security import HTTPBearer
from typing import Optional, List, Dict, Any
import logging

# Import models and services
try:
    from ..models.team import (
        CreateTeamRequest, UpdateTeamRequest, InviteMemberRequest, 
        UpdateMemberRequest, AcceptInviteRequest, TeamResponse,
        MemberResponse, InviteResponse, TeamStatsResponse,
        TeamRole, TeamPlan, TeamError, TeamNotFoundError,
        TeamAccessDeniedError, TeamLimitExceededError,
        InviteError, InviteNotFoundError, InviteExpiredError
    )
    from ..services.team.team_service import TeamService
    from ..models.auth import User
except ImportError:
    from models.team import (
        CreateTeamRequest, UpdateTeamRequest, InviteMemberRequest, 
        UpdateMemberRequest, AcceptInviteRequest, TeamResponse,
        MemberResponse, InviteResponse, TeamStatsResponse,
        TeamRole, TeamPlan, TeamError, TeamNotFoundError,
        TeamAccessDeniedError, TeamLimitExceededError,
        InviteError, InviteNotFoundError, InviteExpiredError
    )
    from services.team.team_service import TeamService
    from models.auth import User


logger = logging.getLogger(__name__)
security = HTTPBearer()


def create_team_router(team_service: TeamService, auth_dependencies: Dict[str, Any]) -> APIRouter:
    """Create team collaboration router with dependency injection"""
    
    router = APIRouter(prefix="/api/teams", tags=["teams"])
    
    # Get auth dependencies
    get_current_user = auth_dependencies["get_current_user_required"]
    get_current_user_optional = auth_dependencies["get_current_user_optional"]
    
    def get_user_context(request: Request) -> Dict[str, Any]:
        """Extract user context from request"""
        return {
            "ip_address": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("user-agent", "unknown")
        }
    
    # Team CRUD Operations
    @router.post("/", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
    async def create_team(
        request_data: CreateTeamRequest,
        current_user: User = Depends(get_current_user),
        context: Dict[str, Any] = Depends(get_user_context)
    ):
        """Create a new team/workspace"""
        try:
            team = await team_service.create_team(
                owner_id=current_user.user_id,
                team_data=request_data.model_dump()
            )
            
            # Build response
            member_count = await team_service._get_member_count(team.id)
            
            return TeamResponse(
                id=team.id,
                name=team.name,
                slug=team.slug,
                description=team.description,
                plan=team.plan,
                member_count=member_count,
                max_members=team.max_members,
                owner_id=team.owner_id,
                created_at=team.created_at,
                current_user_role=TeamRole.OWNER
            )
            
        except TeamError as e:
            logger.error(f"Team creation error for user {current_user.user_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            logger.error(f"Unexpected error creating team: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create team"
            )
    
    @router.get("/", response_model=List[TeamResponse])
    async def get_user_teams(
        current_user: User = Depends(get_current_user)
    ):
        """Get all teams for the current user"""
        try:
            teams = await team_service.get_user_teams(current_user.user_id)
            
            # Convert to response format
            team_responses = []
            for team_data in teams:
                team_responses.append(TeamResponse(
                    id=team_data["id"],
                    name=team_data["name"],
                    slug=team_data["slug"],
                    description=team_data.get("description"),
                    plan=TeamPlan(team_data["plan"]),
                    member_count=team_data["member_count"],
                    max_members=team_data["max_members"],
                    owner_id=team_data.get("owner_id", ""),
                    created_at=team_data["created_at"],
                    current_user_role=TeamRole(team_data["current_user_role"])
                ))
            
            return team_responses
            
        except Exception as e:
            logger.error(f"Error fetching user teams for {current_user.user_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch teams"
            )
    
    @router.get("/{team_id}", response_model=TeamResponse)
    async def get_team(
        team_id: str,
        current_user: User = Depends(get_current_user)
    ):
        """Get team details"""
        try:
            team = await team_service.get_team(team_id, current_user.user_id)
            user_role = await team_service.get_user_role(team_id, current_user.user_id)
            member_count = await team_service._get_member_count(team_id)
            
            return TeamResponse(
                id=team.id,
                name=team.name,
                slug=team.slug,
                description=team.description,
                plan=team.plan,
                member_count=member_count,
                max_members=team.max_members,
                owner_id=team.owner_id,
                created_at=team.created_at,
                current_user_role=user_role
            )
            
        except TeamNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team not found"
            )
        except TeamAccessDeniedError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to team"
            )
        except Exception as e:
            logger.error(f"Error fetching team {team_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch team"
            )
    
    @router.put("/{team_id}", response_model=TeamResponse)
    async def update_team(
        team_id: str,
        updates: UpdateTeamRequest,
        current_user: User = Depends(get_current_user)
    ):
        """Update team details"""
        try:
            # Filter out None values
            update_data = {k: v for k, v in updates.model_dump().items() if v is not None}
            
            team = await team_service.update_team(team_id, current_user.user_id, update_data)
            user_role = await team_service.get_user_role(team_id, current_user.user_id)
            member_count = await team_service._get_member_count(team_id)
            
            return TeamResponse(
                id=team.id,
                name=team.name,
                slug=team.slug,
                description=team.description,
                plan=team.plan,
                member_count=member_count,
                max_members=team.max_members,
                owner_id=team.owner_id,
                created_at=team.created_at,
                current_user_role=user_role
            )
            
        except TeamNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team not found"
            )
        except TeamAccessDeniedError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to update team"
            )
        except Exception as e:
            logger.error(f"Error updating team {team_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update team"
            )
    
    @router.delete("/{team_id}")
    async def delete_team(
        team_id: str,
        current_user: User = Depends(get_current_user)
    ):
        """Delete team (owner only)"""
        try:
            await team_service.delete_team(team_id, current_user.user_id)
            return {"message": "Team deleted successfully"}
            
        except TeamNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team not found"
            )
        except TeamAccessDeniedError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only team owner can delete team"
            )
        except Exception as e:
            logger.error(f"Error deleting team {team_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete team"
            )
    
    # Member Management
    @router.get("/{team_id}/members", response_model=List[MemberResponse])
    async def get_team_members(
        team_id: str,
        current_user: User = Depends(get_current_user)
    ):
        """Get team members"""
        try:
            members = await team_service.get_team_members(team_id, current_user.user_id)
            
            # Convert to response format
            member_responses = []
            for member_data in members:
                member_responses.append(MemberResponse(
                    user_id=member_data["user_id"],
                    email=member_data["email"],
                    role=TeamRole(member_data["role"]),
                    joined_at=member_data["joined_at"],
                    last_activity_at=member_data.get("last_activity_at"),
                    thread_count=member_data["thread_count"],
                    is_active=member_data["is_active"]
                ))
            
            return member_responses
            
        except TeamNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team not found"
            )
        except TeamAccessDeniedError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to team"
            )
        except Exception as e:
            logger.error(f"Error fetching team members for {team_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch team members"
            )
    
    @router.post("/{team_id}/invites", response_model=InviteResponse, status_code=status.HTTP_201_CREATED)
    async def invite_member(
        team_id: str,
        invite_data: InviteMemberRequest,
        current_user: User = Depends(get_current_user)
    ):
        """Invite a new team member"""
        try:
            invite = await team_service.invite_member(
                team_id=team_id,
                inviter_id=current_user.user_id,
                email=invite_data.email,
                role=invite_data.role,
                message=invite_data.message
            )
            
            return InviteResponse(
                id=invite.id,
                email=invite.email,
                role=invite.role,
                status=invite.status,
                created_at=invite.created_at,
                expires_at=invite.expires_at,
                invited_by=current_user.email
            )
            
        except TeamNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team not found"
            )
        except TeamAccessDeniedError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to invite members"
            )
        except TeamLimitExceededError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except TeamError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            logger.error(f"Error inviting member to team {team_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to invite member"
            )
    
    @router.get("/{team_id}/invites", response_model=List[InviteResponse])
    async def get_team_invites(
        team_id: str,
        current_user: User = Depends(get_current_user)
    ):
        """Get pending team invites"""
        try:
            invites = await team_service.get_team_invites(team_id, current_user.user_id)
            
            # Convert to response format
            invite_responses = []
            for invite_data in invites:
                invite_responses.append(InviteResponse(
                    id=invite_data["id"],
                    email=invite_data["email"],
                    role=TeamRole(invite_data["role"]),
                    status=invite_data["status"],
                    created_at=invite_data["created_at"],
                    expires_at=invite_data["expires_at"],
                    invited_by=invite_data["invited_by"]
                ))
            
            return invite_responses
            
        except TeamNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team not found"
            )
        except TeamAccessDeniedError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to view invites"
            )
        except Exception as e:
            logger.error(f"Error fetching team invites for {team_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch team invites"
            )
    
    @router.post("/invites/accept", response_model=Dict[str, str])
    async def accept_invite(
        accept_data: AcceptInviteRequest,
        current_user: User = Depends(get_current_user)
    ):
        """Accept team invitation"""
        try:
            membership = await team_service.accept_invite(accept_data.token, current_user.user_id)
            
            return {
                "message": "Invite accepted successfully",
                "team_id": membership.team_id,
                "role": membership.role
            }
            
        except InviteNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invite not found"
            )
        except InviteExpiredError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invite has expired"
            )
        except TeamLimitExceededError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except TeamError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            logger.error(f"Error accepting invite {accept_data.token}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to accept invite"
            )
    
    @router.put("/{team_id}/members/{member_id}", response_model=MemberResponse)
    async def update_member(
        team_id: str,
        member_id: str,
        updates: UpdateMemberRequest,
        current_user: User = Depends(get_current_user)
    ):
        """Update team member role/permissions"""
        try:
            if updates.role:
                membership = await team_service.update_member_role(
                    team_id, current_user.user_id, member_id, updates.role
                )
            else:
                # Handle permission updates if needed
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No updates provided"
                )
            
            # Get user email for response
            user_email = "unknown@example.com"
            if team_service.auth_service:
                user = await team_service.auth_service.get_user_by_id(member_id)
                if user:
                    user_email = user.email
            
            return MemberResponse(
                user_id=membership.user_id,
                email=user_email,
                role=membership.role,
                joined_at=membership.joined_at,
                last_activity_at=membership.last_activity_at,
                thread_count=membership.thread_count,
                is_active=membership.is_active
            )
            
        except TeamNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team not found"
            )
        except TeamAccessDeniedError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to update member"
            )
        except TeamError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            logger.error(f"Error updating member {member_id} in team {team_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update member"
            )
    
    @router.delete("/{team_id}/members/{member_id}")
    async def remove_member(
        team_id: str,
        member_id: str,
        current_user: User = Depends(get_current_user)
    ):
        """Remove team member"""
        try:
            await team_service.remove_member(team_id, current_user.user_id, member_id)
            
            return {"message": "Member removed successfully"}
            
        except TeamNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team not found"
            )
        except TeamAccessDeniedError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to remove member"
            )
        except TeamError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            logger.error(f"Error removing member {member_id} from team {team_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to remove member"
            )
    
    # Team Statistics and Analytics
    @router.get("/{team_id}/stats", response_model=TeamStatsResponse)
    async def get_team_stats(
        team_id: str,
        current_user: User = Depends(get_current_user)
    ):
        """Get team usage statistics"""
        try:
            stats = await team_service.get_team_stats(team_id, current_user.user_id)
            
            return TeamStatsResponse(
                member_count=stats["member_count"],
                active_members=stats["active_members"],
                total_threads=stats["total_threads"],
                threads_this_month=stats["threads_this_month"],
                monthly_limit=stats["monthly_limit"],
                plan_usage_percent=stats["plan_usage_percent"]
            )
            
        except TeamNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team not found"
            )
        except TeamAccessDeniedError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to team"
            )
        except Exception as e:
            logger.error(f"Error fetching team stats for {team_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch team statistics"
            )
    
    @router.get("/{team_id}/activity")
    async def get_team_activity(
        team_id: str,
        current_user: User = Depends(get_current_user),
        limit: int = Query(50, ge=1, le=100),
        offset: int = Query(0, ge=0)
    ):
        """Get team activity feed"""
        try:
            activities = await team_service.get_team_activity(team_id, current_user.user_id, limit, offset)
            
            return {
                "activities": activities,
                "limit": limit,
                "offset": offset,
                "count": len(activities)
            }
            
        except TeamNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team not found"
            )
        except TeamAccessDeniedError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to team"
            )
        except Exception as e:
            logger.error(f"Error fetching team activity for {team_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch team activity"
            )
    
    # Utility Endpoints
    @router.get("/{team_id}/permissions")
    async def get_user_permissions(
        team_id: str,
        current_user: User = Depends(get_current_user)
    ):
        """Get current user's permissions in team"""
        try:
            user_role = await team_service.get_user_role(team_id, current_user.user_id)
            if not user_role:
                raise TeamAccessDeniedError("Not a team member")
            
            # Get all permissions for the role
            role_permissions = {
                TeamRole.OWNER: [
                    "team.delete", "team.billing", "team.settings", 
                    "members.invite", "members.remove", "members.manage",
                    "threads.create", "threads.edit", "threads.delete", "threads.approve",
                    "analytics.view"
                ],
                TeamRole.ADMIN: [
                    "team.settings", "members.invite", "members.remove",
                    "threads.create", "threads.edit", "threads.delete", "threads.approve",
                    "analytics.view"
                ],
                TeamRole.EDITOR: [
                    "threads.create", "threads.edit", "threads.submit",
                    "analytics.view_own"
                ],
                TeamRole.VIEWER: [
                    "threads.view", "analytics.view_summary"
                ]
            }
            
            return {
                "role": user_role,
                "permissions": role_permissions.get(user_role, [])
            }
            
        except TeamAccessDeniedError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to team"
            )
        except Exception as e:
            logger.error(f"Error fetching permissions for team {team_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch permissions"
            )
    
    return router