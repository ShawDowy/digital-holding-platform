from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime
import uuid

class Equipment(Base):
    __tablename__ = "equipment"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tag = Column(String(50), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    type = Column(String(100))
    status = Column(String(50), default="operational")  # operational, broken, maintenance
    last_maintenance = Column(DateTime, default=datetime.now)
    
    enterprise_id = Column(String, ForeignKey("enterprises.id"))
    enterprise = relationship("Enterprise", back_populates="equipment")

