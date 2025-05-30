from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlmodel import Session

from ..core.database import get_session
from ..models.plan import Plan, PlanCreate, PlanRead, PlanUpdate
from ..models.user import User # Import User for dependency typing
from ..services import plan_service
# Import real dependencies
from ..core.dependencies import get_current_active_user, get_current_active_superuser

router = APIRouter()

# Endpoint to create default plans (restricted to superuser)
@router.post("/create-defaults", status_code=status.HTTP_201_CREATED, include_in_schema=False) # Hide from docs
def create_default_plans_endpoint(
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_superuser) # Require superuser
):
    """Creates the default plans if they don't exist. (Superuser only)"""
    plan_service.create_default_plans(db)
    return {"message": "Default plans checked/created."}

@router.post("/", response_model=PlanRead, status_code=status.HTTP_201_CREATED)
def create_plan(
    *, 
    db: Session = Depends(get_session), 
    plan_in: PlanCreate,
    current_user: User = Depends(get_current_active_superuser) # Require superuser
):
    """
    Create new plan. (Requires superuser privileges)
    """
    existing_plan = plan_service.get_plan_by_name(db, name=plan_in.name)
    if existing_plan:
        raise HTTPException(status_code=400, detail="Plan with this name already exists.")
    plan = plan_service.create_plan(db=db, plan=plan_in)
    return plan

@router.get("/", response_model=List[PlanRead])
def read_plans(
    db: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user) # Allow any logged-in user
):
    """
    Retrieve plans. (Requires logged-in user)
    """
    plans = plan_service.get_plans(db, skip=skip, limit=limit)
    return plans

@router.get("/{plan_id}", response_model=PlanRead)
def read_plan(
    *, 
    db: Session = Depends(get_session), 
    plan_id: int,
    current_user: User = Depends(get_current_active_user) # Allow any logged-in user
):
    """
    Get plan by ID. (Requires logged-in user)
    """
    plan = plan_service.get_plan(db, plan_id=plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan

@router.put("/{plan_id}", response_model=PlanRead)
def update_plan(
    *, 
    db: Session = Depends(get_session), 
    plan_id: int, 
    plan_in: PlanUpdate,
    current_user: User = Depends(get_current_active_superuser) # Require superuser
):
    """
    Update a plan. (Requires superuser privileges)
    """
    db_plan = plan_service.get_plan(db, plan_id=plan_id)
    if not db_plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    plan = plan_service.update_plan(db=db, db_plan=db_plan, plan_in=plan_in)
    return plan

@router.delete("/{plan_id}", status_code=status.HTTP_200_OK)
def delete_plan(
    *, 
    db: Session = Depends(get_session), 
    plan_id: int,
    current_user: User = Depends(get_current_active_superuser) # Require superuser
):
    """
    Delete a plan. (Requires superuser privileges)
    """
    db_plan = plan_service.get_plan(db, plan_id=plan_id)
    if not db_plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    # Add check: ensure no users are currently assigned to this plan before deleting?
    # users_on_plan = user_service.get_users_by_plan(db, plan_id=plan_id)
    # if users_on_plan:
    #     raise HTTPException(status_code=400, detail="Cannot delete plan with assigned users.")
    plan_service.delete_plan(db=db, db_plan=db_plan)
    return {"message": "Plan deleted successfully"}

