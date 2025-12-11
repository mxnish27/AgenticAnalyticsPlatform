FROM apache/airflow:2.7.3-python3.11

# Install system dependencies
USER root
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /opt/airflow
USER airflow

# Create directories
RUN mkdir -p /opt/airflow/dags /opt/airflow/logs /opt/airflow/plugins

# Copy DAG files
COPY dags/ /opt/airflow/dags/

# Set environment variables
ENV AIRFLOW__CORE__EXECUTOR=LocalExecutor
ENV AIRFLOW__CORE__SQL_ALCHEMY_CONN=postgresql://analytics_user:analytics_password@postgres:5432/analytics_db
ENV AIRFLOW__CORE__FERNET_KEY=your-fernet-key-here
ENV AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION=false
ENV AIRFLOW__CORE__LOAD_EXAMPLES=false
ENV AIRFLOW__API__AUTH_BACKENDS=airflow.api.auth.backend.basic_auth

# Expose Airflow ports
EXPOSE 8080

# Initialize database
RUN airflow db init

# Create admin user
RUN airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password admin

# Command to run Airflow webserver
CMD ["airflow", "webserver"]
