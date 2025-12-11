from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.email import EmailOperator
from airflow.providers.http.operators.http import HttpOperator
import requests
import json
import structlog
from pathlib import Path

logger = structlog.get_logger()

default_args = {
    'owner': 'analytics',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

def generate_daily_report(**context):
    """Generate daily analytics report"""
    
    try:
        # Call AI agents for report generation
        response = requests.post(
            "http://ai-agents:8001/agents/generate-report",
            json={
                "report_type": "summary",
                "time_range": "24h",
                "format": "json",
                "include_recommendations": True
            },
            headers={"Content-Type": "application/json"},
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            report_data = result.get("result", {}).get("report", {}).get("content", {})
            
            daily_report = {
                'report_type': 'daily_summary',
                'generated_at': datetime.utcnow().isoformat(),
                'time_range': '24h',
                'data': report_data,
                'metadata': {
                    'report_id': result.get("report_id"),
                    'insights_count': len(result.get("insights", [])),
                    'data_points': result.get("metadata", {}).get("data_points", {})
                }
            }
            
            # Push report to XCom
            context['task_instance'].xcom_push(key='daily_report', value=daily_report)
            
            logger.info("Daily report generated successfully", 
                       report_id=daily_report['metadata']['report_id'])
            
            return f"Daily report generated with ID: {daily_report['metadata']['report_id']}"
        
        else:
            logger.error("Daily report generation failed", status=response.status_code)
            return "Daily report generation failed"
    
    except Exception as e:
        logger.error("Failed to generate daily report", error=str(e))
        raise

def generate_anomaly_report(**context):
    """Generate anomaly-focused report"""
    
    try:
        response = requests.post(
            "http://ai-agents:8001/agents/generate-report",
            json={
                "report_type": "anomaly",
                "time_range": "24h",
                "format": "json",
                "include_recommendations": True
            },
            headers={"Content-Type": "application/json"},
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            report_data = result.get("result", {}).get("report", {}).get("content", {})
            
            anomaly_report = {
                'report_type': 'anomaly_analysis',
                'generated_at': datetime.utcnow().isoformat(),
                'time_range': '24h',
                'data': report_data,
                'metadata': {
                    'report_id': result.get("report_id"),
                    'insights_count': len(result.get("insights", [])),
                    'anomaly_count': report_data.get("anomaly_overview", {}).get("total_anomalies", 0)
                }
            }
            
            # Push report to XCom
            context['task_instance'].xcom_push(key='anomaly_report', value=anomaly_report)
            
            logger.info("Anomaly report generated successfully",
                       report_id=anomaly_report['metadata']['report_id'],
                       anomaly_count=anomaly_report['metadata']['anomaly_count'])
            
            return f"Anomaly report generated with {anomaly_report['metadata']['anomaly_count']} anomalies"
        
        else:
            logger.error("Anomaly report generation failed", status=response.status_code)
            return "Anomaly report generation failed"
    
    except Exception as e:
        logger.error("Failed to generate anomaly report", error=str(e))
        raise

def generate_performance_report(**context):
    """Generate performance-focused report"""
    
    try:
        response = requests.post(
            "http://ai-agents:8001/agents/generate-report",
            json={
                "report_type": "performance",
                "time_range": "24h",
                "format": "json",
                "include_recommendations": True
            },
            headers={"Content-Type": "application/json"},
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            report_data = result.get("result", {}).get("report", {}).get("content", {})
            
            performance_report = {
                'report_type': 'performance_analysis',
                'generated_at': datetime.utcnow().isoformat(),
                'time_range': '24h',
                'data': report_data,
                'metadata': {
                    'report_id': result.get("report_id"),
                    'insights_count': len(result.get("insights", [])),
                    'metrics_analyzed': report_data.get("performance_overview", {}).get("total_metrics", 0)
                }
            }
            
            # Push report to XCom
            context['task_instance'].xcom_push(key='performance_report', value=performance_report)
            
            logger.info("Performance report generated successfully",
                       report_id=performance_report['metadata']['report_id'],
                       metrics_count=performance_report['metadata']['metrics_analyzed'])
            
            return f"Performance report generated with {performance_report['metadata']['metrics_analyzed']} metrics"
        
        else:
            logger.error("Performance report generation failed", status=response.status_code)
            return "Performance report generation failed"
    
    except Exception as e:
        logger.error("Failed to generate performance report", error=str(e))
        raise

def generate_ci_cd_report(**context):
    """Generate CI/CD focused report"""
    
    try:
        response = requests.post(
            "http://ai-agents:8001/agents/generate-report",
            json={
                "report_type": "ci_cd",
                "time_range": "24h",
                "format": "json",
                "include_recommendations": True
            },
            headers={"Content-Type": "application/json"},
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            report_data = result.get("result", {}).get("report", {}).get("content", {})
            
            cicd_report = {
                'report_type': 'ci_cd_analysis',
                'generated_at': datetime.utcnow().isoformat(),
                'time_range': '24h',
                'data': report_data,
                'metadata': {
                    'report_id': result.get("report_id"),
                    'insights_count': len(result.get("insights", [])),
                    'pipeline_count': report_data.get("cicd_overview", {}).get("total_pipelines", 0),
                    'success_rate': report_data.get("cicd_overview", {}).get("success_rate", 0)
                }
            }
            
            # Push report to XCom
            context['task_instance'].xcom_push(key='cicd_report', value=cicd_report)
            
            logger.info("CI/CD report generated successfully",
                       report_id=cicd_report['metadata']['report_id'],
                       success_rate=cicd_report['metadata']['success_rate'])
            
            return f"CI/CD report generated with {cicd_report['metadata']['success_rate']:.1f}% success rate"
        
        else:
            logger.error("CI/CD report generation failed", status=response.status_code)
            return "CI/CD report generation failed"
    
    except Exception as e:
        logger.error("Failed to generate CI/CD report", error=str(e))
        raise

def generate_weekly_summary(**context):
    """Generate comprehensive weekly summary"""
    
    # Get execution date to determine if it's the weekly run
    execution_date = context['execution_date']
    
    # Only run on Mondays (weekday() == 0)
    if execution_date.weekday() != 0:
        logger.info("Skipping weekly summary - not Monday")
        return "Weekly summary skipped (not Monday)"
    
    try:
        response = requests.post(
            "http://ai-agents:8001/agents/generate-report",
            json={
                "report_type": "summary",
                "time_range": "7d",
                "format": "html",
                "include_recommendations": True
            },
            headers={"Content-Type": "application/json"},
            timeout=180
        )
        
        if response.status_code == 200:
            result = response.json()
            report_data = result.get("result", {}).get("report", {}).get("content", {})
            
            weekly_summary = {
                'report_type': 'weekly_summary',
                'generated_at': datetime.utcnow().isoformat(),
                'time_range': '7d',
                'data': report_data,
                'metadata': {
                    'report_id': result.get("report_id"),
                    'insights_count': len(result.get("insights", [])),
                    'format': 'html'
                }
            }
            
            # Push weekly summary to XCom
            context['task_instance'].xcom_push(key='weekly_summary', value=weekly_summary)
            
            logger.info("Weekly summary generated successfully",
                       report_id=weekly_summary['metadata']['report_id'])
            
            return f"Weekly summary generated with ID: {weekly_summary['metadata']['report_id']}"
        
        else:
            logger.error("Weekly summary generation failed", status=response.status_code)
            return "Weekly summary generation failed"
    
    except Exception as e:
        logger.error("Failed to generate weekly summary", error=str(e))
        raise

def save_reports_to_storage(**context):
    """Save generated reports to persistent storage"""
    
    saved_reports = []
    
    # Get all reports from XCom
    reports = [
        ('daily_report', 'daily_summary'),
        ('anomaly_report', 'anomaly_analysis'),
        ('performance_report', 'performance_analysis'),
        ('cicd_report', 'ci_cd_analysis'),
        ('weekly_summary', 'weekly_summary')
    ]
    
    for xcom_key, report_name in reports:
        report = context['task_instance'].xcom_pull(key=xcom_key)
        
        if not report:
            continue
        
        try:
            # Create report filename
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"{report_name}_{timestamp}.json"
            
            # Save to local storage (in production, this would be S3, Azure Blob, etc.)
            report_dir = Path("/opt/airflow/reports")
            report_dir.mkdir(exist_ok=True)
            
            file_path = report_dir / filename
            
            with open(file_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            saved_reports.append({
                'name': report_name,
                'filename': filename,
                'path': str(file_path),
                'size': file_path.stat().st_size
            })
            
            logger.info("Report saved to storage", 
                       name=report_name, 
                       filename=filename,
                       size=file_path.stat().st_size)
        
        except Exception as e:
            logger.error("Failed to save report", name=report_name, error=str(e))
    
    # Push saved reports info to XCom
    context['task_instance'].xcom_push(key='saved_reports', value=saved_reports)
    
    return f"Saved {len(saved_reports)} reports to storage"

def email_reports(**context):
    """Email reports to stakeholders"""
    
    saved_reports = context['task_instance'].xcom_pull(
        task_ids='save_reports',
        key='saved_reports'
    )
    
    if not saved_reports:
        logger.info("No reports to email")
        return "No reports to email"
    
    try:
        # Create email content
        email_content = create_email_content(saved_reports)
        
        # In a real implementation, you would use EmailOperator or SMTP
        # For now, we'll just log the email content
        logger.info("Email reports prepared", 
                   recipients_count=len(get_report_recipients()),
                   reports_count=len(saved_reports))
        
        # Example of how you would send with EmailOperator:
        # EmailOperator(
        #     task_id='send_email',
        #     to=get_report_recipients(),
        #     subject=f"Analytics Platform Reports - {datetime.utcnow().strftime('%Y-%m-%d')}",
        #     html_content=email_content,
        #     files=[report['path'] for report in saved_reports]
        # ).execute(context)
        
        return f"Email prepared with {len(saved_reports)} reports for {len(get_report_recipients())} recipients"
    
    except Exception as e:
        logger.error("Failed to email reports", error=str(e))
        return "Failed to email reports"

def create_email_content(reports):
    """Create HTML email content for reports"""
    
    html_content = """
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .header { background-color: #f8f9fa; padding: 20px; border-radius: 5px; }
            .report { margin: 10px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
            .summary { background-color: #e9ecef; padding: 10px; margin: 5px 0; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Agentic Analytics Platform - Daily Reports</h1>
            <p>Generated on: {}</p>
        </div>
    """.format(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))
    
    for report in reports:
        html_content += f"""
        <div class="report">
            <h3>{report['name'].replace('_', ' ').title()}</h3>
            <div class="summary">
                <p><strong>File:</strong> {report['filename']}</p>
                <p><strong>Size:</strong> {report['size']} bytes</p>
            </div>
        </div>
        """
    
    html_content += """
        <div class="footer">
            <p>For detailed analysis, please refer to the attached reports or visit the dashboard.</p>
            <p><a href="http://localhost:3000">Analytics Dashboard</a></p>
        </div>
    </body>
    </html>
    """
    
    return html_content

def get_report_recipients():
    """Get list of report recipients"""
    # In a real implementation, this would come from configuration or database
    return [
        'admin@company.com',
        'devops@company.com',
        'analytics@company.com'
    ]

def cleanup_old_reports(**context):
    """Clean up old reports from storage"""
    
    try:
        import os
        import glob
        
        report_dir = Path("/opt/airflow/reports")
        
        if not report_dir.exists():
            logger.info("Report directory does not exist")
            return "Report directory does not exist"
        
        # Find reports older than 30 days
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        deleted_count = 0
        
        for report_file in report_dir.glob("*.json"):
            file_time = datetime.fromtimestamp(report_file.stat().st_mtime)
            
            if file_time < cutoff_date:
                report_file.unlink()
                deleted_count += 1
                logger.info("Deleted old report", file=report_file.name)
        
        logger.info("Report cleanup completed", deleted_count=deleted_count)
        return f"Cleaned up {deleted_count} old reports"
    
    except Exception as e:
        logger.error("Failed to cleanup old reports", error=str(e))
        return "Failed to cleanup old reports"

# Create DAG
with DAG(
    dag_id='report_generation_pipeline',
    default_args=default_args,
    description='Generate and distribute analytics reports',
    schedule_interval='0 8 * * *',  # Daily at 8 AM
    catchup=False,
    tags=['reports', 'analytics', 'email'],
) as dag:
    
    # Task 1: Generate daily summary report
    generate_daily = PythonOperator(
        task_id='generate_daily_report',
        python_callable=generate_daily_report
    )
    
    # Task 2: Generate anomaly report
    generate_anomaly = PythonOperator(
        task_id='generate_anomaly_report',
        python_callable=generate_anomaly_report
    )
    
    # Task 3: Generate performance report
    generate_performance = PythonOperator(
        task_id='generate_performance_report',
        python_callable=generate_performance_report
    )
    
    # Task 4: Generate CI/CD report
    generate_cicd = PythonOperator(
        task_id='generate_cicd_report',
        python_callable=generate_ci_cd_report
    )
    
    # Task 5: Generate weekly summary (Mondays only)
    generate_weekly = PythonOperator(
        task_id='generate_weekly_summary',
        python_callable=generate_weekly_summary
    )
    
    # Task 6: Save reports to storage
    save_reports = PythonOperator(
        task_id='save_reports',
        python_callable=save_reports_to_storage
    )
    
    # Task 7: Email reports to stakeholders
    email_reports = PythonOperator(
        task_id='email_reports',
        python_callable=email_reports
    )
    
    # Task 8: Clean up old reports
    cleanup_reports = PythonOperator(
        task_id='cleanup_reports',
        python_callable=cleanup_old_reports
    )
    
    # Define task dependencies
    [generate_daily, generate_anomaly, generate_performance, generate_cicd, generate_weekly] >> save_reports >> email_reports
    email_reports >> cleanup_reports
