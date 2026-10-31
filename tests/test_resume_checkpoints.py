import json
import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from clipping.config import ClipitConfig
import clipping.runner


class TestResumeCheckpoints(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.outputs_dir = os.path.join(self.test_dir.name, "outputs")
        os.makedirs(self.outputs_dir, exist_ok=True)
        self.source_video = os.path.join(self.test_dir.name, "video.mp4")
        with open(self.source_video, "wb") as f:
            f.write(b"0" * 2048)

    def tearDown(self):
        self.test_dir.cleanup()

    @patch("clipping.engine.download_video")
    @patch("clipping.engine.transcribe_video")
    @patch("clipping.engine.analyze_with_ai")
    @patch("clipping.studio.detect_video_encoder")
    @patch("clipping.studio.proses_klip")
    def test_resume_skips_transcription_when_cache_exists(
        self,
        mock_proses_klip,
        mock_detect_encoder,
        mock_analyze,
        mock_transcribe,
        mock_download,
    ):
        """When transcription_cache.json exists and resume=True, transcribe_video is not called."""
        cache_file = os.path.join(self.outputs_dir, "transcription_cache.json")
        cached_content = {
            "transkrip_lengkap": "Cached transcript data",
            "data_segmen": [{"start": 0.0, "end": 10.0, "text": "Cached transcript data"}],
        }
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(cached_content, f)

        mock_analyze.return_value = [
            {"rank": 1, "start_time": 0.0, "end_time": 10.0, "judul": "Clip 1", "viral_score": 90}
        ]
        mock_detect_encoder.return_value = {"name": "libx264", "args": []}
        mock_proses_klip.return_value = {"rank": 1, "title": "Clip 1", "output_file": "/tmp/c1.mp4"}

        cfg = ClipitConfig(
            url_youtube="https://youtube.com/watch?v=123",
            file_video_asli=self.source_video,
            outputs_dir=self.outputs_dir,
            pilihan_rasio="9:16",
            resume=True,
            use_hook_glitch=False,
            voiceover=False,
            jumlah_clip=1,
            durasi_hook=3,
            max_kata_per_subtitle=4,
        )

        manifest = clipping.runner.run_pipeline(cfg)

        # Assertions
        mock_download.assert_not_called()  # Source video already > 1024 bytes
        mock_transcribe.assert_not_called()  # Transcription loaded from cache
        mock_analyze.assert_called_once()
        self.assertEqual(len(manifest), 1)

    @patch("clipping.engine.download_video")
    @patch("clipping.engine.transcribe_video")
    @patch("clipping.engine.analyze_with_ai")
    @patch("clipping.studio.detect_video_encoder")
    @patch("clipping.studio.proses_klip")
    def test_no_resume_forces_retranscription(
        self,
        mock_proses_klip,
        mock_detect_encoder,
        mock_analyze,
        mock_transcribe,
        mock_download,
    ):
        """When resume=False, transcription_cache.json is ignored and transcribe_video is called."""
        cache_file = os.path.join(self.outputs_dir, "transcription_cache.json")
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump({"transkrip_lengkap": "Old cached", "data_segmen": []}, f)

        mock_transcribe.return_value = (
            "Fresh transcript",
            [{"start": 0.0, "end": 5.0, "text": "Fresh"}],
        )
        mock_analyze.return_value = [
            {"rank": 1, "start_time": 0.0, "end_time": 5.0, "judul": "Clip", "viral_score": 85}
        ]
        mock_detect_encoder.return_value = {"name": "libx264", "args": []}
        mock_proses_klip.return_value = {"rank": 1, "title": "Clip", "output_file": "/tmp/c.mp4"}

        cfg = ClipitConfig(
            url_youtube="https://youtube.com/watch?v=123",
            file_video_asli=self.source_video,
            outputs_dir=self.outputs_dir,
            pilihan_rasio="9:16",
            resume=False,
            use_hook_glitch=False,
            voiceover=False,
            jumlah_clip=1,
            durasi_hook=3,
            max_kata_per_subtitle=4,
        )

        clipping.runner.run_pipeline(cfg)

        mock_transcribe.assert_called_once()

    @patch("clipping.engine.download_video")
    @patch("clipping.engine.transcribe_video")
    @patch("clipping.engine.analyze_with_ai")
    @patch("clipping.studio.detect_video_encoder")
    @patch("clipping.studio.proses_klip")
    def test_resume_skips_already_rendered_clip(
        self,
        mock_proses_klip,
        mock_detect_encoder,
        mock_analyze,
        mock_transcribe,
        mock_download,
    ):
        """When a clip already exists on disk and in render_manifest.json, proses_klip is skipped."""
        existing_clip_mp4 = os.path.join(self.outputs_dir, "clip_1.mp4")
        with open(existing_clip_mp4, "wb") as f:
            f.write(b"MOCK_MP4_VIDEO_BYTES" * 100)

        manifest_file = os.path.join(self.outputs_dir, "render_manifest.json")
        with open(manifest_file, "w", encoding="utf-8") as f:
            json.dump(
                [{"rank": 1, "title": "Pre-rendered Clip", "output_file": existing_clip_mp4}],
                f,
            )

        mock_transcribe.return_value = (
            "Transcript",
            [{"start": 0.0, "end": 10.0, "text": "Transcript"}],
        )
        mock_analyze.return_value = [
            {"rank": 1, "start_time": 0.0, "end_time": 10.0, "judul": "Pre-rendered Clip", "viral_score": 90}
        ]
        mock_detect_encoder.return_value = {"name": "libx264", "args": []}

        cfg = ClipitConfig(
            url_youtube="https://youtube.com/watch?v=123",
            file_video_asli=self.source_video,
            outputs_dir=self.outputs_dir,
            pilihan_rasio="9:16",
            resume=True,
            use_hook_glitch=False,
            voiceover=False,
            jumlah_clip=1,
            durasi_hook=3,
            max_kata_per_subtitle=4,
        )

        manifest = clipping.runner.run_pipeline(cfg)

        mock_proses_klip.assert_not_called()
        self.assertEqual(len(manifest), 1)
        self.assertEqual(manifest[0]["title"], "Pre-rendered Clip")


if __name__ == "__main__":
    unittest.main()
