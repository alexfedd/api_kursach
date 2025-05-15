from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.models import Follow

async def follow_user(db: AsyncSession, follower_id: int, followed_id: int) -> Follow:
    follow = Follow(follower_id=follower_id, followed_id=followed_id)
    db.add(follow)
    await db.commit()
    await db.refresh(follow)
    return follow

async def unfollow_user(db: AsyncSession, follower_id: int, followed_id: int) -> bool:
    follow = await db.execute(
        select(Follow).filter(Follow.follower_id == follower_id, Follow.followed_id == followed_id)
    )
    follow = follow.scalars().first()
    if not follow:
        return False
    await db.delete(follow)
    await db.commit()
    return True

async def get_followers(db: AsyncSession, user_id: int) -> list[Follow]:
    result = await db.execute(select(Follow).filter(Follow.followed_id == user_id))
    return result.scalars().all()

async def get_following(db: AsyncSession, user_id: int) -> list[Follow]:
    result = await db.execute(select(Follow).filter(Follow.follower_id == user_id))
    return result.scalars().all()