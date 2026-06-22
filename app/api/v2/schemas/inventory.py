# app/api/v2/schemas/inventory.py
from pydantic import BaseModel
from typing import Optional, List


class ProductBase(BaseModel):
    id: str
    name: str


class ProductCreate(ProductBase):
    pass


class InventoryCreate(BaseModel):
    product_id: str
    product_title: str
    quantity: float = 0.0
    min_stock: Optional[float] = 0.0
    max_stock: Optional[float] = 0.0


class InventoryOut(BaseModel):
    id: int
    product_id: str
    quantity: float
    min_stock: float
    max_stock: float
    warehouse_id: Optional[int] = None # 👈 اضافه شد
    store_id: Optional[str] = None     # 👈 اضافه شد
    product: Optional[ProductBase] = None

    class Config:
        from_attributes = True