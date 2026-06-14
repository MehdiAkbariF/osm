# app/api/v1/endpoints/user_locations.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.user import User
from app.schemas.location import LocationCreate, LocationUpdate, LocationResponse, MessageResponse
from app.services.location_service import location_service
from app.api.v1.dependencies import get_current_user

router = APIRouter(prefix="/user/locations", tags=["User Locations"])

def parse_user_location_to_dict(loc) -> dict:
    """تبدیل ایمن آبجکت دیتابیس به دیکشنری برای ارسال به Pydantic"""
    return {c.name: getattr(loc, c.name) for c in loc.__table__.columns}

@router.post("/", response_model=LocationResponse, status_code=status.HTTP_201_CREATED)
async def create_user_location(
    location_data: LocationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    ثبت موقعیت مکانی انبار/فروشگاه جدید توسط کاربر لاگین شده
    """
    location = location_service.create_location(db, location_data, current_user.id)
    return LocationResponse(**parse_user_location_to_dict(location))

@router.get("/", response_model=List[LocationResponse])
async def get_my_locations(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[str] = Query(None, description="pending, approved, rejected"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    دریافت موقعیت‌های ثبت شده توسط خود کاربر جاری
    """
    locations = location_service.get_user_locations(db, current_user.id, skip, limit, status)
    return [LocationResponse(**parse_user_location_to_dict(loc)) for loc in locations]

@router.get("/{location_id}", response_model=LocationResponse)
async def get_my_location_detail(
    location_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    دریافت جزئیات کامل یکی از موقعیت‌های انبار شخصی
    """
    location = location_service.get_location(db, location_id)
    if not location:
        raise HTTPException(status_code=404, detail="موقعیت یافت نشد")
    if location.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="شما دسترسی به این موقعیت ندارید")
    return LocationResponse(**parse_user_location_to_dict(location))

@router.put("/{location_id}", response_model=LocationResponse)
async def update_my_location(
    location_id: int,
    location_data: LocationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    ویرایش موقعیت شخصی (فقط اگر انبار در وضعیت pending باشد قابل ویرایش است)
    """
    location = location_service.get_location(db, location_id)
    if not location:
        raise HTTPException(status_code=404, detail="موقعیت یافت نشد")
    if location.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="شما دسترسی به این موقعیت ندارید")
    if location.status != "pending":
        raise HTTPException(status_code=400, detail="فقط موقعیت‌های در انتظار تایید قابل ویرایش هستند")
    
    updated = location_service.update_location(db, location_id, location_data)
    return LocationResponse(**parse_user_location_to_dict(updated))

@router.delete("/{location_id}", response_model=MessageResponse)
async def delete_my_location(
    location_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    حذف موقعیت شخصی (فقط اگر انبار در وضعیت pending باشد قابل حذف است)
    """
    location = location_service.get_location(db, location_id)
    if not location:
        raise HTTPException(status_code=404, detail="موقعیت یافت نشد")
    if location.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="شما دسترسی به این موقعیت ندارید")
    if location.status != "pending":
        raise HTTPException(status_code=400, detail="فقط موقعیت‌های در انتظار تایید قابل حذف هستند")
    
    location_service.delete_location(db, location_id)
    return MessageResponse(message="موقعیت با موفقیت حذف شد", location_id=location_id)