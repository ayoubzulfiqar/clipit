import os
import tempfile
import unittest

from clipping.marketplace import (
    MarketplacePackError,
    export_pack,
    import_pack,
    inspect_pack,
)


class TestMarketplace(unittest.TestCase):
    def test_export_and_inspect_pack(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            font_path = os.path.join(tmpdir, "font.ttf")
            with open(font_path, "wb") as f:
                f.write(b"MOCK_FONT_BYTES")

            preset = {
                "font_style": "the_bold_font",
                "pilihan_rasio": "9:16",
                "use_sfx": True,
            }

            pack_out = os.path.join(tmpdir, "test.clipit-pack")
            export_pack(
                pack_name="Cyberpunk Viral",
                preset_data=preset,
                output_path=pack_out,
                author="Neo",
                description="High intensity neon clips",
                tags=["gaming", "neon"],
                asset_files={"custom_fonts/font.ttf": font_path},
            )

            self.assertTrue(os.path.exists(pack_out))

            # Inspect pack
            meta = inspect_pack(pack_out)
            self.assertEqual(meta["pack_name"], "Cyberpunk Viral")
            self.assertEqual(meta["author"], "Neo")
            self.assertIn("custom_fonts/font.ttf", meta["assets"])
            self.assertIn("pack.json", meta["files"])

    def test_import_pack(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            bgm_path = os.path.join(tmpdir, "bgm.mp3")
            with open(bgm_path, "wb") as f:
                f.write(b"MOCK_AUDIO_STREAM")

            preset = {"bgm_mode": "custom", "pilihan_rasio": "1:1"}
            pack_out = os.path.join(tmpdir, "podcast.clipit-pack")

            export_pack(
                pack_name="Podcast Pack",
                preset_data=preset,
                output_path=pack_out,
                asset_files={"bgm/track.mp3": bgm_path},
            )

            install_target = os.path.join(tmpdir, "installed")
            result = import_pack(pack_out, install_target)

            self.assertEqual(result["pack_name"], "Podcast Pack")
            self.assertTrue(os.path.exists(os.path.join(install_target, "bgm/track.mp3")))
            self.assertTrue(os.path.exists(result["installed_preset_path"]))

    def test_malicious_path_traversal_prevention(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            pack_out = os.path.join(tmpdir, "bad.clipit-pack")
            with self.assertRaises(MarketplacePackError):
                export_pack(
                    pack_name="Bad",
                    preset_data={"a": 1},
                    output_path=pack_out,
                    asset_files={"../../etc/passwd": "/tmp/dummy"},
                )


if __name__ == "__main__":
    unittest.main()
