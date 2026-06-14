from fastapi import APIRouter

from app.api.v2.endpoints.map import router as map_router
from app.api.v2.endpoints.stores import router as stores_router
from app.api.v2.endpoints.warehouses import router as warehouse_router
from app.api.v2.endpoints.inventory import router as inventory_router

router = APIRouter()

router.include_router(map_router)
router.include_router(stores_router)
router.include_router(warehouse_router)
router.include_router(inventory_router)