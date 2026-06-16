# c:\Users\Raven\OSM\app\api\v2\endpoints\inventory.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.v2.core.deps import get_db
from app.api.v2.schemas.inventory import InventoryCreate
from app.api.v2.services.inventory_service import (
    add_inventory,
    get_inventory
)
from app.api.v2.endpoints.auth import get_current_user

router = APIRouter(prefix="/inventory", tags=["Inventory"])


@router.post("/{warehouse_id}")
def create(warehouse_id: int, data: InventoryCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ["super_admin", "warehouse_manager"]:
        raise HTTPException(status_code=403, detail="Permission denied")
    return add_inventory(db, warehouse_id, data)


@router.get("/{warehouse_id}")
def list_items(warehouse_id: int, db: Session = Depends(get_db)):
    return get_inventory(db, warehouse_id)