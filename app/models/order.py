from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime
import uuid

class ProductionOrder(Base):
    __tablename__ = "production_orders"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    order_number = Column(String(50), unique=True, nullable=False)
    product_code = Column(String(50), nullable=False)
    product_name = Column(String(200))
    quantity = Column(Float, nullable=False)
    
    # New: Estimated price per unit for finished product
    price_per_unit = Column(Float, default=0.0)
    
    due_date = Column(DateTime, nullable=True)
    problem_details = Column(Text, nullable=True)
    
    status = Column(String(50), default="new")
    created_date = Column(DateTime, default=datetime.now)
    
    enterprise_id = Column(String, ForeignKey("enterprises.id"))
    enterprise = relationship("Enterprise", back_populates="orders")
