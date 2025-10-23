from typing import List, Optional
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.user import User
from app.models.user_role import UserRole
from app.models.role import Role, Permission
from app.api.auth import get_current_user


async def check_permission(
    resource: str,
    action: str,
    enterprise_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Проверка прав доступа пользователя.
    
    Args:
        resource: Ресурс (например, 'audit', 'finding')
        action: Действие (например, 'create', 'read', 'update', 'delete')
        enterprise_id: ID предприятия для ограничения области действия
        current_user: Текущий пользователь
        db: Сессия БД
    
    Returns:
        User: Текущий пользователь
    
    Raises:
        HTTPException: Если у пользователя нет прав
    """
    if current_user.is_superuser:
        return current_user
    
    result = await db.execute(
        select(UserRole)
        .where(UserRole.user_id == current_user.id)
        .join(Role)
        .join(Permission)
        .where(Permission.resource == resource)
        .where(Permission.action == action)
    )
    
    user_role = result.scalar_one_or_none()
    
    if user_role is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"No permission to {action} {resource}"
        )
    
    if enterprise_id is not None and user_role.enterprise_id is not None:
        if str(user_role.enterprise_id) != enterprise_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"No permission to {action} {resource} for this enterprise"
            )
    
    return current_user


async def require_staff(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Требует, чтобы пользователь был staff.
    """
    if not current_user.is_staff and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requires staff privileges"
        )
    return current_user


async def require_superuser(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Требует, чтобы пользователь был superuser.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requires superuser privileges"
        )
    return current_user

