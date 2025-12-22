from sqlalchemy import Column, String, Float, Integer
from app.db.base import Base
import uuid

class WarehouseItem(Base):
    __tablename__ = "warehouse_items"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    product_code = Column(String(50), unique=True, nullable=False)
    product_name = Column(String(200), nullable=False)
    quantity = Column(Float, default=0.0)
    unit = Column(String(20), default="т")
    price = Column(Float, default=0.0)  # New: Price per unit
    location = Column(String(100), default="Основной склад")
