from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
import structlog
import time
from datetime import datetime

from models import AgentExecution, AgentInsight
from schemas import AgentExecutionCreate, AgentInsightCreate, ExecutionStatus

logger = structlog.get_logger()

class BaseAgent(ABC):
    """Base class for all AI agents"""
    
    def __init__(self, name: str, agent_type: str):
        self.name = name
        self.agent_type = agent_type
        self.logger = structlog.get_logger().bind(agent=name)
        
    @abstractmethod
    async def analyze(self, data: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """Analyze data and return insights"""
        pass
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "name": self.name,
            "type": self.agent_type,
            "status": "active",
            "last_execution": None,
        }
    
    async def execute_with_tracking(
        self, 
        data: Dict[str, Any], 
        db: Session,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute agent with execution tracking"""
        start_time = time.time()
        
        # Create execution record
        execution_data = AgentExecutionCreate(
            agent_name=self.name,
            agent_type=self.agent_type,
            input_data=data,
            status=ExecutionStatus.SUCCESS,
            metadata=parameters or {}
        )
        
        execution = AgentExecution(**execution_data.dict())
        db.add(execution)
        
        try:
            # Execute the analysis
            result = await self.analyze(data, db)
            
            # Update execution with results
            execution.output_data = result
            execution.execution_time = time.time() - start_time
            execution.status = ExecutionStatus.SUCCESS
            
            # Store insights if any
            if "insights" in result:
                await self._store_insights(result["insights"], db, execution.id)
            
            db.commit()
            
            self.logger.info(
                "Agent execution completed successfully",
                execution_time=execution.execution_time,
                execution_id=execution.id
            )
            
            return result
            
        except Exception as e:
            execution.execution_time = time.time() - start_time
            execution.status = ExecutionStatus.FAILED
            execution.error_message = str(e)
            db.commit()
            
            self.logger.error(
                "Agent execution failed",
                error=str(e),
                execution_time=execution.execution_time,
                execution_id=execution.id
            )
            
            raise
    
    async def _store_insights(
        self, 
        insights: Dict[str, Any], 
        db: Session, 
        execution_id: int
    ) -> None:
        """Store agent insights in database"""
        try:
            if isinstance(insights, list):
                insight_list = insights
            else:
                insight_list = [insights]
            
            for insight_data in insight_list:
                insight = AgentInsight(
                    agent_name=self.name,
                    insight_type=insight_data.get("type", "general"),
                    title=insight_data.get("title", "Insight"),
                    description=insight_data.get("description", ""),
                    confidence_score=insight_data.get("confidence", 0.5),
                    severity=insight_data.get("severity", "medium"),
                    data_source=insight_data.get("data_source", "unknown"),
                    related_entities=insight_data.get("related_entities", {}),
                    metadata=insight_data.get("metadata", {})
                )
                db.add(insight)
            
            db.commit()
            self.logger.info("Insights stored successfully", count=len(insight_list))
            
        except Exception as e:
            self.logger.error("Failed to store insights", error=str(e))
            # Don't raise here to avoid failing the main execution
    
    def validate_input(self, data: Dict[str, Any]) -> bool:
        """Validate input data"""
        if not isinstance(data, dict):
            return False
        return True
    
    def format_response(
        self, 
        result: Dict[str, Any], 
        execution_time: Optional[float] = None
    ) -> Dict[str, Any]:
        """Format agent response"""
        response = {
            "agent": self.name,
            "type": self.agent_type,
            "timestamp": datetime.utcnow().isoformat(),
            "result": result,
        }
        
        if execution_time:
            response["execution_time"] = execution_time
        
        return response
