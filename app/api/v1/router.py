# در فایل app/api/v1/router.py
from fastapi import APIRouter
from app.api.v1.endpoints import search, reverse, tiles, pois, auth, admin, locations, api_keys, route, styles  # اضافه شدن styles به ایمپورت‌ها

api_router = APIRouter()

# ثبت روترها
api_router.include_router(auth.router)
api_router.include_router(admin.router)
api_router.include_router(locations.router)
api_router.include_router(api_keys.router)
api_router.include_router(route.router)
api_router.include_router(styles.router)  # 🔑 ثبت روتر جدید سرویس‌دهی استایل‌ها

api_router.include_router(pois.router, prefix="/pois", tags=["POIs"])
api_router.include_router(reverse.router, prefix="/reverse", tags=["Reverse Geocoding"])
api_router.include_router(search.router, prefix="/search", tags=["Search"])
api_router.include_router(tiles.router, prefix="/tiles", tags=["Vector Tiles"])