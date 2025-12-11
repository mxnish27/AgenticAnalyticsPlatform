# Agentic Analytics Platform - Deployment Guide

## ✅ Build Status: SUCCESS

The frontend has been successfully built and is ready for deployment.

**Build output location:** `frontend/build/`

---

## Option 1: Deploy to Netlify (Manual - Drag & Drop)

This is the easiest method:

1. Go to https://app.netlify.com/
2. Sign up or log in with GitHub
3. Click **"Add new site"** → **"Deploy manually"**
4. Drag and drop the `frontend/build` folder
5. Your site will be live in seconds!

**Build folder path:**
```
C:\Users\palmanis\CascadeProjects\agentic-analytics-platform\frontend\build
```

---

## Option 2: Deploy to Netlify via GitHub

1. Push your code to GitHub:
   ```cmd
   cd C:\Users\palmanis\CascadeProjects\agentic-analytics-platform
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/agentic-analytics-platform.git
   git push -u origin main
   ```

2. Go to https://app.netlify.com/
3. Click **"Add new site"** → **"Import an existing project"**
4. Connect to GitHub and select your repository
5. Configure build settings:
   - **Base directory:** `frontend`
   - **Build command:** `npm run build`
   - **Publish directory:** `frontend/build`
6. Click **"Deploy site"**

---

## Option 3: Deploy to Vercel

1. Go to https://vercel.com/
2. Sign up or log in with GitHub
3. Click **"Add New..."** → **"Project"**
4. Import your GitHub repository
5. Configure:
   - **Root Directory:** `frontend`
   - **Framework Preset:** Create React App
6. Click **"Deploy"**

---

## Option 4: Deploy Full Stack with Docker

For the complete application (frontend + backend + database):

### On Your Local Machine:
```cmd
cd C:\Users\palmanis\CascadeProjects\agentic-analytics-platform

# Copy environment file
copy .env.example .env

# Edit .env and add your OpenAI API key
notepad .env

# Start all services
docker-compose up -d
```

### On a Cloud Server (AWS, Azure, GCP, DigitalOcean):

1. **Provision a server** with Docker installed (Ubuntu 20.04+ recommended)

2. **Copy the project** to the server:
   ```bash
   scp -r agentic-analytics-platform user@server-ip:/home/user/
   ```

3. **Configure and run:**
   ```bash
   cd agentic-analytics-platform
   cp .env.example .env
   nano .env  # Add your OpenAI API key and change secrets
   docker-compose up -d
   ```

4. **Access the application:**
   - Frontend: http://server-ip:3000
   - Backend API: http://server-ip:8000
   - Grafana: http://server-ip:3001

---

## Environment Variables Required

For production deployment, set these in your `.env` file:

```env
# Required
OPENAI_API_KEY=sk-your-openai-api-key

# Security - CHANGE THESE IN PRODUCTION
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this
POSTGRES_PASSWORD=your-secure-database-password

# Optional
REACT_APP_API_URL=https://your-backend-url.com
```

---

## Service URLs After Deployment

| Service | Local URL | Description |
|---------|-----------|-------------|
| Frontend | http://localhost:3000 | Main dashboard |
| Backend API | http://localhost:8000 | REST API |
| API Docs | http://localhost:8000/docs | Swagger UI |
| Grafana | http://localhost:3001 | Monitoring |
| Prometheus | http://localhost:9090 | Metrics |
| Airflow | http://localhost:8080 | Workflow orchestration |

---

## Quick Commands

```cmd
# Rebuild after code changes
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Reset everything (including database)
docker-compose down -v
```

---

## Need Help?

- Check `docker-compose logs` for errors
- Ensure all ports are available (3000, 8000, 5432, 6379)
- Verify your OpenAI API key is valid
