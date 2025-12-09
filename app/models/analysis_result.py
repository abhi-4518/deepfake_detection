from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db import Base

class AnalysisResult(Base):
    """Model for storing deepfake detection results"""
    __tablename__ = "analysis_results"
    
    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=False, unique=True)
    
    # Verdict
    verdict = Column(String, nullable=False)  # 'real', 'ai_generated', or 'unknown'
    
    # Probabilities
    prob_ai = Column(Float, nullable=True)
    prob_real = Column(Float, nullable=True)
    confidence = Column(Float, nullable=True)
    
    # Model information
    source_model = Column(String, nullable=True)  # 'primary', 'fallback', 'primary (low confidence fallback)', 'none'
    
    # Detailed metrics (stored as JSON)
    # Example: {"texture": 0.85, "lighting": 0.92, "geometry": 0.78}
    feature_metrics = Column(JSON, nullable=True)
    
    # Full response data (for debugging/auditing)
    raw_response = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    analysis = relationship("Analysis", back_populates="result")
    
    def __repr__(self):
        return f"<AnalysisResult(id={self.id}, verdict={self.verdict}, confidence={self.confidence})>"
