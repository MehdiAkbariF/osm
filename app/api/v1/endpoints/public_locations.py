# app/api/v1/endpoints/public_locations.py
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.api_key import APIKey
from app.schemas.location import LocationCreate, LocationResponse
from app.services.location_service import location_service
from app.api.v1.dependencies import get_api_key

router = APIRouter(prefix="/locations", tags=["Public Locations"])

@router.post("/public", response_model=LocationResponse, status_code=status.HTTP_201_CREATED)
async def create_public_location_suggestion(
    location_data: LocationCreate,
    api_key: APIKey = Depends(get_api_key),  # 🔒 فقط نیاز به API Key معتبر دارد
    db: Session = Depends(get_db)
):
    """
    ثبت پیشنهاد موقعیت جدید توسط کاربران مهمان (بدون نیاز به لاگین)
    - موقعیت با وضعیت پیش‌فرض pending و فیلد ایجادکننده NULL ذخیره می‌شود.
    - فیلدهای آدرس و شهر به صورت خودکار توسط PostGIS محاسبه و پر می‌شوند.
    """
    location = location_service.create_location(db, location_data, user_id=None)
    return location

@router.get("/search", response_model=List[LocationResponse])
async def search_and_filter_locations(
    lat: float = Query(..., description="عرض جغرافیایی مرکز جستجو"),
    lon: float = Query(..., description="طول جغرافیایی مرکز جستجو"),
    radius_km: float = Query(5.0, description="شعاع جستجو بر حسب کیلومتر"),
    part: Optional[str] = Query(None, description="فیلتر نام قطعه یدکی موجود در فیلد متادیتا"),
    brand: Optional[str] = Query(None, description="فیلتر برند قطعه موجود در فیلد متادیتا"),
    is_return_usage: Optional[bool] = Query(None, description="فیلتر قابلیت مرجوعی کالا"),
    api_key: APIKey = Depends(get_api_key),  # 🔒 تایید کلید دسترسی
    db: Session = Depends(get_db)
):
    """
    موتور جستجوی همزمان جغرافیایی و ویژگی‌های قطعات یدکی (JSONB)
    - یافتن انبارهای فعال یدکچی در یک محدوده جغرافیایی خاص که قطعه یا برند فیلتر شده را موجود دارند.
    """
    locations = location_service.search_locations(
        db=db,
        lat=lat,
        lon=lon,
        radius_km=radius_km,
        part_filter=part,
        brand_filter=brand,
        is_return_usage=is_return_usage
    )
    return locations

@router.get("/approved", response_model=List[LocationResponse])
async def get_approved_locations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    category: Optional[str] = None,
    city: Optional[str] = None,
    api_key: APIKey = Depends(get_api_key),  # 🔒 تایید کلید دسترسی
    db: Session = Depends(get_db)
):
    """
    دریافت تمام موقعیت‌های تایید شده جهت نمایش عمومی بر روی نقشه
    """
    locations = location_service.get_all_locations(
        db, skip, limit, status="approved", category=category, city=city
    )
    return locations