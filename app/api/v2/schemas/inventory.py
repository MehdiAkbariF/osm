from pydantic import BaseModel


class InventoryCreate(BaseModel):
    product_id: int
    quantity: int = 0


class InventoryOut(BaseModel):
    id: int
    product_id: int
    quantity: int

    class Config:
        from_attributes = True