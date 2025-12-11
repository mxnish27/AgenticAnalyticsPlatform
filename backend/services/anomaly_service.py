from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
from sklearn.cluster import DBSCAN
import structlog

from models import Metric, Anomaly
from schemas import AnomalyResponse, AnomalyCreate

logger = structlog.get_logger()

class AnomalyService:
    def __init__(self):
        self.scaler = StandardScaler()
        self.isolation_forest = IsolationForest(contamination=0.1, random_state=42)
        self.dbscan = DBSCAN(eps=0.5, min_samples=5)

    async def get_anomalies(
        self,
        db: Session,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        severity: Optional[str] = None
    ) -> List[AnomalyResponse]:
        """Get detected anomalies with optional filtering"""
        query = db.query(Anomaly)
        
        if start_time:
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            query = query.filter(Anomaly.detected_at >= start_dt)
        
        if end_time:
            end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            query = query.filter(Anomaly.detected_at <= end_dt)
        
        if severity:
            query = query.filter(Anomaly.severity == severity)
        
        anomalies = query.order_by(desc(Anomaly.detected_at)).limit(500).all()
        return [AnomalyResponse.from_orm(anomaly) for anomaly in anomalies]

    async def detect_anomalies(self, db: Session, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect anomalies in provided data"""
        try:
            anomalies = []
            
            # Handle different data formats
            if 'metrics' in data:
                metrics_data = data['metrics']
            elif 'values' in data:
                metrics_data = data['values']
            else:
                metrics_data = [data]
            
            # Convert to DataFrame for analysis
            df = pd.DataFrame(metrics_data)
            
            if df.empty or 'value' not in df.columns:
                return []
            
            # Statistical anomaly detection
            statistical_anomalies = self._detect_statistical_anomalies(df)
            
            # Machine learning anomaly detection
            ml_anomalies = self._detect_ml_anomalies(df)
            
            # Combine results
            all_anomalies = statistical_anomalies + ml_anomalies
            
            # Store anomalies in database
            for anomaly_data in all_anomalies:
                anomaly = Anomaly(
                    metric_id=anomaly_data.get('metric_id'),
                    severity=anomaly_data.get('severity', 'medium'),
                    score=anomaly_data.get('score', 0.0),
                    description=anomaly_data.get('description', ''),
                    metadata=anomaly_data.get('metadata', {})
                )
                db.add(anomaly)
                anomalies.append(anomaly_data)
            
            db.commit()
            logger.info("Anomaly detection completed", count=len(anomalies))
            
            return anomalies
            
        except Exception as e:
            db.rollback()
            logger.error("Anomaly detection failed", error=str(e))
            raise

    def _detect_statistical_anomalies(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect anomalies using statistical methods"""
        anomalies = []
        
        try:
            values = df['value'].dropna()
            if len(values) < 10:  # Need minimum data points
                return anomalies
            
            # Z-score method
            mean = values.mean()
            std = values.std()
            
            if std > 0:
                z_scores = np.abs((values - mean) / std)
                anomaly_threshold = 3.0
                
                for idx, (index, row) in enumerate(df.iterrows()):
                    if pd.notna(row['value']):
                        z_score = z_scores.iloc[idx] if idx < len(z_scores) else 0
                        if z_score > anomaly_threshold:
                            severity = "high" if z_score > 4 else "medium"
                            if z_score > 5:
                                severity = "critical"
                            
                            anomalies.append({
                                'metric_id': row.get('id'),
                                'severity': severity,
                                'score': float(z_score),
                                'description': f"Statistical anomaly detected: Z-score {z_score:.2f}",
                                'method': 'statistical',
                                'metadata': {
                                    'z_score': float(z_score),
                                    'mean': float(mean),
                                    'std': float(std),
                                    'value': float(row['value'])
                                }
                            })
        
        except Exception as e:
            logger.error("Statistical anomaly detection failed", error=str(e))
        
        return anomalies

    def _detect_ml_anomalies(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect anomalies using machine learning"""
        anomalies = []
        
        try:
            values = df['value'].dropna().values.reshape(-1, 1)
            if len(values) < 20:  # Need minimum data points for ML
                return anomalies
            
            # Isolation Forest
            anomaly_labels = self.isolation_forest.fit_predict(values)
            anomaly_scores = self.isolation_forest.decision_function(values)
            
            for idx, (index, row) in enumerate(df.iterrows()):
                if pd.notna(row['value']) and idx < len(anomaly_labels):
                    if anomaly_labels[idx] == -1:  # Anomaly
                        score = abs(anomaly_scores[idx])
                        severity = "medium"
                        if score > 0.5:
                            severity = "high"
                        if score > 0.8:
                            severity = "critical"
                        
                        anomalies.append({
                            'metric_id': row.get('id'),
                            'severity': severity,
                            'score': float(score),
                            'description': f"ML anomaly detected: Isolation Forest score {score:.3f}",
                            'method': 'isolation_forest',
                            'metadata': {
                                'score': float(score),
                                'value': float(row['value']),
                                'algorithm': 'isolation_forest'
                            }
                        })
        
        except Exception as e:
            logger.error("ML anomaly detection failed", error=str(e))
        
        return anomalies

    async def get_anomaly_trends(
        self,
        db: Session,
        time_range: str = "7d"
    ) -> Dict[str, Any]:
        """Get anomaly trends over time"""
        try:
            # Calculate time range
            if time_range == "24h":
                delta = timedelta(hours=24)
            elif time_range == "7d":
                delta = timedelta(days=7)
            elif time_range == "30d":
                delta = timedelta(days=30)
            else:
                delta = timedelta(days=7)
            
            start_time = datetime.utcnow() - delta
            
            # Get anomalies grouped by day
            anomalies = db.query(Anomaly).filter(Anomaly.detected_at >= start_time).all()
            
            # Group by severity and date
            trends = {}
            for anomaly in anomalies:
                date_key = anomaly.detected_at.strftime('%Y-%m-%d')
                severity = anomaly.severity
                
                if date_key not in trends:
                    trends[date_key] = {
                        'total': 0,
                        'low': 0,
                        'medium': 0,
                        'high': 0,
                        'critical': 0
                    }
                
                trends[date_key]['total'] += 1
                trends[date_key][severity] += 1
            
            return {
                'trends': trends,
                'time_range': time_range,
                'total_anomalies': len(anomalies)
            }
            
        except Exception as e:
            logger.error("Failed to get anomaly trends", error=str(e))
            raise

    async def resolve_anomaly(self, db: Session, anomaly_id: int) -> bool:
        """Mark an anomaly as resolved"""
        try:
            anomaly = db.query(Anomaly).filter(Anomaly.id == anomaly_id).first()
            if anomaly:
                anomaly.resolved = True
                anomaly.resolved_at = datetime.utcnow()
                db.commit()
                logger.info("Anomaly resolved", anomaly_id=anomaly_id)
                return True
            return False
            
        except Exception as e:
            db.rollback()
            logger.error("Failed to resolve anomaly", error=str(e))
            raise
