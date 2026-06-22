# c:\Users\Raven\OSM\app\api\v2\endpoints\inventory.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.api.v2.core.deps import get_db
from app.api.v2.schemas.inventory import InventoryCreate, InventoryOut
from app.api.v2.services.inventory_service import (
    add_bulk_inventory,
    get_inventory_by_warehouse,
    get_inventory_by_store
)
from app.api.v2.endpoints.auth import get_current_user

router = APIRouter(prefix="/inventory", tags=["Inventory"])


@router.post("/warehouse/{warehouse_id}", response_model=List[InventoryOut])
def create_warehouse_inventory(warehouse_id: int, data: List[InventoryCreate], db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ["super_admin", "warehouse_manager"]:
        raise HTTPException(status_code=403, detail="Permission denied")
    return add_bulk_inventory(db, warehouse_id=warehouse_id, store_id=None, items_data=data)


@router.post("/store/{store_id}", response_model=List[InventoryOut])
def create_store_inventory(store_id: str, data: List[InventoryCreate], db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ["super_admin", "warehouse_manager"]:
        raise HTTPException(status_code=403, detail="Permission denied")
    return add_bulk_inventory(db, warehouse_id=None, store_id=store_id, items_data=data)


@router.get("/warehouse/{warehouse_id}", response_model=List[InventoryOut])
def list_warehouse_items(warehouse_id: int, db: Session = Depends(get_db)):
    return get_inventory_by_warehouse(db, warehouse_id)


@router.get("/store/{store_id}", response_model=List[InventoryOut])
def list_store_items(store_id: str, db: Session = Depends(get_db)):
    return get_inventory_by_store(db, store_id)