from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.api.v2.models.base import Base, TimestampMixin

class Warehouse(Base, TimestampMixin):
    __tablename__ = "warehouses"
    
    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String, nullable=False)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    address = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    
    store = relationship("Store", back_populates="warehouses")
    inventories = relationship("Inventory", back_populates="warehouse", cascade="all, delete-orphan")