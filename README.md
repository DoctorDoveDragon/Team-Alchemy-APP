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
- Backend API: http://localhost:5000
- API Documentation: http://localhost:5000/docs
- PostgreSQL: localhost:5432
- Redis: localhost:6379

### Running Locally

#### Backend

```bash
cd server
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Set environment variables
export DATABASE_URL="postgresql://teamalchemy:teamalchemy@localhost:5432/teamalchemy"
export JWT_SECRET="your-secret-key-here"

# Run the server
uvicorn app.main:app --reload --port 5000
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
├── server/               # FastAPI backend
│   ├── app/
│   │   ├── main.py       # FastAPI app
│   │   ├── models.py     # SQLModel models
│   │   ├── routes.py     # API routes
│   │   └── auth.py       # Authentication
│   └── tests/
├── .github/
│   └── workflows/
│       └── ci.yml        # CI workflow
├── docker-compose.yml    # Docker services
├── nginx.conf            # Nginx configuration
└── .env.example          # Environment variables template
```

## Development

### Backend Tests

```bash
cd server
pytest tests/
```

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

## Environment Variables

Copy `.env.example` to `.env` and configure:

- `JWT_SECRET`: Secret key for JWT tokens (REQUIRED - must be set by repository owners)
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `ENVIRONMENT`: development/production

**Note**: Secrets are not set in this repository. Repository owners must add JWT_SECRET and other sensitive values.

## API Endpoints

- `GET /healthz` - Health check endpoint
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/documents` - Create document

Full API documentation available at http://localhost:5000/docs

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues and questions, please use the [GitHub issue tracker](https://github.com/DoctorDoveDragon/Team-Alchemy-APP/issues).

---

**Team Alchemy APP** - Modern full-stack application scaffold
