import os
import shutil
import tempfile
import time
import unittest

try:
    from web.api.routes.files import cleanup_old_files, download_job_zip
    FASTAPI_AVAILABLE = True
except (ImportError, RuntimeError):
    FASTAPI_AVAILABLE = False


@unittest.skipUnless(FASTAPI_AVAILABLE, "FastAPI is not installed in current environment")
class TestFilesAdvanced(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.upload_dir = os.path.join(self.tmp_dir, "uploads")
        self.output_dir = os.path.join(self.tmp_dir, "outputs")
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    async def test_download_job_zip_creates_valid_zip(self):
        # Create a mock job output directory with 2 files
        job_id = "test_job_123"
        job_dir = os.path.join(self.output_dir, job_id)
        os.makedirs(job_dir, exist_ok=True)

        with open(os.path.join(job_dir, "clip_1.mp4"), "w") as f:
            f.write("mock video content")
        with open(os.path.join(job_dir, "metadata.json"), "w") as f:
            f.write('{"test": true}')

        from unittest.mock import patch
        with patch("web.api.routes.files.OUTPUTS_DIR", self.output_dir):
            res = await download_job_zip(job_id)
            self.assertEqual(res.media_type, "application/zip")
            self.assertTrue(os.path.exists(res.path))
            self.assertGreater(os.path.getsize(res.path), 0)
            if os.path.exists(res.path):
                os.remove(res.path)

    async def test_cleanup_old_files_removes_expired_items(self):
        # Create old file (10 days old) and fresh file (1 hour old)
        old_file = os.path.join(self.upload_dir, "old_video.mp4")
        fresh_file = os.path.join(self.upload_dir, "fresh_video.mp4")

        with open(old_file, "w") as f:
            f.write("old")
        with open(fresh_file, "w") as f:
            f.write("fresh")

        ten_days_ago = time.time() - (10 * 86400)
        os.utime(old_file, (ten_days_ago, ten_days_ago))

        from unittest.mock import patch
        with patch("web.api.routes.files.UPLOAD_DIR", self.upload_dir), \
             patch("web.api.routes.files.OUTPUTS_DIR", self.output_dir):
            res = await cleanup_old_files(days=7)
            self.assertEqual(res["status"], "success")
            self.assertEqual(res["cleaned_uploads"], 1)

            # Old file should be deleted, fresh file preserved
            self.assertFalse(os.path.exists(old_file))
            self.assertTrue(os.path.exists(fresh_file))


if __name__ == "__main__":
    unittest.main()
