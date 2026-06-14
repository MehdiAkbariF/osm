from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.api.v2.schemas.warehouse import WarehouseCreate, WarehouseUpdate, WarehouseResponse
from app.api.v2.services.warehouse_service import (
    create_warehouse,
    get_warehouses,
    get_warehouse,
    update_warehouse,
    delete_warehouse
)
from app.core.database import get_db

router = APIRouter(prefix="/warehouses", tags=["Warehouses"])


@router.post("/{store_id}", response_model=WarehouseResponse)
def create(store_id: int, warehouse: WarehouseCreate, db: Session = Depends(get_db)):
    """ایجاد انبار جدید برای فروشگاه"""
    return create_warehouse(db, store_id=store_id, data=warehouse)


@router.get("/{store_id}", response_model=List[WarehouseResponse])
def list_warehouses(store_id: int, db: Session = Depends(get_db)):
    """دریافت لیست انبارهای یک فروشگاه"""
    return get_warehouses(db, store_id=store_id)


@router.get("/detail/{warehouse_id}", response_model=WarehouseResponse)
def get(warehouse_id: int, db: Session = Depends(get_db)):
    """دریافت جزئیات یک انبار"""
    warehouse = get_warehouse(db, warehouse_id)
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    return warehouse


@router.put("/{warehouse_id}", response_model=WarehouseResponse)
def update(warehouse_id: int, data: WarehouseUpdate, db: Session = Depends(get_db)):
    """به‌روزرسانی انبار"""
    warehouse = update_warehouse(db, warehouse_id, data)
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    return warehouse


@router.delete("/{warehouse_id}")
def delete(warehouse_id: int, db: Session = Depends(get_db)):
    """حذف انبار"""
    ok = delete_warehouse(db, warehouse_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    return {"message": "Warehouse deleted successfully"}