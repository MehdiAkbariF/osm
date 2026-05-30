from enum import Enum
from fastapi import APIRouter, HTTPException, Query
from app.services.nominatim import nominatim_service

router = APIRouter()

# تعریف حالت‌های مجاز جستجو به صورت Enum جهت ولیدیشن خودکار و منوی کشویی در Swagger
class SearchMode(str, Enum):
    global_search = "global"
    proximity_search = "proximity"
    viewport_search = "viewport"
    city_search = "city"

@router.get("/", summary="موتور جستجوی هوشمند چندحالته نقشه ایران")
async def search_address(
    q: str = Query(..., description="متن مورد جستجو (مثال: رستوران، آزادی)"),
    mode: SearchMode = Query(SearchMode.global_search, description="حالت جستجو: یکی از موارد مجاز کشویی"),
    lat: float = Query(None, description="عرض جغرافیایی (برای حالت proximity)"),
    lon: float = Query(None, description="طول جغرافیایی (برای حالت proximity)"),
    viewbox: str = Query(None, description="کادر نقشه فعلی به فرمت minLon,maxLat,maxLon,minLat (برای حالت viewport)"),
    city: str = Query(None, description="نام شهر مشخص جهت محدودسازی نتایج (برای حالت city)")
):
    # بررسی ولیدیشن منطقی پارامترها بر اساس Enum انتخاب شده
    if mode == SearchMode.proximity_search and (lat is None or lon is None):
        raise HTTPException(status_code=400, detail="برای جستجوی اطراف لوکیشن، ارسال lat و lon الزامی است.")
        
    if mode == SearchMode.viewport_search and viewbox is None:
        raise HTTPException(status_code=400, detail="برای جستجوی کادر نقشه، ارسال پارامتر viewbox الزامی است.")
        
    if mode == SearchMode.city_search and city is None:
        raise HTTPException(status_code=400, detail="برای جستجوی مقید به شهر، ارسال پارامتر city الزامی است.")

    try:
        # مقدار واقعی متنی Enum با ویژگی mode.value ارسال می‌شود
        results = nominatim_service.search_places(
            query=q,
            mode=mode.value, 
            lat=lat,
            lon=lon,
            viewbox=viewbox,
            city=city
        )
        return results
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))