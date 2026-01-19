from datetime import datetime
from enum import Enum
from typing import Optional
from sqlalchemy import Column, String, DateTime, Enum as SQLEnum, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from src.core.database import Base

class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class MediaType(str, Enum):
    TEXT = "text"
    AUDIO = "audio"
    IMAGE = "image"
    VIDEO = "video"

class Tenant(Base):
    __tablename__ = "tenants"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    jobs = relationship("IngestionJob", back_populates="tenant")

class IngestionJob(Base):
    __tablename__ = "ingestion_jobs"
    
    id = Column(String, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False, index=True)
    status = Column(SQLEnum(JobStatus), default=JobStatus.PENDING)
    media_type = Column(SQLEnum(MediaType), nullable=False)
    
    file_path = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    
    error_message = Column(Text, nullable=True)
    metadata_json = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    tenant = relationship("Tenant", back_populates="jobs")
