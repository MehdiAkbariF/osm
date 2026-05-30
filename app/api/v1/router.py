from fastapi import APIRouter
# اضافه کردن پورت pois
from app.api.v1.endpoints import search, reverse, tiles, pois 

api_router = APIRouter()

api_router.include_router(search.router, prefix="/search", tags=["Search"])
api_router.include_router(reverse.router, prefix="/reverse", tags=["Reverse"])
api_router.include_router(tiles.router, prefix="/tiles", tags=["Tiles"])
api_router.include_router(pois.router, prefix="/pois", tags=["POIs"]) # ثبت روت مکان‌ها