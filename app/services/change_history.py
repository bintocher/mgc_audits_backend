from typing import Optional, Any, Dict
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.change_history import log_change


async def log_entity_changes(
    db: AsyncSession,
    entity_type: str,
    entity_id: UUID,
    user_id: UUID,
    old_data: Dict[str, Any],
    new_data: Dict[str, Any],
    exclude_fields: Optional[list] = None
) -> None:
    """
    Централизованное логирование изменений сущности.
    
    Args:
        db: Сессия базы данных
        entity_type: Тип сущности (например, 'audit', 'finding')
        entity_id: ID сущности
        user_id: ID пользователя, внесшего изменения
        old_data: Словарь старых значений полей
        new_data: Словарь новых значений полей
        exclude_fields: Список полей, которые не нужно логировать
    """
    if exclude_fields is None:
        exclude_fields = ['id', 'created_at', 'updated_at', 'deleted_at']
    
    all_fields = set(old_data.keys()) | set(new_data.keys())
    
    for field in all_fields:
        if field in exclude_fields:
            continue
        
        old_value = old_data.get(field)
        new_value = new_data.get(field)
        
        # Сравниваем значения
        if old_value != new_value:
            # Преобразуем значения в строки для хранения
            old_str = str(old_value) if old_value is not None else None
            new_str = str(new_value) if new_value is not None else None
            
            await log_change(
                db=db,
                entity_type=entity_type,
                entity_id=entity_id,
                user_id=user_id,
                field_name=field,
                old_value=old_str,
                new_value=new_str
            )

