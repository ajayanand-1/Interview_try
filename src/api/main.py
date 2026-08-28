"""FastAPI Main Application Entrypoint for Project Rosetta (Phase 6B & Production)."""

import os
import sys
from pathlib import Path

# Ensure repo root is on sys.path
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.routes.evaluations import router as evaluations_router

app = FastAPI(
    title="Project Rosetta — Multi-Agent AI Interview Panel API",
    description="HTTP API for orchestrating multi-agent interview panel simulations and retrieving traceable evaluation deliverables.",
    version="1.0.0"
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


@app.get("/api/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "project-rosetta-api",
        "version": "1.0.0"
    }


# Include Evaluation Routes
app.include_router(evaluations_router, prefix="/api")


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
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)
