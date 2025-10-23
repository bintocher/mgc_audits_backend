from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.core.dependencies import get_current_user
from app.models.user import User
from app.crud import audit_component as crud_audit_component
from app.schemas.audit_component import (
    AuditComponentCreate,
    AuditComponentUpdate,
    AuditComponentResponse
)


router = APIRouter(prefix="/audit_components", tags=["audit_components"])


@router.get("/", response_model=List[AuditComponentResponse])
async def get_audit_components(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    audit_id: Optional[UUID] = None,
    component_type: Optional[str] = None,
    sap_id: Optional[str] = None,
    part_number: Optional[str] = None,
    db: AsyncSession = Depends(get_session)
):
    """
    Получить список компонентов аудитов с пагинацией и фильтрацией.
    
    Args:
        skip: Количество записей для пропуска
        limit: Максимальное количество записей для возврата (1-100)
        audit_id: Фильтр по аудиту
        component_type: Фильтр по типу компонента
        sap_id: Фильтр по SAP ID
        part_number: Фильтр по номеру детали
        db: Сессия базы данных
    
    Returns:
        Список компонентов аудитов
    """
    components = await crud_audit_component.get_audit_components(
        db=db,
        skip=skip,
        limit=limit,
        audit_id=audit_id,
        component_type=component_type,
        sap_id=sap_id,
        part_number=part_number
    )
    return components


@router.post("/", response_model=AuditComponentResponse, status_code=status.HTTP_201_CREATED)
async def create_audit_component(
    component: AuditComponentCreate,
    db: AsyncSession = Depends(get_session)
):
    """
    Создать новый компонент аудита.
    
    Args:
        component: Данные для создания компонента
        db: Сессия базы данных
    
    Returns:
        Созданный компонент
    
    Raises:
        HTTPException: Если произошла ошибка при создании
    """
    return await crud_audit_component.create_audit_component(db=db, component=component)


@router.get("/{component_id}", response_model=AuditComponentResponse)
async def get_audit_component(
    component_id: UUID,
    db: AsyncSession = Depends(get_session)
):
    """
    Получить информацию о компоненте аудита по ID.
    
    Args:
        component_id: UUID компонента
        db: Сессия базы данных
    
    Returns:
        Информация о компоненте
    
    Raises:
        HTTPException: Если компонент не найден
    """
    component = await crud_audit_component.get_audit_component(db, component_id)
    if not component:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit component not found"
        )
    return component


@router.put("/{component_id}", response_model=AuditComponentResponse)
async def update_audit_component(
    component_id: UUID,
    component_update: AuditComponentUpdate,
    db: AsyncSession = Depends(get_session)
):
    """
    Обновить информацию о компоненте аудита.
    
    Args:
        component_id: UUID компонента
        component_update: Данные для обновления
        db: Сессия базы данных
    
    Returns:
        Обновленная информация о компоненте
    
    Raises:
        HTTPException: Если компонент не найден
    """
    updated_component = await crud_audit_component.update_audit_component(db, component_id, component_update)
    if not updated_component:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit component not found"
        )
    return updated_component


@router.delete("/{component_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_audit_component(
    component_id: UUID,
    db: AsyncSession = Depends(get_session)
):
    """
    Деактивировать компонент аудита (мягкое удаление).
    
    Args:
        component_id: UUID компонента
        db: Сессия базы данных
    
    Raises:
        HTTPException: Если компонент не найден
    """
    success = await crud_audit_component.delete_audit_component(db, component_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit component not found"
        )


@router.get("/audits/{audit_id}/components", response_model=List[AuditComponentResponse])
async def get_audit_components_by_audit(
    audit_id: UUID,
    db: AsyncSession = Depends(get_session)
):
    """
    Получить список компонентов для конкретного аудита.
    
    Args:
        audit_id: UUID аудита
        db: Сессия базы данных
    
    Returns:
        Список компонентов аудита
    """
    components = await crud_audit_component.get_audit_components(
        db=db,
        audit_id=audit_id
    )
    return components

