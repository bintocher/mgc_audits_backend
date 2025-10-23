from typing import Optional
from uuid import UUID
from datetime import date
from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.crud import report as crud_report
from app.schemas.report import (
    ReportFilter,
    FindingsReportResponse,
    ProcessReportResponse,
    SolverReportResponse
)
from app.services.export import (
    export_findings_to_excel,
    export_process_to_excel,
    export_solver_to_excel
)


router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/findings", response_model=FindingsReportResponse)
async def get_findings_report(
    enterprise_id: Optional[UUID] = Query(None, description="Фильтр по предприятию"),
    date_from: Optional[date] = Query(None, description="Начальная дата"),
    date_to: Optional[date] = Query(None, description="Конечная дата"),
    status_id: Optional[UUID] = Query(None, description="Фильтр по статусу"),
    finding_type: Optional[str] = Query(None, description="Тип несоответствия (CAR1, CAR2, OFI)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(1000, ge=1, le=10000),
    db: AsyncSession = Depends(get_session)
):
    """
    Получить отчет по несоответствиям.
    
    Returns:
        Отчет по несоответствиям с фильтрацией и пагинацией
    """
    data, total = await crud_report.get_findings_report(
        db=db,
        enterprise_id=enterprise_id,
        date_from=date_from,
        date_to=date_to,
        status_id=status_id,
        finding_type=finding_type,
        skip=skip,
        limit=limit
    )
    
    return FindingsReportResponse(total=total, data=data)


@router.get("/findings/export")
async def export_findings_report(
    enterprise_id: Optional[UUID] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    status_id: Optional[UUID] = Query(None),
    finding_type: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_session)
):
    """
    Экспортировать отчет по несоответствиям в Excel.
    
    Returns:
        Excel файл
    """
    data, _ = await crud_report.get_findings_report(
        db=db,
        enterprise_id=enterprise_id,
        date_from=date_from,
        date_to=date_to,
        status_id=status_id,
        finding_type=finding_type,
        skip=0,
        limit=10000
    )
    
    excel_file = export_findings_to_excel(data)
    
    return Response(
        content=excel_file.read(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=findings_report_{date.today().isoformat()}.xlsx"
        }
    )


@router.get("/by_processes", response_model=ProcessReportResponse)
async def get_process_report(
    enterprise_id: Optional[UUID] = Query(None, description="Фильтр по предприятию"),
    date_from: Optional[date] = Query(None, description="Начальная дата"),
    date_to: Optional[date] = Query(None, description="Конечная дата"),
    db: AsyncSession = Depends(get_session)
):
    """
    Получить отчет по процессам.
    
    Returns:
        Отчет по процессам с группировкой несоответствий
    """
    data = await crud_report.get_process_report(
        db=db,
        enterprise_id=enterprise_id,
        date_from=date_from,
        date_to=date_to
    )
    
    return ProcessReportResponse(total=len(data), data=data)


@router.get("/by_processes/export")
async def export_process_report(
    enterprise_id: Optional[UUID] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_session)
):
    """
    Экспортировать отчет по процессам в Excel.
    
    Returns:
        Excel файл
    """
    data = await crud_report.get_process_report(
        db=db,
        enterprise_id=enterprise_id,
        date_from=date_from,
        date_to=date_to
    )
    
    excel_file = export_process_to_excel(data)
    
    return Response(
        content=excel_file.read(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=process_report_{date.today().isoformat()}.xlsx"
        }
    )


@router.get("/by_solvers", response_model=SolverReportResponse)
async def get_solver_report(
    enterprise_id: Optional[UUID] = Query(None, description="Фильтр по предприятию"),
    date_from: Optional[date] = Query(None, description="Начальная дата"),
    date_to: Optional[date] = Query(None, description="Конечная дата"),
    db: AsyncSession = Depends(get_session)
):
    """
    Получить отчет по исполнителям.
    
    Returns:
        Отчет по исполнителям с группировкой несоответствий
    """
    data = await crud_report.get_solver_report(
        db=db,
        enterprise_id=enterprise_id,
        date_from=date_from,
        date_to=date_to
    )
    
    return SolverReportResponse(total=len(data), data=data)


@router.get("/by_solvers/export")
async def export_solver_report(
    enterprise_id: Optional[UUID] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_session)
):
    """
    Экспортировать отчет по исполнителям в Excel.
    
    Returns:
        Excel файл
    """
    data = await crud_report.get_solver_report(
        db=db,
        enterprise_id=enterprise_id,
        date_from=date_from,
        date_to=date_to
    )
    
    excel_file = export_solver_to_excel(data)
    
    return Response(
        content=excel_file.read(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=solver_report_{date.today().isoformat()}.xlsx"
        }
    )

