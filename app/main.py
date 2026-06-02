# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import Base, engine
from app.api.v1.router import api_router

# ایجاد جداول دیتابیس (اجرا یک بار در ابتدا)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="پلتفرم جامع نقشه و آدرس‌یابی ایران با قابلیت احراز هویت کاربران",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # در تولید، آدرس‌های خاص را قرار دهید
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ثبت روت‌های API
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {
        "message": "Iran Map API Platform",
        "status": "running",
        "version": settings.VERSION,
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Iran Map API"}