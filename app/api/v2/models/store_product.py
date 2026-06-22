# app/api/v2/models/store_product.py
from sqlalchemy import Column, String
from app.api.v2.models.base import Base

class StoreProduct(Base):
    __tablename__ = "store_products"

    store_id = Column(String(50), primary_key=True)
    product_id = Column(String(50), primary_key=True) # 👈 تغییر به ساختار رشته‌ای جهت هماهنگی با شناسه یدکچی