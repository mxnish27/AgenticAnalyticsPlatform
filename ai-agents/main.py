from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
import structlog
from typing import List, Optional, Dict, Any
import uvicorn

from database import get_db, engine
from models import Base
from schemas import HealthResponse, AgentRequest, AgentResponse
from services.anomaly_agent import AnomalyAgent
from services.data_interpretation_agent import DataInterpretationAgent
from services.root_cause_agent import RootCauseAgent
from services.report_generation_agent import ReportGenerationAgent
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

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Agentic Analytics AI Service")
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown
    logger.info("Shutting down Agentic Analytics AI Service")

# Create FastAPI app
app = FastAPI(
    title="Agentic Analytics AI Service",
    description="AI agents for analytics and insights",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI agents
anomaly_agent = AnomalyAgent()
data_interpretation_agent = DataInterpretationAgent()
root_cause_agent = RootCauseAgent()
report_generation_agent = ReportGenerationAgent()

@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint"""
    return HealthResponse(
        status="healthy",
        service="agentic-analytics-ai",
        version="1.0.0"
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        service="agentic-analytics-ai",
        version="1.0.0"
    )

@app.post("/agents/anomaly-detect", response_model=AgentResponse)
async def detect_anomalies(
    request: AgentRequest,
    db: Session = Depends(get_db)
):
    """Detect anomalies using AI agent"""
    try:
        result = await anomaly_agent.analyze(request.data, db)
        return AgentResponse(
            success=True,
            result=result,
            message="Anomaly detection completed successfully"
        )
    except Exception as e:
        logger.error("Anomaly detection failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agents/interpret-data", response_model=AgentResponse)
async def interpret_data(
    request: AgentRequest,
    db: Session = Depends(get_db)
):
    """Interpret data using AI agent"""
    try:
        result = await data_interpretation_agent.analyze(request.data, db)
        return AgentResponse(
            success=True,
            result=result,
            message="Data interpretation completed successfully"
        )
    except Exception as e:
        logger.error("Data interpretation failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agents/root-cause", response_model=AgentResponse)
async def analyze_root_cause(
    request: AgentRequest,
    db: Session = Depends(get_db)
):
    """Analyze root cause using AI agent"""
    try:
        result = await root_cause_agent.analyze(request.data, db)
        return AgentResponse(
            success=True,
            result=result,
            message="Root cause analysis completed successfully"
        )
    except Exception as e:
        logger.error("Root cause analysis failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agents/generate-report", response_model=AgentResponse)
async def generate_report(
    request: AgentRequest,
    db: Session = Depends(get_db)
):
    """Generate report using AI agent"""
    try:
        result = await report_generation_agent.analyze(request.data, db)
        return AgentResponse(
            success=True,
            result=result,
            message="Report generation completed successfully"
        )
    except Exception as e:
        logger.error("Report generation failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agents/conversational-query", response_model=AgentResponse)
async def conversational_query(
    request: AgentRequest,
    db: Session = Depends(get_db)
):
    """Process conversational query using AI agents"""
    try:
        query = request.data.get("query", "")
        
        # Route to appropriate agent based on query content
        if "anomaly" in query.lower() or "unusual" in query.lower():
            result = await anomaly_agent.analyze(request.data, db)
        elif "interpret" in query.lower() or "explain" in query.lower():
            result = await data_interpretation_agent.analyze(request.data, db)
        elif "root cause" in query.lower() or "why" in query.lower():
            result = await root_cause_agent.analyze(request.data, db)
        elif "report" in query.lower() or "summary" in query.lower():
            result = await report_generation_agent.analyze(request.data, db)
        else:
            # Default to data interpretation
            result = await data_interpretation_agent.analyze(request.data, db)
        
        return AgentResponse(
            success=True,
            result=result,
            message="Query processed successfully"
        )
    except Exception as e:
        logger.error("Conversational query failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agents/status")
async def get_agents_status():
    """Get status of all AI agents"""
    return {
        "anomaly_agent": anomaly_agent.get_status(),
        "data_interpretation_agent": data_interpretation_agent.get_status(),
        "root_cause_agent": root_cause_agent.get_status(),
        "report_generation_agent": report_generation_agent.get_status(),
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
