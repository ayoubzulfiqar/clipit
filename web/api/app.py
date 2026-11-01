"""
web.api.app — FastAPI Application Entry Point

Clipit Studio — Web GUI Backend

Run with:
    uvicorn web.api.app:app --host 0.0.0.0 --port 8000 --reload
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from clipping import __version__
from .routes import batch, files, jobs, presets, settings, system, tools
from . import store


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup/shutdown lifecycle."""
    print("🚀 Clipit Studio — Backend starting...")
    reconciled = store.reconcile_orphan_jobs()
    if reconciled > 0:
        print(f"⚠️ Reconciled {reconciled} interrupted job(s) from previous session.")
    yield
    print("👋 Backend shutting down...")


app = FastAPI(
    title="Clipit Studio",
    description="AI Auto-Clipper & Teaser Generator — Web GUI API",
    version=__version__,
    lifespan=lifespan,
)

# CORS — allow frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:5175",
        "https://ayoubzulfiqar.github.io",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def api_key_auth_middleware(request, call_next):
    """
    Authenticate incoming API requests when CLIPIT_API_KEY is set.
    Allows public health probes and docs to function unauthenticated.
    """
    configured_key = os.environ.get("CLIPIT_API_KEY", "").strip()
    if not configured_key:
        return await call_next(request)

    path = request.url.path
    if (
        not path.startswith("/api/")
        or path in {"/api/health", "/api/health/ready"}
        or path.startswith("/docs")
        or path.startswith("/openapi")
    ):
        return await call_next(request)

    header_key = request.headers.get("X-API-Key")
    auth_header = request.headers.get("Authorization", "")
    bearer_key = auth_header.split("Bearer ")[-1].strip() if "Bearer " in auth_header else ""

    if (header_key == configured_key) or (bearer_key == configured_key):
        return await call_next(request)

    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=401,
        content={"detail": "Unauthorized: Missing or invalid CLIPIT_API_KEY."},
    )


# Routes
app.include_router(jobs.router)
app.include_router(batch.router)
app.include_router(files.router)
app.include_router(presets.router)
app.include_router(settings.router)
app.include_router(system.router)
app.include_router(tools.router)


@app.get("/")
async def root():
    return {
        "name": "Clipit Studio",
        "version": __version__,
        "docs": "/docs",
        "health": "/api/health",
    }

import os
import signal
import asyncio

@app.post("/api/shutdown")
async def shutdown_server():
    """Trigger graceful shutdown of the FastAPI server."""
    # Send SIGINT to own process to trigger uvicorn graceful shutdown
    async def _shutdown():
        await asyncio.sleep(0.5)
        os.kill(os.getpid(), signal.SIGINT)
    
    asyncio.create_task(_shutdown())
    return {"status": "shutting down", "message": "Server is stopping..."}


def main():
    """CLI entry point to launch the Clipit Studio web server."""
    import argparse
    import uvicorn

    parser = argparse.ArgumentParser(description="Clipit Studio Web Server")
    parser.add_argument("--host", default=os.getenv("CLIPIT_HOST", "0.0.0.0"), help="Host IP to bind (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=int(os.getenv("CLIPIT_PORT", "8000")), help="Port to bind (default: 8000)")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload on code change")
    args = parser.parse_args()

    uvicorn.run("web.api.app:app", host=args.host, port=args.port, reload=args.reload)


if __name__ == "__main__":
    main()

