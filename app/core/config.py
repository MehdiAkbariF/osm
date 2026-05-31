# app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # مقادیر اولیه پروژه
    PROJECT_NAME: str = "Iran Map API Platform"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # آدرس سرویس‌های نقشه
    NOMINATIM_URL: str
    OSRM_URL: str
    POSTGRES_URL: str
    MARTIN_URL: str
    
    # دیتابیس کاربران (SQLite) - جدید
    SQLITE_URL: str = "sqlite:///./data/users.db"

    # تنظیمات امنیتی توکن JWT
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()