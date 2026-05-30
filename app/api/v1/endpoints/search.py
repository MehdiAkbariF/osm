from fastapi import APIRouter, HTTPException, Query
from app.services.nominatim import nominatim_service

router = APIRouter()

@router.get("/", summary="جستجوی متنی آدرس در ایران")
async def search_address(
    q: str = Query(..., description="متن جستجو (مثال: بزرگراه صدر)"),
    lat: float = Query(None, description="عرض جغرافیایی کاربر جهت اولویت‌دهی مکانی"),
    lon: float = Query(None, description="طول جغرافیایی کاربر جهت اولویت‌دهی مکانی")
):
    try:
        # فراخوانی لایه خدمات
        results = nominatim_service.search_places(query=q, lat=lat, lon=lon)
        return results
    except RuntimeError as e:
        # تبدیل خطاهای سیستمی به خطای استاندارد HTTP 502
        raise HTTPException(status_code=502, detail=str(e))