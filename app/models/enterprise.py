from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship
from app.db.base import Base
import uuid

class Enterprise(Base):
    __tablename__ = "enterprises"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(200), nullable=False)
    type = Column(String(50), nullable=False)  # добыча/переработка
    region = Column(String(100))
    description = Column(Text)
    
    equipment = relationship("Equipment", back_populates="enterprise")
    orders = relationship("ProductionOrder", back_populates="enterprise")

