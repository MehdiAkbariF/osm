# app/api/v1/router.py
from fastapi import APIRouter
from app.api.v1.endpoints import (
    search, reverse, tiles, pois, auth, admin, api_keys, route, styles,
    public_locations, user_locations, admin_locations  # 🔑 وارد کردن ۳ روتر جدید تفکیک‌شده
)

api_router = APIRouter()

# ۱. ثبت روترهای دارای پیشوند داخلی
api_router.include_router(auth.router)
api_router.include_router(admin.router)
api_router.include_router(api_keys.router)
api_router.include_router(route.router)
api_router.include_router(styles.router)

# 🔑 ثبت روترهای تفکیک‌شده‌ی جدید برای MaaS لوکیشن‌ها
api_router.include_router(public_locations.router) # درگاه لوکیشن‌های عمومی نقشه و سرچ یدکچی
api_router.include_router(user_locations.router)   # درگاه پنل انبار داران شخصی
api_router.include_router(admin_locations.router)  # درگاه پنل تایید/رد ادمین سیستم

# ۲. ثبت روترهای عمومی
api_router.include_router(pois.router, prefix="/pois", tags=["POIs"])
api_router.include_router(reverse.router, prefix="/reverse", tags=["Reverse Geocoding"])
api_router.include_router(search.router, prefix="/search", tags=["Search"])
api_router.include_router(tiles.router, prefix="/tiles", tags=["Vector Tiles"])