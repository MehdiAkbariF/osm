# app/models/user_location.py
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class LocationStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class UserLocation(Base):
    __tablename__ = "user_locations"

    id = Column(Integer, primary_key=True, index=True)
    
    # اطلاعات موقعیت
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    province = Column(String(100), nullable=True)
    
    # اطلاعات تماس
    phone_number = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    
    # دسته‌بندی و تگ‌ها
    category = Column(String(50), nullable=True)
    tags = Column(Text, nullable=True)
    
    # وضعیت
    status = Column(Enum(LocationStatus), default=LocationStatus.PENDING)
    is_visible = Column(Boolean, default=False)
    
    # روابط
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # زمان‌ها
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    approved_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<UserLocation {self.title}>"