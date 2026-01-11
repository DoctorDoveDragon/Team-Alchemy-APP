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
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"API Port: {settings.api_port}")
    logger.info(f"CORS Origins: {settings.cors_origins}")
    
    init_db()
    logger.info("Database initialized successfully")
    
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


@app.get("/healthz")
async def health():
    """Health check endpoint for Railway."""
    logger.debug("Health check endpoint called")
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "healthy",
        "environment": settings.environment,
        "docs": "/docs",
    }


@app.get("/health")
async def health_legacy():
    """Legacy health check endpoint."""
    logger.debug("Legacy health check endpoint called")
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
    }


# Setup static file serving for frontend after all API routes
def setup_static_files():
    """Setup static file serving for the frontend."""
    static_dir = Path(__file__).parent / "static"
    logger.info(f"Checking for static files at: {static_dir}")
    logger.info(f"Static directory exists: {static_dir.exists()}")
    
    if static_dir.exists():
        logger.info(f"Setting up static file serving from {static_dir.resolve()}")
        
        # List contents for debugging
        try:
            contents = list(static_dir.iterdir())
            logger.info(f"Static directory contains {len(contents)} items: {[p.name for p in contents]}")
        except Exception as e:
            logger.error(f"Error listing static directory contents: {e}")
        
        # Cache resolved static directory path for security checks
        resolved_static_dir = static_dir.resolve()
        
        # Mount assets directory if it exists
        assets_dir = static_dir / "assets"
        if assets_dir.exists():
            logger.info(f"Mounting assets directory from {assets_dir}")
            app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="static-assets")
        else:
            logger.warning(f"Assets directory not found at {assets_dir}")
        
        # Check for index.html
        index_path = static_dir / "index.html"
        if index_path.exists():
            logger.info(f"Found index.html at {index_path}")
        else:
            logger.warning(f"index.html not found at {index_path}")
        
        @app.get("/{full_path:path}")
        async def serve_frontend(full_path: str):
            """Serve frontend application
            
            Note: This catch-all route is registered after all API routes to ensure
            API routes take precedence. Any future API routes should be registered
            before calling setup_static_files() to ensure they are not overridden.
            """
            logger.debug(f"Frontend request for: /{full_path}")
            
            # Prevent path traversal attacks
            try:
                file_path = (static_dir / full_path).resolve()
                # Ensure the resolved path is within static_dir
                file_path.relative_to(resolved_static_dir)
            except ValueError:
                # Path is outside static directory - serve index.html for client-side routing
                logger.debug(f"Path outside static dir or not found: {full_path}, serving index.html")
                index_path = static_dir / "index.html"
                if index_path.exists():
                    return FileResponse(index_path)
                logger.error("index.html not found, cannot serve frontend")
                return {"message": "Frontend not built", "error": "index.html not found"}
            
            # If requesting a file that exists, serve it
            if file_path.is_file():
                logger.debug(f"Serving file: {file_path}")
                return FileResponse(file_path)
            
            # Otherwise, serve index.html for client-side routing
            logger.debug(f"File not found: {full_path}, serving index.html for SPA routing")
            index_path = static_dir / "index.html"
            if index_path.exists():
                return FileResponse(index_path)
            
            logger.error("index.html not found, cannot serve frontend")
            return {"message": "Frontend not built", "error": "index.html not found"}
            
        logger.info("Static file serving configured successfully")
        
    else:
        logger.warning(f"Static directory not found at {static_dir}, setting up fallback root route")
        
        @app.get("/")
        async def root():
            """Root endpoint when no static files are available."""
            logger.info("Root endpoint called - no static files available")
            return {
                "name": settings.app_name,
                "version": settings.app_version,
                "status": "running",
                "environment": settings.environment,
                "docs": "/docs",
                "api_docs": "/redoc",
                "message": "API is running. Frontend not built yet.",
                "endpoints": {
                    "health": "/healthz",
                    "api": settings.api_prefix,
                    "docs": "/docs"
                }
            }
        
        logger.info("Fallback root route configured")


# Call setup_static_files after all API routes are registered
logger.info("Configuring static file serving...")
setup_static_files()
logger.info("Application setup complete")


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting uvicorn server on {settings.api_host}:{settings.api_port}")
    
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
