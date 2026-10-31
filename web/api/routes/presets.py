"""
web.api.routes.presets — Pipeline preset management endpoints.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..models import (
    PresetCreateRequest,
    PresetListResponse,
    PresetResponse,
)
from .. import store

router = APIRouter(prefix="/api/presets", tags=["presets"])


@router.get("")
async def list_presets() -> PresetListResponse:
    """List all available pipeline presets."""
    presets = store.list_presets()
    return PresetListResponse(
        presets=[PresetResponse(**p) for p in presets],
        total=len(presets),
    )


@router.post("", status_code=201)
async def create_or_update_preset(req: PresetCreateRequest) -> PresetResponse:
    """Save or update a named pipeline preset profile."""
    name = req.name.strip().lower().replace(" ", "_")
    if not name:
        raise HTTPException(status_code=400, detail="Invalid preset name")

    res = store.save_preset(name, req.config, req.description or "")
    return PresetResponse(**res)


@router.get("/{name}")
async def get_preset(name: str) -> PresetResponse:
    """Get preset details by name."""
    preset = store.get_preset(name.strip().lower())
    if preset is None:
        raise HTTPException(status_code=404, detail=f"Preset '{name}' not found")
    return PresetResponse(**preset)


@router.delete("/{name}")
async def delete_preset(name: str) -> dict:
    """Delete a custom preset by name."""
    success = store.delete_preset(name.strip().lower())
    if not success:
        raise HTTPException(status_code=404, detail=f"Preset '{name}' not found")
    return {"message": f"Preset '{name}' deleted"}
