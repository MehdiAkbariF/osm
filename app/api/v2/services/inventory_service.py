# app/api/v2/services/inventory_service.py
from sqlalchemy.orm import Session
from typing import List
from app.api.v2.models.inventory import Inventory
from app.api.v2.models.product import Product
from app.api.v2.schemas.inventory import InventoryCreate

def add_bulk_inventory(
    db: Session, 
    warehouse_id: int | None, 
    store_id: str | None, 
    items_data: List[InventoryCreate]
):
    added_inventories = []
    
    for data in items_data:
        # ۱. همگام‌سازی مشخصات محصول با دیتابیس محلی
        product = db.query(Product).filter(Product.id == data.product_id).first()
        if not product:
            product = Product(
                id=data.product_id,
                name=data.product_title
            )
            db.add(product)
            db.commit()
            db.refresh(product)
        else:
            if product.name != data.product_title:
                product.name = data.product_title
                db.commit()

        # ۲. بررسی و ثبت/آپدیت موجودی بر اساس نوع تخصیص (انبار یا فروشگاه)
        if warehouse_id:
            inventory = db.query(Inventory).filter(
                Inventory.warehouse_id == warehouse_id,
                Inventory.product_id == data.product_id
            ).first()
        else:
            inventory = db.query(Inventory).filter(
                Inventory.store_id == store_id,
                Inventory.product_id == data.product_id
            ).first()

        if inventory:
            inventory.quantity = data.quantity
            if data.min_stock is not None:
                inventory.min_stock = data.min_stock
            if data.max_stock is not None:
                inventory.max_stock = data.max_stock
        else:
            inventory = Inventory(
                warehouse_id=warehouse_id,
                store_id=store_id,
                product_id=data.product_id,
                quantity=data.quantity,
                min_stock=data.min_stock or 0.0,
                max_stock=data.max_stock or 100.0
            )
            db.add(inventory)

        db.commit()
        db.refresh(inventory)
        added_inventories.append(inventory)

    return added_inventories

def get_inventory_by_warehouse(db: Session, warehouse_id: int):
    return db.query(Inventory).filter(Inventory.warehouse_id == warehouse_id).all()

def get_inventory_by_store(db: Session, store_id: str):
    return db.query(Inventory).filter(Inventory.store_id == store_id).all()