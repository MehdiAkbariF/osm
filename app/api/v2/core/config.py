from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "OSM Map Platform"
    VERSION: str = "2.0.0"

    API_V1_STR: str = "/api/v1"

    POSTGRES_URL: str = "postgresql://user:pass@localhost:5432/osm"

    JWT_SECRET: str = "change_me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    NOMINATIM_URL: str = "http://localhost:8080"
    OSRM_URL: str = "http://localhost:5000"
    MARTIN_URL: str = "http://localhost:3000"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()