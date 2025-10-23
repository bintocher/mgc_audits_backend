from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.crud import user as crud_user
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserMeResponse
from app.models.user import User


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    is_active: Optional[bool] = None,
    location_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_session)
):
    """
    Получить список пользователей с пагинацией и фильтрацией.
    
    Args:
        skip: Количество записей для пропуска
        limit: Максимальное количество записей для возврата (1-100)
        is_active: Фильтр по статусу активности
        location_id: Фильтр по ID локации
        db: Сессия базы данных
    
    Returns:
        Список пользователей
    """
    users = await crud_user.get_users(
        db=db,
        skip=skip,
        limit=limit,
        is_active=is_active,
        location_id=location_id
    )
    return users


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_session)
):
    """
    Создать нового пользователя.
    
    Args:
        user: Данные для создания пользователя
        db: Сессия базы данных
    
    Returns:
        Созданный пользователь
    
    Raises:
        HTTPException: Если email или username уже заняты
    """
    existing_user = await crud_user.get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    existing_username = await crud_user.get_user_by_username(db, user.username)
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    return await crud_user.create_user(db=db, user=user)


@router.get("/me", response_model=UserMeResponse)
async def get_current_user_info(
    current_user: User = Depends(lambda: None)
):
    """
    Получить информацию о текущем авторизованном пользователе.
    
    Args:
        current_user: Текущий авторизованный пользователь
    
    Returns:
        Информация о текущем пользователе
    """
    return UserMeResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        first_name_ru=current_user.first_name_ru,
        last_name_ru=current_user.last_name_ru,
        patronymic_ru=current_user.patronymic_ru,
        first_name_en=current_user.first_name_en,
        last_name_en=current_user.last_name_en,
        location_id=current_user.location_id,
        language=current_user.language,
        is_auditor=current_user.is_auditor,
        is_expert=current_user.is_expert,
        is_active=current_user.is_active,
        is_staff=current_user.is_staff,
        is_superuser=current_user.is_superuser,
        telegram_linked=current_user.telegram_chat_id is not None,
        telegram_chat_id=current_user.telegram_chat_id
    )


@router.patch("/me", response_model=UserMeResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(lambda: None),
    db: AsyncSession = Depends(get_session)
):
    """
    Обновить информацию о текущем пользователе.
    
    Args:
        user_update: Данные для обновления
        current_user: Текущий авторизованный пользователь
        db: Сессия базы данных
    
    Returns:
        Обновленная информация о пользователе
    
    Raises:
        HTTPException: Если пользователь не найден
    """
    updated_user = await crud_user.update_user(db, current_user.id, user_update)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserMeResponse(
        id=updated_user.id,
        email=updated_user.email,
        username=updated_user.username,
        first_name_ru=updated_user.first_name_ru,
        last_name_ru=updated_user.last_name_ru,
        patronymic_ru=updated_user.patronymic_ru,
        first_name_en=updated_user.first_name_en,
        last_name_en=updated_user.last_name_en,
        location_id=updated_user.location_id,
        language=updated_user.language,
        is_auditor=updated_user.is_auditor,
        is_expert=updated_user.is_expert,
        is_active=updated_user.is_active,
        is_staff=updated_user.is_staff,
        is_superuser=updated_user.is_superuser,
        telegram_linked=updated_user.telegram_chat_id is not None,
        telegram_chat_id=updated_user.telegram_chat_id
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_session)
):
    """
    Получить информацию о пользователе по ID.
    
    Args:
        user_id: UUID пользователя
        db: Сессия базы данных
    
    Returns:
        Информация о пользователе
    
    Raises:
        HTTPException: Если пользователь не найден
    """
    user = await crud_user.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_session)
):
    """
    Обновить информацию о пользователе.
    
    Args:
        user_id: UUID пользователя
        user_update: Данные для обновления
        db: Сессия базы данных
    
    Returns:
        Обновленная информация о пользователе
    
    Raises:
        HTTPException: Если пользователь не найден
    """
    updated_user = await crud_user.update_user(db, user_id, user_update)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return updated_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_session)
):
    """
    Деактивировать пользователя (мягкое удаление).
    
    Args:
        user_id: UUID пользователя
        db: Сессия базы данных
    
    Raises:
        HTTPException: Если пользователь не найден
    """
    success = await crud_user.delete_user(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

