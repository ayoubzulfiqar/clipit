"""
clipping.ai — Multi-provider AI abstraction, fallback chain, and cost tracking.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from .base import AIResult, BaseAIProvider, UsageMetadata
from .gemini import GeminiProvider
from .openai_compatible import NvidiaProvider, OllamaProvider, OpenAICompatibleProvider
from .anthropic import AnthropicProvider
from .fallback_chain import FallbackChainProvider

__all__ = [
    "BaseAIProvider",
    "AIResult",
    "UsageMetadata",
    "GeminiProvider",
    "NvidiaProvider",
    "OllamaProvider",
    "OpenAICompatibleProvider",
    "AnthropicProvider",
    "FallbackChainProvider",
    "get_ai_provider",
    "analyze_with_ai",
]


def get_ai_provider(provider_name: str = "gemini", cfg=None) -> BaseAIProvider:
    """
    Factory to return an AI provider instance.

    Supported provider names:
    - 'gemini': Google Gemini Flash / Pro
    - 'nvidia': NVIDIA NIM (LLaMA 3.1)
    - 'openai': OpenAI GPT-4o / GPT-4o-mini
    - 'ollama': Local offline LLM (Ollama)
    - 'anthropic': Claude 3.5 Sonnet / Haiku
    - 'auto' / 'chain': Prioritized fallback chain
    """
    name = (provider_name or "gemini").lower().strip()

    if name == "gemini":
        return GeminiProvider()
    elif name == "nvidia":
        return NvidiaProvider()
    elif name == "openai":
        return OpenAICompatibleProvider(
            name="openai",
            base_url="https://api.openai.com/v1",
            default_model="gpt-4o-mini",
            api_key_attr="api_key_openai",
            env_key="OPENAI_API_KEY",
        )
    elif name == "ollama":
        return OllamaProvider()
    elif name == "anthropic":
        return AnthropicProvider()
    elif name in ("auto", "chain", "fallback"):
        # Build automatic fallback chain based on active keys
        chain: List[BaseAIProvider] = []
        if cfg and getattr(cfg, "api_key_nvidia", None):
            chain.append(NvidiaProvider())
        chain.append(GeminiProvider())
        chain.append(OllamaProvider())
        return FallbackChainProvider(chain)
    else:
        # Default fallback to Gemini
        return GeminiProvider()


def analyze_with_ai(transcript: str, cfg) -> List[Dict[str, object]]:
    """
    Dispatch transcript analysis through configured AI provider or fallback chain.
    """
    provider_name = getattr(cfg, "ai_provider", "gemini")
    provider = get_ai_provider(provider_name, cfg=cfg)

    # If provider is not configured but a fallback chain is possible, use auto chain
    if not provider.is_configured(cfg):
        provider = get_ai_provider("auto", cfg=cfg)

    result = provider.analyze(transcript, cfg)
    return result.clips
