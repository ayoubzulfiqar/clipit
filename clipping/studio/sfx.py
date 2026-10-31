"""
clipping.studio.sfx — Dynamic Sound Effects (SFX) Compositing Engine.

Synthesizes and composites impactful sound effects (whooshes, risers, impacts, pops)
for hook transitions, punchlines, and kinetic subtitle pops using either local assets
or native FFmpeg audio synthesis.
"""

from __future__ import annotations

import os
import random
import subprocess
from typing import Dict, List, Optional, Tuple

from clipping.logger import get_logger

logger = get_logger("clipping.studio.sfx")

# Supported SFX types
SFX_TYPES = ("whoosh", "impact", "riser", "pop")


def get_local_sfx_file(sfx_type: str, sfx_dir: Optional[str] = None) -> Optional[str]:
    """
    Look for a user-provided sound effect file in assets/sfx/<sfx_type>/
    """
    if not sfx_dir:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        sfx_dir = os.path.join(base_dir, "assets", "sfx")

    target_dir = os.path.join(sfx_dir, sfx_type)
    if not os.path.isdir(target_dir):
        return None

    audio_files = [
        f for f in os.listdir(target_dir)
        if f.lower().endswith((".mp3", ".wav", ".aac", ".ogg"))
    ]
    if not audio_files:
        return None

    return os.path.join(target_dir, random.choice(audio_files))


def get_synthetic_sfx_eval(sfx_type: str, duration: float = 0.3, volume: float = 0.35) -> str:
    """
    Generate an FFmpeg filter source string that synthesizes sound effects in-memory.
    Zero external files required.
    """
    sfx = sfx_type.lower()
    vol_clamped = max(0.01, min(1.0, volume))

    if sfx == "whoosh":
        # Filtered pink noise sweep creating a smooth rush of air
        return (
            f"anoisesrc=d={duration:.2f}:c=pink:r=48000, "
            f"bandpass=f=1000:width_type=h:w=800, "
            f"afade=t=in:ss=0:d={duration * 0.4:.2f}, "
            f"afade=t=out:st={duration * 0.4:.2f}:d={duration * 0.6:.2f}, "
            f"volume={vol_clamped:.2f}"
        )
    elif sfx == "impact":
        # Deep bass punch with quick attack and low-end decay
        return (
            f"aevalsrc=expr='sin(2*PI*(80 - 40*t)*t)*exp(-8*t)':d={duration:.2f}:s=48000, "
            f"afade=t=out:st={duration * 0.2:.2f}:d={duration * 0.8:.2f}, "
            f"volume={vol_clamped * 1.5:.2f}"
        )
    elif sfx == "riser":
        # Pitch-ascending sine sweep for dramatic tension
        dur = max(0.6, duration)
        return (
            f"aevalsrc=expr='sin(2*PI*(200 + 700*t)*t)':d={dur:.2f}:s=48000, "
            f"afade=t=in:ss=0:d={dur * 0.3:.2f}, "
            f"afade=t=out:st={dur * 0.7:.2f}:d={dur * 0.3:.2f}, "
            f"volume={vol_clamped:.2f}"
        )
    elif sfx == "pop":
        # Short crisp pop for text or emoji appearance
        pop_dur = min(0.12, duration)
        return (
            f"aevalsrc=expr='sin(2*PI*880*t)*exp(-30*t)':d={pop_dur:.2f}:s=48000, "
            f"afade=t=out:st=0.02:d={pop_dur - 0.02:.2f}, "
            f"volume={vol_clamped:.2f}"
        )
    else:
        # Fallback gentle chime
        return f"sine=f=440:d={duration:.2f}, volume={vol_clamped:.2f}"


def generate_synthetic_sfx_file(
    output_path: str,
    sfx_type: str = "whoosh",
    duration: float = 0.35,
    volume: float = 0.5,
) -> bool:
    """
    Render a synthesized SFX to a standalone .wav or .mp3 file using FFmpeg.
    """
    filter_expr = get_synthetic_sfx_eval(sfx_type, duration=duration, volume=volume)
    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-f",
        "lavfi",
        "-i",
        filter_expr,
        "-t",
        f"{duration:.2f}",
        output_path,
    ]

    try:
        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=False)
        return res.returncode == 0
    except Exception as exc:
        logger.warning("Failed to synthesize SFX '%s' to %s: %s", sfx_type, output_path, exc)
        return False


def build_sfx_mix_filter(
    base_audio_label: str = "[voc]",
    sfx_cues: Optional[List[Dict]] = None,
    default_volume: float = 0.35,
) -> Tuple[str, str]:
    """
    Construct an FFmpeg audio filter segment that overlays SFX at specific timestamps.

    Args:
        base_audio_label: FFmpeg input label for main speech/audio, e.g. '[voc]'
        sfx_cues: List of dicts with keys:
                  'type': 'whoosh' | 'impact' | 'riser' | 'pop'
                  'timestamp': float (in seconds)
                  'volume': optional float
        default_volume: Volume multiplier for SFX

    Returns:
        (filter_string, output_label)
    """
    if not sfx_cues:
        return f"{base_audio_label}anull[a_sfx_out]", "[a_sfx_out]"

    filter_chains = []
    mix_inputs = [base_audio_label]

    for idx, cue in enumerate(sfx_cues):
        sfx_type = cue.get("type", "whoosh")
        ts = max(0.0, float(cue.get("timestamp", 0.0)))
        vol = float(cue.get("volume", default_volume))
        dur = float(cue.get("duration", 0.35))

        synth_expr = get_synthetic_sfx_eval(sfx_type, duration=dur, volume=vol)
        label = f"[sfx_{idx}]"
        delay_ms = int(ts * 1000)

        # Generate audio source, format, and apply delay
        chain = f"{synth_expr}, aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo, adelay={delay_ms}|{delay_ms}{label}"
        filter_chains.append(chain)
        mix_inputs.append(label)

    # Mix main audio and all delayed SFX nodes together
    inputs_str = "".join(mix_inputs)
    mix_chain = f"{inputs_str}amix=inputs={len(mix_inputs)}:duration=first:dropout_transition=0[a_sfx_out]"
    filter_chains.append(mix_chain)

    return "; ".join(filter_chains), "[a_sfx_out]"
