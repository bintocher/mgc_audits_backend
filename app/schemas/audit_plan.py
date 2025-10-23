from datetime import date, datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class AuditPlanBase(BaseModel):
    title: str = Field(..., max_length=500)
    date_from: date
    date_to: date
    enterprise_id: UUID
    category: str = Field(..., max_length=50)  # 'product', 'process_system', 'lra', 'external'
    status: str = Field(default='draft', max_length=20)  # 'draft', 'approved', 'in_progress', 'completed'
    version_number: int = Field(default=1)


class AuditPlanCreate(AuditPlanBase):
    created_by_id: UUID


class AuditPlanUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=500)
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    enterprise_id: Optional[UUID] = None
    category: Optional[str] = Field(None, max_length=50)
    status: Optional[str] = Field(None, max_length=20)
    version_number: Optional[int] = None


class AuditPlanApproveRequest(BaseModel):
    reason: Optional[str] = None


class AuditPlanRejectRequest(BaseModel):
    reason: str = Field(..., min_length=1)


class AuditPlanResponse(AuditPlanBase):
    id: UUID
    approved_by_division: bool
    approved_by_division_user_id: Optional[UUID] = None
    approved_by_division_at: Optional[datetime] = None
    approved_by_uk: bool
    approved_by_uk_user_id: Optional[UUID] = None
    approved_by_uk_at: Optional[datetime] = None
    created_by_id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AuditPlanItemBase(BaseModel):
    audit_plan_id: UUID
    audit_type_id: UUID
    process_id: Optional[UUID] = None
    product_id: Optional[UUID] = None
    project_id: Optional[UUID] = None
    norm_id: Optional[UUID] = None
    planned_auditor_id: Optional[UUID] = None
    planned_date_from: date
    planned_date_to: date
    priority: str = Field(default='medium', max_length=20)  # 'high', 'medium', 'low'
    notes: Optional[str] = None


class AuditPlanItemCreate(AuditPlanItemBase):
    pass


class AuditPlanItemUpdate(BaseModel):
    audit_plan_id: Optional[UUID] = None
    audit_type_id: Optional[UUID] = None
    process_id: Optional[UUID] = None
    product_id: Optional[UUID] = None
    project_id: Optional[UUID] = None
    norm_id: Optional[UUID] = None
    planned_auditor_id: Optional[UUID] = None
    planned_date_from: Optional[date] = None
    planned_date_to: Optional[date] = None
    priority: Optional[str] = Field(None, max_length=20)
    notes: Optional[str] = None


class AuditPlanItemResponse(AuditPlanItemBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True

