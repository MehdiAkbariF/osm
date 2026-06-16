from sqlalchemy.orm import Session
from app.api.v2.models.setting import MapSetting
from app.api.v2.schemas.settings import SettingsUpdate

def get_active_settings(db: Session) -> MapSetting:
    """
    دریافت تنظیمات فعال نقشه. 
    در صورتی که تنظیمی در دیتابیس نباشد، ردیف پیش‌فرض را ایجاد می‌کند.
    """
    setting = db.query(MapSetting).filter(MapSetting.id == 1).first()
    if not setting:
        setting = MapSetting(id=1)
        db.add(setting)
        db.commit()
        db.refresh(setting)
    return setting

def update_settings(db: Session, data: SettingsUpdate) -> MapSetting:
    """
    به‌روزرسانی تنظیمات نقشه
    """
    setting = get_active_settings(db)
    
    update_data = data.model_dump(exclude_unset=True) if hasattr(data, 'model_dump') else data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(setting, field, value)
        
    db.commit()
    db.refresh(setting)
    return setting