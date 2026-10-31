"""
clipping.silence — Smart silence detection, dead-air trimming, and filler word filtering.
"""

from __future__ import annotations

import re
import subprocess
from typing import Dict, List, Optional, Tuple

from clipping.logger import get_logger

logger = get_logger("clipping.silence")

DEFAULT_FILLER_WORDS = {
    "en": {"uh", "um", "umm", "uhh", "er", "err", "ah", "ahh", "like", "you know"},
    "id": {"anu", "nganu", "hmm", "eh", "ehm", "egh", "kayak", "gitu", "ya kan", "apa tuh"},
}


def detect_silence_from_words(
    data_segmen: List[Dict],
    clip_start: float,
    clip_end: float,
    min_silence_duration: float = 0.5,
) -> List[Tuple[float, float]]:
    """
    Detect pauses / dead-air within [clip_start, clip_end] from Whisper word timestamps.

    Returns:
        List of (silence_start, silence_end) relative to absolute video time.
    """
    # Extract all words falling within clip range
    words: List[Dict] = []
    for seg in data_segmen:
        seg_words = seg.get("words", [])
        if seg_words:
            for w in seg_words:
                w_start = float(w.get("start", 0.0))
                w_end = float(w.get("end", 0.0))
                if w_end > clip_start and w_start < clip_end:
                    words.append({"start": max(clip_start, w_start), "end": min(clip_end, w_end)})
        else:
            # Fallback to segment-level timestamps if words are not present
            s_st = float(seg.get("start", 0.0))
            s_en = float(seg.get("end", 0.0))
            if s_en > clip_start and s_st < clip_end:
                words.append({"start": max(clip_start, s_st), "end": min(clip_end, s_en)})

    words.sort(key=lambda x: x["start"])
    silence_intervals: List[Tuple[float, float]] = []

    # 1. Check leading silence before the first word
    if words:
        leading_gap = words[0]["start"] - clip_start
        if leading_gap >= min_silence_duration:
            silence_intervals.append((clip_start, words[0]["start"]))

        # 2. Check gaps between consecutive words
        for i in range(len(words) - 1):
            curr_end = words[i]["end"]
            next_start = words[i + 1]["start"]
            gap = next_start - curr_end
            if gap >= min_silence_duration:
                silence_intervals.append((curr_end, next_start))

        # 3. Check trailing silence after the last word
        trailing_gap = clip_end - words[-1]["end"]
        if trailing_gap >= min_silence_duration:
            silence_intervals.append((words[-1]["end"], clip_end))
    else:
        # No speech detected at all
        silence_intervals.append((clip_start, clip_end))

    return silence_intervals


def detect_silence_ffmpeg(
    media_path: str,
    clip_start: float,
    clip_end: float,
    noise_db: float = -30.0,
    min_duration: float = 0.5,
) -> List[Tuple[float, float]]:
    """
    Detect audio silence within [clip_start, clip_end] using FFmpeg's silencedetect filter.

    Returns:
        List of (silence_start, silence_end) relative to absolute video time.
    """
    dur = max(0.1, clip_end - clip_start)
    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-nostats",
        "-ss",
        str(clip_start),
        "-t",
        str(dur),
        "-i",
        media_path,
        "-af",
        f"silencedetect=noise={noise_db}dB:d={min_duration}",
        "-f",
        "null",
        "-",
    ]

    try:
        proc = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, check=False)
        stderr = proc.stderr or ""
    except Exception as exc:
        logger.warning("FFmpeg silencedetect failed: %s", exc)
        return []

    intervals: List[Tuple[float, float]] = []
    current_silence_start: Optional[float] = None

    start_pattern = re.compile(r"silence_start:\s*([0-9.]+)")
    end_pattern = re.compile(r"silence_end:\s*([0-9.]+)")

    for line in stderr.splitlines():
        sm = start_pattern.search(line)
        if sm:
            rel_s = float(sm.group(1))
            current_silence_start = clip_start + rel_s

        em = end_pattern.search(line)
        if em:
            rel_e = float(em.group(1))
            abs_e = min(clip_end, clip_start + rel_e)
            abs_s = current_silence_start if current_silence_start is not None else clip_start
            if abs_e > abs_s:
                intervals.append((abs_s, abs_e))
            current_silence_start = None

    if current_silence_start is not None and current_silence_start < clip_end:
        intervals.append((current_silence_start, clip_end))

    return intervals


def merge_silence_intervals(intervals: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
    """Merge overlapping or adjacent silence intervals."""
    if not intervals:
        return []

    sorted_ints = sorted(intervals, key=lambda x: x[0])
    merged = [sorted_ints[0]]

    for current in sorted_ints[1:]:
        prev_start, prev_end = merged[-1]
        if current[0] <= prev_end:
            # Overlap or contiguous
            merged[-1] = (prev_start, max(prev_end, current[1]))
        else:
            merged.append(current)

    return merged


def compute_keep_segments(
    clip_start: float,
    clip_end: float,
    silence_intervals: List[Tuple[float, float]],
    padding_seconds: float = 0.08,
    min_segment_duration: float = 0.5,
) -> List[Dict[str, float]]:
    """
    Invert silence intervals to produce active speech segments ('keep_segments').

    Adds a tiny acoustic safety margin (padding) to prevent abruptly cutting
    first/last consonant bursts.
    """
    if not silence_intervals:
        return [{"start_time": round(clip_start, 2), "end_time": round(clip_end, 2)}]

    merged_silence = merge_silence_intervals(silence_intervals)
    speech_segments: List[Dict[str, float]] = []
    cursor = clip_start

    for s_start, s_end in merged_silence:
        # Speech occurs between cursor and s_start
        speech_end = max(cursor, s_start + padding_seconds)
        speech_start = max(clip_start, cursor - (padding_seconds if cursor > clip_start else 0.0))

        if (speech_end - speech_start) >= min_segment_duration:
            speech_segments.append({
                "start_time": round(speech_start, 2),
                "end_time": round(speech_end, 2),
            })

        cursor = s_end - padding_seconds

    # Final segment from last silence to clip_end
    if (clip_end - cursor) >= min_segment_duration:
        speech_segments.append({
            "start_time": round(max(clip_start, cursor), 2),
            "end_time": round(clip_end, 2),
        })

    # Fallback to entire clip if everything was somehow filtered out
    if not speech_segments:
        speech_segments = [{"start_time": round(clip_start, 2), "end_time": round(clip_end, 2)}]

    return speech_segments


def filter_filler_words(text: str, language: str = "id") -> str:
    """
    Remove or clean common filler words from subtitle text.
    """
    fillers = DEFAULT_FILLER_WORDS.get(language, DEFAULT_FILLER_WORDS["en"])
    words = text.split()
    cleaned = [w for w in words if w.lower().strip(",.!?\"'") not in fillers]
    return " ".join(cleaned) if cleaned else text
