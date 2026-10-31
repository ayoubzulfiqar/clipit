"""
web.api.routes.batch — Batch API & Enterprise Bulk Processing

Enables enterprise users to submit batches of video URLs or uploaded sources,
monitor aggregated progress across multiple concurrent jobs, and perform bulk cancellations.
"""

from __future__ import annotations

import time
import uuid
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from web.api import store, worker

router = APIRouter(prefix="/api/batch", tags=["batch"])

# In-memory batch store: batch_id -> {batch_id, created_at, job_ids, webhook_url}
_BATCH_STORE: Dict[str, Dict[str, Any]] = {}


class BatchJobItem(BaseModel):
    url: Optional[str] = None
    upload_filename: Optional[str] = None
    source: str = "youtube"
    pilihan_rasio: Optional[str] = None
    jumlah_klip: Optional[int] = None
    preset: Optional[str] = None
    webhook_url: Optional[str] = None
    tags: Optional[List[str]] = None
    extra_config: Optional[Dict[str, Any]] = None


class BatchJobCreateRequest(BaseModel):
    items: List[BatchJobItem] = Field(..., min_length=1, max_length=100)
    default_config: Optional[Dict[str, Any]] = None
    batch_webhook_url: Optional[str] = None


class BatchJobResponse(BaseModel):
    batch_id: str
    total_jobs: int
    created_at: float
    jobs: List[Dict[str, Any]]


class BatchStatusResponse(BaseModel):
    batch_id: str
    total: int
    completed: int
    failed: int
    processing: int
    queued: int
    jobs: List[Dict[str, Any]]


@router.post("/jobs", status_code=201, response_model=BatchJobResponse)
async def create_batch_jobs(req: BatchJobCreateRequest) -> BatchJobResponse:
    """Submit a batch of video clipping jobs for parallel execution."""
    batch_id = f"batch_{uuid.uuid4().hex[:10]}"
    created_jobs = []
    job_ids = []

    for item in req.items:
        if not item.url and not item.upload_filename:
            continue

        # Combine default_config and item-specific parameters
        cfg_payload = dict(req.default_config or {})
        if item.pilihan_rasio:
            cfg_payload["pilihan_rasio"] = item.pilihan_rasio
        if item.jumlah_klip:
            cfg_payload["jumlah_klip"] = item.jumlah_klip
        if item.webhook_url:
            cfg_payload["webhook_url"] = item.webhook_url
        elif req.batch_webhook_url:
            cfg_payload["webhook_url"] = req.batch_webhook_url
        if item.extra_config:
            cfg_payload.update(item.extra_config)

        tags = list(item.tags or [])
        tags.append(f"batch:{batch_id}")

        job_id = store.create_job(
            url=item.url,
            upload_filename=item.upload_filename,
            source=item.source,
            config=cfg_payload,
        )
        if tags:
            store.set_tags(job_id, tags)

        await worker.submit_job(job_id, cfg_payload)
        job_ids.append(job_id)
        created_jobs.append({
            "job_id": job_id,
            "url": item.url,
            "upload_filename": item.upload_filename,
            "status": "pending",
        })

    if not created_jobs:
        raise HTTPException(status_code=400, detail="No valid items provided in batch request.")

    now = time.time()
    _BATCH_STORE[batch_id] = {
        "batch_id": batch_id,
        "created_at": now,
        "job_ids": job_ids,
        "batch_webhook_url": req.batch_webhook_url,
    }

    return BatchJobResponse(
        batch_id=batch_id,
        total_jobs=len(created_jobs),
        created_at=now,
        jobs=created_jobs,
    )


@router.get("/{batch_id}", response_model=BatchStatusResponse)
async def get_batch_status(batch_id: str) -> BatchStatusResponse:
    """Retrieve aggregated status across all jobs in a batch."""
    batch = _BATCH_STORE.get(batch_id)
    if not batch:
        raise HTTPException(status_code=404, detail=f"Batch {batch_id} not found.")

    counts = {"completed": 0, "failed": 0, "processing": 0, "queued": 0}
    jobs_summary = []

    for jid in batch["job_ids"]:
        j = store.get_job(jid)
        if not j:
            continue
        st = j.get("status", "pending")
        if st in ("done", "completed"):
            counts["completed"] += 1
        elif st in ("error", "failed"):
            counts["failed"] += 1
        elif st in ("pending", "queued"):
            counts["queued"] += 1
        else:
            counts["processing"] += 1

        jobs_summary.append({
            "job_id": jid,
            "status": st,
            "progress": j.get("progress", 0.0),
            "step": j.get("step"),
            "url": j.get("url"),
            "clips_count": len(j.get("clips", [])),
        })

    return BatchStatusResponse(
        batch_id=batch_id,
        total=len(batch["job_ids"]),
        completed=counts["completed"],
        failed=counts["failed"],
        processing=counts["processing"],
        queued=counts["queued"],
        jobs=jobs_summary,
    )


@router.post("/{batch_id}/cancel")
async def cancel_batch_jobs(batch_id: str) -> Dict[str, Any]:
    """Cancel all active or queued jobs belonging to a batch."""
    batch = _BATCH_STORE.get(batch_id)
    if not batch:
        raise HTTPException(status_code=404, detail=f"Batch {batch_id} not found.")

    cancelled = 0
    for jid in batch["job_ids"]:
        if store.cancel_job(jid):
            cancelled += 1

    return {
        "batch_id": batch_id,
        "total": len(batch["job_ids"]),
        "cancelled": cancelled,
    }
