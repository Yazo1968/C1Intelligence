"""
C1 — FastAPI Application Entry Point
Registers all routes, error handlers, and CORS configuration.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.logging_config import configure_logging
from src.ingestion.models import IngestionError
from src.agents.models import AgentError
from src.api.errors import (
    agent_error_handler,
    generic_error_handler,
    ingestion_error_handler,
)
from src.api.routes.health import router as health_router
from src.api.routes.projects import router as projects_router
from src.api.routes.documents import router as documents_router
from src.api.routes.queries import router as queries_router

# Configure structured logging on import
configure_logging()

app = FastAPI(
    title="C1 — Construction Documentation Intelligence Platform",
    description="Forensic intelligence API for construction project documentation.",
    version="0.1.0",
)

# ---------------------------------------------------------------------------
# CORS — allow the Vercel-hosted frontend
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tighten to Vercel domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Error handlers — structured JSON errors, never raw exceptions
# ---------------------------------------------------------------------------
app.add_exception_handler(IngestionError, ingestion_error_handler)
app.add_exception_handler(AgentError, agent_error_handler)
app.add_exception_handler(Exception, generic_error_handler)

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
app.include_router(health_router)
app.include_router(projects_router)
app.include_router(documents_router)
app.include_router(queries_router)
