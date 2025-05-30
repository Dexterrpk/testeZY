# Placeholder for campaign-related service functions
# e.g., get_campaign, get_campaigns, create_campaign, update_campaign_status

from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime

from ..models.campaign import Campaign, CampaignCreate, CampaignUpdate
from ..models.user import User

def get_campaign(db: Session, campaign_id: int, owner_id: int) -> Optional[Campaign]:
    # Ensure campaign belongs to the user requesting it
    statement = select(Campaign).where(Campaign.id == campaign_id, Campaign.owner_id == owner_id)
    campaign = db.exec(statement).first()
    return campaign

def get_campaigns_by_owner(db: Session, owner_id: int, skip: int = 0, limit: int = 100) -> List[Campaign]:
    statement = select(Campaign).where(Campaign.owner_id == owner_id).offset(skip).limit(limit)
    campaigns = db.exec(statement).all()
    return campaigns

def create_campaign(db: Session, campaign_in: CampaignCreate, owner_id: int) -> Campaign:
    # Ensure owner_id from input matches the one from the token/user later
    if campaign_in.owner_id != owner_id:
        # This check might be redundant if owner_id is always set from current_user
        raise ValueError("Owner ID mismatch") 
    db_campaign = Campaign.model_validate(campaign_in)
    # Set created_at automatically by model default
    db.add(db_campaign)
    db.commit()
    db.refresh(db_campaign)
    return db_campaign

def update_campaign(db: Session, db_campaign: Campaign, campaign_in: CampaignUpdate) -> Campaign:
    campaign_data = campaign_in.model_dump(exclude_unset=True)
    for key, value in campaign_data.items():
        setattr(db_campaign, key, value)
    # Manually update updated_at if not handled by DB trigger
    db_campaign.updated_at = datetime.utcnow()
    db.add(db_campaign)
    db.commit()
    db.refresh(db_campaign)
    return db_campaign

def delete_campaign(db: Session, db_campaign: Campaign):
    db.delete(db_campaign)
    db.commit()
    return {"ok": True}

# Add functions for scheduling, sending simulation, status updates etc.

