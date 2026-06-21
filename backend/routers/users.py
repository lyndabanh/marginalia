import bcrypt
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_current_user
from models import User
from schemas import BaseResponse, MessageResponse

router = APIRouter(prefix="/users", tags=["users"])

class UserPublicResponse(BaseResponse):
    name: str
    location: str | None = None
    avatar: str | None = None

class UserPrivateResponse(BaseResponse):
    name: str
    email: str
    location: str | None = None
    avatar: str | None = None
    created_at: datetime

class UserUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    location: str | None = None
    avatar: str | None = None    
    password: str | None = None

@router.get("/me", response_model=UserPrivateResponse)
def get_me(current_user: User = Depends(get_current_user)):   
    return current_user

@router.get("/{user_id}", response_model=UserPublicResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.scalars(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user

@router.put("/me", response_model=UserPrivateResponse)
def update_me(request: UserUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    updates = request.model_dump(exclude_unset=True)
    for field, value in updates.items():
        if field == "password":
            setattr(current_user, "password_hash", bcrypt.hashpw(value.encode(), bcrypt.gensalt()).decode())
        else:
            setattr(current_user, field, value)

    try:
        db.commit()
        db.refresh(current_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already in use"
        )
    
    return current_user

@router.delete("/me", response_model=MessageResponse)
def delete_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.delete(current_user)
    db.commit()
    
    return MessageResponse(message=f"{current_user.name} has been deleted")
