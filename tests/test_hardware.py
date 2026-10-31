import unittest
from unittest.mock import patch, MagicMock

from clipping.hardware import (
    HardwareProfile,
    detect_hardware,
    resolve_whisper_device,
)


class TestHardwareDetection(unittest.TestCase):
    def test_hardware_profile_to_dict(self):
        profile = HardwareProfile(
            device="cuda",
            compute_type="float16",
            cuda_available=True,
            gpu_name="NVIDIA GeForce RTX 4090",
            gpu_count=1,
            vram_total_gb=24.0,
            vram_free_gb=20.5,
        )
        d = profile.to_dict()
        self.assertEqual(d["device"], "cuda")
        self.assertEqual(d["compute_type"], "float16")
        self.assertTrue(d["cuda_available"])
        self.assertEqual(d["gpu_name"], "NVIDIA GeForce RTX 4090")
        self.assertEqual(d["gpu_count"], 1)
        self.assertEqual(d["vram_total_gb"], 24.0)
        self.assertEqual(d["vram_free_gb"], 20.5)

    def test_detect_hardware_returns_valid_profile(self):
        profile = detect_hardware()
        self.assertIsInstance(profile, HardwareProfile)
        self.assertIn(profile.device, ["cuda", "cpu"])
        self.assertIn(profile.compute_type, ["float16", "int8", "float32"])
        self.assertIsInstance(profile.cuda_available, bool)

    @patch("clipping.hardware.detect_hardware")
    def test_resolve_whisper_device_auto_cpu(self, mock_detect):
        mock_detect.return_value = HardwareProfile(
            device="cpu",
            compute_type="int8",
            cuda_available=False,
        )
        device, compute = resolve_whisper_device("auto")
        self.assertEqual(device, "cpu")
        self.assertEqual(compute, "int8")

    @patch("clipping.hardware.detect_hardware")
    def test_resolve_whisper_device_auto_cuda(self, mock_detect):
        mock_detect.return_value = HardwareProfile(
            device="cuda",
            compute_type="float16",
            cuda_available=True,
            gpu_name="NVIDIA A100",
            gpu_count=1,
        )
        device, compute = resolve_whisper_device("auto")
        self.assertEqual(device, "cuda")
        self.assertEqual(compute, "float16")

    @patch("clipping.hardware.detect_hardware")
    def test_resolve_whisper_device_cuda_fallback_when_unavailable(self, mock_detect):
        mock_detect.return_value = HardwareProfile(
            device="cpu",
            compute_type="int8",
            cuda_available=False,
        )
        # User requested cuda, but cuda is not available -> fallback to cpu
        device, compute = resolve_whisper_device("cuda")
        self.assertEqual(device, "cpu")
        self.assertEqual(compute, "int8")

    @patch("clipping.hardware.detect_hardware")
    def test_resolve_whisper_device_explicit_cpu(self, mock_detect):
        mock_detect.return_value = HardwareProfile(
            device="cuda",
            compute_type="float16",
            cuda_available=True,
        )
        # Even if CUDA is available, user explicitly requested CPU
        device, compute = resolve_whisper_device("cpu")
        self.assertEqual(device, "cpu")
        self.assertEqual(compute, "int8")

    @patch("clipping.hardware.detect_hardware")
    def test_resolve_whisper_device_custom_compute_type(self, mock_detect):
        mock_detect.return_value = HardwareProfile(
            device="cpu",
            compute_type="int8",
            cuda_available=False,
        )
        device, compute = resolve_whisper_device("cpu", requested_compute="float32")
        self.assertEqual(device, "cpu")
        self.assertEqual(compute, "float32")


if __name__ == "__main__":
    unittest.main()
