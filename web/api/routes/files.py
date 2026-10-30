"""
web.api.routes.files — File upload and output serving endpoints.
"""

from __future__ import annotations

import os
import shutil

from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import FileResponse

router = APIRouter(tags=["files"])

# Resolve absolute path to the project root (2 levels up from web/api/routes)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

UPLOAD_DIR = os.path.join(PROJECT_ROOT, "uploads")
OUTPUTS_DIR = os.path.join(PROJECT_ROOT, "outputs")

# Ensure directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUTS_DIR, exist_ok=True)

# Max upload size: 2GB
MAX_UPLOAD_SIZE = 2 * 1024 * 1024 * 1024


def _validate_safe_child_path(base_dir: str, *segments: str) -> str:
    """
    Validate that joining segments to base_dir stays strictly inside base_dir.
    Rejects path traversal, absolute segments, null bytes, and directory escapes.
    Returns the real canonical path if safe, else raises HTTPException(400).
    """
    for seg in segments:
        if not seg or "\x00" in seg:
            raise HTTPException(status_code=400, detail="Invalid path parameter")
        if os.path.sep in seg or (os.path.altsep and os.path.altsep in seg):
            raise HTTPException(status_code=400, detail="Path traversal detected")
        if seg in {".", ".."}:
            raise HTTPException(status_code=400, detail="Path traversal detected")

    real_base = os.path.realpath(base_dir)
    target_path = os.path.realpath(os.path.join(real_base, *segments))

    try:
        common = os.path.commonpath([real_base, target_path])
    except ValueError:
        raise HTTPException(status_code=400, detail="Path traversal detected")

    if common != real_base or target_path == real_base:
        raise HTTPException(status_code=400, detail="Path traversal detected")

    return target_path


@router.post("/api/upload")
async def upload_video(file: UploadFile = File(...)) -> dict:
    """
    Upload a video file for processing.

    Returns the stored filename that can be used in ``upload_filename``
    when creating a job.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    # Validate extension
    allowed_exts = {".mp4", ".mkv", ".avi", ".mov", ".webm", ".flv", ".ts"}
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_exts:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {ext}. Allowed: {', '.join(allowed_exts)}",
        )

    # Sanitize filename
    safe_name = os.path.basename(file.filename)
    safe_name = safe_name.replace(" ", "_")
    for ch in '<>:"/\\|?*#\x00':
        safe_name = safe_name.replace(ch, "")

    if not safe_name or safe_name in {".", ".."}:
        raise HTTPException(status_code=400, detail="Invalid filename")

    dest = os.path.join(UPLOAD_DIR, safe_name)

    # Stream write to disk
    total_written = 0
    with open(dest, "wb") as f:
        while True:
            chunk = await file.read(1024 * 1024)  # 1MB chunks
            if not chunk:
                break
            total_written += len(chunk)
            if total_written > MAX_UPLOAD_SIZE:
                f.close()
                os.remove(dest)
                raise HTTPException(
                    status_code=413,
                    detail=f"File too large. Maximum size is {MAX_UPLOAD_SIZE // (1024**3)}GB.",
                )
            f.write(chunk)

    size_mb = total_written / (1024 * 1024)
    return {
        "filename": safe_name,
        "size_mb": round(size_mb, 2),
        "message": f"Upload berhasil: {safe_name} ({size_mb:.1f} MB)",
    }


@router.get("/api/outputs/{job_id}/{filename}")
async def serve_output(job_id: str, filename: str):
    """Serve a rendered clip or other output file."""
    file_path = _validate_safe_child_path(OUTPUTS_DIR, job_id, filename)
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    # Determine media type
    ext = os.path.splitext(filename)[1].lower()
    media_types = {
        ".mp4": "video/mp4",
        ".mkv": "video/x-matroska",
        ".avi": "video/x-msvideo",
        ".webm": "video/webm",
        ".json": "application/json",
        ".ass": "text/plain",
        ".srt": "text/plain",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
    }
    media_type = media_types.get(ext, "application/octet-stream")

    return FileResponse(
        file_path,
        media_type=media_type,
        filename=filename,
    )


@router.get("/api/outputs/{job_id}")
async def list_outputs(job_id: str) -> dict:
    """List all output files for a job."""
    job_dir = _validate_safe_child_path(OUTPUTS_DIR, job_id)
    if not os.path.exists(job_dir) or not os.path.isdir(job_dir):
        raise HTTPException(status_code=404, detail="Job output directory not found")

    files = []
    for fname in sorted(os.listdir(job_dir)):
        fpath = os.path.join(job_dir, fname)
        if os.path.isfile(fpath):
            size = os.path.getsize(fpath)
            files.append({
                "filename": fname,
                "size_bytes": size,
                "size_mb": round(size / (1024 * 1024), 2),
                "download_url": f"/api/outputs/{job_id}/{fname}",
            })

    return {"job_id": job_id, "files": files, "total": len(files)}
