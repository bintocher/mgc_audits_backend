from typing import Optional, List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.system_setting import SystemSetting
from app.schemas.system_setting import SystemSettingCreate, SystemSettingUpdate
from app.core.security import encrypt_value, decrypt_value


async def create_system_setting(db: AsyncSession, setting: SystemSettingCreate, updated_by_id: Optional[UUID] = None) -> SystemSetting:
    db_setting = SystemSetting(
        key=setting.key,
        value=encrypt_value(setting.value) if setting.is_encrypted else setting.value,
        value_type=setting.value_type,
        description=setting.description,
        category=setting.category,
        is_public=setting.is_public,
        is_encrypted=setting.is_encrypted,
        updated_by_id=updated_by_id
    )
    db.add(db_setting)
    await db.commit()
    await db.refresh(db_setting)
    return db_setting


async def get_system_setting(db: AsyncSession, setting_id: UUID) -> Optional[SystemSetting]:
    stmt = select(SystemSetting).where(SystemSetting.id == setting_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_system_setting_by_key(db: AsyncSession, key: str) -> Optional[SystemSetting]:
    stmt = select(SystemSetting).where(SystemSetting.key == key)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_system_settings(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    is_public: Optional[bool] = None
) -> List[SystemSetting]:
    stmt = select(SystemSetting)
    
    if category is not None:
        stmt = stmt.where(SystemSetting.category == category)
    
    if is_public is not None:
        stmt = stmt.where(SystemSetting.is_public == is_public)
    
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def update_system_setting(
    db: AsyncSession,
    setting_id: UUID,
    setting_update: SystemSettingUpdate,
    updated_by_id: Optional[UUID] = None
) -> Optional[SystemSetting]:
    db_setting = await get_system_setting(db, setting_id)
    if not db_setting:
        return None
    
    update_data = setting_update.model_dump(exclude_unset=True)
    
    if "value" in update_data and db_setting.is_encrypted:
        update_data["value"] = encrypt_value(update_data["value"])
    
    if updated_by_id:
        update_data["updated_by_id"] = updated_by_id
    
    for field, value in update_data.items():
        setattr(db_setting, field, value)
    
    await db.commit()
    await db.refresh(db_setting)
    return db_setting


async def delete_system_setting(db: AsyncSession, setting_id: UUID) -> bool:
    db_setting = await get_system_setting(db, setting_id)
    if not db_setting:
        return False
    
    db_setting.soft_delete()
    await db.commit()
    return True


def get_setting_value(db_setting: SystemSetting) -> str:
    if db_setting.is_encrypted:
        return decrypt_value(db_setting.value)
    return db_setting.value

