# Placeholder for user-related service functions
# e.g., get_user_by_email, create_user, update_user, authenticate_user

from sqlmodel import Session, select
from typing import Optional

from ..models.user import User, UserCreate
from ..core.security import get_password_hash, verify_password

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    statement = select(User).where(User.email == email)
    user = db.exec(statement).first()
    return user

def create_user(db: Session, user: UserCreate) -> User:
    hashed_password = get_password_hash(user.password)
    # Create a dictionary excluding the plain password
    user_data = user.model_dump(exclude={"password"})
    db_user = User(**user_data, hashed_password=hashed_password)
    # Set default plan or handle plan_id assignment if needed
    # db_user.plan_id = get_default_plan_id(db) # Example
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = get_user_by_email(db, email=email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

