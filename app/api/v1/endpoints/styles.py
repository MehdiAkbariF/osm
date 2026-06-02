# app/api/v1/endpoints/styles.py
import os
import json
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import JSONResponse
from app.api.v1.dependencies import get_api_key
from app.models.api_key import APIKey

router = APIRouter(prefix="/styles", tags=["Map Styles"])

# بررسی هوشمند و چندمرحله‌ای آدرس‌های احتمالی فایل روی هارد (با پشتیبانی از پوشه ریشه OSM شما)
possible_paths = [
    # ۱. مسیر ریشه اصلی پروژه OSM شما (C:\Users\Raven\OSM\styles\default.json)
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))), "styles", "default.json"),
    # ۲. مسیر نسبی مستقیم ریشه
    "./styles/default.json",
    # ۳. مسیر استاندارد در پوشه static/styles روت app
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "static", "styles", "default.json"),
    # ۴. مسیر مستقیم نسبی در فرآیند اجرای uvicorn
    "./app/static/styles/default.json"
]

# پیدا کردن مسیر معتبر فعال روی سیستم شما
STYLE_FILE_PATH = None
for path in possible_paths:
    if os.path.exists(path):
        STYLE_FILE_PATH = path
        break

@router.get("/default", summary="ارائه پویا و امن فایل استایل نقشه برداری")
async def get_default_style(
    request: Request,
    api_key: APIKey = Depends(get_api_key) # 🔒 بررسی اعتبار کلید دسترسی
):
    """
    سرویس‌دهی پویای استایل نقشه به اپلیکیشن موبایل یا فرانت وب بر اساس آی‌پی کلاینت و کلید فعال
    """
    # اگر فایل در هیچ‌کدام از مسیرها پیدا نشد
    if STYLE_FILE_PATH is None:
        raise HTTPException(
            status_code=404, 
            detail="فایل استایل default.json یافت نشد. مطمئن شوید فایل را در مسیر OSM/styles/default.json ساخته‌اید."
        )
    
    try:
        # ۱. خواندن فایل خام
        with open(STYLE_FILE_PATH, "r", encoding="utf-8") as f:
            style_content = f.read()
        
        # ۲. محاسبه خودکار آدرس دامنه و پورت پایتون به صورت داینامیک
        base_url = f"{request.url.scheme}://{request.url.netloc}/api/v1"
        
        # ۳. جایگذاری هوشمند آدرس‌ها و کلید دسترسی کلاینت در داخل مشخصات استایل
        style_content = style_content.replace("{{BASE_URL}}", base_url)
        style_content = style_content.replace("{{API_KEY}}", api_key.key)
        
        # ۴. بازگرداندن فایل نهایی به صورت فرمت استاندارد JSON
        return JSONResponse(content=json.loads(style_content))
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"خطا در پردازش فایل استایل نقشه: {str(e)}")