from sqlalchemy import Column, Integer, ForeignKey
from app.api.v2.models.base import Base


class StoreProduct(Base):
    __tablename__ = "store_products"

    store_id = Column(Integer, primary_key=True)
    product_id = Column(Integer, primary_key=True)