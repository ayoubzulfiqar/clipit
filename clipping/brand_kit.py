"""
clipping.brand_kit — Brand Kit management for consistent logos, palettes, typography, and bumpers.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional

from clipping.logger import get_logger

logger = get_logger("clipping.brand_kit")


@dataclass
class BrandKit:
    name: str = "Default Brand"
    logo_path: Optional[str] = None
    logo_position: str = "top_right"  # top_left, top_right, bottom_left, bottom_right, center
    logo_opacity: float = 0.85
    logo_scale: float = 0.15
    primary_color: str = "&H00FFFF&"  # ASS format or hex (#FFFF00)
    secondary_color: str = "&HFFFFFF&"
    accent_color: str = "&H00A5FF&"
    font_name: Optional[str] = None
    intro_bumper_path: Optional[str] = None
    outro_bumper_path: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> BrandKit:
        valid_keys = cls.__dataclass_fields__.keys()
        filtered = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered)

    @classmethod
    def load_from_file(cls, path: str) -> BrandKit:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Brand kit file not found: {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)

    def save_to_file(self, path: str) -> None:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    def apply_to_config(self, cfg) -> None:
        """
        Inject brand kit settings into ClipitConfig runtime configuration.
        """
        if self.logo_path and os.path.exists(self.logo_path):
            cfg.watermark_image = self.logo_path
            cfg.watermark_anchor = self.logo_position
            cfg.watermark_opacity = self.logo_opacity
            cfg.watermark_scale = self.logo_scale

        if self.primary_color:
            cfg.warna_kata_khusus = self._normalize_ass_color(self.primary_color)

        if self.intro_bumper_path and os.path.exists(self.intro_bumper_path):
            cfg.intro_bumper = self.intro_bumper_path

        if self.outro_bumper_path and os.path.exists(self.outro_bumper_path):
            cfg.outro_bumper = self.outro_bumper_path

    @staticmethod
    def _normalize_ass_color(color_str: str) -> str:
        """Convert standard #RRGGBB hex into ASS format &HBBGGRR&."""
        c = color_str.strip()
        if c.startswith("&H") and c.endswith("&"):
            return c
        if c.startswith("#") and len(c) == 7:
            r = c[1:3]
            g = c[3:5]
            b = c[5:7]
            return f"&H{b}{g}{r}&".upper()
        return c
