from datetime import date
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field


class ReportFilter(BaseModel):
    enterprise_id: Optional[UUID] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    status_id: Optional[UUID] = None
    finding_type: Optional[str] = Field(None, pattern="^(CAR1|CAR2|OFI)$")


class FindingReportRow(BaseModel):
    finding_number: int
    audit_number: str
    audit_title: str
    title: str
    finding_type: str
    process_name: str
    status_name: str
    resolver_name: str
    approver_name: Optional[str]
    deadline: date
    closing_date: Optional[date]
    created_at: date


class ProcessReportRow(BaseModel):
    process_name: str
    total_findings: int
    car1_count: int
    car2_count: int
    ofi_count: int
    closed_count: int
    overdue_count: int


class SolverReportRow(BaseModel):
    solver_name: str
    total_findings: int
    active_findings: int
    overdue_findings: int
    closed_findings: int


class FindingsReportResponse(BaseModel):
    total: int
    data: List[FindingReportRow]


class ProcessReportResponse(BaseModel):
    total: int
    data: List[ProcessReportRow]


class SolverReportResponse(BaseModel):
    total: int
    data: List[SolverReportRow]

