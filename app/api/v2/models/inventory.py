# app/api/v2/models/inventory.py
from sqlalchemy import Column, Integer, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID  # استفاده از نوع داده اختصاصی UUID پستگرس
from sqlalchemy.orm import relationship
from app.api.v2.models.base import Base, TimestampMixin

class Inventory(Base, TimestampMixin):
    __tablename__ = "inventories"
    
    id = Column(Integer, primary_key=True, index=True)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id", ondelete="CASCADE"), nullable=True, index=True)
    
    # استفاده از UUID پستگرس برای همخوانی کامل با شناسهstores.id بدون خطای ناسازگاری تایپ
    store_id = Column(UUID(as_uuid=False), ForeignKey("stores.id", ondelete="CASCADE"), nullable=True, index=True)
    
    product_id = Column(String(50), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    quantity = Column(Float, default=0.0)
    min_stock = Column(Float, default=0.0)
    max_stock = Column(Float, default=0.0)
    
    # روابط استاندارد و بدون تداخل روابط دوطرفه
    warehouse = relationship("Warehouse", back_populates="inventories")
    store = relationship("Store") # 👈 اصلاح شد: رابطه یک‌طرفه ساده و عاری از هرگونه تداخل با مپر کلاس Store
    product = relationship("Product", back_populates="inventories")