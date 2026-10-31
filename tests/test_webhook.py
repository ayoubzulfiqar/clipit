import json
import unittest
from unittest.mock import MagicMock, patch

from clipping.webhook import (
    compute_signature,
    dispatch_webhook,
    verify_webhook_signature,
)


class TestWebhook(unittest.TestCase):
    def test_compute_and_verify_signature(self):
        secret = "test_secret_key_12345"
        payload = json.dumps({"event": "job.completed", "job_id": "abc1"}).encode("utf-8")

        sig = compute_signature(payload, secret)
        self.assertIsInstance(sig, str)
        self.assertEqual(len(sig), 64)

        # Valid signature with prefix
        self.assertTrue(verify_webhook_signature(payload, f"sha256={sig}", secret))
        # Valid signature without prefix
        self.assertTrue(verify_webhook_signature(payload, sig, secret))
        # Tampered payload fails
        tampered = json.dumps({"event": "job.completed", "job_id": "hacked"}).encode("utf-8")
        self.assertFalse(verify_webhook_signature(tampered, sig, secret))
        # Wrong secret fails
        self.assertFalse(verify_webhook_signature(payload, sig, "wrong_secret"))

    @patch("urllib.request.urlopen")
    def test_dispatch_webhook_success(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.getcode.return_value = 200
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        success = dispatch_webhook(
            url="https://webhook.site/test",
            event="job.completed",
            data={"job_id": "123", "clips": 5},
            secret="my_secret",
        )
        self.assertTrue(success)
        mock_urlopen.assert_called_once()
        req = mock_urlopen.call_args[0][0]
        sig_header = req.get_header("X-clipit-signature")
        self.assertIsNotNone(sig_header)
        self.assertTrue(sig_header.startswith("sha256="))

    def test_dispatch_webhook_empty_url(self):
        self.assertFalse(dispatch_webhook("", "job.completed", {}))


if __name__ == "__main__":
    unittest.main()
