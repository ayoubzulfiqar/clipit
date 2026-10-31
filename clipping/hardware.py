"""
clipping.hardware — Accelerator and GPU hardware detection and auto-configuration.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Dict, Optional, Tuple


@dataclass
class HardwareProfile:
    device: str
    compute_type: str
    cuda_available: bool
    gpu_name: Optional[str] = None
    gpu_count: int = 0
    vram_total_gb: Optional[float] = None
    vram_free_gb: Optional[float] = None

    def to_dict(self) -> Dict[str, object]:
        return {
            "device": self.device,
            "compute_type": self.compute_type,
            "cuda_available": self.cuda_available,
            "gpu_name": self.gpu_name,
            "gpu_count": self.gpu_count,
            "vram_total_gb": self.vram_total_gb,
            "vram_free_gb": self.vram_free_gb,
        }


def detect_hardware() -> HardwareProfile:
    """
    Detect optimal compute device and compute_type for Whisper and Pyannote.
    Prefers CUDA GPU when available, otherwise falls back gracefully to CPU.
    """
    # 1. Try PyTorch CUDA check
    try:
        import torch

        if torch.cuda.is_available():
            count = torch.cuda.device_count()
            name = torch.cuda.get_device_name(0)
            mem_total = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            # Try to get free memory
            try:
                free_bytes, total_bytes = torch.cuda.mem_get_info(0)
                mem_free = free_bytes / (1024**3)
            except Exception:
                mem_free = None

            return HardwareProfile(
                device="cuda",
                compute_type="float16",
                cuda_available=True,
                gpu_name=name,
                gpu_count=count,
                vram_total_gb=round(mem_total, 2),
                vram_free_gb=round(mem_free, 2) if mem_free is not None else None,
            )
    except Exception:
        pass

    # 2. Try ctranslate2 CUDA check as fallback if torch is not installed
    try:
        import ctranslate2

        count = ctranslate2.get_cuda_device_count()
        if count > 0:
            return HardwareProfile(
                device="cuda",
                compute_type="float16",
                cuda_available=True,
                gpu_name=f"CUDA Accelerator ({count} device{'s' if count > 1 else ''})",
                gpu_count=count,
            )
    except Exception:
        pass

    # 3. CPU Fallback (int8 is optimal for CPU inference)
    return HardwareProfile(
        device="cpu",
        compute_type="int8",
        cuda_available=False,
        gpu_name=None,
        gpu_count=0,
    )


def resolve_whisper_device(requested_device: str, requested_compute: Optional[str] = None) -> Tuple[str, str]:
    """
    Resolve requested Whisper device and compute_type against available hardware.

    Returns:
        tuple of (resolved_device, resolved_compute_type)
    """
    profile = detect_hardware()
    req = (requested_device or "auto").lower().strip()

    if req == "auto":
        return profile.device, requested_compute if requested_compute else profile.compute_type

    if req == "cuda":
        if not profile.cuda_available:
            # Automatic fallback to CPU
            return "cpu", "int8"
        return "cuda", requested_compute if requested_compute else "float16"

    # CPU explicitly requested
    return "cpu", requested_compute if requested_compute else "int8"
