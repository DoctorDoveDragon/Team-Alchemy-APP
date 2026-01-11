"""
Main FastAPI application entry point.
"""

import os
import re
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from pathlib import Path
from datetime import datetime

from team_alchemy.api.routes import assessment, analysis, teams
from team_alchemy.api.middleware.auth import AuthMiddleware
from team_alchemy.api.middleware.validation import ValidationMiddleware
from team_alchemy.data.repository import init_db
from config.settings import get_settings
from config.logging_config import setup_logging

settings = get_settings()
logger = setup_logging(settings.log_level, settings.log_format)

# Log application startup information
logger.info("="*60)
logger.info("STARTING TEAM ALCHEMY APPLICATION")
logger.info("="*60)
logger.info(f"App Name: {settings.app_name}")
logger.info(f"Version: {settings.app_version}")
logger.info(f"Environment: {settings.environment}")
logger.info(f"Debug Mode: {settings.debug}")
logger.info(f"API Host: {settings.api_host}")
logger.info(f"API Port: {settings.api_port}")
logger.info(f"API Prefix: {settings.api_prefix}")
logger.info(f"CORS Origins: {settings.cors_origins}")
# Sanitize database URL to hide credentials
db_url_sanitized = re.sub(r'://[^:]*:[^@]*@', '://***:***@', settings.database_url) if '@' in settings.database_url else settings.database_url
logger.info(f"Database URL: {db_url_sanitized}")
logger.info(f"Log Level: {settings.log_level}")
logger.info("="*60)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("="*60)
    logger.info("LIFESPAN STARTUP EVENT")
    logger.info("="*60)
    logger.info("Starting Team Alchemy application...")
    
    try:
        init_db()
        logger.info("✓ Database initialized successfully")
    except Exception as e:
        logger.error(f"✗ Database initialization failed: {e}", exc_info=True)
        raise
    
    logger.info("="*60)
    
    yield
    
    # Shutdown
    logger.info("="*60)
    logger.info("LIFESPAN SHUTDOWN EVENT")
    logger.info("Shutting down Team Alchemy application...")
    logger.info("="*60)


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
async def healthz():
    """Health check endpoint for Railway."""
    logger.debug("Health check called at /healthz")
    return {
        "status": "healthy",
        "name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/health")
async def health_legacy():
    """Legacy health check endpoint."""
    logger.debug("Health check called at /health (legacy)")
    return {
        "status": "running",
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
    }


@app.get("/api/v1/debug/info")
async def debug_info():
    """Debug endpoint to check application configuration (disable in production)."""
    if settings.environment.lower() == "production":
        raise HTTPException(status_code=404, detail="Not found")
    
    static_dir = Path(__file__).parent / "static"
    
    return {
        "environment": settings.environment,
        "debug": settings.debug,
        "api_port": settings.api_port,
        "api_prefix": settings.api_prefix,
        "port_env": os.getenv("PORT"),
        "railway_env": os.getenv("RAILWAY_ENVIRONMENT"),
        "static_dir_exists": static_dir.exists(),
        "static_dir_path": str(static_dir),
        "static_files": list(str(f) for f in static_dir.glob("*")) if static_dir.exists() else [],
        "cwd": os.getcwd(),
        "python_path": os.getenv("PYTHONPATH"),
    }


# Setup static file serving for frontend after all API routes
def setup_static_files():
    """Setup static file serving for the frontend."""
    static_dir = Path(__file__).parent / "static"
    
    logger.info("="*60)
    logger.info("SETTING UP STATIC FILE SERVING")
    logger.info("="*60)
    logger.info(f"Static directory path: {static_dir}")
    logger.info(f"Static directory exists: {static_dir.exists()}")
    
    if static_dir.exists():
        logger.info(f"Static directory resolved to: {static_dir.resolve()}")
        
        # List contents
        try:
            contents = list(static_dir.iterdir())
            logger.info(f"Static directory contains {len(contents)} items:")
            for item in contents[:10]:  # Log first 10 items
                logger.info(f"  - {item.name} ({'dir' if item.is_dir() else 'file'})")
            if len(contents) > 10:
                logger.info(f"  ... and {len(contents) - 10} more items")
        except Exception as e:
            logger.error(f"Error listing static directory: {e}")
        
        # Cache resolved static directory path for security checks
        resolved_static_dir = static_dir.resolve()
        
        # Mount assets directory if it exists
        assets_dir = static_dir / "assets"
        if assets_dir.exists():
            logger.info(f"Mounting assets directory: {assets_dir}")
            app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="static-assets")
        else:
            logger.warning(f"Assets directory not found: {assets_dir}")
        
        # Check for index.html
        index_path = static_dir / "index.html"
        if index_path.exists():
            logger.info(f"✓ Found index.html at {index_path}")
        else:
            logger.warning(f"✗ index.html NOT FOUND at {index_path}")
        
        @app.get("/{full_path:path}")
        async def serve_frontend(full_path: str):
            """Serve frontend application
            
            Note: This catch-all route is registered after all API routes to ensure
            API routes take precedence. Any future API routes should be registered
            before calling setup_static_files() to ensure they are not overridden.
            """
            logger.debug(f"Serving static file request: {full_path}")
            
            # Prevent path traversal attacks
            try:
                file_path = (static_dir / full_path).resolve()
                # Ensure the resolved path is within static_dir
                file_path.relative_to(resolved_static_dir)
            except ValueError:
                # Path is outside static directory - serve index.html for client-side routing
                logger.debug(f"Path outside static dir, serving index.html for: {full_path}")
                index_path = static_dir / "index.html"
                if index_path.exists():
                    return FileResponse(index_path)
                logger.error(f"index.html not found at {index_path}")
                return {"message": "Frontend not built"}
            
            # If requesting a file that exists, serve it
            if file_path.is_file():
                logger.debug(f"Serving file: {file_path}")
                return FileResponse(file_path)
            
            # Otherwise, serve index.html for client-side routing
            logger.debug(f"File not found, serving index.html for SPA routing: {full_path}")
            index_path = static_dir / "index.html"
            if index_path.exists():
                return FileResponse(index_path)
            
            logger.error(f"Cannot serve {full_path}, index.html not found")
            return {"message": "Frontend not built"}
        
        logger.info("✓ Static file serving configured successfully")
        logger.info("="*60)
    else:
        logger.warning("="*60)
        logger.warning(f"STATIC DIRECTORY NOT FOUND: {static_dir}")
        logger.warning("Frontend will NOT be served!")
        logger.warning("="*60)
        
        @app.get("/")
        async def root():
            """Root endpoint when no static files are available."""
            logger.debug("Root endpoint called (no static files)")
            return {
                "name": settings.app_name,
                "version": settings.app_version,
                "status": "running",
                "environment": settings.environment,
                "docs": "/docs",
                "api": settings.api_prefix,
                "warning": "Frontend not built - static directory not found"
            }
        
        logger.info("✓ Fallback root endpoint configured")


# Call setup_static_files after all API routes are registered
# ============================================================================
# CRITICAL: Call setup_static_files to actually register the routes
# ============================================================================
logger.info("Calling setup_static_files()...")
setup_static_files()
logger.info("Application startup complete!")


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
