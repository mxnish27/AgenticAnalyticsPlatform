@echo off
echo ========================================
echo   Platform Status Check
echo ========================================
echo.

echo 🔍 Docker Services Status:
echo ============================
docker-compose ps
echo.

echo 🏥 Health Checks:
echo ==================

:: Check Backend
echo Checking Backend API...
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Backend API: http://localhost:8000 - HEALTHY
) else (
    echo ❌ Backend API: http://localhost:8000 - NOT RESPONDING
)

:: Check AI Agents
echo Checking AI Agents...
curl -s http://localhost:8001/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ AI Agents: http://localhost:8001 - HEALTHY
) else (
    echo ❌ AI Agents: http://localhost:8001 - NOT RESPONDING
)

:: Check Database
echo Checking Database...
docker-compose exec -T postgres pg_isready -U analytics_user >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ PostgreSQL: RUNNING
) else (
    echo ❌ PostgreSQL: NOT RESPONDING
)

:: Check Redis
echo Checking Redis...
docker-compose exec -T redis redis-cli ping >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Redis: RUNNING
) else (
    echo ❌ Redis: NOT RESPONDING
)

echo.
echo 🌐 Access Links:
echo ================
echo    Backend API:       http://localhost:8000
echo    API Documentation: http://localhost:8000/docs
echo    AI Agents:         http://localhost:8001
echo    Grafana:           http://localhost:3001 (admin/admin123)
echo    Prometheus:        http://localhost:9090
echo    Airflow:           http://localhost:8080 (admin/admin)
echo.

echo 📊 Quick Test Commands:
echo ========================
echo    Test API:          curl http://localhost:8000/health
echo    View Logs:         docker-compose logs -f backend
echo    Restart Services:  docker-compose restart
echo.

pause
