
from fastapi import Depends, HTTPException, status, Query
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

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="حساب کاربری شما هنوز توسط ادمین تایید نشده است"
        )

    return user

async def get_current_admin(
    current_user: User = Depends(get_current_user)
) -> User:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="شما دسترسی ادمین ندارید"
        )
    return current_user

async def get_api_key(
    api_key_header: str = Depends(api_key_header),
    api_key_query: str = Query(None, alias="api_key"),  
    db: Session = Depends(get_db)
) -> APIKey:
    """
    اعتبارسنجی هدر یا پارامتر آدرس API Key بدون محدودیت نرخ درخواست (Rate Limit)
    """
    
    api_key_val = api_key_header or api_key_query

    if not api_key_val:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="کلید دسترسی (API Key) در هدر یا پارامتر آدرس درخواست یافت نشد"
        )

    
    db_key = db.query(APIKey).filter(APIKey.key == api_key_val).first()
    if not db_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="کلید دسترسی وارد شده نامعتبر است"
        )

    
    if not db_key.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="این کلید دسترسی توسط مدیر سیستم غیرفعال شده است"
        )

    
    if not db_key.is_unlimited:
        if db_key.expires_at and db_key.expires_at < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="مدت اعتبار این کلید دسترسی منقضی شده است"
            )

    
    owner = db_key.user
    if not owner or not owner.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="حساب کاربری مالک این کلید غیرفعال یا مسدود است"
        )

    
    db_key.last_used_at = datetime.now(timezone.utc)
    db.commit()

    return db_key