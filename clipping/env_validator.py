"""
clipping.env_validator — Environment variable and secret validation utility.

Validates that all necessary API keys and runtime tokens are present, non-placeholder,
and properly configured for requested pipeline features.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional


PLACEHOLDER_SUBSTRINGS = (
    "your-",
    "your_",
    "here",
    "placeholder",
    "xxx",
    "11111111",
)


@dataclass
class EnvValidationReport:
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    active_providers: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, object]:
        return {
            "is_valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "active_providers": self.active_providers,
        }


def _is_placeholder_or_empty(val: Optional[str]) -> bool:
    if not val or not val.strip():
        return True
    lower = val.lower().strip()
    return any(p in lower for p in PLACEHOLDER_SUBSTRINGS)


def validate_environment(
    env: Optional[Dict[str, str]] = None,
    require_ai: bool = True,
    require_broll: bool = False,
    require_podcast: bool = False,
    require_meta: bool = False,
    ai_provider: str = "gemini",
) -> EnvValidationReport:
    """
    Validate environment variables and API keys.

    Parameters
    ----------
    env : dict, optional
        Dictionary of environment variables to test. Defaults to `os.environ`.
    require_ai : bool
        Whether AI provider keys must be valid.
    require_broll : bool
        Whether Pexels key is strictly required.
    require_podcast : bool
        Whether HuggingFace token for Pyannote is strictly required.
    require_meta : bool
        Whether Facebook Meta Graph API tokens are required.
    ai_provider : str
        Target AI provider ('gemini' or 'nvidia').
    """
    env_map = env if env is not None else os.environ
    errors: List[str] = []
    warnings: List[str] = []
    active_providers: List[str] = []

    # 1. AI Provider Key
    gemini_key = env_map.get("GOOGLE_API_KEY", "").strip()
    nvidia_key = env_map.get("NVIDIA_API_KEY", "").strip()

    if ai_provider == "gemini":
        if _is_placeholder_or_empty(gemini_key):
            msg = "GOOGLE_API_KEY is missing or contains placeholder. Set via .env or export GOOGLE_API_KEY='...'"
            if require_ai:
                errors.append(msg)
            else:
                warnings.append(msg)
        else:
            active_providers.append("gemini")
    elif ai_provider == "nvidia":
        if _is_placeholder_or_empty(nvidia_key):
            msg = "NVIDIA_API_KEY is missing or contains placeholder. Set via .env or export NVIDIA_API_KEY='...'"
            if require_ai:
                errors.append(msg)
            else:
                warnings.append(msg)
        else:
            active_providers.append("nvidia")

    # 2. B-Roll (Pexels)
    pexels_key = env_map.get("PEXELS_API_KEY", "").strip()
    if _is_placeholder_or_empty(pexels_key):
        msg = "PEXELS_API_KEY not configured. B-roll footage generation will be skipped."
        if require_broll:
            errors.append(msg)
        else:
            warnings.append(msg)
    else:
        active_providers.append("pexels")

    # 3. Speaker Diarization (Pyannote / HuggingFace)
    hf_token = env_map.get("HF_TOKEN", "").strip()
    if _is_placeholder_or_empty(hf_token):
        msg = "HF_TOKEN not configured. Split-screen and camera-switch modes requiring Pyannote will fallback to regular view."
        if require_podcast:
            errors.append(msg)
        else:
            warnings.append(msg)
    else:
        active_providers.append("pyannote")

    # 4. Meta / Facebook Graph API
    meta_token = env_map.get("META_PAGE_ACCESS_TOKEN", "").strip()
    meta_page_id = env_map.get("META_PAGE_ID", "").strip()
    if _is_placeholder_or_empty(meta_token) or _is_placeholder_or_empty(meta_page_id):
        msg = "META_PAGE_ACCESS_TOKEN or META_PAGE_ID not configured for Facebook Reel uploader."
        if require_meta:
            errors.append(msg)
        else:
            warnings.append(msg)
    else:
        active_providers.append("meta")

    is_valid = len(errors) == 0
    return EnvValidationReport(
        is_valid=is_valid,
        errors=errors,
        warnings=warnings,
        active_providers=active_providers,
    )
