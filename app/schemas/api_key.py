# app/schemas/api_key.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class APIKeyCreate(BaseModel):
    name: Optional[str] = Field(None, max_length=100, description="نام یا برچسب کلید")
    expires_at: Optional[datetime] = Field(None, description="تاریخ انقضا (در صورت داشتن انقضا)")
    is_unlimited: bool = Field(False, description="آیا کلید بدون تاریخ انقضا است؟")
    rate_limit: int = Field(60, ge=1, description="تعداد درخواست مجاز در دقیقه")

class APIKeyResponse(BaseModel):
    id: int
    masked_key: str
    name: Optional[str]
    is_active: bool
    is_unlimited: bool
    expires_at: Optional[datetime] = None
    rate_limit: int
    created_at: datetime
    last_used_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class APIKeyCreateResponse(APIKeyResponse):
    raw_key: str  # کلید متنی که فقط یک‌بار در زمان ساخت برای کاربر نمایش داده می‌شود

class APIKeyAdminUpdate(BaseModel):
    is_active: Optional[bool] = None
    is_unlimited: Optional[bool] = None
    expires_at: Optional[datetime] = None
    rate_limit: Optional[int] = None