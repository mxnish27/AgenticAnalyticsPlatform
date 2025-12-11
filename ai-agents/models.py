from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class AgentExecution(Base):
    __tablename__ = "agent_executions"
    
    id = Column(Integer, primary_key=True, index=True)
    agent_name = Column(String, index=True)
    agent_type = Column(String, index=True)
    input_data = Column(JSON)
    output_data = Column(JSON)
    execution_time = Column(Float)  # in seconds
    status = Column(String, index=True)  # success, failed, timeout
    error_message = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    metadata = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AgentInsight(Base):
    __tablename__ = "agent_insights"
    
    id = Column(Integer, primary_key=True, index=True)
    agent_name = Column(String, index=True)
    insight_type = Column(String, index=True)  # anomaly, pattern, recommendation, etc.
    title = Column(String, index=True)
    description = Column(Text)
    confidence_score = Column(Float)
    severity = Column(String, index=True)  # low, medium, high, critical
    data_source = Column(String, index=True)
    related_entities = Column(JSON)  # IDs of related metrics, anomalies, etc.
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    metadata = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AgentModel(Base):
    __tablename__ = "agent_models"
    
    id = Column(Integer, primary_key=True, index=True)
    agent_name = Column(String, unique=True, index=True)
    model_type = Column(String, index=True)  # sklearn, tensorflow, pytorch, etc.
    model_version = Column(String, index=True)
    model_path = Column(String)
    model_config = Column(JSON)
    training_data_hash = Column(String)
    performance_metrics = Column(JSON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_used = Column(DateTime(timezone=True), nullable=True)

class AgentFeedback(Base):
    __tablename__ = "agent_feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    agent_execution_id = Column(Integer, ForeignKey("agent_executions.id"))
    user_id = Column(String, index=True)
    feedback_type = Column(String, index=True)  # positive, negative, neutral
    feedback_text = Column(Text)
    rating = Column(Integer)  # 1-5 stars
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    metadata = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
