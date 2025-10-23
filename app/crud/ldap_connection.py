from typing import Optional, List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.ldap_connection import LdapConnection
from app.schemas.ldap_connection import LdapConnectionCreate, LdapConnectionUpdate
from app.core.security import encrypt_value, decrypt_value


async def create_ldap_connection(db: AsyncSession, connection: LdapConnectionCreate) -> LdapConnection:
    db_connection = LdapConnection(
        name=connection.name,
        server_uri=connection.server_uri,
        bind_dn=connection.bind_dn,
        bind_password=encrypt_value(connection.bind_password),
        user_search_base=connection.user_search_base,
        enterprise_id=connection.enterprise_id,
        division_id=connection.division_id,
        is_default=connection.is_default,
        is_active=connection.is_active
    )
    db.add(db_connection)
    await db.commit()
    await db.refresh(db_connection)
    return db_connection


async def get_ldap_connection(db: AsyncSession, connection_id: UUID) -> Optional[LdapConnection]:
    stmt = select(LdapConnection).where(LdapConnection.id == connection_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_ldap_connections(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    enterprise_id: Optional[UUID] = None,
    division_id: Optional[UUID] = None,
    is_active: Optional[bool] = None
) -> List[LdapConnection]:
    stmt = select(LdapConnection)
    
    if enterprise_id is not None:
        stmt = stmt.where(LdapConnection.enterprise_id == enterprise_id)
    
    if division_id is not None:
        stmt = stmt.where(LdapConnection.division_id == division_id)
    
    if is_active is not None:
        stmt = stmt.where(LdapConnection.is_active == is_active)
    
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def update_ldap_connection(
    db: AsyncSession,
    connection_id: UUID,
    connection_update: LdapConnectionUpdate
) -> Optional[LdapConnection]:
    db_connection = await get_ldap_connection(db, connection_id)
    if not db_connection:
        return None
    
    update_data = connection_update.model_dump(exclude_unset=True)
    
    if "bind_password" in update_data:
        update_data["bind_password"] = encrypt_value(update_data["bind_password"])
    
    for field, value in update_data.items():
        setattr(db_connection, field, value)
    
    await db.commit()
    await db.refresh(db_connection)
    return db_connection


async def delete_ldap_connection(db: AsyncSession, connection_id: UUID) -> bool:
    db_connection = await get_ldap_connection(db, connection_id)
    if not db_connection:
        return False
    
    db_connection.soft_delete()
    await db.commit()
    return True


async def get_default_ldap_connection(db: AsyncSession) -> Optional[LdapConnection]:
    stmt = select(LdapConnection).where(LdapConnection.is_default == True, LdapConnection.is_active == True)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


def get_ldap_credentials(db_connection: LdapConnection) -> dict:
    return {
        "bind_password": decrypt_value(db_connection.bind_password)
    }

