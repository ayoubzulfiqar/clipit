import unittest
from unittest.mock import MagicMock, patch

try:
    from fastapi import Response
    from web.api.routes.system import health_liveness, health_readiness
    from clipping import __version__
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False


@unittest.skipUnless(FASTAPI_AVAILABLE, "FastAPI is not installed in current environment")
class TestSystemHealth(unittest.IsolatedAsyncioTestCase):
    async def test_health_liveness(self):
        res = await health_liveness()
        self.assertEqual(res["status"], "ok")
        self.assertEqual(res["version"], __version__)

    async def test_health_readiness_all_ok(self):
        response = Response()
        with patch("shutil.which", return_value="/usr/bin/mocked"), \
             patch("web.api.store.get_queued_count", return_value=0), \
             patch("web.api.routes.system.detect_video_encoder", return_value={"name": "h264_nvenc"}), \
             patch("web.api.routes.system._check_storage", return_value={"writable": True, "free_gb": 50.0}):
            result = await health_readiness(response)
            self.assertTrue(result["ready"])
            self.assertEqual(response.status_code, 200)
            self.assertEqual(result["encoder"], {"name": "h264_nvenc"})
            self.assertTrue(result["database"]["ok"])

    async def test_health_readiness_missing_ffmpeg(self):
        response = Response()
        def mock_which(binary):
            if binary == "ffmpeg":
                return None
            return f"/usr/bin/{binary}"

        with patch("shutil.which", side_effect=mock_which), \
             patch("web.api.store.get_queued_count", return_value=0), \
             patch("web.api.routes.system._check_storage", return_value={"writable": True, "free_gb": 50.0}):
            result = await health_readiness(response)
            self.assertFalse(result["ready"])
            self.assertEqual(response.status_code, 503)
            self.assertFalse(result["binaries"]["ffmpeg"]["installed"])


if __name__ == "__main__":
    unittest.main()
