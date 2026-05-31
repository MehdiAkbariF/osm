# app/api/v1/endpoints/admin.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import List, Optional
from app.core.database import get_db
from app.models.user import User
from app.models.api_key import APIKey
from app.schemas.user import UserResponse, MessageResponse
from app.schemas.api_key import APIKeyResponse, APIKeyAdminUpdate
from app.api.v1.dependencies import get_current_admin

router = APIRouter(
    prefix="/admin", 
    tags=["Admin"], 
    dependencies=[Depends(get_current_admin)]
)

@router.get("/users", response_model=List[UserResponse])
async def get_all_users(
    skip: int = Query(0, ge=0, description="تعداد رد شده"),
    limit: int = Query(50, ge=1, le=100, description="تعداد در هر صفحه"),
    db: Session = Depends(get_db)
):
    """ دریافت لیست همه کاربران (فقط ادمین) """
    users = db.query(User).offset(skip).limit(limit).all()
    return [UserResponse.model_validate(user) for user in users]

@router.get("/users/pending", response_model=List[UserResponse])
async def get_pending_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """ دریافت لیست کاربران در انتظار تایید (is_active=False) """
    users = db.query(User).filter(User.is_active == False).offset(skip).limit(limit).all()
    return [UserResponse.model_validate(user) for user in users]

@router.put("/users/{user_id}/approve", response_model=MessageResponse)
async def approve_user(
    user_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """ تایید کاربر توسط ادمین """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="کاربر یافت نشد")

    if user.is_active:
        return MessageResponse(message="کاربر قبلاً تایید شده است", success=True)

    user.is_active = True
    user.approved_at = datetime.now(timezone.utc)
    user.approved_by = current_admin.id

    db.commit()

    return MessageResponse(message=f"کاربر {user.username} با موفقیت تایید شد")

@router.put("/users/{user_id}/reject", response_model=MessageResponse)
async def reject_user(
    user_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """ رد درخواست کاربر (حذف کاربر) """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="کاربر یافت نشد")

    db.delete(user)
    db.commit()

    return MessageResponse(message=f"درخواست کاربر {user.username} رد و حذف شد")

@router.put("/users/{user_id}/block", response_model=MessageResponse)
async def block_user(
    user_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """ مسدود کردن کاربر (is_active = False) """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="کاربر یافت نشد")

    if user.is_admin:
        raise HTTPException(status_code=403, detail="نمی‌توانید ادمین را مسدود کنید")

    user.is_active = False
    db.commit()

    return MessageResponse(message=f"کاربر {user.username} مسدود شد")

@router.delete("/users/{user_id}", response_model=MessageResponse)
async def delete_user(
    user_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """ حذف کامل کاربر """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="کاربر یافت نشد")

    if user.is_admin:
        raise HTTPException(status_code=403, detail="نمی‌توانید ادمین را حذف کنید")

    db.delete(user)
    db.commit()

    return MessageResponse(message=f"کاربر {user.username} حذف شد")

# ========== مدیریت API Keyها توسط ادمین ==========

@router.get("/api-keys", response_model=List[APIKeyResponse])
async def admin_get_all_api_keys(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    دریافت لیست تمام کلیدهای صادر شده در کل سامانه (فقط ادمین)
    """
    keys = db.query(APIKey).offset(skip).limit(limit).all()
    return keys

@router.put("/api-keys/{key_id}", response_model=APIKeyResponse)
async def admin_update_api_key(
    key_id: int,
    update_data: APIKeyAdminUpdate,
    db: Session = Depends(get_db)
):
    """
    ویرایش و مدیریت وضعیت کلید دسترسی (فعال/غیرفعال‌سازی، تغییر انقضا، نرخ درخواست) (فقط ادمین)
    """
    db_key = db.query(APIKey).filter(APIKey.id == key_id).first()
    if not db_key:
        raise HTTPException(status_code=404, detail="کلید دسترسی یافت نشد")

    if update_data.is_active is not None:
        db_key.is_active = update_data.is_active
    if update_data.is_unlimited is not None:
        db_key.is_unlimited = update_data.is_unlimited
        if update_data.is_unlimited:
            db_key.expires_at = None
    if update_data.expires_at is not None and not db_key.is_unlimited:
        db_key.expires_at = update_data.expires_at
    if update_data.rate_limit is not None:
        db_key.rate_limit = update_data.rate_limit

    db.commit()
    db.refresh(db_key)
    return db_key

@router.delete("/api-keys/{key_id}", response_model=MessageResponse)
async def admin_delete_api_key(
    key_id: int,
    db: Session = Depends(get_db)
):
    """
    ابطال همیشگی و حذف کلید از دیتابیس توسط ادمین
    """
    db_key = db.query(APIKey).filter(APIKey.id == key_id).first()
    if not db_key:
        raise HTTPException(status_code=404, detail="کلید دسترسی یافت نشد")

    db.delete(db_key)
    db.commit()
    return MessageResponse(message=f"کلید دسترسی مربوط به کاربر با شناسه {db_key.user_id} حذف شد")