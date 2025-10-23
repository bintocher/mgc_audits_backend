from typing import Optional, Dict, Any
import ldap
from ldap.ldapobject import SimpleLDAPObject
from app.core.config import settings


class LDAPService:
    def __init__(self):
        self.server_uri = getattr(settings, 'LDAP_SERVER_URI', '')
        self.bind_dn = getattr(settings, 'LDAP_BIND_DN', '')
        self.bind_password = getattr(settings, 'LDAP_BIND_PASSWORD', '')
        self.user_search_base = getattr(settings, 'LDAP_USER_SEARCH_BASE', '')
    
    async def authenticate(
        self,
        username: str,
        password: str
    ) -> Optional[Dict[str, Any]]:
        """
        Аутентификация пользователя через LDAP.
        
        Args:
            username: Имя пользователя или email
            password: Пароль
        
        Returns:
            Dict с данными пользователя или None при неудаче
        """
        if not self.server_uri:
            return None
        
        try:
            conn = ldap.initialize(self.server_uri)
            conn.set_option(ldap.OPT_REFERRALS, 0)
            
            search_filter = f"(|(sAMAccountName={username})(mail={username}))"
            
            result = conn.search_s(
                self.user_search_base,
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
            print(f"LDAP error: {e}")
            return None
        finally:
            try:
                conn.unbind()
            except:
                pass
    
    async def search_user(
        self,
        username: str
    ) -> Optional[Dict[str, Any]]:
        """
        Поиск пользователя в LDAP без проверки пароля.
        
        Args:
            username: Имя пользователя или email
        
        Returns:
            Dict с данными пользователя или None если не найден
        """
        if not self.server_uri:
            return None
        
        try:
            conn = ldap.initialize(self.server_uri)
            conn.set_option(ldap.OPT_REFERRALS, 0)
            
            if self.bind_dn and self.bind_password:
                conn.simple_bind_s(self.bind_dn, self.bind_password)
            
            search_filter = f"(|(sAMAccountName={username})(mail={username}))"
            
            result = conn.search_s(
                self.user_search_base,
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
            print(f"LDAP search error: {e}")
            return None
        finally:
            try:
                conn.unbind()
            except:
                pass


ldap_service = LDAPService()

