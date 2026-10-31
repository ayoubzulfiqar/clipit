"""
clipping.ctr_optimizer — CTR, Title & Thumbnail Hook Optimization Engine.

Scores candidate titles for viral short-form clickability and generates
high-CTR curiosity-gap variants and thumbnail punchline overlays.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

from clipping.logger import get_logger

logger = get_logger("clipping.ctr_optimizer")

# High-converting power words for short-form engagement (English & Indonesian)
POWER_WORDS = {
    "secret", "insane", "crazy", "shocking", "huge", "never", "always",
    "stop", "mistake", "warning", "ruined", "revealed", "truth", "exposed",
    "hack", "trick", "genius", "fast", "easy", "proof", "proven", "money",
    "rich", "scale", "viral", "disaster", "free", "dangerous", "illegal",
    "rahasia", "bahaya", "jangan", "terbukti", "gila", "kaget", "rugi",
    "untung", "trik", "kesalahan", "bongkar", "fakta", "nyata", "awas",
}

CURIOSITY_STARTERS = (
    "why ", "how ", "this is why ", "what happens when ", "never do ",
    "the secret to ", "nobody told you ", "kenapa ", "cara ", "alasan ",
    "jangan pernah ", "rahasia ",
)


def score_title_ctr(title: str, platform: str = "shorts") -> Dict[str, Any]:
    """
    Score a short-form video title for CTR clickability from 0 to 100.

    Factors:
      - Length sweet-spot (ideal: 30 to 55 characters for Shorts/TikTok)
      - Power words density
      - Curiosity gap presence (question or revelation)
      - Readability & capitalization
    """
    clean = (title or "").strip()
    if not clean:
        return {
            "title": "",
            "ctr_score": 0,
            "grade": "F",
            "feedback": ["Title is empty."],
        }

    char_len = len(clean)
    words = clean.lower().split()
    feedback: List[str] = []

    # 1. Length Score (max 30 pts)
    if 25 <= char_len <= 60:
        len_score = 30.0
    elif 15 <= char_len < 25:
        len_score = 20.0
        feedback.append("Title is slightly short; add context or emotional hook.")
    elif 60 < char_len <= 85:
        len_score = 22.0
        feedback.append("Title is slightly long; consider trimming to fit mobile preview.")
    else:
        len_score = 10.0
        feedback.append("Title length is suboptimal for mobile short-form feeds.")

    # 2. Power Words Score (max 30 pts)
    matched_power = [w.strip("!?,.") for w in words if w.strip("!?,.") in POWER_WORDS]
    if len(matched_power) >= 2:
        power_score = 30.0
    elif len(matched_power) == 1:
        power_score = 20.0
    else:
        power_score = 8.0
        feedback.append("Include high-converting power words (e.g. secret, mistake, insane).")

    # 3. Curiosity Gap (max 25 pts)
    lower_title = clean.lower()
    has_curiosity = any(lower_title.startswith(prefix) for prefix in CURIOSITY_STARTERS) or "?" in clean
    if has_curiosity:
        curiosity_score = 25.0
    else:
        curiosity_score = 10.0
        feedback.append("Add a curiosity gap hook (e.g. 'Why...', 'The reason...', or question).")

    # 4. Form & Punctuation (max 15 pts)
    form_score = 15.0
    if clean.islower():
        form_score -= 5.0
        feedback.append("Capitalize the first letters or key words for better visual contrast.")
    if clean.isupper() and len(clean) > 20:
        form_score -= 4.0
        feedback.append("Avoid all-caps sentences; reserve uppercase for 1-2 emphasis words.")

    total_score = min(100, int(round(len_score + power_score + curiosity_score + form_score)))

    # Determine letter grade
    if total_score >= 90:
        grade = "A+"
    elif total_score >= 80:
        grade = "A"
    elif total_score >= 70:
        grade = "B"
    elif total_score >= 60:
        grade = "C"
    else:
        grade = "D"

    return {
        "title": clean,
        "ctr_score": total_score,
        "grade": grade,
        "matched_power_words": matched_power,
        "char_count": char_len,
        "feedback": feedback if feedback else ["Title is well-optimized for high CTR."],
    }


def recommend_thumbnail_text(title: str, max_words: int = 4) -> str:
    """
    Extract a punchy 2-4 word teaser phrase suitable for high-contrast thumbnail stickers.
    """
    clean = re.sub(r"[^\w\s]", "", (title or "")).strip()
    words = clean.split()
    if not words:
        return "WATCH THIS"

    # Prioritize power words first
    power_matches = [w.upper() for w in words if w.lower() in POWER_WORDS]
    if power_matches:
        first_power = power_matches[0]
        # Return punchy phrase containing the power word
        return f"THE {first_power} REVEALED" if len(first_power) < 8 else first_power

    # Fallback to the first 3 words uppercase
    punch = " ".join(words[:max_words]).upper()
    return punch


def generate_ctr_variants(title: str) -> List[Dict[str, Any]]:
    """
    Generate three high-converting alternative title angles for A/B testing:
    1. Curiosity Gap
    2. Mistake / Fear of Missing Out (FOMO)
    3. Direct Bold Benefit
    """
    clean = (title or "").strip().rstrip(".!?")
    if not clean:
        return []

    # Clean leading words like "How to" or "Why"
    core = re.sub(r"^(how to|why|the|cara|rahasia)\s+", "", clean, flags=re.IGNORECASE).strip()

    variants = [
        {
            "angle": "Curiosity Gap",
            "title": f"Why Nobody Talks About {core.title()}...",
            "score": 88,
        },
        {
            "angle": "Mistake & FOMO",
            "title": f"The #1 Mistake With {core.title()} (Don't Do This)",
            "score": 92,
        },
        {
            "angle": "Direct High-Value",
            "title": f"How To Master {core.title()} In 60 Seconds",
            "score": 85,
        },
    ]

    for v in variants:
        res = score_title_ctr(v["title"])
        v["score"] = res["ctr_score"]
        v["grade"] = res["grade"]

    return variants
