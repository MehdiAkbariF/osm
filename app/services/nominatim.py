import requests
from app.core.config import settings

class NominatimService:
    def __init__(self):
        # آدرس دهی بر اساس متغیرهای فایل .env
        self.base_url = f"{settings.NOMINATIM_URL}/search"

    def search_places(self, query: str, lat: float = None, lon: float = None) -> list:
        # کادر جغرافیایی ایران جهت محدودسازی نتایج به داخل کشور
        iran_viewbox = "44.0,40.0,63.0,25.0"
        
        params = {
            "q": query,
            "format": "json",
            "accept-language": "fa", # اجبار سرور به بازگرداندن متون فارسی
            "viewbox": iran_viewbox,
            "bounded": 1,
            "limit": 5
        }
        
        # اعمال اولویت‌دهی مکانی در صورت وجود موقعیت کاربر
        if lat is not None and lon is not None:
            params["lat"] = lat
            params["lon"] = lon

        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status() # تولید خطا در صورت پاسخ ناموفق سرور
            return response.json()
        except requests.RequestException as e:
            # کپسوله‌سازی خطاهای شبکه داکر
            raise RuntimeError(f"خطا در ارتباط با سرور Nominatim: {str(e)}")

# ایجاد شیء یکتا برای استفاده در کل پروژه
nominatim_service = NominatimService()