@echo off
echo ========================================
echo   Agentic Analytics Platform - Quick Setup
echo ========================================
echo.

:: Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed!
    echo Please install Docker Desktop first: https://www.docker.com/products/docker-desktop/
    echo.
    pause
    exit /b 1
)

:: Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running!
    echo Please start Docker Desktop first.
    echo.
    pause
    exit /b 1
)

echo ✅ Docker is ready!
echo.

:: Stop any existing containers
echo 🔄 Stopping any existing services...
docker-compose down >nul 2>&1

:: Start all services
echo 🚀 Starting all services...
echo This will take 2-3 minutes on first run...
echo.

docker-compose up -d

:: Wait for services to be ready
echo ⏳ Waiting for services to start...
timeout /t 30 /nobreak >nul

:: Check if services are running
echo.
echo 🔍 Checking service status...
docker-compose ps

echo.
echo ========================================
echo   ✅ Setup Complete!
echo ========================================
echo.
echo 🌐 Access your platform:
echo    Backend API:       http://localhost:8000
echo    API Docs:          http://localhost:8000/docs
echo    AI Agents:         http://localhost:8001
echo    Grafana Dashboard: http://localhost:3001 (admin/admin123)
echo    Prometheus:        http://localhost:9090
echo    Airflow:           http://localhost:8080 (admin/admin)
echo.
echo 💡 To stop all services later, run: docker-compose down
echo.
pause
