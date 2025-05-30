from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlmodel import Session

from . import security
from .database import get_session
from ..models.user import User
from ..models.token import TokenData
from ..services import user_service

# This defines the URL where the client will send the username and password to get a token
# It doesn't create the endpoint itself, that's done in routes/auth.py
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{security.settings.API_V1_STR}/login/access-token")

def get_current_user(
    db: Session = Depends(get_session),
    token: str = Depends(oauth2_scheme)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = security.jwt.decode(
            token, security.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user = user_service.get_user_by_email(db, email=token_data.username)
    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def get_current_active_superuser(
    current_user: User = Depends(get_current_active_user)
) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user

# Function to get user with plan details for permission checks
def get_user_with_plan(db: Session, user_id: int) -> User | None:
    # This requires eager loading or a specific query if Plan is needed frequently
    # For simplicity, let's just get the user and assume plan_id is sufficient for now
    # or fetch the plan separately in the service/route where needed.
    # A more optimized way would be to join the tables if performance becomes an issue.
    user = db.get(User, user_id)
    if user and user.plan_id:
         # Eagerly load the plan relationship if defined correctly in the model
         # Or fetch it manually:
         user.plan = db.get(Plan, user.plan_id) # Assuming Plan model is imported
    return user

