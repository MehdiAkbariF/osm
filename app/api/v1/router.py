# app/api/v1/router.py
from fastapi import APIRouter
from app.api.v1.endpoints import search, reverse, tiles, pois, auth, admin, locations

api_router = APIRouter()

# ========== احراز هویت و مدیریت کاربران ==========
api_router.include_router(auth.router)
api_router.include_router(admin.router)

# ========== سرویس‌های نقشه و مکانیابی ==========
api_router.include_router(search.router, prefix="/search", tags=["Search"])
api_router.include_router(reverse.router, prefix="/reverse", tags=["Reverse Geocoding"])
api_router.include_router(tiles.router, prefix="/tiles", tags=["Tiles"])
api_router.include_router(pois.router, prefix="/pois", tags=["POIs"])

# ========== مدیریت موقعیت‌های مکانی (جدید) ==========
api_router.include_router(locations.router)