"""
clipping.ai.fallback_chain — Resilient fallback chain across multiple LLM providers.
"""

from __future__ import annotations

from typing import List, Optional

from .base import AIResult, BaseAIProvider
from ..logger import get_logger

logger = get_logger("clipit.ai.chain")


class FallbackChainProvider(BaseAIProvider):
    name: str = "fallback_chain"

    def __init__(self, providers: List[BaseAIProvider]):
        self.providers = providers

    def is_configured(self, cfg) -> bool:
        return any(p.is_configured(cfg) for p in self.providers)

    def analyze(self, transcript: str, cfg) -> AIResult:
        errors = []
        for provider in self.providers:
            if not provider.is_configured(cfg):
                logger.debug(f"Provider '{provider.name}' is not configured. Skipping in fallback chain.")
                continue

            try:
                logger.info(f"Attempting video analysis with AI provider '{provider.name}'...")
                result = provider.analyze(transcript, cfg)
                logger.info(
                    f"AI analysis succeeded via '{provider.name}' | "
                    f"clips={len(result.clips)} | cost=${result.usage.estimated_cost_usd:.4f}"
                )
                return result
            except Exception as exc:
                logger.warning(
                    f"AI provider '{provider.name}' failed with error: {exc}. "
                    f"Falling back to next provider in chain..."
                )
                errors.append(f"{provider.name}: {exc}")

        raise RuntimeError(
            f"All AI providers in fallback chain failed. Errors: {'; '.join(errors)}"
        )
