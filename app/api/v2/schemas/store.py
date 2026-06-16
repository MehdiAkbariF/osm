# c:\Users\Raven\OSM\app\api\v2\schemas\store.py
from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class StoreBase(BaseModel):
    name: str
    lat: float
    lon: float
    address: Optional[str] = None
    phone: Optional[str] = None
    shop_id: Optional[UUID] = None


class StoreCreate(StoreBase):
    pass


class StoreUpdate(BaseModel):
    name: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    shop_id: Optional[UUID] = None


class StoreResponse(StoreBase):
    id: UUID
    user_id: Optional[int] = None
    status: Optional[str] = None
    admin_notes: Optional[str] = None

    class Config:
        from_attributes = True