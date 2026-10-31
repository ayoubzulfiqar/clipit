"""
clipping.ai.base — Base interface for AI LLM providers and cost tracking.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class UsageMetadata:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_usd: float = 0.0


@dataclass
class AIResult:
    clips: List[Dict[str, Any]]
    provider_name: str
    model_name: str
    usage: UsageMetadata = field(default_factory=UsageMetadata)


class BaseAIProvider(ABC):
    """Abstract base class for LLM video analysis providers."""

    name: str = "base"

    @abstractmethod
    def analyze(self, transcript: str, cfg) -> AIResult:
        """
        Analyze full transcript to extract and score viral moments.

        Returns AIResult containing structured clip dictionaries and usage data.
        """
        pass

    @abstractmethod
    def is_configured(self, cfg) -> bool:
        """Returns True if required credentials and models are configured."""
        pass

    def estimate_cost(self, prompt_tokens: int, completion_tokens: int, model: str) -> float:
        """Estimate cost in USD based on model pricing (default 0.0 for local/free)."""
        return 0.0
