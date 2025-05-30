from typing import Optional
from sqlmodel import Field, SQLModel

class PlanBase(SQLModel):
    name: str = Field(index=True, unique=True)
    description: Optional[str] = None
    # Define features allowed by this plan, e.g., max_campaigns, ai_training, custom_branding
    allow_ai_training: bool = False
    allow_custom_branding: bool = False
    max_scheduled_campaigns: int = 0
    allow_api_access: bool = False

class Plan(PlanBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

class PlanCreate(PlanBase):
    pass

class PlanRead(PlanBase):
    id: int

class PlanUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    allow_ai_training: Optional[bool] = None
    allow_custom_branding: Optional[bool] = None
    max_scheduled_campaigns: Optional[int] = None
    allow_api_access: Optional[bool] = None

