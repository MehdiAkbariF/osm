# c:\Users\Raven\OSM\app\api\v2\endpoints\warehouses.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List

from app.api.v2.schemas.warehouse import WarehouseCreate, WarehouseUpdate, WarehouseResponse
from app.core.database import get_db
from app.api.v2.endpoints.auth import get_current_user

router = APIRouter(prefix="/warehouses", tags=["Warehouses"])


@router.post("/{store_id}", response_model=WarehouseResponse)
def create(store_id: str, warehouse: WarehouseCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "super_admin":
        raise HTTPException(status_code=403, detail="Permission denied")
    
    try:
        db.execute(
            text(
                "INSERT INTO warehouses (name, lat, lon, address, phone, store_id) "
                "VALUES (:name, :lat, :lon, :address, :phone, :store_id);"
            ),
            {
                "name": warehouse.name,
                "lat": warehouse.lat,
                "lon": warehouse.lon,
                "address": warehouse.address,
                "phone": warehouse.phone,
                "store_id": store_id
            }
        )
        db.commit()
        
        result = db.execute(
            text("SELECT id, name, lat, lon, address, phone, store_id FROM warehouses WHERE store_id = :store_id ORDER BY id DESC LIMIT 1;"),
            {"store_id": store_id}
        )
        return result.mappings().one()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{store_id}", response_model=List[WarehouseResponse])
def list_warehouses(store_id: str, db: Session = Depends(get_db)):
    result = db.execute(
        text("SELECT id, name, lat, lon, address, phone, store_id FROM warehouses WHERE store_id = :store_id;"),
        {"store_id": store_id}
    ).mappings().all()
    return result


@router.get("/detail/{warehouse_id}", response_model=WarehouseResponse)
def get(warehouse_id: int, db: Session = Depends(get_db)):
    result = db.execute(
        text("SELECT id, name, lat, lon, address, phone, store_id FROM warehouses WHERE id = :warehouse_id;"),
        {"warehouse_id": warehouse_id}
    )
    warehouse = result.mappings().one_or_none()
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    return warehouse


@router.put("/{warehouse_id}", response_model=WarehouseResponse)
def update(warehouse_id: int, data: WarehouseUpdate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user["role"] not in ["super_admin", "warehouse_manager"]:
        raise HTTPException(status_code=403, detail="Permission denied")
    
    update_fields = []
    update_values = {}
    for field, value in data.dict(exclude_unset=True).items():
        update_fields.append(f"{field} = :{field}")
        update_values[field] = value
        
    if update_fields:
        update_values["warehouse_id"] = warehouse_id
        sql = f"UPDATE warehouses SET {', '.join(update_fields)} WHERE id = :warehouse_id;"
        db.execute(text(sql), update_values)
        db.commit()
        
    result = db.execute(
        text("SELECT id, name, lat, lon, address, phone, store_id FROM warehouses WHERE id = :warehouse_id;"),
        {"warehouse_id": warehouse_id}
    )
    return result.mappings().one()


@router.delete("/{warehouse_id}")
def delete(warehouse_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "super_admin":
        raise HTTPException(status_code=403, detail="Permission denied")
        
    db.execute(text("DELETE FROM warehouses WHERE id = :warehouse_id;"), {"warehouse_id": warehouse_id})
    db.commit()
    return {"message": "Warehouse deleted successfully"}