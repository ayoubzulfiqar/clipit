"""
clipping.chapters — Auto-Chapters, Show Notes & SEO Metadata Generator

Generates YouTube/Spotify timestamped chapters, markdown show notes, and search-optimized
metadata directly from Whisper transcripts and segmented clips.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional


def format_timestamp(seconds: float) -> str:
    """
    Format seconds into MM:SS or HH:MM:SS string for YouTube chapter compatibility.
    Example: 85.0 -> '01:25', 3665.0 -> '01:01:05'
    """
    total_sec = max(0, int(seconds))
    hours = total_sec // 3600
    minutes = (total_sec % 3600) // 60
    secs = total_sec % 60

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def generate_chapters_from_clips(clips: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Convert scored clip candidates into an ordered list of chapters.
    Ensures first chapter begins at 00:00 as required by YouTube algorithm.
    """
    if not clips:
        return [{"timestamp": "00:00", "seconds": 0.0, "title": "Introduction"}]

    # Sort clips chronologically by start_time
    sorted_clips = sorted(clips, key=lambda c: float(c.get("start_time", 0.0)))
    chapters = []

    # First chapter must start at 00:00 for YouTube
    first_start = float(sorted_clips[0].get("start_time", 0.0))
    if first_start > 0.0:
        chapters.append({"timestamp": "00:00", "seconds": 0.0, "title": "Introduction"})

    for clip in sorted_clips:
        start_sec = float(clip.get("start_time", 0.0))
        title = (
            clip.get("title_en")
            or clip.get("title_id")
            or clip.get("judul_en")
            or clip.get("judul_id")
            or f"Segment {len(chapters) + 1}"
        )
        # Clean title
        clean_title = re.sub(r'[\r\n]+', ' ', title).strip()
        chapters.append({
            "timestamp": format_timestamp(start_sec),
            "seconds": round(start_sec, 2),
            "title": clean_title,
        })

    return chapters


def format_youtube_chapters_block(chapters: List[Dict[str, Any]]) -> str:
    """Format chapters into standard YouTube description text block."""
    lines = ["📌 Timestamps:"]
    for ch in chapters:
        lines.append(f"{ch['timestamp']} - {ch['title']}")
    return "\n".join(lines)


def generate_show_notes(
    title: str,
    summary: str,
    chapters: List[Dict[str, Any]],
    takeaways: Optional[List[str]] = None,
    source_url: Optional[str] = None,
) -> str:
    """Generate Markdown show notes for YouTube descriptions or blog distribution."""
    parts = []
    parts.append(f"# {title}\n")
    if summary:
        parts.append(f"## Summary\n{summary.strip()}\n")

    if takeaways:
        parts.append("## Key Takeaways")
        for t in takeaways:
            parts.append(f"- {t.strip()}")
        parts.append("")

    if chapters:
        parts.append("## Chapters")
        for ch in chapters:
            parts.append(f"- **{ch['timestamp']}** — {ch['title']}")
        parts.append("")

    if source_url:
        parts.append(f"🔗 Original Source: {source_url}\n")

    parts.append("Generated with [Clipit](https://github.com/ayoubzulfiqar/clipit) — AI Auto-Clipper")
    return "\n".join(parts)


def extract_seo_keywords(text: str, max_keywords: int = 15) -> List[str]:
    """Extract frequent and salient keyword tokens from transcript or summary text."""
    stop_words = {
        "the", "and", "this", "that", "with", "from", "for", "have", "what",
        "they", "will", "about", "your", "when", "make", "like", "time",
        "yang", "dan", "dari", "untuk", "ini", "itu", "dengan", "akan", "pada",
    }
    words = re.findall(r"\b[a-zA-Z0-9_-]{3,}\b", text.lower())
    freq: Dict[str, int] = {}
    for w in words:
        if w not in stop_words and not w.isdigit():
            freq[w] = freq.get(w, 0) + 1

    sorted_words = sorted(freq.items(), key=lambda item: item[1], reverse=True)
    return [w for w, _ in sorted_words[:max_keywords]]
