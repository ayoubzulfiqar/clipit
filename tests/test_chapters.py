import unittest

from clipping.chapters import (
    extract_seo_keywords,
    format_timestamp,
    format_youtube_chapters_block,
    generate_chapters_from_clips,
    generate_show_notes,
)


class TestChapters(unittest.TestCase):
    def test_format_timestamp(self):
        self.assertEqual(format_timestamp(0), "00:00")
        self.assertEqual(format_timestamp(45), "00:45")
        self.assertEqual(format_timestamp(75), "01:15")
        self.assertEqual(format_timestamp(3665), "01:01:05")

    def test_generate_chapters_from_clips(self):
        clips = [
            {"start_time": 45.0, "title_en": "Deep Learning Breakdown"},
            {"start_time": 120.0, "title_en": "Transformer Architecture"},
        ]
        chapters = generate_chapters_from_clips(clips)
        self.assertEqual(len(chapters), 3)  # Added 00:00 Introduction
        self.assertEqual(chapters[0]["timestamp"], "00:00")
        self.assertEqual(chapters[0]["title"], "Introduction")
        self.assertEqual(chapters[1]["timestamp"], "00:45")
        self.assertEqual(chapters[1]["title"], "Deep Learning Breakdown")
        self.assertEqual(chapters[2]["timestamp"], "02:00")
        self.assertEqual(chapters[2]["title"], "Transformer Architecture")

    def test_format_youtube_chapters_block(self):
        chapters = [
            {"timestamp": "00:00", "title": "Intro"},
            {"timestamp": "01:30", "title": "The Big Reveal"},
        ]
        block = format_youtube_chapters_block(chapters)
        self.assertIn("📌 Timestamps:", block)
        self.assertIn("00:00 - Intro", block)
        self.assertIn("01:30 - The Big Reveal", block)

    def test_generate_show_notes(self):
        chapters = [{"timestamp": "00:00", "title": "Start"}]
        notes = generate_show_notes(
            title="Episode 42",
            summary="An in-depth look at AI.",
            chapters=chapters,
            takeaways=["AI changes everything", "Prompt engineering matters"],
            source_url="https://youtu.be/test123",
        )
        self.assertIn("# Episode 42", notes)
        self.assertIn("## Summary", notes)
        self.assertIn("## Key Takeaways", notes)
        self.assertIn("https://youtu.be/test123", notes)

    def test_extract_seo_keywords(self):
        text = "Artificial intelligence and machine learning models are changing artificial neural networks."
        kw = extract_seo_keywords(text, max_keywords=3)
        self.assertIn("artificial", kw)
        self.assertLessEqual(len(kw), 3)


if __name__ == "__main__":
    unittest.main()
