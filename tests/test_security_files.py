import os
import tempfile
import unittest
from unittest.mock import patch

try:
    from fastapi import HTTPException
    from web.api.routes.files import serve_output, list_outputs, OUTPUTS_DIR
    FASTAPI_AVAILABLE = True
except (ImportError, RuntimeError):
    FASTAPI_AVAILABLE = False


@unittest.skipUnless(FASTAPI_AVAILABLE, "FastAPI is not installed in the current environment")
class TestSecurityFiles(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.outputs_dir = os.path.realpath(self.test_dir.name)
        # Create a dummy job folder and valid file
        self.job_id = "test_job_123"
        self.job_dir = os.path.join(self.outputs_dir, self.job_id)
        os.makedirs(self.job_dir, exist_ok=True)
        self.valid_file = os.path.join(self.job_dir, "clip_1.mp4")
        with open(self.valid_file, "wb") as f:
            f.write(b"fake video data")

    def tearDown(self):
        self.test_dir.cleanup()

    async def test_absolute_path_traversal_is_blocked(self):
        """Test that absolute paths like /etc/passwd are strictly rejected."""
        with patch("web.api.routes.files.OUTPUTS_DIR", self.outputs_dir):
            with self.assertRaises(HTTPException) as ctx:
                await serve_output(self.job_id, "/etc/passwd")
            self.assertIn(ctx.exception.status_code, [400, 403, 404])

    async def test_relative_path_traversal_in_filename_is_blocked(self):
        """Test that relative traversal like ../../etc/passwd is blocked."""
        with patch("web.api.routes.files.OUTPUTS_DIR", self.outputs_dir):
            with self.assertRaises(HTTPException) as ctx:
                await serve_output(self.job_id, "../../etc/passwd")
            self.assertIn(ctx.exception.status_code, [400, 403, 404])

    async def test_relative_path_traversal_in_job_id_is_blocked(self):
        """Test that directory escape via job_id is blocked."""
        with patch("web.api.routes.files.OUTPUTS_DIR", self.outputs_dir):
            with self.assertRaises(HTTPException) as ctx:
                await serve_output("../etc", "passwd")
            self.assertIn(ctx.exception.status_code, [400, 403, 404])

    async def test_valid_file_is_served(self):
        """Test that an authentic file within the job directory is allowed."""
        with patch("web.api.routes.files.OUTPUTS_DIR", self.outputs_dir):
            response = await serve_output(self.job_id, "clip_1.mp4")
            self.assertEqual(response.path, self.valid_file)

    async def test_list_outputs_traversal_blocked(self):
        """Test that list_outputs blocks traversal job_ids."""
        with patch("web.api.routes.files.OUTPUTS_DIR", self.outputs_dir):
            with self.assertRaises(HTTPException) as ctx:
                await list_outputs("../")
            self.assertIn(ctx.exception.status_code, [400, 403])


if __name__ == "__main__":
    unittest.main()
