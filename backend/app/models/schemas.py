from pydantic import BaseModel, Field, confloat, field_validator
from typing import Optional, List
from pydantic import HttpUrl

class CustomerRecord(BaseModel):
    twitter_username: str
    webscraping_batch_size: int

class JobRunMain(BaseModel):
    Id: str
    job_id: str
    cursor: Optional[str]
    status: str
    batch_count: int
    ceiling_count: int
    cumulative_count: int
    customer_telegram: str
    twitter_username: str
    customer_uuid: str
    note: str

class JobRunCustomer(BaseModel):
    Id: str
    job_run: str
    note: str
    status: str
    progress: int
    prompt: str

class TwitterStatus(BaseModel):
    text: Optional[str] = ""
    retweet_count: Optional[int] = 0
    favorite_count: Optional[int] = 0

class TwitterUser(BaseModel):
    id: str
    screen_name: str
    name: str
    location: Optional[str]
    description: Optional[str]
    followers_count: int
    friends_count: int
    favourites_count: int
    created_at: str
    statuses_count: int
    media_count: int
    profile_image_url: Optional[str]
    verified: bool
    status: Optional[TwitterStatus] = None

class AnalyzedUser(BaseModel):
    twitter_username: str
    bot_score: float
    ai_notes: str
    job_run: str
    twitter_profile_url: str
    twitter_user_id: str
    bio: Optional[str]
    followers_count: int
    following_count: int
    status_count: int
    media_count: int
    bookmarks_count: int
    twitter_display_name: str
    tags: Optional[str] 

class UserInfo(BaseModel):
    user_id: str
    tags: List[str]
    ai_analysis_notes: str
    bot_score: int = Field(
        ...,
        ge=1,
        le=10,
        description="Bot score from 1 (human) to 10 (definitely a bot)"
    )
    
class RelevantUsersResponse(BaseModel):
    total_matches: int
    users: List[UserInfo]   


class WebscrapeRequest(BaseModel):
    user_request: str
    user_prompt: str
    count: Optional[int] = 100
    cursor: Optional[str] = None