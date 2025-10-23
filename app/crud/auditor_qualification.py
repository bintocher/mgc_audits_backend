from typing import Optional, List
from uuid import UUID
from datetime import date
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.auditor_qualification import AuditorQualification
from app.models.qualification_standard import QualificationStandard, StandardChapter
from app.schemas.auditor_qualification import (
    AuditorQualificationCreate,
    AuditorQualificationUpdate,
    QualificationStandardCreate,
    QualificationStandardUpdate,
    StandardChapterCreate,
    StandardChapterUpdate,
)


async def create_qualification_standard(db: AsyncSession, standard: QualificationStandardCreate) -> QualificationStandard:
    db_standard = QualificationStandard(
        name=standard.name,
        code=standard.code,
        description=standard.description,
        is_active=standard.is_active
    )
    db.add(db_standard)
    await db.commit()
    await db.refresh(db_standard)
    return db_standard


async def get_qualification_standard(db: AsyncSession, standard_id: UUID) -> Optional[QualificationStandard]:
    stmt = select(QualificationStandard).where(QualificationStandard.id == standard_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_qualification_standards(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None
) -> List[QualificationStandard]:
    stmt = select(QualificationStandard)
    
    if is_active is not None:
        stmt = stmt.where(QualificationStandard.is_active == is_active)
    
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def update_qualification_standard(
    db: AsyncSession,
    standard_id: UUID,
    standard_update: QualificationStandardUpdate
) -> Optional[QualificationStandard]:
    db_standard = await get_qualification_standard(db, standard_id)
    if not db_standard:
        return None
    
    update_data = standard_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_standard, field, value)
    
    await db.commit()
    await db.refresh(db_standard)
    return db_standard


async def delete_qualification_standard(db: AsyncSession, standard_id: UUID) -> bool:
    db_standard = await get_qualification_standard(db, standard_id)
    if not db_standard:
        return False
    
    db_standard.soft_delete()
    await db.commit()
    return True


async def create_standard_chapter(db: AsyncSession, chapter: StandardChapterCreate) -> StandardChapter:
    db_chapter = StandardChapter(
        standard_id=chapter.standard_id,
        name=chapter.name,
        code=chapter.code,
        description=chapter.description,
        is_active=chapter.is_active
    )
    db.add(db_chapter)
    await db.commit()
    await db.refresh(db_chapter)
    return db_chapter


async def get_standard_chapter(db: AsyncSession, chapter_id: UUID) -> Optional[StandardChapter]:
    stmt = select(StandardChapter).where(StandardChapter.id == chapter_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_standard_chapters_by_standard(
    db: AsyncSession,
    standard_id: UUID,
    skip: int = 0,
    limit: int = 100
) -> List[StandardChapter]:
    stmt = select(StandardChapter).where(StandardChapter.standard_id == standard_id)
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def update_standard_chapter(
    db: AsyncSession,
    chapter_id: UUID,
    chapter_update: StandardChapterUpdate
) -> Optional[StandardChapter]:
    db_chapter = await get_standard_chapter(db, chapter_id)
    if not db_chapter:
        return None
    
    update_data = chapter_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_chapter, field, value)
    
    await db.commit()
    await db.refresh(db_chapter)
    return db_chapter


async def delete_standard_chapter(db: AsyncSession, chapter_id: UUID) -> bool:
    db_chapter = await get_standard_chapter(db, chapter_id)
    if not db_chapter:
        return False
    
    db_chapter.soft_delete()
    await db.commit()
    return True


async def create_auditor_qualification(
    db: AsyncSession,
    qualification: AuditorQualificationCreate
) -> AuditorQualification:
    db_qualification = AuditorQualification(
        user_id=qualification.user_id,
        status_id=qualification.status_id,
        certification_body=qualification.certification_body,
        certificate_number=qualification.certificate_number,
        certificate_date=qualification.certificate_date,
        expiry_date=qualification.expiry_date,
        additional_info=qualification.additional_info,
        is_active=qualification.is_active
    )
    
    if qualification.standard_ids:
        stmt = select(QualificationStandard).where(QualificationStandard.id.in_(qualification.standard_ids))
        result = await db.execute(stmt)
        standards = list(result.scalars().all())
        db_qualification.standards = standards
    
    db.add(db_qualification)
    await db.commit()
    await db.refresh(db_qualification)
    return db_qualification


async def get_auditor_qualification(db: AsyncSession, qualification_id: UUID) -> Optional[AuditorQualification]:
    stmt = select(AuditorQualification).where(AuditorQualification.id == qualification_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_auditor_qualifications(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[UUID] = None,
    status_id: Optional[UUID] = None,
    is_active: Optional[bool] = None
) -> List[AuditorQualification]:
    stmt = select(AuditorQualification)
    
    if user_id is not None:
        stmt = stmt.where(AuditorQualification.user_id == user_id)
    
    if status_id is not None:
        stmt = stmt.where(AuditorQualification.status_id == status_id)
    
    if is_active is not None:
        stmt = stmt.where(AuditorQualification.is_active == is_active)
    
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def update_auditor_qualification(
    db: AsyncSession,
    qualification_id: UUID,
    qualification_update: AuditorQualificationUpdate
) -> Optional[AuditorQualification]:
    db_qualification = await get_auditor_qualification(db, qualification_id)
    if not db_qualification:
        return None
    
    update_data = qualification_update.model_dump(exclude_unset=True)
    
    if "standard_ids" in update_data:
        standard_ids = update_data.pop("standard_ids")
        if standard_ids is not None:
            stmt = select(QualificationStandard).where(QualificationStandard.id.in_(standard_ids))
            result = await db.execute(stmt)
            standards = list(result.scalars().all())
            db_qualification.standards = standards
    
    for field, value in update_data.items():
        setattr(db_qualification, field, value)
    
    await db.commit()
    await db.refresh(db_qualification)
    return db_qualification


async def delete_auditor_qualification(db: AsyncSession, qualification_id: UUID) -> bool:
    db_qualification = await get_auditor_qualification(db, qualification_id)
    if not db_qualification:
        return False
    
    db_qualification.soft_delete()
    await db.commit()
    return True


async def check_auditor_qualification(
    db: AsyncSession,
    user_id: UUID,
    standard_ids: List[UUID]
) -> bool:
    stmt = select(AuditorQualification).where(
        AuditorQualification.user_id == user_id,
        AuditorQualification.is_active == True
    )
    result = await db.execute(stmt)
    qualifications = list(result.scalars().all())
    
    for qualification in qualifications:
        user_standard_ids = [standard.id for standard in qualification.standards]
        if all(std_id in user_standard_ids for std_id in standard_ids):
            if qualification.expiry_date >= date.today():
                return True
    
    return False

