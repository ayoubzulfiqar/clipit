"""
clipping.vision_scoring — Multimodal Frame & Thumbnail Quality Analyzer

Analyzes candidate video frames for visual sharpness (Laplacian gradient variance),
brightness adequacy, contrast dynamic range, and compositional quality to automatically
select and rank the highest-converting thumbnail moments for short-form clips.
"""

from __future__ import annotations

import math
import os
import subprocess
from typing import Any, Dict, List, Optional, Union

from PIL import Image


def _get_pixel_list(gray_img: Image.Image) -> List[int]:
    """Retrieve flat list of pixel values supporting Pillow 10+ and 14+."""
    if hasattr(gray_img, "get_flattened_data"):
        return list(gray_img.get_flattened_data())
    return list(gray_img.getdata())


def compute_brightness_score(gray_img: Image.Image) -> float:
    """
    Score brightness adequacy on a 0-100 scale.
    Optimal average luminance is centered around 110-150. Extreme dark or light is penalized.
    """
    pixels = _get_pixel_list(gray_img)
    if not pixels:
        return 0.0
    mean_val = sum(pixels) / len(pixels)

    # Ideal target luminance ~130
    diff = abs(mean_val - 130.0)
    # Quadratic falloff
    score = max(0.0, 100.0 - (diff ** 2) / 80.0)
    return round(score, 2)


def compute_contrast_score(gray_img: Image.Image) -> float:
    """
    Score dynamic range / contrast on a 0-100 scale based on standard deviation.
    Higher contrast gives punchier thumbnails.
    """
    pixels = _get_pixel_list(gray_img)
    if len(pixels) < 2:
        return 0.0
    mean_val = sum(pixels) / len(pixels)
    variance = sum((p - mean_val) ** 2 for p in pixels) / len(pixels)
    std_dev = math.sqrt(variance)

    # Standard deviations between 40-75 are vibrant; score up to 100
    score = min(100.0, (std_dev / 65.0) * 100.0)
    return round(score, 2)


def compute_sharpness_score(gray_img: Image.Image) -> float:
    """
    Compute edge gradient sharpness using discrete 2D spatial gradients (Sobel/Laplacian proxy).
    Higher values represent crisp details; low values indicate motion blur.
    """
    width, height = gray_img.size
    if width < 3 or height < 3:
        return 0.0

    pixels = gray_img.load()
    diff_sum = 0.0
    count = 0

    # Sample rows & columns (stride 2 for performance)
    for y in range(1, height - 1, 2):
        for x in range(1, width - 1, 2):
            dx = int(pixels[x + 1, y]) - int(pixels[x - 1, y])
            dy = int(pixels[x, y + 1]) - int(pixels[x, y - 1])
            diff_sum += (dx * dx + dy * dy)
            count += 1

    if count == 0:
        return 0.0

    avg_gradient = diff_sum / count
    # Scale: an average gradient variance of 1500+ is exceptionally sharp
    score = min(100.0, (avg_gradient / 1200.0) * 100.0)
    return round(score, 2)


def score_frame(image_or_path: Union[str, Image.Image]) -> Dict[str, Any]:
    """
    Score a video frame for visual appeal and thumbnail fitness.
    
    Returns:
      {
        "composite_score": float (0-100),
        "sharpness": float,
        "contrast": float,
        "brightness": float,
        "is_blurry": bool,
      }
    """
    if isinstance(image_or_path, str):
        if not os.path.isfile(image_or_path):
            raise FileNotFoundError(f"Image not found: {image_or_path}")
        img = Image.open(image_or_path)
    else:
        img = image_or_path

    # Work in downscaled grayscale for high-performance evaluation
    gray = img.convert("L")
    if gray.width > 640:
        gray = gray.resize((480, int(480 * gray.height / gray.width)), Image.Resampling.BILINEAR)

    sharpness = compute_sharpness_score(gray)
    contrast = compute_contrast_score(gray)
    brightness = compute_brightness_score(gray)

    # Composite weight: 45% sharpness, 30% contrast, 25% brightness
    composite = (0.45 * sharpness) + (0.30 * contrast) + (0.25 * brightness)

    return {
        "composite_score": round(composite, 2),
        "sharpness": sharpness,
        "contrast": contrast,
        "brightness": brightness,
        "is_blurry": sharpness < 20.0,
    }


def extract_frame(
    video_path: str,
    timestamp_sec: float,
    output_path: str,
    ffmpeg_binary: str = "ffmpeg",
) -> bool:
    """Extract a single frame from video at timestamp using FFmpeg."""
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    cmd = [
        ffmpeg_binary,
        "-y",
        "-ss",
        f"{timestamp_sec:.2f}",
        "-i",
        video_path,
        "-frames:v",
        "1",
        "-q:v",
        "2",
        output_path,
    ]
    try:
        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return res.returncode == 0 and os.path.isfile(output_path)
    except Exception:
        return False


def rank_clip_frames(
    video_path: str,
    start_time: float,
    end_time: float,
    sample_count: int = 5,
    output_dir: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Sample candidate frames within a clip interval, score each, and return ranked list
    ordered descending by visual appeal composite score.
    """
    duration = max(0.1, end_time - start_time)
    step = duration / (sample_count + 1)
    results = []

    out_folder = output_dir or "/tmp/clipit_frames"
    os.makedirs(out_folder, exist_ok=True)

    for i in range(1, sample_count + 1):
        ts = start_time + (i * step)
        frame_name = f"frame_{int(ts * 1000)}.jpg"
        out_file = os.path.join(out_folder, frame_name)

        success = extract_frame(video_path, ts, out_file)
        if success and os.path.isfile(out_file):
            try:
                metrics = score_frame(out_file)
                metrics["timestamp"] = round(ts, 2)
                metrics["frame_path"] = out_file
                results.append(metrics)
            except Exception:
                pass

    results.sort(key=lambda r: r["composite_score"], reverse=True)
    return results
