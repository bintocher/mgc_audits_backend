from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class AuditScheduleWeekBase(BaseModel):
    audit_id: UUID
    week_number: int = Field(..., ge=1, le=53)
    year: int = Field(..., ge=2020, le=2100)

    manual_data: Optional[str] = Field(None, max_length=100)
    calculated_result: Optional[str] = Field(None, max_length=50)
    calculated_status: Optional[str] = Field(None, max_length=50)
    color_override: Optional[str] = Field(None, max_length=7)


class AuditScheduleWeekCreate(AuditScheduleWeekBase):
    pass


class AuditScheduleWeekUpdate(BaseModel):
    manual_data: Optional[str] = Field(None, max_length=100)
    calculated_result: Optional[str] = Field(None, max_length=50)
    calculated_status: Optional[str] = Field(None, max_length=50)
    color_override: Optional[str] = Field(None, max_length=7)


class AuditScheduleWeekResponse(AuditScheduleWeekBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True

