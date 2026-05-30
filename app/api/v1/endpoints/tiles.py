from fastapi import APIRouter, Response, HTTPException
from app.services.tile_service import tile_service

router = APIRouter()

@router.get("/{table}/{z}/{x}/{y}", summary="دریافت تایل‌های برداری نقشه")
async def get_tile(table: str, z: int, x: int, y: int):
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