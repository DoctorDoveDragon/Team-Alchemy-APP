# Stage 1: Build frontend
FROM node:18-alpine AS frontend-build

WORKDIR /frontend

# Copy frontend package files
COPY frontend/package*.json ./
RUN npm ci

# Copy frontend source and build
COPY frontend/ ./
RUN npm run build

# Stage 2: Backend + serve frontend
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
# gcc: Required for building Python packages with C extensions
# postgresql-client: Required for psycopg2-binary to connect to PostgreSQL databases
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy setup files and source code
COPY pyproject.toml setup.py ./
COPY src/ ./src/
COPY config/ ./config/
COPY main.py ./

# Install the team_alchemy package
RUN pip install --no-cache-dir -e .

# Copy built frontend from previous stage
COPY --from=frontend-build /frontend/dist ./static

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port (Railway will override with $PORT)
EXPOSE 8000

# Use shell form to properly expand $PORT environment variable at runtime
# Railway sets PORT dynamically, so we need shell expansion
CMD sh -c "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"
