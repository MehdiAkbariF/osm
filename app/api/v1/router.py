from fastapi import APIRouter
from app.api.v1.endpoints import search

api_router = APIRouter()

# اضافه کردن روت جستجو به روت اصلی نسخه ۱
api_router.include_router(search.router, prefix="/search", tags=["Search"])