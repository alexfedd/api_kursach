from fastapi import APIRouter, Depends, HTTPException, status, Form, Query, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.user import (
    get_user_by_username,
    get_user_by_mail,
    create_user,
)
from app.core import schemas
from app.dependencies.auth import create_access_token, verify_password
from app.core.database import get_db
from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import timedelta




class OAuth2PasswordRequestFormWithEmail(OAuth2PasswordRequestForm):
    def __init__(
        self,
        email: str = Form(...),  
        password: str = Form(...),
    ):
        super().__init__(username=email, password=password)


router = APIRouter()

@router.post("/register", response_model=schemas.DefaultResponse)
async def register(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    if await get_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    if await get_user_by_mail(db, user.email):
        raise HTTPException(status_code=400, detail="Mail already registered")

    return await create_user(db, user)

@router.post("/token", response_model=schemas.Token)
async def login(form_data: OAuth2PasswordRequestFormWithEmail = Depends(), db: AsyncSession = Depends(get_db)):
    user = await get_user_by_mail(db, form_data.username)  
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",  
            headers={"WWW-Authenticate": "Bearer"},
        )
    # if not user.activated:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Inactive user",
    #         headers={"WWW-Authenticate": "Bearer"},
    #     )
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {
        "access_token": access_token,
        "user_id": user.id
    }