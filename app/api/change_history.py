from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.core.dependencies import get_current_user
from app.models.user import User
from app.crud import change_history as crud_change_history
from app.schemas.change_history import ChangeHistoryResponse


router = APIRouter(prefix="/change_history", tags=["change_history"])


@router.get("/", response_model=List[ChangeHistoryResponse])
async def get_change_history_list(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    entity_type: Optional[str] = Query(None, description="Фильтр по типу сущности"),
    entity_id: Optional[UUID] = Query(None, description="Фильтр по ID сущности"),
    user_id: Optional[UUID] = Query(None, description="Фильтр по ID пользователя"),
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Получить список истории изменений с пагинацией и фильтрацией.
    
    Args:
        skip: Количество записей для пропуска
        limit: Максимальное количество записей для возврата (1-100)
        entity_type: Фильтр по типу сущности
        entity_id: Фильтр по ID сущности
        user_id: Фильтр по ID пользователя
        db: Сессия базы данных
        current_user: Текущий авторизованный пользователь
    
    Returns:
        Список записей истории изменений
    """
    history = await crud_change_history.get_change_history_list(
        db=db,
        skip=skip,
        limit=limit,
        entity_type=entity_type,
        entity_id=entity_id,
        user_id=user_id
    )
    return history


@router.get("/{change_id}", response_model=ChangeHistoryResponse)
async def get_change_history(
    change_id: UUID,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Получить информацию о записи истории изменений по ID.
    
    Args:
        change_id: UUID записи истории изменений
        db: Сессия базы данных
        current_user: Текущий авторизованный пользователь
    
    Returns:
        Информация о записи истории изменений
    
    Raises:
        HTTPException: Если запись не найдена
    """
    change = await crud_change_history.get_change_history(db, change_id)
    if not change:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Change history not found"
        )
    return change

