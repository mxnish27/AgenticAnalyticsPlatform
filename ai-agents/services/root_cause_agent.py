import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from typing import Dict, Any, List
import structlog
from datetime import datetime, timedelta
from collections import defaultdict

from .base_agent import BaseAgent
from models import Metric, Anomaly, LogEntry, CICDPipeline

logger = structlog.get_logger()

class RootCauseAgent(BaseAgent):
    """AI Agent for root cause analysis of anomalies and issues"""
    
    def __init__(self):
        super().__init__("root_cause_agent", "root_cause_analysis")
        
    async def analyze(self, data: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """Analyze root causes for anomalies or issues"""
        try:
            anomaly_id = data.get("anomaly_id")
            symptoms = data.get("symptoms", [])
            time_range = data.get("time_range", "24h")
            related_data = data.get("related_data", {})
            
            # Extract relevant data
            if anomaly_id:
                # Analyze specific anomaly
                result = await self._analyze_specific_anomaly(anomaly_id, time_range, db)
            elif symptoms:
                # Analyze based on symptoms
                result = await self._analyze_symptoms(symptoms, time_range, db)
            else:
                # General analysis of recent issues
                result = await self._analyze_recent_issues(time_range, db)
            
            # Generate insights
            insights = await self._generate_root_cause_insights(result)
            
            return {
                "root_cause_analysis": result,
                "symptoms": symptoms,
                "time_range": time_range,
                "insights": insights,
                "recommendations": await self._generate_recommendations(result),
                "metadata": {
                    "analysis_timestamp": datetime.utcnow().isoformat(),
                    "confidence": result.get("confidence", 0.5)
                }
            }
            
        except Exception as e:
            logger.error("Root cause analysis failed", error=str(e))
            raise
    
    async def _analyze_specific_anomaly(self, anomaly_id: int, time_range: str, db: Session) -> Dict[str, Any]:
        """Analyze root cause for a specific anomaly"""
        # Get the anomaly
        anomaly = db.query(Anomaly).filter(Anomaly.id == anomaly_id).first()
        if not anomaly:
            return {"error": "Anomaly not found", "analysis": {}}
        
        # Get time window around the anomaly
        anomaly_time = anomaly.detected_at
        start_time = anomaly_time - timedelta(hours=6)
        end_time = anomaly_time + timedelta(hours=2)
        
        # Collect related data
        related_metrics = await self._get_related_metrics(anomaly.metric_id, start_time, end_time, db)
        related_logs = await self._get_related_logs(start_time, end_time, db)
        related_pipelines = await self._get_related_pipelines(start_time, end_time, db)
        
        # Analyze correlations
        correlations = await self._analyze_temporal_correlations(anomaly, related_metrics, related_logs, related_pipelines)
        
        # Identify potential causes
        potential_causes = await self._identify_potential_causes(correlations, anomaly)
        
        # Rank causes by likelihood
        ranked_causes = await self._rank_causes(potential_causes)
        
        return {
            "anomaly_id": anomaly_id,
            "anomaly_details": {
                "severity": anomaly.severity,
                "score": anomaly.score,
                "description": anomaly.description,
                "detected_at": anomaly.detected_at.isoformat()
            },
            "time_window": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat(),
                "anomaly_time": anomaly_time.isoformat()
            },
            "data_collected": {
                "metrics_count": len(related_metrics),
                "logs_count": len(related_logs),
                "pipelines_count": len(related_pipelines)
            },
            "correlations": correlations,
            "potential_causes": ranked_causes,
            "confidence": ranked_causes[0]["likelihood"] if ranked_causes else 0.0
        }
    
    async def _analyze_symptoms(self, symptoms: List[str], time_range: str, db: Session) -> Dict[str, Any]:
        """Analyze root cause based on symptoms"""
        # Parse time range
        if time_range == "24h":
            start_time = datetime.utcnow() - timedelta(hours=24)
        elif time_range == "7d":
            start_time = datetime.utcnow() - timedelta(days=7)
        else:
            start_time = datetime.utcnow() - timedelta(hours=24)
        end_time = datetime.utcnow()
        
        # Collect data based on symptoms
        relevant_data = await self._collect_data_by_symptoms(symptoms, start_time, end_time, db)
        
        # Analyze patterns in the data
        patterns = await self._analyze_symptom_patterns(symptoms, relevant_data)
        
        # Identify potential causes
        potential_causes = await self._identify_causes_from_patterns(patterns, symptoms)
        
        return {
            "symptoms": symptoms,
            "time_window": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat()
            },
            "relevant_data": relevant_data,
            "patterns": patterns,
            "potential_causes": potential_causes,
            "confidence": max([c["likelihood"] for c in potential_causes]) if potential_causes else 0.0
        }
    
    async def _analyze_recent_issues(self, time_range: str, db: Session) -> Dict[str, Any]:
        """Analyze root causes for recent issues"""
        # Parse time range
        if time_range == "24h":
            start_time = datetime.utcnow() - timedelta(hours=24)
        elif time_range == "7d":
            start_time = datetime.utcnow() - timedelta(days=7)
        else:
            start_time = datetime.utcnow() - timedelta(hours=24)
        end_time = datetime.utcnow()
        
        # Get recent anomalies and issues
        recent_anomalies = db.query(Anomaly).filter(
            Anomaly.detected_at >= start_time,
            Anomaly.detected_at <= end_time
        ).all()
        
        recent_errors = db.query(LogEntry).filter(
            LogEntry.timestamp >= start_time,
            LogEntry.timestamp <= end_time,
            LogEntry.level.in_(['ERROR', 'FATAL'])
        ).all()
        
        recent_failed_pipelines = db.query(CICDPipeline).filter(
            CICDPipeline.created_at >= start_time,
            CICDPipeline.created_at <= end_time,
            CICDPipeline.status == 'failed'
        ).all()
        
        # Group issues by time and source
        issue_clusters = await self._cluster_issues(recent_anomalies, recent_errors, recent_failed_pipelines)
        
        # Analyze each cluster
        cluster_analyses = []
        for cluster in issue_clusters:
            analysis = await self._analyze_issue_cluster(cluster, db)
            cluster_analyses.append(analysis)
        
        return {
            "time_window": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat()
            },
            "issues_summary": {
                "anomalies": len(recent_anomalies),
                "errors": len(recent_errors),
                "failed_pipelines": len(recent_failed_pipelines)
            },
            "issue_clusters": issue_clusters,
            "cluster_analyses": cluster_analyses,
            "confidence": 0.7  # General analysis has moderate confidence
        }
    
    async def _get_related_metrics(self, metric_id: int, start_time: datetime, end_time: datetime, db: Session) -> List[Dict[str, Any]]:
        """Get metrics related to the anomaly"""
        # Get the original metric
        original_metric = db.query(Metric).filter(Metric.id == metric_id).first()
        if not original_metric:
            return []
        
        # Get metrics from the same source and time window
        related_metrics = db.query(Metric).filter(
            Metric.source == original_metric.source,
            Metric.timestamp >= start_time,
            Metric.timestamp <= end_time
        ).all()
        
        return [
            {
                "id": m.id,
                "name": m.name,
                "value": m.value,
                "timestamp": m.timestamp,
                "source": m.source
            }
            for m in related_metrics
        ]
    
    async def _get_related_logs(self, start_time: datetime, end_time: datetime, db: Session) -> List[Dict[str, Any]]:
        """Get logs from the time window"""
        logs = db.query(LogEntry).filter(
            LogEntry.timestamp >= start_time,
            LogEntry.timestamp <= end_time
        ).order_by(LogEntry.timestamp.desc()).limit(500).all()
        
        return [
            {
                "id": l.id,
                "level": l.level,
                "message": l.message,
                "source": l.source,
                "timestamp": l.timestamp
            }
            for l in logs
        ]
    
    async def _get_related_pipelines(self, start_time: datetime, end_time: datetime, db: Session) -> List[Dict[str, Any]]:
        """Get CI/CD pipelines from the time window"""
        pipelines = db.query(CICDPipeline).filter(
            CICDPipeline.created_at >= start_time,
            CICDPipeline.created_at <= end_time
        ).all()
        
        return [
            {
                "id": p.id,
                "pipeline_name": p.pipeline_name,
                "status": p.status,
                "duration": p.duration,
                "start_time": p.start_time,
                "end_time": p.end_time,
                "commit_hash": p.commit_hash,
                "branch": p.branch
            }
            for p in pipelines
        ]
    
    async def _analyze_temporal_correlations(
        self, 
        anomaly: Anomaly, 
        metrics: List[Dict[str, Any]], 
        logs: List[Dict[str, Any]], 
        pipelines: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze temporal correlations around the anomaly"""
        anomaly_time = anomaly.detected_at
        correlations = {
            "metric_correlations": [],
            "log_correlations": [],
            "pipeline_correlations": []
        }
        
        # Analyze metric correlations
        for metric in metrics:
            time_diff = abs((metric['timestamp'] - anomaly_time).total_seconds())
            if time_diff < 3600:  # Within 1 hour
                # Simple correlation based on time proximity and value changes
                correlation_score = max(0, 1 - time_diff / 3600)
                correlations["metric_correlations"].append({
                    "metric_id": metric["id"],
                    "metric_name": metric["name"],
                    "time_difference": time_diff,
                    "correlation_score": correlation_score,
                    "value": metric["value"]
                })
        
        # Analyze log correlations
        for log in logs:
            time_diff = abs((log['timestamp'] - anomaly_time).total_seconds())
            if time_diff < 1800:  # Within 30 minutes
                # Higher correlation for error logs
                base_score = max(0, 1 - time_diff / 1800)
                if log['level'] in ['ERROR', 'FATAL']:
                    base_score *= 1.5
                
                correlations["log_correlations"].append({
                    "log_id": log["id"],
                    "level": log["level"],
                    "message": log["message"],
                    "source": log["source"],
                    "time_difference": time_diff,
                    "correlation_score": min(1.0, base_score)
                })
        
        # Analyze pipeline correlations
        for pipeline in pipelines:
            if pipeline['start_time']:
                time_diff = abs((pipeline['start_time'] - anomaly_time).total_seconds())
                if time_diff < 7200:  # Within 2 hours
                    # Higher correlation for failed pipelines
                    base_score = max(0, 1 - time_diff / 7200)
                    if pipeline['status'] == 'failed':
                        base_score *= 2.0
                    
                    correlations["pipeline_correlations"].append({
                        "pipeline_id": pipeline["id"],
                        "pipeline_name": pipeline["pipeline_name"],
                        "status": pipeline["status"],
                        "time_difference": time_diff,
                        "correlation_score": min(1.0, base_score)
                    })
        
        # Sort correlations by score
        for key in correlations:
            correlations[key].sort(key=lambda x: x['correlation_score'], reverse=True)
        
        return correlations
    
    async def _identify_potential_causes(self, correlations: Dict[str, Any], anomaly: Anomaly) -> List[Dict[str, Any]]:
        """Identify potential causes based on correlations"""
        causes = []
        
        # Analyze metric correlations
        high_metric_correlations = [c for c in correlations["metric_correlations"] if c['correlation_score'] > 0.7]
        if high_metric_correlations:
            causes.append({
                "type": "metric_anomaly",
                "description": f"Related metric anomalies detected: {len(high_metric_correlations)} metrics showing unusual behavior",
                "evidence": high_metric_correlations[:3],
                "likelihood": 0.8
            })
        
        # Analyze log correlations
        high_log_correlations = [c for c in correlations["log_correlations"] if c['correlation_score'] > 0.6]
        error_logs = [c for c in high_log_correlations if c['level'] in ['ERROR', 'FATAL']]
        if error_logs:
            causes.append({
                "type": "application_errors",
                "description": f"Application errors detected: {len(error_logs)} error logs around the anomaly time",
                "evidence": error_logs[:3],
                "likelihood": 0.9
            })
        
        # Analyze pipeline correlations
        high_pipeline_correlations = [c for c in correlations["pipeline_correlations"] if c['correlation_score'] > 0.5]
        failed_pipelines = [c for c in high_pipeline_correlations if c['status'] == 'failed']
        if failed_pipelines:
            causes.append({
                "type": "deployment_issues",
                "description": f"Deployment issues detected: {len(failed_pipelines)} failed pipelines around the anomaly time",
                "evidence": failed_pipelines[:3],
                "likelihood": 0.85
            })
        
        # Add generic causes if no specific ones found
        if not causes:
            causes.append({
                "type": "unknown",
                "description": "No clear correlations found with other system events",
                "evidence": [],
                "likelihood": 0.3
            })
        
        return causes
    
    async def _rank_causes(self, causes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rank potential causes by likelihood"""
        return sorted(causes, key=lambda x: x['likelihood'], reverse=True)
    
    async def _collect_data_by_symptoms(self, symptoms: List[str], start_time: datetime, end_time: datetime, db: Session) -> Dict[str, Any]:
        """Collect relevant data based on symptoms"""
        data = {"metrics": [], "logs": [], "pipelines": []}
        
        # Parse symptoms to determine what data to collect
        symptom_lower = [s.lower() for s in symptoms]
        
        # Collect logs if symptoms mention errors or logs
        if any(symptom in symptom_lower for symptom in ["error", "log", "exception", "fail"]):
            logs = db.query(LogEntry).filter(
                LogEntry.timestamp >= start_time,
                LogEntry.timestamp <= end_time,
                LogEntry.level.in_(['ERROR', 'FATAL'])
            ).limit(200).all()
            
            data["logs"] = [
                {
                    "id": l.id,
                    "level": l.level,
                    "message": l.message,
                    "source": l.source,
                    "timestamp": l.timestamp
                }
                for l in logs
            ]
        
        # Collect metrics if symptoms mention performance or metrics
        if any(symptom in symptom_lower for symptom in ["performance", "metric", "slow", "cpu", "memory"]):
            metrics = db.query(Metric).filter(
                Metric.timestamp >= start_time,
                Metric.timestamp <= end_time
            ).limit(500).all()
            
            data["metrics"] = [
                {
                    "id": m.id,
                    "name": m.name,
                    "value": m.value,
                    "timestamp": m.timestamp,
                    "source": m.source
                }
                for m in metrics
            ]
        
        # Collect pipeline data if symptoms mention deployment or CI/CD
        if any(symptom in symptom_lower for symptom in ["deploy", "pipeline", "build", "cicd"]):
            pipelines = db.query(CICDPipeline).filter(
                CICDPipeline.created_at >= start_time,
                CICDPipeline.created_at <= end_time
            ).all()
            
            data["pipelines"] = [
                {
                    "id": p.id,
                    "pipeline_name": p.pipeline_name,
                    "status": p.status,
                    "duration": p.duration,
                    "start_time": p.start_time,
                    "end_time": p.end_time
                }
                for p in pipelines
            ]
        
        return data
    
    async def _analyze_symptom_patterns(self, symptoms: List[str], data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze patterns in the collected data"""
        patterns = []
        
        # Analyze log patterns
        if data["logs"]:
            error_sources = defaultdict(int)
            for log in data["logs"]:
                error_sources[log["source"]] += 1
            
            if error_sources:
                patterns.append({
                    "type": "error_concentration",
                    "description": f"Errors concentrated in sources: {dict(error_sources)}",
                    "data": error_sources
                })
        
        # Analyze metric patterns
        if data["metrics"]:
            # Group metrics by name and analyze trends
            metric_groups = defaultdict(list)
            for metric in data["metrics"]:
                metric_groups[metric["name"]].append(metric)
            
            for name, metrics_list in metric_groups.items():
                if len(metrics_list) > 5:
                    values = [m["value"] for m in metrics_list]
                    std_dev = np.std(values)
                    if std_dev > np.mean(values) * 0.5:  # High variability
                        patterns.append({
                            "type": "metric_volatility",
                            "description": f"High volatility detected in {name} metric",
                            "data": {"metric": name, "std_dev": std_dev, "mean": np.mean(values)}
                        })
        
        return patterns
    
    async def _identify_causes_from_patterns(self, patterns: List[Dict[str, Any]], symptoms: List[str]) -> List[Dict[str, Any]]:
        """Identify causes from analyzed patterns"""
        causes = []
        
        for pattern in patterns:
            if pattern["type"] == "error_concentration":
                causes.append({
                    "type": "service_failure",
                    "description": "Service or component failure detected",
                    "evidence": pattern["data"],
                    "likelihood": 0.8
                })
            elif pattern["type"] == "metric_volatility":
                causes.append({
                    "type": "resource_instability",
                    "description": "Resource instability or performance issues",
                    "evidence": pattern["data"],
                    "likelihood": 0.7
                })
        
        return causes
    
    async def _cluster_issues(self, anomalies: List, errors: List, pipelines: List) -> List[Dict[str, Any]]:
        """Cluster related issues by time and source"""
        clusters = []
        
        # Simple time-based clustering (within 1 hour windows)
        all_issues = []
        
        for anomaly in anomalies:
            all_issues.append({
                "type": "anomaly",
                "timestamp": anomaly.detected_at,
                "severity": anomaly.severity,
                "data": anomaly
            })
        
        for error in errors:
            all_issues.append({
                "type": "error",
                "timestamp": error.timestamp,
                "severity": "high" if error.level == "FATAL" else "medium",
                "data": error
            })
        
        for pipeline in pipelines:
            all_issues.append({
                "type": "pipeline_failure",
                "timestamp": pipeline.created_at,
                "severity": "high",
                "data": pipeline
            })
        
        # Sort by timestamp
        all_issues.sort(key=lambda x: x['timestamp'])
        
        # Cluster by time proximity
        if all_issues:
            current_cluster = [all_issues[0]]
            cluster_start = all_issues[0]['timestamp']
            
            for issue in all_issues[1:]:
                time_diff = (issue['timestamp'] - cluster_start).total_seconds()
                if time_diff < 3600:  # Within 1 hour
                    current_cluster.append(issue)
                else:
                    if len(current_cluster) > 1:
                        clusters.append({
                            "issues": current_cluster,
                            "time_window": {
                                "start": cluster_start.isoformat(),
                                "end": current_cluster[-1]['timestamp'].isoformat()
                            },
                            "issue_count": len(current_cluster)
                        })
                    current_cluster = [issue]
                    cluster_start = issue['timestamp']
            
            # Add the last cluster
            if len(current_cluster) > 1:
                clusters.append({
                    "issues": current_cluster,
                    "time_window": {
                        "start": cluster_start.isoformat(),
                        "end": current_cluster[-1]['timestamp'].isoformat()
                    },
                    "issue_count": len(current_cluster)
                })
        
        return clusters
    
    async def _analyze_issue_cluster(self, cluster: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """Analyze a specific cluster of issues"""
        issues = cluster["issues"]
        
        # Count by type
        type_counts = defaultdict(int)
        severity_counts = defaultdict(int)
        
        for issue in issues:
            type_counts[issue["type"]] += 1
            severity_counts[issue["severity"]] += 1
        
        # Identify dominant patterns
        dominant_type = max(type_counts, key=type_counts.get)
        dominant_severity = max(severity_counts, key=severity_counts.get)
        
        return {
            "cluster_summary": {
                "total_issues": len(issues),
                "dominant_type": dominant_type,
                "dominant_severity": dominant_severity,
                "type_breakdown": dict(type_counts),
                "severity_breakdown": dict(severity_counts)
            },
            "likely_cause": f"Cluster of {dominant_type} issues with {dominant_severity} severity",
            "confidence": 0.75
        }
    
    async def _generate_root_cause_insights(self, result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate insights from root cause analysis"""
        insights = []
        
        try:
            if "potential_causes" in result:
                causes = result["potential_causes"]
                if causes:
                    top_cause = causes[0]
                    insights.append({
                        "type": "root_cause",
                        "title": "Primary Root Cause Identified",
                        "description": f"Most likely cause: {top_cause['description']}",
                        "confidence": top_cause["likelihood"],
                        "severity": "high" if top_cause["likelihood"] > 0.8 else "medium",
                        "data_source": "root_cause_analysis",
                        "related_entities": {"cause_type": top_cause["type"]},
                        "metadata": {"evidence_count": len(top_cause.get("evidence", []))}
                    })
            
            if "confidence" in result:
                confidence = result["confidence"]
                if confidence > 0.8:
                    insights.append({
                        "type": "analysis_confidence",
                        "title": "High Confidence Analysis",
                        "description": f"Root cause analysis completed with {confidence:.1%} confidence",
                        "confidence": confidence,
                        "severity": "low",
                        "data_source": "root_cause_analysis",
                        "related_entities": {"confidence_level": confidence}
                    })
                elif confidence < 0.5:
                    insights.append({
                        "type": "analysis_confidence",
                        "title": "Low Confidence Analysis",
                        "description": f"Root cause analysis has low confidence ({confidence:.1%}). Additional data may be needed.",
                        "confidence": confidence,
                        "severity": "medium",
                        "data_source": "root_cause_analysis",
                        "related_entities": {"confidence_level": confidence}
                    })
        
        except Exception as e:
            logger.error("Failed to generate root cause insights", error=str(e))
        
        return insights
    
    async def _generate_recommendations(self, result: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on root cause analysis"""
        recommendations = []
        
        try:
            if "potential_causes" in result:
                causes = result["potential_causes"]
                
                for cause in causes[:3]:  # Top 3 causes
                    if cause["type"] == "application_errors":
                        recommendations.append("Review application logs and fix reported errors")
                    elif cause["type"] == "deployment_issues":
                        recommendations.append("Investigate recent deployment changes and consider rollback if necessary")
                    elif cause["type"] == "metric_anomaly":
                        recommendations.append("Monitor system resources and investigate performance bottlenecks")
                    elif cause["type"] == "service_failure":
                        recommendations.append("Check service health and restart affected components")
                    elif cause["type"] == "resource_instability":
                        recommendations.append("Scale resources or optimize resource usage")
            
            # Add general recommendations
            recommendations.extend([
                "Implement automated monitoring to prevent similar issues",
                "Document incident response procedures for future reference"
            ])
        
        except Exception as e:
            logger.error("Failed to generate recommendations", error=str(e))
            recommendations.append("Review system logs and metrics for detailed investigation")
        
        return recommendations[:5]  # Limit to top 5 recommendations
