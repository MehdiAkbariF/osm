import re
from fastapi import APIRouter, HTTPException, Query
from app.services.postgis_service import postgis_service
from app.services.nominatim import nominatim_service

router = APIRouter()

def convert_digits_to_persian(text: str) -> str:
    """
    تبدیل اعداد انگلیسی به فارسی
    """
    if not text:
        return ""
    translation = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
    return text.translate(translation)

def is_numeric_plate(text: str) -> bool:
    """
    بررسی اینکه آیا پلاک واقعاً عدد است یا نام یک مکان (مثل مرکز کامپیوتر ایران)
    """
    if not text:
        return False
    # اگر طول متن کم باشد و شامل عدد باشد، آن را پلاک عددی در نظر می‌گیریم
    clean_text = text.strip()
    return any(char.isdigit() for char in clean_text) and len(clean_text) < 10

@router.get("", summary="آدرس‌یابی معکوس هوشمند و بهینه پستی")
async def reverse_geocoding(
    lat: float = Query(..., description="عرض جغرافیایی نقطه"),
    lon: float = Query(..., description="طول جغرافیایی نقطه")
):
    # ۱. استعلام نزدیک‌ترین خیابان واقعی از بافر PostGIS دیتابیس خودمان
    nearest_street = postgis_service.get_nearest_street(lat=lat, lon=lon, buffer_meters=100.0)
    
    # ۲. استعلام جزئیات کامل تقسیمات کشوری از Nominatim
    try:
        nominatim_data = nominatim_service.reverse_geocode(lat=lat, lon=lon)
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))

    address = nominatim_data.get("address", {})
    
    # ۳. پارسر هوشمند سلسله‌مراتبی آدرس
    parts = []
    
    # الف) استان
    if "state" in address: 
        parts.append(address["state"])
        
    # ب) شهر / شهرک / روستا
    city = address.get("city", address.get("town", address.get("village")))
    if city:
        parts.append(city)
    
    # ج) منطقه شهری
    suburb = address.get("suburb")
    if suburb:
        clean_suburb = suburb.replace(" شهر تهران", "").replace("منطقه ", "منطقهٔ ")
        parts.append(clean_suburb)

    # د) نام محله (Neighbourhood)
    neighbourhood = address.get("neighbourhood")
    if neighbourhood and neighbourhood != suburb:
        parts.append(f"محلهٔ {neighbourhood}")

    # هـ) تزریق خیابان واقعی استخراج‌شده از بافر PostGIS
    street_name = None
    if nearest_street:
        street_name = nearest_street["name"]
        parts.append(street_name)
    elif "road" in address:
        street_name = address["road"]
        parts.append(street_name)

    # و) نام واحد تجاری / مغازه / دفتر اداری (به صورت مستقیم و بدون کلمه ساختگی)
    shop = address.get("shop")
    office = address.get("office")
    amenity = address.get("amenity")
    building = address.get("building")

    if shop:
        parts.append(shop)
    elif office:
        parts.append(office)
    elif amenity:
        parts.append(amenity)
    elif building and building != "yes": # نادیده گرفتن مقدار ساختگی yes در دیتابیس
        parts.append(f"ساختمان {building}")

    # ز) شماره پلاک (بررسی هوشمند عددی بودن)
    house_number = address.get("house_number")
    if house_number:
        if is_numeric_plate(house_number):
            persian_plate = convert_digits_to_persian(house_number)
            parts.append(f"پلاک {persian_plate}")
        else:
            # اگر متنی بود، آن را مستقیماً بدون کلمه پلاک اضافه کن
            persian_text = convert_digits_to_persian(house_number)
            parts.append(persian_text)

    # ساخت آدرس نهایی یکپارچه و بهینه
    final_address = "، ".join(parts)

    return {
        "address": final_address,
        "nearest_street": nearest_street["name"] if nearest_street else None,
        "distance_to_street_meters": nearest_street["distance"] if nearest_street else None,
        "raw_address_details": address
    }