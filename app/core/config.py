from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    DATABASE_URL: str
    REDIS_URL: str = "redis://localhost:6379/0"

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    SETTINGS_ENCRYPTION_KEY: str
    
    MAIL_USERNAME: str = ""
    MAIL_PASSWORD: str = ""
    MAIL_FROM: str = ""
    MAIL_FROM_NAME: str = "MGC Audits"
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.yandex.ru"
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    
    FRONTEND_URL: str = "http://localhost:3000"
    
    LDAP_SERVER_URI: str = ""
    LDAP_BIND_DN: str = ""
    LDAP_BIND_PASSWORD: str = ""
    LDAP_USER_SEARCH_BASE: str = ""
    
    TELEGRAM_BOT_TOKEN: str = ""


settings = Settings()

