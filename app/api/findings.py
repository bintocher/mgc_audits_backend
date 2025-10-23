from typing import List, Optional
from uuid import UUID
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.core.dependencies import get_current_user
from app.models.user import User
from app.crud import finding as crud_finding
from app.crud import finding_delegation as crud_delegation
from app.crud import finding_comment as crud_comment
from app.schemas.finding import (
    FindingCreate,
    FindingUpdate,
    FindingResponse,
    FindingDelegationCreate,
    FindingDelegationResponse,
    FindingCommentCreate,
    FindingCommentUpdate,
    FindingCommentResponse
)
from app.schemas.change_history import ChangeHistoryResponse


router = APIRouter(prefix="/findings", tags=["findings"])


@router.get("/", response_model=List[FindingResponse])
async def get_findings(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    audit_id: Optional[UUID] = None,
    enterprise_id: Optional[UUID] = None,
    status_id: Optional[UUID] = None,
    resolver_id: Optional[UUID] = None,
    approver_id: Optional[UUID] = None,
    deadline_from: Optional[date] = None,
    deadline_to: Optional[date] = None,
    db: AsyncSession = Depends(get_session)
):
    """
    Получить список несоответствий с пагинацией и фильтрацией.
    
    Args:
        skip: Количество записей для пропуска
        limit: Максимальное количество записей для возврата (1-100)
        audit_id: Фильтр по аудиту
        enterprise_id: Фильтр по предприятию
        status_id: Фильтр по статусу
        resolver_id: Фильтр по исполнителю
        approver_id: Фильтр по утверждающему
        deadline_from: Фильтр по начальной дате дедлайна
        deadline_to: Фильтр по конечной дате дедлайна
        db: Сессия базы данных
    
    Returns:
        Список несоответствий
    """
    findings = await crud_finding.get_findings(
        db=db,
        skip=skip,
        limit=limit,
        audit_id=audit_id,
        enterprise_id=enterprise_id,
        status_id=status_id,
        resolver_id=resolver_id,
        approver_id=approver_id,
        deadline_from=deadline_from,
        deadline_to=deadline_to
    )
    return findings


@router.post("/", response_model=FindingResponse, status_code=status.HTTP_201_CREATED)
async def create_finding(
    finding: FindingCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """
    Создать новое несоответствие.
    
    Args:
        finding: Данные для создания несоответствия
        current_user: Текущий пользователь
        db: Сессия базы данных
    
    Returns:
        Созданное несоответствие
    
    Raises:
        HTTPException: Если произошла ошибка при создании
    """
    finding_dict = finding.model_dump()
    finding_dict['created_by_id'] = current_user.id
    
    create_schema = FindingCreate(**finding_dict)
    return await crud_finding.create_finding(db=db, finding=create_schema)


@router.get("/{finding_id}", response_model=FindingResponse)
async def get_finding(
    finding_id: UUID,
    db: AsyncSession = Depends(get_session)
):
    """
    Получить информацию о несоответствии по ID.
    
    Args:
        finding_id: UUID несоответствия
        db: Сессия базы данных
    
    Returns:
        Информация о несоответствии
    
    Raises:
        HTTPException: Если несоответствие не найдено
    """
    finding = await crud_finding.get_finding(db, finding_id)
    if not finding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Finding not found"
        )
    return finding


@router.put("/{finding_id}", response_model=FindingResponse)
async def update_finding(
    finding_id: UUID,
    finding_update: FindingUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """
    Обновить информацию о несоответствии.
    
    Args:
        finding_id: UUID несоответствия
        finding_update: Данные для обновления
        current_user: Текущий пользователь
        db: Сессия базы данных
    
    Returns:
        Обновленная информация о несоответствии
    
    Raises:
        HTTPException: Если несоответствие не найдено
    """
    # Получаем старые данные
    old_finding = await crud_finding.get_finding(db, finding_id)
    if not old_finding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Finding not found"
        )
    
    # Сохраняем старые данные в виде словаря
    old_data = {
        field: getattr(old_finding, field, None)
        for field in old_finding.__table__.columns.keys()
    }
    
    # Обновляем несоответствие
    updated_finding = await crud_finding.update_finding(db, finding_id, finding_update)
    if not updated_finding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Finding not found"
        )
    
    # Получаем новые данные
    new_data = {
        field: getattr(updated_finding, field, None)
        for field in updated_finding.__table__.columns.keys()
    }
    
    # Логируем изменения
    from app.services.change_history import log_entity_changes
    await log_entity_changes(
        db=db,
        entity_type='finding',
        entity_id=finding_id,
        user_id=current_user.id,
        old_data=old_data,
        new_data=new_data
    )
    
    await db.commit()
    await db.refresh(updated_finding)
    
    return updated_finding


@router.delete("/{finding_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_finding(
    finding_id: UUID,
    db: AsyncSession = Depends(get_session)
):
    """
    Деактивировать несоответствие (мягкое удаление).
    
    Args:
        finding_id: UUID несоответствия
        db: Сессия базы данных
    
    Raises:
        HTTPException: Если несоответствие не найдено
    """
    success = await crud_finding.delete_finding(db, finding_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Finding not found"
        )


@router.post("/{finding_id}/delegate", response_model=FindingDelegationResponse, status_code=status.HTTP_201_CREATED)
async def delegate_finding(
    finding_id: UUID,
    delegation: FindingDelegationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """
    Делегировать ответственность за несоответствие.
    
    Args:
        finding_id: UUID несоответствия
        delegation: Данные для делегирования
        current_user: Текущий пользователь
        db: Сессия базы данных
    
    Returns:
        Созданное делегирование
    
    Raises:
        HTTPException: Если несоответствие не найдено
    """
    finding = await crud_finding.get_finding(db, finding_id)
    if not finding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Finding not found"
        )
    
    delegation_dict = delegation.model_dump()
    delegation_dict['finding_id'] = finding_id
    delegation_dict['from_user_id'] = current_user.id
    
    create_schema = FindingDelegationCreate(**delegation_dict)
    created_delegation = await crud_delegation.create_finding_delegation(db=db, delegation=create_schema)
    
    finding.resolver_id = delegation.to_user_id
    await db.commit()
    await db.refresh(finding)
    
    return created_delegation


@router.get("/comments/", response_model=List[FindingCommentResponse])
async def get_finding_comments(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    finding_id: Optional[UUID] = Query(None, description="Фильтр по несоответствию"),
    db: AsyncSession = Depends(get_session)
):
    """
    Получить список комментариев к несоответствиям.
    
    Args:
        skip: Количество записей для пропуска
        limit: Максимальное количество записей для возврата (1-100)
        finding_id: Фильтр по несоответствию
        db: Сессия базы данных
    
    Returns:
        Список комментариев
    """
    comments = await crud_comment.get_finding_comments(
        db=db,
        skip=skip,
        limit=limit,
        finding_id=finding_id
    )
    return comments


@router.post("/comments/", response_model=FindingCommentResponse, status_code=status.HTTP_201_CREATED)
async def create_finding_comment(
    comment: FindingCommentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    """
    Добавить комментарий к несоответствию.
    
    Args:
        comment: Данные для создания комментария
        current_user: Текущий пользователь
        db: Сессия базы данных
    
    Returns:
        Созданный комментарий
    
    Raises:
        HTTPException: Если произошла ошибка при создании
    """
    comment_dict = comment.model_dump()
    comment_dict['author_id'] = current_user.id
    
    create_schema = FindingCommentCreate(**comment_dict)
    return await crud_comment.create_finding_comment(db=db, comment=create_schema)


@router.put("/comments/{comment_id}", response_model=FindingCommentResponse)
async def update_finding_comment(
    comment_id: UUID,
    comment_update: FindingCommentUpdate,
    db: AsyncSession = Depends(get_session)
):
    """
    Обновить комментарий к несоответствию.
    
    Args:
        comment_id: UUID комментария
        comment_update: Данные для обновления
        db: Сессия базы данных
    
    Returns:
        Обновленный комментарий
    
    Raises:
        HTTPException: Если комментарий не найден
    """
    updated_comment = await crud_comment.update_finding_comment(db, comment_id, comment_update)
    if not updated_comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    return updated_comment


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_finding_comment(
    comment_id: UUID,
    db: AsyncSession = Depends(get_session)
):
    """
    Удалить комментарий к несоответствию.
    
    Args:
        comment_id: UUID комментария
        db: Сессия базы данных
    
    Raises:
        HTTPException: Если комментарий не найден
    """
    success = await crud_comment.delete_finding_comment(db, comment_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )


@router.get("/{finding_id}/history", response_model=List[ChangeHistoryResponse])
async def get_finding_history(
    finding_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Получить историю изменений несоответствия.
    
    Args:
        finding_id: UUID несоответствия
        skip: Количество записей для пропуска
        limit: Максимальное количество записей для возврата (1-100)
        db: Сессия базы данных
        current_user: Текущий авторизованный пользователь
    
    Returns:
        Список записей истории изменений
    
    Raises:
        HTTPException: Если несоответствие не найдено
    """
    from app.crud import change_history as crud_change_history
    
    # Проверяем существование несоответствия
    finding = await crud_finding.get_finding(db, finding_id)
    if not finding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Finding not found"
        )
    
    # Получаем историю изменений
    history = await crud_change_history.get_change_history_list(
        db=db,
        skip=skip,
        limit=limit,
        entity_type='finding',
        entity_id=finding_id
    )
    
    return history

