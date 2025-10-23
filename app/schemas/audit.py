from datetime import date, datetime
from typing import Optional, List
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, Field


class AuditBase(BaseModel):
    title: str = Field(..., max_length=500)
    audit_number: str = Field(..., max_length=100)
    subject: str = Field(..., max_length=500)
    enterprise_id: UUID
    audit_type_id: UUID
    process_id: Optional[UUID] = None
    product_id: Optional[UUID] = None
    project_id: Optional[UUID] = None
    norm_id: Optional[UUID] = None
    status_id: UUID
    auditor_id: UUID
    responsible_user_id: Optional[UUID] = None
    audit_plan_item_id: Optional[UUID] = None
    audit_date_from: date
    audit_date_to: date
    year: int

    audit_category: str = Field(..., max_length=50)

    audit_result: Optional[str] = Field(None, max_length=20)
    estimated_hours: Optional[Decimal] = None
    actual_hours: Optional[Decimal] = None

    risk_level_id: Optional[UUID] = None
    milestone_codes: Optional[str] = Field(None, max_length=100)
    result_comment: Optional[str] = None
    manual_result_value: Optional[str] = Field(None, max_length=50)

    pcd_planned_close_date: Optional[date] = None
    pcd_actual_close_date: Optional[date] = None
    pcd_status: Optional[str] = Field(None, max_length=50)

    postponed_reason: Optional[str] = None
    rescheduled_date: Optional[date] = None
    rescheduled_by_id: Optional[UUID] = None
    rescheduled_at: Optional[datetime] = None

    approved_by_id: Optional[UUID] = None
    approved_date: Optional[date] = None


class AuditCreate(AuditBase):
    created_by_id: UUID
    location_ids: Optional[List[UUID]] = None
    client_ids: Optional[List[UUID]] = None
    shift_ids: Optional[List[UUID]] = None


class AuditUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=500)
    audit_number: Optional[str] = Field(None, max_length=100)
    subject: Optional[str] = Field(None, max_length=500)
    enterprise_id: Optional[UUID] = None
    audit_type_id: Optional[UUID] = None
    process_id: Optional[UUID] = None
    product_id: Optional[UUID] = None
    project_id: Optional[UUID] = None
    norm_id: Optional[UUID] = None
    status_id: Optional[UUID] = None
    auditor_id: Optional[UUID] = None
    responsible_user_id: Optional[UUID] = None
    audit_plan_item_id: Optional[UUID] = None
    audit_date_from: Optional[date] = None
    audit_date_to: Optional[date] = None
    year: Optional[int] = None

    audit_category: Optional[str] = Field(None, max_length=50)

    audit_result: Optional[str] = Field(None, max_length=20)
    estimated_hours: Optional[Decimal] = None
    actual_hours: Optional[Decimal] = None

    risk_level_id: Optional[UUID] = None
    milestone_codes: Optional[str] = Field(None, max_length=100)
    result_comment: Optional[str] = None
    manual_result_value: Optional[str] = Field(None, max_length=50)

    pcd_planned_close_date: Optional[date] = None
    pcd_actual_close_date: Optional[date] = None
    pcd_status: Optional[str] = Field(None, max_length=50)

    postponed_reason: Optional[str] = None
    rescheduled_date: Optional[date] = None
    rescheduled_by_id: Optional[UUID] = None
    rescheduled_at: Optional[datetime] = None

    approved_by_id: Optional[UUID] = None
    approved_date: Optional[date] = None

    location_ids: Optional[List[UUID]] = None
    client_ids: Optional[List[UUID]] = None
    shift_ids: Optional[List[UUID]] = None


class AuditRescheduleRequest(BaseModel):
    new_date_from: date
    new_date_to: date
    reason: str = Field(..., min_length=1)


class SimpleLocation(BaseModel):
    id: UUID
    name: str
    short_name: Optional[str] = None

    class Config:
        from_attributes = True


class SimpleDictionary(BaseModel):
    id: UUID
    name: str
    code: str

    class Config:
        from_attributes = True


class SimpleUser(BaseModel):
    id: UUID
    first_name_ru: str
    last_name_ru: str
    patronymic_ru: Optional[str] = None

    class Config:
        from_attributes = True


class AuditResponse(AuditBase):
    id: UUID
    created_by_id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    enterprise: Optional[dict] = None
    audit_type: Optional[dict] = None
    process: Optional[dict] = None
    product: Optional[dict] = None
    project: Optional[dict] = None
    norm: Optional[dict] = None
    status: Optional[dict] = None
    auditor: Optional[dict] = None
    responsible_user: Optional[dict] = None
    audit_plan_item: Optional[dict] = None
    rescheduled_by: Optional[dict] = None
    approver: Optional[dict] = None
    creator: Optional[dict] = None
    risk_level: Optional[dict] = None

    locations: List[SimpleLocation] = []
    clients: List[SimpleDictionary] = []
    shifts: List[SimpleDictionary] = []

    class Config:
        from_attributes = True


class WeekInfo(BaseModel):
    week_number: int
    year: int
    start_date: date
    end_date: date


class PeriodInfo(BaseModel):
    date_from: date
    date_to: date
    weeks: List[WeekInfo]


class WeekSchedule(BaseModel):
    week_number: int
    year: int
    manual_data: Optional[str] = None
    calculated_result: Optional[str] = None
    calculated_status: Optional[str] = None
    color: Optional[str] = None


class AuditInfo(BaseModel):
    id: UUID
    title: str
    audit_number: str
    category: str
    auditor: SimpleUser
    locations: List[SimpleLocation]
    clients: List[str]
    risk_level: Optional[str] = None
    milestone_codes: Optional[str] = None
    status: dict
    weeks: List[WeekSchedule]


class AuditScheduleResponse(BaseModel):
    period: PeriodInfo
    audits: List[AuditInfo]


class ScheduleWeekUpdate(BaseModel):
    manual_data: Optional[str] = Field(None, max_length=100)
    color_override: Optional[str] = Field(None, max_length=7)


class RescheduleHistoryItem(BaseModel):
    rescheduled_date: date
    postponed_reason: str
    rescheduled_by: SimpleUser
    rescheduled_at: datetime


class ComponentScheduleItem(BaseModel):
    component_type: str
    sap_id: Optional[str] = None
    part_number: Optional[str] = None
    component_name: str
    audit_date_from: date
    audit_date_to: date
    estimated_hours: Optional[Decimal] = None
    actual_hours: Optional[Decimal] = None
    status: dict

