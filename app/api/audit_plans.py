from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.core.dependencies import get_current_user
from app.models.user import User
from app.crud import audit_plan as crud_audit_plan
from app.schemas.audit_plan import (
    AuditPlanCreate,
    AuditPlanUpdate,
    AuditPlanResponse,
    AuditPlanApproveRequest,
    AuditPlanRejectRequest,
    AuditPlanItemCreate,
    AuditPlanItemUpdate,
    AuditPlanItemResponse
)


router = APIRouter(prefix="/audit_plans", tags=["audit_plans"])


@router.get("/", response_model=List[AuditPlanResponse])
async def get_audit_plans(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    enterprise_id: Optional[UUID] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_session)
):
    """
    Получить список планов аудитов с пагинацией и фильтрацией.
    
    Args:
        skip: Количество записей для пропуска
        limit: Максимальное количество записей для возврата (1-100)
        enterprise_id: Фильтр по предприятию
        category: Фильтр по категории графика ('product', 'process_system', 'lra', 'external')
        status: Фильтр по статусу ('draft', 'approved', 'in_progress', 'completed')
        db: Сессия базы данных
    
    Returns:
        Список планов аудитов
    """
    audit_plans = await crud_audit_plan.get_audit_plans(
        db=db,
        skip=skip,
        limit=limit,
        enterprise_id=enterprise_id,
        category=category,
        status=status
    )
    return audit_plans


@router.post("/", response_model=AuditPlanResponse, status_code=status.HTTP_201_CREATED)
async def create_audit_plan(
    audit_plan: AuditPlanCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """
    Создать новый план аудитов.
    
    Args:
        audit_plan: Данные для создания плана аудитов
        current_user: Текущий пользователь
        db: Сессия базы данных
    
    Returns:
        Созданный план аудитов
    
    Raises:
        HTTPException: Если предприятие не найдено
    """
    audit_plan_dict = audit_plan.model_dump()
    audit_plan_dict['created_by_id'] = current_user.id
    
    create_schema = AuditPlanCreate(**audit_plan_dict)
    return await crud_audit_plan.create_audit_plan(db=db, audit_plan=create_schema)


@router.get("/{audit_plan_id}", response_model=AuditPlanResponse)
async def get_audit_plan(
    audit_plan_id: UUID,
    db: AsyncSession = Depends(get_session)
):
    """
    Получить информацию о плане аудитов по ID.
    
    Args:
        audit_plan_id: UUID плана аудитов
        db: Сессия базы данных
    
    Returns:
        Информация о плане аудитов
    
    Raises:
        HTTPException: Если план аудитов не найден
    """
    audit_plan = await crud_audit_plan.get_audit_plan(db, audit_plan_id)
    if not audit_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit plan not found"
        )
    return audit_plan


@router.put("/{audit_plan_id}", response_model=AuditPlanResponse)
async def update_audit_plan(
    audit_plan_id: UUID,
    audit_plan_update: AuditPlanUpdate,
    db: AsyncSession = Depends(get_session)
):
    """
    Обновить информацию о плане аудитов.
    
    Args:
        audit_plan_id: UUID плана аудитов
        audit_plan_update: Данные для обновления
        db: Сессия базы данных
    
    Returns:
        Обновленная информация о плане аудитов
    
    Raises:
        HTTPException: Если план аудитов не найден
    """
    updated_plan = await crud_audit_plan.update_audit_plan(db, audit_plan_id, audit_plan_update)
    if not updated_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit plan not found"
        )
    return updated_plan


@router.delete("/{audit_plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_audit_plan(
    audit_plan_id: UUID,
    db: AsyncSession = Depends(get_session)
):
    """
    Деактивировать план аудитов (мягкое удаление).
    
    Args:
        audit_plan_id: UUID плана аудитов
        db: Сессия базы данных
    
    Raises:
        HTTPException: Если план аудитов не найден
    """
    success = await crud_audit_plan.delete_audit_plan(db, audit_plan_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit plan not found"
        )


@router.post("/{audit_plan_id}/approve_by_division", response_model=AuditPlanResponse)
async def approve_by_division(
    audit_plan_id: UUID,
    approve_request: AuditPlanApproveRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """
    Утвердить план аудитов на уровне Дивизиона.
    
    Args:
        audit_plan_id: UUID плана аудитов
        approve_request: Запрос на утверждение
        current_user: Текущий пользователь
        db: Сессия базы данных
    
    Returns:
        Обновленный план аудитов
    
    Raises:
        HTTPException: Если план аудитов не найден
    """
    updated_plan = await crud_audit_plan.approve_by_division(db, audit_plan_id, current_user.id)
    if not updated_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit plan not found"
        )
    return updated_plan


@router.post("/{audit_plan_id}/approve_by_uk", response_model=AuditPlanResponse)
async def approve_by_uk(
    audit_plan_id: UUID,
    approve_request: AuditPlanApproveRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """
    Утвердить план аудитов на уровне УК (управляющей компании).
    
    Args:
        audit_plan_id: UUID плана аудитов
        approve_request: Запрос на утверждение
        current_user: Текущий пользователь
        db: Сессия базы данных
    
    Returns:
        Обновленный план аудитов
    
    Raises:
        HTTPException: Если план аудитов не найден
    """
    updated_plan = await crud_audit_plan.approve_by_uk(db, audit_plan_id, current_user.id)
    if not updated_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit plan not found"
        )
    return updated_plan


@router.post("/{audit_plan_id}/reject", response_model=AuditPlanResponse)
async def reject_audit_plan(
    audit_plan_id: UUID,
    reject_request: AuditPlanRejectRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """
    Отклонить план аудитов с указанием причины.
    
    Args:
        audit_plan_id: UUID плана аудитов
        reject_request: Запрос на отклонение с причиной
        current_user: Текущий пользователь
        db: Сессия базы данных
    
    Returns:
        Обновленный план аудитов
    
    Raises:
        HTTPException: Если план аудитов не найден
    """
    updated_plan = await crud_audit_plan.reject_audit_plan(db, audit_plan_id, reject_request.reason)
    if not updated_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit plan not found"
        )
    return updated_plan


@router.get("/items/", response_model=List[AuditPlanItemResponse])
async def get_audit_plan_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    audit_plan_id: Optional[UUID] = None,
    planned_auditor_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_session)
):
    """
    Получить список пунктов плана аудитов с пагинацией и фильтрацией.
    
    Args:
        skip: Количество записей для пропуска
        limit: Максимальное количество записей для возврата (1-100)
        audit_plan_id: Фильтр по плану аудитов
        planned_auditor_id: Фильтр по запланированному аудитору
        db: Сессия базы данных
    
    Returns:
        Список пунктов плана аудитов
    """
    items = await crud_audit_plan.get_audit_plan_items(
        db=db,
        skip=skip,
        limit=limit,
        audit_plan_id=audit_plan_id,
        planned_auditor_id=planned_auditor_id
    )
    return items


@router.post("/items/", response_model=AuditPlanItemResponse, status_code=status.HTTP_201_CREATED)
async def create_audit_plan_item(
    audit_plan_item: AuditPlanItemCreate,
    db: AsyncSession = Depends(get_session)
):
    """
    Создать новый пункт плана аудитов.
    
    Args:
        audit_plan_item: Данные для создания пункта плана
        db: Сессия базы данных
    
    Returns:
        Созданный пункт плана аудитов
    
    Raises:
        HTTPException: Если аудитор не имеет необходимой квалификации
    """
    try:
        return await crud_audit_plan.create_audit_plan_item(db, audit_plan_item.model_dump())
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/items/{audit_plan_item_id}", response_model=AuditPlanItemResponse)
async def get_audit_plan_item(
    audit_plan_item_id: UUID,
    db: AsyncSession = Depends(get_session)
):
    """
    Получить информацию о пункте плана аудитов по ID.
    
    Args:
        audit_plan_item_id: UUID пункта плана
        db: Сессия базы данных
    
    Returns:
        Информация о пункте плана аудитов
    
    Raises:
        HTTPException: Если пункт плана не найден
    """
    item = await crud_audit_plan.get_audit_plan_item(db, audit_plan_item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit plan item not found"
        )
    return item


@router.put("/items/{audit_plan_item_id}", response_model=AuditPlanItemResponse)
async def update_audit_plan_item(
    audit_plan_item_id: UUID,
    audit_plan_item_update: AuditPlanItemUpdate,
    db: AsyncSession = Depends(get_session)
):
    """
    Обновить информацию о пункте плана аудитов.
    
    Args:
        audit_plan_item_id: UUID пункта плана
        audit_plan_item_update: Данные для обновления
        db: Сессия базы данных
    
    Returns:
        Обновленная информация о пункте плана
    
    Raises:
        HTTPException: Если пункт плана не найден или аудитор не имеет необходимой квалификации
    """
    try:
        updated_item = await crud_audit_plan.update_audit_plan_item(
            db, 
            audit_plan_item_id, 
            audit_plan_item_update.model_dump(exclude_unset=True)
        )
        if not updated_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Audit plan item not found"
            )
        return updated_item
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/items/{audit_plan_item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_audit_plan_item(
    audit_plan_item_id: UUID,
    db: AsyncSession = Depends(get_session)
):
    """
    Деактивировать пункт плана аудитов (мягкое удаление).
    
    Args:
        audit_plan_item_id: UUID пункта плана
        db: Сессия базы данных
    
    Raises:
        HTTPException: Если пункт плана не найден
    """
    success = await crud_audit_plan.delete_audit_plan_item(db, audit_plan_item_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit plan item not found"
        )

