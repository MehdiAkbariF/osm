from pydantic import BaseModel
from typing import Optional

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
    store_id: int
    
    class Config:
        from_attributes = True