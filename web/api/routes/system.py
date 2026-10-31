"""
web.api.routes.system — System diagnostics, health checks, and readiness probes.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from typing import Any, Dict

from fastapi import APIRouter, Response, status

from clipping import __version__
from clipping.env_validator import validate_environment
from clipping.hardware import detect_hardware
from clipping.studio import detect_video_encoder
from .. import store
from ..queue import get_task_queue
from .files import OUTPUTS_DIR, UPLOAD_DIR

router = APIRouter(prefix="/api", tags=["system"])


def _check_binary(name: str) -> Dict[str, Any]:
    path = shutil.which(name)
    if not path:
        return {"installed": False, "path": None, "version": None}

    version_str = None
    try:
        proc = subprocess.run(
            [path, "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=3,
        )
        if proc.returncode == 0:
            first_line = proc.stdout.strip().splitlines()[0] if proc.stdout else ""
            version_str = first_line[:100]
    except Exception:
        pass

    return {
        "installed": True,
        "path": path,
        "version": version_str,
    }


def _check_storage(path: str) -> Dict[str, Any]:
    os.makedirs(path, exist_ok=True)
    writable = os.access(path, os.W_OK)
    usage = shutil.disk_usage(path)
    return {
        "path": path,
        "writable": writable,
        "total_gb": round(usage.total / (1024**3), 2),
        "free_gb": round(usage.free / (1024**3), 2),
        "used_percent": round((usage.used / usage.total) * 100, 1),
    }


@router.get("/health")
async def health_liveness():
    """Liveness probe: returns 200 if the FastAPI application is alive."""
    return {
        "status": "ok",
        "version": __version__,
    }


@router.get("/health/ready")
@router.get("/system/readiness")
async def health_readiness(response: Response):
    """
    Readiness probe: validates external binaries, database connectivity,
    hardware encoder availability, and disk storage access.
    """
    binaries = {
        "ffmpeg": _check_binary("ffmpeg"),
        "ffprobe": _check_binary("ffprobe"),
        "yt-dlp": _check_binary("yt-dlp"),
    }

    # Video encoder detection
    try:
        video_encoder = detect_video_encoder()
    except Exception as exc:
        video_encoder = f"error: {exc}"

    # Database connectivity
    db_ok = True
    db_error = None
    try:
        store.get_queued_count()
    except Exception as exc:
        db_ok = False
        db_error = str(exc)

    # Storage check
    outputs_storage = _check_storage(OUTPUTS_DIR)
    uploads_storage = _check_storage(UPLOAD_DIR)

    # Environment & API keys check
    env_report = validate_environment(require_ai=False).to_dict()

    # Core readiness requirements
    is_ready = bool(
        binaries["ffmpeg"]["installed"]
        and binaries["ffprobe"]["installed"]
        and db_ok
        and outputs_storage["writable"]
    )

    if not is_ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return {
        "ready": is_ready,
        "version": __version__,
        "binaries": binaries,
        "encoder": video_encoder,
        "hardware": detect_hardware().to_dict(),
        "queue": get_task_queue().get_info(),
        "database": {"ok": db_ok, "error": db_error},
        "storage": {
            "outputs": outputs_storage,
            "uploads": uploads_storage,
        },
        "environment": env_report,
    }
