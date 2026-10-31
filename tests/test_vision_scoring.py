import os
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image, ImageDraw

from clipping.vision_scoring import (
    compute_brightness_score,
    compute_contrast_score,
    compute_sharpness_score,
    extract_frame,
    rank_clip_frames,
    score_frame,
)


class TestVisionScoring(unittest.TestCase):
    def test_sharpness_solid_vs_high_contrast_pattern(self):
        # A solid flat image has zero gradient sharpness
        flat_img = Image.new("L", (100, 100), color=128)
        flat_sharpness = compute_sharpness_score(flat_img)
        self.assertEqual(flat_sharpness, 0.0)

        # An image with alternating high contrast lines has high sharpness
        pattern_img = Image.new("L", (100, 100), color=0)
        draw = ImageDraw.Draw(pattern_img)
        for i in range(0, 100, 4):
            draw.line([(i, 0), (i, 100)], fill=255, width=2)

        pattern_sharpness = compute_sharpness_score(pattern_img)
        self.assertGreater(pattern_sharpness, 40.0)

    def test_brightness_scoring(self):
        # Completely pitch black image (underexposed)
        black_img = Image.new("L", (50, 50), color=0)
        self.assertLess(compute_brightness_score(black_img), 20.0)

        # Well-balanced medium gray (~130)
        ideal_img = Image.new("L", (50, 50), color=130)
        self.assertGreater(compute_brightness_score(ideal_img), 95.0)

    def test_contrast_scoring(self):
        flat_img = Image.new("L", (50, 50), color=128)
        self.assertEqual(compute_contrast_score(flat_img), 0.0)

        high_contrast = Image.new("L", (50, 50), color=0)
        draw = ImageDraw.Draw(high_contrast)
        draw.rectangle([(0, 0), (25, 50)], fill=255)
        self.assertGreater(compute_contrast_score(high_contrast), 50.0)

    def test_score_frame_dict_keys(self):
        img = Image.new("RGB", (200, 200), color=(120, 140, 160))
        metrics = score_frame(img)
        self.assertIn("composite_score", metrics)
        self.assertIn("sharpness", metrics)
        self.assertIn("contrast", metrics)
        self.assertIn("brightness", metrics)
        self.assertIn("is_blurry", metrics)
        self.assertIsInstance(metrics["composite_score"], float)

    @patch("subprocess.run")
    def test_extract_frame_mock(self, mock_run):
        mock_run.return_value.returncode = 0
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = os.path.join(tmpdir, "frame.jpg")
            # Create a mock file so isfile returns true
            with open(out_path, "wb") as f:
                f.write(b"JPEG")

            success = extract_frame("/tmp/video.mp4", 12.5, out_path)
            self.assertTrue(success)

    @patch("clipping.vision_scoring.extract_frame")
    def test_rank_clip_frames_mock(self, mock_extract):
        with tempfile.TemporaryDirectory() as tmpdir:
            def side_effect(vid, ts, out_path):
                img = Image.new("RGB", (100, 100), color=(int(ts * 10) % 255, 100, 150))
                img.save(out_path)
                return True

            mock_extract.side_effect = side_effect
            ranked = rank_clip_frames(
                video_path="/tmp/fake.mp4",
                start_time=10.0,
                end_time=20.0,
                sample_count=3,
                output_dir=tmpdir,
            )
            self.assertEqual(len(ranked), 3)
            # Should be sorted descending by composite_score
            self.assertGreaterEqual(ranked[0]["composite_score"], ranked[1]["composite_score"])
            self.assertGreaterEqual(ranked[1]["composite_score"], ranked[2]["composite_score"])


if __name__ == "__main__":
    unittest.main()
