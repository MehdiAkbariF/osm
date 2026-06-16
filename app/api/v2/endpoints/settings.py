from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.v2.core.deps import get_db
from app.api.v2.schemas.settings import SettingsUpdate, SettingsResponse
from app.api.v2.services.settings_service import get_active_settings, update_settings
from app.api.v2.endpoints.auth import get_current_user

router = APIRouter(prefix="/settings", tags=["Map Settings"])

@router.get("/", response_model=SettingsResponse)
def get_map_settings(db: Session = Depends(get_db)):
    """
    دریافت تنظیمات فعلی نقشه (دسترسی عمومی برای کلاینت‌ها)
    """
    try:
        return get_active_settings(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving settings: {str(e)}")

@router.put("/", response_model=SettingsResponse)
def update_map_settings(
    data: SettingsUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    به‌روزرسانی تنظیمات نقشه (فقط سوپر ادمین)
    """
    if current_user.get("role") != "super_admin":
        raise HTTPException(status_code=403, detail="Permission denied. Admin privileges required.")
    
    try:
        return update_settings(db, data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating settings: {str(e)}")