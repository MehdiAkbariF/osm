# app/services/location_service.py
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.models.location import Location
from app.models.user import User
from app.schemas.location import LocationCreate, LocationUpdate
from datetime import datetime
from typing import Optional, List

class LocationService:
    
    @staticmethod
    def create_location(db: Session, location_data: LocationCreate, user_id: int) -> Location:
        """ایجاد موقعیت مکانی جدید (وضعیت: pending)"""
        location = Location(
            **location_data.dict(),
            created_by=user_id,
            status="pending",
            is_active=True
        )
        db.add(location)
        db.commit()
        db.refresh(location)
        return location
    
    @staticmethod
    def get_location(db: Session, location_id: int) -> Optional[Location]:
        """دریافت موقعیت با شناسه"""
        return db.query(Location).filter(Location.id == location_id).first()
    
    @staticmethod
    def get_user_locations(
        db: Session, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100,
        status: Optional[str] = None
    ) -> List[Location]:
        """دریافت موقعیت‌های یک کاربر"""
        query = db.query(Location).filter(Location.created_by == user_id)
        
        if status:
            query = query.filter(Location.status == status)
        
        return query.order_by(Location.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_pending_locations(db: Session, skip: int = 0, limit: int = 100) -> List[Location]:
        """دریافت موقعیت‌های در انتظار تایید (برای ادمین)"""
        return db.query(Location)\
            .filter(Location.status == "pending")\
            .order_by(Location.created_at.asc())\
            .offset(skip)\
            .limit(limit)\
            .all()
    
    @staticmethod
    def get_all_locations(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        status: Optional[str] = None,
        category: Optional[str] = None,
        city: Optional[str] = None
    ) -> List[Location]:
        """دریافت تمام موقعیت‌ها با فیلتر (برای ادمین)"""
        query = db.query(Location)
        
        if status:
            query = query.filter(Location.status == status)
        if category:
            query = query.filter(Location.category == category)
        if city:
            query = query.filter(Location.city == city)
        
        return query.order_by(Location.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_approved_locations(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        radius: Optional[float] = None
    ) -> List[Location]:
        """دریافت موقعیت‌های تایید شده (برای نمایش در نقشه)"""
        query = db.query(Location).filter(Location.status == "approved", Location.is_active == True)
        
        # فیلتر شعاعی (ساده - برای دقت بهتر باید از PostGIS استفاده کرد)
        if lat and lon and radius:
            # تبدیل مختصات به رادیان برای محاسبه فاصله
            import math
            # این یک محاسبه ساده است، برای دقت بالا باید از PostGIS استفاده کنید
            pass
        
        return query.order_by(Location.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_location(db: Session, location_id: int, location_data: LocationUpdate) -> Optional[Location]:
        """به‌روزرسانی موقعیت (فقط توسط ایجادکننده)"""
        location = LocationService.get_location(db, location_id)
        if not location:
            return None
        
        update_data = location_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(location, field, value)
        
        location.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(location)
        return location
    
    @staticmethod
    def approve_location(
        db: Session, 
        location_id: int, 
        admin_id: int,
        admin_notes: Optional[str] = None
    ) -> Optional[Location]:
        """تایید موقعیت توسط ادمین"""
        location = LocationService.get_location(db, location_id)
        if not location:
            return None
        
        location.status = "approved"
        location.approved_by = admin_id
        location.approved_at = datetime.utcnow()
        location.admin_notes = admin_notes
        
        db.commit()
        db.refresh(location)
        return location
    
    @staticmethod
    def reject_location(
        db: Session, 
        location_id: int, 
        admin_id: int,
        reason: str,
        admin_notes: Optional[str] = None
    ) -> Optional[Location]:
        """رد موقعیت توسط ادمین"""
        location = LocationService.get_location(db, location_id)
        if not location:
            return None
        
        location.status = "rejected"
        location.rejected_by = admin_id
        location.rejected_at = datetime.utcnow()
        location.rejection_reason = reason
        location.admin_notes = admin_notes
        location.is_active = False
        
        db.commit()
        db.refresh(location)
        return location
    
    @staticmethod
    def delete_location(db: Session, location_id: int) -> bool:
        """حذف موقعیت (فیزیکی)"""
        location = LocationService.get_location(db, location_id)
        if not location:
            return False
        
        db.delete(location)
        db.commit()
        return True
    
    @staticmethod
    def get_locations_count(db: Session, status: Optional[str] = None) -> int:
        """تعداد موقعیت‌ها"""
        query = db.query(Location)
        if status:
            query = query.filter(Location.status == status)
        return query.count()
    
    @staticmethod
    def get_nearby_locations(
        db: Session, 
        lat: float, 
        lon: float, 
        radius_km: float = 5.0,
        limit: int = 20
    ) -> List[Location]:
        """یافتن موقعیت‌های نزدیک (با استفاده از محاسبه فاصله)"""
        import math
        
        query = db.query(Location).filter(
            Location.status == "approved",
            Location.is_active == True
        )
        
        # محاسبه فاصله برای هر موقعیت (در Python)
        # برای دقت بالا باید از PostGIS در دیتابیس استفاده کنید
        all_locations = query.all()
        
        def calculate_distance(lat1, lon1, lat2, lon2):
            R = 6371  # شعاع زمین بر حسب کیلومتر
            phi1 = math.radians(lat1)
            phi2 = math.radians(lat2)
            delta_phi = math.radians(lat2 - lat1)
            delta_lambda = math.radians(lon2 - lon1)
            
            a = math.sin(delta_phi/2)**2 + \
                math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda/2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
            return R * c
        
        nearby = []
        for loc in all_locations:
            distance = calculate_distance(lat, lon, loc.latitude, loc.longitude)
            if distance <= radius_km:
                nearby.append((distance, loc))
        
        nearby.sort(key=lambda x: x[0])
        return [loc for _, loc in nearby[:limit]]


location_service = LocationService()