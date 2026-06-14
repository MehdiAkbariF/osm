from app.api.v2.models.inventory import Inventory


def add_inventory(db, warehouse_id: int, data):
    item = Inventory(
        warehouse_id=warehouse_id,
        product_id=data.product_id,
        quantity=data.quantity
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def get_inventory(db, warehouse_id: int):
    return db.query(Inventory).filter(
        Inventory.warehouse_id == warehouse_id
    ).all()