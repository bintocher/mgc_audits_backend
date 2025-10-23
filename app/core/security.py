from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from cryptography.fernet import Fernet
import base64
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


def generate_password() -> str:
    import secrets
    import string
    
    words = [
        "дом", "кот", "мир", "лук", "шар", "рис", "луг", "пар", "вид", "дуб",
        "мел", "лес", "мост", "стол", "кран", "пруд", "класс", "лист", "корабль", "труд"
    ]
    
    word1 = secrets.choice(words)
    word2 = secrets.choice(words)
    number = secrets.randbelow(100)
    
    return f"{word1.capitalize()}-{word2.capitalize()}-{number}"


def get_encryption_key() -> bytes:
    key = settings.SETTINGS_ENCRYPTION_KEY.encode()
    key_b64 = base64.urlsafe_b64encode(key.ljust(32)[:32])
    return key_b64


def encrypt_value(value: str) -> str:
    f = Fernet(get_encryption_key())
    encrypted_value = f.encrypt(value.encode())
    return encrypted_value.decode()


def decrypt_value(encrypted_value: str) -> str:
    f = Fernet(get_encryption_key())
    decrypted_value = f.decrypt(encrypted_value.encode())
    return decrypted_value.decode()

