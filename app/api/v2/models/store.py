# app/api/v2/models/store.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.api.v2.models.base import Base, TimestampMixin

class Store(Base, TimestampMixin):
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    lat = Column(Float, nullable=False)
    lon = Column(Float, nullable=False)
    address = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    is_warehouse = Column(Boolean, default=False, nullable=False)  # 👈 اضافه شد

    user = relationship("User", back_populates="stores")
    warehouses = relationship("Warehouse", back_populates="store", cascade="all, delete-orphan")