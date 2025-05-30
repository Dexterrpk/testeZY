# Placeholder for AI training data related service functions
# e.g., get_training_data, create_training_data, delete_training_data

from sqlmodel import Session, select
from typing import List, Optional

from ..models.ai_training import AiTrainingData, AiTrainingDataCreate
from ..models.user import User

def get_training_data_by_id(db: Session, data_id: int, owner_id: int) -> Optional[AiTrainingData]:
    # Ensure data belongs to the user requesting it
    statement = select(AiTrainingData).where(AiTrainingData.id == data_id, AiTrainingData.owner_id == owner_id)
    data = db.exec(statement).first()
    return data

def get_training_data_by_owner(db: Session, owner_id: int, skip: int = 0, limit: int = 100) -> List[AiTrainingData]:
    statement = select(AiTrainingData).where(AiTrainingData.owner_id == owner_id).offset(skip).limit(limit)
    data_list = db.exec(statement).all()
    return data_list

def create_training_data(db: Session, data_in: AiTrainingDataCreate, owner_id: int) -> AiTrainingData:
    # Ensure owner_id from input matches the one from the token/user later
    if data_in.owner_id != owner_id:
        raise ValueError("Owner ID mismatch")
    
    # Add check: Does user plan allow AI training?
    # user = db.get(User, owner_id)
    # if not user or not user.plan or not user.plan.allow_ai_training:
    #     raise HTTPException(status_code=403, detail="User plan does not allow AI training.")

    db_data = AiTrainingData.model_validate(data_in)
    db.add(db_data)
    db.commit()
    db.refresh(db_data)
    return db_data

def delete_training_data(db: Session, db_data: AiTrainingData):
    db.delete(db_data)
    db.commit()
    return {"ok": True}

# Add functions to retrieve formatted data for AI model training

