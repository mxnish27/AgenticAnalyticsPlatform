from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.http.operators.http import HttpOperator
from airflow.providers.http.sensors.http import HttpSensor
from airflow.models import Variable
import pandas as pd
import requests
import json
import structlog

logger = structlog.get_logger()

default_args = {
    'owner': 'analytics',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def extract_metrics_from_sources(**context):
    """Extract metrics from various data sources"""
    
    # Example: Extract from Prometheus API
    prometheus_url = Variable.get("PROMETHEUS_URL", default_var="http://prometheus:9090")
    
    metrics_to_extract = [
        'cpu_usage_percent',
        'memory_usage_percent',
        'disk_usage_percent',
        'network_bytes_sent',
        'network_bytes_received',
        'response_time_ms',
        'error_rate'
    ]
    
    extracted_metrics = []
    
    for metric_name in metrics_to_extract:
        try:
            # Query Prometheus
            query = f'rate({metric_name}[5m])'
            response = requests.get(
                f"{prometheus_url}/api/v1/query",
                params={'query': query}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data['status'] == 'success' and data['data']['result']:
                    for result in data['data']['result']:
                        metric_value = float(result['value'][1])
                        metric_labels = result['metric']
                        
                        extracted_metrics.append({
                            'name': metric_name,
                            'value': metric_value,
                            'unit': get_metric_unit(metric_name),
                            'source': 'prometheus',
                            'timestamp': datetime.utcnow(),
                            'tags': metric_labels
                        })
            
        except Exception as e:
            logger.error("Failed to extract metric", metric=metric_name, error=str(e))
    
    # Push metrics to XCom for next task
    context['task_instance'].xcom_push(key='extracted_metrics', value=extracted_metrics)
    
    return f"Extracted {len(extracted_metrics)} metrics from sources"

def get_metric_unit(metric_name):
    """Get unit for metric based on name"""
    if 'percent' in metric_name:
        return 'percent'
    elif 'bytes' in metric_name:
        return 'bytes'
    elif 'time' in metric_name:
        return 'milliseconds'
    elif 'rate' in metric_name:
        return 'rate'
    else:
        return 'count'

def transform_metrics(**context):
    """Transform and validate metrics"""
    
    # Pull metrics from previous task
    extracted_metrics = context['task_instance'].xcom_pull(
        task_ids='extract_metrics',
        key='extracted_metrics'
    )
    
    if not extracted_metrics:
        logger.warning("No metrics to transform")
        return "No metrics to transform"
    
    transformed_metrics = []
    
    for metric in extracted_metrics:
        # Data validation and cleaning
        try:
            # Validate numeric value
            if not isinstance(metric['value'], (int, float)):
                continue
            
            # Remove outliers (simple IQR method)
            if is_outlier(metric['value'], metric['name']):
                logger.warning("Skipping outlier metric", 
                             metric=metric['name'], value=metric['value'])
                continue
            
            # Add derived metrics
            if metric['name'] == 'cpu_usage_percent':
                metric['cpu_load'] = metric['value'] / 100.0
            elif metric['name'] == 'memory_usage_percent':
                metric['memory_pressure'] = 'high' if metric['value'] > 80 else 'normal'
            
            # Standardize timestamp format
            metric['timestamp'] = metric['timestamp'].isoformat()
            
            transformed_metrics.append(metric)
            
        except Exception as e:
            logger.error("Failed to transform metric", metric=metric, error=str(e))
    
    # Push transformed metrics to XCom
    context['task_instance'].xcom_push(
        key='transformed_metrics', 
        value=transformed_metrics
    )
    
    return f"Transformed {len(transformed_metrics)} metrics"

def is_outlier(value, metric_name, threshold=3.0):
    """Simple outlier detection using z-score (placeholder)"""
    # In a real implementation, you'd use historical data
    # For now, just check for obviously invalid values
    if 'percent' in metric_name and (value < 0 or value > 100):
        return True
    if value < 0:
        return True
    return False

def load_metrics_to_database(**context):
    """Load metrics into the analytics database"""
    
    # Pull transformed metrics
    transformed_metrics = context['task_instance'].xcom_pull(
        task_ids='transform_metrics',
        key='transformed_metrics'
    )
    
    if not transformed_metrics:
        logger.warning("No metrics to load")
        return "No metrics to load"
    
    # Database connection details
    db_url = Variable.get("DATABASE_URL", 
                          default_var="postgresql://analytics_user:analytics_password@postgres:5432/analytics_db")
    
    try:
        # Insert metrics into database (using SQLAlchemy)
        from sqlalchemy import create_engine, text
        
        engine = create_engine(db_url)
        
        loaded_count = 0
        with engine.connect() as conn:
            for metric in transformed_metrics:
                try:
                    # Insert metric using raw SQL for performance
                    insert_query = text("""
                        INSERT INTO metrics (name, value, unit, source, timestamp, tags, metadata, created_at)
                        VALUES (:name, :value, :unit, :source, :timestamp, :tags, :metadata, :created_at)
                    """)
                    
                    conn.execute(insert_query, {
                        'name': metric['name'],
                        'value': metric['value'],
                        'unit': metric.get('unit'),
                        'source': metric['source'],
                        'timestamp': metric['timestamp'],
                        'tags': json.dumps(metric.get('tags', {})),
                        'metadata': json.dumps({}),
                        'created_at': datetime.utcnow()
                    })
                    
                    loaded_count += 1
                    
                except Exception as e:
                    logger.error("Failed to insert metric", metric=metric, error=str(e))
            
            conn.commit()
        
        logger.info("Successfully loaded metrics to database", count=loaded_count)
        return f"Loaded {loaded_count} metrics to database"
        
    except Exception as e:
        logger.error("Failed to load metrics to database", error=str(e))
        raise

def trigger_anomaly_detection(**context):
    """Trigger anomaly detection AI agent"""
    
    backend_url = Variable.get("BACKEND_URL", default_var="http://backend:8000")
    ai_agents_url = Variable.get("AI_AGENTS_URL", default_var="http://ai-agents:8001")
    
    try:
        # Call anomaly detection API
        response = requests.post(
            f"{ai_agents_url}/agents/anomaly-detect",
            json={
                "data": {
                    "time_range": "1h",
                    "analysis_type": "batch"
                }
            },
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            anomaly_count = result.get("result", {}).get("statistics", {}).get("anomaly_count", 0)
            logger.info("Anomaly detection completed", anomalies_detected=anomaly_count)
            return f"Detected {anomaly_count} anomalies"
        else:
            logger.error("Anomaly detection failed", status=response.status_code)
            return "Anomaly detection failed"
            
    except Exception as e:
        logger.error("Failed to trigger anomaly detection", error=str(e))
        return "Failed to trigger anomaly detection"

# Create DAG
with DAG(
    dag_id='metrics_ingestion_pipeline',
    default_args=default_args,
    description='Ingest metrics from various sources and process them',
    schedule_interval='*/5 * * * *',  # Every 5 minutes
    catchup=False,
    tags=['metrics', 'ingestion', 'analytics'],
) as dag:
    
    # Task 1: Check if data sources are available
    check_data_sources = HttpSensor(
        task_id='check_data_sources',
        http_conn_id='prometheus_default',
        endpoint='/api/v1/query',
        request_params={'query': 'up'},
        poke_interval=60,
        timeout=300,
        mode='poke'
    )
    
    # Task 2: Extract metrics from sources
    extract_metrics = PythonOperator(
        task_id='extract_metrics',
        python_callable=extract_metrics_from_sources
    )
    
    # Task 3: Transform and validate metrics
    transform_metrics = PythonOperator(
        task_id='transform_metrics',
        python_callable=transform_metrics
    )
    
    # Task 4: Load metrics to database
    load_metrics = PythonOperator(
        task_id='load_metrics',
        python_callable=load_metrics_to_database
    )
    
    # Task 5: Trigger anomaly detection
    trigger_anomaly_detection = PythonOperator(
        task_id='trigger_anomaly_detection',
        python_callable=trigger_anomaly_detection
    )
    
    # Task 6: Clean up old data (optional)
    cleanup_old_data = BashOperator(
        task_id='cleanup_old_data',
        bash_command="""
        echo "Cleaning up data older than 30 days..."
        # This would typically be a Python script or SQL command
        echo "Cleanup completed"
        """
    )
    
    # Define task dependencies
    check_data_sources >> extract_metrics >> transform_metrics >> load_metrics >> trigger_anomaly_detection
    trigger_anomaly_detection >> cleanup_old_data
