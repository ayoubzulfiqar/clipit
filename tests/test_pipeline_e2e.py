"""
tests.test_pipeline_e2e — End-to-end synthetic integration tests for pipeline orchestration.

Validates that:
1. `clipping.runner.run_pipeline` executes all lifecycle steps (download, transcription,
   AI analysis, metadata normalization, clip processing, manifest generation).
2. `web.api.worker._run_pipeline_sync` updates the job store across all milestones,
   saving progress events and final clips to SQLite.
"""

import json
import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import clipping.engine
import clipping.runner
import clipping.studio
from clipping.config import ClipitConfig

try:
    from web.api import store, worker
    from web.api.models import JobStatus
    FASTAPI_AVAILABLE = True
except (ImportError, RuntimeError):
    FASTAPI_AVAILABLE = False


class TestPipelineE2E(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.outputs_dir = os.path.join(self.test_dir.name, "outputs")
        os.makedirs(self.outputs_dir, exist_ok=True)
        self.dummy_video = os.path.join(self.test_dir.name, "source.mp4")
        with open(self.dummy_video, "wb") as f:
            f.write(b"fake mp4 payload")

    def tearDown(self):
        self.test_dir.cleanup()

    @patch("clipping.engine.download_video")
    @patch("clipping.engine.transcribe_video")
    @patch("clipping.engine.analyze_with_ai")
    @patch("clipping.studio.detect_video_encoder")
    @patch("clipping.studio.proses_klip")
    def test_run_pipeline_orchestration(
        self,
        mock_proses_klip,
        mock_detect_encoder,
        mock_analyze,
        mock_transcribe,
        mock_download,
    ):
        """Verify runner.run_pipeline coordinates all sub-engines and writes manifest."""
        mock_transcribe.return_value = (
            "This is a test transcript of the video.",
            [
                {
                    "start": 0.0,
                    "end": 15.0,
                    "text": "This is a test transcript",
                    "words": [{"word": "This", "start": 0.0, "end": 0.5}],
                }
            ],
        )

        mock_analyze.return_value = [
            {
                "rank": 1,
                "start_time": 0.0,
                "end_time": 15.0,
                "judul": "Top Viral Clip",
                "viral_score": 98,
                "ringkasan": "A remarkable moment.",
            }
        ]

        mock_detect_encoder.return_value = {"name": "libx264", "args": ["-c:v", "libx264"]}
        mock_proses_klip.return_value = {
            "rank": 1,
            "title": "Top Viral Clip",
            "output_file": os.path.join(self.outputs_dir, "clip_1.mp4"),
            "duration": 15.0,
            "viral_score": 98,
        }

        cfg = ClipitConfig(
            url_youtube="https://youtube.com/watch?v=mocked123",
            file_video_asli=self.dummy_video,
            outputs_dir=self.outputs_dir,
            pilihan_rasio="9:16",
            use_hook_glitch=False,
            use_split_screen=False,
            use_camera_switch=False,
            voiceover=False,
            jumlah_clip=1,
            durasi_hook=3,
            max_kata_per_subtitle=4,
            whisper_model="tiny",
            whisper_device="cpu",
            whisper_compute_type="float32",
            ai_provider="gemini",
            api_key_gemini="mock_gemini_key",
            hf_token="mock_hf_token",
            split_trigger="manual",
            aspect_ratio="9:16",
            diarization_num_speakers=1,
        )

        manifest = clipping.runner.run_pipeline(cfg)

        self.assertEqual(len(manifest), 1)
        self.assertEqual(manifest[0]["rank"], 1)
        self.assertEqual(manifest[0]["title"], "Top Viral Clip")

        manifest_file = os.path.join(self.outputs_dir, "render_manifest.json")
        self.assertTrue(os.path.exists(manifest_file))
        with open(manifest_file, "r", encoding="utf-8") as f:
            saved_manifest = json.load(f)
            self.assertEqual(len(saved_manifest), 1)
            self.assertEqual(saved_manifest[0]["rank"], 1)

        meta_file = os.path.join(self.outputs_dir, "metadata_preview.json")
        self.assertTrue(os.path.exists(meta_file))


@unittest.skipUnless(FASTAPI_AVAILABLE, "FastAPI is not installed in current environment")
class TestWorkerPipelineSync(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.test_dir.name, "jobs.db")
        self.persist_path = os.path.join(self.test_dir.name, "jobs.json")

    def tearDown(self):
        self.test_dir.cleanup()

    @patch("clipping.engine.download_video")
    @patch("clipping.engine.transcribe_video")
    @patch("clipping.engine.analyze_with_ai")
    @patch("clipping.studio.detect_video_encoder")
    @patch("clipping.studio.proses_klip")
    def test_worker_run_pipeline_sync_success(
        self,
        mock_proses_klip,
        mock_detect_encoder,
        mock_analyze,
        mock_transcribe,
        mock_download,
    ):
        """Verify web.api.worker._run_pipeline_sync updates SQLite store to completed."""
        with patch("web.api.store.PERSIST_PATH", self.persist_path), \
             patch("web.api.store.DB_PATH", self.db_path):
            store._init_db()

            job_id = store.create_job(url="https://youtube.com/watch?v=mocked")

            payload = {
                "url": "https://youtube.com/watch?v=mocked",
                "gemini_api_key": "mock_key",
                "pilihan_rasio": "9:16",
                "clips": 1,
            }

            mock_transcribe.return_value = (
                "Transcript text",
                [{"start": 0.0, "end": 10.0, "text": "Transcript text"}],
            )
            mock_analyze.return_value = [
                {
                    "rank": 1,
                    "start_time": 0.0,
                    "end_time": 10.0,
                    "judul": "E2E Clip",
                    "viral_score": 95,
                    "ringkasan": "Short summary",
                }
            ]
            mock_detect_encoder.return_value = {"name": "libx264", "args": []}
            mock_proses_klip.return_value = {
                "rank": 1,
                "title_indonesia": "E2E Clip",
                "output_file": "/tmp/mock/clip_1.mp4",
                "duration": 10.0,
                "viral_score": 95,
            }

            with patch("web.api.worker._settings_env", {"GOOGLE_API_KEY": "mock_key"}):
                worker._run_pipeline_sync(job_id, payload)

            job = store.get_job(job_id)
            self.assertEqual(job["status"], JobStatus.COMPLETED.value)
            self.assertEqual(len(job["clips"]), 1)
            self.assertEqual(job["clips"][0]["title"], "E2E Clip")


if __name__ == "__main__":
    unittest.main()
