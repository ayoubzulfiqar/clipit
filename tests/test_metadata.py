import unittest

from clipping.metadata import (
    _trim_title,
    _normalize_hashtags,
    _normalize_keyword_tags,
    _build_youtube_description,
    _build_tiktok_caption,
    _looks_indonesian,
    normalize_and_validate,
)


class TestMetadata(unittest.TestCase):
    def test_trim_title(self):
        """Test title is trimmed at word boundaries within length."""
        short_title = "Short Title"
        self.assertEqual(_trim_title(short_title, 50), short_title)

        long_title = "This is a very long title that exceeds the limit and should be nicely truncated"
        trimmed = _trim_title(long_title, 30)
        self.assertLessEqual(len(trimmed), 30)
        self.assertFalse(trimmed.endswith(" "))
        self.assertTrue(trimmed.startswith("This is a very long"))

    def test_normalize_hashtags(self):
        """Test hashtag normalization and deduping."""
        raw = "viral   #podcast #VIRAL podcasting #clips"
        tags, count = _normalize_hashtags(raw, min_tags=2, max_tags=3)
        self.assertEqual(count, 3)
        self.assertEqual(tags, "#viral #podcast #podcasting")

    def test_normalize_keyword_tags(self):
        """Test keyword tags cleaning and bounding."""
        raw_tags = ["podcast", "ai tool", "PODCAST", "", "  tech  ", "video editor", "clips", "viral", "extra"]
        cleaned = _normalize_keyword_tags(raw_tags, min_items=3, max_items=5)
        self.assertEqual(len(cleaned), 5)
        self.assertIn("podcast", cleaned)
        self.assertIn("ai tool", cleaned)
        self.assertIn("tech", cleaned)

    def test_build_descriptions(self):
        """Test YouTube description and TikTok caption assembling."""
        yt_desc = _build_youtube_description("Hook statement", "Detailed context here", "#viral #clips", source_url="https://youtube.com/original")
        self.assertIn("Hook statement", yt_desc)
        self.assertIn("Detailed context here", yt_desc)
        self.assertIn("#viral #clips", yt_desc)
        self.assertIn("Source: https://youtube.com/original", yt_desc)

        tt_cap = _build_tiktok_caption("Check this out!", "#viral #fyp")
        self.assertEqual(tt_cap, "Check this out!\n#viral #fyp")

    def test_looks_indonesian(self):
        """Test Indonesian language heuristics."""
        self.assertTrue(_looks_indonesian("Video ini sangat menarik dan bermanfaat untuk bisnis."))
        self.assertFalse(_looks_indonesian("This video is completely in English with no foreign words."))

    def test_normalize_and_validate_manifest(self):
        """Test end-to-end normalization of raw AI clip json."""
        raw_items = [
            {
                "rank": 1,
                "viral_score": 95,
                "title_indonesia": "Klip Hebat Ini",
                "title_inggris": "This Great Clip",
                "start_time": 10.0,
                "end_time": 40.0,
                "hastag": "viral fyp",
                "keyword_tags": ["tag1", "tag2", "tag3"],
                "description_hook": "Hook",
                "description_context": "Context",
                "tiktok_caption": "Caption",
            }
        ]
        validated = normalize_and_validate(raw_items)
        self.assertEqual(len(validated), 1)
        self.assertIn("#viral", validated[0]["hastag"])
        self.assertIn("#fyp", validated[0]["hastag"])


if __name__ == "__main__":
    unittest.main()
