import unittest

from clipping.stream_highlight import (
    cluster_highlight_intervals,
    detect_excitement_peaks,
    detect_transcript_hype_moments,
)


class TestStreamHighlight(unittest.TestCase):
    def test_detect_excitement_peaks(self):
        stats = [
            {"time": 0.0, "rms_db": -30.0},
            {"time": 1.0, "rms_db": -28.0},
            {"time": 2.0, "rms_db": -29.0},
            {"time": 3.0, "rms_db": -12.0},  # Massive scream/shout peak
            {"time": 4.0, "rms_db": -31.0},
        ]
        peaks = detect_excitement_peaks(stats, sensitivity=1.2)
        self.assertIn(3.0, peaks)
        self.assertNotIn(0.0, peaks)

    def test_detect_transcript_hype_moments(self):
        segments = [
            {"start": 10.0, "end": 12.0, "text": "let's go we just won that!"},
            {"start": 15.0, "end": 18.0, "text": "regular talking here"},
            {"start": 25.0, "end": 28.0, "text": "oh my god no way!"},
        ]
        hype = detect_transcript_hype_moments(segments)
        self.assertEqual(len(hype), 2)
        self.assertEqual(hype[0]["trigger"], "let's go")
        self.assertIn(hype[1]["trigger"], ("oh my god", "no way"))

    def test_cluster_highlight_intervals(self):
        peaks = [20.0, 22.0, 24.0, 80.0, 82.0]
        intervals = cluster_highlight_intervals(
            peaks,
            min_clip_duration=15.0,
            max_clip_duration=45.0,
            pre_roll=4.0,
            post_roll=6.0,
        )
        self.assertEqual(len(intervals), 2)
        # First cluster around 20-24s
        self.assertLessEqual(intervals[0]["start_time"], 16.0)
        self.assertGreaterEqual(intervals[0]["duration"], 15.0)
        # Second cluster around 80-82s
        self.assertGreaterEqual(intervals[1]["start_time"], 75.0)


if __name__ == "__main__":
    unittest.main()
