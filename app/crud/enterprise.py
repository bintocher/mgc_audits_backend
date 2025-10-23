from typing import Optional, List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.enterprise import Enterprise
from app.schemas.enterprise import EnterpriseCreate, EnterpriseUpdate


async def create_enterprise(db: AsyncSession, enterprise: EnterpriseCreate) -> Enterprise:
    db_enterprise = Enterprise(
        name=enterprise.name,
        code=enterprise.code,
        description=enterprise.description,
        is_active=enterprise.is_active
    )
    db.add(db_enterprise)
    await db.commit()
    await db.refresh(db_enterprise)
    return db_enterprise


async def get_enterprise(db: AsyncSession, enterprise_id: UUID) -> Optional[Enterprise]:
    stmt = select(Enterprise).where(Enterprise.id == enterprise_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_enterprise_by_code(db: AsyncSession, code: str) -> Optional[Enterprise]:
    stmt = select(Enterprise).where(Enterprise.code == code)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_enterprises(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None
) -> List[Enterprise]:
    stmt = select(Enterprise)
    
    if is_active is not None:
        stmt = stmt.where(Enterprise.is_active == is_active)
    
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def update_enterprise(
    db: AsyncSession,
    enterprise_id: UUID,
    enterprise_update: EnterpriseUpdate
) -> Optional[Enterprise]:
    db_enterprise = await get_enterprise(db, enterprise_id)
    if not db_enterprise:
        return None
    
    update_data = enterprise_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_enterprise, field, value)
    
    await db.commit()
    await db.refresh(db_enterprise)
    return db_enterprise


async def delete_enterprise(db: AsyncSession, enterprise_id: UUID) -> bool:
    db_enterprise = await get_enterprise(db, enterprise_id)
    if not db_enterprise:
        return False
    
    db_enterprise.soft_delete()
    await db.commit()
    return True

