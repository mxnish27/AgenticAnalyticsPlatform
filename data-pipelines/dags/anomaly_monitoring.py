from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.email import EmailOperator
from airflow.providers.http.operators.http import HttpOperator
import requests
import json
import structlog

logger = structlog.get_logger()

default_args = {
    'owner': 'analytics',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

def check_system_health(**context):
    """Check overall system health and metrics"""
    
    health_status = {
        'overall': 'healthy',
        'components': {},
        'issues': [],
        'timestamp': datetime.utcnow().isoformat()
    }
    
    # Check backend service
    try:
        response = requests.get("http://backend:8000/health", timeout=10)
        if response.status_code == 200:
            health_status['components']['backend'] = 'healthy'
        else:
            health_status['components']['backend'] = 'unhealthy'
            health_status['issues'].append(f"Backend returned status {response.status_code}")
    except Exception as e:
        health_status['components']['backend'] = 'unreachable'
        health_status['issues'].append(f"Backend unreachable: {str(e)}")
    
    # Check AI agents service
    try:
        response = requests.get("http://ai-agents:8001/health", timeout=10)
        if response.status_code == 200:
            health_status['components']['ai_agents'] = 'healthy'
        else:
            health_status['components']['ai_agents'] = 'unhealthy'
            health_status['issues'].append(f"AI Agents returned status {response.status_code}")
    except Exception as e:
        health_status['components']['ai_agents'] = 'unreachable'
        health_status['issues'].append(f"AI Agents unreachable: {str(e)}")
    
    # Check database connectivity
    try:
        from sqlalchemy import create_engine, text
        
        engine = create_engine("postgresql://analytics_user:analytics_password@postgres:5432/analytics_db")
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            health_status['components']['database'] = 'healthy'
    except Exception as e:
        health_status['components']['database'] = 'unhealthy'
        health_status['issues'].append(f"Database connection failed: {str(e)}")
    
    # Check Redis connectivity
    try:
        import redis
        r = redis.Redis(host='redis', port=6379, decode_responses=True)
        r.ping()
        health_status['components']['redis'] = 'healthy'
    except Exception as e:
        health_status['components']['redis'] = 'unhealthy'
        health_status['issues'].append(f"Redis connection failed: {str(e)}")
    
    # Determine overall health
    unhealthy_components = [k for k, v in health_status['components'].items() if v != 'healthy']
    if unhealthy_components:
        health_status['overall'] = 'unhealthy' if len(unhealthy_components) > 2 else 'degraded'
    
    # Push health status to XCom
    context['task_instance'].xcom_push(key='health_status', value=health_status)
    
    logger.info("System health check completed", status=health_status)
    
    return f"System health: {health_status['overall']} - {len(health_status['issues'])} issues found"

def detect_anomalies(**context):
    """Run comprehensive anomaly detection"""
    
    try:
        # Call AI agents for anomaly detection
        response = requests.post(
            "http://ai-agents:8001/agents/anomaly-detect",
            json={
                "data": {
                    "time_range": "1h",
                    "analysis_type": "comprehensive",
                    "sensitivity": 0.7
                }
            },
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            anomalies = result.get("result", {}).get("anomalies", [])
            statistics = result.get("result", {}).get("statistics", {})
            
            anomaly_summary = {
                'total_anomalies': len(anomalies),
                'critical_anomalies': len([a for a in anomalies if a.get('severity') == 'critical']),
                'high_anomalies': len([a for a in anomalies if a.get('severity') == 'high']),
                'anomaly_rate': statistics.get('anomaly_rate', 0),
                'detection_timestamp': datetime.utcnow().isoformat(),
                'anomalies': anomalies[:10]  # Store top 10 anomalies
            }
            
            # Push anomaly summary to XCom
            context['task_instance'].xcom_push(key='anomaly_summary', value=anomaly_summary)
            
            logger.info("Anomaly detection completed", 
                       total=anomaly_summary['total_anomalies'],
                       critical=anomaly_summary['critical_anomalies'])
            
            return f"Detected {anomaly_summary['total_anomalies']} anomalies"
        
        else:
            logger.error("Anomaly detection failed", status=response.status_code)
            return "Anomaly detection failed"
    
    except Exception as e:
        logger.error("Failed to detect anomalies", error=str(e))
        raise

def analyze_performance_metrics(**context):
    """Analyze performance metrics and trends"""
    
    try:
        # Get recent metrics from backend
        response = requests.get(
            "http://backend:8000/metrics",
            params={
                "start_time": (datetime.utcnow() - timedelta(hours=1)).isoformat(),
                "end_time": datetime.utcnow().isoformat()
            },
            timeout=30
        )
        
        if response.status_code == 200:
            metrics = response.json()
            
            performance_analysis = {
                'total_metrics': len(metrics),
                'metric_types': list(set(m.get('name', '') for m in metrics)),
                'sources': list(set(m.get('source', '') for m in metrics)),
                'time_range': '1h',
                'analysis_timestamp': datetime.utcnow().isoformat()
            }
            
            # Analyze specific performance metrics
            cpu_metrics = [m for m in metrics if 'cpu' in m.get('name', '').lower()]
            memory_metrics = [m for m in metrics if 'memory' in m.get('name', '').lower()]
            
            if cpu_metrics:
                cpu_values = [m.get('value', 0) for m in cpu_metrics]
                performance_analysis['cpu_analysis'] = {
                    'average': sum(cpu_values) / len(cpu_values),
                    'max': max(cpu_values),
                    'count': len(cpu_metrics)
                }
            
            if memory_metrics:
                memory_values = [m.get('value', 0) for m in memory_metrics]
                performance_analysis['memory_analysis'] = {
                    'average': sum(memory_values) / len(memory_values),
                    'max': max(memory_values),
                    'count': len(memory_metrics)
                }
            
            # Push performance analysis to XCom
            context['task_instance'].xcom_push(key='performance_analysis', value=performance_analysis)
            
            logger.info("Performance analysis completed", metrics_count=len(metrics))
            
            return f"Analyzed {len(metrics)} performance metrics"
        
        else:
            logger.error("Performance metrics analysis failed", status=response.status_code)
            return "Performance metrics analysis failed"
    
    except Exception as e:
        logger.error("Failed to analyze performance metrics", error=str(e))
        return "Failed to analyze performance metrics"

def check_error_rates(**context):
    """Check error rates from logs and services"""
    
    try:
        # Get recent error logs
        response = requests.get(
            "http://backend:8000/logs",
            params={
                "start_time": (datetime.utcnow() - timedelta(hours=1)).isoformat(),
                "end_time": datetime.utcnow().isoformat(),
                "level": "ERROR"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            error_logs = response.json()
            
            # Get total logs for rate calculation
            total_response = requests.get(
                "http://backend:8000/logs",
                params={
                    "start_time": (datetime.utcnow() - timedelta(hours=1)).isoformat(),
                    "end_time": datetime.utcnow().isoformat()
                },
                timeout=30
            )
            
            total_logs = total_response.json() if total_response.status_code == 200 else []
            
            error_analysis = {
                'error_count': len(error_logs),
                'total_log_count': len(total_logs),
                'error_rate': len(error_logs) / len(total_logs) * 100 if total_logs else 0,
                'error_sources': list(set(log.get('source', '') for log in error_logs)),
                'time_range': '1h',
                'analysis_timestamp': datetime.utcnow().isoformat()
            }
            
            # Analyze error patterns
            error_messages = [log.get('message', '') for log in error_logs]
            common_errors = {}
            for message in error_messages:
                # Extract error type from message
                error_type = message.split(':')[0] if ':' in message else 'Unknown'
                common_errors[error_type] = common_errors.get(error_type, 0) + 1
            
            error_analysis['common_error_types'] = dict(sorted(
                common_errors.items(), key=lambda x: x[1], reverse=True
            )[:5])
            
            # Push error analysis to XCom
            context['task_instance'].xcom_push(key='error_analysis', value=error_analysis)
            
            logger.info("Error rate analysis completed", 
                       error_rate=error_analysis['error_rate'],
                       error_count=error_analysis['error_count'])
            
            return f"Error rate: {error_analysis['error_rate']:.2f}%"
        
        else:
            logger.error("Error rate analysis failed", status=response.status_code)
            return "Error rate analysis failed"
    
    except Exception as e:
        logger.error("Failed to check error rates", error=str(e))
        return "Failed to check error rates"

def generate_alerts(**context):
    """Generate alerts based on all analyses"""
    
    # Pull all analysis results
    health_status = context['task_instance'].xcom_pull(
        task_ids='check_health',
        key='health_status'
    )
    
    anomaly_summary = context['task_instance'].xcom_pull(
        task_ids='detect_anomalies',
        key='anomaly_summary'
    )
    
    performance_analysis = context['task_instance'].xcom_pull(
        task_ids='analyze_performance',
        key='performance_analysis'
    )
    
    error_analysis = context['task_instance'].xcom_pull(
        task_ids='check_error_rates',
        key='error_analysis'
    )
    
    alerts = []
    
    # Health alerts
    if health_status and health_status['overall'] != 'healthy':
        alerts.append({
            'type': 'health',
            'severity': 'critical' if health_status['overall'] == 'unhealthy' else 'warning',
            'title': f"System Health: {health_status['overall'].upper()}",
            'message': f"Issues detected: {', '.join(health_status['issues'])}",
            'timestamp': datetime.utcnow().isoformat()
        })
    
    # Anomaly alerts
    if anomaly_summary:
        if anomaly_summary['critical_anomalies'] > 0:
            alerts.append({
                'type': 'anomaly',
                'severity': 'critical',
                'title': f"Critical Anomalies Detected",
                'message': f"{anomaly_summary['critical_anomalies']} critical anomalies found in the last hour",
                'timestamp': anomaly_summary['detection_timestamp']
            })
        elif anomaly_summary['high_anomalies'] > 5:
            alerts.append({
                'type': 'anomaly',
                'severity': 'warning',
                'title': f"High Number of Anomalies",
                'message': f"{anomaly_summary['high_anomalies']} high-severity anomalies detected",
                'timestamp': anomaly_summary['detection_timestamp']
            })
    
    # Performance alerts
    if performance_analysis:
        cpu_analysis = performance_analysis.get('cpu_analysis', {})
        if cpu_analysis.get('average', 0) > 80:
            alerts.append({
                'type': 'performance',
                'severity': 'warning',
                'title': "High CPU Usage",
                'message': f"Average CPU usage is {cpu_analysis['average']:.1f}%",
                'timestamp': performance_analysis['analysis_timestamp']
            })
        
        memory_analysis = performance_analysis.get('memory_analysis', {})
        if memory_analysis.get('average', 0) > 85:
            alerts.append({
                'type': 'performance',
                'severity': 'critical',
                'title': "High Memory Usage",
                'message': f"Average memory usage is {memory_analysis['average']:.1f}%",
                'timestamp': performance_analysis['analysis_timestamp']
            })
    
    # Error rate alerts
    if error_analysis and error_analysis['error_rate'] > 10:
        alerts.append({
            'type': 'error_rate',
            'severity': 'critical' if error_analysis['error_rate'] > 20 else 'warning',
            'title': "High Error Rate",
            'message': f"Error rate is {error_analysis['error_rate']:.2f}% ({error_analysis['error_count']} errors)",
            'timestamp': error_analysis['analysis_timestamp']
        })
    
    # Store alerts in database or send notifications
    if alerts:
        try:
            # Store alerts (this would typically go to a notification service)
            for alert in alerts:
                logger.warning("Alert generated", alert=alert)
            
            # Push alerts to XCom for notification task
            context['task_instance'].xcom_push(key='alerts', value=alerts)
            
            return f"Generated {len(alerts)} alerts"
        
        except Exception as e:
            logger.error("Failed to process alerts", error=str(e))
            return "Failed to process alerts"
    
    else:
        logger.info("No alerts generated - all systems normal")
        return "No alerts - systems operating normally"

def send_notifications(**context):
    """Send notifications for generated alerts"""
    
    alerts = context['task_instance'].xcom_pull(
        task_ids='generate_alerts',
        key='alerts'
    )
    
    if not alerts:
        logger.info("No alerts to notify")
        return "No alerts to notify"
    
    # Filter alerts by severity
    critical_alerts = [a for a in alerts if a['severity'] == 'critical']
    warning_alerts = [a for a in alerts if a['severity'] == 'warning']
    
    notifications_sent = 0
    
    # Send critical alerts immediately
    if critical_alerts:
        try:
            # This would integrate with your notification system
            # Email, Slack, PagerDuty, etc.
            
            for alert in critical_alerts:
                logger.critical("CRITICAL ALERT NOTIFICATION", alert=alert)
                # Send to notification service
                notifications_sent += 1
        
        except Exception as e:
            logger.error("Failed to send critical notifications", error=str(e))
    
    # Send warning alerts in batch
    if warning_alerts:
        try:
            logger.warning("WARNING ALERTS", alerts=warning_alerts)
            # Send batch notification
            notifications_sent += len(warning_alerts)
        
        except Exception as e:
            logger.error("Failed to send warning notifications", error=str(e))
    
    logger.info("Notifications sent", count=notifications_sent)
    return f"Sent {notifications_sent} notifications"

# Create DAG
with DAG(
    dag_id='anomaly_monitoring_pipeline',
    default_args=default_args,
    description='Monitor system health and detect anomalies',
    schedule_interval='*/15 * * * *',  # Every 15 minutes
    catchup=False,
    tags=['monitoring', 'anomalies', 'alerts'],
) as dag:
    
    # Task 1: Check system health
    check_health = PythonOperator(
        task_id='check_health',
        python_callable=check_system_health
    )
    
    # Task 2: Detect anomalies
    detect_anomalies = PythonOperator(
        task_id='detect_anomalies',
        python_callable=detect_anomalies
    )
    
    # Task 3: Analyze performance metrics
    analyze_performance = PythonOperator(
        task_id='analyze_performance',
        python_callable=analyze_performance_metrics
    )
    
    # Task 4: Check error rates
    check_error_rates = PythonOperator(
        task_id='check_error_rates',
        python_callable=check_error_rates
    )
    
    # Task 5: Generate alerts
    generate_alerts = PythonOperator(
        task_id='generate_alerts',
        python_callable=generate_alerts
    )
    
    # Task 6: Send notifications
    send_notifications = PythonOperator(
        task_id='send_notifications',
        python_callable=send_notifications
    )
    
    # Define task dependencies
    [check_health, detect_anomalies, analyze_performance, check_error_rates] >> generate_alerts >> send_notifications
