# app/api/v1/endpoints/reverse.py
import re
from fastapi import APIRouter, Query, Depends
from app.services.postgis_service import postgis_service
from app.models.api_key import APIKey
from app.api.v1.dependencies import get_api_key

router = APIRouter()

def convert_digits_to_persian(text: str) -> str:
    if not text:
        return ""
    translation = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
    return text.translate(translation)

def is_numeric_plate(text: str) -> bool:
    if not text:
        return False
    clean_text = str(text).strip()
    if re.match(r'^[\d]{2,5}$|^\d+[-\s]?\d+$', clean_text):
        return True
    persian_letters = re.findall(r'[آ-ی]', clean_text)
    if len(persian_letters) > 3:
        return False
    return any(char.isdigit() for char in clean_text) and len(clean_text) < 15

def clean_city_name(city: str) -> str:
    if not city:
        return ""
    city = re.sub(r'^شهرستان\s+', '', city)
    city = re.sub(r'^شهر\s+', '', city)
    city = re.sub(r'^بخش\s+مرکزی\s+', '', city)
    return city

def get_landmark_prefix(amenity: str, shop: str) -> str:
    """تولید توصیف‌گر فارسی هوشمند برای لندمارک‌های مجاور"""
    if amenity == 'mosque':
        return "جنب مسجد"
    elif amenity in ['hospital', 'clinic']:
        return "نزدیک بیمارستان"
    elif amenity == 'pharmacy':
        return "جنب داروخانه"
    elif amenity in ['bank', 'atm']:
        return "نزدیک بانک"
    elif amenity in ['school', 'university']:
        return "نزدیک مدرسه/دانشگاه"
    elif shop in ['supermarket', 'convenience']:
        return "جنب سوپرمارکت"
    elif shop == 'mall' or amenity == 'mall':
        return "نزدیک مرکز خرید"
    return "نزدیک"

@router.get("", summary="آدرس‌یابی معکوس هوشمند بومی و فوق دقیق")
async def reverse_geocoding(
    lat: float = Query(..., description="عرض جغرافیایی نقطه"),
    lon: float = Query(..., description="طول جغرافیایی نقطه"),
    include_poi: bool = Query(False, description="آیا نام اماکن تجاری در آدرس نمایش داده شود؟"),
    api_key: APIKey = Depends(get_api_key)
):
    # ۱. استخراج ۱۰۰٪ بومی، آفلاین و فوق‌سریع اطلاعات سلسله‌مراتبی از PostGIS دیتابیس iran_map
    smart_result = postgis_service.smart_reverse_geocode(lat=lat, lon=lon)
    
    if not smart_result:
        return {"address": "آدرسی یافت نشد", "source_type": "none"}

    # ۲. ساختاردهی آدرس سلسله‌مراتب کارتوگرافی بومی ایران
    parts = []
    
    # الف) استان
    if smart_result.get('province'):
        province = re.sub(r'^استان\s+', '', smart_result['province'])
        parts.append(province)
    
    # ب) شهر
    if smart_result.get('city'):
        city = clean_city_name(smart_result['city'])
        parts.append(city)
    
    # ج) منطقه شهرداری
    if smart_result.get('district'):
        district = smart_result['district'].replace(" شهر تهران", "").replace("منطقه ", "منطقهٔ ")
        parts.append(district)

    # د) محله دقیق
    if smart_result.get('neighbourhood'):
        neighbourhood = smart_result['neighbourhood']
        if not neighbourhood.startswith("محلهٔ") and not neighbourhood.startswith("شهر"):
            parts.append(f"محلهٔ {neighbourhood}")
        else:
            parts.append(neighbourhood)

    # هـ) بزرگراه / بلوار شریانی اصلی
    if smart_result.get('highway_street'):
        parts.append(smart_result['highway_street'])

    # و) خیابان اصلی
    if smart_result.get('major_street'):
        major_street = smart_result['major_street']
        if major_street != smart_result.get('highway_street'):
            parts.append(major_street)

    # ز) معبر فرعی (کوچه / بن‌بست)
    if smart_result.get('minor_street'):
        minor_street = smart_result['minor_street']
        if minor_street != smart_result.get('major_street') and minor_street != smart_result.get('highway_street'):
            parts.append(minor_street)

    # ح) نام مجتمع مسکونی، اداری، تجاری یا برج
    if smart_result.get('building_name'):
        parts.append(smart_result['building_name'])

    # ط) پلاک خانه
    if smart_result.get('house_number'):
        house_num = smart_result['house_number']
        if is_numeric_plate(str(house_num)):
            persian_plate = convert_digits_to_persian(str(house_num))
            parts.append(f"پلاک {persian_plate}")

    # ی) توصیف‌گر موقعیت نسبی مجاور (لندمارک)
    if smart_result.get('landmark_name'):
        prefix = get_landmark_prefix(
            smart_result.get('landmark_amenity') or '', 
            smart_result.get('landmark_shop') or ''
        )
        parts.append(f"{prefix} {smart_result['landmark_name']}")

    # ساخت آدرس زنجیره‌ای کامل فارسی
    final_address = "، ".join(parts)

    response = {
        "address": final_address,
        "nearest_street": smart_result.get('minor_street') or smart_result.get('major_street') or smart_result.get('highway_street'),
        "parent_street": smart_result.get('major_street') or smart_result.get('highway_street'),
        "building_name": smart_result.get('building_name'),
        "landmark": f"{prefix} {smart_result['landmark_name']}" if smart_result.get('landmark_name') else None,
        "distance_to_street_meters": smart_result.get('distance'),
        "confidence_score": smart_result.get('final_score'),
        "source_type": smart_result.get('source_type'),
    }
    
    return response