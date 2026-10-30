import os
import tempfile
import unittest

from clipping.config import build_config
from clipping.studio.subtitles import buat_file_ass


class TestSubtitles(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.ass_file = os.path.join(self.test_dir.name, "test_output.ass")
        self.cfg = build_config(["--url", "https://youtube.com/watch?v=sample"])

    def tearDown(self):
        self.test_dir.cleanup()

    def test_buat_file_ass_basic_generation(self):
        """Test generating a valid ASS subtitle file from segments."""
        data_segmen = [
            {
                "start": 5.0,
                "end": 8.0,
                "words": [
                    {"word": "Halo", "start": 5.0, "end": 5.5},
                    {"word": "semuanya", "start": 5.6, "end": 6.2},
                    {"word": "selamat", "start": 6.3, "end": 7.0},
                    {"word": "datang", "start": 7.1, "end": 8.0},
                ],
            }
        ]

        # Use non-advanced text for standard subtitle test
        self.cfg.use_advanced_text = False
        buat_file_ass(
            data_segmen=data_segmen,
            start_clip=0.0,
            end_clip=10.0,
            nama_file_ass=self.ass_file,
            rasio="9:16",
            cfg=self.cfg,
            gunakan_advanced=False,
        )

        self.assertTrue(os.path.exists(self.ass_file))
        with open(self.ass_file, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("[Script Info]", content)
        self.assertIn("[V4+ Styles]", content)
        self.assertIn("[Events]", content)
        self.assertIn("Dialogue:", content)
        self.assertIn("Halo", content)
        self.assertIn("semuanya", content)


if __name__ == "__main__":
    unittest.main()
