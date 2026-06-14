from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v2.core.deps import get_db
from app.api.v2.schemas.inventory import InventoryCreate
from app.api.v2.services.inventory_service import (
    add_inventory,
    get_inventory
)

router = APIRouter(prefix="/inventory", tags=["Inventory"])


@router.post("/{warehouse_id}")
def create(warehouse_id: int, data: InventoryCreate, db: Session = Depends(get_db)):
    return add_inventory(db, warehouse_id, data)


@router.get("/{warehouse_id}")
def list_items(warehouse_id: int, db: Session = Depends(get_db)):
    return get_inventory(db, warehouse_id)