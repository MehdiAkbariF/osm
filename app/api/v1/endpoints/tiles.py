# app/api/v1/endpoints/tiles.py
from fastapi import APIRouter, Response, HTTPException, Depends
from app.services.tile_service import tile_service
from app.models.api_key import APIKey
from app.api.v1.dependencies import get_api_key  # وارد کردن وابستگی کلید دسترسی

router = APIRouter()

@router.get("/{table}/{z}/{x}/{y}", summary="دریافت تایل‌های برداری نقشه")
async def get_tile(
    table: str, 
    z: int, 
    x: int, 
    y: int,
    api_key: APIKey = Depends(get_api_key)  # اجباری کردن ارائه کلید معتبر به تایل سرور داخلی
):
    # دریافت ناهم‌گام تایل (که خودکار توسط httpx دکامپرس شده است)
    tile_bytes, headers = await tile_service.get_vector_tile(table, z, x, y)
    
    if not tile_bytes:
        raise HTTPException(status_code=404, detail="تایل مورد نظر یافت نشد")

    # ارسال مستقیم بایت‌های خام بدون هدر فشرده‌سازی جهت جلوگیری از خطای مرورگر
    return Response(
        content=tile_bytes,
        media_type="application/x-protobuf",
        headers={
            "Cache-Control": "public, max-age=86400" # کش کردن تایل در مرورگر به مدت ۲۴ ساعت
        }
    )