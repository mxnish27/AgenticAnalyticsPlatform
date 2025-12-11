from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class AgentType(str, Enum):
    ANOMALY_DETECTION = "anomaly_detection"
    DATA_INTERPRETATION = "data_interpretation"
    ROOT_CAUSE_ANALYSIS = "root_cause_analysis"
    REPORT_GENERATION = "report_generation"

class ExecutionStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"

class InsightType(str, Enum):
    ANOMALY = "anomaly"
    PATTERN = "pattern"
    TREND = "trend"
    RECOMMENDATION = "recommendation"
    CORRELATION = "correlation"

class SeverityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

# Request/Response Models
class HealthResponse(BaseModel):
    status: str
    service: str
    version: str

class AgentRequest(BaseModel):
    agent_type: Optional[AgentType] = None
    data: Dict[str, Any]
    parameters: Optional[Dict[str, Any]] = None
    context: Optional[Dict[str, Any]] = None

class AgentResponse(BaseModel):
    success: bool
    result: Optional[Dict[str, Any]] = None
    message: str
    execution_time: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

class AgentExecutionBase(BaseModel):
    agent_name: str
    agent_type: str
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]] = None
    execution_time: Optional[float] = None
    status: ExecutionStatus
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class AgentExecutionCreate(AgentExecutionBase):
    pass

class AgentExecutionResponse(AgentExecutionBase):
    id: int
    timestamp: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True

class AgentInsightBase(BaseModel):
    agent_name: str
    insight_type: InsightType
    title: str
    description: str
    confidence_score: float
    severity: SeverityLevel
    data_source: str
    related_entities: Optional[Dict[str, Any]] = None
    expires_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

class AgentInsightCreate(AgentInsightBase):
    pass

class AgentInsightResponse(AgentInsightBase):
    id: int
    timestamp: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True

class AgentModelBase(BaseModel):
    agent_name: str
    model_type: str
    model_version: str
    model_path: str
    model_config: Dict[str, Any]
    training_data_hash: Optional[str] = None
    performance_metrics: Optional[Dict[str, Any]] = None
    is_active: bool = True

class AgentModelCreate(AgentModelBase):
    pass

class AgentModelResponse(AgentModelBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_used: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class AgentFeedbackBase(BaseModel):
    agent_execution_id: int
    user_id: str
    feedback_type: str
    feedback_text: Optional[str] = None
    rating: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None

class AgentFeedbackCreate(AgentFeedbackBase):
    pass

class AgentFeedbackResponse(AgentFeedbackBase):
    id: int
    timestamp: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True

class AnomalyDetectionRequest(BaseModel):
    metrics: List[Dict[str, Any]]
    time_range: Optional[str] = "24h"
    sensitivity: Optional[float] = 0.7
    lookback_window: Optional[int] = 100

class DataInterpretationRequest(BaseModel):
    data: Dict[str, Any]
    query: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    analysis_type: Optional[str] = "summary"

class RootCauseRequest(BaseModel):
    anomaly_id: Optional[int] = None
    symptoms: List[str] = []
    time_range: Optional[str] = "24h"
    related_data: Optional[Dict[str, Any]] = None

class ReportGenerationRequest(BaseModel):
    report_type: str
    time_range: str
    filters: Optional[Dict[str, Any]] = None
    format: Optional[str] = "json"
    include_recommendations: bool = True
