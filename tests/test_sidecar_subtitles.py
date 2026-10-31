import os
import shutil
import tempfile
import unittest

from clipping.studio.subtitles import (
    build_clip_cues,
    export_sidecar_subtitles,
    format_srt_timestamp,
    format_vtt_timestamp,
    generate_srt,
    generate_vtt,
)


class TestSidecarSubtitles(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_format_timestamps(self):
        self.assertEqual(format_srt_timestamp(0.0), "00:00:00,000")
        self.assertEqual(format_srt_timestamp(65.123), "00:01:05,123")
        self.assertEqual(format_srt_timestamp(3661.050), "01:01:01,050")

        self.assertEqual(format_vtt_timestamp(0.0), "00:00:00.000")
        self.assertEqual(format_vtt_timestamp(65.123), "00:01:05.123")
        self.assertEqual(format_vtt_timestamp(3661.050), "01:01:01.050")

    def test_build_clip_cues_shifts_relative_to_clip_start(self):
        data_segmen = [
            {"start": 5.0, "end": 9.0, "text": "Segment before clip"},
            {"start": 10.5, "end": 15.0, "text": "First clip line"},
            {"start": 15.2, "end": 19.8, "text": "Second clip line"},
            {"start": 21.0, "end": 25.0, "text": "Segment after clip"},
        ]

        # Clip is from 10.0 to 20.0
        cues = build_clip_cues(data_segmen, clip_start=10.0, clip_end=20.0)
        self.assertEqual(len(cues), 2)

        # Cue 1: 10.5 - 10.0 = 0.5s start, 15.0 - 10.0 = 5.0s end
        self.assertAlmostEqual(cues[0]["start"], 0.5)
        self.assertAlmostEqual(cues[0]["end"], 5.0)
        self.assertEqual(cues[0]["text"], "First clip line")

        # Cue 2: 15.2 - 10.0 = 5.2s start, 19.8 - 10.0 = 9.8s end
        self.assertAlmostEqual(cues[1]["start"], 5.2)
        self.assertAlmostEqual(cues[1]["end"], 9.8)
        self.assertEqual(cues[1]["text"], "Second clip line")

    def test_generate_srt_and_vtt(self):
        cues = [
            {"start": 0.5, "end": 2.5, "text": "Welcome to Clipit!"},
            {"start": 3.0, "end": 5.0, "text": "High virality AI clips."},
        ]

        srt_text = generate_srt(cues)
        self.assertIn("1\n00:00:00,500 --> 00:00:02,500\nWelcome to Clipit!", srt_text)
        self.assertIn("2\n00:00:03,000 --> 00:00:05,000\nHigh virality AI clips.", srt_text)

        vtt_text = generate_vtt(cues)
        self.assertTrue(vtt_text.startswith("WEBVTT"))
        self.assertIn("00:00:00.500 --> 00:00:02.500\nWelcome to Clipit!", vtt_text)

    def test_export_sidecar_subtitles_writes_files(self):
        data_segmen = [
            {"start": 1.0, "end": 3.5, "text": "Catchy viral intro."},
            {"start": 4.0, "end": 7.0, "text": "Retention payoff here."},
        ]

        vid_path = os.path.join(self.tmp_dir, "clip_1.mp4")
        res = export_sidecar_subtitles(
            data_segmen=data_segmen,
            clip_start=0.0,
            clip_end=10.0,
            base_video_path=vid_path,
            formats=("srt", "vtt"),
        )

        self.assertIn("srt", res)
        self.assertIn("vtt", res)

        srt_path = res["srt"]
        vtt_path = res["vtt"]

        self.assertTrue(os.path.exists(srt_path))
        self.assertTrue(os.path.exists(vtt_path))

        with open(srt_path, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("Catchy viral intro.", content)

        with open(vtt_path, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertTrue(content.startswith("WEBVTT"))


if __name__ == "__main__":
    unittest.main()
