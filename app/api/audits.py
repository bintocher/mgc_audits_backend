from typing import List, Optional
from uuid import UUID
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.core.dependencies import get_current_user
from app.models.user import User
from app.crud import audit as crud_audit
from app.crud import audit_calendar as crud_calendar
from app.crud import audit_schedule_week as crud_schedule_week
from app.schemas.audit import (
    AuditCreate,
    AuditUpdate,
    AuditResponse,
    AuditRescheduleRequest,
    AuditScheduleResponse,
    ScheduleWeekUpdate,
    RescheduleHistoryItem,
    ComponentScheduleItem
)
from app.schemas.audit_schedule_week import AuditScheduleWeekResponse
from app.schemas.change_history import ChangeHistoryResponse


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
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """
    Обновить информацию об аудите.
    
    Args:
        audit_id: UUID аудита
        audit_update: Данные для обновления
        current_user: Текущий пользователь
        db: Сессия базы данных
    
    Returns:
        Обновленная информация об аудите
    
    Raises:
        HTTPException: Если аудит не найден
    """
    # Получаем старые данные
    old_audit = await crud_audit.get_audit(db, audit_id)
    if not old_audit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit not found"
        )
    
    # Сохраняем старые данные в виде словаря
    old_data = {
        field: getattr(old_audit, field, None)
        for field in old_audit.__table__.columns.keys()
    }
    
    # Обновляем аудит
    updated_audit = await crud_audit.update_audit(db, audit_id, audit_update)
    if not updated_audit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit not found"
        )
    
    # Получаем новые данные
    new_data = {
        field: getattr(updated_audit, field, None)
        for field in updated_audit.__table__.columns.keys()
    }
    
    # Логируем изменения
    from app.services.change_history import log_entity_changes
    await log_entity_changes(
        db=db,
        entity_type='audit',
        entity_id=audit_id,
        user_id=current_user.id,
        old_data=old_data,
        new_data=new_data
    )
    
    await db.commit()
    await db.refresh(updated_audit)
    
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


@router.get("/calendar/schedule", response_model=AuditScheduleResponse)
async def get_audit_schedule(
    date_from: date = Query(..., description="Начальная дата периода"),
    date_to: date = Query(..., description="Конечная дата периода"),
    audit_category: Optional[str] = Query(None, description="Тип графика ('product', 'process_system', 'lra', 'external')"),
    enterprise_id: Optional[UUID] = Query(None, description="Фильтр по предприятию"),
    division_id: Optional[UUID] = Query(None, description="Фильтр по дивизиону"),
    auditor_id: Optional[UUID] = Query(None, description="Фильтр по аудитору"),
    status_id: Optional[UUID] = Query(None, description="Фильтр по статусу"),
    db: AsyncSession = Depends(get_session)
):
    """
    Получить график аудитов за произвольный период, сгруппированный по неделям.
    
    Args:
        date_from: Начальная дата периода
        date_to: Конечная дата периода
        audit_category: Тип графика
        enterprise_id: Фильтр по предприятию
        division_id: Фильтр по дивизиону
        auditor_id: Фильтр по аудитору
        status_id: Фильтр по статусу
        db: Сессия базы данных
    
    Returns:
        График аудитов с разбивкой по неделям
    """
    audits = await crud_calendar.get_audit_schedule(
        db=db,
        date_from=date_from,
        date_to=date_to,
        audit_category=audit_category,
        enterprise_id=enterprise_id,
        auditor_id=auditor_id,
        status_id=status_id
    )
    
    weeks = crud_calendar.get_weeks_in_range(date_from, date_to)
    
    from app.schemas.audit import (
        WeekInfo, PeriodInfo, WeekSchedule, AuditInfo, SimpleUser, SimpleLocation
    )
    
    period_info = PeriodInfo(
        date_from=date_from,
        date_to=date_to,
        weeks=[WeekInfo(**week) for week in weeks]
    )
    
    audit_list = []
    for audit in audits:
        weeks_schedule = []
        for week in audit.schedule_weeks:
            color = week.color_override
            if not color:
                color = crud_calendar.calculate_color(audit.audit_result, audit.status.code if audit.status else None)
            
            weeks_schedule.append(WeekSchedule(
                week_number=week.week_number,
                year=week.year,
                manual_data=week.manual_data,
                calculated_result=week.calculated_result,
                calculated_status=week.calculated_status,
                color=color
            ))
        
        clients = [client.name for client in audit.clients]
        
        audit_info = AuditInfo(
            id=audit.id,
            title=audit.title,
            audit_number=audit.audit_number,
            category=audit.audit_category,
            auditor=SimpleUser(
                id=audit.auditor.id,
                first_name_ru=audit.auditor.first_name_ru,
                last_name_ru=audit.auditor.last_name_ru,
                patronymic_ru=audit.auditor.patronymic_ru
            ),
            locations=[SimpleLocation(
                id=loc.id,
                name=loc.name,
                short_name=loc.short_name
            ) for loc in audit.locations],
            clients=clients,
            risk_level=audit.risk_level.code if audit.risk_level else None,
            milestone_codes=audit.milestone_codes,
            status={
                "id": str(audit.status.id),
                "name": audit.status.name,
                "code": audit.status.code
            },
            weeks=weeks_schedule
        )
        audit_list.append(audit_info)
    
    return AuditScheduleResponse(period=period_info, audits=audit_list)


@router.patch("/{audit_id}/schedule/{week_number}/{year}", response_model=AuditScheduleWeekResponse)
async def update_schedule_week(
    audit_id: UUID,
    week_number: int,
    year: int,
    update_data: ScheduleWeekUpdate,
    db: AsyncSession = Depends(get_session)
):
    """
    Редактировать ячейку графика (ручной ввод).
    
    Args:
        audit_id: UUID аудита
        week_number: Номер недели
        year: Год
        update_data: Данные для обновления
        db: Сессия базы данных
    
    Returns:
        Обновленная ячейка графика
    
    Raises:
        HTTPException: Если ячейка не найдена
    """
    from app.schemas.audit_schedule_week import AuditScheduleWeekUpdate
    
    update_schema = AuditScheduleWeekUpdate(**update_data.model_dump())
    
    updated_week = await crud_schedule_week.update_audit_schedule_week_by_period(
        db=db,
        audit_id=audit_id,
        week_number=week_number,
        year=year,
        schedule_week_update=update_schema
    )
    
    if not updated_week:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule week not found"
        )
    
    return updated_week


@router.get("/calendar/by_component", response_model=List[ComponentScheduleItem])
async def get_audit_schedule_by_component(
    date_from: date = Query(..., description="Начальная дата периода"),
    date_to: date = Query(..., description="Конечная дата периода"),
    component_type: Optional[str] = Query(None, description="Тип компонента"),
    sap_id: Optional[str] = Query(None, description="SAP ID"),
    enterprise_id: Optional[UUID] = Query(None, description="Фильтр по предприятию"),
    db: AsyncSession = Depends(get_session)
):
    """
    Получить график аудитов по компонентам (детали, узлы, системы).
    
    Args:
        date_from: Начальная дата периода
        date_to: Конечная дата периода
        component_type: Тип компонента
        sap_id: SAP ID
        enterprise_id: Фильтр по предприятию
        db: Сессия базы данных
    
    Returns:
        Список компонентов с информацией об аудитах
    """
    components = await crud_calendar.get_audit_schedule_by_component(
        db=db,
        date_from=date_from,
        date_to=date_to,
        component_type=component_type,
        sap_id=sap_id,
        enterprise_id=enterprise_id
    )
    
    return [ComponentScheduleItem(**comp) for comp in components]


@router.get("/{audit_id}/reschedule_history", response_model=List[RescheduleHistoryItem])
async def get_reschedule_history(
    audit_id: UUID,
    db: AsyncSession = Depends(get_session)
):
    """
    Получить историю всех переносов аудита.
    
    Args:
        audit_id: UUID аудита
        db: Сессия базы данных
    
    Returns:
        Список переносов с датами, причинами и исполнителями
    
    Raises:
        HTTPException: Если аудит не найден
    """
    history_list = await crud_audit.get_reschedule_history(db, audit_id)
    
    if not history_list:
        from app.crud import audit as crud_audit_get
        audit = await crud_audit_get.get_audit(db, audit_id)
        if not audit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Audit not found"
            )
        return []
    
    result = []
    for hist in history_list:
        from app.schemas.audit import SimpleUser
        result.append(RescheduleHistoryItem(
            rescheduled_date=hist['rescheduled_date'],
            postponed_reason=hist['postponed_reason'],
            rescheduled_by=SimpleUser(
                id=hist['rescheduled_by'].id,
                first_name_ru=hist['rescheduled_by'].first_name_ru,
                last_name_ru=hist['rescheduled_by'].last_name_ru,
                patronymic_ru=hist['rescheduled_by'].patronymic_ru
            ),
            rescheduled_at=hist['rescheduled_at']
        ))
    
    return result


@router.get("/{audit_id}/history", response_model=List[ChangeHistoryResponse])
async def get_audit_history(
    audit_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Получить историю изменений аудита.
    
    Args:
        audit_id: UUID аудита
        skip: Количество записей для пропуска
        limit: Максимальное количество записей для возврата (1-100)
        db: Сессия базы данных
        current_user: Текущий авторизованный пользователь
    
    Returns:
        Список записей истории изменений
    
    Raises:
        HTTPException: Если аудит не найден
    """
    from app.crud import change_history as crud_change_history
    
    # Проверяем существование аудита
    audit = await crud_audit.get_audit(db, audit_id)
    if not audit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit not found"
        )
    
    # Получаем историю изменений
    history = await crud_change_history.get_change_history_list(
        db=db,
        skip=skip,
        limit=limit,
        entity_type='audit',
        entity_id=audit_id
    )
    
    return history

