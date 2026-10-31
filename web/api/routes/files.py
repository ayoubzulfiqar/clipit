"""
web.api.routes.files — File upload and output serving endpoints.
"""

from __future__ import annotations

import os
import shutil
import tempfile
import time
import zipfile

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


@router.get("/api/outputs/{job_id}/zip")
async def download_job_zip(job_id: str):
    """Bundle all output files for a job into a downloadable zip archive."""
    job_dir = _validate_safe_child_path(OUTPUTS_DIR, job_id)
    if not os.path.exists(job_dir) or not os.path.isdir(job_dir):
        raise HTTPException(status_code=404, detail="Job output directory not found")

    tmp_zip = tempfile.NamedTemporaryFile(delete=False, suffix=f"_{job_id}.zip")
    tmp_zip.close()

    try:
        with zipfile.ZipFile(tmp_zip.name, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, _, filenames in os.walk(job_dir):
                for fname in filenames:
                    abs_file = os.path.join(root, fname)
                    rel_name = os.path.relpath(abs_file, job_dir)
                    zf.write(abs_file, arcname=rel_name)

        return FileResponse(
            tmp_zip.name,
            media_type="application/zip",
            filename=f"clipit_job_{job_id}.zip",
        )
    except Exception as exc:
        if os.path.exists(tmp_zip.name):
            os.remove(tmp_zip.name)
        raise HTTPException(status_code=500, detail=f"Failed to generate zip: {exc}")


@router.delete("/api/outputs/{job_id}")
async def delete_job_outputs(job_id: str) -> dict:
    """Delete an entire job's outputs directory from disk."""
    job_dir = _validate_safe_child_path(OUTPUTS_DIR, job_id)
    if not os.path.exists(job_dir):
        raise HTTPException(status_code=404, detail="Job output directory not found")

    shutil.rmtree(job_dir, ignore_errors=True)
    return {"message": f"Outputs for job '{job_id}' deleted", "job_id": job_id}


@router.post("/api/files/cleanup")
async def cleanup_old_files(days: int = 7) -> dict:
    """
    Remove upload and output files older than N days to free disk space.
    """
    if days < 1:
        raise HTTPException(status_code=400, detail="Days parameter must be at least 1")

    now = time.time()
    max_age_seconds = days * 86400
    cleaned_uploads = 0
    cleaned_outputs = 0

    # 1. Clean uploads
    for fname in os.listdir(UPLOAD_DIR):
        fpath = os.path.join(UPLOAD_DIR, fname)
        if os.path.isfile(fpath) and (now - os.path.getmtime(fpath)) > max_age_seconds:
            try:
                os.remove(fpath)
                cleaned_uploads += 1
            except Exception:
                pass

    # 2. Clean output directories
    for dname in os.listdir(OUTPUTS_DIR):
        dpath = os.path.join(OUTPUTS_DIR, dname)
        # Skip jobs database files
        if dname in {"jobs.sqlite3", "jobs.sqlite3-wal", "jobs.sqlite3-shm", "jobs.json"}:
            continue
        if os.path.isdir(dpath) and (now - os.path.getmtime(dpath)) > max_age_seconds:
            try:
                shutil.rmtree(dpath, ignore_errors=True)
                cleaned_outputs += 1
            except Exception:
                pass

    return {
        "status": "success",
        "retention_days": days,
        "cleaned_uploads": cleaned_uploads,
        "cleaned_outputs": cleaned_outputs,
    }
