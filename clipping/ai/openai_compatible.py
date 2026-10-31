"""
clipping.ai.openai_compatible — OpenAI-compatible provider (NVIDIA NIM, OpenAI, Ollama, vLLM).
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

from .base import AIResult, BaseAIProvider, UsageMetadata


OPENAI_PRICING = {
    "gpt-4o-mini": {"prompt": 0.15, "completion": 0.60},
    "gpt-4o": {"prompt": 2.50, "completion": 10.00},
}


class OpenAICompatibleProvider(BaseAIProvider):
    def __init__(
        self,
        name: str = "openai_compatible",
        base_url: Optional[str] = None,
        default_model: str = "gpt-4o-mini",
        api_key_attr: str = "api_key_openai",
        env_key: str = "OPENAI_API_KEY",
        is_local: bool = False,
    ):
        self.name = name
        self.base_url = base_url
        self.default_model = default_model
        self.api_key_attr = api_key_attr
        self.env_key = env_key
        self.is_local = is_local

    def is_configured(self, cfg) -> bool:
        if self.is_local:
            return True
        key = getattr(cfg, self.api_key_attr, None) or os.environ.get(self.env_key, "")
        return bool(key and not key.startswith("your-") and not key.startswith("placeholder"))

    def estimate_cost(self, prompt_tokens: int, completion_tokens: int, model: str) -> float:
        if self.is_local:
            return 0.0
        rates = OPENAI_PRICING.get(model, {"prompt": 0.20, "completion": 0.80})
        cost = (prompt_tokens / 1_000_000 * rates["prompt"]) + (
            completion_tokens / 1_000_000 * rates["completion"]
        )
        return round(cost, 6)

    def analyze(self, transcript: str, cfg) -> AIResult:
        try:
            from openai import OpenAI
        except ImportError:
            raise RuntimeError("openai package is required: pip install openai")

        from .. import engine

        key = getattr(cfg, self.api_key_attr, None) or os.environ.get(self.env_key, "ollama")
        base_url = getattr(cfg, f"{self.name}_base_url", self.base_url)
        model = getattr(cfg, f"{self.name}_model", self.default_model)

        client = OpenAI(base_url=base_url, api_key=key)

        prompt = engine.get_analysis_prompt(
            transcript, cfg.jumlah_clip, cfg.durasi_hook, cfg=cfg
        )

        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an elite video editor and viral content strategist. Return only a valid JSON array of clips.",
                },
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"} if "gpt-4" in model else None,
            temperature=0.2,
        )

        content = response.choices[0].message.content or ""
        # Clean markdown wrappers if present
        cleaned = content.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]

        parsed = json.loads(cleaned.strip())
        if isinstance(parsed, dict) and "clips" in parsed:
            clips = parsed["clips"]
        elif isinstance(parsed, list):
            clips = parsed
        else:
            raise ValueError("Unexpected JSON format from OpenAI-compatible provider.")

        prompt_tokens = response.usage.prompt_tokens if response.usage else len(prompt) // 4
        comp_tokens = response.usage.completion_tokens if response.usage else len(content) // 4
        cost = self.estimate_cost(prompt_tokens, comp_tokens, model)

        usage = UsageMetadata(
            prompt_tokens=prompt_tokens,
            completion_tokens=comp_tokens,
            total_tokens=prompt_tokens + comp_tokens,
            estimated_cost_usd=cost,
        )

        return AIResult(
            clips=clips,
            provider_name=self.name,
            model_name=model,
            usage=usage,
        )


class NvidiaProvider(OpenAICompatibleProvider):
    def __init__(self):
        super().__init__(
            name="nvidia",
            base_url="https://integrate.api.nvidia.com/v1",
            default_model="meta/llama-3.1-70b-instruct",
            api_key_attr="api_key_nvidia",
            env_key="NVIDIA_API_KEY",
            is_local=False,
        )

    def analyze(self, transcript: str, cfg) -> AIResult:
        from .. import engine

        model = getattr(cfg, "nvidia_model", self.default_model)
        clips = engine.analyze_with_nvidia(transcript, cfg)
        return AIResult(
            clips=clips,
            provider_name=self.name,
            model_name=model,
            usage=UsageMetadata(estimated_cost_usd=0.0),
        )


class OllamaProvider(OpenAICompatibleProvider):
    """Local, offline LLM provider using Ollama's local OpenAI-compatible endpoint."""

    def __init__(self):
        super().__init__(
            name="ollama",
            base_url=os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
            default_model=os.environ.get("OLLAMA_MODEL", "llama3.2"),
            api_key_attr="api_key_ollama",
            env_key="OLLAMA_API_KEY",
            is_local=True,
        )
