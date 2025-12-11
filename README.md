# Agentic Analytics Platform

An AI-driven analytics platform that autonomously gathers, processes, and visualizes enterprise data using agentic AI for actionable insights and predictive analysis.

## Features

- **Multi-source Data Integration**: Logs, metrics, test results, CI/CD reports
- **AI-Powered Analytics**: Anomaly detection, root cause analysis, automated reporting
- **Interactive Dashboard**: Real-time visualization with conversational queries
- **Predictive Insights**: Trend prediction and performance optimization recommendations

## Architecture

```
├── frontend/                 # React + TypeScript + TailwindCSS
├── backend/                  # FastAPI + Python
├── ai-agents/               # LangChain agents and AI logic
├── data-pipelines/          # ETL and data processing
├── infrastructure/          # Docker, K8s configs
└── monitoring/              # Airflow DAGs, monitoring setup
```

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.9+ (for local backend development)

### Using Docker Compose (Recommended)

1. Clone the repository
2. Copy environment files:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. Start all services:
   ```bash
   docker-compose up -d
   ```

4. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Local Development

See individual README files in each service directory for detailed setup instructions.

## Technology Stack

- **Frontend**: React, TypeScript, TailwindCSS, Recharts
- **Backend**: FastAPI, Python, PostgreSQL, Redis
- **AI/ML**: OpenAI, LangChain, Scikit-learn, Pandas
- **Infrastructure**: Docker, Kubernetes, Azure Cloud
- **Monitoring**: Prometheus, Grafana, Airflow

## Configuration

Key environment variables:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/analytics_db
REDIS_URL=redis://localhost:6379

# AI Services
OPENAI_API_KEY=your_openai_api_key

# Security
JWT_SECRET_KEY=your_jwt_secret
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request


