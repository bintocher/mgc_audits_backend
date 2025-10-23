from typing import List, Optional
from uuid import UUID
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.core.dependencies import get_current_user
from app.models.user import User
from app.crud import audit as crud_audit
from app.schemas.audit import (
    AuditCreate,
    AuditUpdate,
    AuditResponse,
    AuditRescheduleRequest
)


router = APIRouter(prefix="/audits", tags=["audits"])


@router.get("/", response_model=List[AuditResponse])
async def get_audits(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    enterprise_id: Optional[UUID] = None,
    audit_category: Optional[str] = None,
    audit_type_id: Optional[UUID] = None,
    status_id: Optional[UUID] = None,
    auditor_id: Optional[UUID] = None,
    year: Optional[int] = None,
    audit_date_from: Optional[date] = None,
    audit_date_to: Optional[date] = None,
    db: AsyncSession = Depends(get_session)
):
    """
    Получить список аудитов с пагинацией и фильтрацией.
    
    Args:
        skip: Количество записей для пропуска
        limit: Максимальное количество записей для возврата (1-100)
        enterprise_id: Фильтр по предприятию
        audit_category: Фильтр по категории ('product', 'process_system', 'lra', 'external')
        audit_type_id: Фильтр по типу аудита
        status_id: Фильтр по статусу
        auditor_id: Фильтр по аудитору
        year: Фильтр по году
        audit_date_from: Фильтр по начальной дате
        audit_date_to: Фильтр по конечной дате
        db: Сессия базы данных
    
    Returns:
        Список аудитов
    """
    audits = await crud_audit.get_audits(
        db=db,
        skip=skip,
        limit=limit,
        enterprise_id=enterprise_id,
        audit_category=audit_category,
        audit_type_id=audit_type_id,
        status_id=status_id,
        auditor_id=auditor_id,
        year=year,
        audit_date_from=audit_date_from,
        audit_date_to=audit_date_to
    )
    return audits


@router.post("/", response_model=AuditResponse, status_code=status.HTTP_201_CREATED)
async def create_audit(
    audit: AuditCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """
    Создать новый аудит.
    
    Args:
        audit: Данные для создания аудита
        current_user: Текущий пользователь
        db: Сессия базы данных
    
    Returns:
        Созданный аудит
    
    Raises:
        HTTPException: Если произошла ошибка при создании
    """
    audit_dict = audit.model_dump()
    audit_dict['created_by_id'] = current_user.id
    
    create_schema = AuditCreate(**audit_dict)
    return await crud_audit.create_audit(db=db, audit=create_schema)


@router.get("/{audit_id}", response_model=AuditResponse)
async def get_audit(
    audit_id: UUID,
    db: AsyncSession = Depends(get_session)
):
    """
    Получить информацию об аудите по ID.
    
    Args:
        audit_id: UUID аудита
        db: Сессия базы данных
    
    Returns:
        Информация об аудите
    
    Raises:
        HTTPException: Если аудит не найден
    """
    audit = await crud_audit.get_audit(db, audit_id)
    if not audit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit not found"
        )
    return audit


@router.put("/{audit_id}", response_model=AuditResponse)
async def update_audit(
    audit_id: UUID,
    audit_update: AuditUpdate,
    db: AsyncSession = Depends(get_session)
):
    """
    Обновить информацию об аудите.
    
    Args:
        audit_id: UUID аудита
        audit_update: Данные для обновления
        db: Сессия базы данных
    
    Returns:
        Обновленная информация об аудите
    
    Raises:
        HTTPException: Если аудит не найден
    """
    updated_audit = await crud_audit.update_audit(db, audit_id, audit_update)
    if not updated_audit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit not found"
        )
    return updated_audit


@router.delete("/{audit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_audit(
    audit_id: UUID,
    db: AsyncSession = Depends(get_session)
):
    """
    Деактивировать аудит (мягкое удаление).
    
    Args:
        audit_id: UUID аудита
        db: Сессия базы данных
    
    Raises:
        HTTPException: Если аудит не найден
    """
    success = await crud_audit.delete_audit(db, audit_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit not found"
        )


@router.post("/{audit_id}/reschedule", response_model=AuditResponse)
async def reschedule_audit(
    audit_id: UUID,
    reschedule_request: AuditRescheduleRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """
    Перенести аудит на новую дату.
    
    Args:
        audit_id: UUID аудита
        reschedule_request: Данные для переноса (новая дата и причина)
        current_user: Текущий пользователь
        db: Сессия базы данных
    
    Returns:
        Обновленная информация об аудите
    
    Raises:
        HTTPException: Если аудит не найден
    """
    updated_audit = await crud_audit.reschedule_audit(
        db=db,
        audit_id=audit_id,
        new_date_from=reschedule_request.new_date_from,
        new_date_to=reschedule_request.new_date_to,
        reason=reschedule_request.reason,
        rescheduled_by_id=current_user.id
    )
    if not updated_audit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit not found"
        )
    return updated_audit

