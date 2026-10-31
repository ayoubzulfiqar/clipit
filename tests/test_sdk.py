import json
import unittest
from unittest.mock import MagicMock, patch

from sdk.python.clipit_sdk import ClipitClient, ClipitError


class TestClipitSDK(unittest.TestCase):
    def setUp(self):
        self.client = ClipitClient(base_url="http://127.0.0.1:8000", api_key="secret123")

    @patch("urllib.request.urlopen")
    def test_health(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({"status": "ok", "version": "1.15.0"}).encode("utf-8")
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        res = self.client.health()
        self.assertEqual(res["status"], "ok")
        self.assertEqual(res["version"], "1.15.0")

    @patch("urllib.request.urlopen")
    def test_create_job(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({"id": "job_999", "status": "queued"}).encode("utf-8")
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        job = self.client.create_job(
            url="https://youtube.com/watch?v=sample",
            clips=5,
            semantic_emojis=True,
            use_sfx=True,
        )
        self.assertEqual(job["id"], "job_999")
        self.assertEqual(job["status"], "queued")

        req = mock_urlopen.call_args[0][0]
        self.assertEqual(req.get_header("X-api-key"), "secret123")
        body = json.loads(req.data.decode("utf-8"))
        self.assertEqual(body["clips"], 5)
        self.assertTrue(body["semantic_emojis"])
        self.assertTrue(body["use_sfx"])

    @patch("urllib.request.urlopen")
    def test_wait_for_job_completed(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "id": "job_999",
            "status": "completed",
            "clips": [{"rank": 1, "download_url": "/api/outputs/job_999/clip_1.mp4"}],
        }).encode("utf-8")
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        job = self.client.wait_for_job("job_999", poll_interval=0.01, timeout=1.0)
        self.assertEqual(job["status"], "completed")
        self.assertEqual(len(job["clips"]), 1)


if __name__ == "__main__":
    unittest.main()
