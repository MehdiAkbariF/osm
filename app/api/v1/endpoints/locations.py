# app/api/v1/endpoints/locations.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.user import User
from app.models.location import Location
from app.schemas.location import (
    LocationCreate, LocationUpdate, LocationResponse, 
    LocationAdminResponse, LocationApprove, LocationReject,
    MessageResponse
)
from app.services.location_service import location_service
from app.api.v1.dependencies import get_current_user, get_current_admin

router = APIRouter(prefix="/locations", tags=["Locations"])

# ========== کاربر معمولی ==========

@router.post("/", response_model=LocationResponse, status_code=status.HTTP_201_CREATED)
async def create_location(
    location_data: LocationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    ثبت موقعیت مکانی جدید
    - فقط کاربران تایید شده می‌توانند ثبت کنند
    - موقعیت با وضعیت pending ذخیره می‌شود
    """
    location = location_service.create_location(db, location_data, current_user.id)
    return location

@router.get("/my-locations", response_model=List[LocationResponse])
async def get_my_locations(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status: Optional[str] = Query(None, description="pending, approved, rejected"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    دریافت موقعیت‌های ثبت شده توسط کاربر جاری
    """
    locations = location_service.get_user_locations(db, current_user.id, skip, limit, status)
    return locations

@router.get("/my-locations/{location_id}", response_model=LocationResponse)
async def get_my_location(
    location_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    دریافت جزئیات یک موقعیت (فقط اگر مالک آن باشید)
    """
    location = location_service.get_location(db, location_id)
    if not location:
        raise HTTPException(status_code=404, detail="موقعیت یافت نشد")
    if location.created_by != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="شما دسترسی به این موقعیت ندارید")
    return location

@router.put("/my-locations/{location_id}", response_model=LocationResponse)
async def update_my_location(
    location_id: int,
    location_data: LocationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    ویرایش موقعیت (فقط اگر در وضعیت pending باشد)
    """
    location = location_service.get_location(db, location_id)
    if not location:
        raise HTTPException(status_code=404, detail="موقعیت یافت نشد")
    if location.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="شما دسترسی به این موقعیت ندارید")
    if location.status != "pending":
        raise HTTPException(status_code=400, detail="فقط موقعیت‌های در انتظار تایید قابل ویرایش هستند")
    
    updated = location_service.update_location(db, location_id, location_data)
    return updated

@router.delete("/my-locations/{location_id}", response_model=MessageResponse)
async def delete_my_location(
    location_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    حذف موقعیت (فقط اگر در وضعیت pending باشد)
    """
    location = location_service.get_location(db, location_id)
    if not location:
        raise HTTPException(status_code=404, detail="موقعیت یافت نشد")
    if location.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="شما دسترسی به این موقعیت ندارید")
    if location.status != "pending":
        raise HTTPException(status_code=400, detail="فقط موقعیت‌های در انتظار تایید قابل حذف هستند")
    
    location_service.delete_location(db, location_id)
    return MessageResponse(message="موقعیت با موفقیت حذف شد")

# ========== API عمومی (برای نقشه) ==========

@router.get("/approved", response_model=List[LocationResponse])
async def get_approved_locations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    category: Optional[str] = None,
    city: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    دریافت موقعیت‌های تایید شده (برای نمایش در نقشه)
    - بدون نیاز به احراز هویت
    """
    locations = location_service.get_all_locations(
        db, skip, limit, status="approved", category=category, city=city
    )
    return locations

@router.get("/nearby", response_model=List[LocationResponse])
async def get_nearby_locations(
    lat: float = Query(..., description="عرض جغرافیایی"),
    lon: float = Query(..., description="طول جغرافیایی"),
    radius_km: float = Query(5.0, ge=0.5, le=50, description="شعاع بر حسب کیلومتر"),
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    دریافت موقعیت‌های تایید شده نزدیک به مختصات داده شده
    - برای نمایش مکان‌های اطراف
    """
    locations = location_service.get_nearby_locations(db, lat, lon, radius_km, limit)
    return locations

# ========== ادمین ==========

@router.get("/admin/all", response_model=List[LocationAdminResponse])
async def admin_get_all_locations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: Optional[str] = Query(None, description="pending, approved, rejected"),
    category: Optional[str] = None,
    city: Optional[str] = None,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    دریافت تمام موقعیت‌ها (فقط ادمین)
    """
    locations = location_service.get_all_locations(db, skip, limit, status, category, city)
    
    # اضافه کردن اطلاعات ایجادکننده
    result = []
    for loc in locations:
        creator = db.query(User).filter(User.id == loc.created_by).first()
        loc_dict = LocationAdminResponse.model_validate(loc).dict()
        loc_dict["creator_name"] = creator.full_name or creator.username
        loc_dict["creator_username"] = creator.username
        result.append(LocationAdminResponse(**loc_dict))
    
    return result

@router.get("/admin/pending", response_model=List[LocationAdminResponse])
async def admin_get_pending_locations(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    دریافت موقعیت‌های در انتظار تایید (فقط ادمین)
    """
    locations = location_service.get_pending_locations(db, skip, limit)
    
    result = []
    for loc in locations:
        creator = db.query(User).filter(User.id == loc.created_by).first()
        loc_dict = LocationAdminResponse.model_validate(loc).dict()
        loc_dict["creator_name"] = creator.full_name or creator.username
        loc_dict["creator_username"] = creator.username
        result.append(LocationAdminResponse(**loc_dict))
    
    return result

@router.put("/admin/{location_id}/approve", response_model=LocationResponse)
async def admin_approve_location(
    location_id: int,
    approve_data: LocationApprove,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    تایید موقعیت توسط ادمین
    """
    location = location_service.get_location(db, location_id)
    if not location:
        raise HTTPException(status_code=404, detail="موقعیت یافت نشد")
    
    if location.status != "pending":
        raise HTTPException(status_code=400, detail="این موقعیت قبلاً بررسی شده است")
    
    approved = location_service.approve_location(
        db, location_id, current_admin.id, approve_data.admin_notes
    )
    return approved

@router.put("/admin/{location_id}/reject", response_model=MessageResponse)
async def admin_reject_location(
    location_id: int,
    reject_data: LocationReject,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    رد موقعیت توسط ادمین با ذکر دلیل
    """
    location = location_service.get_location(db, location_id)
    if not location:
        raise HTTPException(status_code=404, detail="موقعیت یافت نشد")
    
    if location.status != "pending":
        raise HTTPException(status_code=400, detail="این موقعیت قبلاً بررسی شده است")
    
    rejected = location_service.reject_location(
        db, location_id, current_admin.id, reject_data.reason, reject_data.admin_notes
    )
    return MessageResponse(
        message=f"موقعیت {location.title} رد شد",
        success=True,
        location_id=location_id
    )

@router.delete("/admin/{location_id}", response_model=MessageResponse)
async def admin_delete_location(
    location_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    حذف موقعیت توسط ادمین
    """
    location = location_service.get_location(db, location_id)
    if not location:
        raise HTTPException(status_code=404, detail="موقعیت یافت نشد")
    
    location_service.delete_location(db, location_id)
    return MessageResponse(message=f"موقعیت {location.title} حذف شد")