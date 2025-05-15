from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, delete, insert
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.models import User, Follow
from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.core import schemas

router = APIRouter()

@router.get("/follow/{user_id}/", response_model=dict)
async def get_follow_info(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    
    user = await db.execute(select(User).where(User.id == user_id))
    if not user.scalar():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )

    
    followed_query = (
        select(User)
        .join(Follow, User.id == Follow.followed_id)
        .where(Follow.follower_id == user_id)
    )
    followed_result = await db.execute(followed_query)
    followed_users = followed_result.scalars().all()

    
    followers_query = (
        select(User)
        .join(Follow, User.id == Follow.follower_id)
        .where(Follow.followed_id == user_id)
    )
    followers_result = await db.execute(followers_query)
    follower_users = followers_result.scalars().all()

    
    def convert_users(users):
        return [schemas.UserResponse.model_validate(user).model_dump() for user in users]

    return {
        "Following": {
            "count": len(followed_users),
            "persons": convert_users(followed_users)
        },
        "Followers": {
            "count": len(follower_users),
            "persons": convert_users(follower_users)
        }
    }

@router.post("/follow/{user_id}/", status_code=status.HTTP_200_OK)
async def toggle_follow(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя подписаться на самого себя"
        )
    
    
    target_user = await db.get(User, user_id)
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    
    existing_follow = await db.execute(
        select(Follow).where(
            Follow.follower_id == current_user.id,
            Follow.followed_id == user_id
        )
    )
    
    action = "followed"
    if existing_follow.scalar():
        
        await db.execute(
            delete(Follow).where(
                Follow.follower_id == current_user.id,
                Follow.followed_id == user_id
            )
        )
        action = "unfollowed"
    else:
        
        await db.execute(
            insert(Follow).values(
                follower_id=current_user.id,
                followed_id=user_id
            )
        )
    
    await db.commit()
    
    return {
        "status": "success",
        "action": action,
        "message": f"Successfully {action} user {target_user.username}"
    }