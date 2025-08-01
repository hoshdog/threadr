"""
Thread models for Threadr
Handles thread storage, retrieval, and management
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, field_validator
import uuid
import json


class ThreadTweet(BaseModel):
    """Individual tweet within a thread"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str = Field(..., max_length=280, description="Tweet content")
    order: int = Field(..., ge=1, description="Order in the thread (1-based)")
    character_count: int = Field(..., ge=0, le=280, description="Character count")
    
    def model_dump_json(self, **kwargs) -> str:
        """Custom JSON serialization"""
        return json.dumps(self.model_dump(**kwargs), default=str)
    
    @field_validator('character_count')
    @classmethod
    def validate_character_count(cls, v, info):
        """Validate character count matches content length"""
        if 'content' in info.data:
            actual_count = len(info.data['content'])
            if v != actual_count:
                return actual_count
        return v


class ThreadMetadata(BaseModel):
    """Metadata for a thread"""
    source_url: Optional[str] = None
    source_type: str = Field(default="text", description="URL or text")
    generation_time_ms: Optional[int] = None
    ai_model: str = Field(default="gpt-3.5-turbo")
    content_length: Optional[int] = None
    tags: List[str] = Field(default_factory=list)
    
    def model_dump_json(self, **kwargs) -> str:
        """Custom JSON serialization"""
        return json.dumps(self.model_dump(**kwargs), default=str)


class SavedThread(BaseModel):
    """A saved thread with all its tweets and metadata"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = Field(..., description="User who created the thread")
    title: str = Field(..., max_length=200, description="Thread title/summary")
    original_content: str = Field(..., description="Original content that was converted")
    tweets: List[ThreadTweet] = Field(..., min_length=1, description="Thread tweets")
    metadata: ThreadMetadata = Field(default_factory=ThreadMetadata)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Usage tracking
    view_count: int = Field(default=0, ge=0)
    copy_count: int = Field(default=0, ge=0)
    
    # Premium features
    is_favorite: bool = Field(default=False)
    is_archived: bool = Field(default=False)
    
    def model_dump_json(self, **kwargs) -> str:
        """Custom JSON serialization"""
        return json.dumps(self.model_dump(**kwargs), default=str)
    
    @property
    def tweet_count(self) -> int:
        """Number of tweets in the thread"""
        return len(self.tweets)
    
    @property
    def total_characters(self) -> int:
        """Total character count of all tweets"""
        return sum(tweet.character_count for tweet in self.tweets)
    
    def get_preview_text(self, max_length: int = 100) -> str:
        """Get a preview of the first tweet"""
        if not self.tweets:
            return ""
        first_tweet = self.tweets[0].content
        if len(first_tweet) <= max_length:
            return first_tweet
        return first_tweet[:max_length-3] + "..."
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "original_content": self.original_content,
            "tweets": [tweet.model_dump() for tweet in self.tweets],
            "metadata": self.metadata.model_dump(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "view_count": self.view_count,
            "copy_count": self.copy_count,
            "is_favorite": self.is_favorite,
            "is_archived": self.is_archived,
            "tweet_count": self.tweet_count,
            "total_characters": self.total_characters,
            "preview_text": self.get_preview_text()
        }


class ThreadHistoryFilter(BaseModel):
    """Filters for thread history queries"""
    search_query: Optional[str] = None
    source_type: Optional[str] = None  # "url" or "text"
    is_favorite: Optional[bool] = None
    is_archived: Optional[bool] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    tags: Optional[List[str]] = None
    
    def to_redis_pattern(self) -> str:
        """Convert filter to Redis search pattern"""
        # This would be used for Redis search if we implement full-text search
        patterns = []
        if self.search_query:
            patterns.append(f"*{self.search_query.lower()}*")
        return " ".join(patterns) if patterns else "*"


class ThreadHistoryResponse(BaseModel):
    """Response for thread history API"""
    threads: List[Dict[str, Any]]
    total_count: int
    page: int
    page_size: int
    has_next: bool
    has_previous: bool
    
    def model_dump_json(self, **kwargs) -> str:
        """Custom JSON serialization"""
        return json.dumps(self.model_dump(**kwargs), default=str)


# API Request/Response Models
class SaveThreadRequest(BaseModel):
    """Request to save a new thread"""
    title: str = Field(..., max_length=200)
    original_content: str = Field(..., max_length=50000)
    tweets: List[Dict[str, Any]] = Field(..., min_length=1)
    metadata: Optional[Dict[str, Any]] = None
    
    @field_validator('tweets')
    @classmethod
    def validate_tweets(cls, v):
        """Validate tweet structure"""
        for i, tweet in enumerate(v):
            if not isinstance(tweet, dict):
                raise ValueError(f"Tweet {i} must be a dictionary")
            if 'content' not in tweet:
                raise ValueError(f"Tweet {i} missing 'content' field")
            if len(tweet['content']) > 280:
                raise ValueError(f"Tweet {i} exceeds 280 characters")
        return v


class UpdateThreadRequest(BaseModel):
    """Request to update an existing thread"""
    title: Optional[str] = Field(None, max_length=200)
    is_favorite: Optional[bool] = None
    is_archived: Optional[bool] = None
    tags: Optional[List[str]] = None


class ThreadHistoryRequest(BaseModel):
    """Request for thread history with pagination and filters"""
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=50)
    search_query: Optional[str] = None
    source_type: Optional[str] = None
    is_favorite: Optional[bool] = None
    is_archived: Optional[bool] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    sort_by: str = Field(default="created_at", pattern="^(created_at|updated_at|title|tweet_count)$")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")


# Error Models
class ThreadNotFoundError(Exception):
    """Thread not found error"""
    pass


class ThreadAccessDeniedError(Exception):
    """Thread access denied error"""
    pass


class ThreadStorageError(Exception):
    """Thread storage error"""
    pass