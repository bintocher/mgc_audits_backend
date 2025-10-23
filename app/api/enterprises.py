from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.crud import enterprise as crud_enterprise
from app.schemas.enterprise import EnterpriseCreate, EnterpriseUpdate, EnterpriseResponse


router = APIRouter(prefix="/enterprises", tags=["enterprises"])


@router.get("/", response_model=List[EnterpriseResponse])
async def get_enterprises(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_session)
):
    """
    Получить список предприятий с пагинацией и фильтрацией.
    
    Args:
        skip: Количество записей для пропуска
        limit: Максимальное количество записей для возврата (1-100)
        is_active: Фильтр по статусу активности
        db: Сессия базы данных
    
    Returns:
        Список предприятий
    """
    enterprises = await crud_enterprise.get_enterprises(
        db=db,
        skip=skip,
        limit=limit,
        is_active=is_active
    )
    return enterprises


@router.post("/", response_model=EnterpriseResponse, status_code=status.HTTP_201_CREATED)
async def create_enterprise(
    enterprise: EnterpriseCreate,
    db: AsyncSession = Depends(get_session)
):
    """
    Создать новое предприятие.
    
    Args:
        enterprise: Данные для создания предприятия
        db: Сессия базы данных
    
    Returns:
        Созданное предприятие
    
    Raises:
        HTTPException: Если предприятие с таким кодом уже существует
    """
    existing_enterprise = await crud_enterprise.get_enterprise_by_code(db, enterprise.code)
    if existing_enterprise:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Enterprise with this code already exists"
        )
    
    return await crud_enterprise.create_enterprise(db=db, enterprise=enterprise)


@router.get("/{enterprise_id}", response_model=EnterpriseResponse)
async def get_enterprise(
    enterprise_id: UUID,
    db: AsyncSession = Depends(get_session)
):
    """
    Получить информацию о предприятии по ID.
    
    Args:
        enterprise_id: UUID предприятия
        db: Сессия базы данных
    
    Returns:
        Информация о предприятии
    
    Raises:
        HTTPException: Если предприятие не найдено
    """
    enterprise = await crud_enterprise.get_enterprise(db, enterprise_id)
    if not enterprise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enterprise not found"
        )
    return enterprise


@router.put("/{enterprise_id}", response_model=EnterpriseResponse)
async def update_enterprise(
    enterprise_id: UUID,
    enterprise_update: EnterpriseUpdate,
    db: AsyncSession = Depends(get_session)
):
    """
    Обновить информацию о предприятии.
    
    Args:
        enterprise_id: UUID предприятия
        enterprise_update: Данные для обновления
        db: Сессия базы данных
    
    Returns:
        Обновленная информация о предприятии
    
    Raises:
        HTTPException: Если предприятие не найдено
    """
    updated_enterprise = await crud_enterprise.update_enterprise(db, enterprise_id, enterprise_update)
    if not updated_enterprise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enterprise not found"
        )
    return updated_enterprise


@router.delete("/{enterprise_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_enterprise(
    enterprise_id: UUID,
    db: AsyncSession = Depends(get_session)
):
    """
    Деактивировать предприятие (мягкое удаление).
    
    Args:
        enterprise_id: UUID предприятия
        db: Сессия базы данных
    
    Raises:
        HTTPException: Если предприятие не найдено
    """
    success = await crud_enterprise.delete_enterprise(db, enterprise_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enterprise not found"
        )

