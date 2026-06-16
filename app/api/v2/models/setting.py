# c:\Users\Raven\OSM\app\api\v2\models\setting.py
from sqlalchemy import Column, Integer, Float, Boolean, String
from app.api.v2.models.base import Base, TimestampMixin

class MapSetting(Base, TimestampMixin):
    __tablename__ = "map_settings"

    id = Column(Integer, primary_key=True, index=True)
    
    # تنظیمات پیش‌فرض کارتوگرافی نقشه
    map_pitch = Column(Float, default=45.0, nullable=False)
    map_bearing = Column(Float, default=-15.0, nullable=False)
    map_zoom = Column(Float, default=16.0, nullable=False)
    building_multiplier = Column(Float, default=1.5, nullable=False)
    
    # تنظیمات موتور جستجو
    trigram_threshold = Column(Float, default=0.3, nullable=False)
    
    # تنظیمات ترافیک و مسیریابی
    avoid_traffic_zones = Column(Boolean, default=False, nullable=False)
    traffic_time_multiplier = Column(Float, default=1.2, nullable=False)

    # ستون‌های جدید کارتوگرافی داینامیک نقشه
    background_color = Column(String(10), default="#f4f1ea", nullable=False)
    park_color = Column(String(10), default="#d0e4cc", nullable=False)
    water_color = Column(String(10), default="#aad3df", nullable=False)
    primary_road_color = Column(String(10), default="#ffa042", nullable=False)
    secondary_road_color = Column(String(10), default="#ffe082", nullable=False)
    minor_road_color = Column(String(10), default="#ffffff", nullable=False)
    font_family = Column(String(100), default="Vazirmatn Thin", nullable=False)