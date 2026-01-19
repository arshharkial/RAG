from datetime import datetime
from sqlalchemy import Column, String, DateTime, JSON, Float, ForeignKey
from sqlalchemy.orm import relationship
from src.core.database import Base

class EvaluationReport(Base):
    __tablename__ = "evaluation_reports"

    id = Column(String, primary_key=True, index=True)
    tenant_id = Column(String, nullable=False, index=True)
    
    # Aggregate Scores
    avg_faithfulness = Column(Float, nullable=True)
    avg_answer_relevance = Column(Float, nullable=True)
    avg_context_precision = Column(Float, nullable=True)
    
    # Detailed Data
    report_json = Column(JSON, nullable=True)  # Full breakdown per query
    summary_md = Column(String, nullable=True)  # Generated markdown report
    
    created_at = Column(DateTime, default=datetime.utcnow)
