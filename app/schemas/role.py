from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field


class PermissionBase(BaseModel):
    enterprise_id: Optional[UUID] = None
    resource: str = Field(..., max_length=100)
    action: str = Field(..., max_length=20)


class PermissionCreate(PermissionBase):
    pass


class PermissionResponse(PermissionBase):
    id: UUID
    role_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class RoleBase(BaseModel):
    name: str = Field(..., max_length=100)
    code: str = Field(..., max_length=50)
    description: Optional[str] = None
    is_system: bool = False


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    code: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    is_system: Optional[bool] = None


class RoleResponse(RoleBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    permissions: List[PermissionResponse] = []

    class Config:
        from_attributes = True


class RoleInDB(RoleResponse):
    pass

