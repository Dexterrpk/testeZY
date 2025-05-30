from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlmodel import Session

from ..core.database import get_session
from ..models.campaign import Campaign, CampaignCreate, CampaignRead, CampaignUpdate
from ..models.user import User
from ..services import campaign_service, plan_service, user_service # Added plan_service, user_service
# Import real dependency
from ..core.dependencies import get_current_active_user

router = APIRouter()

# Helper function to check campaign limits (example)
def check_campaign_limit(db: Session, user: User):
    if user.plan and user.plan.max_scheduled_campaigns != -1: # -1 means unlimited
        current_campaigns = campaign_service.get_campaigns_by_owner(db, owner_id=user.id, limit=user.plan.max_scheduled_campaigns + 1)
        # Consider filtering by status (e.g., only count 'scheduled' or 'active')
        if len(current_campaigns) >= user.plan.max_scheduled_campaigns:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Limite de campanhas ({user.plan.max_scheduled_campaigns}) atingido para o plano {user.plan.name}."
            )

@router.post("/", response_model=CampaignRead, status_code=status.HTTP_201_CREATED)
def create_campaign(
    *, 
    db: Session = Depends(get_session), 
    campaign_in: CampaignCreate,
    current_user: User = Depends(get_current_active_user) # Use real dependency
):
    """
    Create new campaign for the current user.
    """
    # Ensure the owner_id in the payload matches the current user
    if campaign_in.owner_id != current_user.id:
         raise HTTPException(
             status_code=status.HTTP_403_FORBIDDEN,
             detail="Cannot create campaign for another user."
         )
    
    # Fetch user with plan details for checks
    user_with_plan = db.get(User, current_user.id) # Get user again to potentially refresh relationships if needed
    if user_with_plan and user_with_plan.plan_id:
        user_with_plan.plan = plan_service.get_plan(db, plan_id=user_with_plan.plan_id)
    else:
         # Handle case where user might not have a plan assigned (should not happen ideally)
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuário sem plano associado.")

    # Check plan limits before creating
    check_campaign_limit(db, user_with_plan)

    campaign = campaign_service.create_campaign(db=db, campaign_in=campaign_in, owner_id=current_user.id)
    return campaign

@router.get("/", response_model=List[CampaignRead])
def read_campaigns(
    db: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user) # Use real dependency
):
    """
    Retrieve campaigns for the current user.
    """
    campaigns = campaign_service.get_campaigns_by_owner(db, owner_id=current_user.id, skip=skip, limit=limit)
    return campaigns

@router.get("/{campaign_id}", response_model=CampaignRead)
def read_campaign(
    *, 
    db: Session = Depends(get_session), 
    campaign_id: int,
    current_user: User = Depends(get_current_active_user) # Use real dependency
):
    """
    Get a specific campaign by ID, owned by the current user.
    """
    campaign = campaign_service.get_campaign(db, campaign_id=campaign_id, owner_id=current_user.id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found or not owned by user")
    return campaign

@router.put("/{campaign_id}", response_model=CampaignRead)
def update_campaign(
    *, 
    db: Session = Depends(get_session), 
    campaign_id: int, 
    campaign_in: CampaignUpdate,
    current_user: User = Depends(get_current_active_user) # Use real dependency
):
    """
    Update a campaign owned by the current user.
    """
    db_campaign = campaign_service.get_campaign(db, campaign_id=campaign_id, owner_id=current_user.id)
    if not db_campaign:
        raise HTTPException(status_code=404, detail="Campaign not found or not owned by user")
    # Add checks if status changes require specific logic (e.g., cannot edit 'sent' campaign)
    if db_campaign.status == 'sent' or db_campaign.status == 'sending':
        # Example: Prevent editing campaigns that are already sent or in progress
        # Adjust logic based on requirements
        # raise HTTPException(status_code=400, detail=f"Cannot modify campaign in '{db_campaign.status}' state.")
        pass # Allow updates for now, refine later

    campaign = campaign_service.update_campaign(db=db, db_campaign=db_campaign, campaign_in=campaign_in)
    return campaign

@router.delete("/{campaign_id}", status_code=status.HTTP_200_OK)
def delete_campaign(
    *, 
    db: Session = Depends(get_session), 
    campaign_id: int,
    current_user: User = Depends(get_current_active_user) # Use real dependency
):
    """
    Delete a campaign owned by the current user.
    """
    db_campaign = campaign_service.get_campaign(db, campaign_id=campaign_id, owner_id=current_user.id)
    if not db_campaign:
        raise HTTPException(status_code=404, detail="Campaign not found or not owned by user")
    # Add checks: cannot delete campaign if it's currently sending?
    if db_campaign.status == 'sending':
         raise HTTPException(status_code=400, detail="Cannot delete campaign while it is sending.")
         
    campaign_service.delete_campaign(db=db, db_campaign=db_campaign)
    return {"message": "Campaign deleted successfully"}

