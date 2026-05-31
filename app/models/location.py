# app/models/location.py
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    
    # اطلاعات اصلی موقعیت
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # مختصات جغرافیایی
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    
    # اطلاعات مکانی (برای نمایش در نقشه)
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    province = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    
    # دسته‌بندی (اختیاری)
    category = Column(String(50), nullable=True)  # shop, office, warehouse, other
    tags = Column(Text, nullable=True)  # JSON array یا متن ساده با کاما
    
    # اطلاعات تماس
    phone_number = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    website = Column(String(200), nullable=True)
    
    # ساعت کاری (JSON)
    working_hours = Column(Text, nullable=True)
    
    # تصاویر (JSON array از URLها)
    images = Column(Text, nullable=True)
    
    # فیلدهای وضعیت
    status = Column(String(20), default="pending")  # pending, approved, rejected, blocked
    is_active = Column(Boolean, default=True)
    
    # فیلدهای مدیریتی
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    rejected_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # دلایل رد (اختیاری)
    rejection_reason = Column(Text, nullable=True)
    admin_notes = Column(Text, nullable=True)
    
    # فیلدهای زمانی
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    approved_at = Column(DateTime(timezone=True), nullable=True)
    rejected_at = Column(DateTime(timezone=True), nullable=True)
    
    # روابط
    creator = relationship("User", foreign_keys=[created_by])
    approver = relationship("User", foreign_keys=[approved_by])
    rejecter = relationship("User", foreign_keys=[rejected_by])
    
    def __repr__(self):
        return f"<Location {self.title} ({self.latitude}, {self.longitude})>"