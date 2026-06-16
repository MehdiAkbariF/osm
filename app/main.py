from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import engine
from app.api.v2.models.base import Base
from app.api.v2.models import user, store, warehouse, inventory, product, setting
# IMPORTANT: همه مدل‌ها را import کن تا ثبت شوند


from app.api.v2.router import router as v2_router

# ایجاد جداول
print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("✅ Database tables created/verified")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(v2_router, prefix="/api/v2")

@app.get("/")
def root():
    return {"status": "ok", "project": settings.PROJECT_NAME}