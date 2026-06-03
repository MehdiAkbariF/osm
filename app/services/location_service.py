# app/services/location_service.py
import math
from sqlalchemy.orm import Session
from app.models.location import Location
from app.schemas.location import LocationCreate, LocationUpdate
from app.services.postgis_service import postgis_service
from datetime import datetime
from typing import Optional, List

class LocationService:
    
    @staticmethod
    def create_location(db: Session, location_data: LocationCreate, user_id: Optional[int]) -> Location:
        loc_dict = location_data.model_dump(exclude_unset=True) if hasattr(location_data, 'model_dump') else location_data.dict(exclude_unset=True)
        
        # 🛠 تغییر کلیدی: تبدیل کلید به meta_data برای ذخیره ایمن در دیتابیس
        if "metadata" in loc_dict:
            loc_dict["meta_data"] = loc_dict.pop("metadata")
            
        loc_dict.pop("created_by", None)
        loc_dict.pop("status", None)
        loc_dict.pop("is_active", None)
        
        try:
            geo_info = postgis_service.smart_reverse_geocode(
                lat=location_data.latitude, 
                lon=location_data.longitude
            )
            if geo_info:
                loc_dict["address"] = location_data.address or geo_info.get("address")
                loc_dict["city"] = location_data.city or geo_info.get("city")
                loc_dict["province"] = location_data.province or geo_info.get("province")
                loc_dict["postal_code"] = location_data.postal_code or geo_info.get("postal_code")
        except Exception as e:
            print(f"Warning: Auto reverse-geocoding failed: {str(e)}")

        status_val = "pending"
        if user_id:
            from app.models.user import User
            user = db.query(User).filter(User.id == user_id).first()
            if user and user.is_admin:
                status_val = "approved"

        location = Location(
            **loc_dict,
            created_by=user_id,
            status=status_val,
            is_active=True
        )
        db.add(location)
        db.commit()
        db.refresh(location)
        return location
    
    @staticmethod
    def get_location(db: Session, location_id: int) -> Optional[Location]:
        return db.query(Location).filter(Location.id == location_id).first()
    
    @staticmethod
    def get_user_locations(db: Session, user_id: int, skip: int = 0, limit: int = 100, status: Optional[str] = None) -> List[Location]:
        query = db.query(Location).filter(Location.created_by == user_id)
        if status:
            query = query.filter(Location.status == status)
        return query.order_by(Location.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_pending_locations(db: Session, skip: int = 0, limit: int = 100) -> List[Location]:
        return db.query(Location).filter(Location.status == "pending").order_by(Location.created_at.asc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_all_locations(db: Session, skip: int = 0, limit: int = 100, status: Optional[str] = None, category: Optional[str] = None, city: Optional[str] = None) -> List[Location]:
        query = db.query(Location)
        if status:
            query = query.filter(Location.status == status)
        if category:
            query = query.filter(Location.category == category)
        if city:
            query = query.filter(Location.city == city)
        return query.order_by(Location.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def search_locations(db: Session, lat: float, lon: float, radius_km: float = 5.0, part_filter: Optional[str] = None, brand_filter: Optional[str] = None, is_return_usage: Optional[bool] = None, limit: int = 20) -> List[Location]:
        query = db.query(Location).filter(Location.status == "approved", Location.is_active == True)

        if is_return_usage is not None:
            query = query.filter(Location.is_return_usage == is_return_usage)

        # جستجو در فیلد JSON صحیح
        if part_filter:
            query = query.filter(Location.meta_data["parts"].contains([part_filter]))
        if brand_filter:
            query = query.filter(Location.meta_data["brand"] == brand_filter)

        all_locations = query.all()

        def calculate_distance(lat1, lon1, lat2, lon2):
            R = 6371.0
            phi1 = math.radians(lat1)
            phi2 = math.radians(lat2)
            delta_phi = math.radians(lat2 - lat1)
            delta_lambda = math.radians(lon2 - lon1)
            a = math.sin(delta_phi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda/2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
            return R * c

        nearby = []
        for loc in all_locations:
            distance = calculate_distance(lat, lon, loc.latitude, loc.longitude)
            if distance <= radius_km:
                nearby.append((distance, loc))
        
        nearby.sort(key=lambda x: x[0])
        return [loc for _, loc in nearby[:limit]]
    
    @staticmethod
    def update_location(db: Session, location_id: int, location_data: LocationUpdate) -> Optional[Location]:
        location = LocationService.get_location(db, location_id)
        if not location:
            return None
        
        update_data = location_data.model_dump(exclude_unset=True) if hasattr(location_data, 'model_dump') else location_data.dict(exclude_unset=True)
        if "metadata" in update_data:
            update_data["meta_data"] = update_data.pop("metadata")
            
        for field, value in update_data.items():
            setattr(location, field, value)
        
        location.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(location)
        return location
    
    @staticmethod
    def approve_location(db: Session, location_id: int, admin_id: int, admin_notes: Optional[str] = None) -> Optional[Location]:
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
    def reject_location(db: Session, location_id: int, admin_id: int, reason: str, admin_notes: Optional[str] = None) -> Optional[Location]:
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
        location = LocationService.get_location(db, location_id)
        if not location:
            return False
        db.delete(location)
        db.commit()
        return True

location_service = LocationService()