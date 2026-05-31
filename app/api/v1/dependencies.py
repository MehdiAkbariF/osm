# app/api/v1/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.core.database import get_db
from app.services.auth import auth_service
from app.models.user import User
from app.models.api_key import APIKey

security = HTTPBearer()
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """ دریافت کاربر جاری از روی توکن JWT """
    token = credentials.credentials
    payload = auth_service.verify_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="توکن نامعتبر یا منقضی شده است",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="توکن نامعتبر است"
        )

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="کاربر یافت نشد"
        )

    # بررسی اینکه کاربر تایید شده باشد (is_active = True)
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="حساب کاربری شما هنوز توسط ادمین تایید نشده است"
        )

    return user

async def get_current_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    """ اطمینان از اینکه کاربر جاری ادمین است """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="شما دسترسی ادمین ندارید"
        )
    return current_user

async def get_api_key(
    api_key_val: str = Depends(api_key_header),
    db: Session = Depends(get_db)
) -> APIKey:
    """
    اعتبارسنجی هدر API Key برای دسترسی به اندپوینت‌های عمومی
    """
    if not api_key_val:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="کلید دسترسی (X-API-Key) در هدر درخواست یافت نشد"
        )

    # جستجوی کلید در دیتابیس
    db_key = db.query(APIKey).filter(APIKey.key == api_key_val).first()
    if not db_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="کلید دسترسی وارد شده نامعتبر است"
        )

    # بررسی فعال بودن کلید
    if not db_key.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="این کلید دسترسی توسط مدیر سیستم غیرفعال شده است"
        )

    # بررسی تاریخ انقضا
    if not db_key.is_unlimited:
        if db_key.expires_at and db_key.expires_at < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="مدت اعتبار این کلید دسترسی منقضی شده است"
            )

    # بررسی وضعیت کاربر مالک کلید
    owner = db_key.user
    if not owner or not owner.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="حساب کاربری مالک این کلید غیرفعال یا مسدود است"
        )

    # بروزرسانی زمان آخرین استفاده
    db_key.last_used_at = datetime.now(timezone.utc)
    db.commit()

    return db_key