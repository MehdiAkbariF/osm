# app/api/v2/models/product.py
from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship
from app.api.v2.models.base import Base, TimestampMixin

class Product(Base, TimestampMixin):
    __tablename__ = "products"
    
    id = Column(String(50), primary_key=True, index=True)  # شناسه متنی UUID یدکچی
    name = Column(String, nullable=False)                  # عنوان محصول (productTitle)
    description = Column(Text, nullable=True)
    
    inventories = relationship("Inventory", back_populates="product", cascade="all, delete-orphan")