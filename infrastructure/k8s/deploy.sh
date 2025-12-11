#!/bin/bash

# Agentic Analytics Platform - Kubernetes Deployment Script
# This script deploys the entire platform to Kubernetes

set -e

# Configuration
NAMESPACE="agentic-analytics"
DOCKER_REGISTRY="your-registry.com"  # Replace with your actual registry
VERSION="latest"

echo "🚀 Starting Agentic Analytics Platform deployment..."

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed. Please install kubectl first."
    exit 1
fi

# Check if cluster is accessible
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ Cannot connect to Kubernetes cluster. Please check your kubeconfig."
    exit 1
fi

# Create namespace
echo "📦 Creating namespace..."
kubectl apply -f namespace.yaml

# Apply secrets and configmaps
echo "🔧 Applying configuration..."
kubectl apply -f secrets.yaml
kubectl apply -f configmap.yaml

# Deploy database and cache
echo "🗄️ Deploying database and cache..."
kubectl apply -f postgres.yaml
kubectl apply -f redis.yaml

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
kubectl wait --for=condition=ready pod -l app=postgres -n $NAMESPACE --timeout=300s
kubectl wait --for=condition=ready pod -l app=redis -n $NAMESPACE --timeout=180s

# Deploy backend services
echo "🔧 Deploying backend services..."
kubectl apply -f backend.yaml
kubectl apply -f ai-agents.yaml

# Wait for backend services to be ready
echo "⏳ Waiting for backend services to be ready..."
kubectl wait --for=condition=ready pod -l app=backend -n $NAMESPACE --timeout=300s
kubectl wait --for=condition=ready pod -l app=ai-agents -n $NAMESPACE --timeout=300s

# Deploy frontend
echo "🎨 Deploying frontend..."
kubectl apply -f frontend.yaml

# Deploy monitoring
echo "📊 Deploying monitoring stack..."
kubectl apply -f monitoring.yaml

# Deploy data pipelines
echo "🔄 Deploying data pipelines..."
kubectl apply -f airflow.yaml

# Initialize Airflow
echo "🔧 Initializing Airflow..."
kubectl wait --for=condition=complete job/airflow-init -n $NAMESPACE --timeout=300s

# Wait for all pods to be ready
echo "⏳ Waiting for all pods to be ready..."
kubectl wait --for=condition=ready pod -l app!=airflow-init -n $NAMESPACE --timeout=600s

# Display deployment status
echo "📋 Deployment Status:"
kubectl get pods -n $NAMESPACE
kubectl get services -n $NAMESPACE

# Display access information
echo ""
echo "✅ Deployment completed successfully!"
echo ""
echo "🌐 Access Information:"
echo "   Frontend: http://analytics.yourdomain.com"
echo "   Backend API: http://analytics.yourdomain.com/api"
echo "   AI Agents: http://analytics.yourdomain.com/ai-agents"
echo "   Grafana: http://analytics.yourdomain.com/grafana"
echo "   Airflow: http://analytics.yourdomain.com/airflow"
echo ""
echo "🔑 Default Credentials:"
echo "   Grafana: admin / admin123"
echo "   Airflow: admin / admin"
echo ""
echo "📊 Monitoring Commands:"
echo "   View pods:     kubectl get pods -n $NAMESPACE"
echo "   View logs:     kubectl logs -f deployment/backend -n $NAMESPACE"
echo "   Scale service: kubectl scale deployment backend --replicas=5 -n $NAMESPACE"
echo ""
echo "🔧 Useful Commands:"
echo "   Port forward:  kubectl port-forward service/backend 8000:8000 -n $NAMESPACE"
echo "   Exec into pod: kubectl exec -it deployment/backend -n $NAMESPACE -- bash"
echo "   Check status:  kubectl get all -n $NAMESPACE"

# Optional: Run health checks
echo ""
echo "🏥 Running health checks..."

# Check backend health
BACKEND_URL=$(kubectl get ingress analytics-ingress -n $NAMESPACE -o jsonpath='{.spec.rules[0].host}/api/health')
if curl -f -s $BACKEND_URL > /dev/null; then
    echo "✅ Backend health check passed"
else
    echo "⚠️ Backend health check failed"
fi

# Check AI agents health
AI_AGENTS_URL=$(kubectl get ingress analytics-ingress -n $NAMESPACE -o jsonpath='{.spec.rules[0].host}/ai-agents/health')
if curl -f -s $AI_AGENTS_URL > /dev/null; then
    echo "✅ AI Agents health check passed"
else
    echo "⚠️ AI Agents health check failed"
fi

echo ""
echo "🎉 Agentic Analytics Platform is now running!"
echo "📚 For more information, check the documentation at: https://docs.analytics.yourdomain.com"
