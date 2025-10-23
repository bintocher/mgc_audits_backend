from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.core.dependencies import get_current_user
from app.models.user import User
from app.crud import api_token as crud_api_token
from app.schemas.api_token import (
    APITokenCreate,
    APITokenUpdate,
    APITokenResponse,
    APITokenCreateResponse
)


router = APIRouter(prefix="/api_tokens", tags=["api_tokens"])


@router.get("/", response_model=List[APITokenResponse])
async def get_api_tokens(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    user_id: Optional[UUID] = None,
    is_active: Optional[bool] = None,
    issued_for: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """
    Получить список API токенов с пагинацией и фильтрацией.
    
    Args:
        skip: Количество записей для пропуска
        limit: Максимальное количество записей для возврата (1-100)
        user_id: Фильтр по ID пользователя
        is_active: Фильтр по статусу активности
        issued_for: Фильтр по типу выдачи ('user' или 'system')
        current_user: Текущий пользователь
        db: Сессия базы данных
    
    Returns:
        Список API токенов
    
    Raises:
        HTTPException: Если пользователь не имеет прав администратора
    """
    if not current_user.is_staff and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для просмотра API токенов"
        )
    
    tokens = await crud_api_token.get_tokens(
        db=db,
        skip=skip,
        limit=limit,
        user_id=user_id,
        is_active=is_active,
        issued_for=issued_for
    )
    return tokens


@router.post("/", response_model=APITokenCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_api_token(
    token: APITokenCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """
    Создать новый API токен.
    
    Args:
        token: Данные для создания токена
        current_user: Текущий пользователь
        db: Сессия базы данных
    
    Returns:
        Созданный токен с plain_token
    
    Raises:
        HTTPException: Если пользователь не имеет прав администратора
    """
    if not current_user.is_staff and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для создания API токенов"
        )
    
    new_token, plain_token = await crud_api_token.create_token(
        db=db,
        name=token.name,
        user_id=token.user_id,
        permission_mode=token.permission_mode,
        custom_permissions=token.custom_permissions,
        rate_limit_per_minute=token.rate_limit_per_minute,
        rate_limit_per_hour=token.rate_limit_per_hour,
        expires_at=token.expires_at,
        issued_for=token.issued_for,
        allowed_ips=token.allowed_ips,
        description=token.description
    )
    
    response = APITokenCreateResponse(
        id=new_token.id,
        name=new_token.name,
        token_prefix=new_token.token_prefix,
        user_id=new_token.user_id,
        permission_mode=new_token.permission_mode,
        issued_for=new_token.issued_for,
        is_active=new_token.is_active,
        rate_limit_per_minute=new_token.rate_limit_per_minute,
        rate_limit_per_hour=new_token.rate_limit_per_hour,
        expires_at=new_token.expires_at,
        allowed_ips=new_token.allowed_ips,
        description=new_token.description,
        last_used_at=new_token.last_used_at,
        created_at=new_token.created_at,
        updated_at=new_token.updated_at,
        plain_token=plain_token
    )
    
    return response


@router.get("/{id}", response_model=APITokenResponse)
async def get_api_token(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """
    Получить API токен по ID.
    
    Args:
        id: ID токена
        current_user: Текущий пользователь
        db: Сессия базы данных
    
    Returns:
        API токен
    
    Raises:
        HTTPException: Если токен не найден или пользователь не имеет прав
    """
    if not current_user.is_staff and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для просмотра API токенов"
        )
    
    token = await crud_api_token.get_token(db=db, token_id=id)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API токен не найден"
        )
    return token


@router.put("/{id}", response_model=APITokenResponse)
async def update_api_token(
    id: UUID,
    token_update: APITokenUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """
    Обновить API токен.
    
    Args:
        id: ID токена
        token_update: Данные для обновления
        current_user: Текущий пользователь
        db: Сессия базы данных
    
    Returns:
        Обновленный токен
    
    Raises:
        HTTPException: Если токен не найден или пользователь не имеет прав
    """
    if not current_user.is_staff and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для обновления API токенов"
        )
    
    updated_token = await crud_api_token.update_token(
        db=db,
        token_id=id,
        token_update=token_update
    )
    
    if not updated_token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API токен не найден"
        )
    
    return updated_token


@router.post("/{id}/rotate", response_model=APITokenCreateResponse)
async def rotate_api_token(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """
    Ротация API токена (создание нового токена и отзыв старого).
    
    Args:
        id: ID токена
        current_user: Текущий пользователь
        db: Сессия базы данных
    
    Returns:
        Новый токен с plain_token
    
    Raises:
        HTTPException: Если токен не найден или пользователь не имеет прав
    """
    if not current_user.is_staff and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для ротации API токенов"
        )
    
    try:
        updated_token, plain_token = await crud_api_token.rotate_token(db=db, token_id=id)
        
        response = APITokenCreateResponse(
            id=updated_token.id,
            name=updated_token.name,
            token_prefix=updated_token.token_prefix,
            user_id=updated_token.user_id,
            permission_mode=updated_token.permission_mode,
            issued_for=updated_token.issued_for,
            is_active=updated_token.is_active,
            rate_limit_per_minute=updated_token.rate_limit_per_minute,
            rate_limit_per_hour=updated_token.rate_limit_per_hour,
            expires_at=updated_token.expires_at,
            allowed_ips=updated_token.allowed_ips,
            description=updated_token.description,
            last_used_at=updated_token.last_used_at,
            created_at=updated_token.created_at,
            updated_at=updated_token.updated_at,
            plain_token=plain_token
        )
        
        return response
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_token(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """
    Отозвать API токен (мягкое удаление).
    
    Args:
        id: ID токена
        current_user: Текущий пользователь
        db: Сессия базы данных
    
    Raises:
        HTTPException: Если токен не найден или пользователь не имеет прав
    """
    if not current_user.is_staff and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для отзыва API токенов"
        )
    
    success = await crud_api_token.delete_token(db=db, token_id=id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API токен не найден"
        )

