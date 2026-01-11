from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import os
from pathlib import Path

from app.database import init_db
from app.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    init_db()
    yield
    # Shutdown
    pass


app = FastAPI(
    title="Team Alchemy APP API",
    description="Backend API for Team Alchemy APP",
    version="0.1.0",
    lifespan=lifespan
)

# CORS configuration
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/healthz")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "team-alchemy-app",
        "version": "0.1.0"
    }

# Include API routes
app.include_router(router, prefix="/api")

# Serve static files (frontend)
static_dir = Path(__file__).parent.parent / "static"
if static_dir.exists():
    app.mount("/assets", StaticFiles(directory=str(static_dir / "assets")), name="static-assets")
    
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        """Serve frontend application"""
        # If requesting a file that exists, serve it
        file_path = static_dir / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        
        # Otherwise, serve index.html for client-side routing
        index_path = static_dir / "index.html"
        if index_path.exists():
            return FileResponse(index_path)
        
        return {"message": "Frontend not built"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
