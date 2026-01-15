# Railway Deployment Guide for Team Alchemy

## Prerequisites

- GitHub account with access to the Team-Alchemy-APP repository
- Railway account (sign up at https://railway.app)
- Railway CLI installed (optional, for local testing)

## Deployment Steps

### 1. Connect Repository to Railway

1. Log in to Railway (https://railway.app)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Authorize Railway to access your GitHub account
5. Select the `Team-Alchemy-APP` repository
6. Railway will automatically detect the project and create a service

### 2. Configure Environment Variables

In the Railway dashboard, navigate to your project's Variables tab and set:

**Required Variables:**

```bash
# Security
SECRET_KEY=<generate-a-secure-32+-character-string>

# Database (if using external database)
DATABASE_URL=postgresql://user:password@host:port/database

# Application
ENVIRONMENT=production
```

**Optional Variables:**

```bash
# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# CORS (adjust as needed)
CORS_ORIGINS=["https://yourdomain.com"]

# Redis (if using)
REDIS_URL=redis://host:port
```

**Generate SECRET_KEY:**

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. Database Setup

Railway automatically provisions a PostgreSQL database. To use it:

1. In Railway dashboard, click "New" → "Database" → "Add PostgreSQL"
2. Railway will automatically set the `DATABASE_URL` variable
3. The database will be linked to your service

**Alternative: Use SQLite (for testing only):**

```bash
DATABASE_URL=sqlite:///./teamalchemy.db
```

### 4. Build Configuration

The repository includes these files for Railway deployment:

**railway.json:**
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "sh -c 'python scripts/migrate_database.py && uvicorn main:app --host 0.0.0.0 --port $PORT'",
    "healthcheckPath": "/healthz",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

**Dockerfile** (alternative to railway.json):

The project includes a Dockerfile for containerized deployment. Railway will use this if railway.json is not present.

### 5. Frontend Build

The frontend is built during deployment and served from the `/static` directory.

To build manually:

```bash
cd frontend
npm install
npm run build
cd ..
cp -r frontend/dist static
```

Railway automatically runs these commands during deployment based on the build configuration.

### 6. Database Migrations

Database migrations run automatically on deployment via the `scripts/migrate_database.py` script.

**Manual migration:**

```bash
railway run python scripts/migrate_database.py
```

Or using Alembic directly:

```bash
railway run alembic upgrade head
```

### 7. Health Checks

Railway monitors the `/healthz` endpoint to ensure the application is running correctly.

**Test health endpoint:**

```bash
curl https://your-app.railway.app/healthz
```

Expected response:

```json
{
  "status": "healthy",
  "name": "Team Alchemy",
  "version": "0.1.0",
  "environment": "production",
  "timestamp": "2026-01-15T14:00:00.000000"
}
```

## Troubleshooting

### PORT Issue (PR #44)

**Problem:** Application not binding to the correct port.

**Solution:** Railway automatically sets the `PORT` environment variable. The application reads this in `main.py`:

```python
if __name__ == "__main__":
    run_port = int(os.environ.get("PORT", settings.api_port))
    uvicorn.run("main:app", host="0.0.0.0", port=run_port)
```

Ensure you don't override the `PORT` variable in Railway settings.

### Database Connection Issues

**Problem:** Application can't connect to database.

**Solution:**

1. Verify `DATABASE_URL` is set correctly
2. Check database service is running
3. Test connection:

```bash
railway run python -c "from team_alchemy.data.repository import init_db; init_db()"
```

### Build Failures

**Problem:** Build fails during deployment.

**Solution:**

1. Check Railway build logs
2. Verify all dependencies are in `requirements.txt`
3. Ensure Python version compatibility (3.9+)

### Static Files Not Serving

**Problem:** Frontend not loading.

**Solution:**

1. Verify frontend build completed successfully
2. Check `static` directory exists with `index.html`
3. Review build logs for frontend build errors

### SECRET_KEY Warnings

**Problem:** Application warns about insecure SECRET_KEY.

**Solution:**

1. Generate a secure key: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
2. Set in Railway Variables (minimum 32 characters)
3. Never commit SECRET_KEY to version control

## Monitoring and Logs

### View Logs

**Railway Dashboard:**
1. Navigate to your project
2. Click on the service
3. Click "Logs" tab

**Railway CLI:**
```bash
railway logs
```

**Filter logs:**
```bash
railway logs --filter "ERROR"
```

### Metrics

Railway provides built-in metrics:
- CPU usage
- Memory usage
- Network traffic
- Request count

Access via the "Metrics" tab in Railway dashboard.

## Scaling

### Vertical Scaling

Upgrade your Railway plan for more resources:
- Hobby: $5/month (512MB RAM, 1 vCPU)
- Pro: $20/month (8GB RAM, 8 vCPU)

### Horizontal Scaling

Railway supports horizontal scaling:

1. Go to Settings → Scaling
2. Adjust replica count
3. Railway automatically load balances

## Backup and Recovery

### Database Backups

**Automatic backups:**
Railway automatically backs up PostgreSQL databases daily.

**Manual backup:**
```bash
railway run pg_dump $DATABASE_URL > backup.sql
```

**Restore from backup:**
```bash
railway run psql $DATABASE_URL < backup.sql
```

### Configuration Backup

Export environment variables:

```bash
railway variables --json > railway-vars.json
```

## Custom Domain

1. Go to Settings → Domains
2. Click "Add Domain"
3. Enter your custom domain
4. Add CNAME record to your DNS:
   - Name: `subdomain` (or `@` for root)
   - Value: `<your-app>.railway.app`

## Security Best Practices

1. **Always use HTTPS:** Railway provides free SSL certificates
2. **Set strong SECRET_KEY:** Minimum 32 characters, cryptographically random
3. **Use environment variables:** Never commit secrets to repository
4. **Enable CORS properly:** Restrict to your domain in production
5. **Keep dependencies updated:** Regularly run `pip list --outdated`
6. **Monitor logs:** Watch for suspicious activity
7. **Use production database:** Don't use SQLite in production

## Production Checklist

- [ ] SECRET_KEY set (32+ characters)
- [ ] DATABASE_URL configured (PostgreSQL recommended)
- [ ] ENVIRONMENT=production
- [ ] CORS_ORIGINS restricted to your domain
- [ ] Health check passing (/healthz returns 200)
- [ ] Database migrations applied
- [ ] Frontend built and static files present
- [ ] Logs monitored for errors
- [ ] Custom domain configured (optional)
- [ ] SSL certificate active
- [ ] Backup strategy in place

## Support

For Railway-specific issues:
- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Railway Support: support@railway.app

For Team Alchemy issues:
- GitHub Issues: https://github.com/DoctorDoveDragon/Team-Alchemy-APP/issues
