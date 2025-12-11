import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from typing import Dict, Any, List
import structlog
from datetime import datetime, timedelta
import json
from jinja2 import Template

from .base_agent import BaseAgent
from models import Metric, Anomaly, LogEntry, CICDPipeline, TestResult, AnalyticsReport

logger = structlog.get_logger()

class ReportGenerationAgent(BaseAgent):
    """AI Agent for generating analytics reports"""
    
    def __init__(self):
        super().__init__("report_generation_agent", "report_generation")
        
    async def analyze(self, data: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """Generate analytics report"""
        try:
            report_type = data.get("report_type", "summary")
            time_range = data.get("time_range", "24h")
            filters = data.get("filters", {})
            format_type = data.get("format", "json")
            include_recommendations = data.get("include_recommendations", True)
            
            # Extract data for the report
            report_data = await self._extract_report_data(time_range, filters, db)
            
            # Generate report based on type
            if report_type == "summary":
                report_content = await self._generate_summary_report(report_data)
            elif report_type == "anomaly":
                report_content = await self._generate_anomaly_report(report_data)
            elif report_type == "performance":
                report_content = await self._generate_performance_report(report_data)
            elif report_type == "ci_cd":
                report_content = await self._generate_cicd_report(report_data)
            elif report_type == "testing":
                report_content = await self._generate_testing_report(report_data)
            else:
                report_content = await self._generate_summary_report(report_data)
            
            # Add recommendations if requested
            if include_recommendations:
                recommendations = await self._generate_recommendations(report_data, report_type)
                report_content["recommendations"] = recommendations
            
            # Format the report
            formatted_report = await self._format_report(report_content, format_type)
            
            # Store report in database
            report_record = await self._store_report(report_content, report_type, time_range, db)
            
            # Generate insights
            insights = await self._generate_report_insights(report_content, report_type)
            
            return {
                "report": formatted_report,
                "report_type": report_type,
                "time_range": time_range,
                "report_id": report_record.id if report_record else None,
                "insights": insights,
                "metadata": {
                    "generated_at": datetime.utcnow().isoformat(),
                    "data_points": {
                        "metrics": len(report_data.get("metrics", [])),
                        "anomalies": len(report_data.get("anomalies", [])),
                        "logs": len(report_data.get("logs", [])),
                        "pipelines": len(report_data.get("pipelines", [])),
                        "tests": len(report_data.get("tests", []))
                    }
                }
            }
            
        except Exception as e:
            logger.error("Report generation failed", error=str(e))
            raise
    
    async def _extract_report_data(self, time_range: str, filters: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """Extract data for report generation"""
        # Parse time range
        if time_range == "24h":
            start_time = datetime.utcnow() - timedelta(hours=24)
        elif time_range == "7d":
            start_time = datetime.utcnow() - timedelta(days=7)
        elif time_range == "30d":
            start_time = datetime.utcnow() - timedelta(days=30)
        else:
            start_time = datetime.utcnow() - timedelta(hours=24)
        end_time = datetime.utcnow()
        
        # Extract data
        metrics = db.query(Metric).filter(
            Metric.timestamp >= start_time,
            Metric.timestamp <= end_time
        ).all()
        
        anomalies = db.query(Anomaly).filter(
            Anomaly.detected_at >= start_time,
            Anomaly.detected_at <= end_time
        ).all()
        
        logs = db.query(LogEntry).filter(
            LogEntry.timestamp >= start_time,
            LogEntry.timestamp <= end_time
        ).all()
        
        pipelines = db.query(CICDPipeline).filter(
            CICDPipeline.created_at >= start_time,
            CICDPipeline.created_at <= end_time
        ).all()
        
        tests = db.query(TestResult).filter(
            TestResult.timestamp >= start_time,
            TestResult.timestamp <= end_time
        ).all()
        
        return {
            "time_range": {"start": start_time, "end": end_time},
            "metrics": [
                {
                    "id": m.id,
                    "name": m.name,
                    "value": m.value,
                    "unit": m.unit,
                    "source": m.source,
                    "timestamp": m.timestamp,
                    "tags": m.tags or {}
                }
                for m in metrics
            ],
            "anomalies": [
                {
                    "id": a.id,
                    "metric_id": a.metric_id,
                    "severity": a.severity,
                    "score": a.score,
                    "description": a.description,
                    "detected_at": a.detected_at,
                    "resolved": a.resolved
                }
                for a in anomalies
            ],
            "logs": [
                {
                    "id": l.id,
                    "level": l.level,
                    "message": l.message,
                    "source": l.source,
                    "timestamp": l.timestamp
                }
                for l in logs
            ],
            "pipelines": [
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
            ],
            "tests": [
                {
                    "id": t.id,
                    "test_suite": t.test_suite,
                    "test_name": t.test_name,
                    "status": t.status,
                    "duration": t.duration,
                    "error_message": t.error_message,
                    "timestamp": t.timestamp
                }
                for t in tests
            ]
        }
    
    async def _generate_summary_report(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary report"""
        metrics = data["metrics"]
        anomalies = data["anomalies"]
        logs = data["logs"]
        pipelines = data["pipelines"]
        tests = data["tests"]
        
        # Calculate summary statistics
        summary = {
            "executive_summary": "",
            "key_metrics": {},
            "anomalies_summary": {},
            "system_health": {},
            "recommendations": []
        }
        
        # Key metrics
        if metrics:
            df = pd.DataFrame(metrics)
            values = pd.to_numeric(df['value'], errors='coerce').dropna()
            
            summary["key_metrics"] = {
                "total_metrics": len(metrics),
                "unique_sources": df['source'].nunique() if 'source' in df.columns else 0,
                "average_value": float(values.mean()) if len(values) > 0 else 0,
                "value_range": {
                    "min": float(values.min()) if len(values) > 0 else 0,
                    "max": float(values.max()) if len(values) > 0 else 0
                }
            }
        
        # Anomalies summary
        if anomalies:
            severity_counts = {}
            unresolved_count = 0
            
            for anomaly in anomalies:
                severity = anomaly['severity']
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
                if not anomaly.get('resolved', False):
                    unresolved_count += 1
            
            summary["anomalies_summary"] = {
                "total_anomalies": len(anomalies),
                "severity_breakdown": severity_counts,
                "unresolved_anomalies": unresolved_count,
                "anomaly_rate": len(anomalies) / len(metrics) if metrics else 0
            }
        
        # System health
        if logs:
            level_counts = {}
            for log in logs:
                level = log['level']
                level_counts[level] = level_counts.get(level, 0) + 1
            
            error_rate = (level_counts.get('ERROR', 0) + level_counts.get('FATAL', 0)) / len(logs) * 100
            
            summary["system_health"] = {
                "total_logs": len(logs),
                "error_rate": error_rate,
                "health_status": "healthy" if error_rate < 5 else "warning" if error_rate < 15 else "critical",
                "level_breakdown": level_counts
            }
        
        # CI/CD summary
        if pipelines:
            status_counts = {}
            total_duration = 0
            
            for pipeline in pipelines:
                status = pipeline['status']
                status_counts[status] = status_counts.get(status, 0) + 1
                if pipeline['duration']:
                    total_duration += pipeline['duration']
            
            success_rate = status_counts.get('success', 0) / len(pipelines) * 100
            avg_duration = total_duration / len(pipelines) if pipelines else 0
            
            summary["ci_cd_summary"] = {
                "total_pipelines": len(pipelines),
                "success_rate": success_rate,
                "average_duration": avg_duration,
                "status_breakdown": status_counts
            }
        
        # Testing summary
        if tests:
            status_counts = {}
            total_duration = 0
            
            for test in tests:
                status = test['status']
                status_counts[status] = status_counts.get(status, 0) + 1
                if test['duration']:
                    total_duration += test['duration']
            
            pass_rate = status_counts.get('passed', 0) / len(tests) * 100
            avg_duration = total_duration / len(tests) if tests else 0
            
            summary["testing_summary"] = {
                "total_tests": len(tests),
                "pass_rate": pass_rate,
                "average_duration": avg_duration,
                "status_breakdown": status_counts
            }
        
        # Generate executive summary
        summary["executive_summary"] = await self._generate_executive_summary(summary)
        
        return summary
    
    async def _generate_anomaly_report(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate anomaly-focused report"""
        anomalies = data["anomalies"]
        metrics = data["metrics"]
        
        report = {
            "anomaly_overview": {},
            "severity_analysis": {},
            "temporal_analysis": {},
            "source_analysis": {},
            "recommendations": []
        }
        
        if anomalies:
            # Severity analysis
            severity_counts = {}
            severity_scores = {}
            
            for anomaly in anomalies:
                severity = anomaly['severity']
                score = anomaly['score']
                
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
                if severity not in severity_scores:
                    severity_scores[severity] = []
                severity_scores[severity].append(score)
            
            # Calculate average scores by severity
            severity_avg_scores = {}
            for severity, scores in severity_scores.items():
                severity_avg_scores[severity] = np.mean(scores)
            
            report["severity_analysis"] = {
                "total_anomalies": len(anomalies),
                "severity_counts": severity_counts,
                "average_scores": severity_avg_scores,
                "unresolved_count": sum(1 for a in anomalies if not a.get('resolved', False))
            }
            
            # Temporal analysis
            anomaly_times = [a['detected_at'] for a in anomalies]
            if anomaly_times:
                df = pd.DataFrame({'timestamp': anomaly_times})
                df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
                df['day'] = pd.to_datetime(df['timestamp']).dt.dayofweek
                
                hourly_distribution = df['hour'].value_counts().to_dict()
                daily_distribution = df['day'].value_counts().to_dict()
                
                report["temporal_analysis"] = {
                    "hourly_distribution": hourly_distribution,
                    "daily_distribution": daily_distribution,
                    "peak_hour": max(hourly_distribution, key=hourly_distribution.get),
                    "peak_day": max(daily_distribution, key=daily_distribution.get)
                }
        
        report["anomaly_overview"] = {
            "total_anomalies": len(anomalies),
            "anomaly_rate": len(anomalies) / len(metrics) if metrics else 0,
            "time_period": data["time_range"]
        }
        
        return report
    
    async def _generate_performance_report(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate performance-focused report"""
        metrics = data["metrics"]
        
        report = {
            "performance_overview": {},
            "metric_analysis": {},
            "trend_analysis": {},
            "resource_utilization": {},
            "recommendations": []
        }
        
        if metrics:
            df = pd.DataFrame(metrics)
            df['value'] = pd.to_numeric(df['value'], errors='coerce')
            df = df.dropna(subset=['value'])
            
            # Overall performance metrics
            report["performance_overview"] = {
                "total_metrics": len(metrics),
                "unique_metric_names": df['name'].nunique() if 'name' in df.columns else 0,
                "data_sources": df['source'].nunique() if 'source' in df.columns else 0,
                "time_period": data["time_range"]
            }
            
            # Metric analysis by name
            if 'name' in df.columns:
                metric_stats = {}
                for name in df['name'].unique():
                    name_data = df[df['name'] == name]['value']
                    metric_stats[name] = {
                        "count": len(name_data),
                        "mean": float(name_data.mean()),
                        "std": float(name_data.std()),
                        "min": float(name_data.min()),
                        "max": float(name_data.max()),
                        "median": float(name_data.median())
                    }
                
                report["metric_analysis"] = metric_stats
            
            # Resource utilization (if metrics contain resource-related names)
            resource_metrics = {}
            for name in df['name'].unique():
                if any(keyword in name.lower() for keyword in ['cpu', 'memory', 'disk', 'network']):
                    name_data = df[df['name'] == name]['value']
                    resource_metrics[name] = {
                        "average_utilization": float(name_data.mean()),
                        "peak_utilization": float(name_data.max()),
                        "utilization_spread": float(name_data.std())
                    }
            
            report["resource_utilization"] = resource_metrics
        
        return report
    
    async def _generate_cicd_report(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate CI/CD focused report"""
        pipelines = data["pipelines"]
        
        report = {
            "cicd_overview": {},
            "pipeline_performance": {},
            "failure_analysis": {},
            "deployment_trends": {},
            "recommendations": []
        }
        
        if pipelines:
            # Overall CI/CD metrics
            status_counts = {}
            durations = []
            
            for pipeline in pipelines:
                status = pipeline['status']
                status_counts[status] = status_counts.get(status, 0) + 1
                if pipeline['duration']:
                    durations.append(pipeline['duration'])
            
            success_rate = status_counts.get('success', 0) / len(pipelines) * 100
            avg_duration = np.mean(durations) if durations else 0
            
            report["cicd_overview"] = {
                "total_pipelines": len(pipelines),
                "success_rate": success_rate,
                "average_duration": avg_duration,
                "status_breakdown": status_counts
            }
            
            # Pipeline performance analysis
            pipeline_stats = {}
            for pipeline in pipelines:
                name = pipeline['pipeline_name']
                if name not in pipeline_stats:
                    pipeline_stats[name] = {"durations": [], "statuses": []}
                
                if pipeline['duration']:
                    pipeline_stats[name]["durations"].append(pipeline['duration'])
                pipeline_stats[name]["statuses"].append(pipeline['status'])
            
            # Calculate statistics per pipeline
            for name, stats in pipeline_stats.items():
                durations = stats["durations"]
                statuses = stats["statuses"]
                
                pipeline_stats[name] = {
                    "total_runs": len(statuses),
                    "success_count": statuses.count('success'),
                    "success_rate": statuses.count('success') / len(statuses) * 100,
                    "average_duration": np.mean(durations) if durations else 0,
                    "max_duration": np.max(durations) if durations else 0
                }
            
            report["pipeline_performance"] = pipeline_stats
            
            # Failure analysis
            failed_pipelines = [p for p in pipelines if p['status'] == 'failed']
            if failed_pipelines:
                report["failure_analysis"] = {
                    "total_failures": len(failed_pipelines),
                    "failure_rate": len(failed_pipelines) / len(pipelines) * 100,
                    "failed_pipeline_names": list(set(p['pipeline_name'] for p in failed_pipelines))
                }
        
        return report
    
    async def _generate_testing_report(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate testing-focused report"""
        tests = data["tests"]
        
        report = {
            "testing_overview": {},
            "test_performance": {},
            "failure_analysis": {},
            "coverage_analysis": {},
            "recommendations": []
        }
        
        if tests:
            # Overall testing metrics
            status_counts = {}
            durations = []
            suite_counts = {}
            
            for test in tests:
                status = test['status']
                suite = test['test_suite']
                
                status_counts[status] = status_counts.get(status, 0) + 1
                suite_counts[suite] = suite_counts.get(suite, 0) + 1
                
                if test['duration']:
                    durations.append(test['duration'])
            
            pass_rate = status_counts.get('passed', 0) / len(tests) * 100
            avg_duration = np.mean(durations) if durations else 0
            
            report["testing_overview"] = {
                "total_tests": len(tests),
                "pass_rate": pass_rate,
                "average_duration": avg_duration,
                "unique_test_suites": len(suite_counts),
                "status_breakdown": status_counts
            }
            
            # Test suite performance
            suite_stats = {}
            for test in tests:
                suite = test['test_suite']
                if suite not in suite_stats:
                    suite_stats[suite] = {"durations": [], "statuses": []}
                
                if test['duration']:
                    suite_stats[suite]["durations"].append(test['duration'])
                suite_stats[suite]["statuses"].append(test['status'])
            
            # Calculate statistics per suite
            for suite, stats in suite_stats.items():
                durations = stats["durations"]
                statuses = stats["statuses"]
                
                suite_stats[suite] = {
                    "total_tests": len(statuses),
                    "passed_tests": statuses.count('passed'),
                    "failed_tests": statuses.count('failed'),
                    "skipped_tests": statuses.count('skipped'),
                    "pass_rate": statuses.count('passed') / len(statuses) * 100,
                    "average_duration": np.mean(durations) if durations else 0
                }
            
            report["test_performance"] = suite_stats
            
            # Failure analysis
            failed_tests = [t for t in tests if t['status'] == 'failed']
            if failed_tests:
                error_patterns = {}
                for test in failed_tests:
                    error_msg = test.get('error_message', 'Unknown error')
                    # Extract common error patterns
                    if 'AssertionError' in error_msg:
                        error_patterns['AssertionError'] = error_patterns.get('AssertionError', 0) + 1
                    elif 'TimeoutError' in error_msg:
                        error_patterns['TimeoutError'] = error_patterns.get('TimeoutError', 0) + 1
                    else:
                        error_patterns['Other'] = error_patterns.get('Other', 0) + 1
                
                report["failure_analysis"] = {
                    "total_failures": len(failed_tests),
                    "failure_rate": len(failed_tests) / len(tests) * 100,
                    "error_patterns": error_patterns
                }
        
        return report
    
    async def _generate_executive_summary(self, summary: Dict[str, Any]) -> str:
        """Generate executive summary text"""
        try:
            system_health = summary.get("system_health", {})
            anomalies_summary = summary.get("anomalies_summary", {})
            ci_cd_summary = summary.get("ci_cd_summary", {})
            testing_summary = summary.get("testing_summary", {})
            
            health_status = system_health.get("health_status", "unknown")
            total_anomalies = anomalies_summary.get("total_anomalies", 0)
            success_rate = ci_cd_summary.get("success_rate", 0)
            test_pass_rate = testing_summary.get("pass_rate", 0)
            
            executive_summary = f"""
System Performance Summary for the reporting period:

Overall system health is {health_status} with {total_anomalies} anomalies detected. 
CI/CD pipelines show a {success_rate:.1f}% success rate, while test suites maintain a {test_pass_rate:.1f}% pass rate.

"""
            
            if health_status == "healthy":
                executive_summary += "All systems are operating within normal parameters with minimal issues requiring attention."
            elif health_status == "warning":
                executive_summary += "Some systems show warning signs that should be monitored closely. Proactive measures may be needed to prevent degradation."
            else:
                executive_summary += "Critical issues detected that require immediate attention. System performance is significantly impacted."
            
            return executive_summary.strip()
        
        except Exception as e:
            logger.error("Failed to generate executive summary", error=str(e))
            return "Executive summary generation failed. Please review the detailed metrics and analysis sections."
    
    async def _generate_recommendations(self, data: Dict[str, Any], report_type: str) -> List[str]:
        """Generate recommendations based on report data"""
        recommendations = []
        
        try:
            anomalies = data.get("anomalies", [])
            logs = data.get("logs", [])
            pipelines = data.get("pipelines", [])
            tests = data.get("tests", [])
            
            # Anomaly-based recommendations
            if anomalies:
                unresolved_anomalies = [a for a in anomalies if not a.get('resolved', False)]
                if len(unresolved_anomalies) > 5:
                    recommendations.append("Address the high number of unresolved anomalies to improve system stability")
                
                critical_anomalies = [a for a in anomalies if a.get('severity') == 'critical']
                if critical_anomalies:
                    recommendations.append("Immediately investigate and resolve critical anomalies")
            
            # Log-based recommendations
            if logs:
                error_logs = [l for l in logs if l['level'] in ['ERROR', 'FATAL']]
                if len(error_logs) > len(logs) * 0.1:  # More than 10% errors
                    recommendations.append("Investigate the high error rate in application logs")
            
            # CI/CD recommendations
            if pipelines:
                failed_pipelines = [p for p in pipelines if p['status'] == 'failed']
                if len(failed_pipelines) > len(pipelines) * 0.2:  # More than 20% failure rate
                    recommendations.append("Review and improve CI/CD pipeline reliability")
            
            # Testing recommendations
            if tests:
                failed_tests = [t for t in tests if t['status'] == 'failed']
                if len(failed_tests) > len(tests) * 0.1:  # More than 10% failure rate
                    recommendations.append("Address test failures to improve code quality")
            
            # General recommendations
            recommendations.extend([
                "Continue monitoring system metrics and trends",
                "Implement automated alerting for critical anomalies",
                "Regular review and optimization of system performance"
            ])
            
        except Exception as e:
            logger.error("Failed to generate recommendations", error=str(e))
            recommendations.append("Review system logs and metrics for detailed analysis and optimization opportunities")
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    async def _format_report(self, content: Dict[str, Any], format_type: str) -> Dict[str, Any]:
        """Format report in the specified format"""
        if format_type == "json":
            return {"format": "json", "content": content}
        elif format_type == "html":
            html_content = await self._generate_html_report(content)
            return {"format": "html", "content": html_content}
        elif format_type == "markdown":
            markdown_content = await self._generate_markdown_report(content)
            return {"format": "markdown", "content": markdown_content}
        else:
            return {"format": "json", "content": content}
    
    async def _generate_html_report(self, content: Dict[str, Any]) -> str:
        """Generate HTML report"""
        html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Analytics Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .header { background-color: #f8f9fa; padding: 20px; border-radius: 5px; }
        .section { margin: 20px 0; }
        .metric { background-color: #e9ecef; padding: 10px; margin: 5px 0; border-radius: 3px; }
        .anomaly { background-color: #f8d7da; padding: 10px; margin: 5px 0; border-radius: 3px; }
        .success { background-color: #d4edda; padding: 10px; margin: 5px 0; border-radius: 3px; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Agentic Analytics Platform Report</h1>
        <p>Generated on: {{ timestamp }}</p>
    </div>
    
    {% if executive_summary %}
    <div class="section">
        <h2>Executive Summary</h2>
        <p>{{ executive_summary }}</p>
    </div>
    {% endif %}
    
    {% if key_metrics %}
    <div class="section">
        <h2>Key Metrics</h2>
        <div class="metric">Total Metrics: {{ key_metrics.total_metrics }}</div>
        <div class="metric">Unique Sources: {{ key_metrics.unique_sources }}</div>
        <div class="metric">Average Value: {{ "%.2f"|format(key_metrics.average_value) }}</div>
    </div>
    {% endif %}
    
    {% if anomalies_summary %}
    <div class="section">
        <h2>Anomalies Summary</h2>
        <div class="anomaly">Total Anomalies: {{ anomalies_summary.total_anomalies }}</div>
        <div class="anomaly">Unresolved: {{ anomalies_summary.unresolved_anomalies }}</div>
    </div>
    {% endif %}
    
    {% if recommendations %}
    <div class="section">
        <h2>Recommendations</h2>
        <ul>
        {% for rec in recommendations %}
            <li>{{ rec }}</li>
        {% endfor %}
        </ul>
    </div>
    {% endif %}
</body>
</html>
        """
        
        template = Template(html_template)
        return template.render(
            timestamp=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            **content
        )
    
    async def _generate_markdown_report(self, content: Dict[str, Any]) -> str:
        """Generate Markdown report"""
        markdown = "# Agentic Analytics Platform Report\n\n"
        markdown += f"**Generated on:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        if "executive_summary" in content:
            markdown += "## Executive Summary\n\n"
            markdown += f"{content['executive_summary']}\n\n"
        
        if "key_metrics" in content:
            markdown += "## Key Metrics\n\n"
            metrics = content["key_metrics"]
            markdown += f"- **Total Metrics:** {metrics.get('total_metrics', 0)}\n"
            markdown += f"- **Unique Sources:** {metrics.get('unique_sources', 0)}\n"
            markdown += f"- **Average Value:** {metrics.get('average_value', 0):.2f}\n\n"
        
        if "recommendations" in content:
            markdown += "## Recommendations\n\n"
            for rec in content["recommendations"]:
                markdown += f"- {rec}\n"
            markdown += "\n"
        
        return markdown
    
    async def _store_report(self, content: Dict[str, Any], report_type: str, time_range: str, db: Session) -> AnalyticsReport:
        """Store report in database"""
        try:
            report = AnalyticsReport(
                title=f"{report_type.title()} Report - {time_range}",
                report_type=report_type,
                content=json.dumps(content, default=str),
                time_range_start=datetime.utcnow() - timedelta(hours=24),  # Simplified
                time_range_end=datetime.utcnow(),
                metadata={"generated_by": "report_generation_agent"}
            )
            
            db.add(report)
            db.commit()
            db.refresh(report)
            
            logger.info("Report stored in database", report_id=report.id)
            return report
            
        except Exception as e:
            logger.error("Failed to store report", error=str(e))
            db.rollback()
            return None
    
    async def _generate_report_insights(self, content: Dict[str, Any], report_type: str) -> List[Dict[str, Any]]:
        """Generate insights from the report"""
        insights = []
        
        try:
            insights.append({
                "type": "report_generation",
                "title": f"{report_type.title()} Report Generated",
                "description": f"Successfully generated {report_type} report with comprehensive analysis",
                "confidence": 0.9,
                "severity": "low",
                "data_source": "report_generation",
                "related_entities": {"report_type": report_type},
                "metadata": {"report_sections": list(content.keys())}
            })
            
            # Add specific insights based on content
            if "anomalies_summary" in content:
                anomaly_count = content["anomalies_summary"].get("total_anomalies", 0)
                if anomaly_count > 10:
                    insights.append({
                        "type": "high_anomaly_count",
                        "title": "High Anomaly Count Detected",
                        "description": f"Report shows {anomaly_count} anomalies, which may require attention",
                        "confidence": 0.8,
                        "severity": "medium" if anomaly_count < 20 else "high",
                        "data_source": "report_analysis",
                        "related_entities": {"anomaly_count": anomaly_count}
                    })
        
        except Exception as e:
            logger.error("Failed to generate report insights", error=str(e))
        
        return insights
