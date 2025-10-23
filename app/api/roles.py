from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.crud import role as crud_role
from app.schemas.role import RoleCreate, RoleUpdate, RoleResponse, PermissionCreate, PermissionResponse


router = APIRouter(prefix="/roles", tags=["roles"])


@router.get("/", response_model=List[RoleResponse])
async def get_roles(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    is_system: Optional[bool] = None,
    db: AsyncSession = Depends(get_session)
):
    """
    Получить список ролей с пагинацией и фильтрацией.
    
    Args:
        skip: Количество записей для пропуска
        limit: Максимальное количество записей для возврата (1-100)
        is_system: Фильтр по типу роли (системная/пользовательская)
        db: Сессия базы данных
    
    Returns:
        Список ролей
    """
    roles = await crud_role.get_roles(
        db=db,
        skip=skip,
        limit=limit,
        is_system=is_system
    )
    return roles


@router.post("/", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    role: RoleCreate,
    db: AsyncSession = Depends(get_session)
):
    """
    Создать новую роль.
    
    Args:
        role: Данные для создания роли
        db: Сессия базы данных
    
    Returns:
        Созданная роль
    
    Raises:
        HTTPException: Если роль с таким кодом уже существует
    """
    existing_role = await crud_role.get_role_by_code(db, role.code)
    if existing_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role with this code already exists"
        )
    
    return await crud_role.create_role(db=db, role=role)


@router.get("/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: UUID,
    db: AsyncSession = Depends(get_session)
):
    """
    Получить информацию о роли по ID.
    
    Args:
        role_id: UUID роли
        db: Сессия базы данных
    
    Returns:
        Информация о роли
    
    Raises:
        HTTPException: Если роль не найдена
    """
    role = await crud_role.get_role(db, role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    return role


@router.put("/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: UUID,
    role_update: RoleUpdate,
    db: AsyncSession = Depends(get_session)
):
    """
    Обновить информацию о роли.
    
    Args:
        role_id: UUID роли
        role_update: Данные для обновления
        db: Сессия базы данных
    
    Returns:
        Обновленная информация о роли
    
    Raises:
        HTTPException: Если роль не найдена или является системной
    """
    updated_role = await crud_role.update_role(db, role_id, role_update)
    if not updated_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found or is system role"
        )
    return updated_role


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_id: UUID,
    db: AsyncSession = Depends(get_session)
):
    """
    Деактивировать роль (мягкое удаление).
    
    Args:
        role_id: UUID роли
        db: Сессия базы данных
    
    Raises:
        HTTPException: Если роль не найдена или является системной
    """
    success = await crud_role.delete_role(db, role_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found or is system role"
        )


@router.get("/{role_id}/permissions", response_model=List[PermissionResponse])
async def get_role_permissions(
    role_id: UUID,
    db: AsyncSession = Depends(get_session)
):
    """
    Получить список прав для роли.
    
    Args:
        role_id: UUID роли
        db: Сессия базы данных
    
    Returns:
        Список прав роли
    
    Raises:
        HTTPException: Если роль не найдена
    """
    role = await crud_role.get_role(db, role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    permissions = await crud_role.get_permissions_by_role(db, role_id)
    return permissions


@router.post("/{role_id}/permissions", response_model=PermissionResponse, status_code=status.HTTP_201_CREATED)
async def create_permission(
    role_id: UUID,
    permission: PermissionCreate,
    db: AsyncSession = Depends(get_session)
):
    """
    Создать новое право для роли.
    
    Args:
        role_id: UUID роли
        permission: Данные для создания права
        db: Сессия базы данных
    
    Returns:
        Созданное право
    
    Raises:
        HTTPException: Если роль не найдена
    """
    role = await crud_role.get_role(db, role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    
    return await crud_role.create_permission(db, permission, role_id)

