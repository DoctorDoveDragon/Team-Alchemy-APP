# Railway Deployment Guide

This guide will help you deploy the Team Alchemy application to Railway.

## Prerequisites

- A [Railway](https://railway.app/) account
- GitHub repository connected to Railway
- Basic understanding of environment variables

## Quick Start

1. **Connect your repository to Railway**
   - Log in to Railway
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your Team Alchemy repository

2. **Configure Environment Variables**
   - Railway will automatically set the `PORT` variable
   - You need to configure the following variables in Railway's dashboard

## Required Environment Variables

### Essential Variables

These variables **must** be set for production deployment:

```bash
# Security - CRITICAL: Generate a secure random string
SECRET_KEY=your-secure-secret-key-here

# Environment
ENVIRONMENT=production

# CORS - Update with your actual frontend domain
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### Database Configuration

Railway provides PostgreSQL as a service. To use it:

1. **Add PostgreSQL Service**
   - In your Railway project, click "New" → "Database" → "Add PostgreSQL"
   - Railway will automatically create a `DATABASE_URL` environment variable

2. **Database URL Format**
   ```
   DATABASE_URL=postgresql://user:password@host:port/dbname
   ```
   
   Railway automatically provides this variable when you add PostgreSQL.

### Redis Configuration (Optional)

If using Celery for background tasks:

1. **Add Redis Service**
   - In your Railway project, click "New" → "Database" → "Add Redis"
   - Railway will automatically create a `REDIS_URL` environment variable

2. **Redis Variables** (automatically configured)
   ```bash
   REDIS_URL=redis://default:password@host:port
   CELERY_BROKER_URL=${REDIS_URL}
   CELERY_RESULT_BACKEND=${REDIS_URL}
   ```

### Optional Variables

```bash
# Application
APP_NAME=Team Alchemy
APP_VERSION=0.1.0
DEBUG=False

# API Configuration
API_PREFIX=/api/v1

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# ML Features
MODEL_PATH=./models
ENABLE_ML=True
ENABLE_SHADOW_WORK=True
ENABLE_RECOMMENDATIONS=True
MAX_RECOMMENDATIONS=10

# Database
DATABASE_ECHO=False

# Security
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Deployment Configuration Files

The repository includes the following Railway-specific files:

### `railway.json`
Contains Railway deployment configuration:
- Build settings (using Nixpacks)
- Start command
- Health check endpoint (`/health`)
- Restart policy

### `Procfile`
Defines the web service start command:
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

## Database Setup

### Initial Migration

After deploying, you need to initialize the database:

1. **Using Railway CLI**
   ```bash
   railway run python -c "from team_alchemy.data.repository import init_db; init_db()"
   ```

2. **Or connect to your Railway environment and run**
   ```bash
   python scripts/setup_database.py
   ```

### Database Migrations

For schema updates, consider using Alembic:

```bash
# Generate migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head
```

## Health Checks

The application provides a health check endpoint at `/health` that Railway uses to monitor the service:

```bash
curl https://your-app.railway.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "0.1.0"
}
```

## Deployment Steps

### Step 1: Prepare Repository

Ensure your repository has:
- [x] `railway.json` - Railway configuration
- [x] `Procfile` - Service start command
- [x] `requirements.txt` - Python dependencies (including `psycopg2-binary`)
- [x] `.env.example` - Environment variable template

### Step 2: Create Railway Project

1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Authenticate and select your repository

### Step 3: Add Database Services

1. **PostgreSQL**:
   - Click "New" in your project
   - Select "Database" → "Add PostgreSQL"
   - Railway automatically sets `DATABASE_URL`

2. **Redis** (if needed):
   - Click "New" in your project
   - Select "Database" → "Add Redis"
   - Railway automatically sets `REDIS_URL`

### Step 4: Configure Environment Variables

1. Click on your service in Railway
2. Go to "Variables" tab
3. Add the required variables (see above)
4. Click "Add" for each variable

**Critical variables to set:**
- `SECRET_KEY` - Generate a secure random string
- `ENVIRONMENT` - Set to `production`
- `CORS_ORIGINS` - Your frontend domain(s)

### Step 5: Deploy

Railway automatically deploys when you:
- Push to your connected Git branch
- Change environment variables
- Manually trigger a deployment

Monitor the deployment in the "Deployments" tab.

### Step 6: Verify Deployment

1. **Check health endpoint**:
   ```bash
   curl https://your-app.railway.app/health
   ```

2. **Check API documentation**:
   ```
   https://your-app.railway.app/docs
   ```

3. **View logs**:
   - In Railway dashboard, click on your service
   - Go to "Logs" tab to see application logs

## Frontend Deployment

### Option 1: Separate Frontend Service

Deploy the frontend as a separate Railway service:

1. Create a new service for the frontend
2. Set `VITE_API_URL` to your backend Railway URL
3. Configure build settings for Vite

### Option 2: Static Files with Backend

Serve frontend static files from FastAPI:

```python
from fastapi.staticfiles import StaticFiles

# After building frontend
app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")
```

Update `railway.json` to include frontend build:
```json
{
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "cd frontend && npm install && npm run build && cd .."
  }
}
```

## Troubleshooting

### Database Connection Issues

If you see database connection errors:

1. Verify `DATABASE_URL` is set correctly
2. Check PostgreSQL service is running
3. Ensure `psycopg2-binary` is in `requirements.txt`

### Port Binding Issues

Railway automatically sets the `PORT` variable. Ensure:
- `config/settings.py` reads from `PORT` environment variable
- `main.py` uses `settings.api_port`

### CORS Errors

Update `CORS_ORIGINS` to include your frontend domain:
```bash
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### Migration Issues

If database tables aren't created:

```bash
# Use Railway CLI to run init
railway run python -c "from team_alchemy.data.repository import init_db; init_db()"
```

## Monitoring and Logs

### View Logs

In Railway dashboard:
1. Click on your service
2. Go to "Logs" tab
3. Filter by log level if needed

### Metrics

Railway provides:
- CPU usage
- Memory usage
- Network traffic
- Request metrics

Access these in the "Metrics" tab.

## Scaling

Railway supports both vertical and horizontal scaling:

1. **Vertical Scaling**: Upgrade your plan for more resources
2. **Horizontal Scaling**: Add multiple instances (on paid plans)

## Security Best Practices

1. **Never commit `.env` files**
   - Use `.env.example` as template
   - Set actual values in Railway dashboard

2. **Use strong SECRET_KEY**
   ```python
   # Generate a secure key:
   import secrets
   print(secrets.token_urlsafe(32))
   ```

3. **Limit CORS origins**
   - Don't use `["*"]` in production
   - Specify exact frontend domains

4. **Keep dependencies updated**
   ```bash
   pip list --outdated
   pip install --upgrade package-name
   ```

## Cost Optimization

- Use Railway's free tier for development
- Monitor usage in the "Usage" tab
- Consider using Railway's sleep mode for staging environments
- Optimize database queries to reduce resource usage

## Additional Resources

- [Railway Documentation](https://docs.railway.app/)
- [Railway CLI](https://docs.railway.app/develop/cli)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [PostgreSQL Best Practices](https://wiki.postgresql.org/wiki/Don't_Do_This)

## Support

For Railway-specific issues:
- [Railway Discord](https://discord.gg/railway)
- [Railway Help Center](https://help.railway.app/)

For Team Alchemy application issues:
- Open an issue in the GitHub repository
- Check existing documentation in `/docs`
