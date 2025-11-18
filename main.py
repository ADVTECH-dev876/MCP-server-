import logging
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager
from .config import settings
from .api import mcp, rest
from .utils.logging import setup_logging

# Setup logging
setup_logging()

# Database setup
engine = create_async_engine(settings.database_url, echo=settings.debug)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logging.info("Starting MCP Web Host Server")
    yield
    # Shutdown
    await engine.dispose()
    logging.info("Shutting down MCP Web Host Server")

app = FastAPI(
    title="MCP Web Project Hosting Server",
    description="Model Context Protocol server for hosting web projects with large file support",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for project hosting
app.mount("/projects", StaticFiles(directory=settings.upload_dir), name="projects")

# API routes
app.include_router(mcp.router, prefix="/api")
app.include_router(rest.router, prefix="/api/rest")

# Dependency for database session
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": "2025-11-18T12:00:00Z"}

# Additional endpoints for file download, etc.
@app.get("/api/download/{project_id}/{file_path:path}")
async def download_file(
    project_id: int,
    file_path: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await require_project_permission(project_id, Role.VIEWER, current_user, db)
    project = await project_service.get_project(project_id)
    full_path = Path(settings.upload_dir) / project.storage_path / file_path
    
    if not full_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return StreamingResponse(
        storage_service.get_file_stream(full_path),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={full_path.name}"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port)
