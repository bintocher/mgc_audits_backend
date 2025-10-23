from typing import Optional, List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash


async def create_user(db: AsyncSession, user: UserCreate) -> User:
    db_user = User(
        email=user.email,
        username=user.username,
        first_name_ru=user.first_name_ru,
        last_name_ru=user.last_name_ru,
        patronymic_ru=user.patronymic_ru,
        first_name_en=user.first_name_en,
        last_name_en=user.last_name_en,
        location_id=user.location_id,
        language=user.language,
        is_auditor=user.is_auditor,
        is_expert=user.is_expert,
        is_active=user.is_active,
        is_staff=user.is_staff,
        is_superuser=user.is_superuser,
        password_hash=get_password_hash(user.password)
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def get_user(db: AsyncSession, user_id: UUID) -> Optional[User]:
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_users(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    location_id: Optional[UUID] = None
) -> List[User]:
    stmt = select(User)
    
    if is_active is not None:
        stmt = stmt.where(User.is_active == is_active)
    
    if location_id is not None:
        stmt = stmt.where(User.location_id == location_id)
    
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def update_user(db: AsyncSession, user_id: UUID, user_update: UserUpdate) -> Optional[User]:
    db_user = await get_user(db, user_id)
    if not db_user:
        return None
    
    update_data = user_update.model_dump(exclude_unset=True)
    
    if "password" in update_data:
        update_data["password_hash"] = get_password_hash(update_data.pop("password"))
    
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def delete_user(db: AsyncSession, user_id: UUID) -> bool:
    db_user = await get_user(db, user_id)
    if not db_user:
        return False
    
    db_user.soft_delete()
    await db.commit()
    return True


async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[User]:
    user = await get_user_by_email(db, email)
    if not user:
        return None
    
    if not user.is_active:
        return None
    
    from app.core.security import verify_password
    
    if not verify_password(password, user.password_hash):
        return None
    
    return user

