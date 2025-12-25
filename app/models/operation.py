from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime
import uuid

class ProductionOperation(Base):
    __tablename__ = "production_operations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(200), nullable=False)
    order_id = Column(String, ForeignKey("production_orders.id"))
    
    # Status: pending, in_progress, completed, problem
    status = Column(String(50), default="pending") 
    
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    
    planned_quantity = Column(Float, default=0.0)
    actual_quantity = Column(Float, default=0.0)
    defect_quantity = Column(Float, default=0.0)
    
    order = relationship("ProductionOrder", back_populates="operations")
    defects = relationship("DefectLog", back_populates="operation", cascade="all, delete-orphan")

class DefectLog(Base):
    __tablename__ = "defect_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    operation_id = Column(String, ForeignKey("production_operations.id"))
    
    quantity = Column(Float, nullable=False)
    reason = Column(String(200), nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    
    operation = relationship("ProductionOperation", back_populates="defects")

