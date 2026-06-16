# c:\Users\Raven\OSM\app\api\v2\schemas\warehouse.py
from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class WarehouseBase(BaseModel):
    name: str
    lat: float
    lon: float
    address: Optional[str] = None
    phone: Optional[str] = None


class WarehouseCreate(WarehouseBase):
    pass


class WarehouseUpdate(BaseModel):
    name: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    address: Optional[str] = None
    phone: Optional[str] = None


class WarehouseResponse(WarehouseBase):
    id: int
    store_id: UUID

    class Config:
        from_attributes = True