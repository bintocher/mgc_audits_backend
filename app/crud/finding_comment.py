from typing import Optional, List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.finding_comment import FindingComment
from app.schemas.finding import FindingCommentCreate, FindingCommentUpdate


async def create_finding_comment(db: AsyncSession, comment: FindingCommentCreate) -> FindingComment:
    db_comment = FindingComment(
        finding_id=comment.finding_id,
        author_id=comment.author_id,
        text=comment.text
    )
    
    db.add(db_comment)
    await db.commit()
    await db.refresh(db_comment)
    return db_comment


async def get_finding_comment(db: AsyncSession, comment_id: UUID) -> Optional[FindingComment]:
    stmt = select(FindingComment).where(FindingComment.id == comment_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_finding_comments(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    finding_id: Optional[UUID] = None
) -> List[FindingComment]:
    stmt = select(FindingComment)
    
    if finding_id is not None:
        stmt = stmt.where(FindingComment.finding_id == finding_id)
    
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def update_finding_comment(
    db: AsyncSession,
    comment_id: UUID,
    comment_update: FindingCommentUpdate
) -> Optional[FindingComment]:
    db_comment = await get_finding_comment(db, comment_id)
    if not db_comment:
        return None
    
    update_data = comment_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_comment, field, value)
    
    await db.commit()
    await db.refresh(db_comment)
    return db_comment


async def delete_finding_comment(db: AsyncSession, comment_id: UUID) -> bool:
    db_comment = await get_finding_comment(db, comment_id)
    if not db_comment:
        return False
    
    db_comment.soft_delete()
    await db.commit()
    return True

