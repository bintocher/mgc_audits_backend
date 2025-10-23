from typing import Optional, List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.audit_component import AuditComponent
from app.schemas.audit_component import AuditComponentCreate, AuditComponentUpdate


async def create_audit_component(db: AsyncSession, component: AuditComponentCreate) -> AuditComponent:
    db_component = AuditComponent(
        audit_id=component.audit_id,
        component_type=component.component_type,
        sap_id=component.sap_id,
        part_number=component.part_number,
        component_name=component.component_name,
        description=component.description
    )
    db.add(db_component)
    await db.commit()
    await db.refresh(db_component)
    return db_component


async def get_audit_component(db: AsyncSession, component_id: UUID) -> Optional[AuditComponent]:
    stmt = select(AuditComponent).where(AuditComponent.id == component_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_audit_components(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    audit_id: Optional[UUID] = None,
    component_type: Optional[str] = None,
    sap_id: Optional[str] = None,
    part_number: Optional[str] = None
) -> List[AuditComponent]:
    stmt = select(AuditComponent)
    
    if audit_id is not None:
        stmt = stmt.where(AuditComponent.audit_id == audit_id)
    
    if component_type is not None:
        stmt = stmt.where(AuditComponent.component_type == component_type)
    
    if sap_id is not None:
        stmt = stmt.where(AuditComponent.sap_id == sap_id)
    
    if part_number is not None:
        stmt = stmt.where(AuditComponent.part_number == part_number)
    
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def update_audit_component(
    db: AsyncSession,
    component_id: UUID,
    component_update: AuditComponentUpdate
) -> Optional[AuditComponent]:
    db_component = await get_audit_component(db, component_id)
    if not db_component:
        return None
    
    update_data = component_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_component, field, value)
    
    await db.commit()
    await db.refresh(db_component)
    return db_component


async def delete_audit_component(db: AsyncSession, component_id: UUID) -> bool:
    db_component = await get_audit_component(db, component_id)
    if not db_component:
        return False
    
    db_component.soft_delete()
    await db.commit()
    return True

