from datetime import date
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field


class DashboardStatsResponse(BaseModel):
    total_audits: int = Field(..., description="Общее количество аудитов")
    total_findings: int = Field(..., description="Общее количество несоответствий")
    active_findings: int = Field(..., description="Количество активных несоответствий")
    overdue_findings: int = Field(..., description="Количество просроченных несоответствий")
    total_users: int = Field(..., description="Общее количество пользователей")
    active_users: int = Field(..., description="Количество активных пользователей")


class MyTaskResponse(BaseModel):
    active_findings_count: int = Field(..., description="Количество активных несоответствий пользователя")
    upcoming_audits_count: int = Field(..., description="Количество предстоящих аудитов пользователя")
    overdue_findings_count: int = Field(..., description="Количество просроченных несоответствий пользователя")


class FindingInfo(BaseModel):
    id: UUID
    finding_number: int
    title: str
    deadline: date
    status: str
    audit_title: str


class AuditInfo(BaseModel):
    id: UUID
    audit_number: str
    title: str
    audit_date_from: date
    audit_date_to: date
    status: str


class MyTasksDetailResponse(BaseModel):
    active_findings: List[FindingInfo] = Field(default_factory=list, description="Список активных несоответствий")
    upcoming_audits: List[AuditInfo] = Field(default_factory=list, description="Список предстоящих аудитов")
    overdue_findings: List[FindingInfo] = Field(default_factory=list, description="Список просроченных несоответствий")

