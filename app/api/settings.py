from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.crud import system_setting as crud_setting
from app.schemas.system_setting import SystemSettingCreate, SystemSettingUpdate, SystemSettingResponse
from app.models.user import User
from app.core.dependencies import get_current_user


router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("/", response_model=List[SystemSettingResponse])
async def get_settings(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    is_public: Optional[bool] = None,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Получить список настроек системы с пагинацией и фильтрацией.
    
    Args:
        skip: Количество записей для пропуска
        limit: Максимальное количество записей для возврата (1-100)
        category: Фильтр по категории настроек
        is_public: Фильтр по публичности настройки
        db: Сессия базы данных
        current_user: Текущий авторизованный пользователь
    
    Returns:
        Список настроек системы
    """
    settings = await crud_setting.get_system_settings(
        db=db,
        skip=skip,
        limit=limit,
        category=category,
        is_public=is_public
    )
    return settings


@router.get("/{key}", response_model=SystemSettingResponse)
async def get_setting_by_key(
    key: str,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Получить настройку по ключу.
    
    Args:
        key: Ключ настройки
        db: Сессия базы данных
        current_user: Текущий авторизованный пользователь
    
    Returns:
        Настройка системы
    """
    setting = await crud_setting.get_system_setting_by_key(db=db, key=key)
    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Setting not found"
        )
    return setting


@router.post("/", response_model=SystemSettingResponse, status_code=status.HTTP_201_CREATED)
async def create_setting(
    setting: SystemSettingCreate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Создать новую настройку системы.
    
    Args:
        setting: Данные для создания настройки
        db: Сессия базы данных
        current_user: Текущий авторизованный пользователь
    
    Returns:
        Созданная настройка
    """
    existing = await crud_setting.get_system_setting_by_key(db=db, key=setting.key)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Setting with this key already exists"
        )
    
    new_setting = await crud_setting.create_system_setting(
        db=db,
        setting=setting,
        updated_by_id=current_user.id
    )
    return new_setting


@router.put("/{key}", response_model=SystemSettingResponse)
async def update_setting(
    key: str,
    setting_update: SystemSettingUpdate,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Обновить настройку по ключу.
    
    Args:
        key: Ключ настройки
        setting_update: Данные для обновления
        db: Сессия базы данных
        current_user: Текущий авторизованный пользователь
    
    Returns:
        Обновленная настройка
    """
    setting = await crud_setting.get_system_setting_by_key(db=db, key=key)
    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Setting not found"
        )
    
    updated_setting = await crud_setting.update_system_setting(
        db=db,
        setting_id=setting.id,
        setting_update=setting_update,
        updated_by_id=current_user.id
    )
    return updated_setting


@router.delete("/{key}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_setting(
    key: str,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Удалить настройку по ключу (мягкое удаление).
    
    Args:
        key: Ключ настройки
        db: Сессия базы данных
        current_user: Текущий авторизованный пользователь
    """
    setting = await crud_setting.get_system_setting_by_key(db=db, key=key)
    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Setting not found"
        )
    
    await crud_setting.delete_system_setting(db=db, setting_id=setting.id)

