from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, LargeBinary, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.db import Base

class UploadMethod(enum.Enum):
    """Enum for different image upload methods"""
    FILE = "file"
    CAMERA = "camera"
    CLIPBOARD = "clipboard"

class Analysis(Base):
    """Model for storing user image analysis requests"""
    __tablename__ = "analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Image data (stored as binary)
    image_data = Column(LargeBinary, nullable=False)
    image_filename = Column(String, nullable=True)  # Original filename if available
    
    # Upload method
    upload_method = Column(Enum(UploadMethod), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="analyses")
    result = relationship("AnalysisResult", back_populates="analysis", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Analysis(id={self.id}, user_id={self.user_id}, method={self.upload_method.value})>"
