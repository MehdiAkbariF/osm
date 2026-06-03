# app/api/v1/endpoints/tiles.py
from fastapi import APIRouter, Response, HTTPException, Depends, Request
from app.services.tile_service import tile_service
from app.api.v1.dependencies import get_api_key
from app.models.api_key import APIKey

router = APIRouter()

@router.get("/{table}.json", summary="دریافت خودکار و استاندارد مشخصات TileJSON")
async def get_tile_json(
    request: Request,
    table: str,
    api_key: APIKey = Depends(get_api_key)
):
    base_url = f"{request.url.scheme}://{request.url.netloc}/api/v1"
    return {
        "tilejson": "2.2.0",
        "name": f"Vector Source: {table}",
        "tiles": [
            f"{base_url}/tiles/{table}/{{z}}/{{x}}/{{y}}?api_key={api_key.key}"
        ],
        "minzoom": 0,
        "maxzoom": 18,
        "bounds": [-180.0, -85.0, 180.0, 85.0],
        "type": "vector"
    }

@router.get("/{table}/{z}/{x}/{y}", summary="دریافت تایل‌های برداری نقشه")
async def get_tile(
    table: str, 
    z: str, 
    x: str, 
    y: str,
    api_key: APIKey = Depends(get_api_key)
):
    # پاسخ هوشمند به تست‌های اولیه مپوتنیک
    if not (z.isdigit() and x.isdigit() and y.isdigit()):
        return Response(content=b"", media_type="application/x-protobuf")
    
    # تبدیل به عدد صحیح
    z_int = int(z)
    x_int = int(x)
    y_int = int(y)

    # دریافت تایل برداری از دیتابیس PostGIS
    tile_bytes, headers = await tile_service.get_vector_tile(table, z_int, x_int, y_int)
    
    # اگر تایل فاقد داده بود، پاسخ 200 خالی بازگردان
    if not tile_bytes:
        return Response(
            content=b"",
            media_type="application/x-protobuf",
            headers={"Cache-Control": "public, max-age=86400"}
        )

    # ادغام هوشمند هدرها و حذف هدرهای طول، فشرده‌سازی و انتقال تداخل‌دار (حل قطعی کراش‌های دکودینگ)
    response_headers = {**headers} if headers else {}
    response_headers.pop("Content-Length", None)
    response_headers.pop("content-length", None)
    
    # 🔑 حذف هدر فشرده‌سازی قدیمی چون httpx خودش فایل را از حالت فشرده خارج کرده است
    response_headers.pop("Content-Encoding", None)
    response_headers.pop("content-encoding", None)
    response_headers.pop("Transfer-Encoding", None)
    response_headers.pop("transfer-encoding", None)
    
    response_headers["Cache-Control"] = "public, max-age=86400"

    return Response(
        content=tile_bytes,
        media_type="application/x-protobuf",
        headers=response_headers
    )