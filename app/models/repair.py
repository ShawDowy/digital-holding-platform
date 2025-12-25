from sqlalchemy import Column, String, ForeignKey, DateTime, Text, Float
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime
import uuid

class RepairLog(Base):
    __tablename__ = "repair_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    equipment_id = Column(String, ForeignKey("equipment.id"))
    
    start_date = Column(DateTime, default=datetime.now)
    end_date = Column(DateTime, nullable=True)
    
    description = Column(String(200), nullable=False)
    performed_by = Column(String(100), nullable=True)
    cost = Column(Float, default=0.0)
    
    # Status: pending, in_progress, completed
    status = Column(String(50), default="pending") 
    
    equipment = relationship("Equipment", back_populates="repairs")

