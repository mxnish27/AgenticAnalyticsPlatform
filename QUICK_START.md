# Quick Start Guide

## Prerequisites

Before running the Agentic Analytics Platform, ensure you have the following installed:

1. **Docker & Docker Compose** - Required for containerized deployment
2. **Node.js 18+** - For frontend development (if running locally)
3. **Python 3.11+** - For backend development (if running locally)
4. **PostgreSQL** - Database (can run via Docker)
5. **Redis** - Cache and message queue (can run via Docker)

## Installation & Setup

### 1. Clone and Navigate to Project

```bash
git clone <repository-url>
cd agentic-analytics-platform
```

### 2. Environment Configuration

Copy the environment template and configure your settings:

```bash
cp .env.example .env
```

Edit `.env` file with your configuration:
- Database credentials
- API keys (OpenAI for AI agents)
- Service ports
- Other environment-specific settings

### 3. Start Services with Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### 4. Initialize Database

The database will be automatically initialized with sample data when you start the services. You can also run the initialization manually:

```bash
# Connect to PostgreSQL container
docker-compose exec postgres psql -U analytics_user -d analytics_db -f /docker-entrypoint-initdb.d/init.sql
```

## Access Points

Once services are running, you can access:

- **Frontend Dashboard**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **AI Agents Service**: http://localhost:8001
- **API Documentation**: http://localhost:8000/docs
- **AI Agents API Docs**: http://localhost:8001/docs
- **Grafana Monitoring**: http://localhost:3001
- **Prometheus**: http://localhost:9090
- **Airflow**: http://localhost:8080

## Development Setup

### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
cd frontend
npm install

# Run development server
npm start
```

### AI Agents Development

```bash
cd ai-agents
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run development server
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

## Key Features

### 1. Dashboard
- Real-time metrics visualization
- Anomaly detection alerts
- System health monitoring
- Interactive charts and graphs

### 2. Data Ingestion
- Multiple data source connectors
- Real-time data streaming
- Data validation and preprocessing
- Automatic schema detection

### 3. AI Agents
- **Anomaly Detection**: Statistical and ML-based anomaly detection
- **Data Interpretation**: Natural language query processing
- **Root Cause Analysis**: Automated issue investigation
- **Report Generation**: Automated analytics reports

### 4. Monitoring & Alerting
- Prometheus metrics collection
- Grafana dashboards
- Custom alert rules
- Notification integrations

## API Usage

### Authentication

The platform uses JWT-based authentication. Get your token:

```bash
curl -X POST "http://localhost:8000/auth/login" -H "Content-Type: application/json"
```

### Sample API Calls

#### Get Metrics
```bash
curl -X GET "http://localhost:8000/metrics" -H "Authorization: Bearer <token>"
```

#### Detect Anomalies
```bash
curl -X POST "http://localhost:8001/agents/anomaly-detect" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"data": {"metrics": [...]}}'
```

#### Process Natural Language Query
```bash
curl -X POST "http://localhost:8001/agents/conversational-query" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"data": {"query": "Show me recent anomalies"}}'
```

## Configuration

### Data Sources

Configure data sources through the Settings UI or API:

```json
{
  "name": "Production Metrics",
  "type": "metrics",
  "config": {
    "endpoint": "https://your-metrics-endpoint.com",
    "api_key": "your-api-key",
    "collection_interval": 60
  },
  "enabled": true
}
```

### AI Agent Configuration

Configure AI agents in the `.env` file:

```bash
# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-3.5-turbo

# Agent Settings
AGENT_TIMEOUT=30
ANOMALY_THRESHOLD=0.7
```

## Troubleshooting

### Common Issues

1. **Docker Services Not Starting**
   - Check if Docker is running: `docker --version`
   - Verify ports are not in use
   - Check logs: `docker-compose logs <service-name>`

2. **Database Connection Errors**
   - Verify PostgreSQL is running: `docker-compose ps postgres`
   - Check database credentials in `.env`
   - Ensure database is initialized

3. **Frontend Not Loading**
   - Check if backend API is accessible: `curl http://localhost:8000/health`
   - Verify CORS settings in backend
   - Check browser console for errors

4. **AI Agents Not Responding**
   - Verify OpenAI API key is set correctly
   - Check AI agent service logs
   - Ensure Redis is running for caching

### Logs and Monitoring

- **Application Logs**: `docker-compose logs -f backend frontend ai-agents`
- **Database Logs**: `docker-compose logs -f postgres`
- **System Metrics**: Grafana dashboard at http://localhost:3001
- **Prometheus Metrics**: http://localhost:9090

## Production Deployment

### Environment Variables

For production, ensure these are properly configured:

```bash
# Security
SECRET_KEY=your-secure-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Database
DATABASE_URL=postgresql://user:pass@prod-db:5432/analytics_db
REDIS_URL=redis://prod-redis:6379

# AI Services
OPENAI_API_KEY=your-production-openai-key

# Monitoring
PROMETHEUS_ENABLED=true
GRAFANA_ADMIN_PASSWORD=secure-password
```

### Scaling

- Use Docker Swarm or Kubernetes for orchestration
- Configure horizontal pod autoscaling
- Set up load balancers for high availability
- Implement database replication for fault tolerance

### Security

- Enable HTTPS with SSL certificates
- Configure firewall rules
- Set up API rate limiting
- Enable audit logging
- Regular security updates

## Support

For issues and questions:

1. Check the troubleshooting section above
2. Review application logs for error details
3. Consult the API documentation at `/docs`
4. Check the monitoring dashboards in Grafana

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
