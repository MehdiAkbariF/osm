# app/schemas/location.py
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime

# ========== مدل‌های ورودی (Request) ==========
class LocationBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=200, description="عنوان موقعیت")
    description: Optional[str] = Field(None, description="توضیحات")
    latitude: float = Field(..., ge=-90, le=90, description="عرض جغرافیایی")
    longitude: float = Field(..., ge=-180, le=180, description="طول جغرافیایی")
    address: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    postal_code: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    working_hours: Optional[str] = None
    images: Optional[str] = None

class LocationCreate(LocationBase):
    pass

class LocationUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    postal_code: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    working_hours: Optional[str] = None
    images: Optional[str] = None

class LocationApprove(BaseModel):
    admin_notes: Optional[str] = None

class LocationReject(BaseModel):
    reason: str = Field(..., min_length=3, max_length=500, description="دلیل رد موقعیت")
    admin_notes: Optional[str] = None

# ========== مدل‌های خروجی (Response) ==========
class LocationResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    latitude: float
    longitude: float
    address: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    postal_code: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    working_hours: Optional[str] = None
    images: Optional[str] = None
    status: str
    is_active: bool
    created_by: int
    created_at: datetime
    approved_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    
    class Config:
        from_attributes = True

class LocationAdminResponse(LocationResponse):
    creator_name: Optional[str] = None
    creator_username: Optional[str] = None
    approver_name: Optional[str] = None
    admin_notes: Optional[str] = None

class LocationListResponse(BaseModel):
    total: int
    items: List[LocationResponse]

class MessageResponse(BaseModel):
    message: str
    success: bool = True
    location_id: Optional[int] = None