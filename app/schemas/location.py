# app/schemas/location.py
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

class LocationBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=200, description="عنوان موقعیت")
    description: Optional[str] = Field(None, description="توضیحات اختیاری")
    latitude: float = Field(..., ge=-90, le=90, description="عرض جغرافیایی")
    longitude: float = Field(..., ge=-180, le=180, description="طول جغرافیایی")
    category: Optional[str] = Field("shop", description="دسته‌بندی")
    
    shop_id: Optional[str] = Field(None, description="شناسه مغازه در سیستم یدکچی")
    plaque: Optional[str] = Field(None, description="پلاک")
    unit: Optional[str] = Field(None, description="واحد")
    tell: Optional[str] = Field(None, description="تلفن تماس")
    
    # 🛠 رفع باگ خطای ۵۰۰: تبدیل به Optional تا در صورت NULL بودن در رکوردهای قدیمی خطا ندهد
    is_return_usage: Optional[bool] = Field(False, description="قابلیت مرجوعی کالا")
    
    metadata: Optional[Dict[str, Any]] = Field(None, description="اطلاعات قطعات و برندها به صورت JSON")

class LocationCreate(LocationBase):
    address: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    postal_code: Optional[str] = None

class LocationUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    category: Optional[str] = None
    shop_id: Optional[str] = None
    plaque: Optional[str] = None
    unit: Optional[str] = None
    tell: Optional[str] = None
    is_return_usage: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None
    address: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    postal_code: Optional[str] = None

class LocationApprove(BaseModel):
    admin_notes: Optional[str] = None

class LocationReject(BaseModel):
    reason: str = Field(..., min_length=3, max_length=500, description="دلیل رد موقعیت")
    admin_notes: Optional[str] = None

class LocationResponse(LocationBase):
    id: int
    address: Optional[str]
    city: Optional[str]
    province: Optional[str]
    postal_code: Optional[str]
    status: str
    is_active: bool
    created_by: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]
    approved_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None

    class Config:
        from_attributes = True
        orm_mode = True # برای سازگاری با هر دو نسخه پیدانتیک

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