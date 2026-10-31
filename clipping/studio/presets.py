"""
clipping.studio.presets — Platform aspect-ratio and UI safe-zone presets.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Tuple


@dataclass(frozen=True)
class SafeZoneMargins:
    top_pct: float
    bottom_pct: float
    left_pct: float
    right_pct: float


@dataclass(frozen=True)
class PlatformPreset:
    name: str
    aspect_ratio: str
    target_dimensions: Tuple[int, int]
    safe_zone: SafeZoneMargins
    description: str


PLATFORM_PRESETS: Dict[str, PlatformPreset] = {
    "tiktok": PlatformPreset(
        name="tiktok",
        aspect_ratio="9:16",
        target_dimensions=(1080, 1920),
        safe_zone=SafeZoneMargins(top_pct=0.15, bottom_pct=0.20, left_pct=0.06, right_pct=0.14),
        description="TikTok 9:16 vertical video with right-side action buttons and bottom caption safe zones",
    ),
    "reels": PlatformPreset(
        name="reels",
        aspect_ratio="9:16",
        target_dimensions=(1080, 1920),
        safe_zone=SafeZoneMargins(top_pct=0.14, bottom_pct=0.18, left_pct=0.05, right_pct=0.12),
        description="Instagram Reels 9:16 with profile and audio UI safe zones",
    ),
    "shorts": PlatformPreset(
        name="shorts",
        aspect_ratio="9:16",
        target_dimensions=(1080, 1920),
        safe_zone=SafeZoneMargins(top_pct=0.12, bottom_pct=0.22, left_pct=0.05, right_pct=0.12),
        description="YouTube Shorts 9:16 vertical format with subscribe & description clearance",
    ),
    "instagram": PlatformPreset(
        name="instagram",
        aspect_ratio="4:5",
        target_dimensions=(1080, 1350),
        safe_zone=SafeZoneMargins(top_pct=0.05, bottom_pct=0.08, left_pct=0.05, right_pct=0.05),
        description="Instagram Feed Portrait (4:5) maximum screen real-estate",
    ),
    "linkedin": PlatformPreset(
        name="linkedin",
        aspect_ratio="1:1",
        target_dimensions=(1080, 1080),
        safe_zone=SafeZoneMargins(top_pct=0.05, bottom_pct=0.05, left_pct=0.05, right_pct=0.05),
        description="LinkedIn Square (1:1) video feed format",
    ),
    "x": PlatformPreset(
        name="x",
        aspect_ratio="1:1",
        target_dimensions=(1080, 1080),
        safe_zone=SafeZoneMargins(top_pct=0.05, bottom_pct=0.05, left_pct=0.05, right_pct=0.05),
        description="X / Twitter Square video feed format",
    ),
    "youtube": PlatformPreset(
        name="youtube",
        aspect_ratio="16:9",
        target_dimensions=(1920, 1080),
        safe_zone=SafeZoneMargins(top_pct=0.08, bottom_pct=0.10, left_pct=0.08, right_pct=0.08),
        description="Standard 16:9 horizontal widescreen format",
    ),
}


def get_platform_preset(platform: str) -> Optional[PlatformPreset]:
    """Get preset configuration for a target platform (case-insensitive)."""
    if not platform:
        return None
    return PLATFORM_PRESETS.get(platform.lower().strip())
