# 🚀 Complete Setup Guide for Beginners

This guide will walk you through setting up the Agentic Analytics Platform from scratch, even if you're new to development.

## 📋 Prerequisites (What you need first)

### 1. Install Docker (Most Important!)
Docker helps run all services without complex installations.

**Windows:**
1. Go to https://www.docker.com/products/docker-desktop/
2. Download Docker Desktop for Windows
3. Run the installer (it might take 10-15 minutes)
4. Restart your computer when prompted
5. Open Docker Desktop - it should show "Docker Desktop is running"

### 2. Install Node.js (for the frontend)
1. Go to https://nodejs.org/
2. Download the LTS version (recommended)
3. Run the installer
4. Restart your computer

### 3. Install Git (optional but recommended)
1. Go to https://git-scm.com/download/win
2. Download and install Git

---

## 🎯 Quick Setup (5 minutes if Docker is ready)

### Step 1: Open Terminal/Command Prompt
- Press `Win + R`, type `cmd`, press Enter
- OR press `Win + X`, select "Windows PowerShell"

### Step 2: Navigate to Project Folder
```bash
cd C:\Users\palmanis\CascadeProjects\agentic-analytics-platform
```

### Step 3: Start Everything with One Command
```bash
docker-compose up -d
```

This will:
- ✅ Install and start the database (PostgreSQL)
- ✅ Install and start cache (Redis)
- ✅ Install and start the backend API
- ✅ Install and start the AI agents service
- ✅ Install and start the data pipelines
- ✅ Install and start monitoring tools

### Step 4: Wait 2-3 Minutes
The first time takes longer as Docker downloads everything. You'll see messages like:
```
Creating postgres... done
Creating redis... done
Creating backend... done
```

### Step 5: Check if Everything is Working
```bash
docker-compose ps
```

You should see all services with "Up" status:
```
NAME                COMMAND                  SERVICE             STATUS              PORTS
backend             "uvicorn main:app..."     backend             Up (healthy)        0.0.0.0:8000->8000/tcp
postgres            "docker-entrypoint.s..."  postgres            Up (healthy)        0.0.0.0:5432->5432/tcp
redis               "docker-entrypoint.s..."  redis               Up (healthy)        0.0.0.0:6379->6379/tcp
```

---

## 🌐 Access Your Platform

Once everything is running, open your web browser:

### Main Applications
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **AI Agents**: http://localhost:8001
- **Airflow (Data Pipelines)**: http://localhost:8080

### Monitoring Tools
- **Grafana Dashboard**: http://localhost:3001
  - Username: `admin`
  - Password: `admin123`
- **Prometheus Metrics**: http://localhost:9090

---

## 💻 Setting Up the Frontend (Optional - for development)

If you want to modify the frontend or run it locally:

### Step 1: Open New Terminal
Keep the first terminal running, open a new one.

### Step 2: Navigate to Frontend Folder
```bash
cd C:\Users\palmanis\CascadeProjects\agentic-analytics-platform\frontend
```

### Step 3: Install Dependencies
```bash
npm install
```

### Step 4: Start Frontend
```bash
npm start
```

This will open the frontend at http://localhost:3000

---

## 🔧 Troubleshooting Common Issues

### Problem: "docker: command not found"
**Solution:** Docker isn't installed or not in PATH
1. Restart your computer after installing Docker Desktop
2. Open Command Prompt as Administrator and try again

### Problem: "Port 8000 is already in use"
**Solution:** Another program is using the port
```bash
# Find what's using the port
netstat -ano | findstr :8000

# Stop the service (replace PID with the number from above)
taskkill /PID <PID> /F
```

### Problem: Services keep restarting
**Solution:** Check the logs
```bash
docker-compose logs backend
```

### Problem: "Access denied" errors
**Solution:** Run as Administrator
1. Right-click Command Prompt
2. Select "Run as administrator"

---

## 📊 First Time Data Setup

The platform starts with sample data, but here's how to add your own:

### 1. Add Data Sources via API
Open http://localhost:8000/docs in your browser and use these endpoints:

**Add a Prometheus data source:**
```json
POST /api/data-sources
{
  "name": "My Prometheus",
  "type": "prometheus",
  "url": "http://prometheus:9090",
  "config": {
    "scrape_interval": "15s"
  }
}
```

**Add a logs data source:**
```json
POST /api/data-sources
{
  "name": "Application Logs",
  "type": "logs",
  "config": {
    "log_level": "info",
    "source": "app"
  }
}
```

### 2. Generate Sample Data
```bash
# This creates sample metrics and anomalies
curl -X POST http://localhost:8000/api/generate-sample-data
```

---

## 🎯 What to Try First

1. **Explore the API Documentation**
   - Go to http://localhost:8000/docs
   - Try the `/api/health` endpoint
   - Check `/api/metrics` for sample data

2. **View Monitoring Dashboard**
   - Go to http://localhost:3001
   - Login with admin/admin123
   - Explore the pre-built dashboards

3. **Test AI Agents**
   - Go to http://localhost:8001/docs
   - Try the `/detect-anomalies` endpoint

4. **Check Data Pipelines**
   - Go to http://localhost:8080
   - Login with admin/admin
   - See the automated data processing

---

## 🛑 How to Stop Everything

When you're done working:

```bash
# Stop all services
docker-compose down

# Stop and remove all data (use with caution!)
docker-compose down -v
```

---

## 📝 Environment Variables (Advanced)

If you need to customize settings, create a `.env` file:

```bash
# Create the file
notepad .env
```

Add these settings:
```env
# Database
DATABASE_URL=postgresql://analytics_user:analytics_password@postgres:5432/analytics_db

# Redis
REDIS_URL=redis://redis:6379

# AI Services
OPENAI_API_KEY=your-openai-api-key-here

# Security
SECRET_KEY=your-secret-key-here
```

---

## 🆘 Getting Help

### If Something Goes Wrong:

1. **Check Docker is running**
   - Docker Desktop should be open and show "running"

2. **Check service status**
   ```bash
   docker-compose ps
   ```

3. **View logs for errors**
   ```bash
   docker-compose logs --tail=50
   ```

4. **Restart everything**
   ```bash
   docker-compose down
   docker-compose up -d
   ```

### Common Fixes:
- **Restart Docker Desktop**
- **Run Command Prompt as Administrator**
- **Check if firewall is blocking ports 8000, 5432, 6379**
- **Make sure you have enough disk space (Docker needs ~2GB)**

---

## 🎉 You're All Set!

Congratulations! You now have:
- ✅ A complete analytics platform running
- ✅ Database and cache services
- ✅ AI-powered anomaly detection
- ✅ Real-time monitoring dashboards
- ✅ Automated data pipelines

**Next Steps:**
1. Explore the API documentation
2. Add your own data sources
3. Create custom dashboards in Grafana
4. Set up alerts for anomalies

For detailed documentation, check the `README.md` file in each service folder.
