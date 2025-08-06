"""
Thread History API Routes for Threadr
Handles thread CRUD operations with authentication
"""

from fastapi import APIRouter, HTTPException, Depends, status, Query
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict, Any
import logging
from datetime import datetime

# Import models and services
try:
    from ..models.thread import (
        SaveThreadRequest, UpdateThreadRequest, ThreadHistoryRequest,
        ThreadHistoryResponse, ThreadHistoryFilter, SavedThread,
        ThreadNotFoundError, ThreadAccessDeniedError, ThreadStorageError
    )
except ImportError:
    from src.models.thread import (
        SaveThreadRequest, UpdateThreadRequest, ThreadHistoryRequest,
        ThreadHistoryResponse, ThreadHistoryFilter, SavedThread,
        ThreadNotFoundError, ThreadAccessDeniedError, ThreadStorageError
    )
try:
    from ..services.thread.thread_service import ThreadHistoryService
except ImportError:
    from src.services.thread.thread_service import ThreadHistoryService
try:
    from ..models.auth import User
except ImportError:
    from src.models.auth import User

logger = logging.getLogger(__name__)


def create_thread_router(thread_service: ThreadHistoryService, get_current_user) -> APIRouter:
    """Create and configure the thread API router"""
    
    router = APIRouter(
        prefix="",
        tags=["Thread History"],
        responses={404: {"description": "Not found"}}
    )
    
    @router.post("/save", response_model=Dict[str, Any])
    async def save_thread(
        request: SaveThreadRequest,
        current_user: User = Depends(get_current_user)
    ):
        """Save a new thread for the authenticated user"""
        try:
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            # Save the thread
            saved_thread = await thread_service.save_thread(
                user_id=current_user.user_id,
                title=request.title,
                original_content=request.original_content,
                tweets=request.tweets,
                metadata=request.metadata,
                client_ip=""  # Could be extracted from request if needed
            )
            
            logger.info(f"Thread saved successfully for user {current_user.user_id}: {saved_thread.id}")
            
            return {
                "success": True,
                "message": "Thread saved successfully",
                "thread": saved_thread.to_dict()
            }
            
        except ThreadStorageError as e:
            logger.error(f"Thread storage error: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            logger.error(f"Error saving thread: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save thread"
            )
    
    @router.get("", response_model=ThreadHistoryResponse)
    async def get_thread_history(
        page: int = Query(1, ge=1, description="Page number"),
        page_size: int = Query(10, ge=1, le=50, description="Items per page"),
        search_query: Optional[str] = Query(None, description="Search in title and content"),
        source_type: Optional[str] = Query(None, description="Filter by source type"),
        is_favorite: Optional[bool] = Query(None, description="Filter by favorite status"),
        is_archived: Optional[bool] = Query(None, description="Filter by archived status"),
        date_from: Optional[datetime] = Query(None, description="Filter from date"),
        date_to: Optional[datetime] = Query(None, description="Filter to date"),
        sort_by: str = Query("created_at", regex="^(created_at|updated_at|title|tweet_count)$"),
        sort_order: str = Query("desc", regex="^(asc|desc)$"),
        current_user: User = Depends(get_current_user)
    ):
        """Get paginated thread history for the authenticated user"""
        try:
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            # Create filters
            filters = ThreadHistoryFilter(
                search_query=search_query,
                source_type=source_type,
                is_favorite=is_favorite,
                is_archived=is_archived,
                date_from=date_from,
                date_to=date_to
            )
            
            # Get thread history
            history = await thread_service.get_user_threads(
                user_id=current_user.user_id,
                page=page,
                page_size=page_size,
                filters=filters,
                sort_by=sort_by,
                sort_order=sort_order
            )
            
            logger.info(f"Retrieved {len(history.threads)} threads for user {current_user.user_id}")
            return history
            
        except Exception as e:
            logger.error(f"Error getting thread history: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve thread history"
            )
    
    @router.get("/{thread_id}", response_model=Dict[str, Any])
    async def get_thread_details(
        thread_id: str,
        increment_view: bool = Query(True, description="Increment view count"),
        current_user: User = Depends(get_current_user)
    ):
        """Get details of a specific thread"""
        try:
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            # Get thread
            thread = await thread_service.get_thread_by_id(
                thread_id=thread_id,
                user_id=current_user.user_id,
                increment_view=increment_view
            )
            
            if not thread:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Thread not found"
                )
            
            logger.info(f"Retrieved thread details: {thread_id} for user {current_user.user_id}")
            
            return {
                "success": True,
                "thread": thread.to_dict()
            }
            
        except ThreadAccessDeniedError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this thread"
            )
        except Exception as e:
            logger.error(f"Error getting thread details: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve thread details"
            )
    
    @router.patch("/{thread_id}", response_model=Dict[str, Any])
    async def update_thread(
        thread_id: str,
        request: UpdateThreadRequest,
        current_user: User = Depends(get_current_user)
    ):
        """Update an existing thread"""
        try:
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            # Prepare updates
            updates = {}
            if request.title is not None:
                updates["title"] = request.title
            if request.is_favorite is not None:
                updates["is_favorite"] = request.is_favorite
            if request.is_archived is not None:
                updates["is_archived"] = request.is_archived
            if request.tags is not None:
                updates["tags"] = request.tags
            
            if not updates:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No updates provided"
                )
            
            # Update thread
            updated_thread = await thread_service.update_thread(
                thread_id=thread_id,
                user_id=current_user.user_id,
                updates=updates
            )
            
            if not updated_thread:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Thread not found"
                )
            
            logger.info(f"Updated thread: {thread_id} for user {current_user.user_id}")
            
            return {
                "success": True,
                "message": "Thread updated successfully",
                "thread": updated_thread.to_dict()
            }
            
        except ThreadNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Thread not found"
            )
        except ThreadAccessDeniedError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this thread"
            )
        except ThreadStorageError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            logger.error(f"Error updating thread: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update thread"
            )
    
    @router.delete("/{thread_id}", response_model=Dict[str, Any])
    async def delete_thread(
        thread_id: str,
        current_user: User = Depends(get_current_user)
    ):
        """Delete a thread"""
        try:
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            # Delete thread
            success = await thread_service.delete_thread(
                thread_id=thread_id,
                user_id=current_user.user_id
            )
            
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Thread not found"
                )
            
            logger.info(f"Deleted thread: {thread_id} for user {current_user.user_id}")
            
            return {
                "success": True,
                "message": "Thread deleted successfully"
            }
            
        except ThreadNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Thread not found"
            )
        except ThreadAccessDeniedError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this thread"
            )
        except Exception as e:
            logger.error(f"Error deleting thread: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete thread"
            )
    
    @router.post("/{thread_id}/copy", response_model=Dict[str, Any])
    async def increment_copy_count(
        thread_id: str,
        current_user: User = Depends(get_current_user)
    ):
        """Track that a thread was copied (for analytics)"""
        try:
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            # Increment copy count
            success = await thread_service.increment_copy_count(
                thread_id=thread_id,
                user_id=current_user.user_id
            )
            
            if not success:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Thread not found"
                )
            
            logger.info(f"Incremented copy count for thread: {thread_id}")
            
            return {
                "success": True,
                "message": "Copy count updated"
            }
            
        except Exception as e:
            logger.error(f"Error incrementing copy count: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update copy count"
            )
    
    @router.get("/test")
    async def test_thread_routes():
        """Test endpoint to verify thread routes are working - no auth required"""
        return {
            "success": True,
            "message": "Thread routes are working!",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @router.get("/stats/summary", response_model=Dict[str, Any])
    async def get_thread_stats(
        current_user: User = Depends(get_current_user)
    ):
        """Get thread statistics for the authenticated user"""
        try:
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            # Get thread count
            total_threads = await thread_service.get_user_thread_count(current_user.user_id)
            
            # Get recent threads (last 7 days)
            from datetime import timedelta
            week_ago = datetime.utcnow() - timedelta(days=7)
            recent_filter = ThreadHistoryFilter(date_from=week_ago)
            
            recent_history = await thread_service.get_user_threads(
                user_id=current_user.user_id,
                page=1,
                page_size=100,  # Get all recent threads
                filters=recent_filter
            )
            
            # Calculate stats
            recent_threads = len(recent_history.threads)
            favorite_threads = len([t for t in recent_history.threads if t.get('is_favorite', False)])
            
            stats = {
                "total_threads": total_threads,
                "recent_threads_7d": recent_threads,
                "favorite_threads": favorite_threads,
                "user_id": current_user.user_id
            }
            
            logger.info(f"Retrieved thread stats for user {current_user.user_id}")
            
            return {
                "success": True,
                "stats": stats
            }
            
        except Exception as e:
            logger.error(f"Error getting thread stats: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve thread statistics"
            )
    
    return router


# Create a default router instance for backward compatibility with main.py imports
# This will be a minimal router that can be imported but requires proper initialization
router = APIRouter(prefix="/api/threads", tags=["threads"])

# Add a note that this router needs to be properly initialized
@router.get("/")
async def thread_router_not_initialized():
    """Placeholder endpoint - this router needs proper initialization via create_thread_router()"""
    return {"error": "Thread router not properly initialized. Use create_thread_router() function."}