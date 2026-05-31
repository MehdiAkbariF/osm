# app/models/api_key.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(255), unique=True, index=True, nullable=False)  # کلید اصلی (تولید شده تصادفی)
    masked_key = Column(String(50), nullable=False)  # کلید ماسک شده برای نمایش‌های بعدی
    name = Column(String(100), nullable=True)  # نام یا برچسب اختیاری
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    is_active = Column(Boolean, default=True)
    is_unlimited = Column(Boolean, default=False)  # بدون تاریخ انقضا
    expires_at = Column(DateTime(timezone=True), nullable=True)
    rate_limit = Column(Integer, default=60)  # سقف درخواست در دقیقه
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_used_at = Column(DateTime(timezone=True), nullable=True)

    # روابط با جدول کاربران
    user = relationship("User", backref="api_keys")

    def __repr__(self):
        return f"<APIKey {self.masked_key} - User {self.user_id}>"