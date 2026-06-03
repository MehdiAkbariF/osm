# app/api/v1/endpoints/admin_locations.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
from app.core.database import get_db
from app.models.user import User
from app.schemas.location import (
    LocationCreate, LocationResponse, LocationAdminResponse, LocationApprove, LocationReject, MessageResponse
)
from app.services.location_service import location_service
from app.api.v1.dependencies import get_current_admin

router = APIRouter(prefix="/admin/locations", tags=["Admin Locations"])

def parse_location_to_dict(loc, db: Session = None) -> dict:
    """تبدیل ایمن آبجکت دیتابیس به دیکشنری برای Pydantic با تغییر نام فیلد metadata"""
    loc_data = {c.name: getattr(loc, c.name) for c in loc.__table__.columns}
    loc_data["metadata"] = loc_data.pop("meta_data", None)
    
    if db:
        if loc.created_by:
            creator = db.query(User).filter(User.id == loc.created_by).first()
            if creator:
                loc_data["creator_name"] = creator.full_name or creator.username
                loc_data["creator_username"] = creator.username
        else:
            loc_data["creator_name"] = "کاربر مهمان (Anonymous)"
            loc_data["creator_username"] = "guest"
            
    return loc_data

@router.post("/", response_model=LocationResponse, status_code=status.HTTP_201_CREATED)
async def admin_create_location_on_behalf(
    location_data: LocationCreate,
    creator_id: Optional[int] = Query(None, description="شناسه کاربری فرد مالک در دیتابیس نقشه (در صورت وجود)"),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    owner_id = creator_id if creator_id is not None else current_admin.id
    
    location = location_service.create_location(db, location_data, user_id=owner_id)
    location.status = "approved"
    location.approved_by = current_admin.id
    location.approved_at = datetime.utcnow()
    db.commit()
    db.refresh(location)
    
    return LocationResponse(**parse_location_to_dict(location))


@router.get("/all", response_model=List[LocationAdminResponse])
async def admin_get_all_locations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: Optional[str] = Query(None, description="pending, approved, rejected"),
    category: Optional[str] = None,
    city: Optional[str] = None,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    locations = location_service.get_all_locations(db, skip, limit, status, category, city)
    return [LocationAdminResponse(**parse_location_to_dict(loc, db)) for loc in locations]


@router.get("/pending", response_model=List[LocationAdminResponse])
async def admin_get_pending_locations(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    locations = location_service.get_pending_locations(db, skip, limit)
    return [LocationAdminResponse(**parse_location_to_dict(loc, db)) for loc in locations]


@router.put("/{location_id}/approve", response_model=LocationResponse)
async def admin_approve_location(
    location_id: int,
    approve_data: LocationApprove,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    location = location_service.get_location(db, location_id)
    if not location:
        raise HTTPException(status_code=404, detail="موقعیت یافت نشد")
    
    if location.status != "pending":
        raise HTTPException(status_code=400, detail="این موقعیت قبلاً بررسی شده است")
    
    approved = location_service.approve_location(
        db, location_id, current_admin.id, approve_data.admin_notes
    )
    return LocationResponse(**parse_location_to_dict(approved))


@router.put("/{location_id}/reject", response_model=MessageResponse)
async def admin_reject_location(
    location_id: int,
    reject_data: LocationReject,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    location = location_service.get_location(db, location_id)
    if not location:
        raise HTTPException(status_code=404, detail="موقعیت یافت نشد")
    
    if location.status != "pending":
        raise HTTPException(status_code=400, detail="این موقعیت قبلاً بررسی شده است")
    
    location_service.reject_location(
        db, location_id, current_admin.id, reject_data.reason, reject_data.admin_notes
    )
    return MessageResponse(
        message=f"موقعیت {location.title} رد شد",
        success=True,
        location_id=location_id
    )


@router.delete("/{location_id}", response_model=MessageResponse)
async def admin_delete_location(
    location_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    location = location_service.get_location(db, location_id)
    if not location:
        raise HTTPException(status_code=404, detail="موقعیت یافت نشد")
    
    location_service.delete_location(db, location_id)
    return MessageResponse(message=f"موقعیت {location.title} حذف شد", location_id=location_id)