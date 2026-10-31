"""
clipping.studio.thumbnail — Multi-variant A/B thumbnail generation with CTR optimization.
"""

from __future__ import annotations

import os
import subprocess
import textwrap
import urllib.request
from typing import List, Optional

try:
    import cv2
except ImportError:
    cv2 = None

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    Image = None
    ImageDraw = None
    ImageFont = None

from clipping.logger import get_logger

logger = get_logger("clipping.studio.thumbnail")


def _extract_frame_ffmpeg(video_path: str, timestamp_sec: float, output_path: str) -> bool:
    """Extract a single frame using FFmpeg as a reliable fallback."""
    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-ss",
        str(max(0.1, timestamp_sec)),
        "-i",
        video_path,
        "-vframes",
        "1",
        "-q:v",
        "2",
        output_path,
    ]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        return os.path.exists(output_path) and os.path.getsize(output_path) > 0
    except Exception as exc:
        logger.warning("FFmpeg frame extraction failed at %ss: %s", timestamp_sec, exc)
        return False


def _get_video_duration(video_path: str) -> float:
    """Query video duration using ffprobe."""
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        video_path,
    ]
    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, check=True)
        return max(1.0, float(proc.stdout.strip()))
    except Exception:
        return 10.0


def _extract_frame_rgb(video_path: str, timestamp_sec: float) -> Optional[Image.Image]:
    """Extract video frame at timestamp as PIL RGB Image."""
    if Image is None:
        return None

    # Try cv2 first if available
    if cv2 is not None:
        try:
            cap = cv2.VideoCapture(video_path)
            cap.set(cv2.CAP_PROP_POS_MSEC, int(timestamp_sec * 1000))
            ret, frame = cap.read()
            cap.release()
            if ret and frame is not None:
                return Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        except Exception:
            pass

    # Fallback to FFmpeg frame extraction
    tmp_jpg = f"{video_path}.tmp_thumb_{int(timestamp_sec * 1000)}.jpg"
    try:
        if _extract_frame_ffmpeg(video_path, timestamp_sec, tmp_jpg):
            with Image.open(tmp_jpg) as img:
                return img.convert("RGB")
    finally:
        if os.path.exists(tmp_jpg):
            os.remove(tmp_jpg)

    return None


def _ensure_font(cfg) -> Optional[str]:
    """Ensure thumbnail font file exists locally."""
    font_path = getattr(cfg, "file_font_thumbnail", "assets/fonts/KomikaAxis.ttf")
    font_url = getattr(cfg, "url_font_thumbnail", None)

    if not os.path.exists(font_path) and font_url:
        try:
            os.makedirs(os.path.dirname(os.path.abspath(font_path)), exist_ok=True)
            urllib.request.urlretrieve(font_url, font_path)
        except Exception as exc:
            logger.warning("Failed to download thumbnail font: %s", exc)
            return None

    return font_path if os.path.exists(font_path) else None


def buat_thumbnail(video_path: str, output_image_path: str, teks: str, cfg) -> Optional[str]:
    """
    Extract a frame from the video, composite the clip title on top, and save as a thumbnail image.
    Preserves backwards compatibility with legacy clip rendering.
    """
    variants = buat_thumbnail_variants(video_path, output_image_path, teks, cfg, count=1)
    return variants[0] if variants else None


def buat_thumbnail_variants(
    video_path: str,
    output_image_path: str,
    teks: str,
    cfg,
    count: int = 3,
) -> List[str]:
    """
    Generate multiple distinct thumbnail variants (A/B testing candidates):
    - Variant A (Hook / Center): High-contrast centered punchy headline at ~1.5s.
    - Variant B (Action / Lower-Third): Taken at ~40% duration, bottom badge card with accent highlight.
    - Variant C (Climax / Top-Header): Taken at ~70% duration, top banner style.

    Returns:
        List of generated JPEG file paths.
    """
    if Image is None or ImageDraw is None:
        logger.warning("Pillow is not installed. Skipping thumbnail generation.")
        return []

    font_path = _ensure_font(cfg)
    clip_dur = _get_video_duration(video_path)

    # Candidate timestamps for variants
    timestamps = [
        min(1.5, clip_dur * 0.15),           # Variant A: hook start
        min(clip_dur * 0.45, clip_dur - 0.5), # Variant B: core action/midpoint
        min(clip_dur * 0.75, clip_dur - 0.2), # Variant C: climax/reaction
    ]

    base_no_ext, ext = os.path.splitext(output_image_path)
    if not ext:
        ext = ".jpg"

    generated_paths: List[str] = []
    count = max(1, min(count, 3))

    for idx in range(count):
        ts = timestamps[idx]
        out_path = output_image_path if idx == 0 else f"{base_no_ext}_{chr(97 + idx)}{ext}"
        frame_img = _extract_frame_rgb(video_path, ts)
        if frame_img is None:
            continue

        w, h = frame_img.size
        draw_img = frame_img.convert("RGBA")

        # 1. Overlay style per variant
        if idx == 0:
            # Variant A: Subtle 45% dark vignette across entire frame
            overlay = Image.new("RGBA", (w, h), (0, 0, 0, 115))
            draw_img = Image.alpha_composite(draw_img, overlay)
            draw = ImageDraw.Draw(draw_img)

            font_sz = max(24, int(w * 0.11))
            try:
                font = ImageFont.truetype(font_path, font_sz) if font_path else ImageFont.load_default()
            except Exception:
                font = ImageFont.load_default()

            lines = textwrap.wrap(teks.upper(), width=13)
            total_text_h = len(lines) * (font_sz + 12)
            y_start = (h - total_text_h) // 2

            for line in lines:
                bbox = draw.textbbox((0, 0), line, font=font)
                line_w = bbox[2] - bbox[0]
                x_text = (w - line_w) // 2
                draw.text(
                    (x_text, y_start),
                    line,
                    font=font,
                    fill="#FFFF00",
                    stroke_width=max(3, int(font_sz * 0.08)),
                    stroke_fill="#000000",
                )
                y_start += font_sz + 12

        elif idx == 1:
            # Variant B: Lower-third gradient badge card
            card_h = int(h * 0.35)
            overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            overlay_draw.rectangle([(0, h - card_h), (w, h)], fill=(10, 10, 20, 210))
            draw_img = Image.alpha_composite(draw_img, overlay)
            draw = ImageDraw.Draw(draw_img)

            font_sz = max(22, int(w * 0.095))
            try:
                font = ImageFont.truetype(font_path, font_sz) if font_path else ImageFont.load_default()
            except Exception:
                font = ImageFont.load_default()

            lines = textwrap.wrap(teks, width=15)
            y_start = h - card_h + int(card_h * 0.18)

            for line in lines:
                bbox = draw.textbbox((0, 0), line, font=font)
                line_w = bbox[2] - bbox[0]
                x_text = (w - line_w) // 2
                draw.text(
                    (x_text, y_start),
                    line,
                    font=font,
                    fill="#FFFFFF",
                    stroke_width=max(2, int(font_sz * 0.06)),
                    stroke_fill="#000000",
                )
                y_start += font_sz + 10

        else:
            # Variant C: Top-third banner headline
            card_h = int(h * 0.28)
            overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            overlay_draw.rectangle([(0, 0), (w, card_h)], fill=(220, 20, 60, 225))  # Crimson badge
            draw_img = Image.alpha_composite(draw_img, overlay)
            draw = ImageDraw.Draw(draw_img)

            font_sz = max(22, int(w * 0.09))
            try:
                font = ImageFont.truetype(font_path, font_sz) if font_path else ImageFont.load_default()
            except Exception:
                font = ImageFont.load_default()

            lines = textwrap.wrap(teks.upper(), width=14)
            y_start = (card_h - (len(lines) * (font_sz + 8))) // 2

            for line in lines:
                bbox = draw.textbbox((0, 0), line, font=font)
                line_w = bbox[2] - bbox[0]
                x_text = (w - line_w) // 2
                draw.text(
                    (x_text, y_start),
                    line,
                    font=font,
                    fill="#FFFFFF",
                    stroke_width=max(2, int(font_sz * 0.05)),
                    stroke_fill="#000000",
                )
                y_start += font_sz + 8

        final_rgb = draw_img.convert("RGB")
        os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
        final_rgb.save(out_path, quality=92)
        generated_paths.append(out_path)

    return generated_paths
