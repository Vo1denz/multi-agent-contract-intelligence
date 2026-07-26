"""FastAPI application entrypoint and static frontend server."""

from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from .routers import health_router, contract_router

app = FastAPI(
    title="ClauseIQ API",
    description="Multi-Agent, Multimodal Contract Risk Intelligence System",
    version="0.1.0"
)

# CORS middleware for local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router.router)
app.include_router(contract_router.router)

# Mount frontend static files
frontend_dir = Path(__file__).resolve().parent.parent.parent / "frontend"

if frontend_dir.exists():
    app.mount("/css", StaticFiles(directory=frontend_dir / "css"), name="css")
    app.mount("/js", StaticFiles(directory=frontend_dir / "js"), name="js")
    app.mount("/assets", StaticFiles(directory=frontend_dir / "assets"), name="assets")

    @app.get("/", summary="Serve main interactive web dashboard")
    async def serve_index():
        """Return the Vanilla HTML frontend dashboard."""
        return FileResponse(frontend_dir / "index.html")
