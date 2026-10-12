"""
The Lenny Growth Assistant — FastAPI Application Entrypoint

Initializes the FastAPI app with:
  - CORS middleware for frontend communication
  - Health check endpoint for operational readiness
  - Lifespan context manager for startup/shutdown hooks
  - Structured error handling
"""

from __future__ import annotations

import platform
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.core.logging import setup_logging
from app.api.middleware.logging_middleware import StructuredLoggingMiddleware

# Initialize JSON structured logging globally
setup_logging()


# --------------------------------------------------------------------- #
#  Lifespan — startup / shutdown hooks                                   #
# --------------------------------------------------------------------- #
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.
    - Startup: validate config, log provider info, init DB pool (future).
    - Shutdown: close DB pool, release resources (future).
    """
    # --- Startup ---
    provider = settings.resolved_provider.value
    print(f"[startup] {settings.app_name} v{settings.app_version}")
    print(f"[startup] LLM Provider: {provider}")
    print(f"[startup] Database: {settings.database_url.split('@')[-1] if '@' in settings.database_url else 'configured'}")
    print(f"[startup] CORS Origins: {settings.cors_origins}")

    yield

    # --- Shutdown ---
    print("[shutdown] Releasing resources...")


# --------------------------------------------------------------------- #
#  FastAPI Application                                                   #
# --------------------------------------------------------------------- #
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "AI-powered conversational assistant that ingests Lenny's Podcast transcripts, "
        "provides source-grounded answers to product & growth queries, generates "
        "long-form essays, and renders Markdown/HTML/CSS artifacts."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


# --------------------------------------------------------------------- #
#  Middleware                                                             #
# --------------------------------------------------------------------- #
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5175",
        "http://127.0.0.1:3000",
        *settings.cors_origins,  # Keeps any existing configured origins
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(StructuredLoggingMiddleware)


# --------------------------------------------------------------------- #
#  API Route Registration                                                #
# --------------------------------------------------------------------- #
from app.api import chat, sessions, health

app.include_router(health.router, prefix="/health", tags=["ops"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(sessions.router, prefix="/api/sessions", tags=["sessions"])


# --------------------------------------------------------------------- #
#  Global Exception Handler                                              #
# --------------------------------------------------------------------- #
import traceback

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Catch-all exception handler returning the standardized error contract.
    """
    print("GLOBAL EXCEPTION:", repr(exc))
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": str(exc),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        },
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )
