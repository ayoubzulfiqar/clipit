import io
import json
import unittest
from unittest.mock import MagicMock, patch

from clipping.gpu_offload import (
    GPUOffloadProvider,
    LocalGPUProvider,
    ModalOffloadProvider,
    RunPodOffloadProvider,
    get_gpu_offload_provider,
)


class TestGPUOffload(unittest.TestCase):
    def test_local_provider(self):
        provider = LocalGPUProvider()
        self.assertEqual(provider.name, "local")
        self.assertTrue(provider.is_configured())

        task_id = provider.submit_task("render", {"clip": 1})
        self.assertTrue(task_id.startswith("local_"))

        status = provider.get_status(task_id)
        self.assertEqual(status["status"], "COMPLETED")
        self.assertIn("Local execution", status["result"]["message"])

    def test_modal_provider_unconfigured(self):
        provider = ModalOffloadProvider(endpoint_url="")
        self.assertFalse(provider.is_configured())
        with self.assertRaises(ValueError):
            provider.submit_task("render", {})

    @patch("urllib.request.urlopen")
    def test_modal_provider_submit_and_status(self, mock_urlopen):
        # Mock submit
        mock_resp_submit = MagicMock()
        mock_resp_submit.read.return_value = json.dumps({"task_id": "modal_123"}).encode("utf-8")
        mock_resp_submit.__enter__.return_value = mock_resp_submit

        # Mock status
        mock_resp_status = MagicMock()
        mock_resp_status.read.return_value = json.dumps({"status": "COMPLETED", "result": {"url": "https://cdn.modal.run/out.mp4"}}).encode("utf-8")
        mock_resp_status.__enter__.return_value = mock_resp_status

        mock_urlopen.side_effect = [mock_resp_submit, mock_resp_status]

        provider = ModalOffloadProvider(endpoint_url="https://modal.run/api/render", auth_token="tok_abc")
        self.assertTrue(provider.is_configured())

        task_id = provider.submit_task("render", {"job_id": "j1"})
        self.assertEqual(task_id, "modal_123")

        status = provider.get_status(task_id)
        self.assertEqual(status["status"], "COMPLETED")
        self.assertEqual(status["result"]["url"], "https://cdn.modal.run/out.mp4")

    def test_runpod_provider_unconfigured(self):
        provider = RunPodOffloadProvider(api_key="", endpoint_id="")
        self.assertFalse(provider.is_configured())
        with self.assertRaises(ValueError):
            provider.submit_task("render", {})

    @patch("urllib.request.urlopen")
    def test_runpod_provider_submit_and_status(self, mock_urlopen):
        mock_resp_submit = MagicMock()
        mock_resp_submit.read.return_value = json.dumps({"id": "rp_task_999"}).encode("utf-8")
        mock_resp_submit.__enter__.return_value = mock_resp_submit

        mock_resp_status = MagicMock()
        mock_resp_status.read.return_value = json.dumps({
            "status": "COMPLETED",
            "output": {"s3_key": "renders/clip1.mp4"},
            "error": None,
        }).encode("utf-8")
        mock_resp_status.__enter__.return_value = mock_resp_status

        mock_urlopen.side_effect = [mock_resp_submit, mock_resp_status]

        provider = RunPodOffloadProvider(api_key="rpa_key123", endpoint_id="ep_abc")
        self.assertTrue(provider.is_configured())

        task_id = provider.submit_task("render", {"clip": 1})
        self.assertEqual(task_id, "rp_task_999")

        status = provider.get_status(task_id)
        self.assertEqual(status["status"], "COMPLETED")
        self.assertEqual(status["result"]["s3_key"], "renders/clip1.mp4")

    def test_get_gpu_offload_provider_factory(self):
        self.assertIsInstance(get_gpu_offload_provider("local"), LocalGPUProvider)
        self.assertIsInstance(get_gpu_offload_provider("modal"), ModalOffloadProvider)
        self.assertIsInstance(get_gpu_offload_provider("runpod"), RunPodOffloadProvider)
        self.assertIsInstance(get_gpu_offload_provider("unknown"), LocalGPUProvider)


if __name__ == "__main__":
    unittest.main()
