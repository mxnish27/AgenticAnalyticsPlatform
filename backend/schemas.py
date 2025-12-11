from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class SeverityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"
    FATAL = "FATAL"

class PipelineStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    RUNNING = "running"
    PENDING = "pending"

class TestStatus(str, Enum):
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"

# Response Models
class HealthResponse(BaseModel):
    status: str
    service: str
    version: str

class MetricBase(BaseModel):
    name: str
    value: float
    unit: Optional[str] = None
    source: str
    tags: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

class MetricCreate(MetricBase):
    pass

class MetricResponse(MetricBase):
    id: int
    timestamp: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True

class AnomalyBase(BaseModel):
    severity: SeverityLevel
    score: float
    description: str
    metadata: Optional[Dict[str, Any]] = None

class AnomalyCreate(AnomalyBase):
    metric_id: int

class AnomalyResponse(AnomalyBase):
    id: int
    metric_id: int
    detected_at: datetime
    resolved: bool
    resolved_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class DataSourceBase(BaseModel):
    name: str
    type: str
    config: Dict[str, Any]
    enabled: bool = True

class DataSourceCreate(DataSourceBase):
    pass

class DataSourceResponse(DataSourceBase):
    id: int
    last_sync: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class LogEntryBase(BaseModel):
    level: LogLevel
    message: str
    source: str
    metadata: Optional[Dict[str, Any]] = None

class LogEntryCreate(LogEntryBase):
    pass

class LogEntryResponse(LogEntryBase):
    id: int
    timestamp: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True

class CICDPipelineBase(BaseModel):
    pipeline_name: str
    status: PipelineStatus
    duration: Optional[float] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    commit_hash: Optional[str] = None
    branch: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class CICDPipelineCreate(CICDPipelineBase):
    pass

class CICDPipelineResponse(CICDPipelineBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class TestResultBase(BaseModel):
    test_suite: str
    test_name: str
    status: TestStatus
    duration: Optional[float] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class TestResultCreate(TestResultBase):
    pass

class TestResultResponse(TestResultBase):
    id: int
    timestamp: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True

class AnalyticsReportBase(BaseModel):
    title: str
    report_type: str
    content: str
    time_range_start: datetime
    time_range_end: datetime
    metadata: Optional[Dict[str, Any]] = None

class AnalyticsReportCreate(AnalyticsReportBase):
    pass

class AnalyticsReportResponse(AnalyticsReportBase):
    id: int
    generated_at: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserBase(BaseModel):
    username: str
    email: str
    is_active: bool = True
    is_admin: bool = False

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class QueryRequest(BaseModel):
    query: str
    time_range: Optional[str] = "24h"
    filters: Optional[Dict[str, Any]] = None

class QueryResponse(BaseModel):
    results: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    execution_time: float

class AnalyticsSummary(BaseModel):
    total_metrics: int
    total_anomalies: int
    active_data_sources: int
    recent_pipelines: int
    test_pass_rate: float
    time_range: str
    generated_at: datetime
