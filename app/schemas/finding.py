from datetime import date, datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, model_validator


class FindingBase(BaseModel):
    audit_id: UUID
    enterprise_id: UUID
    title: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    process_id: UUID
    status_id: UUID
    finding_type: str = Field(..., pattern="^(CAR1|CAR2|OFI)$")
    resolver_id: UUID
    approver_id: Optional[UUID] = None
    deadline: date

    why_1: Optional[str] = None
    why_2: Optional[str] = None
    why_3: Optional[str] = None
    why_4: Optional[str] = None
    why_5: Optional[str] = None

    immediate_action: Optional[str] = None
    root_cause: Optional[str] = None
    long_term_action: Optional[str] = None
    action_verification: Optional[str] = None
    preventive_measures: Optional[str] = None


class FindingCreate(FindingBase):
    created_by_id: UUID
    
    @model_validator(mode='after')
    def validate_car1_fields(self):
        """Валидация для CAR1."""
        if self.finding_type == 'CAR1':
            why_fields = [self.why_1, self.why_2, self.why_3, self.why_4, self.why_5]
            why_count = sum(1 for field in why_fields if field is not None and field.strip())
            
            if why_count < 3:
                raise ValueError("Для CAR1 необходимо заполнить минимум 3 поля почему (why_1-why_5)")
            
            if not self.immediate_action or not self.immediate_action.strip():
                raise ValueError("Для CAR1 поле immediate_action обязательно")
            
            if not self.root_cause or not self.root_cause.strip():
                raise ValueError("Для CAR1 поле root_cause обязательно")
            
            if not self.long_term_action or not self.long_term_action.strip():
                raise ValueError("Для CAR1 поле long_term_action обязательно")
            
            if not self.action_verification or not self.action_verification.strip():
                raise ValueError("Для CAR1 поле action_verification обязательно")
            
            if not self.preventive_measures or not self.preventive_measures.strip():
                raise ValueError("Для CAR1 поле preventive_measures обязательно")
        
        return self
    
    @model_validator(mode='after')
    def validate_car2_fields(self):
        """Валидация для CAR2."""
        if self.finding_type == 'CAR2':
            why_fields = [self.why_1, self.why_2, self.why_3, self.why_4, self.why_5]
            why_count = sum(1 for field in why_fields if field is not None and field.strip())
            
            if why_count < 3:
                raise ValueError("Для CAR2 необходимо заполнить минимум 3 поля почему (why_1-why_5)")
            
            if not self.immediate_action or not self.immediate_action.strip():
                raise ValueError("Для CAR2 поле immediate_action обязательно")
        
        return self


class FindingUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = Field(None, min_length=1)
    process_id: Optional[UUID] = None
    status_id: Optional[UUID] = None
    finding_type: Optional[str] = Field(None, pattern="^(CAR1|CAR2|OFI)$")
    resolver_id: Optional[UUID] = None
    approver_id: Optional[UUID] = None
    deadline: Optional[date] = None
    closing_date: Optional[date] = None

    why_1: Optional[str] = None
    why_2: Optional[str] = None
    why_3: Optional[str] = None
    why_4: Optional[str] = None
    why_5: Optional[str] = None

    immediate_action: Optional[str] = None
    root_cause: Optional[str] = None
    long_term_action: Optional[str] = None
    action_verification: Optional[str] = None
    preventive_measures: Optional[str] = None


class FindingResponse(FindingBase):
    id: UUID
    finding_number: int
    closing_date: Optional[date] = None
    created_by_id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    audit: Optional[dict] = None
    enterprise: Optional[dict] = None
    process: Optional[dict] = None
    status: Optional[dict] = None
    resolver: Optional[dict] = None
    approver: Optional[dict] = None
    creator: Optional[dict] = None

    class Config:
        from_attributes = True


class FindingDelegationBase(BaseModel):
    finding_id: UUID
    from_user_id: UUID
    to_user_id: UUID
    reason: str = Field(..., min_length=1)


class FindingDelegationCreate(FindingDelegationBase):
    pass


class FindingDelegationResponse(FindingDelegationBase):
    id: UUID
    delegated_at: datetime
    revoked_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    finding: Optional[dict] = None
    from_user: Optional[dict] = None
    to_user: Optional[dict] = None

    class Config:
        from_attributes = True


class FindingCommentBase(BaseModel):
    finding_id: UUID
    text: str = Field(..., min_length=1)


class FindingCommentCreate(FindingCommentBase):
    author_id: UUID


class FindingCommentUpdate(BaseModel):
    text: Optional[str] = Field(None, min_length=1)


class FindingCommentResponse(FindingCommentBase):
    id: UUID
    author_id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    finding: Optional[dict] = None
    author: Optional[dict] = None

    class Config:
        from_attributes = True

