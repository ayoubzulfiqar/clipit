"""
clipping.dedup — Temporal and semantic duplicate / near-duplicate clip detection.
"""

from __future__ import annotations

import re
from typing import Dict, List, Set, Tuple

from clipping.logger import get_logger

logger = get_logger("clipping.dedup")


def calculate_temporal_iou(start_a: float, end_a: float, start_b: float, end_b: float) -> float:
    """
    Calculate Temporal Intersection-over-Union (tIoU) between two time intervals.
    """
    intersection_start = max(start_a, start_b)
    intersection_end = min(end_a, end_b)
    intersection = max(0.0, intersection_end - intersection_start)

    union_start = min(start_a, start_b)
    union_end = max(end_a, end_b)
    union = max(0.0001, union_end - union_start)

    return intersection / union


def _tokenize_text(text: str) -> Set[str]:
    """Tokenize and normalize text into word shingles."""
    clean = re.sub(r"[^\w\s]", "", str(text or "").lower())
    words = clean.split()
    return set(words)


def calculate_text_similarity(text_a: str, text_b: str) -> float:
    """Calculate Jaccard similarity between two texts."""
    tokens_a = _tokenize_text(text_a)
    tokens_b = _tokenize_text(text_b)

    if not tokens_a or not tokens_b:
        return 0.0

    intersection = len(tokens_a.intersection(tokens_b))
    union = len(tokens_a.union(tokens_b))
    return intersection / max(1, union)


def filter_duplicate_candidates(
    clips: List[Dict],
    threshold_iou: float = 0.60,
    threshold_text_similarity: float = 0.75,
) -> List[Dict]:
    """
    Filter out near-duplicate clips from a ranked list of clip candidates.
    Preserves higher-ranked clips (higher viral_score) and drops overlapping duplicates.

    Returns:
        Deduplicated list of clip dictionaries.
    """
    if not clips:
        return []

    # Ensure clips are evaluated in order of rank / viral score
    sorted_clips = sorted(clips, key=lambda x: x.get("viral_score", 0), reverse=True)
    kept_clips: List[Dict] = []

    for candidate in sorted_clips:
        c_start = float(candidate.get("start_time", 0.0))
        c_end = float(candidate.get("end_time", 0.0))
        c_text = candidate.get("title_inggris", "") or candidate.get("title_indonesia", "")

        is_duplicate = False
        for prior in kept_clips:
            p_start = float(prior.get("start_time", 0.0))
            p_end = float(prior.get("end_time", 0.0))
            p_text = prior.get("title_inggris", "") or prior.get("title_indonesia", "")

            # 1. Temporal IoU check
            iou = calculate_temporal_iou(c_start, c_end, p_start, p_end)
            if iou >= threshold_iou:
                logger.info(
                    "Dropping near-duplicate clip (tIoU %.2f >= %.2f) between [%s-%s] and [%s-%s]",
                    iou, threshold_iou, c_start, c_end, p_start, p_end,
                )
                is_duplicate = True
                break

            # 2. Textual similarity check if titles or hooks are almost identical
            if c_text and p_text:
                sim = calculate_text_similarity(c_text, p_text)
                if sim >= threshold_text_similarity and iou >= 0.35:
                    logger.info(
                        "Dropping semantic duplicate clip (text sim %.2f, iou %.2f): '%s' vs '%s'",
                        sim, iou, c_text, p_text,
                    )
                    is_duplicate = True
                    break

        if not is_duplicate:
            kept_clips.append(candidate)

    return kept_clips
