from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from app.dependencies import auth
from app.core import models, database, schemas

router = APIRouter()

@router.post("/posts/{post_id}/like", response_model=schemas.LikeToggleResponse)
async def toggle_like(
    post_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: AsyncSession = Depends(database.get_db)
):
    # Проверяем существование поста
    post = await db.get(models.Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Проверяем, существует ли лайк
    result = await db.execute(
        select(models.Like).where(
            models.Like.user_id == current_user.id,
            models.Like.post_id == post_id
        )
    )
    like = result.scalar_one_or_none()

    if like:
        # Лайк существует, удаляем его
        await db.delete(like)
        await db.commit()
        return schemas.LikeToggleResponse(liked=False)
    else:
        # Лайка нет, создаем новый
        new_like = models.Like(user_id=current_user.id, post_id=post_id)
        db.add(new_like)
        try:
            await db.commit()
            return schemas.LikeToggleResponse(liked=True)
        except IntegrityError:
            await db.rollback()
            return schemas.LikeToggleResponse(liked=True)  # Лайк уже существует