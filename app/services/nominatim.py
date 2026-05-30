import requests
from app.core.config import settings

class NominatimService:
    def __init__(self):
        self.base_url = f"{settings.NOMINATIM_URL}/search"

    def search_places(
        self, 
        query: str, 
        mode: str = "global", 
        lat: float = None, 
        lon: float = None, 
        viewbox: str = None, 
        city: str = None
    ) -> list:
        # کادر پیش‌فرض مرز جغرافیایی کل ایران
        iran_viewbox = "44.0,40.0,63.0,25.0"
        
        # پارامترهای پیش‌فرض وب‌سرویس
        params = {
            "format": "json",
            "accept-language": "fa",
            "limit": 5
        }

        # پردازش لایه منطق بر اساس حالت انتخاب‌شده (Mode)
        if mode == "global":
            # ۱. جستجوی سراسری در کل ایران
            params["q"] = query
            params["viewbox"] = iran_viewbox
            params["bounded"] = 1

        elif mode == "proximity":
            # ۲. جستجو در اطراف لوکیشن کاربر (Proximity)
            params["q"] = query
            if lat is not None and lon is not None:
                params["lat"] = lat
                params["lon"] = lon
                # اعمال یک باندینگ باکس کوچک فرضی دور کاربر برای اولویت‌دهی شدید محلی
                params["viewbox"] = f"{lon-0.1},{lat+0.1},{lon+0.1},{lat-0.1}"
                params["bounded"] = 0 # برای اینکه اگر در آن نزدیکی پیدا نشد، نتایج دورتر را بیاورد

        elif mode == "viewport":
            # ۳. جستجو دقیقاً درون کادر فعلی نقشه کاربر (Bounding Box)
            params["q"] = query
            if viewbox:
                params["viewbox"] = viewbox
                params["bounded"] = 1 # اجبار به عدم خروج از کادر نقشه فعلی

        elif mode == "city":
            # ۴. جستجوی مقید به یک شهر مشخص
            # در OSM، ادغام نام شهر با کلمه کلیدی، بهترین نتایج POI را در آن شهر می‌دهد
            if city:
                params["q"] = f"{city} {query}"
            else:
                params["q"] = query
            params["viewbox"] = iran_viewbox
            params["bounded"] = 1

        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise RuntimeError(f"خطا در پردازش موتور جستجوی Nominatim: {str(e)}")

            # متد جدید برای دریافت سلسله مراتب آدرس از Nominatim
    def reverse_geocode(self, lat: float, lon: float) -> dict:
        url = f"{settings.NOMINATIM_URL}/reverse"
        params = {
            "lat": lat,
            "lon": lon,
            "format": "json",
            "zoom": 18,
            "addressdetails": 1,
            "accept-language": "fa"
        }
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise RuntimeError(f"خطا در ارتباط با سرور Nominatim: {str(e)}")

nominatim_service = NominatimService()