"""
Main FastAPI application entry point.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from pathlib import Path

from team_alchemy.api.routes import assessment, analysis, teams
from team_alchemy.api.middleware.auth import AuthMiddleware
from team_alchemy.api.middleware.validation import ValidationMiddleware
from team_alchemy.data.repository import init_db
from config.settings import get_settings
from config.logging_config import setup_logging

settings = get_settings()
logger = setup_logging(settings.log_level, settings.log_format)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting Team Alchemy application...")
    init_db()
    logger.info("Database initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Team Alchemy application...")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="A comprehensive team dynamics and psychological assessment platform",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.add_middleware(ValidationMiddleware, max_request_size=10 * 1024 * 1024)

# Include routers
app.include_router(
    assessment.router,
    prefix=settings.api_prefix,
)
app.include_router(
    analysis.router,
    prefix=settings.api_prefix,
)
app.include_router(
    teams.router,
    prefix=settings.api_prefix,
)


@app.get("/health")
@app.get("/healthz")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.app_version,
    }


@app.get("/api")
async def api_root():
    """API root endpoint."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
    }


# Serve static files (frontend) - must be registered after API routes
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    # Cache resolved static directory path for security checks
    resolved_static_dir = static_dir.resolve()
    
    # Mount assets directory if it exists
    assets_dir = static_dir / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="static-assets")
    
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        """Serve frontend application
        
        Note: This catch-all route is registered after all API routes to ensure
        API routes take precedence. Any future API routes should be registered
        before this catch-all handler.
        """
        # Prevent path traversal attacks
        try:
            file_path = (static_dir / full_path).resolve()
            # Ensure the resolved path is within static_dir (Python 3.9+)
            if not file_path.is_relative_to(resolved_static_dir):
                # Path is outside static directory
                index_path = static_dir / "index.html"
                if index_path.exists():
                    return FileResponse(index_path)
                return {"message": "Frontend not built"}
        except (OSError, ValueError):
            # Filesystem error
            index_path = static_dir / "index.html"
            if index_path.exists():
                return FileResponse(index_path)
            return {"message": "Frontend not built"}
        
        # If requesting a file that exists, serve it
        if file_path.is_file():
            return FileResponse(file_path)
        
        # Otherwise, serve index.html for client-side routing
        index_path = static_dir / "index.html"
        if index_path.exists():
            return FileResponse(index_path)
        
        return {"message": "Frontend not built"}
else:
    # If static directory doesn't exist, serve API info at root
    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "name": settings.app_name,
            "version": settings.app_version,
            "status": "running",
            "docs": "/docs",
        }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
