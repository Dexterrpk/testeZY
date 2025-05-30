from typing import Optional
from sqlmodel import Field, SQLModel, Relationship
from .plan import Plan # Import Plan model

class UserBase(SQLModel):
    email: str = Field(unique=True, index=True)
    is_active: bool = True
    is_superuser: bool = False
    full_name: Optional[str] = None
    plan_id: Optional[int] = Field(default=None, foreign_key="plan.id")
    # Add fields for custom branding if needed, e.g., logo_url
    custom_logo_url: Optional[str] = None

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str
    plan: Optional[Plan] = Relationship(back_populates=None) # Define relationship if needed elsewhere
    # Add relationships to other models like Campaigns, AI Training Data, etc.

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int

class UserUpdate(SQLModel):
    email: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    plan_id: Optional[int] = None
    custom_logo_url: Optional[str] = None

