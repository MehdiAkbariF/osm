# app/api/v1/endpoints/reverse.py
import re
from fastapi import APIRouter, HTTPException, Query
from app.services.postgis_service import postgis_service
from app.services.nominatim import nominatim_service

router = APIRouter()

def convert_digits_to_persian(text: str) -> str:
    if not text:
        return ""
    translation = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
    return text.translate(translation)

def is_numeric_plate(text: str) -> bool:
    if not text:
        return False
    clean_text = text.strip()
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

@router.get("", summary="آدرس‌یابی معکوس هوشمند و دقیق")
async def reverse_geocoding(
    lat: float = Query(..., description="عرض جغرافیایی نقطه"),
    lon: float = Query(..., description="طول جغرافیایی نقطه"),
    include_poi: bool = Query(False, description="آیا نام اماکن تجاری در آدرس نمایش داده شود؟")
):
    # ۱. استعلام هوشمند با بافرهای چندمرحله‌ای
    smart_result = postgis_service.smart_reverse_geocode(lat=lat, lon=lon)
    
    # ۲. استعلام جزئیات از Nominatim
    try:
        nominatim_data = nominatim_service.reverse_geocode(lat=lat, lon=lon)
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))

    address = nominatim_data.get("address", {})
    
    # ۳. ساخت آدرس با اولویت داده‌های دقیق
    parts = []
    
    # استان
    if "state" in address:
        state = re.sub(r'^استان\s+', '', address["state"])
        parts.append(state)
    
    # شهر
    city = address.get("city", address.get("town", address.get("village")))
    if city:
        city = clean_city_name(city)
        parts.append(city)
    
    # منطقه
    suburb = address.get("suburb")
    if suburb:
        clean_suburb = suburb.replace(" شهر تهران", "").replace("منطقه ", "منطقهٔ ")
        parts.append(clean_suburb)

    # محله
    neighbourhood = address.get("neighbourhood")
    if neighbourhood and neighbourhood != suburb:
        if not neighbourhood.startswith("محلهٔ"):
            parts.append(f"محلهٔ {neighbourhood}")
        else:
            parts.append(neighbourhood)

    # خیابان (از داده‌های دقیق PostGIS)
    street_name = None
    if smart_result and smart_result.get('street_name'):
        street_name = smart_result['street_name']
        parts.append(street_name)
    elif "road" in address:
        street_name = address["road"]
        parts.append(street_name)

    # پلاک (از داده‌های دقیق PostGIS یا Nominatim)
    house_number = None
    if smart_result and smart_result.get('house_number'):
        house_number = smart_result['house_number']
    elif "house_number" in address:
        house_number = address["house_number"]
    
    if house_number and is_numeric_plate(house_number):
        persian_plate = convert_digits_to_persian(house_number)
        parts.append(f"پلاک {persian_plate}")

    # نام مکان تجاری
    poi_name = address.get("shop") or address.get("office") or address.get("amenity") or address.get("tourism")
    
    # ساخت آدرس نهایی
    final_address = "، ".join(parts)

    if include_poi and poi_name:
        final_address = f"{final_address}، {poi_name}"

    response = {
        "address": final_address,
        "nearest_street": street_name,
        "distance_to_street_meters": smart_result.get('distance') if smart_result else None,
        "confidence_score": smart_result.get('final_score') if smart_result else None,
        "source_type": smart_result.get('source_type') if smart_result else None,
        "raw_address_details": address
    }
    
    if poi_name:
        response["place_name"] = poi_name
    
    if smart_result and smart_result.get('approx_house_number'):
        response["approx_house_number"] = smart_result.get('approx_house_number')
    
    return response