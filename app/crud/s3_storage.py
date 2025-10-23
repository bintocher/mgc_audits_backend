from typing import Optional, List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.s3_storage import S3Storage
from app.schemas.s3_storage import S3StorageCreate, S3StorageUpdate
from app.core.security import encrypt_value, decrypt_value


async def create_s3_storage(db: AsyncSession, storage: S3StorageCreate) -> S3Storage:
    db_storage = S3Storage(
        name=storage.name,
        endpoint_url=storage.endpoint_url,
        region=storage.region,
        access_key_id=encrypt_value(storage.access_key_id),
        secret_access_key=encrypt_value(storage.secret_access_key),
        bucket_name=storage.bucket_name,
        prefix=storage.prefix,
        enterprise_id=storage.enterprise_id,
        division_id=storage.division_id,
        is_default=storage.is_default,
        is_active=storage.is_active
    )
    db.add(db_storage)
    await db.commit()
    await db.refresh(db_storage)
    return db_storage


async def get_s3_storage(db: AsyncSession, storage_id: UUID) -> Optional[S3Storage]:
    stmt = select(S3Storage).where(S3Storage.id == storage_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_s3_storages(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    enterprise_id: Optional[UUID] = None,
    division_id: Optional[UUID] = None,
    is_active: Optional[bool] = None
) -> List[S3Storage]:
    stmt = select(S3Storage)
    
    if enterprise_id is not None:
        stmt = stmt.where(S3Storage.enterprise_id == enterprise_id)
    
    if division_id is not None:
        stmt = stmt.where(S3Storage.division_id == division_id)
    
    if is_active is not None:
        stmt = stmt.where(S3Storage.is_active == is_active)
    
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def update_s3_storage(
    db: AsyncSession,
    storage_id: UUID,
    storage_update: S3StorageUpdate
) -> Optional[S3Storage]:
    db_storage = await get_s3_storage(db, storage_id)
    if not db_storage:
        return None
    
    update_data = storage_update.model_dump(exclude_unset=True)
    
    if "access_key_id" in update_data:
        update_data["access_key_id"] = encrypt_value(update_data["access_key_id"])
    
    if "secret_access_key" in update_data:
        update_data["secret_access_key"] = encrypt_value(update_data["secret_access_key"])
    
    for field, value in update_data.items():
        setattr(db_storage, field, value)
    
    await db.commit()
    await db.refresh(db_storage)
    return db_storage


async def delete_s3_storage(db: AsyncSession, storage_id: UUID) -> bool:
    db_storage = await get_s3_storage(db, storage_id)
    if not db_storage:
        return False
    
    db_storage.soft_delete()
    await db.commit()
    return True


async def get_default_s3_storage(db: AsyncSession) -> Optional[S3Storage]:
    stmt = select(S3Storage).where(S3Storage.is_default == True, S3Storage.is_active == True)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


def get_storage_credentials(db_storage: S3Storage) -> dict:
    return {
        "access_key_id": decrypt_value(db_storage.access_key_id),
        "secret_access_key": decrypt_value(db_storage.secret_access_key)
    }

