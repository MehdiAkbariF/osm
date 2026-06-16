# c:\Users\Raven\OSM\app\api\v2\endpoints\stores.py
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel

from app.api.v2.schemas.store import StoreCreate, StoreUpdate, StoreResponse
from app.core.database import get_db
from app.api.v2.endpoints.auth import get_current_user

router = APIRouter(prefix="/stores", tags=["Stores"])


class AdminNotesRequest(BaseModel):
    admin_notes: str


@router.post("/", response_model=StoreResponse)
def create(store: StoreCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "super_admin":
        raise HTTPException(status_code=403, detail="Permission denied")
    
    new_uuid = str(uuid.uuid4())
    shop_id_str = str(store.shop_id) if store.shop_id else None
    
    try:
        db.execute(
            text(
                "INSERT INTO stores (id, name, lat, lon, address, phone, user_id, status, shop_id) "
                "VALUES (:id, :name, :lat, :lon, :address, :phone, :user_id, 'Approved', :shop_id) "
                "RETURNING id, name, lat, lon, address, phone, user_id, shop_id;"
            ),
            {
                "id": new_uuid,
                "name": store.name,
                "lat": store.lat,
                "lon": store.lon,
                "address": store.address,
                "phone": store.phone,
                "user_id": current_user["id"],
                "shop_id": shop_id_str
            }
        )
        db.commit()
        
        result = db.execute(
            text("SELECT id, name, lat, lon, address, phone, user_id, status, admin_notes, shop_id FROM stores WHERE id = :id;"),
            {"id": new_uuid}
        )
        return result.mappings().one()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=list[StoreResponse])
def list_stores(db: Session = Depends(get_db)):
    result = db.execute(
        text("SELECT id, name, lat, lon, address, phone, user_id, status, admin_notes, shop_id FROM stores WHERE status = 'Approved';")
    ).mappings().all()
    return result


@router.get("/admin/pending", response_model=list[StoreResponse])
def list_pending_stores(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "super_admin":
        raise HTTPException(status_code=403, detail="Permission denied")
    result = db.execute(
        text("SELECT id, name, lat, lon, address, phone, user_id, status, admin_notes, shop_id FROM stores WHERE status = 'Pending';")
    ).mappings().all()
    return result


@router.put("/{store_id}/approve", response_model=StoreResponse)
def approve(store_id: str, payload: AdminNotesRequest, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "super_admin":
        raise HTTPException(status_code=403, detail="Permission denied")
    
    check_store = db.execute(
        text("SELECT id FROM stores WHERE id = :store_id;"),
        {"store_id": store_id}
    ).fetchone()
    
    if not check_store:
        raise HTTPException(status_code=404, detail="Store not found")
        
    db.execute(
        text("UPDATE stores SET status = 'Approved', admin_notes = :admin_notes WHERE id = :store_id;"),
        {"admin_notes": payload.admin_notes, "store_id": store_id}
    )
    db.commit()
    
    result = db.execute(
        text("SELECT id, name, lat, lon, address, phone, user_id, status, admin_notes, shop_id FROM stores WHERE id = :store_id;"),
        {"store_id": store_id}
    )
    return result.mappings().one()


@router.put("/{store_id}/reject", response_model=StoreResponse)
def reject(store_id: str, payload: AdminNotesRequest, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "super_admin":
        raise HTTPException(status_code=403, detail="Permission denied")
        
    check_store = db.execute(
        text("SELECT id FROM stores WHERE id = :store_id;"),
        {"store_id": store_id}
    ).fetchone()
    
    if not check_store:
        raise HTTPException(status_code=404, detail="Store not found")
        
    db.execute(
        text("UPDATE stores SET status = 'Rejected', admin_notes = :admin_notes WHERE id = :store_id;"),
        {"admin_notes": payload.admin_notes, "store_id": store_id}
    )
    db.commit()
    
    result = db.execute(
        text("SELECT id, name, lat, lon, address, phone, user_id, status, admin_notes, shop_id FROM stores WHERE id = :store_id;"),
        {"store_id": store_id}
    )
    return result.mappings().one()


@router.get("/{store_id}", response_model=StoreResponse)
def get(store_id: str, db: Session = Depends(get_db)):
    result = db.execute(
        text("SELECT id, name, lat, lon, address, phone, user_id, status, admin_notes, shop_id FROM stores WHERE id = :store_id;"),
        {"store_id": store_id}
    )
    store = result.mappings().one_or_none()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")
    return store


@router.put("/{store_id}", response_model=StoreResponse)
def update(store_id: str, data: StoreUpdate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "super_admin":
        raise HTTPException(status_code=403, detail="Permission denied")
    
    update_fields = []
    update_values = {}
    
    for field, value in data.dict(exclude_unset=True).items():
        if field == "shop_id":
            update_fields.append("shop_id = :shop_id")
            update_values["shop_id"] = str(value) if value else None
        else:
            update_fields.append(f"{field} = :{field}")
            update_values[field] = value
        
    if update_fields:
        update_values["store_id"] = store_id
        sql = f"UPDATE stores SET {', '.join(update_fields)} WHERE id = :store_id;"
        db.execute(text(sql), update_values)
        db.commit()
        
    result = db.execute(
        text("SELECT id, name, lat, lon, address, phone, user_id, status, admin_notes, shop_id FROM stores WHERE id = :store_id;"),
        {"store_id": store_id}
    )
    return result.mappings().one()


@router.delete("/{store_id}")
def delete(store_id: str, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "super_admin":
        raise HTTPException(status_code=403, detail="Permission denied")
        
    db.execute(text("DELETE FROM stores WHERE id = :store_id;"), {"store_id": store_id})
    db.commit()
    return {"message": "deleted"}