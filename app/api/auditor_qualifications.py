from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.crud import auditor_qualification as crud
from app.schemas.auditor_qualification import (
    AuditorQualificationCreate,
    AuditorQualificationUpdate,
    AuditorQualificationResponse,
    QualificationStandardCreate,
    QualificationStandardUpdate,
    QualificationStandardResponse,
    StandardChapterCreate,
    StandardChapterUpdate,
    StandardChapterResponse,
)


router = APIRouter(prefix="/auditor_qualifications", tags=["auditor_qualifications"])


@router.get("/standards", response_model=List[QualificationStandardResponse])
async def get_qualification_standards(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_session)
):
    """
    Получить список стандартов квалификации.
    
    Args:
        skip: Количество записей для пропуска
        limit: Максимальное количество записей для возврата (1-100)
        is_active: Фильтр по статусу активности
        db: Сессия базы данных
    
    Returns:
        Список стандартов квалификации
    """
    standards = await crud.get_qualification_standards(
        db=db,
        skip=skip,
        limit=limit,
        is_active=is_active
    )
    return standards


@router.post("/standards", response_model=QualificationStandardResponse, status_code=status.HTTP_201_CREATED)
async def create_qualification_standard(
    standard: QualificationStandardCreate,
    db: AsyncSession = Depends(get_session)
):
    """
    Создать новый стандарт квалификации.
    
    Args:
        standard: Данные для создания стандарта
        db: Сессия базы данных
    
    Returns:
        Созданный стандарт квалификации
    """
    return await crud.create_qualification_standard(db=db, standard=standard)


@router.get("/standards/{standard_id}", response_model=QualificationStandardResponse)
async def get_qualification_standard(
    standard_id: UUID,
    db: AsyncSession = Depends(get_session)
):
    """
    Получить стандарт квалификации по ID.
    
    Args:
        standard_id: ID стандарта
        db: Сессия базы данных
    
    Returns:
        Стандарт квалификации
    
    Raises:
        HTTPException: Если стандарт не найден
    """
    standard = await crud.get_qualification_standard(db, standard_id)
    if not standard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Qualification standard not found"
        )
    return standard


@router.put("/standards/{standard_id}", response_model=QualificationStandardResponse)
async def update_qualification_standard(
    standard_id: UUID,
    standard_update: QualificationStandardUpdate,
    db: AsyncSession = Depends(get_session)
):
    """
    Обновить стандарт квалификации.
    
    Args:
        standard_id: ID стандарта
        standard_update: Данные для обновления
        db: Сессия базы данных
    
    Returns:
        Обновленный стандарт квалификации
    
    Raises:
        HTTPException: Если стандарт не найден
    """
    standard = await crud.update_qualification_standard(db, standard_id, standard_update)
    if not standard:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Qualification standard not found"
        )
    return standard


@router.delete("/standards/{standard_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_qualification_standard(
    standard_id: UUID,
    db: AsyncSession = Depends(get_session)
):
    """
    Удалить стандарт квалификации (мягкое удаление).
    
    Args:
        standard_id: ID стандарта
        db: Сессия базы данных
    
    Raises:
        HTTPException: Если стандарт не найден
    """
    success = await crud.delete_qualification_standard(db, standard_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Qualification standard not found"
        )


@router.get("/chapters", response_model=List[StandardChapterResponse])
async def get_standard_chapters(
    standard_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_session)
):
    """
    Получить список разделов стандарта.
    
    Args:
        standard_id: ID стандарта
        skip: Количество записей для пропуска
        limit: Максимальное количество записей для возврата (1-100)
        db: Сессия базы данных
    
    Returns:
        Список разделов стандарта
    """
    chapters = await crud.get_standard_chapters_by_standard(
        db=db,
        standard_id=standard_id,
        skip=skip,
        limit=limit
    )
    return chapters


@router.post("/chapters", response_model=StandardChapterResponse, status_code=status.HTTP_201_CREATED)
async def create_standard_chapter(
    chapter: StandardChapterCreate,
    db: AsyncSession = Depends(get_session)
):
    """
    Создать новый раздел стандарта.
    
    Args:
        chapter: Данные для создания раздела
        db: Сессия базы данных
    
    Returns:
        Созданный раздел стандарта
    """
    return await crud.create_standard_chapter(db=db, chapter=chapter)


@router.get("/chapters/{chapter_id}", response_model=StandardChapterResponse)
async def get_standard_chapter(
    chapter_id: UUID,
    db: AsyncSession = Depends(get_session)
):
    """
    Получить раздел стандарта по ID.
    
    Args:
        chapter_id: ID раздела
        db: Сессия базы данных
    
    Returns:
        Раздел стандарта
    
    Raises:
        HTTPException: Если раздел не найден
    """
    chapter = await crud.get_standard_chapter(db, chapter_id)
    if not chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Standard chapter not found"
        )
    return chapter


@router.put("/chapters/{chapter_id}", response_model=StandardChapterResponse)
async def update_standard_chapter(
    chapter_id: UUID,
    chapter_update: StandardChapterUpdate,
    db: AsyncSession = Depends(get_session)
):
    """
    Обновить раздел стандарта.
    
    Args:
        chapter_id: ID раздела
        chapter_update: Данные для обновления
        db: Сессия базы данных
    
    Returns:
        Обновленный раздел стандарта
    
    Raises:
        HTTPException: Если раздел не найден
    """
    chapter = await crud.update_standard_chapter(db, chapter_id, chapter_update)
    if not chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Standard chapter not found"
        )
    return chapter


@router.delete("/chapters/{chapter_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_standard_chapter(
    chapter_id: UUID,
    db: AsyncSession = Depends(get_session)
):
    """
    Удалить раздел стандарта (мягкое удаление).
    
    Args:
        chapter_id: ID раздела
        db: Сессия базы данных
    
    Raises:
        HTTPException: Если раздел не найден
    """
    success = await crud.delete_standard_chapter(db, chapter_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Standard chapter not found"
        )


@router.get("/", response_model=List[AuditorQualificationResponse])
async def get_auditor_qualifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    user_id: Optional[UUID] = None,
    status_id: Optional[UUID] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_session)
):
    """
    Получить список квалификаций аудиторов.
    
    Args:
        skip: Количество записей для пропуска
        limit: Максимальное количество записей для возврата (1-100)
        user_id: Фильтр по ID пользователя
        status_id: Фильтр по ID статуса
        is_active: Фильтр по статусу активности
        db: Сессия базы данных
    
    Returns:
        Список квалификаций аудиторов
    """
    qualifications = await crud.get_auditor_qualifications(
        db=db,
        skip=skip,
        limit=limit,
        user_id=user_id,
        status_id=status_id,
        is_active=is_active
    )
    return qualifications


@router.post("/", response_model=AuditorQualificationResponse, status_code=status.HTTP_201_CREATED)
async def create_auditor_qualification(
    qualification: AuditorQualificationCreate,
    db: AsyncSession = Depends(get_session)
):
    """
    Создать новую квалификацию аудитора.
    
    Args:
        qualification: Данные для создания квалификации
        db: Сессия базы данных
    
    Returns:
        Созданная квалификация аудитора
    """
    return await crud.create_auditor_qualification(db=db, qualification=qualification)


@router.get("/{qualification_id}", response_model=AuditorQualificationResponse)
async def get_auditor_qualification(
    qualification_id: UUID,
    db: AsyncSession = Depends(get_session)
):
    """
    Получить квалификацию аудитора по ID.
    
    Args:
        qualification_id: ID квалификации
        db: Сессия базы данных
    
    Returns:
        Квалификация аудитора
    
    Raises:
        HTTPException: Если квалификация не найдена
    """
    qualification = await crud.get_auditor_qualification(db, qualification_id)
    if not qualification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Auditor qualification not found"
        )
    return qualification


@router.put("/{qualification_id}", response_model=AuditorQualificationResponse)
async def update_auditor_qualification(
    qualification_id: UUID,
    qualification_update: AuditorQualificationUpdate,
    db: AsyncSession = Depends(get_session)
):
    """
    Обновить квалификацию аудитора.
    
    Args:
        qualification_id: ID квалификации
        qualification_update: Данные для обновления
        db: Сессия базы данных
    
    Returns:
        Обновленная квалификация аудитора
    
    Raises:
        HTTPException: Если квалификация не найдена
    """
    qualification = await crud.update_auditor_qualification(db, qualification_id, qualification_update)
    if not qualification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Auditor qualification not found"
        )
    return qualification


@router.delete("/{qualification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_auditor_qualification(
    qualification_id: UUID,
    db: AsyncSession = Depends(get_session)
):
    """
    Удалить квалификацию аудитора (мягкое удаление).
    
    Args:
        qualification_id: ID квалификации
        db: Сессия базы данных
    
    Raises:
        HTTPException: Если квалификация не найдена
    """
    success = await crud.delete_auditor_qualification(db, qualification_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Auditor qualification not found"
        )

