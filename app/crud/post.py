from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.models import Post
from app.core.schemas import PostCreate

async def create_post(db: AsyncSession, post: PostCreate, author_id: int) -> Post:
    db_post = Post(content=post.content, author_id=author_id)
    db.add(db_post)
    await db.commit()
    await db.refresh(db_post)
    return db_post

async def get_posts(db: AsyncSession, skip: int = 0, limit: int = 10) -> list[Post]:
    result = await db.execute(select(Post).offset(skip).limit(limit))
    return result.scalars().all()