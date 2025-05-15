from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.models import User
from app.core.schemas import UserCreate, UserUpdate
from app.dependencies.auth import get_password_hash
from starlette.status import HTTP_200_OK

async def get_user_by_username(db: AsyncSession, username: str) -> User:
    result = await db.execute(select(User).filter(User.username == username))
    return result.scalars().first()

async def get_user_by_mail(db: AsyncSession, email: str) -> User:
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalars().first()

async def create_user(db: AsyncSession, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username, 
        tag=user.username,
        email=user.email, 
        hashed_password=hashed_password,
        #ctivation_code=user.activation_code,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return {"State": HTTP_200_OK, "Message": "User created successfully"}

async def update_user(db: AsyncSession, user_id: int, user_update: UserUpdate) -> User:
    db_user = await db.get(User, user_id)
    if not db_user:
        return None
    update_data = user_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def delete_user(db: AsyncSession, user_id: int) -> bool:
    db_user = await db.get(User, user_id)
    if not db_user:
        return False
    await db.delete(db_user)
    await db.commit()
    return True