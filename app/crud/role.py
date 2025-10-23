from typing import Optional, List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.role import Role, Permission
from app.schemas.role import RoleCreate, RoleUpdate, PermissionCreate


async def create_role(db: AsyncSession, role: RoleCreate) -> Role:
    db_role = Role(
        name=role.name,
        code=role.code,
        description=role.description,
        is_system=role.is_system
    )
    db.add(db_role)
    await db.commit()
    await db.refresh(db_role)
    return db_role


async def get_role(db: AsyncSession, role_id: UUID) -> Optional[Role]:
    stmt = select(Role).where(Role.id == role_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_role_by_code(db: AsyncSession, code: str) -> Optional[Role]:
    stmt = select(Role).where(Role.code == code)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_roles(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    is_system: Optional[bool] = None
) -> List[Role]:
    stmt = select(Role)
    
    if is_system is not None:
        stmt = stmt.where(Role.is_system == is_system)
    
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def update_role(db: AsyncSession, role_id: UUID, role_update: RoleUpdate) -> Optional[Role]:
    db_role = await get_role(db, role_id)
    if not db_role:
        return None
    
    if db_role.is_system:
        return None
    
    update_data = role_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_role, field, value)
    
    await db.commit()
    await db.refresh(db_role)
    return db_role


async def delete_role(db: AsyncSession, role_id: UUID) -> bool:
    db_role = await get_role(db, role_id)
    if not db_role:
        return False
    
    if db_role.is_system:
        return False
    
    db_role.soft_delete()
    await db.commit()
    return True


async def create_permission(db: AsyncSession, permission: PermissionCreate, role_id: UUID) -> Permission:
    db_permission = Permission(
        role_id=role_id,
        enterprise_id=permission.enterprise_id,
        resource=permission.resource,
        action=permission.action
    )
    db.add(db_permission)
    await db.commit()
    await db.refresh(db_permission)
    return db_permission


async def get_permissions_by_role(db: AsyncSession, role_id: UUID) -> List[Permission]:
    stmt = select(Permission).where(Permission.role_id == role_id)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def delete_permission(db: AsyncSession, permission_id: UUID) -> bool:
    stmt = select(Permission).where(Permission.id == permission_id)
    result = await db.execute(stmt)
    db_permission = result.scalar_one_or_none()
    
    if not db_permission:
        return False
    
    await db.delete(db_permission)
    await db.commit()
    return True

