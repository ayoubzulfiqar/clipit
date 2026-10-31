"""
clipping.copyright — Copyright Safety & Content Originality Analyzer

Analyzes candidate clips for automated Content ID and copyright strike risks,
and recommends concrete audiovisual transformations (tempo/pitch shifts, voiceover ducking,
and B-roll cutaway cadence) to safeguard fair-use and monetization eligibility.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

# Known high-risk copyright and automated Content ID triggers
COMMERCIAL_MUSIC_SIGNALS = [
    r"\b(song by|track by|performed by|feat\.|ft\.)\b",
    r"\b(taylor swift|drake|beyonce|bad bunny|the weeknd|ed sheeran|bts)\b",
    r"\b(universal music|warner music|sony music|sme|umg|wmg)\b",
    r"\b(nintendo soundtrack|disney records|marvel music)\b",
]

RESTRICTED_TRADEMARKS = [
    r"\b(super bowl|olympic games|fifa world cup)\b",
]


def check_text_copyright_signals(text: str) -> List[str]:
    """Scan transcript or title text for high-risk copyright and trademark triggers."""
    lowered = text.lower()
    flagged = []
    for pattern in COMMERCIAL_MUSIC_SIGNALS:
        match = re.search(pattern, lowered, re.IGNORECASE)
        if match:
            flagged.append(f"music_signal:{match.group(0)}")

    for pattern in RESTRICTED_TRADEMARKS:
        match = re.search(pattern, lowered, re.IGNORECASE)
        if match:
            flagged.append(f"trademark_signal:{match.group(0)}")

    return flagged


def analyze_content_safety(
    transcript: str,
    title: str = "",
    has_commercial_bgm: bool = False,
    continuous_duration_sec: float = 30.0,
) -> Dict[str, Any]:
    """
    Produce a copyright risk assessment for a clip candidate.
    
    Risk Levels: 'low' (0-29), 'medium' (30-69), 'high' (70-100).
    """
    flags = check_text_copyright_signals(f"{title} {transcript}")
    score = 0.0

    if has_commercial_bgm:
        score += 45.0
        flags.append("unmodified_background_music")

    if continuous_duration_sec > 45.0:
        score += 20.0
        flags.append("long_uninterrupted_segment")
    elif continuous_duration_sec > 25.0:
        score += 10.0

    for f in flags:
        if f.startswith("music_signal"):
            score += 25.0
        elif f.startswith("trademark_signal"):
            score += 20.0

    score = min(100.0, score)

    if score >= 70.0:
        risk_level = "high"
    elif score >= 30.0:
        risk_level = "medium"
    else:
        risk_level = "low"

    return {
        "risk_level": risk_level,
        "risk_score": round(score, 1),
        "flags": flags,
        "is_safe_for_monetization": risk_level == "low",
    }


def recommend_originality_transforms(safety_report: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Recommend audiovisual transformations to mitigate copyright risk and break
    automated acoustic fingerprinting (Content ID).
    """
    transforms = []
    level = safety_report.get("risk_level", "low")
    flags = safety_report.get("flags", [])

    if level in ("medium", "high") or "unmodified_background_music" in flags:
        transforms.append({
            "type": "audio_pitch_shift",
            "parameter": "+1.2 semitones",
            "filter": "asetrate=44100*1.0717,aresample=44100,atempo=0.933",
            "rationale": "Slight pitch adjustment alters acoustic spectral peaks detected by automated matchers.",
        })
        transforms.append({
            "type": "audio_tempo_ramp",
            "parameter": "1.03x",
            "filter": "atempo=1.03",
            "rationale": "3% speed variation alters duration-based fingerprint alignments without degrading speech clarity.",
        })

    if "long_uninterrupted_segment" in flags or level == "high":
        transforms.append({
            "type": "broll_cutaway_cadence",
            "parameter": "every_6_seconds",
            "rationale": "Inserting contextual B-roll or reaction zoom cuts breaks continuous visual keyframe matches.",
        })

    if level in ("medium", "high"):
        transforms.append({
            "type": "voiceover_sidechain_ducking",
            "parameter": "-16_dB_ducking",
            "rationale": "Ducking underlying audio under commentary establishes transformative fair-use character.",
        })

    return transforms
