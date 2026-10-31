import unittest

from clipping.emoji_engine import (
    annotate_words_with_emojis,
    clean_word,
    enrich_text_with_emojis,
    get_palette_color,
    lookup_semantic_emoji,
)


class TestEmojiEngine(unittest.TestCase):
    def test_clean_word(self):
        self.assertEqual(clean_word("Money!"), "money")
        self.assertEqual(clean_word("  \"ROCKET\"  "), "rocket")
        self.assertEqual(clean_word("cuan..."), "cuan")

    def test_lookup_semantic_emoji(self):
        self.assertEqual(lookup_semantic_emoji("money"), "💰")
        self.assertEqual(lookup_semantic_emoji("cuan"), "💸")
        self.assertEqual(lookup_semantic_emoji("fire!"), "🔥")
        self.assertEqual(lookup_semantic_emoji("rocket"), "🚀")
        self.assertEqual(lookup_semantic_emoji("bahaya"), "⚠️")
        self.assertEqual(lookup_semantic_emoji("mindblown"), "🤯")
        self.assertIsNone(lookup_semantic_emoji("the"))

    def test_annotate_words_with_emojis(self):
        words = [
            {"word": "This", "start": 0.0, "end": 0.4},
            {"word": "is", "start": 0.4, "end": 0.6},
            {"word": "pure", "start": 0.6, "end": 0.9},
            {"word": "fire", "start": 0.9, "end": 1.2},
            {"word": "and", "start": 1.2, "end": 1.4},
            {"word": "money", "start": 1.4, "end": 1.8},
        ]
        annotated = annotate_words_with_emojis(words, max_emojis=2)
        self.assertEqual(annotated[3].get("emoji"), "🔥")
        self.assertEqual(annotated[5].get("emoji"), "💰")

    def test_enrich_text_with_emojis(self):
        title = "How I make money and scale my business fast"
        enriched = enrich_text_with_emojis(title, max_emojis=2)
        self.assertIn("💰", enriched)
        self.assertIn("🚀", enriched)

    def test_get_palette_color(self):
        # Default modern
        self.assertEqual(get_palette_color("modern", "normal"), "&H00FFFF&")
        # Gold palette
        self.assertEqual(get_palette_color("gold_amber", "normal"), "&H00C8FF&")
        # Emotional tones override
        self.assertEqual(get_palette_color("modern", "money"), "&H00FF7F&")
        self.assertEqual(get_palette_color("modern", "fire"), "&H0033FF&")


if __name__ == "__main__":
    unittest.main()
