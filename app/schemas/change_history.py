from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class ChangeHistoryBase(BaseModel):
    entity_type: str = Field(..., max_length=50)
    entity_id: UUID
    user_id: UUID
    field_name: str = Field(..., max_length=100)
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    changed_at: datetime


class ChangeHistoryCreate(ChangeHistoryBase):
    pass


class ChangeHistoryResponse(ChangeHistoryBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    user: Optional[dict] = None

    class Config:
        from_attributes = True

