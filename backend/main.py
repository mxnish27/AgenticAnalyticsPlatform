from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
import structlog
from typing import List, Optional
import uvicorn

from database import get_db, engine
from models import Base
from schemas import HealthResponse, MetricResponse, AnomalyResponse
from services.metrics_service import MetricsService
from services.anomaly_service import AnomalyService
from services.auth_service import AuthService
from config import settings

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Security
security = HTTPBearer()
auth_service = AuthService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Agentic Analytics Backend")
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown
    logger.info("Shutting down Agentic Analytics Backend")

# Create FastAPI app
app = FastAPI(
    title="Agentic Analytics Platform API",
    description="AI-driven analytics platform for enterprise data",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Services
metrics_service = MetricsService()
anomaly_service = AnomalyService()

# Dependency for authentication
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = auth_service.verify_token(credentials.credentials)
        return payload
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint"""
    return HealthResponse(
        status="healthy",
        service="agentic-analytics-backend",
        version="1.0.0"
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        service="agentic-analytics-backend",
        version="1.0.0"
    )

@app.post("/auth/login")
async def login():
    """Login endpoint - returns JWT token"""
    token = auth_service.create_access_token(data={"sub": "user"})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/metrics", response_model=List[MetricResponse])
async def get_metrics(
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    metric_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get metrics with optional filtering"""
    try:
        metrics = await metrics_service.get_metrics(
            db=db,
            start_time=start_time,
            end_time=end_time,
            metric_type=metric_type
        )
        return metrics
    except Exception as e:
        logger.error("Failed to fetch metrics", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch metrics")

@app.post("/metrics/ingest")
async def ingest_metrics(
    metric_data: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Ingest new metrics data"""
    try:
        result = await metrics_service.ingest_metrics(db=db, data=metric_data)
        return {"status": "success", "ingested_count": result}
    except Exception as e:
        logger.error("Failed to ingest metrics", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to ingest metrics")

@app.get("/anomalies", response_model=List[AnomalyResponse])
async def get_anomalies(
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    severity: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get detected anomalies"""
    try:
        anomalies = await anomaly_service.get_anomalies(
            db=db,
            start_time=start_time,
            end_time=end_time,
            severity=severity
        )
        return anomalies
    except Exception as e:
        logger.error("Failed to fetch anomalies", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch anomalies")

@app.post("/anomalies/detect")
async def detect_anomalies(
    metric_data: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Detect anomalies in provided data"""
    try:
        anomalies = await anomaly_service.detect_anomalies(db=db, data=metric_data)
        return {"anomalies": anomalies, "count": len(anomalies)}
    except Exception as e:
        logger.error("Failed to detect anomalies", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to detect anomalies")

@app.get("/analytics/summary")
async def get_analytics_summary(
    time_range: str = "24h",
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get analytics summary"""
    try:
        summary = await metrics_service.get_summary(db=db, time_range=time_range)
        return summary
    except Exception as e:
        logger.error("Failed to get analytics summary", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get analytics summary")

@app.post("/analytics/query")
async def query_analytics(
    query: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Execute natural language or structured query"""
    try:
        result = await metrics_service.execute_query(db=db, query=query)
        return result
    except Exception as e:
        logger.error("Failed to execute query", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to execute query")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
