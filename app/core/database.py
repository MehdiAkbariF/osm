# app/core/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# اتصال به SQLite برای ذخیره اطلاعات کاربران
# SQLite فایل سبکی است که در کنار پروژه قرار می‌گیرد
engine = create_engine(
    "sqlite:///./data/users.db",  # مسیر ذخیره فایل دیتابیس
    connect_args={"check_same_thread": False}  # لازم برای FastAPI
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# تابع وابستگی (Dependency) برای دریافت نشست دیتابیس در هر درخواست
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()