import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
from sqlalchemy.orm import Session
from typing import Dict, Any, List
import structlog
from datetime import datetime, timedelta

from .base_agent import BaseAgent
from models import Metric, Anomaly

logger = structlog.get_logger()

class AnomalyAgent(BaseAgent):
    """AI Agent for anomaly detection in metrics and time series data"""
    
    def __init__(self):
        super().__init__("anomaly_detection_agent", "anomaly_detection")
        self.scaler = StandardScaler()
        self.isolation_forest = IsolationForest(
            contamination=0.1,
            random_state=42,
            n_estimators=100
        )
        self.dbscan = DBSCAN(eps=0.5, min_samples=5)
        
    async def analyze(self, data: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """Analyze data for anomalies"""
        try:
            # Extract metrics from request or database
            metrics = await self._extract_metrics(data, db)
            
            if not metrics:
                return {
                    "anomalies": [],
                    "summary": "No metrics data available for analysis",
                    "insights": []
                }
            
            # Convert to DataFrame for analysis
            df = self._metrics_to_dataframe(metrics)
            
            # Detect anomalies using multiple methods
            statistical_anomalies = await self._detect_statistical_anomalies(df)
            ml_anomalies = await self._detect_ml_anomalies(df)
            cluster_anomalies = await self._detect_cluster_anomalies(df)
            
            # Combine and rank anomalies
            all_anomalies = await self._combine_anomalies(
                statistical_anomalies, ml_anomalies, cluster_anomalies
            )
            
            # Generate insights
            insights = await self._generate_insights(all_anomalies, df)
            
            # Store anomalies in database if needed
            await self._store_anomalies(all_anomalies, db)
            
            return {
                "anomalies": all_anomalies,
                "summary": f"Detected {len(all_anomalies)} anomalies in {len(metrics)} metrics",
                "insights": insights,
                "statistics": {
                    "total_metrics": len(metrics),
                    "anomaly_count": len(all_anomalies),
                    "anomaly_rate": len(all_anomalies) / len(metrics) if metrics else 0,
                    "analysis_timestamp": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            logger.error("Anomaly detection failed", error=str(e))
            raise
    
    async def _extract_metrics(self, data: Dict[str, Any], db: Session) -> List[Dict[str, Any]]:
        """Extract metrics from request data or database"""
        metrics = []
        
        if "metrics" in data:
            metrics = data["metrics"]
        elif "metric_data" in data:
            metrics = data["metric_data"]
        else:
            # Query recent metrics from database
            time_range = data.get("time_range", "24h")
            if time_range == "24h":
                start_time = datetime.utcnow() - timedelta(hours=24)
            elif time_range == "7d":
                start_time = datetime.utcnow() - timedelta(days=7)
            else:
                start_time = datetime.utcnow() - timedelta(hours=24)
            
            db_metrics = db.query(Metric).filter(
                Metric.timestamp >= start_time
            ).limit(1000).all()
            
            metrics = [
                {
                    "id": m.id,
                    "name": m.name,
                    "value": m.value,
                    "timestamp": m.timestamp,
                    "source": m.source,
                    "tags": m.tags or {}
                }
                for m in db_metrics
            ]
        
        return metrics
    
    def _metrics_to_dataframe(self, metrics: List[Dict[str, Any]]) -> pd.DataFrame:
        """Convert metrics list to DataFrame"""
        if not metrics:
            return pd.DataFrame()
        
        df = pd.DataFrame(metrics)
        
        # Ensure we have numeric values
        df['value'] = pd.to_numeric(df['value'], errors='coerce')
        df = df.dropna(subset=['value'])
        
        # Convert timestamp to datetime if it's not already
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        return df
    
    async def _detect_statistical_anomalies(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect anomalies using statistical methods"""
        anomalies = []
        
        if df.empty or len(df) < 10:
            return anomalies
        
        try:
            # Group by metric name for individual analysis
            for metric_name in df['name'].unique():
                metric_data = df[df['name'] == metric_name]
                values = metric_data['value']
                
                if len(values) < 5:
                    continue
                
                # Z-score method
                mean = values.mean()
                std = values.std()
                
                if std > 0:
                    z_scores = np.abs((values - mean) / std)
                    threshold = 3.0
                    
                    for idx, (index, row) in enumerate(metric_data.iterrows()):
                        if z_scores.iloc[idx] > threshold:
                            anomalies.append({
                                "metric_id": row.get('id'),
                                "metric_name": metric_name,
                                "value": float(row['value']),
                                "timestamp": row['timestamp'].isoformat() if pd.notna(row['timestamp']) else None,
                                "method": "statistical",
                                "score": float(z_scores.iloc[idx]),
                                "severity": "high" if z_scores.iloc[idx] > 4 else "medium",
                                "description": f"Statistical anomaly: Z-score {z_scores.iloc[idx]:.2f}",
                                "confidence": min(0.9, z_scores.iloc[idx] / 5.0)
                            })
        
        except Exception as e:
            logger.error("Statistical anomaly detection failed", error=str(e))
        
        return anomalies
    
    async def _detect_ml_anomalies(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect anomalies using machine learning"""
        anomalies = []
        
        if df.empty or len(df) < 20:
            return anomalies
        
        try:
            # Prepare features
            features = []
            for _, row in df.iterrows():
                feature_vector = [row['value']]
                
                # Add time-based features
                if pd.notna(row['timestamp']):
                    timestamp = pd.to_datetime(row['timestamp'])
                    feature_vector.extend([
                        timestamp.hour,
                        timestamp.dayofweek,
                        timestamp.day
                    ])
                else:
                    feature_vector.extend([0, 0, 0])
                
                # Add encoded categorical features
                if 'source' in row:
                    feature_vector.append(hash(row['source']) % 1000)
                else:
                    feature_vector.append(0)
                
                features.append(feature_vector)
            
            if not features:
                return anomalies
            
            # Scale features
            features_scaled = self.scaler.fit_transform(features)
            
            # Isolation Forest
            anomaly_labels = self.isolation_forest.fit_predict(features_scaled)
            anomaly_scores = self.isolation_forest.decision_function(features_scaled)
            
            for idx, (index, row) in enumerate(df.iterrows()):
                if anomaly_labels[idx] == -1:  # Anomaly
                    score = abs(anomaly_scores[idx])
                    severity = "medium"
                    if score > 0.5:
                        severity = "high"
                    if score > 0.8:
                        severity = "critical"
                    
                    anomalies.append({
                        "metric_id": row.get('id'),
                        "metric_name": row.get('name', 'unknown'),
                        "value": float(row['value']),
                        "timestamp": row['timestamp'].isoformat() if pd.notna(row['timestamp']) else None,
                        "method": "isolation_forest",
                        "score": float(score),
                        "severity": severity,
                        "description": f"ML anomaly detected: Isolation Forest score {score:.3f}",
                        "confidence": min(0.95, score + 0.5)
                    })
        
        except Exception as e:
            logger.error("ML anomaly detection failed", error=str(e))
        
        return anomalies
    
    async def _detect_cluster_anomalies(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect anomalies using clustering"""
        anomalies = []
        
        if df.empty or len(df) < 30:
            return anomalies
        
        try:
            # Prepare features for clustering
            features = df[['value']].values.reshape(-1, 1)
            
            # DBSCAN clustering
            cluster_labels = self.dbscan.fit_predict(features)
            
            # Points with label -1 are considered noise/anomalies
            for idx, (index, row) in enumerate(df.iterrows()):
                if cluster_labels[idx] == -1:
                    anomalies.append({
                        "metric_id": row.get('id'),
                        "metric_name": row.get('name', 'unknown'),
                        "value": float(row['value']),
                        "timestamp": row['timestamp'].isoformat() if pd.notna(row['timestamp']) else None,
                        "method": "clustering",
                        "score": 0.7,  # Fixed score for clustering anomalies
                        "severity": "medium",
                        "description": "Cluster-based anomaly: outlier detected",
                        "confidence": 0.7
                    })
        
        except Exception as e:
            logger.error("Cluster anomaly detection failed", error=str(e))
        
        return anomalies
    
    async def _combine_anomalies(
        self, 
        statistical: List[Dict[str, Any]], 
        ml: List[Dict[str, Any]], 
        cluster: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Combine anomalies from different methods and rank them"""
        all_anomalies = statistical + ml + cluster
        
        # Group by metric_id to avoid duplicates
        anomaly_groups = {}
        for anomaly in all_anomalies:
            key = f"{anomaly.get('metric_id', 0)}_{anomaly.get('timestamp', '')}"
            if key not in anomaly_groups:
                anomaly_groups[key] = []
            anomaly_groups[key].append(anomaly)
        
        # Combine and rank
        combined_anomalies = []
        for key, group in anomaly_groups.items():
            if len(group) == 1:
                combined_anomalies.append(group[0])
            else:
                # Multiple methods detected the same anomaly
                max_score = max(a['score'] for a in group)
                max_severity = max(a['severity'] for a in group, key=lambda x: {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}[x])
                methods = [a['method'] for a in group]
                
                combined_anomalies.append({
                    "metric_id": group[0]['metric_id'],
                    "metric_name": group[0]['metric_name'],
                    "value": group[0]['value'],
                    "timestamp": group[0]['timestamp'],
                    "method": f"multiple({', '.join(methods)})",
                    "score": max_score,
                    "severity": max_severity,
                    "description": f"Anomaly detected by {len(group)} methods: {', '.join(methods)}",
                    "confidence": min(0.95, sum(a['confidence'] for a in group) / len(group) + 0.1)
                })
        
        # Sort by score (descending)
        combined_anomalies.sort(key=lambda x: x['score'], reverse=True)
        
        return combined_anomalies[:50]  # Limit to top 50 anomalies
    
    async def _generate_insights(self, anomalies: List[Dict[str, Any]], df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Generate insights from detected anomalies"""
        insights = []
        
        if not anomalies:
            return insights
        
        try:
            # Analyze anomaly patterns
            severity_counts = {}
            method_counts = {}
            source_counts = {}
            
            for anomaly in anomalies:
                severity = anomaly['severity']
                method = anomaly['method']
                
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
                method_counts[method] = method_counts.get(method, 0) + 1
            
            # Generate summary insight
            insights.append({
                "type": "anomaly_summary",
                "title": "Anomaly Detection Summary",
                "description": f"Detected {len(anomalies)} anomalies across multiple metrics. "
                             f"Severity distribution: {severity_counts}. "
                             f"Detection methods: {method_counts}.",
                "confidence": 0.9,
                "severity": "high" if anomalies else "low",
                "data_source": "anomaly_detection",
                "related_entities": {"anomaly_count": len(anomalies)},
                "metadata": {
                    "severity_breakdown": severity_counts,
                    "method_breakdown": method_counts,
                    "total_anomalies": len(anomalies)
                }
            })
            
            # Generate severity-specific insights
            if severity_counts.get('critical', 0) > 0:
                insights.append({
                    "type": "critical_anomalies",
                    "title": "Critical Anomalies Detected",
                    "description": f"{severity_counts['critical']} critical anomalies require immediate attention",
                    "confidence": 0.95,
                    "severity": "critical",
                    "data_source": "anomaly_detection",
                    "related_entities": {"critical_anomalies": severity_counts['critical']},
                    "metadata": {"critical_count": severity_counts['critical']}
                })
        
        except Exception as e:
            logger.error("Failed to generate insights", error=str(e))
        
        return insights
    
    async def _store_anomalies(self, anomalies: List[Dict[str, Any]], db: Session) -> None:
        """Store detected anomalies in database"""
        try:
            for anomaly_data in anomalies:
                # Check if anomaly already exists
                existing = db.query(Anomaly).filter(
                    Anomaly.metric_id == anomaly_data.get('metric_id'),
                    Anomaly.detected_at >= datetime.utcnow() - timedelta(hours=1)
                ).first()
                
                if not existing:
                    anomaly = Anomaly(
                        metric_id=anomaly_data.get('metric_id'),
                        severity=anomaly_data['severity'],
                        score=anomaly_data['score'],
                        description=anomaly_data['description'],
                        metadata={
                            "method": anomaly_data['method'],
                            "confidence": anomaly_data['confidence'],
                            "value": anomaly_data['value']
                        }
                    )
                    db.add(anomaly)
            
            db.commit()
            logger.info("Anomalies stored in database", count=len(anomalies))
            
        except Exception as e:
            logger.error("Failed to store anomalies", error=str(e))
            db.rollback()
