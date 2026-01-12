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

#### Manual Migration
```bash
# Generate migration from model changes
alembic revision --autogenerate -m "description"

# Apply migration via Railway CLI
railway run alembic upgrade head
```

#### Automated Migration (Recommended)

Add a migration step to your deployment process:

**Option 1: Add to railway.json**
```json
{
  "build": {
    "builder": "DOCKERFILE"
  },
  "deploy": {
    "healthcheckPath": "/healthz",
    "healthcheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10,
    "startCommand": "python scripts/migrate_database.py && uvicorn main:app --host 0.0.0.0 --port $PORT"
  }
}
```

**Option 2: Run migration script manually**
```bash
# Via Railway CLI
railway run python scripts/migrate_database.py

# Then restart the service
railway restart
```

The `migrate_database.py` script:
- Runs all pending Alembic migrations
- Initializes database if needed
- Provides clear status messages
- Safe to run multiple times (idempotent)

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

**Symptoms:**
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solutions:**

1. **Verify DATABASE_URL is set correctly**
   ```bash
   # In Railway dashboard, check Variables tab
   # Ensure DATABASE_URL is present and properly formatted
   ```

2. **Check PostgreSQL service is running**
   - In Railway dashboard, verify PostgreSQL service status
   - Check service logs for errors

3. **Ensure psycopg2-binary is installed**
   ```bash
   # Verify in requirements.txt
   grep psycopg2-binary requirements.txt
   ```

4. **Test database connection manually**
   ```bash
   railway run python -c "from team_alchemy.data.repository import init_db; init_db()"
   ```

5. **Check database initialization**
   ```bash
   # View deployment logs to see if database init succeeded
   # Look for "✓ Database initialized successfully"
   ```

### Port Binding Issues

**Symptoms:**
```
Error: Address already in use
uvicorn.error: Can't bind to port
```

**Solutions:**

Railway automatically sets the `PORT` variable. Ensure:

1. **Don't manually set PORT in Railway variables**
   - Railway provides this automatically
   - Your app should read from `os.getenv("PORT")`

2. **Verify settings.py reads PORT correctly**
   ```python
   # The parse_port validator in settings.py handles this
   # PORT takes priority over API_PORT
   ```

3. **Check application startup logs**
   ```
   Look for: "API Port: <port_number>"
   ```

4. **Verify railway.json configuration**
   ```json
   {
     "deploy": {
       "healthcheckPath": "/healthz"
     }
   }
   ```

### CORS Errors

**Symptoms:**
```
Access to fetch at 'https://api.example.com' from origin 'https://example.com' 
has been blocked by CORS policy
```

**Solutions:**

1. **Update CORS_ORIGINS environment variable**
   ```bash
   CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
   ```

2. **Don't use wildcards in production**
   ```bash
   # Bad (insecure):
   CORS_ORIGINS=*
   
   # Good (secure):
   CORS_ORIGINS=https://myapp.com,https://www.myapp.com
   ```

3. **Include all necessary origins**
   - Main domain
   - www subdomain
   - Any other subdomains that need access

### Environment Variable Validation Errors

**Symptoms:**
```
ValueError: Environment variable validation failed:
  - SECRET_KEY is set to default value
```

**Solutions:**

1. **Set a secure SECRET_KEY**
   ```bash
   # Generate a secure key
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   
   # Set in Railway dashboard Variables tab
   SECRET_KEY=<generated_key>
   ```

2. **Ensure minimum key length (32 characters)**
   ```bash
   # The key must be at least 32 characters long for production
   ```

3. **Check environment variable in Railway**
   - Go to Variables tab in Railway dashboard
   - Verify SECRET_KEY is set
   - Restart deployment after adding the variable

### Static Files Not Serving

**Symptoms:**
```
404 Not Found for static assets
Frontend not loading
```

**Solutions:**

1. **Build frontend before deployment**
   ```bash
   # Add to railway.json or Dockerfile
   cd frontend && npm install && npm run build
   ```

2. **Verify static directory exists**
   ```bash
   # Check if static/index.html exists after build
   ls -la static/
   ```

3. **Check application logs**
   ```
   Look for: "✓ Static file serving configured successfully"
   Or: "STATIC DIRECTORY NOT FOUND"
   ```

4. **Verify build configuration**
   ```bash
   # Check that frontend build outputs to /static directory
   # Update frontend/vite.config.js if needed
   ```

### Migration Issues

**Symptoms:**
```
Table doesn't exist
Column not found
alembic.util.exc.CommandError
```

**Solutions:**

1. **Run automated migration script**
   ```bash
   railway run python scripts/migrate_database.py
   ```

2. **Check migration status**
   ```bash
   # Via Railway CLI
   railway run alembic current
   
   # View migration history
   railway run alembic history
   ```

3. **Apply migrations manually**
   ```bash
   # Upgrade to latest version
   railway run alembic upgrade head
   
   # Downgrade if needed
   railway run alembic downgrade -1
   ```

4. **If migrations fail, try database initialization**
   ```bash
   railway run python -c "from team_alchemy.data.repository import init_db; init_db()"
   ```

5. **Check if tables were created**
   ```bash
   # Connect to Railway PostgreSQL
   railway connect postgres
   
   # List tables
   \dt
   
   # Describe a table
   \d table_name
   ```

6. **Generate initial migration (first time only)**
   ```bash
   # If no migrations exist
   alembic revision --autogenerate -m "Initial migration"
   
   # Apply it
   railway run alembic upgrade head
   ```

7. **Reset database (CAUTION: destroys all data)**
   ```bash
   # Only in development/staging!
   railway run alembic downgrade base
   railway run alembic upgrade head
   ```

### Application Crashes on Startup

**Symptoms:**
```
Application exits immediately after start
Health check failing
```

**Solutions:**

1. **Check deployment logs**
   - Railway Dashboard → Service → Deployments → Select deployment → View logs
   - Look for error messages and stack traces

2. **Common startup errors:**
   - Missing environment variables (SECRET_KEY, DATABASE_URL)
   - Database connection failures
   - Invalid configuration values
   - Import errors or missing dependencies

3. **Verify all required environment variables**
   ```bash
   # Critical variables for production:
   SECRET_KEY=<secure-key>
   DATABASE_URL=<provided-by-railway>
   ENVIRONMENT=production
   ```

4. **Test locally with production-like settings**
   ```bash
   # Set environment to production
   export ENVIRONMENT=production
   export SECRET_KEY=<32-char-key>
   export DATABASE_URL=<your-db-url>
   
   # Run application
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

5. **Check dependencies are installed**
   ```bash
   # Verify requirements.txt includes all dependencies
   # Railway installs from this file during build
   ```

### Health Check Failures

**Symptoms:**
```
Railway shows service as unhealthy
Deployment keeps restarting
```

**Solutions:**

1. **Verify health endpoint responds**
   ```bash
   curl https://your-app.railway.app/healthz
   ```

2. **Expected health check response**
   ```json
   {
     "status": "healthy",
     "name": "Team Alchemy",
     "version": "0.1.0",
     "environment": "production",
     "timestamp": "2024-01-01T00:00:00"
   }
   ```

3. **Check railway.json health check configuration**
   ```json
   {
     "deploy": {
       "healthcheckPath": "/healthz",
       "healthcheckTimeout": 300,
       "restartPolicyType": "ON_FAILURE"
     }
   }
   ```

4. **Increase health check timeout if needed**
   - Default is 300 seconds
   - Increase if database initialization takes longer

### Logging and Monitoring

**View Real-time Logs:**
```bash
# Railway CLI
railway logs

# Or in Railway Dashboard
# Service → Logs tab
```

**Key Log Messages to Look For:**

✓ Success indicators:
```
✓ Environment variables validated successfully
✓ Database initialized successfully
✓ Static file serving configured successfully
```

✗ Error indicators:
```
✗ Environment validation failed
✗ Database initialization failed
✗ Static directory not found
```

**Log Levels:**
- Production: INFO (reduces noise from third-party libraries)
- Development: DEBUG (shows all details)

**Filter Logs by Level:**
```bash
# In Railway logs, use the filter dropdown
# Select: Error, Warning, Info, or Debug
```

### Performance Issues

**Symptoms:**
- Slow response times
- Timeouts
- High memory usage

**Solutions:**

1. **Check Railway metrics**
   - Service → Metrics tab
   - Monitor CPU, Memory, Network

2. **Optimize database queries**
   ```python
   # Enable query logging temporarily
   DATABASE_ECHO=True
   ```

3. **Scale resources**
   - Upgrade Railway plan for more resources
   - Enable horizontal scaling (paid plans)

4. **Add database indexes**
   ```sql
   -- For frequently queried columns
   CREATE INDEX idx_column_name ON table_name(column_name);
   ```

5. **Implement caching**
   - Use Redis for frequently accessed data
   - Cache API responses where appropriate

### Getting Help

If problems persist:

1. **Check Railway status**
   - https://status.railway.app/

2. **Review Railway documentation**
   - https://docs.railway.app/

3. **Railway community support**
   - Discord: https://discord.gg/railway
   - Help Center: https://help.railway.app/

4. **Application issues**
   - GitHub Issues: https://github.com/DoctorDoveDragon/Team-Alchemy-APP/issues
   - Include: deployment logs, error messages, environment details

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
