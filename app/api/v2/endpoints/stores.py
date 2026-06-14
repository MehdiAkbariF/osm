from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.v2.schemas.store import StoreCreate, StoreUpdate, StoreResponse
from app.api.v2.services.store_service import (
    create_store,
    get_store,
    get_stores,
    update_store,
    delete_store
)

from app.core.database import get_db

router = APIRouter(prefix="/stores", tags=["Stores"])


# Create
@router.post("/", response_model=StoreResponse)
def create(store: StoreCreate, db: Session = Depends(get_db)):
    # فعلاً user_id ثابت (بعداً از JWT میاد)
    return create_store(db, user_id=1, data=store)


# Get all
@router.get("/", response_model=list[StoreResponse])
def list_stores(db: Session = Depends(get_db)):
    return get_stores(db)


# Get one
@router.get("/{store_id}", response_model=StoreResponse)
def get(store_id: int, db: Session = Depends(get_db)):
    store = get_store(db, store_id)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    return store


# Update
@router.put("/{store_id}", response_model=StoreResponse)
def update(store_id: int, data: StoreUpdate, db: Session = Depends(get_db)):
    store = update_store(db, store_id, data)
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    return store


# Delete
@router.delete("/{store_id}")
def delete(store_id: int, db: Session = Depends(get_db)):
    ok = delete_store(db, store_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Store not found")
    return {"message": "deleted"}