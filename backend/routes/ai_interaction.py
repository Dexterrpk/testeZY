from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from pydantic import BaseModel

from ..core.database import get_session
from ..models.user import User
from ..services import ai_service, plan_service # Added plan_service
# Import real dependency
from ..core.dependencies import get_current_active_user

router = APIRouter()

class AIChatRequest(BaseModel):
    query: str

class AIChatResponse(BaseModel):
    response: str

# Helper function to check AI interaction permission (similar to training)
def check_ai_interaction_permission(db: Session, user: User):
    # Fetch user with plan details for checks
    user_with_plan = db.get(User, user.id) # Get user again to potentially refresh relationships
    if user_with_plan and user_with_plan.plan_id:
        user_with_plan.plan = plan_service.get_plan(db, plan_id=user_with_plan.plan_id)
        # Check if the plan allows AI features (using allow_ai_training as a proxy for now)
        # You might want a more specific flag like 'allow_ai_interaction' in the Plan model
        if not user_with_plan.plan or not user_with_plan.plan.allow_ai_training: 
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Seu plano ({user_with_plan.plan.name if user_with_plan.plan else 'N/A'}) não permite interação com a IA."
            )
    else:
         # Handle case where user might not have a plan assigned
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuário sem plano associado ou plano inválido.")

@router.post("/chat", response_model=AIChatResponse)
def handle_ai_chat(
    *, 
    db: Session = Depends(get_session), 
    request: AIChatRequest,
    current_user: User = Depends(get_current_active_user) # Use real dependency
):
    """
    Handles a chat interaction with the AI for the current user.
    Retrieves context from user's training data and gets a response from the AI model.
    """
    # Check if user plan allows AI interaction
    check_ai_interaction_permission(db, current_user)

    if not request.query:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Query cannot be empty.")

    ai_response_text = ai_service.get_ai_response(db=db, user_query=request.query, owner_id=current_user.id)
    
    return AIChatResponse(response=ai_response_text)

