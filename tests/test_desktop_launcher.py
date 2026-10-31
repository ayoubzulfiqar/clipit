import unittest
from unittest.mock import patch, MagicMock

from desktop.launcher import find_free_port, check_ffmpeg_available, wait_for_server, launch_desktop


class TestDesktopLauncher(unittest.TestCase):
    def test_find_free_port(self):
        port = find_free_port(start_port=29100)
        self.assertIsInstance(port, int)
        self.assertGreaterEqual(port, 29100)

    @patch("shutil.which")
    def test_check_ffmpeg_available(self, mock_which):
        mock_which.return_value = "/usr/bin/ffmpeg"
        self.assertTrue(check_ffmpeg_available())

        mock_which.return_value = None
        self.assertFalse(check_ffmpeg_available())

    @patch("urllib.request.urlopen")
    def test_wait_for_server_success(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        ready = wait_for_server("http://127.0.0.1:8000", timeout_sec=1.0)
        self.assertTrue(ready)

    def test_launch_desktop_dry_run(self):
        code = launch_desktop(dry_run=True)
        self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
