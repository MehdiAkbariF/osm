# c:\Users\Raven\OSM\app\api\v2\services\routing_service.py
import httpx
from fastapi import HTTPException

# فراخوانی آدرس کانتینر داکر OSRM فعال روی پورت 5000 سیستم شما
OSRM_URL = "http://127.0.0.1:5000"

async def get_route(
    start_lat: float,
    start_lon: float,
    end_lat: float,
    end_lon: float
):
    # ۱. تعریف ساختار استاندارد آدرس‌دهی سرویس خودرویی OSRM
    url = f"{OSRM_URL}/route/v1/driving/{start_lon},{start_lat};{end_lon},{end_lat}"

    async with httpx.AsyncClient() as client:
        try:
            # ۲. ارسال پارامترهای حیاتی جهت استخراج هندسه مسیر و لیست کامل گام‌ها (Steps)
            response = await client.get(
                url,
                params={
                    "overview": "full",
                    "geometries": "geojson",
                    "steps": "true" # 🔴 فوق‌العاده حیاتی برای رندر لیست خیابان‌های مسیر در فرانت‌اَند
                },
                timeout=12.0
            )
            
            if response.status_code == 200:
                return response.json()
                
            raise HTTPException(
                status_code=response.status_code,
                detail="خطا در پاسخ‌دهی موتور مسیریاب محلی OSRM"
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=502,
                detail=f"عدم امکان برقراری ارتباط جاده‌ای با سرور OSRM داکر: {str(e)}"
            )