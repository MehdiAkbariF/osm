from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.core.config import settings
from app.core.database import engine
from app.api.v2.models.base import Base
from app.api.v2.models import user, store, warehouse, inventory, product, setting
# IMPORTANT: همه مدل‌ها را import کن تا ثبت شوند

from app.api.v2.router import router as v2_router

# ============================================
# ایجاد جداول دیتابیس با مدیریت خطا
# ============================================
print("🚀 Creating database tables...")
try:
    # اطمینان از اینکه همه مدل‌ها ثبت شده‌اند
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created/verified successfully")
except Exception as e:
    print(f"❌ Error creating database tables: {str(e)}")
    print("⚠️ Please check your database connection and run migrations if needed.")

# ============================================
# ایجاد اپلیکیشن FastAPI
# ============================================
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    description="""
    🗺️ **Map Platform API v2**
    
    پلتفرم نقشه‌برداری و لجستیک یدکچی
    
    ## Features:
    * **نقشه برداری** - تایل‌های برداری و رستری
    * **جستجو** - جستجوی هوشمند مکانی با فیلتر شعاعی
    * **مسیریابی** - مسیریابی جاده‌ای و بهینه‌سازی چندمقصدی
    * **مدیریت فروشگاه** - مدیریت فروشگاه‌ها و انبارها
    * **مدیریت موجودی** - سیستم مدیریت موجودی انبار
    * **تنظیمات پویا** - تنظیمات لحظه‌ای نقشه و کارتوگرافی
    """
)

# ============================================
# تنظیمات CORS
# ============================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:8000",
        "*"  # برای توسعه، در production محدود کنید
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# ثبت مسیرهای API
# ============================================
app.include_router(v2_router, prefix="/api/v2")

# ============================================
# سرویس فایل‌های استاتیک (در صورت نیاز)
# ============================================
# اگر پوشه static وجود دارد
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# ============================================
# مسیرهای سلامت و اطلاعات
# ============================================

@app.get("/")
async def root():
    """
    🏠 **صفحه اصلی API**
    
    اطلاعات کلی درباره سرویس و وضعیت سیستم
    """
    return {
        "status": "online",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
        "api_v2": "/api/v2",
        "timestamp": __import__("datetime").datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """
    💚 **بررسی سلامت سرویس‌ها**
    
    وضعیت اتصال به دیتابیس و سرویس‌های جانبی را بررسی می‌کند
    """
    health_status = {
        "status": "healthy",
        "services": {
            "api": "online",
            "database": "checking..."
        },
        "timestamp": __import__("datetime").datetime.now().isoformat()
    }
    
    # بررسی اتصال به دیتابیس
    try:
        from app.core.database import SessionLocal
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        health_status["services"]["database"] = "connected"
    except Exception as e:
        health_status["services"]["database"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    return health_status

@app.get("/api-info")
async def api_info():
    """
    📚 **اطلاعات کامل API**
    
    لیست کامل اندپوینت‌های موجود و توضیحات آنها
    """
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "endpoints": {
            "map": {
                "styles": "/api/v2/map/styles/default",
                "tiles": "/api/v2/map/tiles/{z}/{x}/{y}",
                "raster": "/api/v2/map/raster/{z}/{x}/{y}",
                "terrain": "/api/v2/map/terrain/{z}/{x}/{y}",
                "search": "/api/v2/map/search?q={query}&lat={lat}&lon={lon}",
                "reverse": "/api/v2/map/reverse?lat={lat}&lon={lon}",
                "route": "/api/v2/map/route (POST)",
                "traffic-zones": "/api/v2/map/traffic-zones"
            },
            "auth": {
                "login": "/api/v2/auth/login (POST)",
                "logout": "/api/v2/auth/logout (POST)",
                "me": "/api/v2/auth/me (GET)"
            },
            "stores": {
                "list": "/api/v2/stores (GET)",
                "create": "/api/v2/stores (POST)",
                "detail": "/api/v2/stores/{store_id} (GET)",
                "update": "/api/v2/stores/{store_id} (PUT)",
                "delete": "/api/v2/stores/{store_id} (DELETE)"
            },
            "warehouses": {
                "list": "/api/v2/warehouses/{store_id} (GET)",
                "create": "/api/v2/warehouses/{store_id} (POST)",
                "detail": "/api/v2/warehouses/detail/{warehouse_id} (GET)",
                "update": "/api/v2/warehouses/{warehouse_id} (PUT)",
                "delete": "/api/v2/warehouses/{warehouse_id} (DELETE)"
            },
            "inventory": {
                "list": "/api/v2/inventory/{warehouse_id} (GET)",
                "create": "/api/v2/inventory/{warehouse_id} (POST)"
            },
            "settings": {
                "get": "/api/v2/settings (GET)",
                "update": "/api/v2/settings (PUT)"
            }
        }
    }

@app.on_event("startup")
async def startup_event():
    """
    🚀 **رویداد راه‌اندازی سرور**
    
    کارهای اولیه هنگام استارت سرور
    """
    print("=" * 60)
    print(f"🚀 {settings.PROJECT_NAME} v{settings.VERSION} is starting...")
    print(f"📡 API Docs: http://localhost:8000/docs")
    print(f"🗺️  Map API: http://localhost:8000/api/v2")
    print("=" * 60)

@app.on_event("shutdown")
async def shutdown_event():
    """
    🛑 **رویداد خاموش‌سازی سرور**
    """
    print("=" * 60)
    print("🛑 Shutting down server...")
    print("=" * 60)

# ============================================
# هندلر خطاهای سفارشی
# ============================================

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    🛡️ **هندلر خطاهای HTTP**
    
    مدیریت یکپارچه خطاها با فرمت استاندارد
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.status_code,
                "message": exc.detail,
                "path": request.url.path,
                "method": request.method,
                "timestamp": __import__("datetime").datetime.now().isoformat()
            }
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    🛡️ **هندلر خطاهای عمومی**
    
    مدیریت خطاهای پیش‌بینی‌نشده
    """
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": 500,
                "message": "Internal server error",
                "detail": str(exc) if settings.DEBUG else "An unexpected error occurred",
                "path": request.url.path,
                "timestamp": __import__("datetime").datetime.now().isoformat()
            }
        }
    )

# ============================================
# اگر فایل به عنوان اسکریپت اصلی اجرا شد
# ============================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )