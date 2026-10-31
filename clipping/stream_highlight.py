"""
clipping.stream_highlight — Streamer & Esports Gaming Highlight Peak Detector.

Analyzes audio energy dynamics, volume spikes (screaming, cheering, high APM),
and hype keyword triggers to identify viral gaming and live stream highlight moments.
"""

from __future__ import annotations

import math
import os
import re
import subprocess
from typing import Any, Dict, List, Optional, Tuple

from clipping.logger import get_logger

logger = get_logger("clipping.stream_highlight")

HYPE_TRIGGERS = {
    "let's go", "lets go", "no way", "oh my god", "omg", "insane",
    "clutch", "headshot", "ace", "what", "holy shit", "holy", "unbelievable",
    "kill", "gg", "pog", "poggers", "clip that", "clip it", "win", "winner",
    "gila", "mati", "menang", "anjir", "gokil", "parah",
}


def extract_rms_volume_stats(
    media_path: str,
    start_sec: float = 0.0,
    duration_sec: Optional[float] = None,
) -> List[Dict[str, float]]:
    """
    Extract windowed audio loudness/RMS data using FFmpeg astats / ebur128 filter.
    Returns list of {'time': float, 'rms_db': float}.
    """
    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-nostats",
        "-ss",
        f"{start_sec:.2f}",
    ]
    if duration_sec:
        cmd.extend(["-t", f"{duration_sec:.2f}"])

    cmd.extend([
        "-i",
        media_path,
        "-filter:a",
        "astats=metadata=1:reset=1,ametadata=print:key=lavfi.astats.Overall.RMS_level:file=-",
        "-f",
        "null",
        "-",
    ])

    try:
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            check=False,
            timeout=45,
        )
        raw_output = proc.stdout or ""
    except Exception as exc:
        logger.warning("FFmpeg astats audio extraction failed: %s", exc)
        return []

    pts_re = re.compile(r"pts_time:([0-9.]+)")
    rms_re = re.compile(r"lavfi\.astats\.Overall\.RMS_level=([-0-9.]+)")

    stats: List[Dict[str, float]] = []
    current_time = 0.0

    for line in raw_output.splitlines():
        line = line.strip()
        m_pts = pts_re.search(line)
        if m_pts:
            current_time = float(m_pts.group(1))

        m_rms = rms_re.search(line)
        if m_rms:
            val = float(m_rms.group(1))
            # Filter out silent infinity values (-inf dB)
            if not math.isinf(val) and val > -90.0:
                stats.append({"time": round(start_sec + current_time, 2), "rms_db": val})

    return stats


def detect_excitement_peaks(
    stats: List[Dict[str, float]],
    sensitivity: float = 1.5,
) -> List[float]:
    """
    Detect timestamps where audio volume surges significantly above baseline mean.
    """
    if not stats:
        return []

    values = [s["rms_db"] for s in stats]
    mean_val = sum(values) / len(values)
    variance = sum((v - mean_val) ** 2 for v in values) / len(values)
    std_dev = math.sqrt(variance)

    # In dB, higher volume is less negative (e.g. -12 dB is louder than -28 dB)
    threshold = mean_val + (sensitivity * std_dev)

    peak_times: List[float] = []
    for s in stats:
        if s["rms_db"] >= threshold:
            peak_times.append(s["time"])

    return peak_times


def detect_transcript_hype_moments(
    word_segments: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Scan spoken transcript word segments for excitement/hype shoutouts.
    """
    if not word_segments:
        return []

    hype_moments = []
    text_buffer = ""
    buf_start = 0.0

    for seg in word_segments:
        txt = (seg.get("text") or " ".join(w["word"] for w in seg.get("words", []))).lower()
        st = float(seg.get("start", 0.0))
        en = float(seg.get("end", 0.0))

        for trigger in HYPE_TRIGGERS:
            if trigger in txt:
                hype_moments.append({
                    "trigger": trigger,
                    "start": st,
                    "end": en,
                })
                break

    return hype_moments


def cluster_highlight_intervals(
    peak_timestamps: List[float],
    min_clip_duration: float = 15.0,
    max_clip_duration: float = 60.0,
    pre_roll: float = 5.0,
    post_roll: float = 10.0,
) -> List[Dict[str, Any]]:
    """
    Group clustered excitement timestamps into cohesive highlight clip boundaries.
    """
    if not peak_timestamps:
        return []

    clusters: List[List[float]] = []
    current_cluster: List[float] = [peak_timestamps[0]]

    for ts in peak_timestamps[1:]:
        # If timestamp is within 6 seconds of previous peak, group together
        if ts - current_cluster[-1] <= 6.0:
            current_cluster.append(ts)
        else:
            clusters.append(current_cluster)
            current_cluster = [ts]
    clusters.append(current_cluster)

    highlights = []
    for rank, cl in enumerate(clusters, start=1):
        peak_center = cl[len(cl) // 2]
        st = max(0.0, cl[0] - pre_roll)
        en = cl[-1] + post_roll

        # Enforce duration constraints
        dur = en - st
        if dur < min_clip_duration:
            en = st + min_clip_duration
        elif dur > max_clip_duration:
            en = st + max_clip_duration

        intensity_score = min(99, int(70 + (len(cl) * 5)))

        highlights.append({
            "rank": rank,
            "start_time": round(st, 2),
            "end_time": round(en, 2),
            "duration": round(en - st, 2),
            "peak_count": len(cl),
            "intensity_score": intensity_score,
            "title": f"Gaming Highlight #{rank} [Hype Spike]",
        })

    return highlights
