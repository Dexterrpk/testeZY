from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlmodel import Session

from ..core.database import get_session
from ..models.user import User, UserCreate, UserRead, UserUpdate
from ..services import user_service
# Import real dependencies
from ..core.dependencies import get_current_active_user, get_current_active_superuser

router = APIRouter()

@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(
    *, 
    db: Session = Depends(get_session), 
    user_in: UserCreate,
    current_user: User = Depends(get_current_active_superuser) # Only superusers can create users for now
):
    """
    Create new user. (Requires superuser privileges)
    """
    user = user_service.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    # Add logic to assign a default plan if plan_id is not provided in user_in
    # or validate the provided plan_id
    user = user_service.create_user(db=db, user=user_in)
    return user

@router.get("/me", response_model=UserRead)
def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Get current logged-in user's details."""
    # Optionally enrich with plan details if needed frequently
    # user_with_plan = get_user_with_plan(db, current_user.id) # Requires db session
    return current_user

# Example: Get user by ID (restricted to superusers or self)
@router.get("/{user_id}", response_model=UserRead)
def read_user_by_id(
    user_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific user by id. (Requires superuser or self)"""
    if user_id == current_user.id:
        return current_user
    if not current_user.is_superuser:
         raise HTTPException(
             status_code=status.HTTP_403_FORBIDDEN, 
             detail="Not enough permissions to view other users"
         )
    
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Add endpoints for updating users (self or superuser), deleting (superuser)
# Remember to add permission checks based on current_user

