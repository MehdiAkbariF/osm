from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# IMPORTANT: Import Base از models.base
from app.api.v2.models.base import Base

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency برای استفاده در Endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()