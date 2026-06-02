# app/api/v1/endpoints/route.py
from fastapi import APIRouter, Depends, Query
from app.api.v1.dependencies import get_api_key
from app.models.api_key import APIKey
from app.services.osrm_service import osrm_service

router = APIRouter(prefix="/route", tags=["Routing"])

@router.get("/directions", summary="مسیریابی هوشمند و سخنگوی جاده‌ای ایران")
async def get_directions(
    start_lat: float = Query(..., description="عرض جغرافیایی مبدا"),
    start_lon: float = Query(..., description="طول جغرافیایی مبدا"),
    end_lat: float = Query(..., description="عرض جغرافیایی مقصد"),
    end_lon: float = Query(..., description="طول جغرافیایی مقصد"),
    api_key: APIKey = Depends(get_api_key) # 🔒 تفویض امنیت و بررسی اعتبار کلید دسترسی و Rate Limit
):
    """
    استعلام مسیر جاده‌ای خودرویی بین دو نقطه مبدا و مقصد به همراه لیست گام‌به‌گام خیابان‌ها
    """
    route_data = await osrm_service.get_route(
        start_lat=start_lat,
        start_lon=start_lon,
        end_lat=end_lat,
        end_lon=end_lon
    )
    return route_data