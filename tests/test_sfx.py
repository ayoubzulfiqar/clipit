import os
import tempfile
import unittest
from unittest.mock import patch

from clipping.studio.sfx import (
    SFX_TYPES,
    build_sfx_mix_filter,
    generate_synthetic_sfx_file,
    get_local_sfx_file,
    get_synthetic_sfx_eval,
)


class TestSFX(unittest.TestCase):
    def test_sfx_types(self):
        self.assertIn("whoosh", SFX_TYPES)
        self.assertIn("impact", SFX_TYPES)
        self.assertIn("riser", SFX_TYPES)
        self.assertIn("pop", SFX_TYPES)

    def test_get_synthetic_sfx_eval(self):
        for sfx in SFX_TYPES:
            expr = get_synthetic_sfx_eval(sfx, duration=0.4, volume=0.5)
            self.assertIsInstance(expr, str)
            self.assertTrue(len(expr) > 10)
            self.assertIn("volume=", expr)

    def test_build_sfx_mix_filter_empty_cues(self):
        filt, out_lbl = build_sfx_mix_filter("[voc]", [])
        self.assertEqual(out_lbl, "[a_sfx_out]")
        self.assertIn("[voc]anull[a_sfx_out]", filt)

    def test_build_sfx_mix_filter_with_cues(self):
        cues = [
            {"type": "whoosh", "timestamp": 0.0, "volume": 0.4},
            {"type": "impact", "timestamp": 2.5, "volume": 0.6},
        ]
        filt, out_lbl = build_sfx_mix_filter("[voc]", cues)
        self.assertEqual(out_lbl, "[a_sfx_out]")
        self.assertIn("adelay=0|0[sfx_0]", filt)
        self.assertIn("adelay=2500|2500[sfx_1]", filt)
        self.assertIn("amix=inputs=3:duration=first", filt)

    def test_get_local_sfx_file_nonexistent_dir(self):
        result = get_local_sfx_file("whoosh", sfx_dir="/nonexistent/dir/for/tests")
        self.assertIsNone(result)

    @patch("subprocess.run")
    def test_generate_synthetic_sfx_file(self, mock_run):
        mock_run.return_value.returncode = 0
        with tempfile.NamedTemporaryFile(suffix=".wav") as tmp:
            ok = generate_synthetic_sfx_file(tmp.name, sfx_type="whoosh")
            self.assertTrue(ok)
            mock_run.assert_called_once()


if __name__ == "__main__":
    unittest.main()
