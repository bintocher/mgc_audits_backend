from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.dependencies import require_staff
from app.models.user import User
from app.models.status import Status
from app.models.status_transition import StatusTransition
from app.schemas.status import (
    StatusCreate,
    StatusUpdate,
    StatusResponse,
    StatusTransitionCreate,
    StatusTransitionUpdate,
    StatusTransitionResponse
)

router = APIRouter(prefix="/workflow", tags=["workflow"])


@router.get("/statuses", response_model=List[StatusResponse])
async def get_statuses(
    entity_type: str = Query(..., description="Тип сущности (audit, finding, audit_plan)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Получить список статусов для указанного типа сущности.
    """
    result = await db.execute(
        select(Status)
        .where(Status.entity_type == entity_type)
        .order_by(Status.order)
    )
    statuses = list(result.scalars().all())
    return statuses


@router.post("/statuses", response_model=StatusResponse)
async def create_status(
    status_data: StatusCreate,
    current_user: User = Depends(require_staff),
    db: AsyncSession = Depends(get_db)
):
    """
    Создать новый статус.
    """
    status_obj = Status(**status_data.model_dump())
    db.add(status_obj)
    await db.commit()
    await db.refresh(status_obj)
    return status_obj


@router.put("/statuses/{status_id}", response_model=StatusResponse)
async def update_status(
    status_id: UUID,
    status_data: StatusUpdate,
    current_user: User = Depends(require_staff),
    db: AsyncSession = Depends(get_db)
):
    """
    Обновить статус.
    """
    result = await db.execute(select(Status).where(Status.id == status_id))
    status_obj = result.scalar_one_or_none()
    
    if status_obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Status not found"
        )
    
    for field, value in status_data.model_dump(exclude_unset=True).items():
        setattr(status_obj, field, value)
    
    await db.commit()
    await db.refresh(status_obj)
    return status_obj


@router.delete("/statuses/{status_id}")
async def delete_status(
    status_id: UUID,
    current_user: User = Depends(require_staff),
    db: AsyncSession = Depends(get_db)
):
    """
    Удалить статус (мягкое удаление).
    """
    result = await db.execute(select(Status).where(Status.id == status_id))
    status_obj = result.scalar_one_or_none()
    
    if status_obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Status not found"
        )
    
    from datetime import datetime, timezone
    status_obj.deleted_at = datetime.now(timezone.utc)
    
    await db.commit()
    return {"message": "Status deleted successfully"}


@router.get("/transitions", response_model=List[StatusTransitionResponse])
async def get_transitions(
    db: AsyncSession = Depends(get_db)
):
    """
    Получить список всех переходов между статусами.
    """
    result = await db.execute(select(StatusTransition))
    transitions = list(result.scalars().all())
    return transitions


@router.post("/transitions", response_model=StatusTransitionResponse)
async def create_transition(
    transition_data: StatusTransitionCreate,
    current_user: User = Depends(require_staff),
    db: AsyncSession = Depends(get_db)
):
    """
    Создать новый переход между статусами.
    """
    transition = StatusTransition(**transition_data.model_dump())
    db.add(transition)
    await db.commit()
    await db.refresh(transition)
    return transition


@router.put("/transitions/{transition_id}", response_model=StatusTransitionResponse)
async def update_transition(
    transition_id: UUID,
    transition_data: StatusTransitionUpdate,
    current_user: User = Depends(require_staff),
    db: AsyncSession = Depends(get_db)
):
    """
    Обновить переход между статусами.
    """
    result = await db.execute(
        select(StatusTransition).where(StatusTransition.id == transition_id)
    )
    transition = result.scalar_one_or_none()
    
    if transition is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transition not found"
        )
    
    for field, value in transition_data.model_dump(exclude_unset=True).items():
        setattr(transition, field, value)
    
    await db.commit()
    await db.refresh(transition)
    return transition


@router.delete("/transitions/{transition_id}")
async def delete_transition(
    transition_id: UUID,
    current_user: User = Depends(require_staff),
    db: AsyncSession = Depends(get_db)
):
    """
    Удалить переход между статусами (мягкое удаление).
    """
    result = await db.execute(
        select(StatusTransition).where(StatusTransition.id == transition_id)
    )
    transition = result.scalar_one_or_none()
    
    if transition is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transition not found"
        )
    
    from datetime import datetime, timezone
    transition.deleted_at = datetime.now(timezone.utc)
    
    await db.commit()
    return {"message": "Transition deleted successfully"}

