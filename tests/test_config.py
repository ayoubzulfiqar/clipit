import unittest
from clipping.config import build_config, ClipitConfig, _make_url_slug


class TestConfig(unittest.TestCase):
    def test_default_config_instantiation(self):
        """Test default config has expected parameters."""
        cfg = build_config(["--url", "https://youtube.com/watch?v=sample"])
        self.assertIsInstance(cfg, ClipitConfig)
        self.assertEqual(cfg.jumlah_clip, 7)
        self.assertEqual(cfg.pilihan_rasio, "9:16")
        self.assertEqual(cfg.gaya_font_aktif, "HORMOZI")
        self.assertTrue(cfg.use_auto_bgm)
        self.assertTrue(cfg.use_hook_glitch)
        self.assertTrue(cfg.use_karaoke_effect)

    def test_custom_cli_args_override(self):
        """Test CLI arguments override defaults."""
        args = [
            "--url", "https://youtube.com/watch?v=dQw4w9WgXcQ",
            "--clips", "3",
            "--ratio", "16:9",
            "--font-style", "CINEMATIC",
            "--no-bgm",
            "--no-hook",
        ]
        cfg = build_config(args)
        self.assertEqual(cfg.url_youtube, "https://youtube.com/watch?v=dQw4w9WgXcQ")
        self.assertEqual(cfg.jumlah_clip, 3)
        self.assertEqual(cfg.pilihan_rasio, "16:9")
        self.assertEqual(cfg.gaya_font_aktif, "CINEMATIC")
        self.assertFalse(cfg.use_auto_bgm)
        self.assertFalse(cfg.use_hook_glitch)

    def test_new_capability_flags(self):
        """Test flags for scene snapping, dedup, sfx, semantic emojis, and palettes."""
        args = [
            "--url", "https://youtube.com/watch?v=sample",
            "--snap-scene-cuts",
            "--scene-snap-distance", "1.5",
            "--dedup",
            "--dedup-iou-threshold", "0.7",
            "--semantic-emojis",
            "--keyword-palette", "gold_amber",
            "--use-sfx",
            "--sfx-volume", "0.45",
        ]
        cfg = build_config(args)
        self.assertTrue(cfg.snap_scene_cuts)
        self.assertEqual(cfg.scene_snap_distance, 1.5)
        self.assertTrue(cfg.dedup)
        self.assertEqual(cfg.dedup_iou_threshold, 0.7)
        self.assertTrue(cfg.semantic_emojis)
        self.assertEqual(cfg.keyword_palette, "gold_amber")
        self.assertTrue(cfg.use_sfx)
        self.assertEqual(cfg.sfx_volume, 0.45)

    def test_url_slug_generation(self):
        """Test safe directory slug generation from URLs."""
        yt_slug = _make_url_slug("https://www.youtube.com/watch?v=dQw4w9WgXcQ", 0)
        self.assertEqual(yt_slug, "video_1_dQw4w9WgXcQ")

        tiktok_slug = _make_url_slug("https://www.tiktok.com/@user/video/123456789012345", 1)
        self.assertEqual(tiktok_slug, "video_2_123456789012")

        generic_slug = _make_url_slug("https://example.com/video.mp4", 2)
        self.assertTrue(generic_slug.startswith("video_3_"))

    def test_config_to_dict_and_clone(self):
        """Test to_dict and clone methods on ClipitConfig."""
        cfg = build_config(["--url", "https://youtube.com/watch?v=sample"])
        d = cfg.to_dict()
        self.assertIsInstance(d, dict)
        self.assertEqual(d["jumlah_clip"], 7)

        cloned = cfg.clone(jumlah_clip=10, pilihan_rasio="1:1")
        self.assertEqual(cloned.jumlah_clip, 10)
        self.assertEqual(cloned.pilihan_rasio, "1:1")
        self.assertEqual(cfg.jumlah_clip, 7)  # original unchanged


if __name__ == "__main__":
    unittest.main()
