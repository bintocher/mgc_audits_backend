from typing import Optional, List
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.change_history import ChangeHistory
from app.schemas.change_history import ChangeHistoryCreate


async def create_change_history(db: AsyncSession, change: ChangeHistoryCreate) -> ChangeHistory:
    db_change = ChangeHistory(
        entity_type=change.entity_type,
        entity_id=change.entity_id,
        user_id=change.user_id,
        field_name=change.field_name,
        old_value=change.old_value,
        new_value=change.new_value,
        changed_at=change.changed_at
    )
    
    db.add(db_change)
    await db.commit()
    await db.refresh(db_change)
    return db_change


async def get_change_history(db: AsyncSession, change_id: UUID) -> Optional[ChangeHistory]:
    stmt = select(ChangeHistory).where(ChangeHistory.id == change_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_change_history_list(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    entity_type: Optional[str] = None,
    entity_id: Optional[UUID] = None,
    user_id: Optional[UUID] = None
) -> List[ChangeHistory]:
    stmt = select(ChangeHistory)
    
    if entity_type is not None:
        stmt = stmt.where(ChangeHistory.entity_type == entity_type)
    
    if entity_id is not None:
        stmt = stmt.where(ChangeHistory.entity_id == entity_id)
    
    if user_id is not None:
        stmt = stmt.where(ChangeHistory.user_id == user_id)
    
    stmt = stmt.order_by(ChangeHistory.changed_at.desc())
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def log_change(
    db: AsyncSession,
    entity_type: str,
    entity_id: UUID,
    user_id: UUID,
    field_name: str,
    old_value: Optional[str] = None,
    new_value: Optional[str] = None
) -> ChangeHistory:
    """
    Записать изменение в историю.
    
    Args:
        db: Сессия базы данных
        entity_type: Тип сущности
        entity_id: ID сущности
        user_id: ID пользователя
        field_name: Имя поля
        old_value: Старое значение
        new_value: Новое значение
    
    Returns:
        Созданная запись истории изменений
    """
    db_change = ChangeHistory(
        entity_type=entity_type,
        entity_id=entity_id,
        user_id=user_id,
        field_name=field_name,
        old_value=old_value,
        new_value=new_value,
        changed_at=datetime.now(timezone.utc)
    )
    
    db.add(db_change)
    await db.commit()
    await db.refresh(db_change)
    return db_change

