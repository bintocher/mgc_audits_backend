from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field


class StatusBase(BaseModel):
    name: str = Field(..., max_length=100)
    code: str = Field(..., max_length=50)
    color: str = Field(..., max_length=7, pattern="^#[0-9A-Fa-f]{6}$")
    entity_type: str = Field(..., max_length=50)
    order: int = Field(..., ge=0)
    is_initial: bool = False
    is_final: bool = False


class StatusCreate(StatusBase):
    pass


class StatusUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    code: Optional[str] = Field(None, max_length=50)
    color: Optional[str] = Field(None, max_length=7, pattern="^#[0-9A-Fa-f]{6}$")
    order: Optional[int] = Field(None, ge=0)
    is_initial: Optional[bool] = None
    is_final: Optional[bool] = None


class StatusResponse(StatusBase):
    id: UUID
    created_at: str
    updated_at: str
    deleted_at: Optional[str] = None

    class Config:
        from_attributes = True


class StatusTransitionBase(BaseModel):
    from_status_id: UUID
    to_status_id: UUID
    required_roles: Optional[List[str]] = None
    required_fields: Optional[List[str]] = None
    require_comment: bool = False
    notification_config: Optional[Dict[str, Any]] = None
    color: Optional[str] = Field(None, max_length=7, pattern="^#[0-9A-Fa-f]{6}$")


class StatusTransitionCreate(StatusTransitionBase):
    pass


class StatusTransitionUpdate(BaseModel):
    required_roles: Optional[List[str]] = None
    required_fields: Optional[List[str]] = None
    require_comment: Optional[bool] = None
    notification_config: Optional[Dict[str, Any]] = None
    color: Optional[str] = Field(None, max_length=7, pattern="^#[0-9A-Fa-f]{6}$")


class StatusTransitionResponse(StatusTransitionBase):
    id: UUID
    created_at: str
    updated_at: str
    deleted_at: Optional[str] = None

    class Config:
        from_attributes = True


class StatusTransitionValidateRequest(BaseModel):
    from_status_id: UUID
    to_status_id: UUID
    entity_data: Optional[Dict[str, Any]] = None
    comment: Optional[str] = None


class StatusTransitionValidateResponse(BaseModel):
    is_valid: bool
    message: str
    transition: Optional[StatusTransitionResponse] = None
    missing_fields: Optional[List[str]] = None
    missing_roles: Optional[List[str]] = None

