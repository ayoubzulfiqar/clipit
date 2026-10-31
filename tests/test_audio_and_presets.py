import unittest

from clipping.config import build_config
from clipping.studio.audio_bgm import build_audio_loudnorm_filter, build_bgm_filter
from clipping.studio.presets import (
    PLATFORM_PRESETS,
    PlatformPreset,
    get_platform_preset,
)


class TestAudioNormalization(unittest.TestCase):
    def test_build_bgm_filter_standard(self):
        filter_str = build_bgm_filter("ducking", 0.25, normalize_loudness=False)
        self.assertIn("sidechaincompress", filter_str)
        self.assertIn("[a_out]", filter_str)
        self.assertNotIn("loudnorm", filter_str)

    def test_build_bgm_filter_with_loudnorm(self):
        filter_str = build_bgm_filter("ducking", 0.25, normalize_loudness=True, target_lufs=-14.0)
        self.assertIn("sidechaincompress", filter_str)
        self.assertIn("[a_mix]", filter_str)
        self.assertIn("loudnorm=I=-14.0:LRA=11:tp=-1.5[a_out]", filter_str)

    def test_build_bgm_filter_background_mode_with_loudnorm(self):
        filter_str = build_bgm_filter("background", 0.20, normalize_loudness=True, target_lufs=-16.0)
        self.assertIn("amix=inputs=2:duration=first[a_mix]", filter_str)
        self.assertIn("loudnorm=I=-16.0:LRA=11:tp=-1.5[a_out]", filter_str)

    def test_build_audio_loudnorm_filter(self):
        loud_f = build_audio_loudnorm_filter("[1:a]", target_lufs=-14.0)
        self.assertIn("[1:a]aformat=", loud_f)
        self.assertIn("loudnorm=I=-14.0:LRA=11:tp=-1.5[a_out]", loud_f)


class TestPlatformPresets(unittest.TestCase):
    def test_known_platform_presets(self):
        for name in ("tiktok", "reels", "shorts", "instagram", "linkedin", "x", "youtube"):
            preset = get_platform_preset(name)
            self.assertIsNotNone(preset)
            self.assertIsInstance(preset, PlatformPreset)
            self.assertTrue(preset.safe_zone.top_pct > 0)
            self.assertTrue(preset.safe_zone.bottom_pct > 0)

        # TikTok, Reels, Shorts are 9:16
        self.assertEqual(get_platform_preset("tiktok").aspect_ratio, "9:16")
        self.assertEqual(get_platform_preset("reels").aspect_ratio, "9:16")
        self.assertEqual(get_platform_preset("shorts").aspect_ratio, "9:16")

        # Instagram portrait is 4:5
        self.assertEqual(get_platform_preset("instagram").aspect_ratio, "4:5")

        # LinkedIn and X are 1:1
        self.assertEqual(get_platform_preset("linkedin").aspect_ratio, "1:1")
        self.assertEqual(get_platform_preset("x").aspect_ratio, "1:1")

    def test_unknown_or_none_preset(self):
        self.assertIsNone(get_platform_preset("unknown_platform"))
        self.assertIsNone(get_platform_preset(""))

    def test_cli_platform_preset_override(self):
        cfg = build_config(["--url", "https://youtube.com/watch?v=123", "--platform", "tiktok"])
        self.assertEqual(cfg.platform, "tiktok")
        self.assertEqual(cfg.pilihan_rasio, "9:16")

        cfg_ig = build_config(["--url", "https://youtube.com/watch?v=123", "--platform", "instagram"])
        self.assertEqual(cfg_ig.pilihan_rasio, "4:5")

        cfg_li = build_config(["--url", "https://youtube.com/watch?v=123", "--platform", "linkedin"])
        self.assertEqual(cfg_li.pilihan_rasio, "1:1")


if __name__ == "__main__":
    unittest.main()
