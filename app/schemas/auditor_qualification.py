from datetime import date, datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field


class QualificationStandardBase(BaseModel):
    name: str = Field(..., max_length=255)
    code: str = Field(..., max_length=100)
    description: Optional[str] = None
    is_active: bool = True


class QualificationStandardCreate(QualificationStandardBase):
    pass


class QualificationStandardUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    code: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class QualificationStandardResponse(QualificationStandardBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class StandardChapterBase(BaseModel):
    name: str = Field(..., max_length=500)
    code: str = Field(..., max_length=100)
    description: Optional[str] = None
    is_active: bool = True


class StandardChapterCreate(StandardChapterBase):
    standard_id: UUID


class StandardChapterUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=500)
    code: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class StandardChapterResponse(StandardChapterBase):
    id: UUID
    standard_id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AuditorQualificationBase(BaseModel):
    certification_body: str = Field(..., max_length=255)
    certificate_number: str = Field(..., max_length=100)
    certificate_date: date
    expiry_date: date
    additional_info: Optional[str] = None
    is_active: bool = True


class AuditorQualificationCreate(AuditorQualificationBase):
    user_id: UUID
    status_id: UUID
    standard_ids: List[UUID] = Field(default_factory=list)


class AuditorQualificationUpdate(BaseModel):
    certification_body: Optional[str] = Field(None, max_length=255)
    certificate_number: Optional[str] = Field(None, max_length=100)
    certificate_date: Optional[date] = None
    expiry_date: Optional[date] = None
    additional_info: Optional[str] = None
    is_active: Optional[bool] = None
    status_id: Optional[UUID] = None
    standard_ids: Optional[List[UUID]] = None


class AuditorQualificationResponse(AuditorQualificationBase):
    id: UUID
    user_id: UUID
    status_id: UUID
    standards: List[QualificationStandardResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True

