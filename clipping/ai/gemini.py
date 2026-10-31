"""
clipping.ai.gemini — Google Gemini AI provider implementation.
"""

from __future__ import annotations

import json
import time
from typing import Any, Dict, List, Optional

from .base import AIResult, BaseAIProvider, UsageMetadata

# Pricing per million tokens (approximate USD)
PRICING_PER_1M = {
    "gemini-2.0-flash": {"prompt": 0.10, "completion": 0.40},
    "gemini-1.5-flash": {"prompt": 0.075, "completion": 0.30},
    "gemini-1.5-pro": {"prompt": 1.25, "completion": 5.00},
}


class GeminiProvider(BaseAIProvider):
    name: str = "gemini"

    def is_configured(self, cfg) -> bool:
        key = getattr(cfg, "api_key_gemini", None)
        return bool(key and not key.startswith("your-") and not key.startswith("placeholder"))

    def estimate_cost(self, prompt_tokens: int, completion_tokens: int, model: str) -> float:
        rates = None
        for m_key, r in PRICING_PER_1M.items():
            if m_key in model.lower():
                rates = r
                break
        if not rates:
            rates = PRICING_PER_1M["gemini-1.5-flash"]

        cost = (prompt_tokens / 1_000_000 * rates["prompt"]) + (
            completion_tokens / 1_000_000 * rates["completion"]
        )
        return round(cost, 6)

    def analyze(self, transcript: str, cfg) -> AIResult:
        import google.genai as genai
        from google.genai import types
        from .. import engine

        key = getattr(cfg, "api_key_gemini", "")
        if not key:
            raise ValueError("GOOGLE_API_KEY is required for GeminiProvider.")

        client = genai.Client(api_key=key)
        prompt = engine.get_analysis_prompt(
            transcript, cfg.jumlah_clip, cfg.durasi_hook, cfg=cfg
        )

        model = getattr(cfg, "gemini_model", "gemini-2.5-flash")
        fallback_model = getattr(cfg, "gemini_fallback_model", "gemini-1.5-flash")

        # Reuse existing robust JSON schema generator
        clips = engine.analyze_with_gemini(transcript, cfg)

        # Estimate usage from length if API doesn't expose usage directly
        prompt_tokens_est = max(1, len(prompt) // 4)
        completion_tokens_est = max(1, len(json.dumps(clips)) // 4)
        cost = self.estimate_cost(prompt_tokens_est, completion_tokens_est, model)

        usage = UsageMetadata(
            prompt_tokens=prompt_tokens_est,
            completion_tokens=completion_tokens_est,
            total_tokens=prompt_tokens_est + completion_tokens_est,
            estimated_cost_usd=cost,
        )

        return AIResult(
            clips=clips,
            provider_name=self.name,
            model_name=model,
            usage=usage,
        )
