from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from app.core.models import Like, User, Post
from app.core.schemas import User
from typing import List
from fastapi import HTTPException

async def get_likers(db: AsyncSession, post_id: int, skip: int = 0, limit: int = 100):
    result = await db.execute(
        select(User)
        .join(Like, Like.user_id == User.id)
        .where(Like.post_id == post_id)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def toggle_like(db: AsyncSession, user_id: int, post_id: int):
    # Проверка существования поста
    post = await db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    existing_like = await db.execute(
        select(Like)
        .where(Like.user_id == user_id, Like.post_id == post_id)
    )
    existing_like = existing_like.scalar()
    
    if existing_like:
        await db.delete(existing_like)
        await db.commit()
        return "unliked"
    
    new_like = Like(user_id=user_id, post_id=post_id)
    db.add(new_like)
    await db.commit()
    return "liked"