# Kubernetes Deployment

This directory contains Kubernetes manifests for deploying the Agentic Analytics Platform to production.

## Architecture

The platform consists of the following services:

- **Frontend**: React dashboard (Node.js/Nginx)
- **Backend**: FastAPI REST API (Python)
- **AI Agents**: AI/ML processing service (Python)
- **PostgreSQL**: Primary database
- **Redis**: Cache and message queue
- **Prometheus**: Metrics collection
- **Grafana**: Monitoring dashboard
- **Airflow**: Data pipeline orchestration

## Prerequisites

1. **Kubernetes cluster** (v1.20+)
2. **kubectl** configured for your cluster
3. **Docker registry** access
4. **SSL certificates** (for production)
5. **Ingress controller** (nginx recommended)

## Quick Start

### 1. Update Configuration

Edit the configuration files with your values:

```bash
# Update secrets with your actual values
kubectl create secret generic analytics-secrets \
  --from-literal=SECRET_KEY=your-secure-secret-key \
  --from-literal=OPENAI_API_KEY=your-openai-api-key \
  --from-literal=DATABASE_PASSWORD=your-db-password \
  --from-literal=GRAFANA_ADMIN_PASSWORD=your-admin-password \
  -n agentic-analytics
```

### 2. Deploy the Platform

```bash
# Make the deployment script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

### 3. Verify Deployment

```bash
# Check all pods
kubectl get pods -n agentic-analytics

# Check services
kubectl get services -n agentic-analytics

# Check ingress
kubectl get ingress -n agentic-analytics
```

## Manual Deployment Steps

If you prefer to deploy components manually:

### 1. Create Namespace
```bash
kubectl apply -f namespace.yaml
```

### 2. Deploy Infrastructure
```bash
kubectl apply -f secrets.yaml
kubectl apply -f configmap.yaml
kubectl apply -f postgres.yaml
kubectl apply -f redis.yaml
```

### 3. Deploy Applications
```bash
kubectl apply -f backend.yaml
kubectl apply -f ai-agents.yaml
kubectl apply -f frontend.yaml
```

### 4. Deploy Monitoring
```bash
kubectl apply -f monitoring.yaml
```

### 5. Deploy Data Pipelines
```bash
kubectl apply -f airflow.yaml
```

## Configuration

### Environment Variables

Key configuration options in `configmap.yaml`:

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | - |
| `REDIS_URL` | Redis connection string | - |
| `PROMETHEUS_URL` | Prometheus URL | - |
| `LOG_LEVEL` | Application log level | INFO |
| `AGENT_TIMEOUT` | AI agent timeout (seconds) | 30 |
| `ANOMALY_THRESHOLD` | Anomaly detection threshold | 0.7 |

### Secrets

Sensitive data stored in `secrets.yaml`:

| Secret | Description |
|--------|-------------|
| `SECRET_KEY` | JWT signing key |
| `OPENAI_API_KEY` | OpenAI API key |
| `DATABASE_PASSWORD` | PostgreSQL password |
| `GRAFANA_ADMIN_PASSWORD` | Grafana admin password |

### Resource Limits

Each deployment includes resource requests and limits:

| Service | CPU Request | CPU Limit | Memory Request | Memory Limit |
|---------|-------------|-----------|----------------|--------------|
| Backend | 500m | 1000m | 512Mi | 1Gi |
| AI Agents | 1000m | 2000m | 1Gi | 2Gi |
| Frontend | 100m | 200m | 128Mi | 256Mi |
| PostgreSQL | 500m | 1000m | 1Gi | 2Gi |
| Redis | 250m | 500m | 256Mi | 512Mi |

## Scaling

### Horizontal Scaling

The platform includes Horizontal Pod Autoscalers for:

- **Backend**: 3-10 replicas (based on CPU/memory)
- **AI Agents**: 2-5 replicas (based on CPU/memory)

Manual scaling:
```bash
# Scale backend to 5 replicas
kubectl scale deployment backend --replicas=5 -n agentic-analytics

# Scale AI agents to 3 replicas
kubectl scale deployment ai-agents --replicas=3 -n agentic-analytics
```

### Vertical Scaling

Update resource limits in the deployment manifests:
```bash
# Edit backend deployment
kubectl edit deployment backend -n agentic-analytics
```

## Monitoring

### Prometheus Metrics

Access Prometheus metrics:
```bash
# Port forward to local
kubectl port-forward service/prometheus 9090:9090 -n agentic-analytics

# Access at http://localhost:9090
```

### Grafana Dashboard

Access Grafana:
```bash
# Port forward to local
kubectl port-forward service/grafana 3000:3000 -n agentic-analytics

# Access at http://localhost:3000
# Username: admin
# Password: admin123 (or your configured password)
```

### Logs

View logs for any service:
```bash
# Backend logs
kubectl logs -f deployment/backend -n agentic-analytics

# AI agents logs
kubectl logs -f deployment/ai-agents -n agentic-analytics

# All logs
kubectl logs -f --all-containers=true -n agentic-analytics
```

## Troubleshooting

### Common Issues

1. **Pods not starting**
   ```bash
   # Check pod status
   kubectl describe pod <pod-name> -n agentic-analytics
   
   # Check events
   kubectl get events -n agentic-analytics --sort-by='.lastTimestamp'
   ```

2. **Database connection issues**
   ```bash
   # Check PostgreSQL pod
   kubectl logs -f statefulset/postgres -n agentic-analytics
   
   # Test connection
   kubectl exec -it statefulset/postgres -n agentic-analytics -- psql -U analytics_user -d analytics_db
   ```

3. **High memory usage**
   ```bash
   # Check resource usage
   kubectl top pods -n agentic-analytics
   
   # Check resource limits
   kubectl describe pod <pod-name> -n agentic-analytics
   ```

### Health Checks

All services include health and readiness probes:

```bash
# Check health endpoints
kubectl get endpoints -n agentic-analytics

# Check pod readiness
kubectl get pods -n agentic-analytics -o wide
```

## Security

### Network Policies

Apply network policies for additional security:
```bash
kubectl apply -f network-policies.yaml
```

### RBAC

The platform uses least-privilege RBAC:
```bash
# Check service accounts
kubectl get serviceaccounts -n agentic-analytics

# Check roles
kubectl get roles -n agentic-analytics
```

## Backup and Recovery

### Database Backup

```bash
# Create backup
kubectl exec -it statefulset/postgres -n agentic-analytics -- \
  pg_dump -U analytics_user analytics_db > backup.sql

# Restore backup
kubectl exec -it statefulset/postgres -n agentic-analytics -- \
  psql -U analytics_user analytics_db < backup.sql
```

### Persistent Volumes

Data is stored in PersistentVolumeClaims:
```bash
# List PVCs
kubectl get pvc -n agentic-analytics

# Check storage classes
kubectl get storageclass
```

## Upgrades

### Rolling Updates

Updates are performed with rolling updates:
```bash
# Update image version
kubectl set image deployment/backend backend=your-registry/backend:v2.0.0 -n agentic-analytics

# Check rollout status
kubectl rollout status deployment/backend -n agentic-analytics

# Rollback if needed
kubectl rollout undo deployment/backend -n agentic-analytics
```

## Maintenance

### Cleanup

Remove the entire deployment:
```bash
# Delete namespace and all resources
kubectl delete namespace agentic-analytics

# Or delete specific resources
kubectl delete -f .
```

### Performance Tuning

Monitor and tune performance:
```bash
# Check resource usage
kubectl top nodes
kubectl top pods -n agentic-analytics

# Adjust resource limits as needed
kubectl edit deployment <deployment-name> -n agentic-analytics
```

## Support

For issues and questions:

1. Check the troubleshooting section above
2. Review the main project documentation
3. Check Kubernetes events and logs
4. Monitor Grafana dashboards for system health

## Production Considerations

1. **SSL/TLS**: Ensure proper SSL certificates are configured
2. **Backup**: Implement regular database backups
3. **Monitoring**: Set up alerting in Grafana/Prometheus
4. **Security**: Apply network policies and RBAC
5. **Scaling**: Configure appropriate resource limits and HPA
6. **Disaster Recovery**: Test backup and restore procedures
