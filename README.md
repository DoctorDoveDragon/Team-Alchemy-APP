# Team Alchemy APP

A comprehensive academic and team collaboration platform combining modern web technologies with data-driven insights.

## Overview

Team Alchemy APP is a full-stack application scaffold featuring:
- **Frontend**: React + Vite + Tailwind CSS
- **Backend**: FastAPI + SQLModel + PostgreSQL
- **Infrastructure**: Docker Compose, Nginx, Redis
- **CI/CD**: GitHub Actions workflow

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)

### Running with Docker Compose

```bash
# Clone the repository
git clone https://github.com/DoctorDoveDragon/Team-Alchemy-APP.git
cd Team-Alchemy-APP

# Copy environment file and configure secrets
cp .env.example .env
# Edit .env and set JWT_SECRET and other secrets

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

Services will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- PostgreSQL: localhost:5432
- Redis: localhost:6379

### Running Locally

#### Backend

```bash
pip install -r requirements.txt
pip install -e .

# Set environment variables
export DATABASE_URL="postgresql://teamalchemy:teamalchemy@localhost:5432/teamalchemy"
export SECRET_KEY="your-secret-key-here"

# Run the server
uvicorn main:app --reload --port 8000
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at http://localhost:3000

## Project Structure

```
.
├── frontend/              # React + Vite frontend
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── data/         # Sample data
│   │   └── main.jsx      # Entry point
│   └── package.json
├── src/                  # Team Alchemy Python package
│   └── team_alchemy/
│       ├── api/          # API routes
│       ├── data/         # Data models and repository
│       └── ml/           # Machine learning modules
├── main.py               # FastAPI application entry point
├── config/               # Configuration files
├── .github/
│   └── workflows/
│       └── ci.yml        # CI workflow
├── docker-compose.yml    # Docker services
├── Dockerfile            # Production Docker image
├── nginx.conf            # Nginx configuration
└── .env.example          # Environment variables template
```

## Development

### Backend Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test suites
pytest tests/unit/ -v          # Unit tests only
pytest tests/integration/ -v   # Integration tests only
pytest tests/config/ -v        # Configuration tests

# Run with coverage
pytest tests/ -v --cov=src/team_alchemy --cov-report=html

# Run specific test file
pytest tests/config/test_settings.py -v
```

### Debugging

#### Check Application Health

```bash
# Local development
curl http://localhost:8000/healthz

# Production/Railway
curl https://your-app.railway.app/healthz
```

#### View Application Logs

```bash
# Local (Docker Compose)
docker-compose logs -f backend

# Railway CLI
railway logs

# Check specific service logs
docker-compose logs -f postgres
docker-compose logs -f redis
```

#### Common Issues and Solutions

**Database Connection Issues:**
```bash
# Verify DATABASE_URL is set correctly
echo $DATABASE_URL

# Test database connectivity
psql $DATABASE_URL -c "SELECT 1;"

# Initialize database if needed
python -c "from team_alchemy.data.repository import init_db; init_db()"
```

**Port Binding Issues:**
- Ensure PORT environment variable is set correctly
- Check if port is already in use: `lsof -i :8000`
- Railway automatically sets PORT - don't override it

**SECRET_KEY Warnings:**
- In production, always set a secure SECRET_KEY (minimum 32 characters)
- Generate secure key: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- Never commit .env files with production secrets

### Frontend Tests

```bash
cd frontend
npm test
```

### Running CI Locally

The CI workflow runs on push and pull requests. It:
1. Installs backend dependencies
2. Runs backend tests with pytest
3. Installs frontend dependencies
4. Builds frontend application

### Database Migrations

This project uses Alembic for database schema migrations.

#### Create a New Migration

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Add new table or column"

# Or create an empty migration template
alembic revision -m "Description of changes"
```

#### Apply Migrations

```bash
# Upgrade to latest version
alembic upgrade head

# Upgrade to specific revision
alembic upgrade <revision_id>

# Downgrade one revision
alembic downgrade -1
```

#### View Migration History

```bash
# Show current version
alembic current

# Show migration history
alembic history

# Show pending migrations
alembic heads
```

#### Automated Deployment Migration

For production deployments (e.g., Railway), use the migration script:

```bash
python scripts/migrate_database.py
```

This script:
1. Runs all pending Alembic migrations
2. Initializes the database if needed
3. Provides clear status messages

## Environment Variables

Copy `.env.example` to `.env` and configure:

- `SECRET_KEY`: Secret key for JWT tokens and encryption (REQUIRED - must be set by repository owners)
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `ENVIRONMENT`: development/production

**Note**: Secrets are not set in this repository. Repository owners must add SECRET_KEY and other sensitive values.

## API Endpoints

- `GET /healthz` - Health check endpoint
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/documents` - Create document

Full API documentation available at http://localhost:8000/docs

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues and questions, please use the [GitHub issue tracker](https://github.com/DoctorDoveDragon/Team-Alchemy-APP/issues).

---

**Team Alchemy APP** - Modern full-stack application scaffold
