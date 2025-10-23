from typing import Dict, Any, List, Optional
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.status_transition import StatusTransition
from app.models.user import User
from app.models.user_role import UserRole
from app.models.role import Role


class StatusTransitionValidationError(Exception):
    """
    Исключение для ошибок валидации переходов статусов.
    """
    pass


async def validate_status_transition(
    db: AsyncSession,
    from_status_id: UUID,
    to_status_id: UUID,
    user: User,
    entity_data: Optional[Dict[str, Any]] = None,
    comment: Optional[str] = None
) -> StatusTransition:
    """
    Валидация перехода между статусами.
    
    Args:
        db: Сессия БД
        from_status_id: ID текущего статуса
        to_status_id: ID целевого статуса
        user: Пользователь, выполняющий переход
        entity_data: Данные сущности для проверки обязательных полей
        comment: Комментарий к переходу (если требуется)
    
    Returns:
        StatusTransition: Объект перехода
    
    Raises:
        HTTPException: Если переход не разрешен
    """
    if from_status_id == to_status_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot transition to the same status"
        )
    
    result = await db.execute(
        select(StatusTransition)
        .where(StatusTransition.from_status_id == from_status_id)
        .where(StatusTransition.to_status_id == to_status_id)
    )
    
    transition = result.scalar_one_or_none()
    
    if transition is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Transition from status {from_status_id} to {to_status_id} is not allowed"
        )
    
    if transition.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This transition has been deleted"
        )
    
    await validate_required_roles(db, transition, user)
    
    if entity_data is not None:
        await validate_required_fields(transition, entity_data)
    
    if transition.require_comment and not comment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comment is required for this transition"
        )
    
    return transition


async def validate_required_roles(
    db: AsyncSession,
    transition: StatusTransition,
    user: User
) -> None:
    """
    Проверка наличия необходимых ролей у пользователя.
    
    Args:
        db: Сессия БД
        transition: Объект перехода
        user: Пользователь
    
    Raises:
        HTTPException: Если у пользователя нет необходимых ролей
    """
    if user.is_superuser:
        return
    
    if transition.required_roles is None or len(transition.required_roles) == 0:
        return
    
    user_role_ids = await get_user_role_ids(db, user.id)
    
    required_role_ids = [UUID(role_id) for role_id in transition.required_roles]
    
    has_required_role = any(role_id in user_role_ids for role_id in required_role_ids)
    
    if not has_required_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have the required roles to perform this transition"
        )


async def validate_required_fields(
    transition: StatusTransition,
    entity_data: Dict[str, Any]
) -> None:
    """
    Проверка заполнения обязательных полей.
    
    Args:
        transition: Объект перехода
        entity_data: Данные сущности
    
    Raises:
        HTTPException: Если не заполнены обязательные поля
    """
    if transition.required_fields is None or len(transition.required_fields) == 0:
        return
    
    missing_fields = []
    
    for field_name in transition.required_fields:
        if field_name not in entity_data or entity_data[field_name] is None:
            missing_fields.append(field_name)
    
    if missing_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Required fields are missing: {', '.join(missing_fields)}"
        )


async def get_user_role_ids(
    db: AsyncSession,
    user_id: UUID
) -> List[UUID]:
    """
    Получить список ID ролей пользователя.
    
    Args:
        db: Сессия БД
        user_id: ID пользователя
    
    Returns:
        List[UUID]: Список ID ролей
    """
    result = await db.execute(
        select(UserRole.role_id)
        .where(UserRole.user_id == user_id)
    )
    
    return list(result.scalars().all())


async def get_allowed_transitions(
    db: AsyncSession,
    from_status_id: UUID,
    user: User
) -> List[StatusTransition]:
    """
    Получить список разрешенных переходов из текущего статуса для пользователя.
    
    Args:
        db: Сессия БД
        from_status_id: ID текущего статуса
        user: Пользователь
    
    Returns:
        List[StatusTransition]: Список разрешенных переходов
    """
    result = await db.execute(
        select(StatusTransition)
        .where(StatusTransition.from_status_id == from_status_id)
        .where(StatusTransition.deleted_at.is_(None))
    )
    
    all_transitions = list(result.scalars().all())
    
    if user.is_superuser:
        return all_transitions
    
    user_role_ids = await get_user_role_ids(db, user.id)
    
    allowed_transitions = []
    
    for transition in all_transitions:
        if transition.required_roles is None or len(transition.required_roles) == 0:
            allowed_transitions.append(transition)
        else:
            required_role_ids = [UUID(role_id) for role_id in transition.required_roles]
            has_required_role = any(role_id in user_role_ids for role_id in required_role_ids)
            
            if has_required_role:
                allowed_transitions.append(transition)
    
    return allowed_transitions

