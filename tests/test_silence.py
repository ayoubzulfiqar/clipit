import unittest

from clipping.silence import (
    compute_keep_segments,
    detect_silence_from_words,
    filter_filler_words,
    merge_silence_intervals,
)


class TestSilenceTrimming(unittest.TestCase):
    def test_detect_silence_from_words_finds_gaps(self):
        # Clip from 10.0 to 30.0
        # Words: 11.0-13.0, gap (13.0-15.0 = 2.0s), 15.0-18.0, gap (18.0-18.2 = 0.2s, too short), 18.2-25.0, gap (25.0-30.0 = 5.0s)
        data_segmen = [
            {
                "start": 11.0,
                "end": 13.0,
                "text": "Hello world",
                "words": [
                    {"word": "Hello", "start": 11.0, "end": 12.0},
                    {"word": "world", "start": 12.1, "end": 13.0},
                ],
            },
            {
                "start": 15.0,
                "end": 25.0,
                "text": "This is a test speech segment",
                "words": [
                    {"word": "This", "start": 15.0, "end": 16.0},
                    {"word": "is", "start": 16.1, "end": 18.0},
                    {"word": "speech", "start": 18.2, "end": 25.0},
                ],
            },
        ]

        silences = detect_silence_from_words(
            data_segmen=data_segmen,
            clip_start=10.0,
            clip_end=30.0,
            min_silence_duration=0.5,
        )

        # Expected silences:
        # 1. Leading silence: 10.0 -> 11.0 (1.0s >= 0.5s)
        # 2. Middle gap: 13.0 -> 15.0 (2.0s >= 0.5s)
        # 3. Trailing silence: 25.0 -> 30.0 (5.0s >= 0.5s)
        self.assertEqual(len(silences), 3)
        self.assertAlmostEqual(silences[0][0], 10.0)
        self.assertAlmostEqual(silences[0][1], 11.0)
        self.assertAlmostEqual(silences[1][0], 13.0)
        self.assertAlmostEqual(silences[1][1], 15.0)
        self.assertAlmostEqual(silences[2][0], 25.0)
        self.assertAlmostEqual(silences[2][1], 30.0)

    def test_merge_silence_intervals(self):
        raw = [(10.0, 12.0), (11.5, 14.0), (20.0, 22.0), (22.0, 24.0)]
        merged = merge_silence_intervals(raw)
        self.assertEqual(len(merged), 2)
        self.assertEqual(merged[0], (10.0, 14.0))
        self.assertEqual(merged[1], (20.0, 24.0))

    def test_compute_keep_segments(self):
        # Clip from 0.0 to 20.0 with silence in the middle (5.0 to 10.0)
        silences = [(5.0, 10.0)]
        keep = compute_keep_segments(0.0, 20.0, silences, padding_seconds=0.1, min_segment_duration=0.5)

        self.assertEqual(len(keep), 2)
        # Segment 1 should be around 0.0 -> 5.1
        self.assertAlmostEqual(keep[0]["start_time"], 0.0)
        self.assertAlmostEqual(keep[0]["end_time"], 5.1)
        # Segment 2 should be around 9.9 -> 20.0
        self.assertAlmostEqual(keep[1]["start_time"], 9.9)
        self.assertAlmostEqual(keep[1]["end_time"], 20.0)

    def test_filter_filler_words_english(self):
        text = "So, um, I was like really, uh, excited about this!"
        cleaned = filter_filler_words(text, language="en")
        self.assertNotIn("um,", cleaned)
        self.assertNotIn("uh,", cleaned)
        self.assertIn("really,", cleaned)
        self.assertIn("excited", cleaned)

    def test_filter_filler_words_indonesian(self):
        text = "Saya merasa anu sangat bangga gitu karena ini berhasil"
        cleaned = filter_filler_words(text, language="id")
        self.assertNotIn("anu", cleaned)
        self.assertNotIn("gitu", cleaned)
        self.assertIn("bangga", cleaned)


if __name__ == "__main__":
    unittest.main()
