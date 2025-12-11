from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.docker.operators.docker import DockerOperator
import pandas as pd
import requests
import json
import structlog
import gzip
import os
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

def extract_logs_from_sources(**context):
    """Extract logs from various sources"""
    
    # Example log sources configuration
    log_sources = {
        'application_logs': {
            'type': 'file',
            'path': '/var/log/application/*.log',
            'format': 'json'
        },
        'nginx_logs': {
            'type': 'file',
            'path': '/var/log/nginx/*.log',
            'format': 'combined'
        },
        'system_logs': {
            'type': 'syslog',
            'path': '/var/log/syslog',
            'format': 'syslog'
        },
        'docker_logs': {
            'type': 'docker',
            'containers': ['backend', 'frontend', 'ai-agents'],
            'format': 'json'
        }
    }
    
    extracted_logs = []
    
    for source_name, source_config in log_sources.items():
        try:
            logs = extract_from_source(source_name, source_config)
            extracted_logs.extend(logs)
            logger.info("Extracted logs from source", source=source_name, count=len(logs))
            
        except Exception as e:
            logger.error("Failed to extract logs from source", source=source_name, error=str(e))
    
    # Push logs to XCom for next task
    context['task_instance'].xcom_push(key='extracted_logs', value=extracted_logs)
    
    return f"Extracted {len(extracted_logs)} log entries from all sources"

def extract_from_source(source_name, source_config):
    """Extract logs from a specific source"""
    logs = []
    
    if source_config['type'] == 'file':
        logs = extract_from_files(source_config['path'], source_config['format'])
    elif source_config['type'] == 'docker':
        logs = extract_from_docker(source_config['containers'], source_config['format'])
    elif source_config['type'] == 'syslog':
        logs = extract_from_syslog(source_config['path'])
    elif source_config['type'] == 'api':
        logs = extract_from_api(source_config.get('url'), source_config.get('headers'))
    
    return logs

def extract_from_files(file_pattern, log_format):
    """Extract logs from files"""
    logs = []
    
    # Find matching files
    import glob
    files = glob.glob(file_pattern)
    
    for file_path in files:
        try:
            if file_path.endswith('.gz'):
                # Handle compressed logs
                with gzip.open(file_path, 'rt') as f:
                    file_logs = parse_log_content(f.read(), log_format, file_path)
            else:
                with open(file_path, 'r') as f:
                    file_logs = parse_log_content(f.read(), log_format, file_path)
            
            logs.extend(file_logs)
            
        except Exception as e:
            logger.error("Failed to read log file", file=file_path, error=str(e))
    
    return logs

def extract_from_docker(containers, log_format):
    """Extract logs from Docker containers"""
    logs = []
    
    import subprocess
    
    for container in containers:
        try:
            # Get Docker logs
            result = subprocess.run(
                ['docker', 'logs', '--since', '5m', container],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                container_logs = parse_log_content(result.stdout, log_format, f"docker://{container}")
                logs.extend(container_logs)
            
        except Exception as e:
            logger.error("Failed to extract Docker logs", container=container, error=str(e))
    
    return logs

def extract_from_syslog(syslog_path):
    """Extract logs from syslog"""
    logs = []
    
    try:
        with open(syslog_path, 'r') as f:
            content = f.read()
            
        # Parse syslog format
        for line in content.split('\n'):
            if line.strip():
                try:
                    # Simple syslog parsing
                    parts = line.split(' ', 5)
                    if len(parts) >= 6:
                        timestamp_str = f"{parts[0]} {parts[1]} {parts[2]}"
                        hostname = parts[3]
                        process = parts[4]
                        message = parts[5] if len(parts) > 5 else ""
                        
                        logs.append({
                            'level': determine_log_level(message),
                            'message': message,
                            'source': f"syslog:{hostname}:{process}",
                            'timestamp': parse_syslog_timestamp(timestamp_str),
                            'metadata': {
                                'hostname': hostname,
                                'process': process
                            }
                        })
                
                except Exception as e:
                    logger.warning("Failed to parse syslog line", line=line, error=str(e))
    
    except Exception as e:
        logger.error("Failed to read syslog", path=syslog_path, error=str(e))
    
    return logs

def extract_from_api(url, headers):
    """Extract logs from API endpoint"""
    logs = []
    
    try:
        response = requests.get(url, headers=headers or {})
        if response.status_code == 200:
            data = response.json()
            
            # Assume API returns array of log entries
            for log_entry in data:
                logs.append({
                    'level': log_entry.get('level', 'INFO'),
                    'message': log_entry.get('message', ''),
                    'source': log_entry.get('source', 'api'),
                    'timestamp': log_entry.get('timestamp', datetime.utcnow()),
                    'metadata': log_entry.get('metadata', {})
                })
    
    except Exception as e:
        logger.error("Failed to extract logs from API", url=url, error=str(e))
    
    return logs

def parse_log_content(content, log_format, source):
    """Parse log content based on format"""
    logs = []
    
    for line in content.split('\n'):
        if not line.strip():
            continue
        
        try:
            if log_format == 'json':
                log_entry = json.loads(line)
                logs.append({
                    'level': log_entry.get('level', 'INFO'),
                    'message': log_entry.get('message', ''),
                    'source': log_entry.get('source', source),
                    'timestamp': log_entry.get('timestamp', datetime.utcnow()),
                    'metadata': {k: v for k, v in log_entry.items() 
                               if k not in ['level', 'message', 'source', 'timestamp']}
                })
            
            elif log_format == 'combined':
                # Parse Apache/Nginx combined log format
                parts = line.split(' ', 7)
                if len(parts) >= 8:
                    logs.append({
                        'level': 'INFO',
                        'message': f"HTTP {parts[5]} {parts[6]} {parts[7]}",
                        'source': source,
                        'timestamp': datetime.utcnow(),
                        'metadata': {
                            'ip': parts[0],
                            'timestamp': parts[3] + ' ' + parts[4],
                            'method': parts[5].strip('"'),
                            'status': parts[6],
                            'size': parts[7]
                        }
                    })
            
            else:
                # Default parsing
                logs.append({
                    'level': determine_log_level(line),
                    'message': line,
                    'source': source,
                    'timestamp': datetime.utcnow(),
                    'metadata': {}
                })
        
        except Exception as e:
            logger.warning("Failed to parse log line", line=line[:100], error=str(e))
    
    return logs

def determine_log_level(message):
    """Determine log level from message content"""
    message_upper = message.upper()
    
    if any(keyword in message_upper for keyword in ['ERROR', 'FATAL', 'CRITICAL']):
        return 'ERROR'
    elif any(keyword in message_upper for keyword in ['WARN', 'WARNING']):
        return 'WARN'
    elif any(keyword in message_upper for keyword in ['DEBUG']):
        return 'DEBUG'
    else:
        return 'INFO'

def parse_syslog_timestamp(timestamp_str):
    """Parse syslog timestamp"""
    try:
        # Simple timestamp parsing - adjust based on your syslog format
        return datetime.strptime(timestamp_str, '%b %d %H:%M:%S').replace(
            year=datetime.now().year
        )
    except:
        return datetime.utcnow()

def transform_logs(**context):
    """Transform and enrich logs"""
    
    # Pull logs from previous task
    extracted_logs = context['task_instance'].xcom_pull(
        task_ids='extract_logs',
        key='extracted_logs'
    )
    
    if not extracted_logs:
        logger.warning("No logs to transform")
        return "No logs to transform"
    
    transformed_logs = []
    
    for log in extracted_logs:
        try:
            # Data validation and cleaning
            if not log.get('message'):
                continue
            
            # Enrich log data
            enriched_log = enrich_log_entry(log)
            
            # Filter out noise
            if should_include_log(enriched_log):
                transformed_logs.append(enriched_log)
        
        except Exception as e:
            logger.error("Failed to transform log", log=log, error=str(e))
    
    # Push transformed logs to XCom
    context['task_instance'].xcom_push(
        key='transformed_logs',
        value=transformed_logs
    )
    
    return f"Transformed {len(transformed_logs)} log entries"

def enrich_log_entry(log):
    """Enrich log entry with additional information"""
    
    # Add parsing timestamp
    log['parsed_at'] = datetime.utcnow()
    
    # Extract structured information from message
    message = log.get('message', '')
    
    # Extract error codes
    import re
    error_codes = re.findall(r'[A-Z]{2,}-\d+', message)
    if error_codes:
        log['error_codes'] = error_codes
    
    # Extract IP addresses
    ip_addresses = re.findall(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', message)
    if ip_addresses:
        log['ip_addresses'] = ip_addresses
    
    # Extract URLs
    urls = re.findall(r'https?://[^\s]+', message)
    if urls:
        log['urls'] = urls
    
    # Categorize log
    log['category'] = categorize_log(message, log.get('level', 'INFO'))
    
    return log

def categorize_log(message, level):
    """Categorize log based on content and level"""
    message_lower = message.lower()
    
    if level in ['ERROR', 'FATAL']:
        return 'error'
    elif any(keyword in message_lower for keyword in ['http', 'request', 'response']):
        return 'http'
    elif any(keyword in message_lower for keyword in ['database', 'sql', 'query']):
        return 'database'
    elif any(keyword in message_lower for keyword in ['auth', 'login', 'token']):
        return 'authentication'
    elif any(keyword in message_lower for keyword in ['performance', 'slow', 'timeout']):
        return 'performance'
    else:
        return 'general'

def should_include_log(log):
    """Filter out noise and unnecessary logs"""
    
    message = log.get('message', '').lower()
    level = log.get('level', 'INFO')
    
    # Filter out health check logs
    if any(keyword in message for keyword in ['health', 'ping', 'heartbeat']):
        return False
    
    # Filter out debug logs unless they contain errors
    if level == 'DEBUG' and 'error' not in message:
        return False
    
    # Filter out very short messages
    if len(message) < 10:
        return False
    
    return True

def load_logs_to_database(**context):
    """Load logs into the analytics database"""
    
    # Pull transformed logs
    transformed_logs = context['task_instance'].xcom_pull(
        task_ids='transform_logs',
        key='transformed_logs'
    )
    
    if not transformed_logs:
        logger.warning("No logs to load")
        return "No logs to load"
    
    # Database connection
    from sqlalchemy import create_engine, text
    
    db_url = "postgresql://analytics_user:analytics_password@postgres:5432/analytics_db"
    
    try:
        engine = create_engine(db_url)
        loaded_count = 0
        
        with engine.connect() as conn:
            for log in transformed_logs:
                try:
                    insert_query = text("""
                        INSERT INTO log_entries (level, message, source, timestamp, metadata, created_at)
                        VALUES (:level, :message, :source, :timestamp, :metadata, :created_at)
                    """)
                    
                    # Prepare metadata
                    metadata = {k: v for k, v in log.items() 
                              if k not in ['level', 'message', 'source', 'timestamp', 'parsed_at']}
                    
                    conn.execute(insert_query, {
                        'level': log['level'],
                        'message': log['message'][:1000],  # Limit message length
                        'source': log['source'],
                        'timestamp': log['timestamp'],
                        'metadata': json.dumps(metadata),
                        'created_at': datetime.utcnow()
                    })
                    
                    loaded_count += 1
                
                except Exception as e:
                    logger.error("Failed to insert log", log=log, error=str(e))
            
            conn.commit()
        
        logger.info("Successfully loaded logs to database", count=loaded_count)
        return f"Loaded {loaded_count} logs to database"
    
    except Exception as e:
        logger.error("Failed to load logs to database", error=str(e))
        raise

def analyze_log_patterns(**context):
    """Analyze log patterns and detect anomalies"""
    
    backend_url = "http://backend:8000"
    
    try:
        # Trigger log analysis
        response = requests.post(
            f"{backend_url}/analytics/analyze-logs",
            json={
                "time_range": "1h",
                "analysis_type": "patterns"
            },
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            logger.info("Log pattern analysis completed", result=result)
            return "Log pattern analysis completed"
        else:
            logger.error("Log pattern analysis failed", status=response.status_code)
            return "Log pattern analysis failed"
    
    except Exception as e:
        logger.error("Failed to analyze log patterns", error=str(e))
        return "Failed to analyze log patterns"

# Create DAG
with DAG(
    dag_id='logs_ingestion_pipeline',
    default_args=default_args,
    description='Ingest logs from various sources and process them',
    schedule_interval='*/10 * * * *',  # Every 10 minutes
    catchup=False,
    tags=['logs', 'ingestion', 'analytics'],
) as dag:
    
    # Task 1: Extract logs from sources
    extract_logs = PythonOperator(
        task_id='extract_logs',
        python_callable=extract_logs_from_sources
    )
    
    # Task 2: Transform and enrich logs
    transform_logs = PythonOperator(
        task_id='transform_logs',
        python_callable=transform_logs
    )
    
    # Task 3: Load logs to database
    load_logs = PythonOperator(
        task_id='load_logs',
        python_callable=load_logs_to_database
    )
    
    # Task 4: Analyze log patterns
    analyze_patterns = PythonOperator(
        task_id='analyze_patterns',
        python_callable=analyze_log_patterns
    )
    
    # Task 5: Archive old logs
    archive_logs = BashOperator(
        task_id='archive_logs',
        bash_command="""
        echo "Archiving logs older than 7 days..."
        # This would typically move logs to cold storage
        echo "Archive completed"
        """
    )
    
    # Define task dependencies
    extract_logs >> transform_logs >> load_logs >> analyze_patterns >> archive_logs
