from typing import Optional, Dict, Any
import ldap
from ldap.ldapobject import SimpleLDAPObject
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
import logging
from app.crud.ldap_connection import get_ldap_connection, get_ldap_credentials
from app.models.ldap_connection import LdapConnection

logger = logging.getLogger(__name__)


async def authenticate_ldap_user(
    connection: LdapConnection,
    username: str,
    password: str
) -> Optional[Dict[str, Any]]:
    """
    Аутентификация пользователя через LDAP.
    
    Args:
        connection: LDAP подключение
        username: Имя пользователя или email
        password: Пароль
    
    Returns:
        Dict с данными пользователя или None при неудаче
    """
    try:
        conn = ldap.initialize(connection.server_uri)
        conn.set_option(ldap.OPT_REFERRALS, 0)
        
        search_filter = f"(|(sAMAccountName={username})(mail={username}))"
        
        result = conn.search_s(
            connection.user_search_base,
            ldap.SCOPE_SUBTREE,
            search_filter,
            ['cn', 'mail', 'sAMAccountName', 'dn', 'givenName', 'sn']
        )
        
        if not result:
            return None
        
        user_dn = result[0][0]
        
        try:
            conn.simple_bind_s(user_dn, password)
        except ldap.INVALID_CREDENTIALS:
            return None
        
        attributes = result[0][1]
        
        return {
            'dn': user_dn,
            'username': attributes.get('sAMAccountName', [username])[0].decode('utf-8'),
            'email': attributes.get('mail', [username])[0].decode('utf-8'),
            'first_name': attributes.get('givenName', [''])[0].decode('utf-8'),
            'last_name': attributes.get('sn', [''])[0].decode('utf-8'),
            'cn': attributes.get('cn', [''])[0].decode('utf-8')
        }
        
    except Exception as e:
        logger.error(f"LDAP error: {e}")
        return None
    finally:
        try:
            conn.unbind()
        except:
            pass


async def search_ldap_user(
    connection: LdapConnection,
    username: str
) -> Optional[Dict[str, Any]]:
    """
    Поиск пользователя в LDAP без проверки пароля.
    
    Args:
        connection: LDAP подключение
        username: Имя пользователя или email
    
    Returns:
        Dict с данными пользователя или None если не найден
    """
    try:
        conn = ldap.initialize(connection.server_uri)
        conn.set_option(ldap.OPT_REFERRALS, 0)
        
        credentials = get_ldap_credentials(connection)
        if connection.bind_dn and credentials['bind_password']:
            conn.simple_bind_s(connection.bind_dn, credentials['bind_password'])
        
        search_filter = f"(|(sAMAccountName={username})(mail={username}))"
        
        result = conn.search_s(
            connection.user_search_base,
            ldap.SCOPE_SUBTREE,
            search_filter,
            ['cn', 'mail', 'sAMAccountName', 'dn', 'givenName', 'sn']
        )
        
        if not result:
            return None
        
        attributes = result[0][1]
        
        return {
            'dn': result[0][0],
            'username': attributes.get('sAMAccountName', [username])[0].decode('utf-8'),
            'email': attributes.get('mail', [username])[0].decode('utf-8'),
            'first_name': attributes.get('givenName', [''])[0].decode('utf-8'),
            'last_name': attributes.get('sn', [''])[0].decode('utf-8'),
            'cn': attributes.get('cn', [''])[0].decode('utf-8')
        }
        
    except Exception as e:
        logger.error(f"LDAP search error: {e}")
        return None
    finally:
        try:
            conn.unbind()
        except:
            pass


async def test_ldap_connection(db: AsyncSession, connection_id: UUID) -> dict:
    """
    Проверить подключение LDAP.
    
    Args:
        db: Сессия базы данных
        connection_id: ID подключения
    
    Returns:
        Словарь с результатом проверки
    """
    connection = await get_ldap_connection(db, connection_id)
    if not connection:
        return {
            "success": False,
            "message": "LDAP connection not found",
            "details": None
        }
    
    try:
        conn = ldap.initialize(connection.server_uri)
        conn.set_option(ldap.OPT_REFERRALS, 0)
        
        credentials = get_ldap_credentials(connection)
        conn.simple_bind_s(connection.bind_dn, credentials['bind_password'])
        
        search_filter = "(objectClass=person)"
        result = conn.search_s(
            connection.user_search_base,
            ldap.SCOPE_BASE,
            search_filter,
            []
        )
        
        connection.health_status = "ok"
        connection.error_message = None
        
        from datetime import datetime, timezone
        connection.last_checked_at = datetime.now(timezone.utc)
        
        await db.commit()
        
        return {
            "success": True,
            "message": "Connection successful",
            "details": {
                "server": connection.server_uri,
                "search_base": connection.user_search_base
            }
        }
    except ldap.INVALID_CREDENTIALS:
        error_message = "Invalid credentials"
        
        connection.health_status = "error"
        connection.error_message = error_message
        
        from datetime import datetime, timezone
        connection.last_checked_at = datetime.now(timezone.utc)
        
        await db.commit()
        
        logger.error(f"LDAP connection test failed: {error_message}")
        
        return {
            "success": False,
            "message": "Connection failed: Invalid credentials",
            "details": {
                "error": error_message
            }
        }
    except Exception as e:
        error_message = str(e)
        
        connection.health_status = "error"
        connection.error_message = error_message
        
        from datetime import datetime, timezone
        connection.last_checked_at = datetime.now(timezone.utc)
        
        await db.commit()
        
        logger.error(f"LDAP connection test failed: {error_message}")
        
        return {
            "success": False,
            "message": f"Connection failed: {error_message}",
            "details": {
                "error": error_message
            }
        }
    finally:
        try:
            conn.unbind()
        except:
            pass


async def test_email_connection(db: AsyncSession, account_id: UUID) -> dict:
    """
    Проверить подключение SMTP.
    
    Args:
        db: Сессия базы данных
        account_id: ID email аккаунта
    
    Returns:
        Словарь с результатом проверки
    """
    from app.crud.email_account import get_email_account, get_email_credentials
    
    account = await get_email_account(db, account_id)
    if not account:
        return {
            "success": False,
            "message": "Email account not found",
            "details": None
        }
    
    try:
        import smtplib
        from email.mime.text import MIMEText
        
        credentials = get_email_credentials(account)
        
        if account.use_tls:
            server = smtplib.SMTP(account.smtp_host, account.smtp_port)
            server.starttls()
        else:
            server = smtplib.SMTP(account.smtp_host, account.smtp_port)
        
        server.login(account.smtp_user, credentials['smtp_password'])
        server.quit()
        
        account.health_status = "ok"
        account.error_message = None
        
        from datetime import datetime, timezone
        account.last_checked_at = datetime.now(timezone.utc)
        
        await db.commit()
        
        return {
            "success": True,
            "message": "Connection successful",
            "details": {
                "host": account.smtp_host,
                "port": account.smtp_port,
                "from_email": account.from_email
            }
        }
    except smtplib.SMTPAuthenticationError as e:
        error_message = str(e)
        
        account.health_status = "error"
        account.error_message = error_message
        
        from datetime import datetime, timezone
        account.last_checked_at = datetime.now(timezone.utc)
        
        await db.commit()
        
        logger.error(f"Email connection test failed: {error_message}")
        
        return {
            "success": False,
            "message": "Connection failed: Authentication error",
            "details": {
                "error": error_message
            }
        }
    except Exception as e:
        error_message = str(e)
        
        account.health_status = "error"
        account.error_message = error_message
        
        from datetime import datetime, timezone
        account.last_checked_at = datetime.now(timezone.utc)
        
        await db.commit()
        
        logger.error(f"Email connection test failed: {error_message}")
        
        return {
            "success": False,
            "message": f"Connection failed: {error_message}",
            "details": {
                "error": error_message
            }
        }

