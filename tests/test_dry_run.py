import os
import tempfile
import unittest
from unittest.mock import patch

from clipping.config import build_config
from clipping.runner import run_pipeline


class TestDryRun(unittest.TestCase):
    def test_dry_run_flag_parsed(self):
        cfg = build_config(["--url", "https://youtube.com/watch?v=sample", "--dry-run", "--seed", "42"])
        self.assertTrue(cfg.dry_run)
        self.assertEqual(cfg.seed, 42)

    @patch("clipping.engine.download_video")
    @patch("clipping.engine.transcribe_video")
    @patch("clipping.engine.analyze_with_ai")
    @patch("clipping.studio.core.proses_klip")
    def test_dry_run_pipeline_skips_render(self, mock_render, mock_ai, mock_transcribe, mock_dl):
        mock_transcribe.return_value = ("Sample full transcript", [{"word": "sample", "start": 0.0, "end": 1.0}])
        mock_ai.return_value = [
            {
                "rank": 1,
                "start_time": 10.0,
                "end_time": 30.0,
                "title": "Dry Run Clip",
                "viral_score": 95,
            }
        ]

        with tempfile.TemporaryDirectory() as tmpdir:
            cfg = build_config([
                "--url", "https://youtube.com/watch?v=sample",
                "--outputs-dir", tmpdir,
                "--dry-run",
                "--seed", "1234",
            ])
            cfg.file_video_asli = os.path.join(tmpdir, "video.mp4")
            with open(cfg.file_video_asli, "wb") as f:
                f.write(b"mock" * 500)

            manifest = run_pipeline(cfg)

            self.assertEqual(len(manifest), 1)
            self.assertTrue(manifest[0].get("dry_run"))
            self.assertEqual(manifest[0]["rank"], 1)
            # Core clip rendering must NOT have been called in dry-run mode
            mock_render.assert_not_called()
            # Render manifest file must have been generated
            manifest_file = os.path.join(tmpdir, "render_manifest.json")
            self.assertTrue(os.path.exists(manifest_file))


if __name__ == "__main__":
    unittest.main()
