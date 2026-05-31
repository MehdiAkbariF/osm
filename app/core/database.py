import os
import yaml
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# یافتن مسیر پوشه اصلی پروژه (سه پوشه بالاتر از فایل جاری)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
config_path = os.path.join(BASE_DIR, "config.yaml")

connection_string = None

# تلاش برای خواندن رشته اتصال مستقیم از فایل config.yaml
if os.path.exists(config_path):
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config_data = yaml.safe_load(f)
            connection_string = config_data.get("postgres", {}).get("connection_string")
    except Exception as e:
        print(f"⚠️ خطایی در خواندن فایل config.yaml رخ داد: {e}")

# اگر در فایل yaml پیدا نشد، از متغیرهای محیطی سیستم یا یک مقدار پیش‌فرض استفاده شود
if not connection_string:
    connection_string = os.getenv(
        "DATABASE_URL", 
        "postgresql://map_admin:map_secure_pass@localhost:5433/iran_map"
    )

# اصلاح پیشوند برای سازگاری با SQLAlchemy
if connection_string.startswith("postgres://"):
    connection_string = connection_string.replace("postgres://", "postgresql://", 1)

# ایجاد موتور اتصال به PostgreSQL
engine = create_engine(
    connection_string,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()