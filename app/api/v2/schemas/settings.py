# c:\Users\Raven\OSM\app\api\v2\schemas\settings.py
from pydantic import BaseModel, Field


class SettingsUpdate(BaseModel):
    # تنظیمات دوربین و موتور جستجو
    map_pitch: float = Field(..., description="زاویه شیب دوربین")
    map_bearing: float = Field(..., description="زاویه چرخش نقشه")
    map_zoom: float = Field(..., description="زوم پیش‌فرض")
    building_multiplier: float = Field(..., description="ضریب ارتفاع ساختمان‌های سه‌بعدی")
    trigram_threshold: float = Field(..., description="حساسیت موتور جستجو")
    
    # تنظیمات لجستیک
    avoid_traffic_zones: bool = Field(..., description="دور زدن طرح ترافیک")
    traffic_time_multiplier: float = Field(..., description="ضریب زمان ترافیک")

    # پارامترهای جدید شخصی‌سازی داینامیک کارتوگرافی نقشه (Dynamic Cartography)
    background_color: str = Field("#f4f1ea", description="رنگ پس‌زمینه خشکی‌ها")
    park_color: str = Field("#d0e4cc", description="رنگ پارک‌ها و فضاهای سبز")
    water_color: str = Field("#aad3df", description="رنگ دریاچه‌ها و رودخانه‌ها")
    primary_road_color: str = Field("#ffa042", description="رنگ بزرگراه‌ها و راه‌های اصلی")
    secondary_road_color: str = Field("#ffe082", description="رنگ خیابان‌های شریانی")
    minor_road_color: str = Field("#ffffff", description="رنگ کوچه‌ها و معابر فرعی")
    font_family: str = Field("Vazirmatn Thin", description="فونت پیش‌فرض رندر اسامی روی نقشه")


class SettingsResponse(SettingsUpdate):
    id: int

    class Config:
        from_attributes = True