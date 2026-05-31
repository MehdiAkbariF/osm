# app/api/v1/endpoints/api_keys.py
import secrets
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone

from app.core.database import get_db
from app.models.user import User
from app.models.api_key import APIKey
from app.schemas.api_key import APIKeyCreate, APIKeyResponse, APIKeyCreateResponse
from app.schemas.user import MessageResponse
from app.api.v1.dependencies import get_current_user

router = APIRouter(prefix="/api-keys", tags=["API Keys"])

@router.post("/", response_model=APIKeyCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_user_api_key(
    key_data: APIKeyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    تولید یک کلید دسترسی جدید برای کاربر جاری
    """
    # تولید کلید تصادفی منحصر‌به‌فرد
    raw_key = f"yk_live_{secrets.token_urlsafe(32)}"
    masked_key = f"yk_live_{raw_key[8:12]}****{raw_key[-4:]}"

    # بررسی صحت منطقی فیلد انقضا
    if not key_data.is_unlimited and not key_data.expires_at:
        raise HTTPException(
            status_code=400, 
            detail="در صورت محدود بودن کلید، تعیین تاریخ انقضا الزامی است"
        )

    new_key = APIKey(
        key=raw_key,
        masked_key=masked_key,
        name=key_data.name,
        user_id=current_user.id,
        is_active=True,
        is_unlimited=key_data.is_unlimited,
        expires_at=key_data.expires_at if not key_data.is_unlimited else None,
        rate_limit=key_data.rate_limit
    )

    db.add(new_key)
    db.commit()
    db.refresh(new_key)

    # ارسال مقدار خام کلید فقط در پاسخ اولین درخواست جهت کپی کردن کاربر
    response_data = APIKeyCreateResponse.model_validate(new_key)
    response_data.raw_key = raw_key
    return response_data

@router.get("/", response_model=List[APIKeyResponse])
async def get_my_api_keys(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    مشاهده لیست کلیدهای ساخته‌شده توسط کاربر جاری (به صورت ماسک‌شده)
    """
    keys = db.query(APIKey).filter(APIKey.user_id == current_user.id).all()
    return keys

@router.delete("/{key_id}", response_model=MessageResponse)
async def delete_my_api_key(
    key_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    حذف و ابطال همیشگی کلید دسترسی توسط مالک آن
    """
    db_key = db.query(APIKey).filter(APIKey.id == key_id, APIKey.user_id == current_user.id).first()
    if not db_key:
        raise HTTPException(status_code=404, detail="کلید دسترسی یافت نشد")

    db.delete(db_key)
    db.commit()
    return MessageResponse(message="کلید دسترسی با موفقیت حذف و ابطال شد")