from sqlalchemy.orm import Session
from typing import Optional, List
from app.api.v2.models.warehouse import Warehouse
from app.api.v2.schemas.warehouse import WarehouseCreate, WarehouseUpdate


def create_warehouse(db: Session, store_id: int, data: WarehouseCreate):
    """ایجاد انبار جدید با داده‌های کامل"""
    warehouse = Warehouse(
        store_id=store_id,
        name=data.name,
        lat=data.lat,
        lon=data.lon,
        address=data.address,
        phone=data.phone
    )
    
    db.add(warehouse)
    db.commit()
    db.refresh(warehouse)
    return warehouse


def get_warehouses(db: Session, store_id: int) -> List[Warehouse]:
    """دریافت لیست انبارهای یک فروشگاه"""
    return db.query(Warehouse).filter(Warehouse.store_id == store_id).all()


def get_warehouse(db: Session, warehouse_id: int) -> Optional[Warehouse]:
    """دریافت یک انبار با شناسه"""
    return db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()


def update_warehouse(db: Session, warehouse_id: int, data: WarehouseUpdate) -> Optional[Warehouse]:
    """به‌روزرسانی انبار"""
    warehouse = get_warehouse(db, warehouse_id)
    if not warehouse:
        return None
    
    update_data = data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(warehouse, field, value)
    
    db.commit()
    db.refresh(warehouse)
    return warehouse


def delete_warehouse(db: Session, warehouse_id: int) -> bool:
    """حذف انبار"""
    warehouse = get_warehouse(db, warehouse_id)
    if not warehouse:
        return False
    
    db.delete(warehouse)
    db.commit()
    return True