from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Map API V2"
    VERSION: str = "1.0.0"  # اضافه شد
    DEBUG: bool = True  # اضافه شد
    
    # تنظیمات دیتابیس دقیقاً بر اساس docker-compose شما
    POSTGRES_USER: str = "map_admin"
    POSTGRES_PASSWORD: str = "map_secure_pass"
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: str = "5433"
    POSTGRES_DB: str = "iran_map"

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # اضافه کردن برای راحتی
    @property
    def SYNC_DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

settings = Settings()