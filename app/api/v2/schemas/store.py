from pydantic import BaseModel
from typing import Optional


class StoreBase(BaseModel):
    name: str
    lat: float
    lon: float
    address: Optional[str] = None
    phone: Optional[str] = None


class StoreCreate(StoreBase):
    pass


class StoreUpdate(BaseModel):
    name: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    address: Optional[str] = None
    phone: Optional[str] = None


class StoreResponse(StoreBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True