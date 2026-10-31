"""
clipping.scene_detect — Natural camera cut / scene change detection and clip boundary auto-snapping.
"""

from __future__ import annotations

import re
import subprocess
from typing import Dict, List, Optional, Tuple

from clipping.logger import get_logger

logger = get_logger("clipping.scene_detect")


def detect_scene_changes(
    video_path: str,
    search_start: float,
    search_end: float,
    threshold: float = 0.35,
) -> List[float]:
    """
    Detect camera cuts / shot transitions using FFmpeg's scene score detection.

    Args:
        video_path: Absolute or relative path to the video file.
        search_start: Start timestamp in seconds for the search window.
        search_end: End timestamp in seconds for the search window.
        threshold: Scene score change threshold between 0.0 and 1.0 (default 0.35).

    Returns:
        Sorted list of scene cut timestamps (in seconds).
    """
    start_sec = max(0.0, search_start - 2.0)
    dur = max(0.5, (search_end + 2.0) - start_sec)

    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-nostats",
        "-ss",
        f"{start_sec:.3f}",
        "-t",
        f"{dur:.3f}",
        "-i",
        video_path,
        "-filter:v",
        f"select='gt(scene,{threshold})',showinfo",
        "-f",
        "null",
        "-",
    ]

    try:
        proc = subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
            timeout=30,
        )
        stderr_output = proc.stderr or ""
    except Exception as exc:
        logger.warning("FFmpeg scene cut detection failed: %s", exc)
        return []

    pts_pattern = re.compile(r"pts_time:\s*([0-9.]+)")
    cuts: List[float] = []

    for line in stderr_output.splitlines():
        if "pts_time:" in line:
            m = pts_pattern.search(line)
            if m:
                rel_ts = float(m.group(1))
                abs_ts = round(start_sec + rel_ts, 3)
                if abs_ts not in cuts:
                    cuts.append(abs_ts)

    cuts.sort()
    return cuts


def snap_to_nearest_scene_cut(
    timestamp: float,
    scene_cuts: List[float],
    max_distance: float = 1.0,
) -> float:
    """
    Snap a timestamp to the closest detected scene cut if within max_distance.

    Returns:
        Snapped timestamp if a cut point is within tolerance, otherwise original timestamp.
    """
    if not scene_cuts:
        return timestamp

    closest_cut = min(scene_cuts, key=lambda c: abs(c - timestamp))
    diff = abs(closest_cut - timestamp)

    if diff <= max_distance:
        logger.info("Snapping timestamp %.2fs -> %.2fs (nearest cut point diff %.2fs)", timestamp, closest_cut, diff)
        return closest_cut

    return timestamp


def snap_clip_boundaries(
    clip: Dict,
    scene_cuts: List[float],
    max_distance: float = 1.0,
    min_clip_duration: float = 10.0,
) -> Dict:
    """
    Snap a single clip's start_time and end_time to natural shot transitions.
    Guarantees the resulting clip duration is not squeezed below min_clip_duration.
    """
    st = float(clip.get("start_time", 0.0))
    en = float(clip.get("end_time", 0.0))

    snapped_st = snap_to_nearest_scene_cut(st, scene_cuts, max_distance=max_distance)
    snapped_en = snap_to_nearest_scene_cut(en, scene_cuts, max_distance=max_distance)

    # Validate that snapping did not violate duration limits
    if (snapped_en - snapped_st) >= min_clip_duration:
        clip["start_time"] = snapped_st
        clip["end_time"] = snapped_en
        clip["scene_cut_snapped"] = True

    return clip


def batch_snap_clips(
    clips: List[Dict],
    video_path: str,
    threshold: float = 0.35,
    max_distance: float = 1.0,
    min_clip_duration: float = 10.0,
) -> List[Dict]:
    """
    Batch process and auto-snap all clips in a video to natural camera cut boundaries.
    """
    if not clips or not video_path:
        return clips

    min_time = min(float(c.get("start_time", 0.0)) for c in clips)
    max_time = max(float(c.get("end_time", 0.0)) for c in clips)

    logger.info("Detecting scene cuts for video '%s' [%.1fs - %.1fs]...", video_path, min_time, max_time)
    cuts = detect_scene_changes(video_path, min_time, max_time, threshold=threshold)
    logger.info("Found %d scene cuts across clip intervals.", len(cuts))

    if not cuts:
        return clips

    for clip in clips:
        snap_clip_boundaries(clip, cuts, max_distance=max_distance, min_clip_duration=min_clip_duration)

    return clips
