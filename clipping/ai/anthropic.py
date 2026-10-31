"""
clipping.ai.anthropic — Anthropic Claude AI provider.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

from .base import AIResult, BaseAIProvider, UsageMetadata

ANTHROPIC_PRICING = {
    "claude-3-5-sonnet": {"prompt": 3.00, "completion": 15.00},
    "claude-3-5-haiku": {"prompt": 1.00, "completion": 5.00},
}


class AnthropicProvider(BaseAIProvider):
    name: str = "anthropic"

    def is_configured(self, cfg) -> bool:
        key = getattr(cfg, "api_key_anthropic", None) or os.environ.get("ANTHROPIC_API_KEY", "")
        return bool(key and not key.startswith("your-") and not key.startswith("placeholder"))

    def estimate_cost(self, prompt_tokens: int, completion_tokens: int, model: str) -> float:
        rates = ANTHROPIC_PRICING.get(model, {"prompt": 3.00, "completion": 15.00})
        cost = (prompt_tokens / 1_000_000 * rates["prompt"]) + (
            completion_tokens / 1_000_000 * rates["completion"]
        )
        return round(cost, 6)

    def analyze(self, transcript: str, cfg) -> AIResult:
        try:
            import anthropic
        except ImportError:
            raise RuntimeError("anthropic package is required: pip install anthropic")

        from .. import engine

        key = getattr(cfg, "api_key_anthropic", None) or os.environ.get("ANTHROPIC_API_KEY", "")
        if not key:
            raise ValueError("ANTHROPIC_API_KEY is required.")

        model = getattr(cfg, "anthropic_model", "claude-3-5-haiku-20241022")
        client = anthropic.Anthropic(api_key=key)

        prompt = engine.get_analysis_prompt(
            transcript, cfg.jumlah_clip, cfg.durasi_hook, cfg=cfg
        )

        message = client.messages.create(
            model=model,
            max_tokens=4096,
            temperature=0.2,
            system="You are an elite video editor and viral short-form strategist. Return only a valid JSON array of clips.",
            messages=[{"role": "user", "content": prompt}],
        )

        content = message.content[0].text if message.content else ""
        cleaned = content.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]

        clips = json.loads(cleaned.strip())
        prompt_tokens = message.usage.input_tokens
        completion_tokens = message.usage.output_tokens
        cost = self.estimate_cost(prompt_tokens, completion_tokens, model)

        usage = UsageMetadata(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            estimated_cost_usd=cost,
        )

        return AIResult(
            clips=clips,
            provider_name=self.name,
            model_name=model,
            usage=usage,
        )
