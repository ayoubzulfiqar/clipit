"""
web.api.routes.tools — Advanced Intelligence Tools & Diagnostics API

Exposes endpoints for multimodal thumbnail scoring, copyright Content ID audits,
YouTube auto-chapters & show notes generation, social release calendar scheduling,
and community template pack (.clipit-pack) management.
"""

from __future__ import annotations

import io
import os
import shutil
import tempfile
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

from clipping import chapters as chapters_mod
from clipping import copyright as copyright_mod
from clipping import marketplace as marketplace_mod
from clipping import scheduler as scheduler_mod
from clipping import vision_scoring as vision_mod
from web.api import store

router = APIRouter(prefix="/api/tools", tags=["tools"])


class CopyrightCheckRequest(BaseModel):
    transcript: str
    title: Optional[str] = ""
    has_commercial_bgm: Optional[bool] = False
    duration: Optional[float] = 30.0


class CopyrightCheckResponse(BaseModel):
    risk_level: str
    risk_score: float
    flags: List[str]
    is_safe_for_monetization: bool
    recommended_transforms: List[Dict[str, Any]]


class ChaptersRequest(BaseModel):
    job_id: Optional[str] = None
    title: Optional[str] = "Clipit Video"
    summary: Optional[str] = ""
    clips: Optional[List[Dict[str, Any]]] = None


class ChaptersResponse(BaseModel):
    chapters: List[Dict[str, Any]]
    youtube_block: str
    show_notes_markdown: str


class CalendarRequest(BaseModel):
    job_id: Optional[str] = None
    clips: Optional[List[Dict[str, Any]]] = None
    platforms: Optional[List[str]] = ["tiktok", "shorts", "reels"]
    clips_per_day: Optional[int] = 2


class CalendarResponse(BaseModel):
    total_slots: int
    schedule: List[Dict[str, Any]]


class MarketplaceExportRequest(BaseModel):
    pack_name: str
    preset_name: Optional[str] = None
    preset_data: Optional[Dict[str, Any]] = None
    author: Optional[str] = "Clipit Studio User"
    description: Optional[str] = ""
    version: Optional[str] = "1.0.0"
    tags: Optional[List[str]] = []


@router.post("/vision-score")
async def score_thumbnail_image(file: UploadFile = File(...)) -> Dict[str, Any]:
    """Score an uploaded image frame for sharpness, contrast, brightness, and composite virality."""
    try:
        from PIL import Image

        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        scores = vision_mod.score_frame(image)
        return {
            "filename": file.filename,
            "format": image.format,
            "dimensions": {"width": image.width, "height": image.height},
            **scores,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Image scoring failed: {e}")


@router.post("/copyright-check", response_model=CopyrightCheckResponse)
async def check_copyright_safety(req: CopyrightCheckRequest) -> CopyrightCheckResponse:
    """Analyze transcript and metadata for automated Content ID risks and suggested transformations."""
    report = copyright_mod.analyze_content_safety(
        transcript=req.transcript,
        title=req.title or "",
        has_commercial_bgm=req.has_commercial_bgm or False,
        continuous_duration_sec=req.duration or 30.0,
    )
    transforms = copyright_mod.recommend_originality_transforms(report)
    return CopyrightCheckResponse(
        risk_level=report["risk_level"],
        risk_score=report["risk_score"],
        flags=report["flags"],
        is_safe_for_monetization=report["is_safe_for_monetization"],
        recommended_transforms=transforms,
    )


@router.post("/chapters", response_model=ChaptersResponse)
async def generate_chapters(req: ChaptersRequest) -> ChaptersResponse:
    """Generate YouTube description chapter timestamps and Markdown show notes."""
    clips_to_use = req.clips or []
    if not clips_to_use and req.job_id:
        job = store.get_job(req.job_id)
        if job and job.get("clips"):
            clips_to_use = job["clips"]

    if not clips_to_use:
        clips_to_use = [
            {"start_time": 0.0, "title_en": "Introduction"},
            {"start_time": 30.0, "title_en": "Key Highlights"},
        ]

    chapters = chapters_mod.generate_chapters_from_clips(clips_to_use)
    yt_block = chapters_mod.format_youtube_chapters_block(chapters)
    show_notes = chapters_mod.generate_show_notes(
        title=req.title or "Video Highlights",
        summary=req.summary or "Viral short-form clips generated with Clipit.",
        chapters=chapters,
        takeaways=["High-impact opening hook", "Key actionable takeaways", "Core conclusion"],
    )

    return ChaptersResponse(
        chapters=chapters,
        youtube_block=yt_block,
        show_notes_markdown=show_notes,
    )


@router.post("/calendar", response_model=CalendarResponse)
async def generate_calendar(req: CalendarRequest) -> CalendarResponse:
    """Generate an optimized multi-platform release calendar for clips."""
    clips_to_use = req.clips or []
    if not clips_to_use and req.job_id:
        job = store.get_job(req.job_id)
        if job and job.get("clips"):
            clips_to_use = job["clips"]

    if not clips_to_use:
        clips_to_use = [
            {"rank": 1, "title_en": "Viral Hook Moment", "start_time": 10.0, "end_time": 40.0},
            {"rank": 2, "title_en": "Insight Breakdown", "start_time": 50.0, "end_time": 85.0},
        ]

    platforms = req.platforms or ["tiktok", "shorts", "reels"]
    schedule = scheduler_mod.generate_posting_schedule(
        clips=clips_to_use,
        platforms=platforms,
        clips_per_day=req.clips_per_day or 2,
    )

    return CalendarResponse(
        total_slots=len(schedule),
        schedule=schedule,
    )


@router.post("/marketplace/export")
async def export_marketplace_pack(req: MarketplaceExportRequest) -> Dict[str, Any]:
    """Export a preset configuration to a portable .clipit-pack bundle."""
    preset_data = req.preset_data
    if not preset_data and req.preset_name:
        preset_obj = store.get_preset(req.preset_name)
        if preset_obj:
            preset_data = preset_obj.get("config", {})

    if not preset_data:
        raise HTTPException(status_code=400, detail="Valid preset_data or preset_name required.")

    # Project root
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    out_dir = os.path.join(project_root, "outputs", "packs")
    os.makedirs(out_dir, exist_ok=True)

    safe_name = "".join(c for c in req.pack_name if c.isalnum() or c in ("-", "_")).lower()
    pack_filename = f"{safe_name}.clipit-pack"
    pack_path = os.path.join(out_dir, pack_filename)

    try:
        marketplace_mod.export_pack(
            pack_name=req.pack_name,
            preset_data=preset_data,
            output_path=pack_path,
            author=req.author or "Clipit Studio",
            description=req.description or "",
            version=req.version or "1.0.0",
            tags=req.tags or [],
        )
        return {
            "pack_name": req.pack_name,
            "filename": pack_filename,
            "download_url": f"/api/files/download_pack/{pack_filename}",
            "size_bytes": os.path.getsize(pack_path),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {e}")


@router.post("/marketplace/import")
async def import_marketplace_pack(file: UploadFile = File(...)) -> Dict[str, Any]:
    """Import and install a .clipit-pack archive into the presets store."""
    if not file.filename.endswith(".clipit-pack") and not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="File must be a .clipit-pack or .zip archive.")

    with tempfile.NamedTemporaryFile(suffix=".clipit-pack", delete=False) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
        install_dir = os.path.join(project_root, "custom_presets")
        imported = marketplace_mod.import_pack(tmp_path, install_dir=install_dir)

        # Also register preset in store so it appears in presets list
        preset_name = imported.get("pack_name", file.filename).lower().replace(" ", "_")
        store.save_preset(
            name=preset_name,
            config=imported.get("preset", {}),
            description=imported.get("description", "Imported from .clipit-pack"),
        )

        return {
            "status": "success",
            "pack_name": imported.get("pack_name"),
            "author": imported.get("author"),
            "version": imported.get("version"),
            "preset_registered": preset_name,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to import pack: {e}")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
