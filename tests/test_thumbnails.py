import os
import shutil
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from PIL import Image

from clipping.studio.thumbnail import buat_thumbnail, buat_thumbnail_variants


class TestThumbnails(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.cfg = SimpleNamespace(
            file_font_thumbnail=os.path.join(self.tmp_dir, "test_font.ttf"),
            url_font_thumbnail=None,
        )

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    @patch("clipping.studio.thumbnail._extract_frame_rgb")
    @patch("clipping.studio.thumbnail._get_video_duration")
    def test_buat_thumbnail_variants_creates_multiple_files(self, mock_dur, mock_extract):
        mock_dur.return_value = 30.0
        # Return a blank RGB image for frame extraction
        mock_extract.return_value = Image.new("RGB", (720, 1280), (50, 50, 80))

        out_thumb = os.path.join(self.tmp_dir, "clip_1.jpg")
        variants = buat_thumbnail_variants(
            video_path="fake_video.mp4",
            output_image_path=out_thumb,
            teks="VIRAL HOOK TITLE",
            cfg=self.cfg,
            count=3,
        )

        self.assertEqual(len(variants), 3)
        self.assertEqual(variants[0], out_thumb)
        self.assertEqual(variants[1], os.path.join(self.tmp_dir, "clip_1_b.jpg"))
        self.assertEqual(variants[2], os.path.join(self.tmp_dir, "clip_1_c.jpg"))

        for p in variants:
            self.assertTrue(os.path.exists(p))
            self.assertGreater(os.path.getsize(p), 0)

    @patch("clipping.studio.thumbnail._extract_frame_rgb")
    @patch("clipping.studio.thumbnail._get_video_duration")
    def test_buat_thumbnail_single_backward_compatibility(self, mock_dur, mock_extract):
        mock_dur.return_value = 15.0
        mock_extract.return_value = Image.new("RGB", (1080, 1920), (30, 30, 30))

        out_thumb = os.path.join(self.tmp_dir, "thumb.jpg")
        result = buat_thumbnail("fake_video.mp4", out_thumb, "Single Title", self.cfg)
        self.assertEqual(result, out_thumb)
        self.assertTrue(os.path.exists(out_thumb))


if __name__ == "__main__":
    unittest.main()
