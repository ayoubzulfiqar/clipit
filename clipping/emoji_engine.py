"""
clipping.emoji_engine — Transcript Semantic Emoji & Dynamic Keyword Coloring Engine.

Analyzes spoken words in transcripts and injects contextual animated emojis and
thematic keyword color highlights into the subtitle and metadata streams.
"""

from __future__ import annotations

import re
import string
from typing import Dict, List, Optional, Tuple

from clipping.logger import get_logger

logger = get_logger("clipping.emoji_engine")

# Semantic keyword to emoji dictionary (English + Indonesian)
SEMANTIC_EMOJI_MAP: Dict[str, str] = {
    # Money, Wealth & Finance
    "money": "💰",
    "cash": "💰",
    "dollar": "💵",
    "dollars": "💵",
    "rich": "🤑",
    "wealth": "💎",
    "profit": "📈",
    "revenue": "📈",
    "sales": "💸",
    "earn": "💰",
    "earning": "💰",
    "salary": "💰",
    "million": "💰",
    "billion": "🏦",
    "invest": "📈",
    "investment": "📈",
    "crypto": "🪙",
    "bitcoin": "🪙",
    "uang": "💰",
    "duit": "💰",
    "cuan": "💸",
    "kaya": "🤑",
    "untung": "📈",
    "modal": "💵",
    "gaji": "💰",
    "omset": "📈",
    "bisnis": "💼",

    # Fire, Viral & Excitement
    "fire": "🔥",
    "lit": "🔥",
    "viral": "🔥",
    "trending": "🔥",
    "explode": "💥",
    "explosion": "💥",
    "blast": "💥",
    "boom": "💥",
    "burning": "🔥",
    "hot": "🔥",
    "api": "🔥",
    "panas": "🔥",
    "meledak": "💥",

    # Rocket, Speed & Rapid Growth
    "rocket": "🚀",
    "moon": "🚀",
    "scale": "🚀",
    "growth": "📈",
    "grow": "🌱",
    "fast": "⚡",
    "speed": "⚡",
    "quick": "⚡",
    "lightning": "⚡",
    "launch": "🚀",
    "roket": "🚀",
    "cepat": "⚡",
    "kilat": "⚡",
    "naik": "📈",
    "tumbuh": "🌱",

    # Shock, Mindblown & Disbelief
    "shock": "🤯",
    "shocked": "🤯",
    "mindblown": "🤯",
    "omg": "😱",
    "insane": "🤯",
    "crazy": "🤪",
    "unbelievable": "🤯",
    "wtf": "😱",
    "gila": "🤯",
    "kaget": "😱",
    "terkejut": "🤯",
    "ngeri": "😱",
    "parah": "🤯",

    # Warning, Alert, Danger & Stop
    "warning": "⚠️",
    "danger": "⚠️",
    "dangerous": "⚠️",
    "careful": "⚠️",
    "beware": "⚠️",
    "alert": "🚨",
    "emergency": "🚨",
    "stop": "🛑",
    "freeze": "🧊",
    "watchout": "👀",
    "bahaya": "⚠️",
    "awas": "⚠️",
    "peringatan": "🚨",
    "waspada": "⚠️",
    "berhenti": "🛑",

    # Ideas, Secrets & Solutions
    "idea": "💡",
    "smart": "🧠",
    "brain": "🧠",
    "genius": "🧠",
    "solution": "💡",
    "secret": "🤫",
    "hack": "🛠️",
    "trick": "✨",
    "tip": "💡",
    "tips": "💡",
    "strategy": "🎯",
    "ide": "💡",
    "rahasia": "🤫",
    "solusi": "💡",
    "trik": "✨",
    "pintar": "🧠",
    "cerdas": "🧠",

    # Target, Focus & Victory
    "target": "🎯",
    "goal": "🎯",
    "focus": "🎯",
    "aim": "🎯",
    "trophy": "🏆",
    "win": "🏆",
    "winner": "🏆",
    "winning": "🏆",
    "champion": "👑",
    "king": "👑",
    "boss": "👑",
    "best": "⭐",
    "fokus": "🎯",
    "tujuan": "🎯",
    "sasaran": "🎯",
    "menang": "🏆",
    "juara": "🏆",
    "raja": "👑",
    "terbaik": "⭐",

    # Skull, Defeat & Death
    "skull": "💀",
    "dead": "💀",
    "death": "💀",
    "rip": "🪦",
    "fail": "❌",
    "failed": "❌",
    "failure": "❌",
    "died": "💀",
    "mati": "💀",
    "tewas": "💀",
    "gagal": "❌",

    # Funny, Laughter & Joy
    "lol": "😂",
    "lmao": "🤣",
    "funny": "😂",
    "laugh": "😂",
    "laughing": "🤣",
    "joke": "🤡",
    "lucu": "😂",
    "ngakak": "🤣",
    "ketawa": "😂",

    # Love, Passion & Heart
    "love": "❤️",
    "favorite": "❤️",
    "heart": "❤️",
    "cinta": "❤️",
    "suka": "💖",
    "sayang": "❤️",

    # Strength & Power
    "power": "💪",
    "strong": "💪",
    "muscle": "💪",
    "gym": "🏋️",
    "beast": "🦍",
    "kuat": "💪",
    "otot": "💪",

    # Time & Urgency
    "time": "⏰",
    "clock": "⏰",
    "wait": "⏳",
    "deadline": "⏳",
    "waktu": "⏰",
    "jam": "⏰",
    "detik": "⏱️",
    "menit": "⏱️",

    # Questions & Perfection
    "why": "❓",
    "kenapa": "❓",
    "mengapa": "❓",
    "bingung": "🤔",
    "perfect": "💯",
    "100": "💯",
    "sempurna": "💯",
}

# Color palettes in ASS format (&H[Blue][Green][Red]&)
KEYWORD_PALETTES: Dict[str, Dict[str, str]] = {
    "modern": {
        "primary": "&H00FFFF&",    # Vibrant Yellow (BGR: 00 Blue, FF Green, FF Red)
        "accent": "&H00D7FF&",     # Warm Amber/Orange
        "positive": "&H00FF7F&",   # Spring Green
        "alert": "&H0033FF&",      # Fiery Crimson Red
        "magic": "&HFF7700&",      # Electric Cyan
    },
    "gold_amber": {
        "primary": "&H00C8FF&",    # Rich Gold
        "accent": "&H00A5FF&",     # Deep Amber
        "positive": "&H00E676&",   # Emerald
        "alert": "&H1E1EFF&",      # Red
        "magic": "&H00E5FF&",      # Bright Yellow
    },
    "neon_cyber": {
        "primary": "&HFFFF00&",    # Neon Cyan (00 Red, FF Green, FF Blue)
        "accent": "&HFF00FF&",     # Neon Magenta
        "positive": "&H00FF00&",   # Lime Green
        "alert": "&H0000FF&",      # Pure Laser Red
        "magic": "&HFFBF00&",      # Electric Sky Blue
    },
    "bold_red": {
        "primary": "&H1313FF&",    # Intense Punch Red
        "accent": "&H0080FF&",     # Fiery Orange
        "positive": "&H00FFCC&",   # Neon Mint
        "alert": "&H0000E6&",      # Deep Blood Red
        "magic": "&HFFFF33&",      # Cyber Blue
    },
    "classic": {
        "primary": "&H00FF00&",    # Classic Green
        "accent": "&H00FFFF&",     # Classic Yellow
        "positive": "&H00FF80&",   # Mint
        "alert": "&H0000FF&",      # Classic Red
        "magic": "&HFF8000&",      # Sky Blue
    },
}


def clean_word(word: str) -> str:
    """Normalize word by stripping punctuation and casing."""
    return re.sub(r"[^\w]", "", str(word or "").lower().strip())


def lookup_semantic_emoji(word: str) -> Optional[str]:
    """Return matching emoji if the given word is a recognized semantic trigger."""
    token = clean_word(word)
    return SEMANTIC_EMOJI_MAP.get(token)


def get_palette_color(
    palette_name: str = "modern",
    word: str = "",
) -> str:
    """
    Get the ASS color tag for a word based on the chosen palette and semantic tone.
    """
    palette = KEYWORD_PALETTES.get(palette_name.lower()) or KEYWORD_PALETTES["modern"]
    token = clean_word(word)

    # Contextual emotional tone overrides
    if token in ("money", "cash", "dollar", "profit", "revenue", "cuan", "kaya", "untung", "rich", "million", "billion"):
        return palette.get("positive", palette["primary"])
    if token in ("fire", "danger", "warning", "stop", "alert", "bahaya", "awas", "kaget", "dead", "mati", "fail"):
        return palette.get("alert", palette["primary"])
    if token in ("rocket", "moon", "scale", "hack", "secret", "magic", "trik", "roket"):
        return palette.get("magic", palette["primary"])

    return palette["primary"]


def annotate_words_with_emojis(
    words: List[Dict],
    max_emojis: int = 15,
) -> List[Dict]:
    """
    Annotate word-level timestamp objects with contextual emojis.
    Attaches an 'emoji' property to qualifying words up to max_emojis.
    """
    if not words:
        return words

    emojis_placed = 0
    for w in words:
        if emojis_placed >= max_emojis:
            break
        raw_token = w.get("word", "")
        emoji = lookup_semantic_emoji(raw_token)
        if emoji:
            w["emoji"] = emoji
            emojis_placed += 1

    return words


def enrich_text_with_emojis(text: str, max_emojis: int = 3) -> str:
    """
    Enrich title or social copy with semantic emojis after triggering keywords.
    """
    if not text:
        return text

    tokens = text.split()
    enriched_tokens = []
    emojis_added = 0

    for token in tokens:
        enriched_tokens.append(token)
        if emojis_added < max_emojis:
            emoji = lookup_semantic_emoji(token)
            if emoji and emoji not in text:
                enriched_tokens.append(emoji)
                emojis_added += 1

    return " ".join(enriched_tokens)
