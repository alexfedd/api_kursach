from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.ext.asyncio import AsyncSession

import os
import uuid
from sqlalchemy import select, exists, and_, literal

from app.core import database, models, schemas
from app.dependencies import auth

from typing import Optional

router = APIRouter()

AVATAR_DIR = "media/avatars/"
BANNER_DIR = "media/banners/"


os.makedirs(AVATAR_DIR, exist_ok=True)
os.makedirs(BANNER_DIR, exist_ok=True)




router = APIRouter()

@router.get("/users", response_model=schemas.UsersResponse2)
async def get_users_list(
    db: AsyncSession = Depends(database.get_db),
    current_user: Optional[models.User] = Depends(auth.get_current_user_optional)
):
    try:
        query = select(
            models.User.id,
            models.User.username,
            models.User.tag,
            models.User.avatar
        )

        if current_user:
            query = query.where(models.User.id != current_user.id)
            
            is_following_expr = exists().where(
                and_(
                    models.Follow.follower_id == current_user.id,
                    models.Follow.followed_id == models.User.id
                )
            ).label("is_following")
        else:
            
            is_following_expr = literal(False).label("is_following")

        
        query = query.add_columns(is_following_expr)
        
        result = await db.execute(query)
        users = result.mappings().all()
        
        response = {
            "users": users,
            "is_authenticated": current_user is not None
        }

        return response

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

@router.get("/user/{user_id}", response_model=schemas.UserResponse)
async def get_user_profile_data(
    user_id: int,
    db: AsyncSession = Depends(database.get_db),
):
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    db_user = result.scalars().first()
    
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    
    return schemas.UserResponse.model_validate(db_user)

@router.patch("/user")
async def update_profile(
    username: str | None = Form(default=None),
    email: str | None = Form(default=None),
    description: str | None = Form(default=None),
    address: str | None = Form(default=None),
    avatar: UploadFile | None = File(default=None),
    banner: UploadFile | None = File(default=None),
    db: AsyncSession = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    result = await db.execute(select(models.User).where(models.User.id == current_user.id))
    db_user = result.scalars().first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    updated_fields = {}
    
    if username is not None:
        db_user.username = username
        updated_fields["username"] = username
    if email is not None:
        db_user.email = email
        updated_fields["email"] = email
    if description is not None:
        db_user.description = description
        updated_fields["description"] = description
    if address is not None:
        db_user.address = address
        updated_fields["address"] = address

    if avatar is not None:
        avatar_filename = f"{uuid.uuid4()}_{avatar.filename}"
        avatar_path = os.path.join(AVATAR_DIR, avatar_filename)
        with open(avatar_path, "wb") as f:
            f.write(await avatar.read())
        db_user.avatar = avatar_path
        updated_fields["avatar"] = avatar_path
    
    if banner is not None:
        banner_filename = f"{uuid.uuid4()}_{banner.filename}"
        banner_path = os.path.join(BANNER_DIR, banner_filename)
        with open(banner_path, "wb") as f:
            f.write(await banner.read())
        db_user.banner = banner_path
        updated_fields["banner"] = banner_path
    
    await db.commit()
    await db.refresh(db_user)
    
    return updated_fields
