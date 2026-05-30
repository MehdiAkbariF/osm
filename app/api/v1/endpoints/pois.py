from fastapi import APIRouter, HTTPException, Query
from app.services.postgis_service import postgis_service

router = APIRouter()

@router.get("/nearest", summary="یافتن نزدیک‌ترین مکان‌های اطراف کاربر (POI)")
async def get_nearest_pois(
    lat: float = Query(..., description="عرض جغرافیایی کاربر"),
    lon: float = Query(..., description="طول جغرافیایی کاربر"),
    category: str = Query(None, description="دسته‌بندی مکان (مثال: fuel, atm, hospital, restaurant)"),
    radius: float = Query(5000.0, description="شعاع جستجو به متر (پیش‌فرض: ۵۰۰۰ متر)"),
    limit: int = Query(10, description="حداکثر تعداد نتایج (پیش‌فرض: ۱۰)")
):
    # فراخوانی متد فضایی PostGIS
    results = postgis_service.get_nearest_pois(
        lat=lat,
        lon=lon,
        category=category,
        radius_meters=radius,
        limit=limit
    )
    
    if not results:
        return []
        
    return results