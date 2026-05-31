# app/api/v1/router.py
from fastapi import APIRouter
from app.api.v1.endpoints import search, reverse, tiles, pois, auth, admin, locations, api_keys

api_router = APIRouter()

# ۱. کنترلرهایی که پیشوند (Prefix) و تگ (Tag) درون خود فایلشان تعریف شده است
api_router.include_router(auth.router)
api_router.include_router(admin.router)
api_router.include_router(locations.router)
api_router.include_router(api_keys.router)  # روتر جدید کلیدهای دسترسی

# ۲. کنترلرهایی که پیشوند و تگ آن‌ها باید در روتر اصلی تعیین شوند
api_router.include_router(pois.router, prefix="/pois", tags=["POIs"])
api_router.include_router(reverse.router, prefix="/reverse", tags=["Reverse Geocoding"])
api_router.include_router(search.router, prefix="/search", tags=["Search"])
api_router.include_router(tiles.router, prefix="/tiles", tags=["Vector Tiles"])