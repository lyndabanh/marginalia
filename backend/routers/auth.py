import os

import bcrypt
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, status
from jose import jwt
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from models import User

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

router = APIRouter(prefix="/auth", tags=["auth"])

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

@router.post("/register", response_model=TokenResponse)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    query = select(User).where(User.email == request.email)
    user = db.scalars(query).first()

    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    user = User(
        name=request.name,
        email=request.email,
        password_hash=bcrypt.hashpw(request.password.encode(), bcrypt.gensalt()).decode()
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    jwt_token = jwt.encode(
        {"sub": str(user.id)},
        SECRET_KEY,
        algorithm="HS256"
    )

    return TokenResponse(access_token=jwt_token)

@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    query = select(User).where(User.email == request.email)
    user = db.scalars(query).first()
    
    if not user or not bcrypt.checkpw(request.password.encode(), user.password_hash.encode()):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    jwt_token = jwt.encode(
        {"sub": str(user.id)},
        SECRET_KEY,
        algorithm="HS256"
    )

    return TokenResponse(access_token=jwt_token)
