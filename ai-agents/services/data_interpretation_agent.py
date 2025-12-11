import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from typing import Dict, Any, List
import structlog
from datetime import datetime, timedelta
import json

from .base_agent import BaseAgent
from models import Metric, Anomaly, LogEntry

logger = structlog.get_logger()

class DataInterpretationAgent(BaseAgent):
    """AI Agent for data interpretation and natural language queries"""
    
    def __init__(self):
        super().__init__("data_interpretation_agent", "data_interpretation")
        
    async def analyze(self, data: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """Analyze and interpret data"""
        try:
            query = data.get("query", "")
            analysis_type = data.get("analysis_type", "summary")
            
            # Extract relevant data
            metrics_data = await self._extract_metrics_data(data, db)
            anomalies_data = await self._extract_anomalies_data(data, db)
            logs_data = await self._extract_logs_data(data, db)
            
            # Perform analysis based on type
            if analysis_type == "summary":
                result = await self._generate_summary(metrics_data, anomalies_data, logs_data)
            elif analysis_type == "trends":
                result = await self._analyze_trends(metrics_data)
            elif analysis_type == "correlations":
                result = await self._analyze_correlations(metrics_data)
            elif analysis_type == "patterns":
                result = await self._identify_patterns(metrics_data, anomalies_data)
            elif query:
                result = await self._process_natural_language_query(query, metrics_data, anomalies_data, logs_data)
            else:
                result = await self._generate_summary(metrics_data, anomalies_data, logs_data)
            
            # Generate insights
            insights = await self._generate_interpretation_insights(result, analysis_type)
            
            return {
                "analysis": result,
                "query": query,
                "analysis_type": analysis_type,
                "insights": insights,
                "metadata": {
                    "data_points": {
                        "metrics": len(metrics_data),
                        "anomalies": len(anomalies_data),
                        "logs": len(logs_data)
                    },
                    "analysis_timestamp": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            logger.error("Data interpretation failed", error=str(e))
            raise
    
    async def _extract_metrics_data(self, data: Dict[str, Any], db: Session) -> List[Dict[str, Any]]:
        """Extract metrics data"""
        if "metrics" in data:
            return data["metrics"]
        
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
        
        return [
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
    
    async def _extract_anomalies_data(self, data: Dict[str, Any], db: Session) -> List[Dict[str, Any]]:
        """Extract anomalies data"""
        if "anomalies" in data:
            return data["anomalies"]
        
        # Query recent anomalies from database
        time_range = data.get("time_range", "24h")
        if time_range == "24h":
            start_time = datetime.utcnow() - timedelta(hours=24)
        elif time_range == "7d":
            start_time = datetime.utcnow() - timedelta(days=7)
        else:
            start_time = datetime.utcnow() - timedelta(hours=24)
        
        db_anomalies = db.query(Anomaly).filter(
            Anomaly.detected_at >= start_time
        ).limit(500).all()
        
        return [
            {
                "id": a.id,
                "metric_id": a.metric_id,
                "severity": a.severity,
                "score": a.score,
                "description": a.description,
                "detected_at": a.detected_at,
                "resolved": a.resolved
            }
            for a in db_anomalies
        ]
    
    async def _extract_logs_data(self, data: Dict[str, Any], db: Session) -> List[Dict[str, Any]]:
        """Extract logs data"""
        if "logs" in data:
            return data["logs"]
        
        # Query recent logs from database
        time_range = data.get("time_range", "24h")
        if time_range == "24h":
            start_time = datetime.utcnow() - timedelta(hours=24)
        elif time_range == "7d":
            start_time = datetime.utcnow() - timedelta(days=7)
        else:
            start_time = datetime.utcnow() - timedelta(hours=24)
        
        db_logs = db.query(LogEntry).filter(
            LogEntry.timestamp >= start_time
        ).limit(1000).all()
        
        return [
            {
                "id": l.id,
                "level": l.level,
                "message": l.message,
                "source": l.source,
                "timestamp": l.timestamp
            }
            for l in db_logs
        ]
    
    async def _generate_summary(
        self, 
        metrics: List[Dict[str, Any]], 
        anomalies: List[Dict[str, Any]], 
        logs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate data summary"""
        summary = {
            "overview": {},
            "metrics_summary": {},
            "anomalies_summary": {},
            "logs_summary": {},
            "key_insights": []
        }
        
        # Metrics summary
        if metrics:
            df = pd.DataFrame(metrics)
            values = pd.to_numeric(df['value'], errors='coerce').dropna()
            
            summary["metrics_summary"] = {
                "total_metrics": len(metrics),
                "unique_sources": df['source'].nunique() if 'source' in df.columns else 0,
                "value_stats": {
                    "mean": float(values.mean()) if len(values) > 0 else 0,
                    "median": float(values.median()) if len(values) > 0 else 0,
                    "std": float(values.std()) if len(values) > 0 else 0,
                    "min": float(values.min()) if len(values) > 0 else 0,
                    "max": float(values.max()) if len(values) > 0 else 0
                },
                "time_range": {
                    "start": df['timestamp'].min().isoformat() if 'timestamp' in df.columns else None,
                    "end": df['timestamp'].max().isoformat() if 'timestamp' in df.columns else None
                }
            }
        
        # Anomalies summary
        if anomalies:
            severity_counts = {}
            for anomaly in anomalies:
                severity = anomaly['severity']
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            summary["anomalies_summary"] = {
                "total_anomalies": len(anomalies),
                "severity_breakdown": severity_counts,
                "unresolved": sum(1 for a in anomalies if not a.get('resolved', False)),
                "average_score": sum(a['score'] for a in anomalies) / len(anomalies)
            }
        
        # Logs summary
        if logs:
            level_counts = {}
            source_counts = {}
            
            for log in logs:
                level = log['level']
                source = log['source']
                level_counts[level] = level_counts.get(level, 0) + 1
                source_counts[source] = source_counts.get(source, 0) + 1
            
            summary["logs_summary"] = {
                "total_logs": len(logs),
                "level_breakdown": level_counts,
                "unique_sources": len(source_counts),
                "error_rate": (level_counts.get('ERROR', 0) + level_counts.get('FATAL', 0)) / len(logs) * 100
            }
        
        # Generate overview
        summary["overview"] = {
            "total_data_points": len(metrics) + len(anomalies) + len(logs),
            "data_health": "good" if len(anomalies) < 5 else "warning" if len(anomalies) < 20 else "critical",
            "analysis_period": "24 hours"
        }
        
        # Key insights
        summary["key_insights"] = await self._generate_key_insights(summary)
        
        return summary
    
    async def _analyze_trends(self, metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze trends in metrics data"""
        if not metrics:
            return {"trends": [], "summary": "No metrics data available for trend analysis"}
        
        df = pd.DataFrame(metrics)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['value'] = pd.to_numeric(df['value'], errors='coerce')
        df = df.dropna(subset=['value', 'timestamp'])
        
        trends = []
        
        # Analyze trends by metric name
        for metric_name in df['name'].unique():
            metric_data = df[df['name'] == metric_name].sort_values('timestamp')
            
            if len(metric_data) < 3:
                continue
            
            values = metric_data['value'].values
            
            # Simple linear trend analysis
            x = np.arange(len(values))
            trend_slope = np.polyfit(x, values, 1)[0]
            
            # Determine trend direction
            if abs(trend_slope) < 0.01:
                trend_direction = "stable"
            elif trend_slope > 0:
                trend_direction = "increasing"
            else:
                trend_direction = "decreasing"
            
            # Calculate trend strength
            correlation = np.corrcoef(x, values)[0, 1]
            trend_strength = abs(correlation)
            
            trends.append({
                "metric_name": metric_name,
                "direction": trend_direction,
                "slope": float(trend_slope),
                "strength": float(trend_strength),
                "data_points": len(values),
                "time_range": {
                    "start": metric_data['timestamp'].min().isoformat(),
                    "end": metric_data['timestamp'].max().isoformat()
                }
            })
        
        return {
            "trends": trends,
            "summary": f"Analyzed {len(trends)} metric trends",
            "analysis_metadata": {
                "total_metrics_analyzed": len(trends),
                "increasing_trends": len([t for t in trends if t['direction'] == 'increasing']),
                "decreasing_trends": len([t for t in trends if t['direction'] == 'decreasing']),
                "stable_trends": len([t for t in trends if t['direction'] == 'stable'])
            }
        }
    
    async def _analyze_correlations(self, metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze correlations between metrics"""
        if not metrics:
            return {"correlations": [], "summary": "No metrics data available for correlation analysis"}
        
        df = pd.DataFrame(metrics)
        df['value'] = pd.to_numeric(df['value'], errors='coerce')
        df = df.dropna(subset=['value'])
        
        # Pivot data to have metrics as columns
        pivot_df = df.pivot_table(
            index='timestamp', 
            columns='name', 
            values='value', 
            aggfunc='mean'
        ).fillna(method='ffill').fillna(method='bfill')
        
        if pivot_df.shape[1] < 2:
            return {"correlations": [], "summary": "Need at least 2 different metrics for correlation analysis"}
        
        # Calculate correlation matrix
        corr_matrix = pivot_df.corr()
        
        # Find strong correlations
        correlations = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i + 1, len(corr_matrix.columns)):
                metric1 = corr_matrix.columns[i]
                metric2 = corr_matrix.columns[j]
                correlation = corr_matrix.iloc[i, j]
                
                if abs(correlation) > 0.5:  # Strong correlation threshold
                    correlations.append({
                        "metric1": metric1,
                        "metric2": metric2,
                        "correlation": float(correlation),
                        "strength": "strong" if abs(correlation) > 0.8 else "moderate",
                        "direction": "positive" if correlation > 0 else "negative"
                    })
        
        # Sort by absolute correlation
        correlations.sort(key=lambda x: abs(x['correlation']), reverse=True)
        
        return {
            "correlations": correlations[:20],  # Top 20 correlations
            "summary": f"Found {len(correlations)} strong correlations between metrics",
            "analysis_metadata": {
                "metrics_analyzed": len(corr_matrix.columns),
                "data_points": len(pivot_df),
                "strong_correlations": len([c for c in correlations if c['strength'] == 'strong'])
            }
        }
    
    async def _identify_patterns(
        self, 
        metrics: List[Dict[str, Any]], 
        anomalies: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Identify patterns in data"""
        patterns = {
            "temporal_patterns": [],
            "anomaly_patterns": [],
            "metric_patterns": []
        }
        
        # Analyze temporal patterns
        if metrics:
            df = pd.DataFrame(metrics)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['hour'] = df['timestamp'].dt.hour
            df['day_of_week'] = df['timestamp'].dt.dayofweek
            
            # Hourly patterns
            hourly_counts = df['hour'].value_counts().sort_index()
            peak_hour = hourly_counts.idxmax()
            
            patterns["temporal_patterns"].append({
                "type": "hourly_activity",
                "description": f"Peak activity occurs at hour {peak_hour}",
                "peak_hour": int(peak_hour),
                "distribution": hourly_counts.to_dict()
            })
            
            # Daily patterns
            daily_counts = df['day_of_week'].value_counts().sort_index()
            peak_day = daily_counts.idxmax()
            
            patterns["temporal_patterns"].append({
                "type": "daily_activity",
                "description": f"Peak activity occurs on day {peak_day}",
                "peak_day": int(peak_day),
                "distribution": daily_counts.to_dict()
            })
        
        # Analyze anomaly patterns
        if anomalies:
            severity_patterns = {}
            for anomaly in anomalies:
                severity = anomaly['severity']
                severity_patterns[severity] = severity_patterns.get(severity, 0) + 1
            
            patterns["anomaly_patterns"].append({
                "type": "severity_distribution",
                "description": f"Anomaly severity distribution: {severity_patterns}",
                "distribution": severity_patterns
            })
        
        return {
            "patterns": patterns,
            "summary": f"Identified {len(patterns['temporal_patterns'])} temporal patterns and {len(patterns['anomaly_patterns'])} anomaly patterns"
        }
    
    async def _process_natural_language_query(
        self, 
        query: str, 
        metrics: List[Dict[str, Any]], 
        anomalies: List[Dict[str, Any]], 
        logs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Process natural language queries"""
        query_lower = query.lower()
        
        # Simple keyword-based query processing
        if "anomaly" in query_lower or "unusual" in query_lower:
            return await self._generate_summary(metrics, anomalies, logs)
        elif "trend" in query_lower or "direction" in query_lower:
            return await self._analyze_trends(metrics)
        elif "correlation" in query_lower or "relationship" in query_lower:
            return await self._analyze_correlations(metrics)
        elif "pattern" in query_lower:
            return await self._identify_patterns(metrics, anomalies)
        elif "error" in query_lower or "log" in query_lower:
            return await self._analyze_logs(logs)
        else:
            # Default to summary
            return await self._generate_summary(metrics, anomalies, logs)
    
    async def _analyze_logs(self, logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze log patterns"""
        if not logs:
            return {"log_analysis": {}, "summary": "No log data available"}
        
        level_counts = {}
        source_counts = {}
        error_messages = []
        
        for log in logs:
            level = log['level']
            source = log['source']
            message = log['message']
            
            level_counts[level] = level_counts.get(level, 0) + 1
            source_counts[source] = source_counts.get(source, 0) + 1
            
            if level in ['ERROR', 'FATAL']:
                error_messages.append(message)
        
        return {
            "log_analysis": {
                "level_distribution": level_counts,
                "source_distribution": source_counts,
                "error_rate": (level_counts.get('ERROR', 0) + level_counts.get('FATAL', 0)) / len(logs) * 100,
                "common_errors": error_messages[:10]  # Top 10 error messages
            },
            "summary": f"Analyzed {len(logs)} log entries"
        }
    
    async def _generate_key_insights(self, summary: Dict[str, Any]) -> List[str]:
        """Generate key insights from summary"""
        insights = []
        
        try:
            # Metrics insights
            metrics_summary = summary.get("metrics_summary", {})
            if metrics_summary:
                total_metrics = metrics_summary.get("total_metrics", 0)
                unique_sources = metrics_summary.get("unique_sources", 0)
                insights.append(f"Collected {total_metrics} metrics from {unique_sources} data sources")
            
            # Anomaly insights
            anomalies_summary = summary.get("anomalies_summary", {})
            if anomalies_summary:
                total_anomalies = anomalies_summary.get("total_anomalies", 0)
                unresolved = anomalies_summary.get("unresolved", 0)
                if total_anomalies > 0:
                    insights.append(f"Detected {total_anomalies} anomalies with {unresolved} unresolved issues")
            
            # Log insights
            logs_summary = summary.get("logs_summary", {})
            if logs_summary:
                total_logs = logs_summary.get("total_logs", 0)
                error_rate = logs_summary.get("error_rate", 0)
                insights.append(f"Processed {total_logs} log entries with {error_rate:.1f}% error rate")
            
            # Overall health
            overview = summary.get("overview", {})
            data_health = overview.get("data_health", "unknown")
            if data_health == "good":
                insights.append("Overall system health is good with minimal issues")
            elif data_health == "warning":
                insights.append("System shows warning signs that may require attention")
            elif data_health == "critical":
                insights.append("System health is critical - immediate attention required")
        
        except Exception as e:
            logger.error("Failed to generate key insights", error=str(e))
            insights.append("Unable to generate key insights due to analysis error")
        
        return insights
    
    async def _generate_interpretation_insights(self, result: Dict[str, Any], analysis_type: str) -> List[Dict[str, Any]]:
        """Generate insights from interpretation results"""
        insights = []
        
        try:
            if analysis_type == "summary":
                overview = result.get("overview", {})
                data_health = overview.get("data_health", "unknown")
                total_points = overview.get("total_data_points", 0)
                
                insights.append({
                    "type": "data_summary",
                    "title": "Data Interpretation Summary",
                    "description": f"Analyzed {total_points} data points with overall system health: {data_health}",
                    "confidence": 0.85,
                    "severity": "low" if data_health == "good" else "medium" if data_health == "warning" else "high",
                    "data_source": "data_interpretation",
                    "related_entities": {"data_points": total_points},
                    "metadata": {"health_status": data_health}
                })
            
            elif analysis_type == "trends":
                trends = result.get("trends", [])
                increasing = len([t for t in trends if t['direction'] == 'increasing'])
                decreasing = len([t for t in trends if t['direction'] == 'decreasing'])
                
                insights.append({
                    "type": "trend_analysis",
                    "title": "Metric Trends Analysis",
                    "description": f"Identified {increasing} increasing and {decreasing} decreasing trends across metrics",
                    "confidence": 0.8,
                    "severity": "medium",
                    "data_source": "trend_analysis",
                    "related_entities": {"trends_analyzed": len(trends)},
                    "metadata": {"increasing": increasing, "decreasing": decreasing}
                })
            
            elif analysis_type == "correlations":
                correlations = result.get("correlations", [])
                strong_correlations = len([c for c in correlations if c['strength'] == 'strong'])
                
                insights.append({
                    "type": "correlation_analysis",
                    "title": "Metric Correlations",
                    "description": f"Found {len(correlations)} significant correlations with {strong_correlations} strong relationships",
                    "confidence": 0.75,
                    "severity": "low",
                    "data_source": "correlation_analysis",
                    "related_entities": {"correlations": len(correlations)},
                    "metadata": {"strong_correlations": strong_correlations}
                })
        
        except Exception as e:
            logger.error("Failed to generate interpretation insights", error=str(e))
        
        return insights
