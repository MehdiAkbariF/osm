import httpx
from fastapi import HTTPException

# اگر OSRM در کانتینر داکر هم‌شبکه است، می‌توانید از نام کانتینر یا localhost استفاده کنید
OSRM_URL = "http://127.0.0.1:5000"

class OSRMService:
    async def get_route(self, start_lat: float, start_lon: float, end_lat: float, end_lon: float):
        # ساختن آدرس استاندارد OSRM
        url = f"{OSRM_URL}/route/v1/driving/{start_lon},{start_lat};{end_lon},{end_lat}?overview=full&geometries=geojson&steps=true"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, timeout=10.0)
                if response.status_code == 200:
                    return response.json()
                raise HTTPException(
                    status_code=response.status_code, 
                    detail="خطا در دریافت پاسخ از موتور مسیریابی OSRM"
                )
            except Exception as e:
                raise HTTPException(
                    status_code=502, 
                    detail=f"عدم امکان برقراری ارتباط با سرور OSRM: {str(e)}"
                )

osrm_service = OSRMService()