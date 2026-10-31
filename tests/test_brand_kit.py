import os
import shutil
import tempfile
from types import SimpleNamespace
import unittest

from clipping.brand_kit import BrandKit


class TestBrandKit(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_brand_kit_serialization(self):
        kit = BrandKit(
            name="Alpha Media",
            logo_position="top_left",
            primary_color="#FF5500",
            logo_opacity=0.9,
        )

        d = kit.to_dict()
        self.assertEqual(d["name"], "Alpha Media")
        self.assertEqual(d["logo_position"], "top_left")
        self.assertEqual(d["primary_color"], "#FF5500")

        # Roundtrip via file
        file_path = os.path.join(self.tmp_dir, "brand_kit.json")
        kit.save_to_file(file_path)

        loaded = BrandKit.load_from_file(file_path)
        self.assertEqual(loaded.name, "Alpha Media")
        self.assertEqual(loaded.logo_position, "top_left")

    def test_apply_to_config(self):
        cfg = SimpleNamespace(
            watermark_image=None,
            watermark_anchor="bottom_right",
            watermark_opacity=0.5,
            warna_kata_khusus="&H00FFFF&",
        )

        logo_file = os.path.join(self.tmp_dir, "logo.png")
        with open(logo_file, "w") as f:
            f.write("mock")

        kit = BrandKit(
            logo_path=logo_file,
            logo_position="top_right",
            logo_opacity=0.95,
            primary_color="#00FF88",  # R=00, G=FF, B=88 -> ASS &H88FF00&
        )

        kit.apply_to_config(cfg)
        self.assertEqual(cfg.watermark_image, logo_file)
        self.assertEqual(cfg.watermark_anchor, "top_right")
        self.assertEqual(cfg.watermark_opacity, 0.95)
        self.assertEqual(cfg.warna_kata_khusus, "&H88FF00&")


if __name__ == "__main__":
    unittest.main()
