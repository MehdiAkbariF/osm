from sqlalchemy import Column, Integer, String, Float, Text
from sqlalchemy.orm import relationship
from app.api.v2.models.base import Base, TimestampMixin

class Product(Base, TimestampMixin):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    sku = Column(String, unique=True, index=True, nullable=False)
    price = Column(Float, nullable=False)
    cost = Column(Float, nullable=False)
    
    inventories = relationship("Inventory", back_populates="product", cascade="all, delete-orphan")