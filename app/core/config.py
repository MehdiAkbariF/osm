from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # مقادیر اولیه پروژه
    PROJECT_NAME: str = "Iran Map API Platform"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # آدرس سرویس‌های نقشه (که از فایل .env خوانده می‌شوند)
    NOMINATIM_URL: str
    OSRM_URL: str
    POSTGRES_URL: str
    MARTIN_URL: str

    # تنظیمات نحوه خواندن فایل .env
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

# ایجاد یک شیء (Object) یکتا از کلاس تنظیمات برای استفاده در کل پلتفرم
settings = Settings()