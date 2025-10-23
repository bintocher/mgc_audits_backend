from typing import Optional, List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.dictionary import DictionaryType, Dictionary
from app.schemas.dictionary import DictionaryTypeCreate, DictionaryTypeUpdate, DictionaryCreate, DictionaryUpdate


async def create_dictionary_type(db: AsyncSession, dictionary_type: DictionaryTypeCreate) -> DictionaryType:
    db_dictionary_type = DictionaryType(
        name=dictionary_type.name,
        code=dictionary_type.code,
        description=dictionary_type.description
    )
    db.add(db_dictionary_type)
    await db.commit()
    await db.refresh(db_dictionary_type)
    return db_dictionary_type


async def get_dictionary_type(db: AsyncSession, dictionary_type_id: UUID) -> Optional[DictionaryType]:
    stmt = select(DictionaryType).where(DictionaryType.id == dictionary_type_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_dictionary_type_by_code(db: AsyncSession, code: str) -> Optional[DictionaryType]:
    stmt = select(DictionaryType).where(DictionaryType.code == code)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_dictionary_types(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100
) -> List[DictionaryType]:
    stmt = select(DictionaryType).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def update_dictionary_type(
    db: AsyncSession,
    dictionary_type_id: UUID,
    dictionary_type_update: DictionaryTypeUpdate
) -> Optional[DictionaryType]:
    db_dictionary_type = await get_dictionary_type(db, dictionary_type_id)
    if not db_dictionary_type:
        return None
    
    update_data = dictionary_type_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_dictionary_type, field, value)
    
    await db.commit()
    await db.refresh(db_dictionary_type)
    return db_dictionary_type


async def delete_dictionary_type(db: AsyncSession, dictionary_type_id: UUID) -> bool:
    db_dictionary_type = await get_dictionary_type(db, dictionary_type_id)
    if not db_dictionary_type:
        return False
    
    db_dictionary_type.soft_delete()
    await db.commit()
    return True


async def create_dictionary(db: AsyncSession, dictionary: DictionaryCreate) -> Dictionary:
    db_dictionary = Dictionary(
        dictionary_type_id=dictionary.dictionary_type_id,
        name=dictionary.name,
        code=dictionary.code,
        description=dictionary.description,
        enterprise_id=dictionary.enterprise_id,
        is_active=dictionary.is_active
    )
    db.add(db_dictionary)
    await db.commit()
    await db.refresh(db_dictionary)
    return db_dictionary


async def get_dictionary(db: AsyncSession, dictionary_id: UUID) -> Optional[Dictionary]:
    stmt = select(Dictionary).where(Dictionary.id == dictionary_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_dictionaries(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    dictionary_type_id: Optional[UUID] = None,
    enterprise_id: Optional[UUID] = None,
    is_active: Optional[bool] = None
) -> List[Dictionary]:
    stmt = select(Dictionary)
    
    if dictionary_type_id is not None:
        stmt = stmt.where(Dictionary.dictionary_type_id == dictionary_type_id)
    
    if enterprise_id is not None:
        stmt = stmt.where(Dictionary.enterprise_id == enterprise_id)
    
    if is_active is not None:
        stmt = stmt.where(Dictionary.is_active == is_active)
    
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def update_dictionary(
    db: AsyncSession,
    dictionary_id: UUID,
    dictionary_update: DictionaryUpdate
) -> Optional[Dictionary]:
    db_dictionary = await get_dictionary(db, dictionary_id)
    if not db_dictionary:
        return None
    
    update_data = dictionary_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_dictionary, field, value)
    
    await db.commit()
    await db.refresh(db_dictionary)
    return db_dictionary


async def delete_dictionary(db: AsyncSession, dictionary_id: UUID) -> bool:
    db_dictionary = await get_dictionary(db, dictionary_id)
    if not db_dictionary:
        return False
    
    db_dictionary.soft_delete()
    await db.commit()
    return True

