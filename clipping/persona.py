"""
clipping.persona — Audience Persona Targeting & Niche Tuning Engine.

Tunes AI clip selection, virality ranking criteria, and visual typography
for specific audience demographics and content genres.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

PERSONAS: Dict[str, Dict[str, Any]] = {
    "general": {
        "name": "General Audience",
        "description": "Broad viral entertainment with high emotional resonance and broad appeal.",
        "font_style": "HORMOZI",
        "keyword_palette": "modern",
        "prompt_guidelines": (
            "Select clips with universal appeal, relatable human emotion, clear punchlines, "
            "and immediate 3-second visual or audio hooks."
        ),
    },
    "tech_founder": {
        "name": "Tech & Startup Founder",
        "description": "Engineers, entrepreneurs, and startup builders focused on SaaS, code, and growth.",
        "font_style": "STORYTELLER",
        "keyword_palette": "neon_cyber",
        "prompt_guidelines": (
            "Prioritize moments discussing architecture decisions, breakthrough engineering, "
            "scaling bottlenecks, fundraising, product-market fit, and contrarian startup lessons. "
            "Filter out generic platitudes; focus on tactical, high-signal insights."
        ),
    },
    "finance_investor": {
        "name": "Finance & Wealth Builder",
        "description": "Investors, crypto traders, and personal finance builders.",
        "font_style": "HORMOZI",
        "keyword_palette": "gold_amber",
        "prompt_guidelines": (
            "Prioritize moments discussing asymmetric risk/reward, wealth preservation, "
            "cash flow, compounding interest, economic cycles, and financial mistakes. "
            "Emphasize tangible numbers, percentages, and dollar figures in titles and hooks."
        ),
    },
    "creator_entertainment": {
        "name": "Creator & Pop Culture Entertainment",
        "description": "High-energy Gen-Z short-form content, gaming, reactions, and dynamic comedy.",
        "font_style": "CINEMATIC",
        "keyword_palette": "bold_red",
        "prompt_guidelines": (
            "Select clips with maximum energy spikes, funny reactions, unexpected plot twists, "
            "and intense dialogue. Prioritize tight pacing with zero dead air."
        ),
    },
    "education_explainer": {
        "name": "Deep-Dive Education & Science",
        "description": "Clear step-by-step conceptual breakdowns, science, history, and tutorials.",
        "font_style": "DEFAULT",
        "keyword_palette": "classic",
        "prompt_guidelines": (
            "Select clips that explain a complex phenomenon clearly and concisely. "
            "The clip must be self-contained: stating the problem, the core mechanism, and the conclusion."
        ),
    },
    "fitness_motivation": {
        "name": "Fitness & Discipline",
        "description": "Gym culture, athletic performance, mindset, and mental toughness.",
        "font_style": "HORMOZI",
        "keyword_palette": "bold_red",
        "prompt_guidelines": (
            "Focus on high-intensity grit, discipline over motivation, overcoming physical limits, "
            "and direct accountability talk that sparks an urgent desire to take action."
        ),
    },
}


def get_persona(persona_name: str = "general") -> Dict[str, Any]:
    """Retrieve configuration dict for the given persona name."""
    key = (persona_name or "general").lower().strip()
    return PERSONAS.get(key) or PERSONAS["general"]


def get_persona_prompt_instructions(persona_name: str = "general") -> str:
    """Get the targeted prompt directive to inject into LLM clip analysis."""
    p = get_persona(persona_name)
    return f"[Audience Persona: {p['name']}]\n{p['prompt_guidelines']}"


def list_personas() -> List[Dict[str, str]]:
    """Return all available persona definitions."""
    return [
        {"id": k, "name": v["name"], "description": v["description"]}
        for k, v in PERSONAS.items()
    ]
