from sqlalchemy import Column, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime
import uuid

class SystemLog(Base):
    __tablename__ = "system_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp = Column(DateTime, default=datetime.now)
    
    # User who performed the action
    username = Column(String(100), nullable=True)
    role = Column(String(50), nullable=True)
    
    # Action details
    action = Column(String(100), nullable=False) # e.g. "CREATE_ORDER", "LOGIN"
    details = Column(Text, nullable=True)
    module = Column(String(50), default="SYSTEM") # e.g. "AUTH", "MES", "EAM"

