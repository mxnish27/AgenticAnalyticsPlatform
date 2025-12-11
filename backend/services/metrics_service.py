from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
import structlog

from models import Metric, Anomaly, DataSource, CICDPipeline, TestResult
from schemas import MetricResponse, AnomalyResponse, AnalyticsSummary

logger = structlog.get_logger()

class MetricsService:
    def __init__(self):
        self.scaler = StandardScaler()
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)

    async def get_metrics(
        self,
        db: Session,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        metric_type: Optional[str] = None
    ) -> List[MetricResponse]:
        """Get metrics with optional filtering"""
        query = db.query(Metric)
        
        if start_time:
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            query = query.filter(Metric.timestamp >= start_dt)
        
        if end_time:
            end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            query = query.filter(Metric.timestamp <= end_dt)
        
        if metric_type:
            query = query.filter(Metric.name.like(f"%{metric_type}%"))
        
        metrics = query.order_by(desc(Metric.timestamp)).limit(1000).all()
        return [MetricResponse.from_orm(metric) for metric in metrics]

    async def ingest_metrics(self, db: Session, data: Dict[str, Any]) -> int:
        """Ingest new metrics data"""
        try:
            if isinstance(data, list):
                metrics_data = data
            else:
                metrics_data = [data]
            
            ingested_count = 0
            for metric_data in metrics_data:
                metric = Metric(
                    name=metric_data.get('name'),
                    value=metric_data.get('value'),
                    unit=metric_data.get('unit'),
                    source=metric_data.get('source'),
                    tags=metric_data.get('tags'),
                    metadata=metric_data.get('metadata')
                )
                db.add(metric)
                ingested_count += 1
            
            db.commit()
            logger.info("Successfully ingested metrics", count=ingested_count)
            return ingested_count
            
        except Exception as e:
            db.rollback()
            logger.error("Failed to ingest metrics", error=str(e))
            raise

    async def get_summary(self, db: Session, time_range: str = "24h") -> AnalyticsSummary:
        """Get analytics summary for a time range"""
        # Calculate time delta
        if time_range == "24h":
            delta = timedelta(hours=24)
        elif time_range == "7d":
            delta = timedelta(days=7)
        elif time_range == "30d":
            delta = timedelta(days=30)
        else:
            delta = timedelta(hours=24)
        
        start_time = datetime.utcnow() - delta
        
        # Get counts
        total_metrics = db.query(Metric).filter(Metric.timestamp >= start_time).count()
        total_anomalies = db.query(Anomaly).filter(Anomaly.detected_at >= start_time).count()
        active_data_sources = db.query(DataSource).filter(DataSource.enabled == True).count()
        recent_pipelines = db.query(CICDPipeline).filter(CICDPipeline.created_at >= start_time).count()
        
        # Calculate test pass rate
        total_tests = db.query(TestResult).filter(TestResult.timestamp >= start_time).count()
        passed_tests = db.query(TestResult).filter(
            and_(TestResult.timestamp >= start_time, TestResult.status == "passed")
        ).count()
        test_pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0.0
        
        return AnalyticsSummary(
            total_metrics=total_metrics,
            total_anomalies=total_anomalies,
            active_data_sources=active_data_sources,
            recent_pipelines=recent_pipelines,
            test_pass_rate=test_pass_rate,
            time_range=time_range,
            generated_at=datetime.utcnow()
        )

    async def execute_query(self, db: Session, query: Dict[str, Any]) -> Dict[str, Any]:
        """Execute natural language or structured query"""
        start_time = datetime.utcnow()
        
        try:
            query_type = query.get('type', 'metrics')
            time_range = query.get('time_range', '24h')
            filters = query.get('filters', {})
            
            # Calculate time range
            if time_range == "24h":
                delta = timedelta(hours=24)
            elif time_range == "7d":
                delta = timedelta(days=7)
            elif time_range == "30d":
                delta = timedelta(days=30)
            else:
                delta = timedelta(hours=24)
            
            start_dt = datetime.utcnow() - delta
            
            results = []
            
            if query_type == 'metrics':
                base_query = db.query(Metric).filter(Metric.timestamp >= start_dt)
                
                # Apply filters
                if 'source' in filters:
                    base_query = base_query.filter(Metric.source == filters['source'])
                if 'name' in filters:
                    base_query = base_query.filter(Metric.name.like(f"%{filters['name']}%"))
                
                metrics = base_query.order_by(desc(Metric.timestamp)).limit(100).all()
                results = [
                    {
                        'id': m.id,
                        'name': m.name,
                        'value': m.value,
                        'unit': m.unit,
                        'source': m.source,
                        'timestamp': m.timestamp.isoformat(),
                        'tags': m.tags
                    }
                    for m in metrics
                ]
            
            elif query_type == 'anomalies':
                base_query = db.query(Anomaly).filter(Anomaly.detected_at >= start_dt)
                
                if 'severity' in filters:
                    base_query = base_query.filter(Anomaly.severity == filters['severity'])
                
                anomalies = base_query.order_by(desc(Anomaly.detected_at)).limit(100).all()
                results = [
                    {
                        'id': a.id,
                        'metric_id': a.metric_id,
                        'severity': a.severity,
                        'score': a.score,
                        'description': a.description,
                        'detected_at': a.detected_at.isoformat(),
                        'resolved': a.resolved
                    }
                    for a in anomalies
                ]
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            return {
                'results': results,
                'metadata': {
                    'query_type': query_type,
                    'time_range': time_range,
                    'result_count': len(results),
                    'execution_time': execution_time
                },
                'execution_time': execution_time
            }
            
        except Exception as e:
            logger.error("Query execution failed", error=str(e))
            raise

    async def get_time_series_data(
        self,
        db: Session,
        metric_name: str,
        time_range: str = "24h",
        aggregation: str = "avg"
    ) -> List[Dict[str, Any]]:
        """Get time series data for a specific metric"""
        # Calculate time range
        if time_range == "24h":
            delta = timedelta(hours=24)
        elif time_range == "7d":
            delta = timedelta(days=7)
        elif time_range == "30d":
            delta = timedelta(days=30)
        else:
            delta = timedelta(hours=24)
        
        start_time = datetime.utcnow() - delta
        
        # Query metrics
        metrics = db.query(Metric).filter(
            and_(
                Metric.name == metric_name,
                Metric.timestamp >= start_time
            )
        ).order_by(Metric.timestamp).all()
        
        # Aggregate data by hour
        df = pd.DataFrame([
            {
                'timestamp': m.timestamp,
                'value': m.value
            }
            for m in metrics
        ])
        
        if df.empty:
            return []
        
        df.set_index('timestamp', inplace=True)
        
        if aggregation == "avg":
            aggregated = df.resample('1H').mean()
        elif aggregation == "sum":
            aggregated = df.resample('1H').sum()
        elif aggregation == "max":
            aggregated = df.resample('1H').max()
        elif aggregation == "min":
            aggregated = df.resample('1H').min()
        else:
            aggregated = df.resample('1H').mean()
        
        return [
            {
                'timestamp': timestamp.isoformat(),
                'value': float(value) if pd.notna(value) else None
            }
            for timestamp, value in aggregated.itertuples()
        ]
