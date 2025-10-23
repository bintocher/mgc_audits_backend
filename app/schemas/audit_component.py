from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class AuditComponentBase(BaseModel):
    audit_id: UUID
    component_type: str = Field(..., max_length=50)
    sap_id: Optional[str] = Field(None, max_length=100)
    part_number: Optional[str] = Field(None, max_length=100)
    component_name: str = Field(..., max_length=500)
    description: Optional[str] = None


class AuditComponentCreate(AuditComponentBase):
    pass


class AuditComponentUpdate(BaseModel):
    audit_id: Optional[UUID] = None
    component_type: Optional[str] = Field(None, max_length=50)
    sap_id: Optional[str] = Field(None, max_length=100)
    part_number: Optional[str] = Field(None, max_length=100)
    component_name: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None


class AuditComponentResponse(AuditComponentBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True

