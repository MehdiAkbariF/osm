from sqlalchemy.orm import Session
from typing import Optional, List
from app.api.v2.models.store import Store
from app.api.v2.schemas.store import StoreUpdate


def create_store(db: Session, user_id: int, data):
    store = Store(
        user_id=user_id,
        name=data.name,
        lat=data.lat,
        lon=data.lon,
        address=data.address,
        phone=data.phone
    )

    db.add(store)
    db.commit()
    db.refresh(store)
    return store


def get_stores(db: Session, user_id: int | None = None) -> List[Store]:
    query = db.query(Store)

    if user_id:
        query = query.filter(Store.user_id == user_id)

    return query.all()


def get_store(db: Session, store_id: int) -> Optional[Store]:
    """دریافت یک فروشگاه با شناسه"""
    return db.query(Store).filter(Store.id == store_id).first()


def update_store(db: Session, store_id: int, data: StoreUpdate) -> Optional[Store]:
    """به‌روزرسانی فروشگاه"""
    store = get_store(db, store_id)
    if not store:
        return None
    
    # فقط فیلدهایی که ارسال شده‌اند را به‌روز می‌کنیم
    if data.name is not None:
        store.name = data.name
    if data.lat is not None:
        store.lat = data.lat
    if data.lon is not None:
        store.lon = data.lon
    if data.address is not None:
        store.address = data.address
    if data.phone is not None:
        store.phone = data.phone
    
    db.commit()
    db.refresh(store)
    return store


def delete_store(db: Session, store_id: int) -> bool:
    """حذف فروشگاه"""
    store = get_store(db, store_id)
    if not store:
        return False
    
    db.delete(store)
    db.commit()
    return True