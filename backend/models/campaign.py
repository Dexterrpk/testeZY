from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime
from .user import User # Import User model
# Consider importing Customer model if needed for recipients

class CampaignBase(SQLModel):
    name: str = Field(index=True)
    message_template: str
    scheduled_time: Optional[datetime] = None
    status: str = Field(default="draft") # e.g., draft, scheduled, sending, sent, failed
    owner_id: int = Field(foreign_key="user.id")
    # Add fields for personalization, target audience (e.g., list of customer IDs or tags)

class Campaign(CampaignBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow})
    owner: User = Relationship(back_populates=None) # Define relationship if needed elsewhere
    # Add relationship to track sent messages or recipients

class CampaignCreate(CampaignBase):
    pass

class CampaignRead(CampaignBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    owner: Optional[User] = None # Avoid exposing full user details unless needed

class CampaignUpdate(SQLModel):
    name: Optional[str] = None
    message_template: Optional[str] = None
    scheduled_time: Optional[datetime] = None
    status: Optional[str] = None
    # Allow updating target audience etc.

