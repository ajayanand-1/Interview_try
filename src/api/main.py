"""FastAPI Unified Application Entrypoint for Project Rosetta & Production Deployments."""

import os
import sys
from pathlib import Path

# Ensure repo root is on sys.path
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from src.api.routes.evaluations import router as evaluations_router

FRONTEND_DIST = _REPO_ROOT / "frontend" / "dist"

app = FastAPI(
    title="Project Rosetta — Multi-Agent AI Interview Panel API",
    description="HTTP API for orchestrating multi-agent interview panel simulations and retrieving traceable evaluation deliverables.",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json"
)

# CORS Configuration for local React frontend + production deployments
custom_origins = os.getenv("ALLOWED_ORIGINS", "").split(",")
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "*"
]
if custom_origins and any(custom_origins):
    allowed_origins.extend([o.strip() for o in custom_origins if o.strip()])

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.api_route("/api/health", methods=["GET", "HEAD"], tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "project-rosetta-api",
        "version": "1.0.0"
    }


# Include Evaluation Routes
app.include_router(evaluations_router, prefix="/api")


# Mount static assets if compiled frontend exists
if FRONTEND_DIST.exists() and (FRONTEND_DIST / "assets").exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="assets")


# SPA Catch-all and static root handlers (supports both GET and HEAD)
@app.api_route("/", methods=["GET", "HEAD"], include_in_schema=False)
async def serve_root():
    """Serve SPA index.html or API welcome message."""
    index_path = FRONTEND_DIST / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "service": "Prompt Wars Multi-Agent Hiring Intelligence API",
            "status": "online",
            "docs": "/docs",
            "health": "/api/health"
        }
    )


@app.api_route("/{full_path:path}", methods=["GET", "HEAD"], include_in_schema=False)
async def serve_spa(full_path: str, request: Request):
    """Serve SPA pages for non-API routes or return 404 for unknown /api/ paths."""
    if full_path.startswith("api/") or full_path in ["docs", "openapi.json", "redoc"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"API endpoint '/{full_path}' not found."
        )

    # Check if exact static file exists in dist (e.g. vite.svg, robots.txt)
    target_file = FRONTEND_DIST / full_path
    if target_file.is_file():
        return FileResponse(str(target_file))

    # Otherwise return index.html for React client-side routing
    index_path = FRONTEND_DIST / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Path '/{full_path}' not found and frontend/dist has not been built."
    )


# Structured Global Exception Handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "message": str(exc),
            "path": request.url.path
        }
    )


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=port, reload=False)
