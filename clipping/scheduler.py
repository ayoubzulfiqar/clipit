"""
clipping.scheduler — Content calendar generation and optimal posting time optimization.
"""

from __future__ import annotations

import csv
import json
import os
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

PLATFORM_PEAK_HOURS = {
    "tiktok": [7, 12, 19, 22],
    "shorts": [14, 17, 20],
    "reels": [9, 13, 21],
    "linkedin": [8, 12, 17],
    "x": [8, 13, 18],
}


def get_next_optimal_slot(
    current_time: datetime,
    platform: str = "tiktok",
    min_gap_hours: float = 3.0,
) -> datetime:
    """Find the next peak posting time slot for the target platform."""
    peak_hours = sorted(PLATFORM_PEAK_HOURS.get(platform.lower(), [12, 18]))
    earliest_allowed = current_time + timedelta(hours=min_gap_hours)

    candidate_day = earliest_allowed.date()
    for day_offset in range(7):
        day = candidate_day + timedelta(days=day_offset)
        for hour in peak_hours:
            candidate_dt = datetime(day.year, day.month, day.day, hour, 0, 0, tzinfo=current_time.tzinfo or timezone.utc)
            if candidate_dt >= earliest_allowed:
                return candidate_dt

    return earliest_allowed


def generate_posting_schedule(
    clips: List[Dict],
    platforms: List[str] | tuple[str, ...] = ("tiktok", "shorts", "reels"),
    start_time: Optional[datetime] = None,
    clips_per_day: int = 2,
) -> List[Dict]:
    """
    Generate an optimized multi-platform publishing calendar for rendered clips.

    Returns:
        List of scheduled post entries with platform, timestamp, title, hashtags, and media path.
    """
    if not clips:
        return []

    cursor = start_time or datetime.now(timezone.utc)
    scheduled_posts: List[Dict] = []

    for clip in clips:
        rank = clip.get("rank", 1)
        title = clip.get("youtube_title_final") or clip.get("title_inggris") or f"Clip #{rank}"
        caption = clip.get("tiktok_caption_final") or clip.get("description_hook") or title
        hashtags = clip.get("hastag") or "#viral #shorts"
        media_path = clip.get("output_video") or f"clip_{rank}.mp4"

        for plat in platforms:
            plat = plat.strip().lower()
            slot = get_next_optimal_slot(cursor, platform=plat, min_gap_hours=2.0)

            scheduled_posts.append({
                "clip_rank": rank,
                "platform": plat,
                "scheduled_time_iso": slot.isoformat(),
                "scheduled_date": slot.strftime("%Y-%m-%d"),
                "scheduled_time": slot.strftime("%H:%M UTC"),
                "title": title,
                "caption": caption,
                "hashtags": hashtags,
                "media_path": media_path,
                "status": "scheduled",
            })

        # Advance cursor forward for the next clip
        cursor += timedelta(hours=24.0 / max(1, clips_per_day))

    # Sort all posts chronologically
    scheduled_posts.sort(key=lambda x: x["scheduled_time_iso"])
    return scheduled_posts


def export_schedule_csv(schedule: List[Dict], output_path: str) -> str:
    """Export the publishing calendar to standard CSV."""
    if not schedule:
        return output_path

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    fieldnames = list(schedule[0].keys())

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(schedule)

    return output_path


def export_schedule_json(schedule: List[Dict], output_path: str) -> str:
    """Export the publishing calendar to JSON."""
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(schedule, f, indent=2, ensure_ascii=False)
    return output_path
