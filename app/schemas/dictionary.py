from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class DictionaryTypeBase(BaseModel):
    name: str = Field(..., max_length=255)
    code: str = Field(..., max_length=100)
    description: Optional[str] = None


class DictionaryTypeCreate(DictionaryTypeBase):
    pass


class DictionaryTypeUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    code: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None


class DictionaryTypeResponse(DictionaryTypeBase):
    id: UUID
    created_at: str
    updated_at: str
    deleted_at: Optional[str] = None

    class Config:
        from_attributes = True


class DictionaryBase(BaseModel):
    dictionary_type_id: UUID
    name: str = Field(..., max_length=255)
    code: str = Field(..., max_length=100)
    description: Optional[str] = None
    enterprise_id: Optional[UUID] = None
    is_active: bool = True


class DictionaryCreate(DictionaryBase):
    pass


class DictionaryUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    code: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    enterprise_id: Optional[UUID] = None
    is_active: Optional[bool] = None


class DictionaryResponse(DictionaryBase):
    id: UUID
    created_at: str
    updated_at: str
    deleted_at: Optional[str] = None

    class Config:
        from_attributes = True

