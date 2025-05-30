from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlmodel import Session

from ..core.database import get_session
from ..models.ai_training import AiTrainingData, AiTrainingDataCreate, AiTrainingDataRead
from ..models.user import User
from ..services import ai_training_service, plan_service # Added plan_service
# Import real dependency
from ..core.dependencies import get_current_active_user

router = APIRouter()

# Helper function to check AI training permission
def check_ai_training_permission(db: Session, user: User):
    # Fetch user with plan details for checks
    user_with_plan = db.get(User, user.id) # Get user again to potentially refresh relationships
    if user_with_plan and user_with_plan.plan_id:
        user_with_plan.plan = plan_service.get_plan(db, plan_id=user_with_plan.plan_id)
        if not user_with_plan.plan or not user_with_plan.plan.allow_ai_training:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Seu plano ({user_with_plan.plan.name if user_with_plan.plan else 'N/A'}) não permite o treinamento da IA."
            )
    else:
         # Handle case where user might not have a plan assigned
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuário sem plano associado ou plano inválido.")

@router.post("/", response_model=AiTrainingDataRead, status_code=status.HTTP_201_CREATED)
def create_training_data(
    *, 
    db: Session = Depends(get_session), 
    data_in: AiTrainingDataCreate,
    current_user: User = Depends(get_current_active_user) # Use real dependency
):
    """
    Create new AI training data entry for the current user.
    """
    # Ensure the owner_id in the payload matches the current user
    if data_in.owner_id != current_user.id:
         raise HTTPException(
             status_code=status.HTTP_403_FORBIDDEN,
             detail="Cannot create training data for another user."
         )
    
    # Check if user plan allows AI training
    check_ai_training_permission(db, current_user)

    data = ai_training_service.create_training_data(db=db, data_in=data_in, owner_id=current_user.id)
    return data

@router.get("/", response_model=List[AiTrainingDataRead])
def read_training_data(
    db: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user) # Use real dependency
):
    """
    Retrieve AI training data for the current user.
    """
    # Check if user plan allows AI training (viewing might be allowed even if creation isn't?)
    # check_ai_training_permission(db, current_user) # Decide if viewing needs permission check
    data_list = ai_training_service.get_training_data_by_owner(db, owner_id=current_user.id, skip=skip, limit=limit)
    return data_list

@router.get("/{data_id}", response_model=AiTrainingDataRead)
def read_single_training_data(
    *, 
    db: Session = Depends(get_session), 
    data_id: int,
    current_user: User = Depends(get_current_active_user) # Use real dependency
):
    """
    Get a specific AI training data entry by ID, owned by the current user.
    """
    # check_ai_training_permission(db, current_user) # Decide if viewing needs permission check
    data = ai_training_service.get_training_data_by_id(db, data_id=data_id, owner_id=current_user.id)
    if not data:
        raise HTTPException(status_code=404, detail="Training data not found or not owned by user")
    return data

@router.delete("/{data_id}", status_code=status.HTTP_200_OK)
def delete_training_data(
    *, 
    db: Session = Depends(get_session), 
    data_id: int,
    current_user: User = Depends(get_current_active_user) # Use real dependency
):
    """
    Delete AI training data owned by the current user.
    """
    # Check if user plan allows AI training (deletion might need permission?)
    # check_ai_training_permission(db, current_user)
    db_data = ai_training_service.get_training_data_by_id(db, data_id=data_id, owner_id=current_user.id)
    if not db_data:
        raise HTTPException(status_code=404, detail="Training data not found or not owned by user")
    ai_training_service.delete_training_data(db=db, db_data=db_data)
    return {"message": "AI training data deleted successfully"}

